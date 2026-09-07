from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# TODO(0.4/13) Correggi queste due righe di import, aggiungendo il prefisso del
#              pacchetto: non `core.config` ma `app.core.config`, e non
#              `api.router` ma `app.api.router`.
#
#              Perche': un "pacchetto" Python e' una cartella che contiene un
#              file __init__.py. Qui il pacchetto e' `app/`, e Python risolve
#              gli import a partire dalla cartella da cui lanci il processo,
#              cioe' `backend/`. Da `backend/` la cartella `core` non esiste:
#              esiste `app/core`. Quindi il nome completo del modulo e'
#              `app.core.config`.
#
#              Il modo giusto di convincersene e' provare: lancia
#              `pipenv run dev` PRIMA di correggere e leggi l'errore. Dira'
#              ModuleNotFoundError e ti dira' quale nome non ha trovato.
#
#              Nota: questa correzione appartiene al passo 0.4 e non al 0.5,
#              perche' senza di essa `pipenv run dev` non parte e il criterio
#              del passo 0.4 non e' verificabile. Tutto il RESTO di questo file
#              (l'on_event deprecato, i security header commentati, il CORS con
#              l'indirizzo scritto a mano, il basicConfig duplicato) e' il passo
#              0.5: non toccarlo adesso.
from core.config import settings, Env
from api.router import api_router
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=(f"{settings.API_PREFIX}/docs" if settings.ENV != Env.DEV else "/docs"),
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

app.include_router(api_router, prefix=settings.API_PREFIX)

'''
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none'" if settings.ENV == Env.DEV else "default-src 'none'; frame-ancestors 'none'"
        response.headers['Cross-Origin-Resource-Policy'] = 'same-site'
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp; report-to=default'
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin; report-to=default'
        # response.headers['Content-Type'] = 'application/json'
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response
'''

# app.add_middleware(SecurityHeadersMiddleware)


if settings.ENV == Env.DEV:
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=[str(settings.BACKEND_CORS_ORIGIN)],
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

@app.on_event('startup')
async def load_config() -> None:
    """
    Bootstrap
    """

    os.makedirs("uploads", exist_ok=True)
    


logging.basicConfig(format='%(levelname)-9s %(asctime)s - %(name)s - %(message)s', level=logging.DEBUG if settings.ENV == Env.DEV else logging.INFO)