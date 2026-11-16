"""
Test del passo 1.6: la forma unica dell'errore.

Due rotte di prova vengono aggiunte all'app vera, quella di app/main.py, perché
conta anche l'ordine in cui main.py registra i pezzi: una sbaglia con un errore
di dominio, l'altra con un'eccezione che nessuno ha previsto, il cui messaggio
contiene SQL e dati di un utente. Le rotte vengono tolte a fine test.

Gli import del codice del passo stanno dentro le funzioni: finché un file non
è scritto falliscono solo i test che lo usano, e gli altri girano.
"""

import logging
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app

ERRORE_DI_DOMINIO = "/prova/errore-di-dominio"
ERRORE_INATTESO = "/prova/errore-inatteso"

# Il messaggio dell'eccezione inattesa: è ciò che non deve mai uscire.
DETTAGLI_INTERNI = ("INSERT INTO users", "ada@example.com", "IntegrityError", "Traceback")


def solleva_errore_di_dominio() -> None:
    from app.core.errori import ErroreDiDominio

    class ConflittoDiProva(ErroreDiDominio):
        status_code = 409
        codice = "conflitto_di_prova"
        messaggio = "Un messaggio scritto per l'utente."

    raise ConflittoDiProva()


def solleva_errore_inatteso() -> None:
    # È l'eccezione che darebbe la registrazione di un'email già usata, se
    # nessuno la gestisse: il suo testo contiene la query e i parametri.
    raise IntegrityError(
        "INSERT INTO users (email) VALUES (?)",
        ("ada@example.com",),
        Exception("UNIQUE constraint failed: users.email"),
    )


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.add_api_route(ERRORE_DI_DOMINIO, solleva_errore_di_dominio)
    app.add_api_route(ERRORE_INATTESO, solleva_errore_inatteso)
    # raise_server_exceptions=False: il client restituisce la risposta che
    # riceverebbe un browser, invece di rilanciare l'eccezione nel test.
    yield TestClient(app, raise_server_exceptions=False)
    di_prova = {ERRORE_DI_DOMINIO, ERRORE_INATTESO}
    app.router.routes[:] = [
        r for r in app.router.routes if getattr(r, "path", None) not in di_prova
    ]


def test_un_errore_di_dominio_ha_la_forma_concordata(client: TestClient) -> None:
    risposta = client.get(ERRORE_DI_DOMINIO)

    assert risposta.status_code == 409
    assert risposta.json() == {
        "codice": "conflitto_di_prova",
        "messaggio": "Un messaggio scritto per l'utente.",
    }


def test_un_errore_inatteso_ha_la_stessa_forma_e_nessun_dettaglio(client: TestClient) -> None:
    risposta = client.get(ERRORE_INATTESO)

    assert risposta.status_code == 500
    for dettaglio in DETTAGLI_INTERNI:
        assert dettaglio not in risposta.text, f"il body espone {dettaglio!r}: {risposta.text}"
    corpo = risposta.json()
    assert set(corpo) == {"codice", "messaggio"}, f"forma diversa: {corpo}"
    assert corpo["codice"] == "errore_interno"


def test_un_errore_inatteso_finisce_nel_log(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    """Il dettaglio che non va nel body va nel log, con lo stacktrace."""
    with caplog.at_level(logging.ERROR):
        client.get(ERRORE_INATTESO)

    con_stacktrace = [r for r in caplog.records if r.levelno >= logging.ERROR and r.exc_info]
    assert con_stacktrace, "nessuna riga di log con lo stacktrace dell'errore inatteso"


def test_anche_le_risposte_di_errore_hanno_gli_header_di_sicurezza(client: TestClient) -> None:
    for percorso in (ERRORE_DI_DOMINIO, ERRORE_INATTESO):
        risposta = client.get(percorso)

        assert "Content-Security-Policy" in risposta.headers, f"{percorso}: header assenti"
        assert risposta.headers.get("X-Content-Type-Options") == "nosniff"
