import { useState, useEffect, useCallback } from 'react'; // ^18.2.0
import { 
  isStorageAvailable, 
  setLocalStorageItem, 
  getLocalStorageItem, 
  removeLocalStorageItem 
} from '../utils/storage-utils';

/**
 * A custom React hook that provides a stateful interface for interacting with the browser's localStorage API.
 * This hook enables components to persist state across page refreshes and browser sessions,
 * with automatic JSON serialization and deserialization.
 *
 * @param key - The localStorage key to use for storing the value
 * @param initialValue - The initial value to use if no value is found in localStorage
 * @param expirationInMinutes - Optional expiration time in minutes
 * @returns A tuple containing the stored value, a setter function, and a remove function
 */
const useLocalStorage = <T>(
  key: string,
  initialValue: T,
  expirationInMinutes?: number
): [T, (value: T) => void, () => void] => {
  // Check if localStorage is available
  const storageAvailable = isStorageAvailable('localStorage');

  // Initialize state with the value from localStorage or the provided initialValue
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (!storageAvailable) {
      return initialValue;
    }

    // Attempt to get the item from localStorage
    const item = getLocalStorageItem<T>(key, initialValue);
    return item !== null ? item : initialValue;
  });

  // Create a function to update both state and localStorage
  const setValue = useCallback((value: T) => {
    // Update state
    setStoredValue(value);

    // Update localStorage if available
    if (storageAvailable) {
      setLocalStorageItem(key, value, expirationInMinutes);
    }
  }, [key, storageAvailable, expirationInMinutes]);

  // Create a function to remove the item from both state and localStorage
  const removeValue = useCallback(() => {
    // Reset state to initialValue
    setStoredValue(initialValue);

    // Remove from localStorage if available
    if (storageAvailable) {
      removeLocalStorageItem(key);
    }
  }, [key, initialValue, storageAvailable]);

  // Set up an effect to handle localStorage changes from other tabs/windows
  useEffect(() => {
    if (!storageAvailable) {
      return;
    }

    // Handler for the storage event, which is fired when localStorage changes in another tab
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.storageArea === localStorage) {
        // Get the new value and update state
        const newValue = getLocalStorageItem<T>(key, initialValue);
        if (newValue !== storedValue) {
          setStoredValue(newValue !== null ? newValue : initialValue);
        }
      }
    };

    // Add event listener for storage events
    window.addEventListener('storage', handleStorageChange);

    // Clean up the event listener when the component unmounts
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [key, initialValue, storageAvailable, storedValue]);

  // Return the tuple
  return [storedValue, setValue, removeValue];
};

export default useLocalStorage;