# =============================================================================
# PASSO 0.5 — ZONA ROSSA 🔴: questo file lo scrivi TU.
#
# Io ho lasciato i cartelli e lo scheletro del lifespan. Ogni riga che inizia
# con "# TODO(0.5/n)" è una cosa da fare: fatta quella, cancella il cartello.
# A passo finito non ne deve restare nessuno.
#
# Spiegazione completa, con il perché di ognuna: docs/passi/0.5.md
# Bersaglio oggettivo: `pipenv run test`, che oggi fallisce 5 volte su 5.
#
# Criterio: `curl -I` mostra CSP, X-Frame-Options e X-Content-Type-Options;
# l'app parte e si spegne senza warning di deprecazione.
# =============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings, Env
from app.api.router import api_router
import logging
from starlette.middleware.base import BaseHTTPMiddleware
import os

# TODO(0.5/1) Ti serviranno due import in più: `asynccontextmanager` da
#             `contextlib` e `AsyncIterator` da `collections.abc`, per annotare
#             il tipo di ritorno del lifespan.
#             ⚠️ Alcuni degli import qui sopra diventeranno inutilizzati quando
#             avrai finito: `os` lo resta solo se continui a usarlo, `logging`
#             dipende da dove decidi di configurarlo. `ruff` te lo dirà al
#             passo 0.8, ma è più pulito accorgersene adesso.


# -----------------------------------------------------------------------------
# 1. IL LIFESPAN
# -----------------------------------------------------------------------------
# TODO(0.5/2) Scrivi il corpo di questa funzione, poi cancella il vecchio
#             `@app.on_event('startup')` più sotto.
#
#             La forma è quella di un `with`: ciò che sta PRIMA dello `yield` è
#             l'avvio, ciò che sta DOPO è lo spegnimento, e le variabili
#             restano in scope fra i due — che è esattamente la cosa che con due
#             `on_event` separati non si poteva fare.
#
#             Per adesso all'avvio serve solo creare la cartella degli upload.
#             ⚠️ Ma NON con un percorso relativo come fa il codice attuale:
#             `os.makedirs("uploads")` dipende dalla cartella da cui è stato
#             lanciato il processo. È lo stesso difetto del passo 0.3, e hai già
#             lo strumento per risolverlo — `get_backend_root()`.
#
#             Allo spegnimento, oggi, non c'è niente da fare: lascia il posto e
#             un commento che lo dica. Dalla fase 1 ci andrà la chiusura del
#             pool di connessioni al database.
def lifespan(app: FastAPI):
    """
    Avvio e spegnimento dell'applicazione.

    TODO(0.5/3) Manca il decoratore che trasforma questa funzione in un context
                manager asincrono, e mancano `async` nella firma e
                l'annotazione del tipo di ritorno.
    """
    # TODO: avvio — la cartella degli upload
    yield
    # TODO: spegnimento — per ora niente


# -----------------------------------------------------------------------------
# 2. L'APPLICAZIONE
# -----------------------------------------------------------------------------
# TODO(0.5/4) Passa il lifespan al costruttore, con il parametro `lifespan=`.
#             Finché non lo fai, la funzione qui sopra non viene mai chiamata da
#             nessuno: definire un lifespan e non registrarlo è un errore che
#             non produce nessun messaggio.
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=(f"{settings.API_PREFIX}/docs" if settings.ENV != Env.DEV else "/docs"),
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

app.include_router(api_router, prefix=settings.API_PREFIX)


# -----------------------------------------------------------------------------
# 3. I SECURITY HEADER
# -----------------------------------------------------------------------------
# TODO(0.5/5) ❗ Il blocco qui sotto NON è commentato: è una STRINGA.
#             Le triple apici in Python delimitano una stringa, e una stringa da
#             sola su una riga è un'espressione valida — viene costruita,
#             valutata e buttata via. Quindi la classe
#             `SecurityHeadersMiddleware` non esiste, `ruff` e `pyright` non
#             guardano dentro, e togliere il commento alla riga
#             `app.add_middleware(...)` senza togliere le apici darebbe un
#             NameError.
#
# TODO(0.5/6) Il codice dentro la stringa è una proposta del template, non una
#             soluzione da incollare. Il lavoro di questo passo è deciderla
#             header per header. Tre in particolare vanno guardati con
#             sospetto, e il perché è nella sezione 5 di docs/passi/0.5.md:
#
#             ⚠️ `Cache-Control: no-store` su OGNI risposta impedisce la cache
#                anche di /docs e dello schema OpenAPI, che non contengono
#                niente di personale.
#             ⚠️ `Cross-Origin-Embedder-Policy: require-corp` è quello che
#                rompe le cose: blocca ogni risorsa di terzi che non acconsenta
#                esplicitamente. Va attivato sapendo cosa si sta isolando.
#             ⚠️ `Content-Type: application/json` fisso, se lo riattivassi,
#                romperebbe /docs, che è HTML. È commentato per un motivo.
#
#             Due dei sette li hai già nella tua nota sull'auth: CSP e HSTS.
#             Gli altri cinque no, e la tabella nel briefing li copre uno a uno.
#
# TODO(0.5/7) ⚠️ Nota per il futuro, da non risolvere adesso ma da sapere:
#             `BaseHTTPMiddleware` interferisce con le risposte in streaming,
#             perché le avvolge invece di lasciarle passare. Il passo 4.2 di
#             questo progetto è un endpoint SSE con `StreamingResponse`, quindi
#             il conto arriva lì. L'alternativa è un middleware ASGI puro, che
#             riceve `scope, receive, send`.
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

# TODO(0.5/8) Registra il middleware. Attenzione all'ordine: i middleware si
#             applicano in ordine inverso rispetto a quello di registrazione,
#             quindi rifletti su dove va rispetto al CORS qui sotto.
# app.add_middleware(SecurityHeadersMiddleware)


# -----------------------------------------------------------------------------
# 4. IL CORS
# -----------------------------------------------------------------------------
# TODO(0.5/9) Fai venire le origini da `settings.BACKEND_CORS_ORIGIN` invece che
#             dalla stringa scritta a mano. La riga giusta è già lì, commentata.
#
#             Due decisioni, nessuna delle due ovvia:
#             - `allow_origins` vuole una LISTA, mentre in config.py
#               `BACKEND_CORS_ORIGIN` è un valore singolo. Una sola origine per
#               sempre, o una lista separata da virgole da spezzare?
#             - il default è la stringa vuota, e `[""]` è una lista che non
#               ammette niente ma *sembra* configurata. Decidi cosa farne.
#               (Rifiutarla al boot è il passo 1.1: qui basta non peggiorare.)
#
# TODO(0.5/10) L'`if settings.ENV == Env.DEV` significa che in produzione il
#              CORS non viene aggiunto affatto. È voluto? Il frontend girerà su
#              un'origine diversa dal backend anche in produzione. Non lo
#              risolvi qui — il passo 1.2 è dedicato a CORS — ma decidi se
#              lasciarlo così e perché.
if settings.ENV == Env.DEV:
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=[str(settings.BACKEND_CORS_ORIGIN)],
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


# -----------------------------------------------------------------------------
# 5. DA CANCELLARE
# -----------------------------------------------------------------------------
# TODO(0.5/11) Cancella questo blocco: è ciò che il lifespan sostituisce, ed è
#              la riga che produce il DeprecationWarning che il test
#              `test_nessun_warning_di_deprecazione_all_avvio` intercetta.
@app.on_event('startup')
async def load_config() -> None:
    """
    Bootstrap
    """

    os.makedirs("uploads", exist_ok=True)



# TODO(0.5/12) Una di queste due chiamate va cancellata: la stessa riga esiste
#              in app/core/config.py:74 e `logging.basicConfig` esce in
#              silenzio se il logger radice ha già degli handler.
#              Quale delle due vince oggi, e perché, è la domanda 2 del
#              briefing: rispondici prima di scegliere quale togliere.
logging.basicConfig(format='%(levelname)-9s %(asctime)s - %(name)s - %(message)s', level=logging.DEBUG if settings.ENV == Env.DEV else logging.INFO)
