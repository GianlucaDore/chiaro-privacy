import { defineConfig, mergeConfig } from 'vitest/config'
import configurazioneVite from './vite.config'

// I test girano attraverso Vite, quindi hanno bisogno degli stessi plugin
// dell'applicazione - React e il React Compiler. Un vitest.config.ts scritto
// da zero SOSTITUIREBBE vite.config.ts invece di aggiungersi, e i test
// vedrebbero del JSX che nessuno trasforma: `mergeConfig` fonde le due
// configurazioni invece di scegliere fra loro.
export default mergeConfig(
  configurazioneVite,
  defineConfig({
    test: {
      // Senza un DOM finto non esistono document, window e getByRole:
      // jsdom e' un'implementazione del DOM in Node.
      environment: 'jsdom',

      // Eseguito una volta sola, prima di qualunque test.
      setupFiles: ['./tests/setup.ts'],

      // Permette ai componenti di importare CSS senza che Vitest si fermi.
      css: true,

      // Cosa Vitest considera un file di test. I test end-to-end, quando
      // arriveranno, avranno un altro esecutore e non vanno raccolti qui.
      include: [
        'tests/unit/**/*.test.{ts,tsx}',
        'tests/integration/**/*.test.{ts,tsx}',
      ],
      exclude: ['tests/e2e/**', 'node_modules', 'dist'],

      // ⚠️ Temporaneo: oggi non esiste ancora nessun test, e senza questa
      // riga `vitest run` esce in errore per assenza di file da eseguire.
      // Va tolta quando arriva il primo test, al passo 3.2b: da quel
      // momento una suite vuota e' un guasto e deve fare rumore.
      passWithNoTests: true,

      coverage: {
        provider: 'v8',
        // `text` per leggerla in terminale, `lcov` perche' e' il formato che
        // lo scanner di Sonar importera' al passo 0.13.
        reporter: ['text', 'lcov'],
        reportsDirectory: 'coverage',
        // Si misura la copertura del codice dell'applicazione, non quella
        // dei test stessi ne' dei file di configurazione.
        include: ['src/**/*.{ts,tsx}'],
      },
    },
  }),
)
