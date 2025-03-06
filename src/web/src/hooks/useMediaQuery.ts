import { useState, useEffect, useCallback } from 'react';

/**
 * A custom React hook that provides a way to check if a media query matches the current viewport size.
 * This hook enables responsive design by allowing components to adapt their behavior and appearance
 * based on screen size or other media features.
 *
 * @param {string} query - The media query to check (e.g., "(min-width: 768px)")
 * @returns {boolean} - True if the media query matches, false otherwise
 */
const useMediaQuery = (query: string): boolean => {
  // Initialize state with false for SSR compatibility
  // This ensures the hook won't throw errors during server-side rendering
  const [matches, setMatches] = useState<boolean>(false);

  // Create a memoized callback to handle media query changes
  const handleChange = useCallback((event: MediaQueryListEvent) => {
    setMatches(event.matches);
  }, []);

  useEffect(() => {
    // Check if window is defined (for SSR compatibility)
    if (typeof window === 'undefined') return;

    // Create a MediaQueryList object
    const mediaQueryList = window.matchMedia(query);
    
    // Set the initial state based on the media query match
    setMatches(mediaQueryList.matches);

    // Add an event listener to update the state when the media query match changes
    mediaQueryList.addEventListener('change', handleChange);

    // Return a cleanup function that removes the event listener
    return () => {
      mediaQueryList.removeEventListener('change', handleChange);
    };
  }, [query, handleChange]); // Re-run the effect when the query changes

  return matches;
};

export default useMediaQuery;