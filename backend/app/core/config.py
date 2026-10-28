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

    # ─── PASSO 1.2 · 🔴 · briefing docs/passi/1.2.md ───────────────────────
    # Qui ci sono i cartelli 2 e 3. Cancellali quando li hai fatti, insieme a
    # questa riga.
    #
    # TODO(1.2/2) — un tipo che dica la verità
    #   Da scrivere: il campo diventa una stringa semplice, con la stringa
    #     vuota come default. Via `AnyHttpUrl` e via `Field(...)`: cancella
    #     anche i due import in cima al file, se nessun altro li usa (ruff F401).
    #   Perché: `str | AnyHttpUrl` non valida niente. Una union prova i tipi
    #     in ordine, e qualunque testo è già una `str`: "ciao", "*" e
    #     "http://localhost:5173/" passano tutti. L'alias, poi, è identico al
    #     nome del campo, quindi non cambia nulla. Il controllo vero lo fa
    #     TODO(1.2/3).
    BACKEND_CORS_ORIGIN: str | AnyHttpUrl = Field(default="", alias="BACKEND_CORS_ORIGIN")

    # TODO(1.2/3) — l'origine sbagliata ferma l'avvio
    #   Sintassi: un metodo della classe, decorato così (briefing 4.2):
    #       @field_validator("NOME_DEL_CAMPO")
    #       @classmethod
    #       def nome(cls, valore: str) -> str:
    #     field_validator si importa da pydantic.
    #   Da scrivere: il validatore di BACKEND_CORS_ORIGIN. Chiama
    #     leggi_origini() (da app.core.cors) sul valore, solo per controllarlo,
    #     e restituisce il valore ricevuto.
    #   Perché: un ValueError sollevato dentro un validatore diventa un
    #     ValidationError, e il ValidationError arriva a carica_settings():
    #     un'origine scritta male ferma l'app all'avvio, con il tuo messaggio
    #     del passo 1.1, invece di far fallire in silenzio ogni chiamata.
    #   Trappola: il validatore NON deve restituire la lista: il campo è una
    #     stringa, e la stringa resta. La lista la ricava main.py, chiamando
    #     di nuovo leggi_origini() (TODO(1.2/5)).


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
