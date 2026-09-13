// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// TODO(0.6/7) DECISIONE DA PRENDERE: il React Compiler si attiva qui o in un
//             passo a parte?
//             Cos'e': un programma che gira al BUILD, legge i componenti e
//             inserisce da solo la memoizzazione che oggi si scrive a mano
//             con useMemo e useCallback. Non fa parte di React 19: e' il
//             pacchetto babel-plugin-react-compiler, che si aggancia qui
//             dentro passando una configurazione babel a react().
//             ⚠️ Il criterio del passo NON lo richiede, e la scaletta non ha
//             un passo che lo installa: e' una lacuna del piano. Ma il
//             CLAUDE.md lo da' gia' per attivo quando vieta useMemo e
//             useCallback scritti a mano: finche' il compilatore non c'e',
//             quel divieto chiede una cosa senza fornire il sostituto.
//             Le due strade e i loro costi: sezione 6 del briefing.
//             Cancella questo cartello con la scelta fatta, qualunque sia.

export default defineConfig({
  plugins: [react()]
})