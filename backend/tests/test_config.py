"""
Test della risoluzione della radice del backend e del caricamento del `.env`.

Coprono il criterio del passo 0.3: `DOTENV` deve puntare dentro la repository, e
una variabile scritta nel file `.env` deve arrivare fino ai settings.
"""

from pathlib import Path

import pytest

from app.core.config import (
    DOTENV,
    MARCATORE_RADICE,
    Settings,
    get_backend_root,
    risali_fino_al_marcatore,
)


def test_la_radice_contiene_il_marcatore() -> None:
    """La radice del backend è, per definizione, la cartella con il Pipfile."""
    radice = get_backend_root()
    assert (radice / MARCATORE_RADICE).is_file()


def test_dotenv_punta_dentro_la_repo() -> None:
    """Il `.env` sta accanto al Pipfile, e quella posizione è dentro la repo."""
    assert DOTENV.name == ".env"
    assert DOTENV.parent == get_backend_root()
    # La repository contiene il backend: `.env` deve trovarsi sotto di essa e
    # non in un punto qualsiasi del filesystem.
    repo = get_backend_root().parent
    assert repo in DOTENV.parents


def test_variabile_scritta_nel_dotenv_arriva_nei_settings(tmp_path: Path) -> None:
    """Il percorso non basta: il valore deve attraversare pydantic-settings."""
    env = tmp_path / ".env"
    env.write_text("PROJECT_NAME=Chiaro\n", encoding="utf-8")

    settings = Settings(_env_file=env)

    assert settings.PROJECT_NAME == "Chiaro"


def test_radice_indipendente_dalla_profondita(tmp_path: Path) -> None:
    """
    Regressione del bug corretto in questo passo.

    Contare i livelli con `parents[2]` legava la radice alla posizione esatta del
    modulo: annidare `config.py` di una sola cartella la spostava in silenzio.
    Risalendo fino al marcatore, invece, la profondità di partenza è irrilevante.
    """
    (tmp_path / MARCATORE_RADICE).write_text("", encoding="utf-8")
    poco_profondo = tmp_path / "app" / "core"
    molto_profondo = tmp_path / "app" / "core" / "settings" / "interne"
    poco_profondo.mkdir(parents=True)
    molto_profondo.mkdir(parents=True)

    assert risali_fino_al_marcatore(poco_profondo) == tmp_path
    assert risali_fino_al_marcatore(molto_profondo) == tmp_path


def test_errore_esplicito_se_il_marcatore_manca(tmp_path: Path) -> None:
    """
    Se la radice non si trova, l'errore deve essere immediato e leggibile.

    Senza l'eccezione il fallimento sarebbe silenzioso: pydantic-settings ignora
    un `env_file` inesistente, quindi l'applicazione partirebbe con tutti i
    valori di default e nessun indizio su cosa sia andato storto.
    """
    partenza = tmp_path / "senza" / "marcatore"
    partenza.mkdir(parents=True)

    with pytest.raises(RuntimeError, match="marcatore-che-non-esiste"):
        risali_fino_al_marcatore(partenza, marcatore="marcatore-che-non-esiste")
