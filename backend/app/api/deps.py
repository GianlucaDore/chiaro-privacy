"""
Le dipendenze condivise dalle rotte: per ora, la sessione del database.

Una dipendenza è una funzione che FastAPI chiama prima della rotta, e il cui
risultato consegna alla rotta come parametro. Qui la dipendenza è get_db: a
ogni richiesta apre una sessione, la presta alla rotta e la chiude a lavoro
finito.
"""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Iterator[Session]:
    """Una sessione per richiesta: aperta prima della rotta, chiusa sempre dopo."""
    session = SessionLocal()
    # Se la rotta solleva un'eccezione, FastAPI la rilancia qui, sulla riga dello yield.
    # Il finally non la cattura: chiude la sessione e la lascia proseguire, e la risposta
    # è un 500. `with SessionLocal() as session:` farebbe lo stesso; try/finally rende
    # visibile il punto in cui la chiusura avviene.
    try:
        yield session
    finally:
        session.close()


# La forma con cui le rotte chiedono la sessione: `def rotta(sessione: SessionDep)`.
# Annotated unisce in un nome solo il tipo, per pyright e per l'editor, e la
# dipendenza, per FastAPI: così Depends(get_db) non si ripete in ogni rotta.
# ❗ A Depends si passa la funzione, get_db, non il suo risultato, get_db():
# a chiamarla è FastAPI.
SessionDep = Annotated[Session, Depends(get_db)]
