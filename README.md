# chiaro-privacy

[![CI](https://github.com/GianlucaDore/chiaro-privacy/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/GianlucaDore/chiaro-privacy/actions/workflows/ci.yml)

Applicazione full-stack che legge una privacy policy o dei termini di servizio e spiega in
chiaro cosa si sta accettando: dati raccolti, finalità, base giuridica, conservazione,
trasferimenti extra-UE, diritti esercitabili, clausole insolite. Ogni rilievo cita il testo
esatto e lo evidenzia nel documento originale.

**Vite + React 19 + TypeScript + MUI** sul frontend, **FastAPI + Pydantic v2 + SQLAlchemy**
sul backend, **SQLite**, **SSE** per lo streaming, **Claude** per l'analisi.

Il piano di lavoro è in [`SCALETTA.md`](SCALETTA.md), le regole di collaborazione in
[`CLAUDE.md`](CLAUDE.md).

---

## Avviare il progetto

L'unica cosa che serve è Docker. Due strade, con lo stesso risultato:

```bash
# le immagini già costruite dalla pipeline: nessuna compilazione
docker compose pull && docker compose up

# oppure costruite qui, dal sorgente
docker compose up --build
```

| | Indirizzo |
| --- | --- |
| Applicazione | http://localhost:8081 |
| API, documentazione interattiva | http://localhost:8000/docs |

**Non esiste un ambiente pubblico in esecuzione.** Le immagini sono pubblicate su GitHub
Container Registry, ma girano soltanto sulla macchina di chi le scarica. `:test` è l'ultima
versione verificata di `develop`; `:latest` arriverà con il primo rilascio su `main`, e sarà
la stessa immagine promossa, non ricostruita.

`docker compose down` ferma tutto; con `-v` cancella anche i documenti caricati, che vivono in un
volume e sopravvivono alle ricostruzioni.

I comandi qui sotto servono solo a chi sviluppa, e richiedono Node e Python installati.

---

## Comandi

Ogni riga va lanciata **dentro la cartella del progetto** che si sta toccando, non dalla
radice della repository. L'ordine non è casuale: è dal controllo più fondamentale a quello
più costoso, così il primo che fallisce è anche quello che spiega meglio il problema.

### Frontend — da `frontend/`

| | Comando | Quando | Cosa risponde |
| :---: | --- | --- | --- |
| 0 | `npm install` | solo se `package.json` è cambiato, o dopo un `git pull` | le dipendenze dichiarate sono quelle installate |
| 1 | `npm run typecheck` | sempre | i tipi sono coerenti |
| 2 | `npm run lint` | sempre | il codice è sensato, non solo valido |
| 3 | `npm test` | sempre | la suite Vitest è verde |
| 4 | `npm run build` | prima di una pull request | il bundler regge, e la compilazione di produzione passa |
| — | `npm run test:watch` | mentre si scrive un test | riesegue solo ciò che dipende dal file salvato |
| — | `npm run test:coverage` | prima di una pull request | produce `coverage/lcov.info`, che al passo 0.13 leggerà Sonar |
| — | `npm run dev` | per guardare con gli occhi | l'app gira su `localhost:5173` |

**Perché `typecheck` prima di `lint`.** Il linter è configurato in modalità *type-aware*,
cioè interroga il compilatore per rispondere a certe regole. Se i tipi sono rotti, i suoi
messaggi diventano confusi: `typecheck` dà lo stesso errore in forma leggibile.

**`npm run dev` non sostituisce il resto.** Vite in sviluppo **non** fa il controllo dei tipi:
trasforma i file e li serve, e un errore di tipo non gli impedisce di partire. Un'app che gira
in locale non è un'app che compila.

### Backend — da `backend/`

| | Comando | Quando | Cosa risponde |
| :---: | --- | --- | --- |
| 0 | `pipenv install --dev` | solo se il `Pipfile` è cambiato | le dipendenze, **comprese quelle di sviluppo**, sono installate |
| 1 | `pipenv run ruff` | sempre | nessuna imprecisione logica |
| — | `pipenv run format` | prima di committare | impagina il codice in forma canonica |
| 2 | `pipenv run pyright` | sempre | le annotazioni di tipo sono coerenti |
| 3 | `pipenv run test` | sempre | la suite `pytest` è verde |
| — | `pipenv run dev` | per guardare con gli occhi | uvicorn su `127.0.0.1:8000`, con `/docs` |

**`--dev` non è opzionale.** Un `pipenv install` senza di esso installa solo le dipendenze di
esecuzione, e `pytest`, `ruff` e `pyright` risultano «comando non trovato» — l'errore non dice
che manca il flag.

**Se pipenv annuncia di aver trovato un virtualenv già attivo**, sta usando quello di un altro
progetto invece del proprio. Si neutralizza con `PIPENV_IGNORE_VIRTUALENVS=1` davanti al
comando.

### Prima di aprire una pull request

```bash
cd frontend && npm run typecheck && npm run lint && npm test && npm run build
cd ../backend && pipenv run ruff && pipenv run pyright && pipenv run test
```

Gli `&&` sono voluti: la catena si ferma al primo che fallisce, e non si legge un elenco di
errori a cascata prodotti dalla stessa causa.

---

## Stato

L'infrastruttura di test del frontend c'è, ma **non esiste ancora nessun test**: `npm test`
esce con successo dichiarando di non aver trovato file da eseguire. Il primo test di
componente è il passo **3.2b**, quando ci sarà una pagina vera da interrogare, e da lì una
suite vuota tornerà a essere un errore. Le regole di `ruff` e le impostazioni di `pyright` sono dichiarate in
`backend/pyproject.toml`: prima erano quelle predefinite dello strumento, quindi dipendevano
dalla versione installata. Gli stessi controlli girano in pipeline a ogni push e a ogni pull request, e il badge in
cima mostra l'esito sull'ultimo commit di `develop`. Sulle pull request e sui due branch
stabili si aggiunge l'analisi di **SonarQube Cloud**: se la Quality Gate non passa, il job
diventa rosso. La copertura è esclusa dalla gate fino ai passi 1.9 e 4.9, quando verrà
generata dai test e importata.

Su `develop` e su `main` tre controlli sono **obbligatori**: Frontend, Backend e il verdetto
della Quality Gate pubblicato da SonarQube Cloud. Con uno dei tre rosso, la pull request non
si può mergiare.
