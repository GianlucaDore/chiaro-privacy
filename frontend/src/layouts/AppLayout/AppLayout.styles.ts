import { type SxProps, type Theme } from '@mui/material/styles'

export const layoutSx: Record<string, SxProps<Theme>> = {
  appBar: {
    borderBottom: '1px solid',
    borderBottomColor: 'divider'
  },
  toolbar: {
    gap: 1
  },
  main: {
    minHeight: '100dvh',
    bgcolor: 'background.default',
    color: 'text.primary',
    paddingTop: 3,
    paddingBottom: 3
  },
  navButton: {
    color: 'inherit'
  },
  title: {
    flexGrow: 1,
    color: 'inherit',
    ':hover': {
        cursor: "pointer"
    }
  }
}