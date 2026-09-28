# Immagine del backend: FastAPI servito da uvicorn.
# Il contesto di build e' la cartella backend/, dichiarata con `context:` nel
# docker-compose.yml: tutti i percorsi di origine qui sotto partono da li'.

# `python` e' il nome dell'immagine, cioe' cosa ti serve gia' pronto.
# `3.12-slim` e' l'etichetta: versione di Python + sistema di base (Debian
# ridotto). Non e' un import: e' il disco da cui parte l'immagine.
FROM python:3.12-slim

# Due variabili di prassi in ogni immagine Python: niente file .pyc, e log che
# compaiono subito in `docker compose logs` invece di restare in un buffer.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crea la cartella /app DENTRO L'IMMAGINE (non sul tuo disco) e la rende la
# cartella corrente: da qui in poi `./` significa `/app`. Il nome e' solo una
# convenzione, conta che sia una cartella dedicata.
WORKDIR /app

# Nell'immagine c'e' pip ma non pipenv. `--no-cache-dir` perche' la cache di
# pip serve a reinstallare piu' in fretta, e questa riga gira una volta sola:
# sarebbe peso inutile chiuso nell'immagine per sempre.
RUN pip install --no-cache-dir pipenv

# Origine: relativa al contesto, quindi `Pipfile` e non `backend/Pipfile`.
# Destinazione: `./`, cioe' /app. Si copiano PRIMA del codice, cosi' cambiare
# il codice non rilancia l'installazione qui sotto: resta in cache.
COPY Pipfile Pipfile.lock ./

# `--system`: installa nel Python dell'immagine, senza creare un virtualenv in
# cui uvicorn non verrebbe trovato. `--deploy`: fallisce se il lock non
# combacia col Pipfile. Senza `--dev`, pytest e ruff restano fuori.
RUN pipenv install --system --deploy

# Copia il CONTENUTO di backend/app/ in /app/app/. tests/ e conftest.py stanno
# accanto ad app/, non dentro, quindi restano fuori da soli. Il Pipfile e' gia'
# entrato sopra, e deve restare: l'app lo cerca per trovare la propria radice.
COPY app/ ./app/

# Crea un utente non root e gli da' la proprieta' di /app. uploads/ va creata
# QUI: il compose ci monta sopra un volume prima che l'app parta, e se la
# cartella non esiste nell'immagine il volume nasce di root e l'app non ci
# puo' scrivere.
RUN useradd --create-home appuser \
 && mkdir -p /app/uploads \
 && chown -R appuser /app

# Da qui in poi, e mentre il container gira, si e' appuser e non root.
USER appuser

# Solo documentazione: non apre nessuna porta. La porta verso l'esterno la
# pubblica `ports:` nel compose.
EXPOSE 8000

# Dove uvicorn ascolta lo decide QUESTA riga: il compose inoltra soltanto.
# `0.0.0.0` perche' 127.0.0.1 dentro un container e' irraggiungibile da fuori.
# Forma a lista, cosi' uvicorn riceve il segnale di spegnimento.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
