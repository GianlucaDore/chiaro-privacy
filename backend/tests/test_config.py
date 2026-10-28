"""
Test della configurazione del backend.

I primi coprono il criterio del passo 0.3: `DOTENV` deve puntare dentro la
repository, e una variabile scritta nel file `.env` deve arrivare fino ai
settings. Quelli in fondo, nella sezione «Passo 1.1», coprono le variabili
obbligatorie e il messaggio d'errore all'avvio.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import (
    DOTENV,
    MARCATORE_RADICE,
    Env,
    Settings,
    carica_settings,
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


# --- Passo 1.1: variabili obbligatorie ----------------------------------------
#
# Ogni test toglie ENV dall'ambiente con monkeypatch, e passa `_env_file=None`
# oppure un file preciso: deve dipendere solo da ciò che dichiara, non dalla
# shell né dal `.env` di chi lancia la suite, né dal valore che `conftest.py`
# imposta per tutti gli altri test.

ESEMPIO = get_backend_root() / ".env.example"

# Un valore riconoscibile, che non deve mai comparire in un messaggio d'errore.
# Oggi i settings non contengono segreti, quindi fa da segreto un campo
# qualsiasi: il comportamento da verificare è lo stesso che avrà
# ANTHROPIC_API_KEY quando arriverà.
#
# ❗ Deve restare corto. Nel testo dell'errore pydantic accorcia i valori lunghi
# tenendone solo la parte finale ('...ant-NON-DEVE-COMPARIRE'): un controllo
# sulla stringa intera non la troverebbe, e il test passerebbe nonostante la
# fuga. È successo alla prima stesura di questo test.
SEGRETO = "chiave-finta-42"


def test_env_e_obbligatoria(monkeypatch: pytest.MonkeyPatch) -> None:
    """Senza ENV, né nell'ambiente né in un file, i settings non si creano."""
    monkeypatch.delenv("ENV", raising=False)

    with pytest.raises(ValidationError, match="ENV"):
        Settings(_env_file=None)


def test_l_errore_non_riporta_i_valori_letti(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Il testo dell'errore finisce nei log: non deve contenere i valori.

    Per un campo mancante pydantic riporta, di default, l'intero dizionario di
    ciò che ha letto. Un segreto presente nell'ambiente finirebbe nel log
    d'avvio proprio quando la configurazione è sbagliata.
    """
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.setenv("BACKEND_CORS_ORIGIN", SEGRETO)

    with pytest.raises(ValidationError) as info:
        Settings(_env_file=None)

    assert SEGRETO not in str(info.value)


def test_carica_settings_restituisce_i_settings_se_la_configurazione_e_valida(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Il caso felice: il controllo non deve ostacolare un avvio corretto."""
    monkeypatch.setenv("ENV", "PROD")

    settings = carica_settings(env_file=None)

    assert settings.ENV is Env.PROD


def test_carica_settings_ferma_l_avvio_con_un_messaggio_chiaro(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Il messaggio nomina la variabile, dice dove trovare l'elenco, e non riporta
    alcun valore.

    Accetta sia `SystemExit` sia un'eccezione derivata da `RuntimeError`: la
    scelta fra le due è una decisione del passo, e il test non la prende al
    posto di chi la scrive.
    """
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.setenv("BACKEND_CORS_ORIGIN", SEGRETO)

    with pytest.raises((SystemExit, RuntimeError)) as info:
        carica_settings(env_file=None)

    messaggio = str(info.value)
    assert "ENV" in messaggio, f"il messaggio non nomina la variabile: {messaggio!r}"
    assert ".env.example" in messaggio, f"il messaggio non rimanda all'esempio: {messaggio!r}"
    assert SEGRETO not in messaggio, "il messaggio riporta un valore letto dall'ambiente"


def test_l_esempio_basta_a_far_partire_l_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Chi clona copia `.env.example` in `.env` e avvia: deve funzionare.

    Ogni variabile obbligatoria va documentata nell'esempio con un valore
    valido. Le si toglie tutte dall'ambiente, così che il test non passi per
    merito di un valore impostato altrove.
    """
    obbligatorie = [nome for nome, campo in Settings.model_fields.items() if campo.is_required()]
    assert obbligatorie, "Settings non dichiara nessuna variabile obbligatoria"
    for nome in obbligatorie:
        monkeypatch.delenv(nome, raising=False)

    documentate = _nomi_nell_esempio()
    mancanti = [nome for nome in obbligatorie if nome not in documentate]
    assert not mancanti, f"obbligatorie ma assenti da .env.example: {mancanti}"

    Settings(_env_file=ESEMPIO)


def test_l_esempio_non_contiene_variabili_sconosciute() -> None:
    """
    Un nome scritto male nell'esempio verrebbe ignorato in silenzio.

    `extra="ignore"` scarta le variabili che Settings non conosce: un refuso
    copiato dall'esempio nel `.env` non produrrebbe alcun errore, e il valore
    non arriverebbe mai all'applicazione.
    """
    sconosciute = _nomi_nell_esempio() - set(Settings.model_fields)

    assert not sconosciute, f"variabili in .env.example che Settings non conosce: {sconosciute}"


def _nomi_nell_esempio() -> set[str]:
    """I nomi delle variabili assegnate in `.env.example`, commenti esclusi."""
    righe = ESEMPIO.read_text(encoding="utf-8").splitlines()
    return {
        riga.split("=", 1)[0].strip()
        for riga in righe
        if "=" in riga and not riga.lstrip().startswith("#")
    }
