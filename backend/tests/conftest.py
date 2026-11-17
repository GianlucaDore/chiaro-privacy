"""
Le fixture condivise da tutta la suite.

pytest legge questo file da solo, prima dei test della cartella `tests/`, e ogni
fixture definita qui la può chiedere qualunque test della cartella, senza
importarla.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    """Un motore su un file nuovo, con le tabelle create da zero."""
    from app import models  # noqa: F401  (registra i modelli in Base.metadata)

    motore = create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(motore)
    yield motore
    motore.dispose()


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    """
    L'app vera, ma con il database di prova del test al posto di quello di sviluppo.

    Le rotte continuano a chiedere la sessione a get_db, come in produzione: è
    FastAPI a consegnare loro, al suo posto, una sessione legata a `engine`.
    """

    # Scelta A: una sessione nuova a ogni richiesta, chiusa dopo, come fa get_db in
    # produzione. La B, una sessione sola condivisa con il test, farebbe vedere al test
    # anche ciò che la rotta non ha confermato con commit: il test passerebbe su una
    # rotta che in produzione perde i dati.
    def get_db_di_prova() -> Iterator[Session]:
        """La sostituta di get_db: identica, ma le sessioni le prende da `engine`."""
        session = Session(engine)
        try:
            yield session
        finally:
            session.close()

    # La chiave è la funzione get_db, la stessa che le rotte dichiarano in Depends,
    # non il suo risultato get_db(): con quello l'override non scatterebbe mai.
    app.dependency_overrides[get_db] = get_db_di_prova

    # Il with fa girare il lifespan, come all'avvio vero dell'app.
    with TestClient(app) as client:
        yield client

    # L'app è una sola per tutta la suite: senza clear() l'override resterebbe
    # attivo anche nei test che vengono dopo.
    app.dependency_overrides.clear()
