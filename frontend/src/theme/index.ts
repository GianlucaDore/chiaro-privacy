import { createTheme } from '@mui/material/styles';

// Design Tokens
const tokens = {
  brand: '#0052CC',        // colore principale (primary)
  brandLight: '#4C8DFF',   // variante chiara
  brandDark: '#003A99',    // variante scura
  accent: '#FF6F61',       // colore secondario (secondary)
  appBg: '#F7F8FA',        // sfondo principale
  paperBg: '#FFFFFF',      // sfondo dei contenitori
  textPrimary: '#0F172A',  // testo principale
  textSecondary: '#334155' // testo secondario
}

// MUI Theme
export const theme = createTheme({
  palette: {
    mode: 'light', // tema fisso (mettere 'dark' se serve)
    primary: {
      main: tokens.brand,
      light: tokens.brandLight,
      dark: tokens.brandDark,
      contrastText: '#FFFFFF'
    },
    secondary: {
      main: tokens.accent,
      contrastText: '#000000'
    },
    background: {
      default: tokens.appBg,
      paper: tokens.paperBg
    },
    text: {
      primary: tokens.textPrimary,
      secondary: tokens.textSecondary
    }
  },
  typography: {
    fontFamily: ['Inter', 'system-ui', 'Segoe UI', 'Roboto', 'Arial', 'sans-serif'].join(','),
    button: { textTransform: 'none' }
  },
  shape: { borderRadius: 8 },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { backgroundColor: tokens.appBg }
      }
    },
    MuiButton: {
      defaultProps: { variant: 'contained', size: 'medium' },
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 600
        }
      }
    },
    MuiAppBar: {
      defaultProps: { color: 'primary' }
    },
    MuiTextField: {
      defaultProps: { variant: 'outlined', size: 'small' }
    }
  }
})