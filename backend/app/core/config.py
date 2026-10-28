from enum import Enum
from pathlib import Path

from pydantic import AnyHttpUrl, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Il file che marca la radice del backend. Il Pipfile definisce le dipendenze
# del progetto Python, quindi per costruzione non può stare altrove.
MARCATORE_RADICE = "Pipfile"


def risali_fino_al_marcatore(partenza: Path, marcatore: str = MARCATORE_RADICE) -> Path:
    """
    Risale l'albero delle cartelle da `partenza` e ritorna la prima che
    contiene `marcatore`.

    Solleva RuntimeError se non lo trova. Un percorso di configurazione
    sbagliato deve fallire subito e a voce alta: pydantic-settings ignora in
    silenzio un `env_file` inesistente, quindi senza questa eccezione
    l'applicazione partirebbe con tutti i valori di default e senza indizi.
    """
    for candidato in (partenza, *partenza.parents):
        if (candidato / marcatore).is_file():
            return candidato
    raise RuntimeError(
        f"Radice del backend non trovata: nessun '{marcatore}' risalendo da {partenza}"
    )


def get_backend_root() -> Path:
    """
    Ritorna la radice del backend, cioè la cartella che contiene il Pipfile e
    il file `.env`.

    Non conta i livelli con `parents[n]`: quel conteggio lega il percorso alla
    posizione esatta di questo modulo, e annidarlo di una sola cartella
    sposterebbe la radice senza che nulla segnali l'errore.
    """
    return risali_fino_al_marcatore(Path(__file__).resolve().parent)


DOTENV = get_backend_root() / ".env"


class Env(Enum):
    DEV = "DEV"
    TEST = "TEST"
    PROD = "PROD"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        hide_input_in_errors=True,
    )

    ENV: Env

    PROJECT_NAME: str = "chiaro-privacy"

    API_PREFIX: str = "/api"

    # ❗ Il passo 1.2 è dedicato al CORS: questo campo, in questo passo, non si tocca.
    BACKEND_CORS_ORIGIN: str | AnyHttpUrl = Field(default="", alias="BACKEND_CORS_ORIGIN")


def carica_settings(env_file: Path | None = DOTENV) -> Settings:
    """
    Crea i settings. Se la configurazione non è valida, ferma l'avvio con un
    messaggio che dice quali variabili correggere, senza riportarne i valori.

    `env_file` esiste per i test: `None` vuol dire «non leggere nessun file .env».
    """
    try:
        settings = Settings(_env_file=env_file)  # pyright: ignore[reportCallIssue]
        return settings
    except ValidationError as e:
        error_message: str = "Configurazione dei settings non valida.\n"
        for element in e.errors():
            error_message += f"{element['loc'][0]}: {element['msg']}\n"
        error_message += (
            "Verificare che l'.env file fornito rispetti la struttura "
            "del file di environment di esempio .env.example."
        )
        # Lancio SystemExit perché non c'è nessun Exception da catturare/gestire,
        # se fallisco a istanziare i settings l'app si deve schiantare con quel messaggio.
        raise SystemExit(error_message) from None


settings = carica_settings()
