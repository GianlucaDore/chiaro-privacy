# ─────────────────────────────────────────────────────────────────────────────
# PASSO 1.1 · 🟡 zona gialla · lo scrivi tu
# Criterio: l'app fallisce al boot con un errore chiaro se manca una variabile
#           obbligatoria.
# Briefing: docs/passi/1.1.md · Bersaglio: i test «Passo 1.1» in fondo a
#           tests/test_config.py, cinque dei quali oggi rossi.
# Qui ci sono i cartelli 1, 2, 3 e 4. Cancella ognuno quando l'hai fatto, e a
# fine passo anche questa intestazione.
# ─────────────────────────────────────────────────────────────────────────────
import os
from enum import Enum
from pathlib import Path

from pydantic import AnyHttpUrl, Field
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
    # TODO(1.1/2) — l'errore smette di stampare i valori
    #   Sintassi: un'opzione in più dentro le parentesi di SettingsConfigDict.
    #   Forma:    hide_input_in_errors=True
    #   Perché: quando una variabile manca, pydantic scrive nel messaggio
    #     d'errore TUTTI i valori che ha letto, segreti compresi, e l'errore
    #     d'avvio finisce nei log. L'output reale è nel briefing, sezione 1.3.
    #   Trappola: nasconde i valori solo nel TESTO dell'errore. La lista di
    #     errore.errors() li contiene ancora, nella chiave "input": in
    #     TODO(1.1/3) quella chiave non va mai usata.
    model_config = SettingsConfigDict(
        env_file=DOTENV, env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # TODO(1.1/1) — ENV diventa obbligatoria
    #   Sintassi: un campo senza `=` è obbligatorio.   Forma: NOME: Tipo
    #   Da scrivere: lascia solo nome e tipo, e togli tutto da `=` in poi. Poi
    #     cancella `import os` in cima al file, che resta inutilizzato (ruff
    #     lo segnala come F401), e il commento ❗ qui sotto.
    #   Perché: con un default, una ENV dimenticata o scritta male in produzione
    #     fa partire l'app in DEV: /docs pubblica, niente HSTS, log in DEBUG.
    #     Senza default, l'avvio si ferma e dice cosa manca (briefing 1.1, 1.2).
    #   Trappola: os.getenv dentro un campo è una seconda fonte di verità.
    #     pydantic-settings legge già l'ambiente, e in più legge il .env, che
    #     os.getenv invece ignora (briefing 2.1).
    #   ⚠️ Subito dopo, `pipenv run test` si ferma con "ERROR collecting": è
    #     previsto, lo sistema TODO(1.1/5) in conftest.py. E pyright segnalerà
    #     l'ultima riga del file: lo sistema TODO(1.1/4).
    ENV: Env = Env(os.getenv("ENV", "DEV"))

    PROJECT_NAME: str = "chiaro-privacy"

    API_PREFIX: str = "/api"

    # ❗ TODO(1.1/1): questo commento va cancellato insieme al default di ENV.
    #   Viene da un altro progetto e insegna proprio lo schema che il passo toglie.
    # Dichiarare variabili d'ambiente dall'env file nella forma:
    # VARIABLE_NAME = os.getenv("VARIABLE_NAME_IN_ENV_FILE")
    # es.: INTERCENTER_ENDPOINT: str = os.getenv('INTERCENTER_ENDPOINT')

    # ❗ Il passo 1.2 è dedicato al CORS: questo campo, in questo passo, non si tocca.
    BACKEND_CORS_ORIGIN: str | AnyHttpUrl = Field(default="", alias="BACKEND_CORS_ORIGIN")


def carica_settings(env_file: Path | None = DOTENV) -> Settings:
    """
    Crea i settings. Se la configurazione non è valida, ferma l'avvio con un
    messaggio che dice quali variabili correggere, senza riportarne i valori.

    `env_file` esiste per i test: `None` vuol dire «non leggere nessun file .env».
    """
    # TODO(1.1/3) — il messaggio chiaro
    #   Sintassi: try: … except ValidationError as errore:  (si importa da
    #     pydantic). errore.errors() è una lista di dizionari: "loc" è una tupla
    #     con il nome della variabile, "msg" è il motivo. Un esempio completo è
    #     nel briefing, sezione 4.
    #   Da scrivere:
    #     - nel try, crea e restituisci i settings, passando env_file al
    #       parametro `_env_file` di Settings;
    #     - nell'except, costruisci un messaggio fatto di: una riga che dice che
    #       la configurazione non è valida; una riga per ogni errore, con il nome
    #       della variabile e il motivo; il rimando a backend/.env.example;
    #     - ferma l'avvio con quel messaggio, e cancella il raise qui sotto.
    #   Decisione — come fermare l'avvio (briefing 2.4). Scegline una, e scrivi
    #     il perché in un commento sopra il raise:
    #     A) raise SystemExit(messaggio): solo il messaggio, codice d'uscita 1,
    #        niente traceback. Un `except Exception` non la intercetta.
    #     B) un'eccezione tua, class ConfigurazioneNonValida(RuntimeError):
    #        traceback completo e messaggio in fondo. Si intercetta come le altre.
    #   Trappola: mai e["input"] nel messaggio. Con B serve anche `from None`,
    #     altrimenti il ValidationError originale si ristampa sopra il tuo.
    #   Trappola: pyright segnala la riga con Settings(...): "Argument missing
    #     for parameter ENV" e "No parameter named _env_file". È un falso
    #     positivo noto (briefing 2.6), e si silenzia a fine riga con
    #     # pyright: ignore[reportCallIssue]
    raise NotImplementedError("TODO(1.1/3)")


# TODO(1.1/4) — l'avvio passa da carica_settings()
#   Da scrivere: al posto di Settings(), chiama carica_settings().
#   Perché: questa riga gira all'import del modulo, cioè all'avvio di uvicorn e
#     di pytest. È il punto in cui il messaggio chiaro deve comparire.
#   Trappola: lasciata com'è, all'avvio compare l'errore lungo di pydantic, e
#     pyright segnala questa riga per lo stesso motivo descritto in TODO(1.1/3).
settings = Settings()
