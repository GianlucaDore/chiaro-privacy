// Eseguito una volta sola prima di tutti i test, come dichiarato in
// `setupFiles` dentro vitest.config.ts.

// Aggiunge a `expect` i matcher che parlano di DOM: toBeVisible,
// toBeDisabled, toHaveTextContent. L'import con il suffisso `/vitest`
// registra anche i tipi, quindi TypeScript li conosce senza altro.
import '@testing-library/jest-dom/vitest'

import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Smonta i componenti montati dal test appena concluso. Senza questo, il
// DOM finto si accumula fra un test e l'altro e `getByRole` trova due
// elementi dove il test si aspetta uno.
//
// ⚠️ La pulizia automatica di Testing Library funziona solo quando le
// funzioni di Vitest sono globali. Qui si importano una per una - scelta
// voluta, perche' rende esplicito da dove viene ogni cosa - e quindi la
// pulizia va registrata a mano.
afterEach(() => {
  cleanup()
})
