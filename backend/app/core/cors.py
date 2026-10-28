# ─────────────────────────────────────────────────────────────────────────────
# PASSO 1.2 · 🔴 zona rossa · lo scrivi tu, da zero
# Criterio: una richiesta con un Origin non in elenco viene rifiutata,
#           verificabile con curl.
# Briefing: docs/passi/1.2.md · Bersaglio: tests/test_cors.py, oggi rosso.
# Qui ci sono i cartelli 1 e 4. Cancella ognuno quando l'hai fatto, e a fine
# passo anche questa intestazione.
# ─────────────────────────────────────────────────────────────────────────────
"""
La politica CORS dell'applicazione, in un posto solo.

Due funzioni separate perché hanno due momenti diversi: `leggi_origini` serve
ai settings, all'avvio, per rifiutare una configurazione sbagliata prima che
l'app parta; `aggiungi_cors` serve a `main.py`, per registrare il middleware.
Stando qui, entrambe si possono provare da sole, su un'app di prova.
"""

from fastapi import FastAPI


def leggi_origini(valore: str) -> list[str]:
    """
    Trasforma il valore di BACKEND_CORS_ORIGIN nell'elenco delle origini ammesse.

    Il valore è un'origine sola oppure più origini separate da virgole. Un
    valore vuoto vuol dire «nessuna origine»: restituisce una lista vuota.
    Solleva ValueError, con un messaggio che nomina l'origine sbagliata, se una
    delle voci non è un'origine valida.
    """
    # TODO(1.2/1) — dal testo all'elenco, rifiutando le origini sbagliate
    #   Sintassi: valore.split(",") divide il testo; .strip() toglie gli spazi;
    #     urlsplit(origine) da urllib.parse smonta un URL in scheme, netloc,
    #     path, query, fragment (briefing 4.1, con l'output reale su ogni caso).
    #   Da scrivere:
    #     - dividi sulle virgole, togli gli spazi, salta le voci vuote;
    #     - per ogni voce, solleva ValueError se:
    #         · è "*" (briefing 1.3: con le credenziali Starlette rimanda
    #           l'origine di chiunque);
    #         · lo schema non è http o https;
    #         · manca l'host (netloc vuoto);
    #         · c'è qualcosa dopo l'host: un percorso, anche solo "/", una
    #           query o un frammento (briefing 3: la barra finale non combacia mai);
    #     - restituisci l'elenco delle origini valide.
    #   Decisione — le maiuscole (briefing 3). Il browser manda l'origine in
    #     minuscolo, e il confronto è fra stringhe esatte. Scegline una, e
    #     scrivi il perché in un commento:
    #     A) rifiutarle con un ValueError: la configurazione resta esattamente
    #        quella scritta, e chi la scrive impara la forma giusta;
    #     B) portarle in minuscolo: più indulgente, ma l'elenco usato dal
    #        middleware non è più identico a quello scritto nel .env.
    #   Perché: un'origine scritta male non dà nessun errore al middleware,
    #     semplicemente non combacia mai. Rifiutarla qui la trasforma in un
    #     errore all'avvio, con il messaggio che hai scritto al passo 1.1.
    #   Trappola: il messaggio del ValueError finisce nei log d'avvio. Nominare
    #     l'origine va bene, perché un'origine non è un segreto.
    raise NotImplementedError("TODO(1.2/1)")


def aggiungi_cors(app: FastAPI, origini: list[str]) -> None:
    """
    Registra il CORSMiddleware sull'app, con la politica di Chiaro.

    Va chiamata solo con un elenco non vuoto: senza origini, nessun
    middleware, e il browser applica la same-origin policy pura.
    """
    # TODO(1.2/4) — la politica CORS, decisa
    #   Sintassi: app.add_middleware(CORSMiddleware, allow_origins=...,
    #     allow_credentials=..., allow_methods=[...], allow_headers=[...]).
    #     CORSMiddleware si importa da fastapi.middleware.cors. Ogni opzione è
    #     spiegata nel briefing, sezione 4.3.
    #   Da scrivere: la chiamata, con le origini ricevute e un valore deciso per
    #     ciascuna delle altre tre opzioni. Sopra ognuna, una riga di commento
    #     che dica perché quel valore.
    #   Decisione — le credenziali (briefing 2.3). Dalla fase 2 la sessione è un
    #     cookie, e al passo 3.5 il frontend chiamerà l'API con
    #     credentials: 'include'. Scrivi quale valore serve, e cosa si
    #     romperebbe con l'altro.
    #   Decisione — i metodi. Le operazioni previste dalla scaletta: leggere
    #     (il proprio profilo, le analisi), creare (registrazione, login,
    #     logout, una nuova analisi), modificare in parte un rilievo
    #     (verificato o contestato, passo 5.7), cancellare l'account (B.1).
    #     Scegli una strada, e scrivi il perché:
    #     A) elencare già tutti i metodi che il piano prevede: nessuna sorpresa
    #        quando arriveranno quelle rotte;
    #     B) elencare solo quelli usati presto, e aggiungere gli altri con il
    #        passo che li introduce: il minimo indispensabile, al prezzo di
    #        doversene ricordare (te lo ricorderebbe un errore CORS nel browser).
    #   Da scrivere, per gli header: un elenco esplicito degli header di
    #     richiesta che il frontend manderà oggi. Le chiamate dell'API hanno un
    #     corpo JSON: pensa a quale header lo dichiara.
    #   Trappola: "*" in metodi e header sembra comodo, ma Starlette lo
    #     traduce in «tutto ciò che mi chiedono» (briefing 3, output reale).
    #   ❗ Non aggiungere ora l'header del token CSRF: arriva con il passo 2.8,
    #     insieme al motivo per cui serve.
    raise NotImplementedError("TODO(1.2/4)")
