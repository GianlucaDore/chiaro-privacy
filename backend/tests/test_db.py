"""
Test del passo 1.3: il database, il modello User e create_all.

Ogni test costruisce il proprio motore su un file SQLite in una cartella
temporanea di pytest (`tmp_path`): non tocca mai il database di sviluppo, ed è
un primo assaggio di quello che il passo 1.7 farà per tutta la suite.

Gli import di `app.models` e `app.db.base` stanno dentro le funzioni: finché il
modello non esiste, falliscono i test che lo usano, ma il file si raccoglie
comunque e gli altri girano.
"""

from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine, inspect, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_backend_root


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    """Un motore su un file nuovo, con le tabelle create da zero."""
    from app import models  # noqa: F401  (registra i modelli in Base.metadata)
    from app.db.base import Base

    motore = create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(motore)
    return motore


# --- La configurazione -------------------------------------------------------


def test_database_url_e_un_percorso_assoluto(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Il file del database non deve dipendere dalla cartella da cui si lancia
    uvicorn: è il bug del passo 0.3, in un'altra forma.
    """
    monkeypatch.delenv("DATABASE_URL", raising=False)
    url = make_url(Settings(_env_file=None).DATABASE_URL)

    assert url.drivername == "sqlite"
    assert url.database, "il database non può essere in memoria: sparirebbe a ogni riavvio"
    percorso = Path(url.database)
    assert percorso.is_absolute(), f"percorso relativo: {url.database}"
    assert get_backend_root() in percorso.parents, f"fuori dal backend: {percorso}"


# --- Il registro e create_all ------------------------------------------------


def test_importando_app_models_si_registra_la_tabella_users() -> None:
    """
    Base.metadata conosce solo le classi importate. Importare il pacchetto
    app.models deve bastare a iscrivere User.
    """
    from app import models  # noqa: F401
    from app.db.base import Base

    assert "users" in Base.metadata.tables


def test_create_all_crea_la_tabella_users(engine: Engine) -> None:
    assert "users" in inspect(engine).get_table_names()


def test_la_tabella_users_ha_le_colonne_previste(engine: Engine) -> None:
    colonne = {c["name"]: c for c in inspect(engine).get_columns("users")}

    assert {"id", "email", "creato_il"} <= set(colonne), f"colonne trovate: {sorted(colonne)}"
    assert not colonne["email"]["nullable"], "l'email deve essere obbligatoria"


# --- Creare e rileggere ------------------------------------------------------


def test_un_utente_si_crea_e_si_rilegge(engine: Engine) -> None:
    """
    È il criterio del passo. La rilettura avviene in una sessione nuova: così
    il valore arriva davvero dal database, e non dalla memoria della prima.
    """
    from app.models import User

    with Session(engine) as sessione:
        sessione.add(User(email="ada@example.com"))
        sessione.commit()

    with Session(engine) as sessione:
        riletto = sessione.scalars(select(User).where(User.email == "ada@example.com")).one()

        assert riletto.id is not None, "l'id lo assegna il database (o il modello) al commit"
        assert riletto.creato_il is not None, "la data di creazione si riempie da sola"


def test_due_utenti_con_la_stessa_email_sono_rifiutati(engine: Engine) -> None:
    """
    L'unicità la garantisce il database, non il codice che controlla prima di
    inserire: due richieste contemporanee passerebbero entrambe il controllo.
    """
    from app.models import User

    with Session(engine) as sessione:
        sessione.add(User(email="ada@example.com"))
        sessione.commit()

    with Session(engine) as sessione:
        sessione.add(User(email="ada@example.com"))
        with pytest.raises(IntegrityError):
            sessione.commit()
