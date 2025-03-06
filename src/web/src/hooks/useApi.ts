/**
 * A custom React hook that provides a standardized interface for making API requests
 * in the Freight Price Movement Agent web application. This hook manages loading states,
 * error handling, and provides a consistent way to interact with the backend API.
 */

import axios, { CancelTokenSource } from 'axios'; // ^1.3.4
import { useState, useCallback, useRef } from 'react'; // ^18.2.0

import { apiClient, handleApiError } from '../api/api-client';
import {
  ApiResponse,
  ApiHookState,
  ApiHookActions,
  ApiHookResult,
  HttpMethod,
  ApiError
} from '../types/api.types';

/**
 * A hook that provides a standardized interface for making API requests
 * with loading state and error handling
 *
 * @param apiFunction - The API function to execute
 * @param options - Configuration options for the hook
 * @returns Object containing state (data, error, loading flags) and actions (execute, reset, cancel)
 */
const useApi = (
  apiFunction: (...args: any[]) => Promise<ApiResponse>,
  options: {
    immediate?: boolean;
    initialData?: any;
    onSuccess?: (data: any) => void;
    onError?: (error: ApiError) => void;
  } = {}
): ApiHookResult => {
  // Initialize state with default values
  const [state, setState] = useState<ApiHookState>({
    data: options.initialData || null,
    error: null,
    isLoading: options.immediate === true,
    isSuccess: false,
    isError: false
  });

  // Reference to cancel token source for canceling requests
  const cancelTokenSourceRef = useRef<CancelTokenSource | null>(null);

  /**
   * Execute the API function with the provided arguments
   * 
   * @param args - Arguments to pass to the API function
   * @returns Promise resolving to the API response data
   */
  const execute = useCallback(async (...args: any[]): Promise<any> => {
    // Set loading state
    setState(prevState => ({
      ...prevState,
      isLoading: true,
      isError: false,
      isSuccess: false
    }));

    // Create cancel token
    if (cancelTokenSourceRef.current) {
      cancelTokenSourceRef.current.cancel('Request superseded by new request');
    }
    cancelTokenSourceRef.current = axios.CancelToken.source();

    try {
      // Call API function with args and cancel token
      const apiArgs = [...args];
      
      // Find and update options object if it exists
      const lastArg = apiArgs.length > 0 ? apiArgs[apiArgs.length - 1] : undefined;
      if (lastArg && typeof lastArg === 'object' && !Array.isArray(lastArg)) {
        apiArgs[apiArgs.length - 1] = {
          ...lastArg,
          cancelToken: cancelTokenSourceRef.current.token
        };
      } else {
        // Add options object with cancel token
        apiArgs.push({ cancelToken: cancelTokenSourceRef.current.token });
      }
      
      const response = await apiFunction(...apiArgs);

      // Update state with successful response
      setState({
        data: response.data,
        error: null,
        isLoading: false,
        isSuccess: true,
        isError: false
      });

      // Call onSuccess callback if provided
      if (options.onSuccess) {
        options.onSuccess(response.data);
      }

      return response.data;
    } catch (error) {
      // Don't update state if request was cancelled
      if (axios.isCancel(error)) {
        return;
      }

      // Handle API error
      const apiErrorResponse = handleApiError(error);

      // Update state with error
      setState({
        data: null,
        error: apiErrorResponse.error,
        isLoading: false,
        isSuccess: false,
        isError: true
      });

      // Call onError callback if provided
      if (options.onError && apiErrorResponse.error) {
        options.onError(apiErrorResponse.error);
      }

      // Re-throw the error for caller handling
      throw apiErrorResponse.error;
    }
  }, [apiFunction, options.onSuccess, options.onError]);

  /**
   * Reset the hook state to its initial values
   */
  const reset = useCallback((): void => {
    setState({
      data: options.initialData || null,
      error: null,
      isLoading: false,
      isSuccess: false,
      isError: false
    });
  }, [options.initialData]);

  /**
   * Cancel the ongoing API request
   */
  const cancel = useCallback((): void => {
    if (cancelTokenSourceRef.current) {
      cancelTokenSourceRef.current.cancel('Request cancelled by user');
      cancelTokenSourceRef.current = null;
      
      setState(prevState => ({
        ...prevState,
        isLoading: false
      }));
    }
  }, []);

  // Return state and actions
  return {
    state,
    actions: {
      execute,
      reset,
      cancel
    }
  };
};

export default useApi;