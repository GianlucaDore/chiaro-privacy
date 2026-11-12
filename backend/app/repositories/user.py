"""
Il contratto fra il servizio e i dati degli utenti.

Qui sta che cosa il servizio può chiedere, non come glielo si procura: Utente
è la forma in cui un utente arriva al servizio, UserRepository l'elenco delle
operazioni. Il come sta nelle implementazioni: user_sqlalchemy.py per il
database vero, un dizionario nei test.
"""

# ❗ Niente import da sqlalchemy né da app.models: il servizio importa questo
# file, e si porterebbe dietro SQLAlchemy.
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Utente:
    """Un utente come lo vede il servizio: un oggetto Python puro e immutabile."""

    id: int
    email: str
    creato_il: datetime


class UserRepository(ABC):
    """Le operazioni che il servizio può chiedere sui dati degli utenti."""

    # Riceve l'email e non un Utente: id e data di creazione li decide il database.
    @abstractmethod
    def aggiungi(self, email: str) -> Utente: ...

    @abstractmethod
    def cerca_per_email(self, email: str) -> Utente | None: ...
