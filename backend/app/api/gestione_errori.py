"""
Come un errore diventa una risposta: sempre nella stessa forma, mai con i dettagli interni.

La forma concordata è un oggetto JSON con due chiavi: `codice`, che il
frontend usa per decidere cosa fare, e `messaggio`, che mostra all'utente.
Gli errori di dominio la riempiono con i propri valori; gli errori inattesi
con un testo generico, mentre il dettaglio finisce nel log.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.core.errori import ErroreDiDominio

logger = logging.getLogger(__name__)


async def gestisci_errore_di_dominio(request: Request, exc: ErroreDiDominio) -> JSONResponse:
    # Un gestore solo per tutti gli errori di dominio: i valori arrivano dalla
    # classe figlia che è stata sollevata.
    return JSONResponse(
        status_code=exc.status_code,
        content={"codice": exc.codice, "messaggio": exc.messaggio},
    )


async def intercetta_errori_inattesi(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
    try:
        return await call_next(request)
    except Exception:
        # Il dettaglio, con lo stacktrace, va nel log. Nel body mai str(exc):
        # quello di un IntegrityError contiene la query e i dati dell'utente.
        logger.exception("Errore inatteso su %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"codice": "errore_interno", "messaggio": "Errore interno del server."},
        )


def registra_gestione_errori(app: FastAPI) -> None:
    # Collega una funzione a una classe di eccezioni. Da qui in poi, quando una rotta solleva quella
    # classe o una sua figlia, FastAPI chiama la funzione al posto di rispondere 500.
    # app.add_exception_handler farebbe lo stesso, ma pyright rifiuta il tipo del gestore.
    app.exception_handler(ErroreDiDominio)(gestisci_errore_di_dominio)
    # L'errore inatteso si intercetta con un middleware, non con
    # app.exception_handler(Exception): quel gestore Starlette lo esegue fuori da
    # tutti i middleware, e il suo 500 uscirebbe senza header di sicurezza né CORS.
    app.middleware("http")(intercetta_errori_inattesi)
