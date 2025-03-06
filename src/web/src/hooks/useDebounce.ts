import { useState, useEffect, useRef } from 'react'; // version ^18.2.0

/**
 * A custom React hook that provides debouncing functionality to delay the execution
 * of a function or update of a value until after a specified delay period has elapsed
 * since the last invocation.
 * 
 * This is particularly useful for performance optimization in scenarios like
 * search inputs, form validation, and API requests.
 *
 * @param value - The value to debounce
 * @param delay - The delay in milliseconds
 * @returns The debounced value that updates only after the specified delay
 */
function useDebounce(value: any, delay: number): any {
  // Initialize state with the initial value provided
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  // Ref to store the timeout ID
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  
  useEffect(() => {
    // Clear any existing timeout to reset the delay timer
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    // Create a timeout that will update the debounced value after the specified delay
    timeoutRef.current = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    // Return a cleanup function that clears the timeout if the component unmounts
    // or the value/delay changes before the timeout completes
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, delay]); // Re-run the effect when value or delay changes
  
  // Return the debounced value from the hook
  return debouncedValue;
}

export default useDebounce;