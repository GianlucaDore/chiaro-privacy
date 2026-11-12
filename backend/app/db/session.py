"""Il collegamento al database: il motore e la fabbrica di sessioni."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Env, settings

# Un engine solo per tutta l'app: tiene il pool di connessioni ed è costoso da creare.
# È pigro: il file del database non si apre finché non serve davvero.
# check_same_thread=False: il modulo sqlite3 di Python, per default, vieta di usare una
#   connessione da un thread diverso da quello che l'ha aperta. Il pool invece la presta
#   a thread diversi, una richiesta dopo l'altra e mai a due insieme. SQLAlchemy 2 lo
#   imposta già da solo per SQLite su file: la riga è ridondante, e resta per dichiararlo.
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENV is Env.DEV,
    connect_args={"check_same_thread": False},
)

# Ogni SessionLocal() è una sessione nuova, da aprire per un lavoro e chiudere.
SessionLocal = sessionmaker(bind=engine)
