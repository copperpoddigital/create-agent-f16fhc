import { useEffect } from 'react'; // v18.2.0

/**
 * Enum defining available theme options for the Freight Price Movement Agent
 */
export enum ThemeType {
  LIGHT = 'light',
  DARK = 'dark',
  SYSTEM = 'system',
}

/**
 * localStorage key for storing user's theme preference
 */
export const STORAGE_KEY = 'freight-price-agent-theme';

/**
 * Detects the user's system theme preference
 * @returns The detected system theme (LIGHT or DARK)
 */
export const getSystemTheme = (): ThemeType => {
  // Check if window.matchMedia is available (for SSR compatibility)
  if (typeof window !== 'undefined' && window.matchMedia) {
    // Check if the user prefers dark color scheme
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return ThemeType.DARK;
    }
  }
  // Default to light theme
  return ThemeType.LIGHT;
};

/**
 * Applies the specified theme to the document by adding appropriate CSS classes
 * @param theme The theme to apply
 */
export const applyTheme = (theme: ThemeType): void => {
  // Remove any existing theme classes
  document.body.classList.remove('light-theme', 'dark-theme');
  
  // Apply the appropriate theme class
  let appliedTheme = theme;
  
  // If system theme is selected, determine the actual theme from system preference
  if (theme === ThemeType.SYSTEM) {
    appliedTheme = getSystemTheme();
  }
  
  // Add the theme class to the document body
  document.body.classList.add(`${appliedTheme}-theme`);
  
  // Store the selected theme preference (not the resolved system theme)
  localStorage.setItem(STORAGE_KEY, theme);
};

/**
 * Sets up a listener for system theme preference changes
 * @param callback Function to call when the system theme changes
 * @returns A cleanup function to remove the listener
 */
export const listenForSystemThemeChanges = (
  callback: (theme: ThemeType) => void
): (() => void) => {
  // Check if window.matchMedia is available (for SSR compatibility)
  if (typeof window === 'undefined' || !window.matchMedia) {
    // Return empty cleanup function if not available
    return () => {};
  }
  
  // Create a MediaQueryList for prefers-color-scheme: dark
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  // Define the change handler
  const handleChange = (event: MediaQueryListEvent) => {
    callback(event.matches ? ThemeType.DARK : ThemeType.LIGHT);
  };
  
  // Add the event listener
  // Use the appropriate method based on browser support
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', handleChange);
  } else {
    // Fallback for older browsers
    mediaQuery.addListener(handleChange);
  }
  
  // Return a cleanup function
  return () => {
    if (mediaQuery.removeEventListener) {
      mediaQuery.removeEventListener('change', handleChange);
    } else {
      // Fallback for older browsers
      mediaQuery.removeListener(handleChange);
    }
  };
};

/**
 * React hook that listens for system theme changes and applies them when using system theme
 * @param currentTheme The current theme setting
 */
export const useSystemThemeListener = (currentTheme: ThemeType): void => {
  useEffect(() => {
    // Only set up the listener if we're using system theme
    if (currentTheme === ThemeType.SYSTEM) {
      // Set up the listener and get the cleanup function
      const cleanup = listenForSystemThemeChanges(() => {
        // Re-apply the system theme when it changes
        applyTheme(ThemeType.SYSTEM);
      });
      
      // Clean up the listener when the component unmounts or theme changes
      return cleanup;
    }
  }, [currentTheme]);
};