import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './theme';
import { Route, Routes } from 'react-router';
import AppLayout from './layouts/AppLayout/AppLayout';

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={null} />
        </Route>
      </Routes>
    </ThemeProvider>
  )
}