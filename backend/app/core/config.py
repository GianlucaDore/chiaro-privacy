import os
import logging
from enum import Enum
from typing import Union
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


def get_project_root() -> Path:
    """
    Ritorna la radice del progetto.
    Se questo file è in app/core/config.py -> parents[2] è la repo root.
    """
    return Path(__file__).resolve().parents[2]

    
DOTENV = (get_project_root() / ".env")

class Env(Enum):
	DEV = "DEV"
	TEST = "TEST"
	PROD = "PROD"


class Settings(BaseSettings):
    
	model_config = SettingsConfigDict(env_file=DOTENV, env_file_encoding="utf-8", case_sensitive= True, extra="ignore")
 
	ENV: Env = Env(os.getenv('ENV', 'DEV'))

	PROJECT_NAME: str = ""

	API_PREFIX: str = "/api"

    # Dichiarare variabili d'ambiente dall'env file nella forma: VARIABLE_NAME = os.getenv("VARIABLE_NAME_IN_ENV_FILE")
	# es.: INTERCENTER_ENDPOINT: str = os.getenv('INTERCENTER_ENDPOINT')
	

	BACKEND_CORS_ORIGIN: Union[str, AnyHttpUrl] = Field(default='', alias='BACKEND_CORS_ORIGIN')



settings = Settings()

logging.basicConfig(format='%(levelname)-9s %(asctime)s - %(name)s - %(message)s', level=logging.DEBUG if settings.ENV == Env.DEV else logging.INFO)

