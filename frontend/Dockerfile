# Immagine del frontend: build statica di Vite servita da nginx.
# Il contesto di build e' la cartella frontend/, dichiarata con `context:` nel
# docker-compose.yml: tutti i percorsi di origine qui sotto partono da li'.
#
# Due stadi. Ogni FROM ne apre uno nuovo, e l'immagine finale e' SOLO
# l'ultimo: Node serve a costruire e poi viene buttato, resta nginx.

# ---- STADIO 1: costruzione --------------------------------------------------

# `node` e' il nome dell'immagine; `22.22.2-alpine` l'etichetta. `alpine` e' il
# sistema di base, quindi sta nell'etichetta e non nel nome. `AS costruzione`
# da' un nome allo stadio: serve al COPY --from in fondo per ritrovarlo.
FROM node:22.22.2-alpine AS costruzione

# Crea /app dentro questo stadio e la rende la cartella corrente.
WORKDIR /app

# Solo i due file delle dipendenze, prima del resto: finche' non cambiano,
# `npm ci` qui sotto resta in cache e non si rilancia.
COPY package.json package-lock.json ./

# Installa esattamente cio' che dice il lock (`npm install` potrebbe
# riscriverlo). Servono anche le devDependencies: TypeScript e Vite stanno li'.
RUN npm ci

# Qui si copia tutto, perche' `tsc -b` legge i tsconfig, che chiedono anche
# tests/ e vitest.config.ts. node_modules e dist li tiene fuori .dockerignore.
COPY . .

# `tsc -b && vite build`: prima controlla i tipi, poi scrive il sito in /app/dist.
RUN npm run build

# ---- STADIO 2: servizio -----------------------------------------------------

# Da qui Node non esiste piu': l'immagine finale e' questa. nginx e' un server
# web che restituisce file statici.
FROM nginx:alpine

# Sostituisce il sito di default di nginx con la nostra configurazione.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Prende dist/ dallo stadio 1. L'origine e' un percorso ASSOLUTO in quello
# stadio: il suo WORKDIR qui non vale, quindi `/app/dist` e non `dist`.
# La destinazione e' la cartella da cui nginx serve i file.
COPY --from=costruzione /app/dist /usr/share/nginx/html

# Solo documentazione. Fuori la porta e' 8081: la decide `ports:` nel compose.
EXPOSE 80

# Nessun CMD: l'immagine di nginx ne ha gia' uno. Il suo `daemon off` tiene
# nginx in primo piano, altrimenti il container si spegnerebbe appena partito.
