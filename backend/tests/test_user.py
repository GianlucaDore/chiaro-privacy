"""
Test del passo 1.5: il repository di User e il servizio che lo usa.

Il servizio si prova con un repository finto, un dizionario in memoria: se
funziona senza database, vuol dire che non dipende dal database. Il repository
SQLAlchemy si prova invece su un file SQLite temporaneo, come in test_db.py.

Gli import del codice del passo stanno dentro le funzioni: finché un file non
è scritto falliscono solo i test che lo usano, e gli altri girano.
"""

import subprocess
import sys
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import get_backend_root

if TYPE_CHECKING:
    from app.repositories.user import UserRepository
    from app.services.user import UserService


def crea_repository_finto() -> "UserRepository":
    """Un'implementazione del contratto che tiene gli utenti in un dizionario."""
    from app.repositories.user import UserRepository, Utente

    class RepositoryInMemoria(UserRepository):
        def __init__(self) -> None:
            self.utenti: dict[str, Utente] = {}

        def aggiungi(self, email: str) -> Utente:
            utente = Utente(id=len(self.utenti) + 1, email=email, creato_il=datetime.now(UTC))
            self.utenti[email] = utente
            return utente

        def cerca_per_email(self, email: str) -> Utente | None:
            return self.utenti.get(email)

    return RepositoryInMemoria()


@pytest.fixture
def servizio() -> "UserService":
    from app.services.user import UserService

    return UserService(crea_repository_finto())


@pytest.fixture
def sessione(tmp_path: Path) -> Iterator[Session]:
    """Una sessione su un database nuovo, con le tabelle create da zero."""
    from app import models  # noqa: F401  (registra i modelli in Base.metadata)
    from app.db.base import Base

    motore = create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(motore)
    with Session(motore) as sessione:
        yield sessione


# --- Il contratto ------------------------------------------------------------


def test_il_contratto_non_si_istanzia() -> None:
    """UserRepository dichiara i metodi, non li implementa: non può esistere da solo."""
    from app.repositories.user import UserRepository

    with pytest.raises(TypeError):
        UserRepository()  # pyright: ignore[reportAbstractUsage]


# --- Il servizio, con il repository finto ------------------------------------


def test_il_servizio_crea_e_ritrova_un_utente(servizio: "UserService") -> None:
    creato = servizio.crea_utente("ada@example.com")

    assert servizio.trova_utente("ada@example.com") == creato


def test_il_servizio_non_trova_chi_non_esiste(servizio: "UserService") -> None:
    assert servizio.trova_utente("nessuno@example.com") is None


def test_il_servizio_non_carica_sqlalchemy() -> None:
    """
    Il test gira in un interprete nuovo, perché in questo SQLAlchemy è già
    caricato dagli altri test. Lì importa il servizio e guarda se, per
    arrivarci, Python ha dovuto caricare anche SQLAlchemy.
    """
    codice = (
        "import sys; from app.services.user import UserService; print('sqlalchemy' in sys.modules)"
    )
    esito = subprocess.run(
        [sys.executable, "-c", codice],
        cwd=get_backend_root(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert esito.returncode == 0, esito.stderr
    assert esito.stdout.strip() == "False", "importando il servizio si carica anche SQLAlchemy"


# --- Il repository SQLAlchemy, su un database vero ---------------------------


def test_il_repository_restituisce_un_utente_di_dominio(sessione: Session) -> None:
    from app.repositories.user import Utente
    from app.repositories.user_sqlalchemy import SqlAlchemyUserRepository

    utente = SqlAlchemyUserRepository(sessione).aggiungi("ada@example.com")

    assert type(utente) is Utente, f"restituito {type(utente).__name__}, non Utente"
    assert isinstance(utente.id, int), "l'id è vuoto: la riga non è ancora arrivata al database"
    assert isinstance(utente.creato_il, datetime)


def test_il_repository_ritrova_per_email(sessione: Session) -> None:
    from app.repositories.user_sqlalchemy import SqlAlchemyUserRepository

    repository = SqlAlchemyUserRepository(sessione)
    aggiunto = repository.aggiungi("ada@example.com")
    # La sessione dimentica ciò che ha in memoria: la ricerca rilegge dal
    # database, come farà una richiesta successiva.
    sessione.expire_all()

    ritrovato = repository.cerca_per_email("ada@example.com")
    assert ritrovato == aggiunto, f"riletto diverso da scritto:\n{ritrovato}\n{aggiunto}"
    assert repository.cerca_per_email("nessuno@example.com") is None


def test_il_repository_non_fa_commit(sessione: Session) -> None:
    """
    Confermare il lavoro spetta a chi conosce il lavoro intero, non al
    repository. Se il repository facesse commit, il rollback non annullerebbe
    più niente.
    """
    from app.repositories.user_sqlalchemy import SqlAlchemyUserRepository

    repository = SqlAlchemyUserRepository(sessione)
    repository.aggiungi("ada@example.com")
    sessione.rollback()

    assert repository.cerca_per_email("ada@example.com") is None, "il repository ha fatto commit"
