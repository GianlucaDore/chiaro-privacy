import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['dist', 'coverage', 'node_modules'] },
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      // Type-checked: le regole che hanno bisogno dei tipi, non solo della
      // sintassi. Costano un passaggio di tsc in piu' ma trovano cose che
      // senza i tipi sono invisibili, tipo una promise mai attesa.
      ...tseslint.configs.recommendedTypeChecked,
      // Include le regole del React Compiler, attivato al passo 0.6: sono
      // loro a dire dove il compilatore dovra' arrendersi.
      reactHooks.configs.flat['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: {
        // Chiede a TypeScript quale progetto copre ogni file, invece di
        // elencare i tsconfig a mano: qui ce ne sono due.
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // Questo lavoro lo fa gia' il compilatore, con noUnusedLocals e
      // noUnusedParameters nel tsconfig. Tenere entrambi significa lo stesso
      // problema riportato due volte con due messaggi diversi.
      '@typescript-eslint/no-unused-vars': 'off',
    },
  },
);
