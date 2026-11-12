# Debito di apprendimento

Registro di ciò che è rimasto indietro, tenuto perché una scorciatoia annotata è una scelta
consapevole mentre una scorciatoia dimenticata è una deriva.

Il file ha tre sezioni, alimentate da tre meccanismi distinti:

| Sezione | Da dove arriva |
| --- | --- |
| [Codice scritto in deroga](#codice-scritto-in-deroga) | La valvola di sfogo della sezione 9 del `CLAUDE.md` |
| [Risposte sotto le tre stelle](#risposte-sotto-le-tre-stelle) | La valutazione delle risposte della sezione 6.1 |
| [Costrutti introdotti in zona verde](#costrutti-introdotti-in-zona-verde) | Il codice che scrivo io nei passi 🟢, quando usa qualcosa che l'autore non ha ancora scritto di suo |

---

## Codice scritto in deroga

Codice che avrei dovuto scrivere l'autore e che ho scritto io, con la data e cosa resta da
capire.

### 0.5 · Le decisioni sui response header · 13 settembre 2026

**Cosa ho scritto io.** L'intero blocco `SecurityHeadersMiddleware` di
[`backend/app/main.py`](backend/app/main.py), la gestione delle origini CORS e l'esposizione
condizionata della documentazione. L'autore ha implementato il passo — lifespan, CORS dai
settings, `basicConfig` unico — ma ha delegato esplicitamente la **scelta dei valori degli
header**, che era il cuore del passo.

**Le decisioni prese, e perché.**

| Decisione | Motivo |
| --- | --- |
| CSP `default-src 'none'` sulle risposte dell'API | una risposta JSON non deve caricare niente: è la raccomandazione OWASP per le API |
| CSP allargata solo sulle pagine HTML di `/docs` e `/redoc` | Swagger UI carica JS e CSS da `cdn.jsdelivr.net` e FastAPI genera uno `<script>` inline, che senza `'unsafe-inline'` non parte |
| **Documentazione disattivata in produzione** | è la conseguenza del punto sopra: non si possono avere insieme docs interattive e CSP stretta senza rattoppare l'HTML generato da FastAPI. Ed è comunque una mappa dell'API regalata a chiunque |
| `Cross-Origin-Embedder-Policy` **rimosso** | `require-corp` serve a ottenere l'isolamento cross-origin, che serve a `SharedArrayBuffer` e ai timer ad alta risoluzione. Niente di tutto ciò è in programma, e avrebbe bloccato gli asset di `/docs` |
| `report-to=default` **rimosso** da COOP e COEP | puntava a un gruppo di endpoint mai dichiarato con `Reporting-Endpoints`, e il nome andava fra virgolette. Non riportava niente a nessuno |
| `Cache-Control: no-store` ovunque **tranne** documentazione e schema | i dati dell'utente non vanno in cache; le pagine di `/docs` non contengono niente di personale |
| `Referrer-Policy: no-referrer` **aggiunto** | gli URL dell'API conterranno identificativi di analisi, che non devono finire nell'header `Referer` verso altri siti |
| HSTS attivo **solo in PROD**, senza `preload` | su HTTP semplice è inerte, e `preload` è una decisione che i browser ricordano per mesi |
| `X-Frame-Options` e `frame-ancestors` **tenuti entrambi** | ridondanza voluta: il secondo è il moderno, il primo copre i browser che non lo leggono |
| CORS registrato **solo se `BACKEND_CORS_ORIGIN` è valorizzato** | `[""]` è una lista che non ammette niente ma sembra configurata |
| Ordine dei middleware **lasciato com'era** | Starlette inserisce in testa, quindi il CORS registrato per ultimo è il più esterno: è l'ordine giusto, perché gli header CORS devono finire anche sulle risposte di errore |

**Cosa resta da capire.** La differenza fra ciò che protegge un header applicato al
*documento* (CSP, COOP, `X-Frame-Options`) e uno applicato alla *risorsa* (CORP), perché è
la ragione per cui metà di questi header non ha alcun effetto su una risposta JSON. E il
motivo per cui CORP non viene consultato sulle richieste in modalità CORS, che è il punto da
cui dipende il fatto che `same-origin` non ostacoli il frontend.

📄 [OWASP — HTTP Security Response Headers](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html) · [MDN — Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)

**Le cinque domande di verifica del passo sono rimaste senza risposta** e restano aperte in
[`docs/passi/0.5.md`](docs/passi/0.5.md).

### 1.2 · La regex delle origini · 30 ottobre 2026

**Cosa ho scritto io.** In [`backend/app/core/cors.py`](backend/app/core/cors.py), su due
richieste esplicite dell'autore:

- la costante `SCHEMA_ORIGINE`, cioè la regex che descrive un'origine valida. L'autore ha
  scelto la regex al posto di `urlsplit`;
- la seconda metà di `leggi_origini()`: il rifiuto di `*` con un messaggio suo, il controllo
  con `fullmatch` e il `ValueError` che nomina l'origine e mostra la forma giusta.

- il corpo di `aggiungi_cors()`, cioè la chiamata a `app.add_middleware(CORSMiddleware, ...)`
  con un commento per opzione.

Il ciclo che divide, ripulisce e scarta le voci vuote l'ha scritto l'autore, e così il
validatore dei settings (mosse 2 e 3). Le tre decisioni di `aggiungi_cors()` le ha prese
l'autore, rispondendo a tre domande: credenziali `True`, perché il login è un cookie; tutti i
metodi previsti dal piano (`GET`, `POST`, `PATCH`, `DELETE`); `Content-Type` come unico header,
distinto da `Accept`. Io le ho solo trascritte.

**La decisione presa al posto suo.** Le maiuscole si **rifiutano** invece di correggerle,
cioè la strada A del briefing. Così l'elenco usato dal middleware è esattamente quello
scritto nel `.env`, e chi lo scrive vede subito la forma giusta. La strada B, portarle in
minuscolo, sarebbe stata più indulgente, ma avrebbe fatto divergere il `.env` dall'elenco
effettivo.

**Cosa resta da capire.**

- Leggere la regex senza il commento accanto: `?` dopo un carattere e dopo un gruppo, le
  classi fra parentesi quadre, `\d{1,5}`.
- Perché `fullmatch` e non `match` o `search`. `match` accetterebbe
  `http://localhost:5173/` (combacia l'inizio), `search` anche `xx http://a.example`.
- Perché la si compila a livello di modulo e non dentro il ciclo.
- I limiti di una regex rispetto a un parser come `urlsplit`: un solo messaggio per tutti i
  casi, e gli indirizzi IPv6 esclusi.

📄 [Python — `re`, Regular expression operations](https://docs.python.org/3/library/re.html) · [regex101](https://regex101.com), con il dialetto Python

### 1.5 · Il repository di `User` · 12 novembre 2026

**Cosa ho scritto io.** L'autore ha chiesto di chiudere il passo da solo, per andare avanti.

- In [`backend/app/repositories/user_sqlalchemy.py`](backend/app/repositories/user_sqlalchemy.py),
  tutto:
  - la traduzione `_a_dominio`, riscritta: la bozza costruiva l'`Utente` vuoto per poi
    assegnargli i campi, non rimetteva il fuso orario e importava `Session` da pytest;
  - `aggiungi`, con `add` e `flush` ma senza `commit`;
  - `cerca_per_email`, con `select()`.
- La chiusura: il tipo di ritorno di `crea_utente`, i cartelli e le intestazioni.

L'autore ha scritto `Utente`, la struttura di `UserRepository` e `UserService`.

**Cosa resta da capire.** Il quadro d'insieme, cioè chi fa cosa fra `models/`,
`repositories/` e `services/`: è la sezione 0 del
[briefing](docs/passi/1.5.md). E le quattro domande di verifica, rimaste senza risposta:

1. *I test del servizio passano senza il repository vero: cosa dimostra?* Che il servizio
   dipende solo dal contratto, e funziona con qualunque implementazione, anche un dizionario.
   Quale riceve lo decide chi lo costruisce: il test, e nell'app la dipendenza del passo 2.2.
2. *Perché `Utente` e non `User`?* Per gli import: il modello carica SQLAlchemy, e il servizio
   non deve. Per le modifiche: `User` è osservato dalla sessione, e cambiarlo cambia il
   database al primo `commit`. Misurato: `u.email = u.email.upper()` → `ADA@EXAMPLE.COM`.
3. *`flush` contro `commit`?* `flush` scrive nella transazione aperta e la riga riceve l'`id`,
   ma un `rollback` lo annulla; `commit` conferma. Il repository fa `flush` per avere l'`id`;
   il `commit` spetta a chi conosce il lavoro intero.
4. *Perché il fuso orario si corregge nel repository?* Perché è una stranezza del database, e
   deve restare dove sta il database: ogni servizio riceve date già giuste. Senza correzione,
   il confronto con `datetime.now(UTC)` solleva `TypeError: can't compare offset-naive and
   offset-aware datetimes`, e la richiesta risponde 500.

📄 [Cosmic Python — Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html) · [SQLAlchemy — Flushing](https://docs.sqlalchemy.org/en/21/orm/session_basics.html#flushing) · [Python — Aware and naive objects](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects)

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

### 1.6 · Domanda 2 — Mai `str(exc)` nel body · ⭐⭐☆☆☆

**Domanda.** Perché nel body di un 500 non va mai `str(exc)`? Che cosa conteneva, nel caso
misurato, e a chi potrebbe servire?

**Risposta data.** Esporrebbe lo stack trace e i dettagli dell'architettura; `str(exc)` serve
alle funzioni di logging, non alle API.

**Correzione.** `str(exc)` non è lo stacktrace: è il solo messaggio, e basta quello. Misurato, il
messaggio di un `IntegrityError` contiene la query SQL, la tabella e la colonna (`users.email`), e
fra i parametri **l'email dell'utente**: un dato personale consegnato a chi ha provocato
l'errore. A chi attacca serve per ricavare la struttura del database e capire quali input mandano
il sistema in errore. Lo stacktrace, l'elenco delle chiamate, va solo nel log.

📄 [CWE-209 — Generation of Error Message Containing Sensitive Information](https://cwe.mitre.org/data/definitions/209.html) · [OWASP — Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)

### 1.6 · Domanda 4 — Perché `errori.py` non importa FastAPI · ⭐⭐☆☆☆

**Domanda.** Perché `ErroreDiDominio` sta in `app/core` e non importa FastAPI, mentre i gestori
stanno in `app/api`?

**Risposta data.** Separation of concerns: la classe è slegata dalle rotte, che non hanno bisogno
di `except` perché gli errori li cattura il middleware.

**Correzione.** Il motivo è **chi solleva** gli errori di dominio: servizi e repository, che non
devono sapere niente di FastAPI, come all'1.5 il servizio non doveva sapere niente di
SQLAlchemy. Se `errori.py` importasse FastAPI, ogni servizio si porterebbe dietro il framework
web. I gestori traducono in HTTP, e quindi stanno nello strato HTTP. E gli errori di dominio non
li cattura il middleware che abbiamo scritto, ma il gestore registrato con `exception_handler`:
sono due pezzi distinti.

📄 [Cosmic Python — Introduction: layered architecture](https://www.cosmicpython.com/book/introduction.html) · [FastAPI — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)

### 1.4 · Domanda 4 — Le sessioni mai chiuse · ⭐☆☆☆☆

**Domanda.** Un'applicazione dimentica di chiudere le sessioni. In sviluppo nessuno se ne
accorge; in produzione, dopo un'ora di traffico, ogni richiesta che tocca il database resta
appesa trenta secondi e poi risponde 500. Spiega il perché di tutti e due i comportamenti.

**Risposta data.** Interrotta: «In produzione, spesso il DB è configurato per chiudere una
transazione o una connessione».

**Correzione.** I trenta secondi non vengono dal database ma dal **pool**. Ogni sessione non
chiusa tiene in prestito la sua connessione, e il pool ne ha 15: 5 più 10 di scorta. In sviluppo
le richieste sono poche, e il garbage collector libera le sessioni abbandonate, restituendo le
connessioni, prima che finiscano. In produzione si accumulano più in fretta di quanto vengano
raccolte: quando sono tutte in prestito, ogni richiesta nuova aspetta `pool_timeout`, 30 secondi
di default, poi riceve `TimeoutError`, e FastAPI risponde 500. Misurato con un pool da una
connessione: `QueuePool limit of size 1 overflow 0 reached, connection timed out`.

📄 [SQLAlchemy — Connection Pooling](https://docs.sqlalchemy.org/en/21/core/pooling.html) · [SQLAlchemy — QueuePool limit reached](https://docs.sqlalchemy.org/en/21/errors.html#error-3o7r)

### 1.3 · Domanda 2 — Il modello che nessuno importa · ⭐⭐☆☆☆

**Domanda.** Hai scritto il modello `User`, ma nessuno importa `app/models/user.py`. L'app
parte? Cosa succede alla prima query, e perché nessuno ti avvisa prima?

**Risposta data.** L'app parte e la prima query dà errore. Poi la soluzione: `from app import
models` nel main «di modo che venga eseguita la creazione della tabella», e `__all__` che
rende i modelli disponibili.

**Correzione.** Manca il perché del silenzio. La classe si iscrive in `Base.metadata` solo
quando Python la esegue, cioè quando il suo file viene importato. Senza import `create_all`
trova un registro **vuoto**, non crea niente e non lo considera un errore; la prima query
fallisce con `no such table: users`. Due confusioni da sciogliere: importare **registra**, è
`create_all` che **crea**; e a registrare è la riga di import in `__init__.py`, non `__all__`,
che dichiara solo i nomi riesportati.

📄 [SQLAlchemy — Working with Database Metadata](https://docs.sqlalchemy.org/en/21/tutorial/metadata.html)

### 1.3 · Domanda 3 — Perché non si restituisce il modello · ⭐☆☆☆☆

**Domanda.** Perché l'API non deve mai restituire direttamente il modello `User`, ma uno
schema Pydantic separato? Fai un esempio concreto di cosa andrebbe storto.

**Risposta data.** Non scritta nel file. In conversazione: lo schema serve a evitare un errore
di tipi, segnalato da `pyright` e da Pydantic mentre si scrive, perché FastAPI pretende schemi
Pydantic.

**Correzione.** L'errore esiste ma lo dà **FastAPI all'avvio**, solo se il modello è il tipo di
ritorno, e si aggira togliendo l'annotazione. Il motivo vero è ciò che succede quando funziona:
la rotta spedisce **ogni colonna** del modello, anche quelle interne o aggiunte dopo. Misurato,
con una colonna `password_hash`:
`200 {"password_hash":"$argon2id$...","id":1,"email":"ada@example.com"}`. Lo schema non copia
il modello: elenca i soli campi che possono uscire, ed è il contratto da cui nascono i tipi del
frontend.

📄 [FastAPI — Response Model](https://fastapi.tiangolo.com/tutorial/response-model/) · [OWASP API3:2023 — Broken Object Property Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/)

### 1.3 · Domanda 4 — L'unicità nel database · ⭐⭐☆☆☆

**Domanda.** Perché l'unicità dell'email va messa nel database con `unique=True`, invece di
controllare nel codice «esiste già?» prima di inserire?

**Risposta data.** Perché un errore nell'implementazione del controllo farebbe inserire a
SQLAlchemy righe con email duplicate.

**Correzione.** Manca il motivo principale: **anche un controllo perfetto non basta**. Due
registrazioni contemporanee con la stessa email passano entrambe il «non esiste» e inseriscono
entrambe, perché fra la lettura e la scrittura c'è un istante scoperto. Il database controlla il
vincolo nello stesso momento in cui scrive, e rifiuta la seconda con `IntegrityError`. In più il
vincolo vale anche per chi scrive senza passare dall'app. Ad accettare o rifiutare la riga è il
database, non SQLAlchemy.

📄 [Time-of-check to time-of-use](https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use) · [SQLAlchemy — Unique Constraint](https://docs.sqlalchemy.org/en/21/core/constraints.html#unique-constraint)

### 0.6 · Domanda 4 — Chi emette l'errore sui tipi di React · ⭐⭐☆☆☆

**Domanda.** `react` e `@types/react` sono due pacchetti distinti. Se aggiorni solo il primo,
chi emette l'errore, e **quando** — mentre scrivi nell'editor, mentre compili, o mentre l'app
gira nel browser?

**Risposta data.** Dipende da cosa si scrive nell'editor; il mismatch «verrà segnalato dal
secondo quando si scrive nell'editor».

**Correzione.** L'errore lo emette **`tsc`**, non `@types/react`: un pacchetto di tipi è un
file di dichiarazioni, non un programma che esegue controlli. E i momenti sono **due su tre**:
nell'editor, dove gira un server TypeScript, **e in compilazione**, perché `npm run typecheck`
e il `tsc -b` della build sono lo stesso controllo. Nel browser non compare **niente**, perché
i tipi non esistono a runtime — ed è proprio questo il sintomo che inganna: l'app gira e `tsc`
protesta, quindi il guasto si cerca nel posto sbagliato.

📄 [TypeScript — Type Declarations](https://www.typescriptlang.org/docs/handbook/2/type-declarations.html)

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

---

## Costrutti introdotti in zona verde

Cose entrate nel codice perché le ho scritte io in un passo 🟢. Non sono scorciatoie — quei
passi sono miei per assegnazione — ma restano costrutti che l'autore non ha ancora usato di
propria mano, e che quindi non sono suoi finché non li riusa altrove.

### 0.7 · `satisfies` · 15 settembre 2026

**Cos'è.** Un operatore di TypeScript, dalla 4.9, che **verifica** che un valore rispetti un
tipo senza **imporglielo**. La differenza con l'annotazione `:` è cosa il compilatore ricorda
dopo il controllo.

| Come si scrive | Viene controllato? | Cosa TypeScript ricorda |
| --- | --- | --- |
| `const x = valore` | no | tutto |
| `const x: T = valore` | sì | solo `T` |
| `const x = valore satisfies T` | sì | tutto |

**Dov'è nel progetto.** Nel dizionario degli stili del layout, dove l'annotazione
`Record<string, SxProps<Theme>>` cancellava il fatto che le chiavi fossero cinque e note.
Con `satisfies` il vincolo viene comunque verificato, ma le chiavi restano quelle esatte —
quindi un refuso non compila e l'accesso non produce più un `| undefined`.

**Cosa resta da capire.** Quando l'annotazione è la scelta giusta, perché non sempre
`satisfies` è meglio: dove serve **vincolarsi a un contratto** e non far dipendere chi usa il
valore dalle sue specificità — il tipo di ritorno pubblico di una funzione, una variabile da
riassegnare — l'annotazione è corretta proprio perché dimentica.

📄 [TypeScript 4.9 — l'operatore `satisfies`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#the-satisfies-operator)

### 0.12 · Il workflow di GitHub Actions · 28 ottobre 2026

**Cos'è.** Un file YAML in `.github/workflows/` che GitHub esegue da solo quando succede
qualcosa nel repository. La struttura ha tre livelli, ed è tutto ciò che serve per leggerlo:

| Livello | Cosa dichiara |
| --- | --- |
| `on:` | **quando** parte: a ogni push, a ogni pull request |
| `jobs:` | **cosa** gira, ognuno su una macchina virtuale propria e in parallelo agli altri |
| `steps:` | **in che ordine**, dentro un job: o un'azione già pronta (`uses:`) o un comando (`run:`) |

**Dov'è nel progetto.** [`.github/workflows/ci.yml`](.github/workflows/ci.yml): due job,
frontend e backend, che eseguono gli stessi controlli del README.

**Cosa resta da capire.** Perché le azioni di terzi sono fissate all'**impronta di un commit**
e non all'etichetta `v7`: un'etichetta può essere spostata dal suo autore su codice diverso, e
la pipeline eseguirebbe quel codice con l'accesso al repository. È lo stesso ragionamento del
pinning esatto delle dipendenze, applicato a un altro anello della catena di fornitura.

📄 [GitHub — Sintassi dei workflow](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions) · [GitHub — Uso sicuro delle azioni di terzi](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions)

### 0.12b · Costruire una volta, promuovere · 28 ottobre 2026

**Cos'è.** Il principio per cui un'immagine si **costruisce una sola volta**, su `develop`, e
quando arriva in produzione non la si ricostruisce: le si aggiunge un'etichetta. Ciò che va
su `main` è quindi la stessa immagine provata, bit per bit, e non una copia che potrebbe
differire per una dipendenza scaricata in un altro momento.

**Dov'è nel progetto.** Il job `immagini` di [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
Porta con sé quattro costrutti nuovi del workflow:

| Costrutto | Cosa fa |
| --- | --- |
| `needs: [frontend, backend]` | il job aspetta che gli altri due siano verdi: l'equivalente degli `stages` di GitLab |
| `strategy.matrix` | lo stesso job ripetuto per ogni valore, qui una volta per immagine |
| `permissions:` sul job | dà la scrittura sui pacchetti solo a questo job, non a tutto il workflow |
| `$GITHUB_OUTPUT` e `steps.<id>.outputs` | un passo calcola un valore, quelli successivi lo leggono |

**Cosa resta da capire.** Perché per ritrovare l'immagine da promuovere si usa l'impronta
dell'**albero** e non quella del **commit**: il merge di `develop` su `main` crea un commit
nuovo, ma il contenuto dei file è identico, e l'albero descrive il contenuto.

📄 [GitHub — Pubblicare immagini Docker](https://docs.github.com/en/actions/use-cases-and-examples/publishing-packages/publishing-docker-images) · [Git — Oggetti albero](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
