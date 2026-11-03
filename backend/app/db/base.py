"""
La classe base di tutti i modelli SQLAlchemy.

Ogni modello eredita da `Base`. Ereditando, la classe si iscrive in
`Base.metadata`, il registro delle tabelle: è da lì che `create_all` sa quali
tabelle creare. Una classe che nessuno importa non si iscrive, e la sua tabella
non viene creata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """La base comune: non ha colonne, serve solo a tenere il registro."""
