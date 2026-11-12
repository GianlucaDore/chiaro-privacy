"""
Gli errori previsti dell'app: quelli che fanno parte del dominio.

Un errore di dominio è un caso che l'app conosce e sa raccontare all'utente,
come un'email già registrata. Lo sollevano servizi e repository; il modo in cui
diventa una risposta HTTP sta in app/api/gestione_errori.py.
"""


# Ogni errore concreto è una classe figlia che ridefinisce i tre valori, e si
# solleva senza argomenti: `raise EmailGiaUsata()`. Niente import di FastAPI
# qui: lo useranno servizi e repository, e status_code è solo un numero.
class ErroreDiDominio(Exception):  # noqa: N818
    status_code: int = 400
    codice: str = "richiesta_non_valida"
    messaggio: str = "La richiesta non è valida."
