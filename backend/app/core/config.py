import os
import logging
from enum import Enum
from typing import Union
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


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
        f"Radice del backend non trovata: nessun '{marcatore}' "
        f"risalendo da {partenza}"
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
    
	model_config = SettingsConfigDict(env_file=DOTENV, env_file_encoding="utf-8", case_sensitive= True, extra="ignore")
 
	ENV: Env = Env(os.getenv('ENV', 'DEV'))

	PROJECT_NAME: str = "chiaro-privacy"

	API_PREFIX: str = "/api"

    # Dichiarare variabili d'ambiente dall'env file nella forma: VARIABLE_NAME = os.getenv("VARIABLE_NAME_IN_ENV_FILE")
	# es.: INTERCENTER_ENDPOINT: str = os.getenv('INTERCENTER_ENDPOINT')
	

	BACKEND_CORS_ORIGIN: Union[str, AnyHttpUrl] = Field(default='', alias='BACKEND_CORS_ORIGIN')



settings = Settings()

# TODO(0.5/13) Questa riga esiste identica anche in app/main.py:56, ed è
#              QUESTA a vincere: main.py importa app.core.config alla riga
#              3, quindi viene eseguita per prima, e `logging.basicConfig`
#              esce in silenzio se il logger radice ha già degli handler.
#              Quella in main.py non fa dunque assolutamente niente.
#              Una delle due va cancellata. Prima di scegliere, valuta se
#              un modulo di configurazione debba riconfigurare il logging
#              globale come effetto collaterale dell'import: `import`
#              dovrebbe dichiarare, non agire.
#              Il passo 1.8 sposterà tutto in app/core/logging.py, che oggi
#              è vuoto: questa è una decisione provvisoria.
logging.basicConfig(format='%(levelname)-9s %(asctime)s - %(name)s - %(message)s', level=logging.DEBUG if settings.ENV == Env.DEV else logging.INFO)

