import { useThemeContext } from '../contexts/ThemeContext';
import { ThemeType } from '../config/theme';

/**
 * A custom React hook that provides theme management functionality
 * for the Freight Price Movement Agent web application.
 * 
 * This hook simplifies access to theme context and provides an interface
 * for theme operations like switching between light, dark, and system themes.
 * 
 * @returns An object containing theme state and theme management functions
 */
const useTheme = () => {
  // Get theme context using useThemeContext hook
  const themeContext = useThemeContext();
  
  // Return an object with theme state and theme management functions
  return {
    /**
     * Current theme (light, dark, or system)
     */
    theme: themeContext.theme,
    
    /**
     * Function to set a specific theme
     * @param theme - The theme to apply (light, dark, or system)
     */
    setTheme: themeContext.setTheme,
    
    /**
     * Function to toggle between light, dark, and system themes in sequence
     * Light → Dark → System → Light
     */
    toggleTheme: themeContext.toggleTheme,
    
    /**
     * Function to set the theme to follow system preference
     */
    useSystemTheme: themeContext.useSystemTheme,
    
    /**
     * Function to check if the current theme matches a specific theme
     * @param themeToCheck - The theme to compare against the current theme
     * @returns True if the current theme matches the specified theme
     */
    isTheme: themeContext.isTheme,
  };
};

export default useTheme;