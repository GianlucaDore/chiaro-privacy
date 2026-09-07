# Debito di apprendimento

Registro di ciò che è rimasto indietro, tenuto perché una scorciatoia annotata è una scelta
consapevole mentre una scorciatoia dimenticata è una deriva.

Il file ha due sezioni, alimentate da due meccanismi distinti del `CLAUDE.md`:

| Sezione | Da dove arriva |
| --- | --- |
| [Codice scritto in deroga](#codice-scritto-in-deroga) | La valvola di sfogo della sezione 9 |
| [Risposte sotto le tre stelle](#risposte-sotto-le-tre-stelle) | La valutazione delle risposte della sezione 6.1 |

---

## Codice scritto in deroga

Codice che avrei dovuto scrivere l'autore e che ho scritto io, con la data e cosa resta da
capire.

*Nessuna voce.*

> **Nota.** Il passo **0.3** è stato implementato da Claude su autorizzazione esplicita
> dell'autore, che ha però chiesto di **non** annotarlo qui. La deroga è comunque dichiarata
> in testa a [`docs/passi/0.3.md`](docs/passi/0.3.md), dove restano anche le cinque domande
> di verifica del passo.

---

## Risposte sotto le tre stelle

Le risposte alle domande di verifica dei briefing valutate **1 o 2 stelle su 5**. Non sono
bloccanti per la chiusura di un passo: sono qui perché vengano rilette.

Ogni voce riporta la domanda, la risposta data e la correzione. Le correzioni sono brevi per
scelta: dove il concetto richiede più spazio c'è il link a una risorsa che lo spiega.

### 0.4 · Domanda 1 — `Pipfile` contro `Pipfile.lock` · ⭐⭐☆☆☆

**Domanda.** Qual è la differenza fra il `Pipfile` e il `Pipfile.lock`, e perché entrambi
vanno committati mentre la cartella del venv no?

**Risposta data.** Il `Pipfile` è la lista della spesa; l'app non si costruisce senza che le
dipendenze siano soddisfatte; il lock viene creato da `pipenv install`.

**Correzione.** Delle tre parti della domanda ne è stata coperta una. Il lock contiene in
più le versioni **risolte** in modo esatto, le **dipendenze delle dipendenze** — che nel
`Pipfile` non compaiono — e un **hash** per archivio, verificato in installazione. Vanno
committati entrambi perché il `Pipfile` dichiara l'intenzione e il lock garantisce che due
macchine installino gli stessi bit. Il venv non si committa: è rigenerabile, pesa quanto
tutte le dipendenze, e contiene percorsi assoluti della macchina che l'ha creato.

📄 [Pipenv — Pipfile.lock e installazioni deterministiche](https://pipenv.pypa.io/en/latest/pipfile.html)

### 0.4 · Domanda 3 — Linter contro controllore di tipi · ⭐⭐☆☆☆

**Domanda.** Qual è la differenza fra ciò che trova un linter e ciò che trova un controllore
di tipi? Un esempio di problema che `ruff` vede e `pyright` no, e uno del contrario.

**Risposta data.** Distinzione corretta, ma con l'affermazione che «la libreria che permette
di tipizzare il python è Pydantic», e con l'esempio `while True is not !True` per `ruff`.
L'esempio per `pyright` — `return "a"` in una funzione annotata `-> bool` — era corretto.

**Correzione.** Due errori.

1. **Pydantic non serve a tipizzare Python.** Le annotazioni di tipo sono parte del
   linguaggio dalla PEP 484 (Python 3.5) e il modulo standard è `typing`. Pydantic **usa**
   quelle annotazioni per validare **a runtime**. Sono tre ruoli distinti: scrivere i tipi
   (linguaggio), verificarli staticamente (`pyright`), validare i dati in esecuzione
   (Pydantic). Distinzione da avere chiara dal passo 1.3, dove lo schema Pydantic è il
   contratto dell'API.
2. **`!` non è l'operatore di negazione in Python**, si scrive `not`. Quella riga è un errore
   di sintassi, respinto dal parser prima che un linter la esamini. L'intenzione era giusta:
   una condizione costante è proprio ciò che `ruff` segnala.

📄 [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) · [Pydantic — perché usa le annotazioni](https://docs.pydantic.dev/latest/why/)
