import React from 'react'; // version specified in the documentation
import AppRoutes from './routes/AppRoutes';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { AlertProvider } from './contexts/AlertContext';
import './styles/index.css';

/**
 * Main application component that wraps the entire application with necessary context providers
 * @returns {JSX.Element} The rendered application with all context providers and routes
 */
const App: React.FC = () => {
  return (
    // LD1: Wrap the application with AlertProvider for notification management
    <AlertProvider>
      {/* LD1: Wrap with ThemeProvider for theme management */}
      <ThemeProvider>
        {/* LD1: Wrap with AuthProvider for authentication management */}
        <AuthProvider>
          {/* LD1: Render the AppRoutes component which contains all application routes */}
          <AppRoutes />
        </AuthProvider>
      </ThemeProvider>
    </AlertProvider>
  );
};

// IE3: Export the App component as the default export
export default App;