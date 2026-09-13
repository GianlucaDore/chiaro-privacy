/*
 * PASSO 0.6 - Migrazione a React 19.  Zona: GIALLA (il codice lo scrivi tu).
 *
 * Criterio di completamento:
 *   npm ls react        -> una sola riga, 19.x, il resto marcato "deduped"
 *   npm run typecheck   -> nessun errore
 *   npm run dev         -> l'app parte e la console del browser resta pulita
 *
 * IL BRIEFING E' LUNGO ED E' PENSATO PER CHI CONOSCE SOLO REACT 18:
 *   docs/passi/0.6.md
 * Ogni cartello qui sotto rimanda alla sezione che spiega quella cosa.
 *
 * Cancella ogni TODO(0.6/n) quando hai fatto quella cosa: a fine passo non
 * ne deve restare nessuno.
 */

// TODO(0.6/1) package.json non ammette commenti, quindi il cartello sta qui.
//             Vanno portati a ^19.0.0 QUATTRO pacchetti, non due:
//               - react e react-dom      -> dependencies
//               - @types/react
//                 e @types/react-dom     -> devDependencies
//             ⚠️ Muoverne solo una coppia e' l'errore piu' comune di questa
//             migrazione, e il sintomo inganna: l'app gira nel browser e
//             invece protesta tsc, perche' @types/react non e' React ma solo
//             la descrizione dei suoi tipi, pubblicata da un altro progetto.
//             Perche' e da chi: sezione 7 del briefing.

// TODO(0.6/2) Dopo npm install, verifica con `npm ls react` che React compaia
//             UNA volta sola. Se ne comparissero due, l'app morirebbe con
//             "Invalid hook call": un messaggio che parla di hook mentre il
//             problema sta nelle dipendenze.
//             Il perche' e' spiegato nella sezione 8, e vale la pena leggerlo
//             prima: spiega cosa sia davvero un hook sotto il cofano.

// TODO(0.6/3) Il typecheck e' il momento in cui React 19 ti presenta il conto.
//             Le due cose che possono saltare fuori su questo codice sono:
//               - JSX.Element, che ora si scrive React.JSX.Element (sez. 7)
//               - un ref callback con la freccia senza graffe (sez. 4.4)
//             Il secondo e' la trappola vera della 19: il codice sembra
//             identico a prima e si comporta in modo diverso, perche' il
//             valore ritornato da un ref callback adesso viene interpretato
//             come funzione di pulizia.

// TODO(0.6/4) Ultimo controllo del criterio: `npm run dev`, apri il browser e
//             guarda la CONSOLE, non solo la pagina. Il criterio chiede che
//             sia pulita, e i warning di React compaiono li' e non nel
//             terminale di Vite.

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
// ❗ TODO(0.6/5) NON in questo passo. La rimozione di Redux e del suo
//               <Provider> e' il passo 0.9, e l'unificazione degli import
//               di routing su react-router (togliendo react-router-dom)
//               e' lo 0.8. Qui si tocca SOLO la versione di React.
//               Cancella questo cartello quando hai letto la sezione 9,
//               che elenca le tre cose da non fare adesso.
import { Provider } from 'react-redux';
import { store } from './store/store';
import App from './App';

// TODO(0.6/6) StrictMode resta dov'e'. In React 19 alcuni controlli sono
//             piu' rumorosi, quindi e' proprio qui dentro che i warning
//             vietati dal criterio verrebbero fuori: non toglierlo per
//             farli tacere. Lo scopo di StrictMode e' esattamente quello
//             di far emergere in sviluppo i problemi che in produzione si
//             manifesterebbero a caso.
createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </Provider>
  </React.StrictMode>
);