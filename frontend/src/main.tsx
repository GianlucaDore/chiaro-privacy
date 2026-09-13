/*
 * PASSO 0.6 - Migrazione a React 19.  Zona: GIALLA (il codice lo scrivi tu).
 *
 * Criterio di completamento:
 *   npm ls react        -> una sola riga, 19.x
 *   npm run typecheck   -> nessun errore
 *   npm run dev         -> l'app parte e la console del browser resta pulita
 *
 * Briefing completo: docs/passi/0.6.md
 * Cancella ogni cartello TODO(0.6/n) man mano che fai quella cosa: a fine
 * passo non ne deve restare nessuno.
 */

// TODO(0.6/1) package.json non ammette commenti, quindi il cartello sta qui.
//             Vanno portati a React 19 quattro pacchetti, non due: react e
//             react-dom fra le dependencies, @types/react e @types/react-dom
//             fra le devDependencies.
//             ⚠️ Muoverne solo una coppia e' l'errore classico: il codice e i
//             suoi tipi sono pubblicati da soggetti diversi e non si
//             allineano da soli. Vedi la sezione 3 del briefing.

// TODO(0.6/2) Dopo l'installazione, verifica che React compaia una volta sola
//             nell'albero delle dipendenze. Se ne comparissero due, l'app si
//             romperebbe con un messaggio che parla di hook: la sezione 4 del
//             briefing spiega perche'.

// TODO(0.6/3) Decisione da prendere: il React Compiler si attiva in questo
//             passo o in uno successivo? Il criterio non lo richiede, ma il
//             CLAUDE.md lo da' gia' per attivo quando vieta useMemo e
//             useCallback scritti a mano. Sezione 5 del briefing.

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
// ❗ TODO(0.6/4) NON in questo passo: la rimozione di Redux e' il passo 0.9, e
//               l'unificazione degli import di routing su react-router e' lo
//               0.8. Qui si tocca solo la versione di React.
import { Provider } from 'react-redux';
import { store } from './store/store';
import App from './App';

// TODO(0.6/5) StrictMode resta. In React 19 rende piu' rumorosi alcuni
//             controlli, quindi e' proprio qui che i warning vietati dal
//             criterio verrebbero fuori: non toglierlo per farli tacere.
createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </Provider>
  </React.StrictMode>
);