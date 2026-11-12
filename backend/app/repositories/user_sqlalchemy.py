"""
Il contratto UserRepository realizzato con SQLAlchemy: gli utenti nel database.

È l'unico posto, insieme ad app/models/, che sa che gli utenti stanno in una
tabella. Riceve la sessione da fuori e traduce nei due versi: dall'email alla
riga, e dalla riga all'Utente.
"""

from datetime import UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user import UserRepository, Utente


def _a_dominio(riga: User) -> Utente:
    """Traduce la riga del database nell'Utente che vede il servizio."""
    # SQLite non conserva il fuso orario: riletto, creato_il torna senza tzinfo.
    # Lo si rimette qui, così la stranezza non esce dal repository.
    return Utente(id=riga.id, email=riga.email, creato_il=riga.creato_il.replace(tzinfo=UTC))


class SqlAlchemyUserRepository(UserRepository):
    session: Session

    def __init__(self, session: Session) -> None:
        # La sessione arriva da fuori: sarà quella della richiesta, la stessa
        # che get_db presta alla rotta.
        self.session = session

    def aggiungi(self, email: str) -> Utente:
        riga = User(email=email)
        self.session.add(riga)
        # flush scrive la riga nella transazione aperta, e solo da qui ha un id
        # e una data di creazione. Il commit no: confermare spetta a chi
        # conosce il lavoro intero, non a chi scrive una riga sola.
        self.session.flush()
        return _a_dominio(riga)

    def cerca_per_email(self, email: str) -> Utente | None:
        query = select(User).where(User.email == email)
        riga = self.session.scalars(query).one_or_none()
        return None if riga is None else _a_dominio(riga)
