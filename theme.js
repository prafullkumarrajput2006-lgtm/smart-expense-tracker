import { createTheme } from '@mui/material/styles';

// Teal-based color palette as per requirements
const theme = createTheme({
  palette: {
    primary: {
      main: '#00A8A8', // Teal
      light: '#33b9b9',
      dark: '#007676',
      contrastText: '#fff',
    },
    secondary: {
      main: '#007BFF', // Blue
      light: '#3395ff',
      dark: '#0056b3',
      contrastText: '#fff',
    },
    background: {
      default: '#F6F8FA', // Light gray background
      paper: '#ffffff',
    },
    text: {
      primary: '#212529',
      secondary: '#6c757d',
    },
  },
  typography: {
    fontFamily: '"Poppins", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 700,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
      },
    },
  },
});

export default theme;
