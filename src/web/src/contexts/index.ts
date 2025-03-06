/**
 * Barrel file exporting all context providers and hooks for the Freight Price Movement Agent.
 * Centralizes imports for authentication, theme management, and notification functionality.
 * 
 * @version 1.0.0
 */

// Authentication context exports
import { AuthContext, AuthProvider, initialAuthState } from './AuthContext';

// Theme context exports
import { ThemeContext, ThemeProvider, useThemeContext } from './ThemeContext';

// Alert context exports
import { AlertContext, AlertProvider, useAlertContext, AlertType } from './AlertContext';

// Re-export authentication context
export { AuthContext, AuthProvider, initialAuthState };

// Re-export theme context
export { ThemeContext, ThemeProvider, useThemeContext };

// Re-export alert context
export { AlertContext, AlertProvider, useAlertContext, AlertType };