"""
Test del passo 0.5: pulizia di `app/main.py`.

Coprono i quattro pezzi del criterio: gli header di sicurezza presenti nelle
risposte, le origini CORS lette dai settings invece che scritte a mano,
l'assenza di warning di deprecazione all'avvio, e la configurazione del logging
in un solo posto.

Al momento in cui questo file viene scritto **falliscono tutti e quattro**: è il
loro scopo.
"""

import re
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_backend_root
from app.main import app

# Header che il criterio del passo pretende su ogni risposta.
HEADER_ATTESI = (
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
)


def test_header_di_sicurezza_presenti_in_risposta() -> None:
    """
    Ogni risposta deve portare i tre header del criterio.

    Si interroga `/docs`, ma la scelta della rotta è irrilevante: un middleware
    agisce su tutte le risposte, comprese quelle di errore, ed è proprio questo
    che lo rende il posto giusto dove metterli.
    """
    client = TestClient(app)

    risposta = client.get("/docs")

    mancanti = [h for h in HEADER_ATTESI if h not in risposta.headers]
    assert not mancanti, f"header di sicurezza assenti: {mancanti}"


def test_x_frame_options_nega_l_inquadramento() -> None:
    """Non basta che l'header ci sia: deve dire la cosa giusta."""
    client = TestClient(app)

    risposta = client.get("/docs")

    assert risposta.headers.get("X-Frame-Options") == "DENY"
    assert risposta.headers.get("X-Content-Type-Options") == "nosniff"


def test_origini_cors_lette_dai_settings() -> None:
    """
    Le origini ammesse devono venire da `BACKEND_CORS_ORIGIN`, non da una
    stringa scritta nel codice.

    La verifica gira in un sottoprocesso perché `Settings` viene istanziato
    all'import di `app.core.config`: per cambiare la configurazione serve un
    interprete nuovo, non un monkeypatch a modulo già caricato.
    """
    codice = (
        "import sys; sys.path.insert(0, '.');"
        "from app.main import app;"
        "from fastapi.middleware.cors import CORSMiddleware;"
        "origini = next(m.kwargs['allow_origins'] for m in app.user_middleware"
        " if m.cls is CORSMiddleware);"
        "print('|'.join(origini))"
    )
    atteso = "http://esempio.test"

    esito = subprocess.run(
        [sys.executable, "-c", codice],
        cwd=get_backend_root(),
        capture_output=True,
        text=True,
        env={**_ambiente_base(), "ENV": "DEV", "BACKEND_CORS_ORIGIN": atteso},
    )

    assert esito.returncode == 0, esito.stderr
    origini = esito.stdout.strip().split("|")
    assert atteso in origini, (
        f"le origini ammesse sono {origini}: non derivano da BACKEND_CORS_ORIGIN"
    )


def test_nessun_warning_di_deprecazione_all_avvio() -> None:
    """
    L'applicazione deve importarsi senza warning di deprecazione.

    Il sottoprocesso gira con `-W error::DeprecationWarning`, che trasforma ogni
    warning in un'eccezione: se `on_event` è ancora in uso, l'import fallisce e
    il codice di uscita è diverso da zero.
    """
    esito = subprocess.run(
        [sys.executable, "-W", "error::DeprecationWarning", "-c",
         "import sys; sys.path.insert(0, '.'); import app.main"],
        cwd=get_backend_root(),
        capture_output=True,
        text=True,
        env=_ambiente_base(),
    )

    assert esito.returncode == 0, (
        "l'avvio produce un warning di deprecazione:\n"
        + esito.stderr.strip()[-600:]
    )


def test_logging_configurato_in_un_solo_posto() -> None:
    """
    `logging.basicConfig` va chiamato una volta sola in tutto il progetto.

    È una verifica sul codice sorgente e non sul comportamento, per una ragione
    precisa: la seconda chiamata **non fa niente e non segnala niente**, perché
    `basicConfig` esce in silenzio se il logger radice ha già degli handler.
    Non c'è quindi un comportamento osservabile da asserire — solo la presenza
    di due chiamate dove ne serve una.
    """
    radice = get_backend_root()
    chiamate = [
        f"{file.relative_to(radice)}:{n}"
        for file in radice.rglob("*.py")
        if ".venv" not in file.parts
        for n, riga in enumerate(file.read_text(encoding="utf-8").splitlines(), 1)
        if re.search(r"^\s*logging\.basicConfig\(", riga)
    ]

    assert len(chiamate) <= 1, f"basicConfig chiamato piu' volte: {chiamate}"


def _ambiente_base() -> dict[str, str]:
    """
    Ambiente minimo per un sottoprocesso Python su Windows.

    `SYSTEMROOT` e `PATH` servono al caricamento delle DLL di sistema: senza,
    l'interprete non parte affatto.
    """
    import os

    return {
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "PATH": os.environ.get("PATH", ""),
    }
