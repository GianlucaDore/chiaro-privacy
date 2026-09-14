// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    // Il React Compiler inserisce lui la memoizzazione al momento del build:
    // e' la ragione per cui il CLAUDE.md vieta useMemo e useCallback a mano.
    // Su React 19 il runtime sta dentro react stesso, quindi non serve
    // installare react-compiler-runtime.
    react({ babel: { plugins: ['babel-plugin-react-compiler'] } }),
  ],
})