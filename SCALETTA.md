# SCALETTA — Chiaro

**69 passi in 7 fasi, più un backlog.** È la spina dorsale del progetto e la fonte di verità unica
sull'avanzamento: il passo corrente è **il primo non spuntato**.

## Come si usa

| | |
|---|---|
| 🔴 **Zona rossa** | Lo scrivi tu da zero. Claude spiega, dà lo scheletro, scrive il test che fallisce, e ti interroga. Non scrive la soluzione |
| 🟡 **Zona gialla** | Claude spiega e ti interroga, tu scrivi |
| 🟢 **Zona verde** | Claude scrive, poi ti presenta la diff e te la spiega riga per riga. Spunti solo dopo aver rivisto **tutto** il codice |

**La casella la spunti tu, mai Claude.** Claude verifica il criterio, mostra l'output reale, e dice
«criterio soddisfatto, puoi spuntare X.Y». La spunta è la tua dichiarazione di aver capito.

Ogni passo ha un **criterio verificabile eseguendo qualcosa**, non a occhio. I passi 🔴 hanno anche
i *concetti da capire prima*; il briefing esteso viene scritto in `docs/passi/<id>.md` quando arrivi
a quel passo, non prima.

**Avanzamento: 1 / 69** — ultimo completato: nessuno · corrente: **0.2**

---

## Fase 0 — Fusione dei template e impianto — 25h

*Non si crea da zero: si fondono i due template esistenti, si correggono i bug trovati, e si
aggiunge ciò che manca a entrambi (test, linter, Docker, CI, Sonar).*

- [x] **0.1** 🟢 Albero combinato, con i file dei template al posto giusto — *l'albero corrisponde; `app/` esiste come pacchetto; nessuna cartella resta vuota nel clone*
- [ ] **0.2** 🟢 Git: repo, `.gitignore` unificato (corretta la doppia riga `.vscode/`), primo commit, repo pubblica su GitHub — *`git ls-files` mostra `.vscode/extensions.json` tracciato e nessun `.env`*
- [ ] **0.3** 🔴 **Correzione del bug `get_project_root()`** — *concetti: `Path.parents`, perché un percorso relativo al file è fragile, come si verifica* — *un test asserisce che `DOTENV` punta dentro la repo e che una variabile scritta nel `.env` arriva nei settings*
- [ ] **0.4** 🟡 Pipfile: aggiunto `pydantic-settings`, rimossi `pyjwt` e `cryptography`, aggiornati FastAPI e Pydantic, aggiunti pytest/ruff/pyright — *da venv vuoto `pipenv install && pipenv run dev` parte al primo colpo*
- [ ] **0.5** 🔴 `main.py` ripulito: lifespan invece di `on_event`, CORS da `BACKEND_CORS_ORIGIN`, `logging.basicConfig` una volta sola, **security headers attivati** — *concetti: cos'è il lifespan e perché ha sostituito gli event handler; cosa fa ciascuno dei security header oggi commentati (CSP, `X-Frame-Options`, `nosniff`, le tre policy Cross-Origin) e quali di essi hai già nella nota sull'auth; perché `basicConfig` chiamato due volte è un problema silenzioso* — *`curl -I` mostra CSP, `X-Frame-Options` e `X-Content-Type-Options`; l'app parte e si spegne senza warning di deprecazione*
- [ ] **0.6** 🟡 **Migrazione a React 19** — *concetti: cosa cambia da 18, cosa si rompe, React Compiler* — *`npm ls react` dice 19.x; `tsc --noEmit` pulito; l'app parte senza warning in console*
- [ ] **0.7** 🟢 tsconfig: aggiunti `noUncheckedIndexedAccess` e `exactOptionalPropertyTypes` — *`tsc --noEmit` pulito dopo le correzioni che i due flag fanno emergere*
- [ ] **0.8** 🟢 ESLint + Vitest + RTL sul frontend, ruff + pyright sul backend — *i quattro comandi girano e sono verdi; import di routing unificati su `react-router`, `react-router-dom` rimosso*
- [ ] **0.9** 🟢 **Rimozione di Redux dal progetto**: via `@reduxjs/toolkit`, `react-redux`, il `Provider` in `main.tsx` e la cartella `src/store/` — *da saper riassumere in due frasi: è una decisione da difendere in colloquio* — *`npm ls` non elenca più i due pacchetti né `redux` transitivo; l'app parte e naviga; `tsc --noEmit` pulito*
- [ ] **0.10** 🟢 `.vscode/extensions.json`: SonarQube, ESLint, Python; rimosso `Vue.volar` — *aprendo la cartella, VSCode propone le tre estensioni giuste*
- [ ] **0.11** 🔴 **I due Dockerfile li scrivi tu.** Claude fornisce **solo l'ossatura commentata** — le fasi, l'ordine dei layer, i punti dove va cosa — poi li scrivi da zero; il `docker-compose.yml` resta delegabile — *concetti: perché l'ordine delle istruzioni determina la cache dei layer; perché si copiano prima i file di dipendenza e solo dopo il codice; cos'è una build multi-stage e perché il frontend ne ha bisogno (si compila con Node, si serve con nginx); `CMD` contro `ENTRYPOINT`; perché non si gira come root; a cosa serve `.dockerignore`* — *`docker compose up` da clone pulito serve l'app; e la prova che hai capito la cache: **modificando una riga di codice applicativo e ricostruendo, le dipendenze non vengono reinstallate** (verificabile dall'output del build e con `docker history`)*
- [ ] **0.12** 🟢 Pipeline GitHub Actions unica per i due progetti, su push e su PR — *verde al primo push, badge nel README*
- [ ] **0.13** 🟢 SonarQube Cloud collegato: `sonar-project.properties`, step in pipeline, **Quality Gate che blocca** — *un code smell introdotto ad arte rende rosso il job; rimosso, torna verde*
- [ ] **0.14** 🟡 **Connected Mode** dell'estensione verso il progetto Cloud — *concetti: perché senza di essa editor e CI dicono cose diverse* — *la stessa violazione compare nell'editor e nel job di CI*

---

## Fase 1 — Backend: le basi — 17h

*L'impalcatura che ogni backend ha e che nessun tutorial CRUD mostra: come legge la configurazione,
come parla col database, come consegna una connessione a ogni richiesta, come risponde quando
qualcosa va storto.*

- [ ] **1.1** 🟡 Completare i settings: variabili obbligatorie, `.env.example` aggiornato — *l'app fallisce al boot con errore chiaro se manca una variabile obbligatoria*
- [ ] **1.2** 🔴 CORS capito, non copiato — *concetti: cosa apre esattamente, perché `allow_credentials: true` cambia le regole e vieta `*`* — *una richiesta con `Origin` non in lista viene rifiutata, verificabile con `curl -H "Origin: ..."`*
- [ ] **1.3** 🔴 SQLAlchemy 2.0: engine, sessione, modelli dichiarativi, `create_all` — *concetti: differenza tra modello DB e schema API, perché non si espone mai il modello* — *la tabella `users` esiste e un test crea e rilegge una riga*
- [ ] **1.4** 🔴 Dependency injection con `Depends`: una sessione per richiesta in `app/api/deps.py` — *concetti: ciclo di vita, perché non una sessione globale, cosa accade se non la chiudi* — *un test dimostra sessioni distinte per richiesta e chiusura garantita*
- [ ] **1.5** 🟡 Repository astratto più implementazione SQLAlchemy per `User` — *il servizio non importa SQLAlchemy; un test con repository finto in memoria passa*
- [ ] **1.6** 🔴 Gestione errori: exception handler e forma unica dell'errore — *concetti: perché non si espone mai uno stacktrace* — *un errore di dominio risponde con la forma concordata e nessun dettaglio interno nel body*
- [ ] **1.7** 🟡 Test con pytest: `TestClient`, fixture, override delle dipendenze, DB di test — *`pytest` verde e i test non toccano il DB di sviluppo*
- [ ] **1.8** 🟢 `core/logging.py` finalmente popolato, con request id — *ogni risposta ha `X-Request-ID` e la riga di log lo riporta*
- [ ] **1.9** 🟡 Copertura backend in Sonar: `pytest --cov` → `coverage.xml` → scanner — *concetti: Sonar non calcola la copertura, la legge da un report che generi tu* — *la percentuale appare in dashboard e la condizione sul nuovo codice è attiva nella gate*

---

## Fase 2 — Backend: autenticazione — 20h

*Qui trasformi in codice la nota più profonda del tuo vault. La parte «riscrivo con parole mie»
l'hai già fatta: questa è la parte «mani in pasta». Ogni passo ha un corrispettivo diretto in
quella nota.*

- [ ] **2.1** 🔴 Modello utente e hashing con argon2 — *concetti: perché mai in chiaro, perché non SHA256, cos'è il salt, cos'è il work factor* — *due utenti con la stessa password hanno hash diversi e la verifica costa decine di millisecondi*
- [ ] **2.2** 🔴 Registrazione con validazione e gestione del duplicato — *`POST /api/auth/register` crea l'utente; email ripetuta → 409; password debole → 422*
- [ ] **2.3** 🔴 Tabella `sessions` e creazione della sessione al login — *concetti: stateful contro stateless, TTL, scadenza scorrevole, perché in produzione si usa Redis e qui SQLite basta* — *il login crea una riga con scadenza; una sessione scaduta non autentica*
- [ ] **2.4** 🔴 Cookie di sessione con i flag corretti — *concetti: `HttpOnly`, `Secure`, `SameSite`, `Path`, `Max-Age`, uno per uno* — *`curl -i` sul login mostra `Set-Cookie` con tutti i flag previsti*
- [ ] **2.5** 🔴 Rotazione del session id al login — *concetti: session fixation, che hai già in nota* — *un test dimostra che l'id precedente al login non è più valido dopo*
- [ ] **2.6** 🔴 `get_current_user` e protezione delle rotte — *una rotta protetta dà 401 senza cookie, 200 con cookie valido, 401 con cookie scaduto*
- [ ] **2.7** 🔴 Logout con invalidazione lato server — *dopo il logout il vecchio cookie non autentica più, con test esplicito*
- [ ] **2.8** 🔴 CSRF con double-submit token sulle mutazioni — *concetti: perché i cookie espongono a CSRF e perché `SameSite` non basta in tutti i casi* — *`POST` senza header CSRF → 403, con token corretto → 200*
- [ ] **2.9** 🟡 Rate limiting su login e prova anonima — *concetti: brute force e credential stuffing, già in nota* — *al sesto tentativo in cinque minuti la risposta è 429*
- [ ] **2.10** 🟢 Account demo seedato — *da `docker compose up` pulito si entra con le credenziali mostrate nella pagina di accesso*

---

## Fase 3 — Frontend: landing, accesso, prima rotta — 19h

- [ ] **3.1** 🟢 Impianto: router, tipi generati da OpenAPI, client fetch con credenziali — *`npm run gen:api` produce `api.gen.ts`; nessun tipo scritto a mano duplica l'API*
- [ ] **3.2** 🟢 Landing page con i sei blocchi previsti, sul tema MUI esistente — *i sei blocchi sono presenti; Lighthouse ≥ 90 su performance e accessibilità*
- [ ] **3.3** 🔴 `useActionState` sul form di invio del documento — *concetti: azioni, stato di pending, errori dal server* — *durante l'invio il bottone è disabilitato e mostra pending; un errore del server appare in pagina senza perdere il testo inserito*
- [ ] **3.4** 🟡 Registrazione e login lato frontend, con i cookie — *dopo il login `GET /api/me` risponde con l'utente; dopo il logout risponde 401*
- [ ] **3.5** 🔴 **Wrapper `fetch` tipizzato e promise cache** in `src/lib/api/` — *concetti: perché `use()` pretende una promise stabile e chiamare `fetch` nel render produce un loop infinito; invalidazione per chiave; perché serve `credentials: 'include'`, senza cui il cookie non viaggia e l'auth si rompe in silenzio* — *`me` chiamato da tre componenti produce **una sola** richiesta di rete (verificabile nel pannello Network); dopo il login la voce si invalida e la UI si aggiorna senza reload; un test dimostra che togliendo `credentials` l'auth si rompe*
- [ ] **3.6** 🔴 `Suspense` più `use()` sul caricamento di un'analisi salvata — *concetti: sospensione a livello di route, error boundary* — *su `/analisi/:id` compare il fallback e poi il contenuto; un id inesistente finisce nell'error boundary, non in pagina bianca*
- [ ] **3.7** 🟢 Prova anonima, con avviso che l'analisi non viene salvata — *senza login l'analisi parte e il risultato non compare in nessuna lista salvata*
- [ ] **3.8** 🟡 **Lighthouse CI** con budget in pipeline — *concetti: metriche di laboratorio, throttling simulato, TBT come proxy dell'INP* — *un budget volutamente stretto fa fallire il job; con i valori reali passa; il report è allegato alla PR*

---

## Fase 4 — Streaming e misura delle prestazioni — 31h

*Il gap più critico, affrontato senza AI di mezzo per non imparare due cose insieme. E il blocco
sulle prestazioni, quasi tutto in zona rossa perché parti da zero.*

- [ ] **4.1** 🔴 Eventi come union discriminata Pydantic — *ogni evento ha un `type` letterale; un evento malformato è rifiutato dalla validazione in test*
- [ ] **4.2** 🔴 Endpoint SSE con `StreamingResponse` e generatore asincrono — *concetti: cos'è un generatore, perché `yield`, formato dei frame SSE, header, keep-alive* — *`curl -N` mostra i frame arrivare progressivamente, non tutti insieme alla fine*
- [ ] **4.3** 🟢 `MockProvider` deterministico che emette eventi da fixture con ritardi — *due esecuzioni producono la stessa sequenza*
- [ ] **4.4** 🔴 Client SSE scritto a mano: `fetch`, `ReadableStream`, `TextDecoderStream`, parsing dei frame — *concetti: chunk contro riga, e il buffer incompleto a cavallo di due chunk* — *un test alimenta il parser con chunk spezzati a metà frame e ottiene gli eventi corretti*
- [ ] **4.5** 🔴 Reducer della macchina a stati — *concetti: perché una union discriminata rende impossibili gli stati illegali* — *test su idle, streaming, done, error, cancelled; `tsc` verifica l'esaustività dello switch*
- [ ] **4.6** 🔴 `AbortController` e cancellazione — *interrompendo a metà: stato `cancelled`, nessun warning React, nessuna richiesta orfana; test con abort*
- [ ] **4.7** 🔴 `useTransition` sul filtro per gravità — *con 200 rilievi finti l'input resta reattivo durante il cambio filtro e lo stato di pending è visibile*
- [ ] **4.8** 🟡 Live region ARIA sui rilievi in arrivo — *uno screen reader annuncia ogni nuovo rilievo una volta sola, non a ogni chunk*
- [ ] **4.9** 🟡 Copertura frontend in Sonar (Vitest → lcov) — *appare in dashboard accanto a quella del backend*
- [ ] **4.10** 🔴 **Leggere un profilo Performance di Chrome** — *concetti: registrare una traccia, cos'è un long task, come si legge un flamegraph, dove finisce il tempo del main thread. È la competenza di base e va prima di tutto il resto* — *introdotto ad arte un render lento, sai individuarlo nella traccia e dire quale componente e quanti millisecondi; lo scrivi in `PERFORMANCE.md`*
- [ ] **4.11** 🔴 **Marche User Timing** sul percorso di streaming: `time-to-first-event` e `time-to-first-finding-rendered`, con overlay in sviluppo — *concetti: `performance.mark` e `measure`, e perché in una UI in streaming queste due metriche contano più di LCP* — *l'overlay mostra i due valori e le marche compaiono nel pannello Performance di Chrome*
- [ ] **4.12** 🔴 **Misura prima/dopo di `useTransition`** con il `<Profiler>` su 200 rilievi, documentata in `PERFORMANCE.md` — *concetti: `actualDuration` contro `baseDuration`, perché `useTransition` agisce sull'INP e non sull'LCP* — *il documento riporta i numeri delle due configurazioni e il metodo di misura, e la differenza è riproducibile da un altro lettore*
- [ ] **4.13** 🟡 `web-vitals` che raccoglie LCP, INP e CLS dal browser — *concetti: dati di campo contro dati di laboratorio, perché l'INP vero richiede un'interazione umana* — *i tre valori compaiono nell'overlay; il README dichiara che senza traffico non ci sono dati di campo significativi*

---

## Fase 5 — L'AI vera — 18h

- [ ] **5.1** 🔴 Porta `LLMProvider` come Protocol in `app/llm/port.py` — *concetti: inversione delle dipendenze, perché mock e reale sono intercambiabili* — *una variabile d'ambiente passa da mock a reale senza toccare le rotte*
- [ ] **5.2** 🔴 `AnthropicProvider` con output strutturato validato — *concetti: `output_config.format`, `messages.parse()`, cosa fare quando il modello viola lo schema* — *con una risposta finta malformata si ottiene un evento `error` gestito, non un'eccezione non catturata*
- [ ] **5.3** 🔴 Streaming dei rilievi dal modello agli eventi SSE — *i rilievi appaiono uno a uno nell'interfaccia mentre arrivano*
- [ ] **5.4** 🔴 Component registry in `src/lib/registry/`: la mappa più il **primo** componente — *concetti: whitelist dei prop, perché il modello non controlla mai `href` né HTML* — *tipo sconosciuto o prop non validi danno un fallback visibile e mai un crash; test con payload ostile*
- [ ] **5.5** 🟡 Un secondo componente del registry — *due tipi di rilievo resi correttamente, con snapshot test*
- [ ] **5.6** 🔴 Citazioni con offset e highlight nel documento originale — *cliccando un rilievo il testo corrispondente si evidenzia; un offset fuori range non rompe il rendering*
- [ ] **5.7** 🔴 `useOptimistic` sulla marcatura verificato/contestato — *l'esito appare prima della risposta del server e si riallinea in caso di errore; test del rollback*
- [ ] **5.8** 🟡 Salvataggio delle analisi per l'utente autenticato — *l'analisi compare nella lista dell'utente e non in quella di un altro, con test di isolamento*
- [ ] **5.9** 🟢 Banner di disclosure AI e disclaimer «non è un parere legale» — *presenti su ogni schermata che mostra output del modello.* **Non negoziabile:** senza, l'app non è onesta su sé stessa

---

## Fase 6 — Vetrina finale — 6h

*Non sacrificarla mai: senza vetrina il lavoro non si vede. Meglio tagliare in fase 5.*

- [ ] **6.1** 🟢 README con le decisioni architetturali, i badge di CI e Sonar, e il rimando a `PERFORMANCE.md` — *un estraneo capisce cosa fa e perché è costruito così senza aprire il codice*
- [ ] **6.2** 🟢 Video di 2-3 minuti — *mostra l'analisi in streaming, l'highlight della citazione, e i numeri di `PERFORMANCE.md`*

---

## Backlog — dopo il 15 gennaio, in ordine di valore (~26h)

*Fuori dal budget. Ordinati per valore, così puoi fermarti in qualunque punto.*

- [ ] **B.1** 🔴 GDPR su se stessi: esporta i miei dati, cancella il mio account (4h) — *l'export contiene tutto e solo ciò che riguarda l'utente; dopo la cancellazione nessuna riga residua in nessuna tabella, con test*
- [ ] **B.2** 🟢 `CONFORMITA.md` con la matrice requisito normativo → componente → come lo dimostro (2h)
- [ ] **B.3** 🔴 Azioni classificate per rischio, con conferma esplicita sulla condivisione (4h)
- [ ] **B.4** 🟡 Audit trail esportabile (3h)
- [ ] **B.5** 🟡 Gli altri due componenti del registry (3h)
- [ ] **B.6** 🟡 SonarQube self-hosted: `docker-compose.sonarqube.yml` con Community Build e PostgreSQL, più il paragrafo nel README sulla differenza misurata (3h) — *concetti: perché serve un database vero e non quello embedded*
- [ ] **B.7** 🟡 Passata di accessibilità completa con axe (3h)
- [ ] **B.8** 🟡 Interrupt e ripresa dell'analisi a metà (4h)

---

## Il budget, detto onestamente

| Fase | Ore | Cumulato |
|---|---:|---:|
| 0 — Fusione template e impianto | 25 | 25 |
| 1 — Backend: le basi | 17 | 42 |
| 2 — Backend: autenticazione | 20 | 62 |
| 3 — Frontend: landing e accesso | 19 | 81 |
| 4 — Streaming e prestazioni | 31 | 112 |
| 5 — L'AI vera | 18 | 130 |
| 6 — Vetrina | 6 | **136** |

Al 15 gennaio restano **~110 ore realistiche**: il piano completo è ~26 ore di troppo, e va saputo
in anticipo. L'ordine sopra è tale che **in qualunque punto ti fermi hai qualcosa di coerente**.

**I tagli, in ordine, se le ore mancano:** prima **5.5** (secondo componente del registry, −3h),
poi **5.6** (citazioni con highlight, −4h). Il punto di non ritorno è **5.9**, il banner di
disclosure: un'ora, e senza di esso l'app non è onesta su sé stessa.

**Se a metà dicembre sei sotto le 90 ore:** chiudi a fine fase 4 più 5.1, 5.2, 5.3 e 5.9 — cioè
streaming, prestazioni misurate e AI minima funzionante — e sposta registry e citazioni nel
backlog. Resta un progetto pienamente difendibile in colloquio.
