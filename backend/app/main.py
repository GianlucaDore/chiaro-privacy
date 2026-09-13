import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.api.router import api_router
from app.core.config import Env, get_backend_root, settings

# --- Documentazione interattiva --------------------------------------------
# In produzione non viene esposta affatto: una mappa navigabile dell'API e'
# superficie d'attacco regalata, e Swagger UI carica il proprio JavaScript da
# una CDN di terzi dentro la nostra origine. Fuori da DEV vive sotto il
# prefisso dell'API.
if settings.ENV is Env.PROD:
    DOCS_URL: str | None = None
    REDOC_URL: str | None = None
    OPENAPI_URL: str | None = None
else:
    prefisso = "" if settings.ENV is Env.DEV else settings.API_PREFIX
    DOCS_URL = f"{prefisso}/docs"
    REDOC_URL = f"{prefisso}/redoc"
    OPENAPI_URL = f"{settings.API_PREFIX}/openapi.json"

# Le pagine HTML della documentazione: sono le uniche che caricano risorse di
# terzi, quindi le uniche che hanno bisogno di una CSP allargata.
PAGINE_DOCUMENTAZIONE = frozenset(
    p
    for p in (DOCS_URL, REDOC_URL, f"{DOCS_URL}/oauth2-redirect" if DOCS_URL else None)
    if p is not None
)

# Tutto cio' che serve documentazione invece di dati dell'utente: nessuno di
# questi percorsi ha ragione di essere escluso dalla cache.
PERCORSI_PUBBLICI = PAGINE_DOCUMENTAZIONE | {p for p in (OPENAPI_URL,) if p is not None}

# --- Content Security Policy ------------------------------------------------
# Sulle risposte dell'API: una risposta JSON non deve caricare nulla, quindi
# si nega tutto. E' la raccomandazione OWASP per le API.
CSP_API = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"

# Sulle pagine di documentazione serve una politica piu' larga, perche' Swagger
# UI e ReDoc caricano JS e CSS da cdn.jsdelivr.net, il favicon da
# fastapi.tiangolo.com, i font da Google, e FastAPI genera uno <script> inline
# che senza 'unsafe-inline' non verrebbe eseguito. Le origini sono elencate
# una per una: e' il motivo per cui queste pagine non esistono in produzione.
CSP_DOCUMENTAZIONE = (
    "default-src 'none'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "connect-src 'self'; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # avvio
    os.makedirs(get_backend_root() / "uploads", exist_ok=True)
    yield
    # spegnimento - per ora niente


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)

app.include_router(api_router, prefix=settings.API_PREFIX)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applica gli header di sicurezza a ogni risposta, comprese quelle di errore.

    Il middleware e' il posto giusto perche' e' l'unico punto attraversato da
    tutte le risposte: un header applicato rotta per rotta manca esattamente
    sulle risposte che nessuno ha scritto a mano, cioe' i 404 e i 500.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        percorso = request.url.path

        response.headers["Content-Security-Policy"] = (
            CSP_DOCUMENTAZIONE if percorso in PAGINE_DOCUMENTAZIONE else CSP_API
        )
        # Vieta al browser di indovinare il tipo di contenuto dai byte.
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Anti-clickjacking. Dice la stessa cosa di frame-ancestors 'none':
        # resta per i browser che la direttiva CSP non la leggono.
        response.headers["X-Frame-Options"] = "DENY"
        # Gli URL dell'API conterranno identificativi di analisi: non devono
        # finire nell'header Referer delle richieste verso altri siti.
        response.headers["Referrer-Policy"] = "no-referrer"
        # Recide il legame window.opener con le pagine aperte da qui.
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        # Vieta di incorporare le nostre risposte come sottorisorsa altrui.
        # Non riguarda le fetch in modalita' CORS, che e' il modo in cui il
        # frontend parla con l'API: non la ostacola.
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # no-store solo dove c'e' qualcosa da proteggere. Le pagine di
        # documentazione e lo schema OpenAPI non contengono dati personali e
        # non c'e' ragione di ricaricarli a ogni visita.
        if percorso not in PERCORSI_PUBBLICI:
            response.headers["Cache-Control"] = "no-store"

        # HSTS e' ignorato su HTTP semplice, quindi in sviluppo sarebbe inerte.
        # Niente preload: e' una decisione che i browser ricordano per mesi e
        # che non si ritira in fretta.
        if settings.ENV is Env.PROD:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


# --- Origini CORS ------------------------------------------------------------
# BACKEND_CORS_ORIGIN e' un valore singolo o un elenco separato da virgole.
# Se e' vuoto non si registra alcun CORSMiddleware: [""] sarebbe una lista che
# non ammette niente ma che ha tutta l'aria di essere configurata.
ORIGINI_CORS = [
    origine.strip() for origine in str(settings.BACKEND_CORS_ORIGIN).split(",") if origine.strip()
]

app.add_middleware(SecurityHeadersMiddleware)

# Registrato per ultimo, quindi e' il piu' esterno: Starlette inserisce in
# testa alla pila. Serve che stia fuori, cosi' gli header CORS finiscono anche
# sulle risposte di errore generate piu' internamente - altrimenti il browser
# nasconde al frontend il corpo di ogni 500.
if ORIGINI_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINI_CORS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


logging.basicConfig(
    format="%(levelname)-9s %(asctime)s - %(name)s - %(message)s",
    level=logging.DEBUG if settings.ENV is Env.DEV else logging.INFO,
)
