"""
La politica CORS dell'applicazione, in un posto solo.

Due funzioni separate perché hanno due momenti diversi: `leggi_origini` serve
ai settings, all'avvio, per rifiutare una configurazione sbagliata prima che
l'app parta; `aggiungi_cors` serve a `main.py`, per registrare il middleware.
Stando qui, entrambe si possono provare da sole, su un'app di prova.
"""

import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

SCHEMA_ORIGINE = re.compile(r"https?://[a-z0-9]([a-z0-9.-]*[a-z0-9])?(:\d{1,5})?")


def leggi_origini(valore: str) -> list[str]:
    """
    Trasforma il valore di BACKEND_CORS_ORIGIN nell'elenco delle origini ammesse.

    Il valore è un'origine sola oppure più origini separate da virgole. Un
    valore vuoto vuol dire «nessuna origine»: restituisce una lista vuota.
    Solleva ValueError, con un messaggio che nomina l'origine sbagliata, se una
    delle voci non è un'origine valida.
    """
    origini: list[str] = []
    for origine in valore.split(","):
        origine_pulita = origine.strip()
        if origine_pulita != "":
            # "*" ha un messaggio suo: è l'errore più pericoloso, e il motivo è
            # diverso da quello di un'origine scritta male.
            if origine_pulita == "*":
                raise ValueError(
                    "'*' non è ammesso: con i cookie, Starlette rimanderebbe "
                    "l'origine di chiunque. Elenca le origini una per una."
                )
            # Le maiuscole si rifiutano invece di correggerle: così l'elenco
            # usato dal middleware è esattamente quello scritto nel .env, e chi
            # lo scrive vede subito la forma giusta.
            if SCHEMA_ORIGINE.fullmatch(origine_pulita) is None:
                raise ValueError(
                    f"{origine_pulita!r} non è un'origine valida: la forma è "
                    "http(s)://host oppure http(s)://host:porta, in minuscolo, "
                    "senza barra finale né percorso."
                )
            origini.append(origine_pulita)
    return origini


def aggiungi_cors(app: FastAPI, origini: list[str]) -> None:
    """
    Registra il CORSMiddleware sull'app, con la politica di Chiaro.

    Va chiamata solo con un elenco non vuoto: senza origini, nessun
    middleware, e il browser applica la same-origin policy pura.
    """
    app.add_middleware(
        CORSMiddleware,
        # Solo le origini scritte nel .env, già controllate da leggi_origini().
        allow_origins=origini,
        # Dalla fase 2 il login è un cookie di sessione: senza credenziali il
        # cookie non viaggerebbe, e l'autenticazione si romperebbe in silenzio.
        allow_credentials=True,
        # Tutti i metodi che il piano prevede: leggere, creare, modificare in
        # parte un rilievo (5.7) e cancellare l'account (B.1). Nessuna sorpresa
        # quando arriveranno quelle rotte.
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        # Le chiamate mandano un corpo JSON, e Content-Type è l'header che lo
        # dichiara. Niente "*": Starlette lo leggerebbe come «qualsiasi header».
        allow_headers=["Content-Type"],
    )
