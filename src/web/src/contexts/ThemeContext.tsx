import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react'; // ^18.2.0
import { ThemeType, STORAGE_KEY, applyTheme, getSystemTheme, useSystemThemeListener } from '../config/theme';

/**
 * Interface defining the shape of the ThemeContext value
 */
interface ThemeContextType {
  theme: ThemeType;
  setTheme: (theme: ThemeType) => void;
  toggleTheme: () => void;
  useSystemTheme: () => void;
  isTheme: (themeToCheck: ThemeType) => boolean;
}

// Initial state for the theme context
const initialThemeState = { theme: ThemeType.SYSTEM };

/**
 * Context for theme state and functions
 */
export const ThemeContext = createContext<ThemeContextType | null>(null);

/**
 * Provider component that makes theme context available to child components
 * @param children - React components that will have access to the theme context
 */
export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Initialize theme state, retrieve from localStorage if available
  const [theme, setThemeState] = useState<ThemeType>(() => {
    // Check if we're in a browser environment
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem(STORAGE_KEY);
      if (savedTheme && Object.values(ThemeType).includes(savedTheme as ThemeType)) {
        return savedTheme as ThemeType;
      }
    }
    return ThemeType.SYSTEM; // Default to system theme
  });

  // Apply the theme on initial render
  useEffect(() => {
    applyTheme(theme);
  }, []);

  /**
   * Set theme and apply it to the document
   * @param newTheme - The theme to apply
   */
  const setTheme = (newTheme: ThemeType) => {
    setThemeState(newTheme);
    applyTheme(newTheme);
  };

  /**
   * Toggle between light, dark, and system themes
   */
  const toggleTheme = () => {
    switch (theme) {
      case ThemeType.LIGHT:
        setTheme(ThemeType.DARK);
        break;
      case ThemeType.DARK:
        setTheme(ThemeType.SYSTEM);
        break;
      case ThemeType.SYSTEM:
      default:
        setTheme(ThemeType.LIGHT);
        break;
    }
  };

  /**
   * Set theme to system preference
   */
  const useSystemTheme = () => {
    setTheme(ThemeType.SYSTEM);
  };

  /**
   * Check if current theme matches the specified theme
   * @param themeToCheck - Theme to compare with current theme
   * @returns True if current theme matches checked theme
   */
  const isTheme = (themeToCheck: ThemeType): boolean => {
    return theme === themeToCheck;
  };

  // Listen for system theme changes when using system theme
  useSystemThemeListener(theme);

  // Create context value
  const contextValue: ThemeContextType = {
    theme,
    setTheme,
    toggleTheme,
    useSystemTheme,
    isTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

/**
 * Custom hook to access the theme context
 * @returns The theme context value
 * @throws Error if used outside a ThemeProvider
 */
export const useThemeContext = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  
  if (context === null) {
    throw new Error('useThemeContext must be used within a ThemeProvider');
  }
  
  return context;
};