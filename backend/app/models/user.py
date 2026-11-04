from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Un utente registrato: la tabella users."""

    __tablename__ = "users"

    # Ciascun utente ha un id progressivo: più semplice
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    # Il timestamp di creazione, per semplicità, lo gestisce Python.
    # SQLite non conserva il fuso orario.
    creato_il: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
