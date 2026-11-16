"""
Test del passo 1.4: una sessione per richiesta, chiusa sempre.

Le rotte di questo file esistono solo per i test: chiedono la sessione con
`SessionDep`, cioè con la dipendenza vera di `app/api/deps.py`, e la usano
come farà ogni rotta vera.

Il database invece è finto. Dentro `app.api.deps` la fabbrica `SessionLocal`
viene sostituita da una legata a un file SQLite temporaneo, che produce
sessioni «osservate»: sessioni normali che in più ricordano se qualcuno le ha
chiuse. Così il test vede quello che di solito non si vede, cioè se la
chiusura è avvenuta davvero.
"""

from pathlib import Path
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool

from app.api import deps
from app.api.deps import SessionDep


class SessioneOsservata(Session):
    """Una sessione normale, che in più ricorda se è stata chiusa."""

    chiusa: bool = False

    def close(self) -> None:
        self.chiusa = True
        super().close()


class Osservatore:
    """La fabbrica finta: un database temporaneo, e l'elenco delle sessioni prodotte."""

    def __init__(self, motore: Engine) -> None:
        self.motore = motore
        self.sessioni: list[SessioneOsservata] = []

    def __call__(self) -> SessioneOsservata:
        sessione = SessioneOsservata(bind=self.motore)
        self.sessioni.append(sessione)
        return sessione

    def in_prestito(self) -> int:
        """Quante connessioni del pool sono in prestito in questo momento."""
        pool = self.motore.pool
        assert isinstance(pool, QueuePool), "SQLite su file usa QueuePool"
        return pool.checkedout()


@pytest.fixture
def osservatore(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Osservatore:
    if not hasattr(deps, "SessionLocal"):
        pytest.fail("app/api/deps.py non importa SessionLocal per nome: il test non la sostituisce")
    osservatore = Osservatore(create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}"))
    # get_db cerca SessionLocal per nome nel proprio modulo, al momento della
    # chiamata: sostituendola qui, trova la fabbrica finta.
    monkeypatch.setattr(deps, "SessionLocal", osservatore)
    return osservatore


def crea_app() -> FastAPI:
    app = FastAPI()

    @app.get("/query")
    def query(sessione: SessionDep) -> int:
        # Una query vera: la sessione prende una connessione dal pool.
        return sessione.execute(text("select 1")).scalar_one()

    @app.get("/errore")
    def errore(sessione: SessionDep) -> None:
        sessione.execute(text("select 1"))
        raise RuntimeError("la rotta fallisce a metà")

    def anche_io(sessione: SessionDep) -> Session:
        # Una seconda dipendenza che chiede anche lei la sessione.
        return sessione

    @app.get("/due")
    def due(sessione: SessionDep, altra: Annotated[Session, Depends(anche_io)]) -> bool:
        return sessione is altra

    return app


def test_ogni_richiesta_riceve_una_sessione_nuova(osservatore: Osservatore) -> None:
    client = TestClient(crea_app())

    client.get("/query")
    client.get("/query")

    assert len(osservatore.sessioni) == 2, "serve una sessione per richiesta"
    prima, seconda = osservatore.sessioni
    assert prima is not seconda


def test_nella_stessa_richiesta_la_sessione_e_una_sola(osservatore: Osservatore) -> None:
    """
    Due dipendenze chiedono la sessione nella stessa richiesta: FastAPI chiama
    get_db una volta sola e consegna a entrambe lo stesso oggetto. Per questo
    tutto il lavoro di una richiesta finisce in una sola transazione.
    """
    risposta = TestClient(crea_app()).get("/due")

    assert risposta.json() is True
    assert len(osservatore.sessioni) == 1


def test_la_sessione_si_chiude_dopo_la_risposta(osservatore: Osservatore) -> None:
    TestClient(crea_app()).get("/query")

    assert osservatore.sessioni, "nessuna sessione: get_db non l'ha presa da SessionLocal"
    assert all(s.chiusa for s in osservatore.sessioni), "la sessione è rimasta aperta"
    assert osservatore.in_prestito() == 0, "una connessione è rimasta in prestito"


def test_la_sessione_si_chiude_anche_se_la_rotta_fallisce(osservatore: Osservatore) -> None:
    """
    È il caso che distingue una chiusura garantita da una chiusura sperata:
    l'eccezione della rotta rientra in get_db proprio nel punto dello yield, e
    il codice scritto dopo, se non è protetto, non viene mai eseguito.
    """
    client = TestClient(crea_app(), raise_server_exceptions=False)

    risposta = client.get("/errore")

    assert risposta.status_code == 500
    assert osservatore.sessioni, "nessuna sessione: get_db non l'ha presa da SessionLocal"
    assert osservatore.sessioni[0].chiusa, "dopo l'errore la sessione è rimasta aperta"
    assert osservatore.in_prestito() == 0, "dopo l'errore una connessione è rimasta in prestito"
