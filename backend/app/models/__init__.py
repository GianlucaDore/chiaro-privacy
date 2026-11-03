"""I modelli del database: importare questo pacchetto li registra tutti in Base.metadata."""

from app.models.user import User

__all__ = ["User"]
