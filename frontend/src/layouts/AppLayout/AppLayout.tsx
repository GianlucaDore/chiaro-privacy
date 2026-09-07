import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material'
import { Outlet, useNavigate } from 'react-router-dom'
import { layoutSx as sx } from './AppLayout.styles';

export default function AppLayout() {

  const navigate = useNavigate();

  const handleTitleClick = (): void => {
    navigate("/");
  }

  return (
    <>
      <AppBar position="sticky" color="primary" sx={sx.appBar}>
        <Toolbar sx={sx.toolbar}>
          <Typography variant="h6" sx={sx.title} onClick={handleTitleClick}>React Template</Typography>
        </Toolbar>
      </AppBar>

      <Box component="main" sx={sx.main}>
        <Container maxWidth="lg">
          <Outlet />
        </Container>
      </Box>
    </>
  )
}