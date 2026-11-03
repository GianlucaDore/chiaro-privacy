"""Il collegamento al database: il motore e la fabbrica di sessioni."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Env, settings

# Uno solo per tutta l'app: tiene il pool di connessioni ed è costoso da creare.
# È pigro: il file del database non si apre finché non serve davvero.
# check_same_thread=False: FastAPI usa la connessione da thread diversi da
# quello che l'ha aperta, e SQLite di suo lo vieterebbe.
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENV is Env.DEV,
    connect_args={"check_same_thread": False},
)

# Ogni SessionLocal() è una sessione nuova, da aprire per un lavoro e chiudere.
SessionLocal = sessionmaker(bind=engine)
