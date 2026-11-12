"""
Il servizio degli utenti: la logica che li riguarda, senza database.

Riceve un UserRepository nel costruttore e a lui chiede i dati. Non sa se
dietro ci sono SQLite, un altro database o un dizionario: per questo si prova
con un repository finto, e per questo non importa SQLAlchemy.
"""

# ❗ Si importa solo il contratto. Un import di app.models o di sqlalchemy,
# anche solo per un'annotazione, caricherebbe SQLAlchemy.
from app.repositories.user import UserRepository, Utente


class UserService:
    repository: UserRepository

    def __init__(self, repository: UserRepository) -> None:
        # Quale implementazione ricevere lo decide chi costruisce il servizio:
        # il test gli dà un dizionario, l'app gli darà SQLAlchemy.
        self.repository = repository

    def crea_utente(self, email: str) -> Utente:
        return self.repository.aggiungi(email=email)

    def trova_utente(self, email: str) -> Utente | None:
        return self.repository.cerca_per_email(email=email)
