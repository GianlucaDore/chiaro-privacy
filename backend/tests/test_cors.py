"""
Test del passo 1.2: la politica CORS.

Le due funzioni di `app.core.cors` si provano da sole. `leggi_origini` è una
funzione pura, da testo a lista. `aggiungi_cors` si prova su un'app di prova
costruita qui, con una rotta sola: così i test non dipendono dall'ambiente in
cui gira la suite, né dalle rotte che l'API avrà in futuro.

Nessun test impone le decisioni del passo — quali metodi, credenziali sì o
no — tranne dove la scaletta le ha già prese: le origini sono un elenco
esplicito, `*` non è ammesso, e gli header non sono «tutti».
"""

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.core.cors import aggiungi_cors, leggi_origini

FRONTEND = "http://localhost:5173"
ESTRANEA = "https://sito-cattivo.example"

# I metodi che Starlette dichiara quando allow_methods è ["*"].
TUTTI_I_METODI = {"DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"}


# --- leggi_origini: dal testo all'elenco ------------------------------------


def test_un_valore_vuoto_vuol_dire_nessuna_origine() -> None:
    assert leggi_origini("") == []


def test_piu_origini_separate_da_virgole() -> None:
    """Gli spazi attorno alle virgole non contano, le voci vuote si saltano."""
    valore = "http://localhost:5173, https://chiaro.example:8443,"

    assert leggi_origini(valore) == ["http://localhost:5173", "https://chiaro.example:8443"]


@pytest.mark.parametrize(
    ("origine", "perche"),
    [
        ("*", "con le credenziali Starlette rimanda l'origine di chiunque"),
        ("http://localhost:5173/", "la barra finale non combacia mai con l'header Origin"),
        ("http://localhost:5173/app", "un'origine non ha percorso"),
        ("http://localhost:5173?x=1", "un'origine non ha query"),
        ("localhost:5173", "manca lo schema"),
        ("ftp://localhost:5173", "il browser manda solo http o https"),
        ("http://", "manca l'host"),
    ],
)
def test_le_origini_sbagliate_sono_rifiutate(origine: str, perche: str) -> None:
    """
    Un'origine sbagliata non dà errori al middleware: non combacia e basta.

    `perche` non serve al test: compare nel suo nome, così un fallimento dice
    da solo quale regola è stata violata.
    """
    with pytest.raises(ValueError):
        leggi_origini(origine)


def test_il_messaggio_nomina_l_origine_sbagliata() -> None:
    """In un elenco lungo, chi legge l'errore deve sapere quale voce correggere."""
    with pytest.raises(ValueError, match="localhost:9999/"):
        leggi_origini("http://localhost:5173, http://localhost:9999/")


# --- I settings rifiutano un'origine sbagliata all'avvio --------------------


def test_i_settings_rifiutano_un_origine_sbagliata(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    L'errore deve arrivare all'avvio, nel messaggio di `carica_settings`, e non
    come una chiamata CORS che fallisce in silenzio nel browser.
    """
    monkeypatch.setenv("ENV", "TEST")
    monkeypatch.setenv("BACKEND_CORS_ORIGIN", "*")

    with pytest.raises(ValidationError, match="BACKEND_CORS_ORIGIN"):
        Settings(_env_file=None)


def test_i_settings_accettano_un_origine_valida(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "TEST")
    monkeypatch.setenv("BACKEND_CORS_ORIGIN", FRONTEND)

    assert Settings(_env_file=None).BACKEND_CORS_ORIGIN == FRONTEND


# --- aggiungi_cors: il middleware su un'app di prova ------------------------


@pytest.fixture
def client() -> TestClient:
    """Un'app minima, con la politica CORS di Chiaro e il frontend come origine."""
    app = FastAPI()

    @app.get("/dati")
    def dati() -> dict[str, str]:
        return {"contenuto": "dati dell'utente"}

    aggiungi_cors(app, [FRONTEND])
    return TestClient(app)


def _preflight(
    client: TestClient, origine: str, metodo: str = "POST", header: str = "content-type"
) -> httpx.Response:
    return client.options(
        "/dati",
        headers={
            "Origin": origine,
            "Access-Control-Request-Method": metodo,
            "Access-Control-Request-Headers": header,
        },
    )


def test_il_frontend_supera_il_preflight(client: TestClient) -> None:
    """Un POST con corpo JSON dal frontend: il caso di quasi tutte le chiamate."""
    risposta = _preflight(client, FRONTEND)

    assert risposta.status_code == 200
    assert risposta.headers.get("access-control-allow-origin") == FRONTEND


def test_un_origine_estranea_e_rifiutata_al_preflight(client: TestClient) -> None:
    """
    È il criterio del passo. Il preflight rifiutato vuol dire che il browser
    non manderà la richiesta vera.
    """
    risposta = _preflight(client, ESTRANEA)

    assert risposta.status_code == 400
    assert "access-control-allow-origin" not in risposta.headers


def test_un_origine_estranea_non_puo_leggere_la_risposta(client: TestClient) -> None:
    """
    Una richiesta semplice arriva comunque, e il server risponde: il CORS non
    ferma la richiesta. Manca però il permesso di lettura, e senza quello il
    browser nasconde la risposta alla pagina. `curl` invece la legge lo stesso.
    """
    risposta = client.get("/dati", headers={"Origin": ESTRANEA})

    assert risposta.status_code == 200
    assert "access-control-allow-origin" not in risposta.headers


def test_un_header_non_dichiarato_e_rifiutato(client: TestClient) -> None:
    """Con allow_headers=["*"] Starlette rimanderebbe indietro qualsiasi header."""
    risposta = _preflight(client, FRONTEND, header="x-header-inventato")

    assert risposta.status_code == 400


def test_i_metodi_sono_un_elenco_esplicito(client: TestClient) -> None:
    """
    Quali metodi è una decisione del passo, e il test non la prende. Controlla
    solo che non siano «tutti», cioè che allow_methods non sia ["*"].
    """
    risposta = _preflight(client, FRONTEND)
    dichiarati = {
        m.strip() for m in risposta.headers.get("access-control-allow-methods", "").split(",")
    }

    assert dichiarati != TUTTI_I_METODI, "allow_methods equivale a ['*']"
