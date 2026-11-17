"""
Test del passo 1.7: la suite ha un database suo, e non tocca quello di sviluppo.

Usano due fixture che questo file non definisce, `engine` e `client`: pytest le
trova in `tests/conftest.py`, che le condivide con tutta la suite.

La rotta di prova scrive un utente con la sessione che riceve da `SessionDep`,
cioè dalla dipendenza vera. Su quale database finisca lo decide l'override
scritto nella fixture `client`. La rotta viene aggiunta all'app vera e tolta a
fine test, come in `test_errori.py`.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.api.deps import SessionDep
from app.core.config import get_backend_root
from app.main import app
from app.models import User

DB_DI_SVILUPPO = get_backend_root() / "data" / "chiaro.db"
ROTTA_DI_PROVA = "/prova/utenti"


def punta_al_db_di_sviluppo(motore: Engine) -> bool:
    """Vero se il motore scrive sul file del database di sviluppo."""
    database = motore.url.database
    if not database or database == ":memory:":
        return False
    return Path(database).resolve() == DB_DI_SVILUPPO.resolve()


def crea_utente(email: str, sessione: SessionDep) -> None:
    """La rotta di prova: scrive un utente e conferma la transazione."""
    sessione.add(User(email=email))
    sessione.commit()


@pytest.fixture(autouse=True)
def rotta_di_prova(request: pytest.FixtureRequest) -> Iterator[None]:
    """
    Aggiunge la rotta di prova all'app, e la toglie a fine test.

    Prima, se il test chiede `client`, controlla che l'app non punti al
    database di sviluppo: aprendo il client parte il lifespan, che crea le
    tabelle con il motore dell'app, e lo farebbe prima ancora del test.
    """
    from app.db.session import engine as motore_dell_app

    if "client" in request.fixturenames and punta_al_db_di_sviluppo(motore_dell_app):
        pytest.fail("l'app punta al DB di sviluppo: DATABASE_URL va impostata in conftest.py")

    app.add_api_route(ROTTA_DI_PROVA, crea_utente, methods=["POST"])
    yield
    app.router.routes[:] = [
        r for r in app.router.routes if getattr(r, "path", None) != ROTTA_DI_PROVA
    ]


def test_nei_test_l_app_non_punta_al_db_di_sviluppo() -> None:
    """
    Il motore dell'app nasce all'import di `app.db.session`, con DATABASE_URL.
    Se nei test vale ancora quello di sviluppo, tutto ciò che non passa da
    `get_db` finisce lì: il lifespan, per esempio.
    """
    from app.db.session import engine

    assert not punta_al_db_di_sviluppo(engine), f"il motore dell'app usa {engine.url}"


def test_una_richiesta_scrive_nel_db_dei_test(client: TestClient, engine: Engine) -> None:
    """
    È il criterio del passo. La rilettura usa una sessione nuova sul motore dei
    test: se l'utente si trova lì, la rotta ha lavorato su quel database.
    """
    risposta = client.post(ROTTA_DI_PROVA, params={"email": "ada@example.com"})

    assert risposta.status_code == 200, risposta.text
    with Session(engine) as sessione:
        assert sessione.scalars(select(User.email)).all() == ["ada@example.com"]


@pytest.mark.parametrize("giro", [1, 2])
def test_ogni_test_parte_da_un_db_vuoto(client: TestClient, engine: Engine, giro: int) -> None:
    """
    Lo stesso test due volte, con la stessa email. Se il database restasse da
    un test all'altro, al secondo giro la tabella non sarebbe vuota.
    """
    with Session(engine) as sessione:
        presenti = sessione.scalars(select(User.email)).all()
    assert presenti == [], f"giro {giro}: il DB contiene già {presenti}"

    risposta = client.post(ROTTA_DI_PROVA, params={"email": "ada@example.com"})

    assert risposta.status_code == 200, risposta.text


def test_finiti_i_test_con_client_non_resta_nessun_override() -> None:
    """
    `dependency_overrides` è un attributo dell'app, e l'app è una sola per
    tutta la suite: un override lasciato lì vale anche per i test successivi.

    ❗ Il test conta sull'ordine: pytest esegue i test nell'ordine del file, e
    questo viene dopo quelli che usano `client`.
    """
    assert app.dependency_overrides == {}, f"override rimasti: {app.dependency_overrides}"
