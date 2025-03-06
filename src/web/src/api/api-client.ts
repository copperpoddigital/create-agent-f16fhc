/**
 * api-client.ts
 *
 * Core API client implementation for the Freight Price Movement Agent web application.
 * Configures and exports an Axios instance with interceptors for authentication,
 * error handling, and request/response processing.
 */

import axios, { 
  AxiosInstance, 
  AxiosRequestConfig, 
  AxiosResponse, 
  AxiosError 
} from 'axios'; // ^1.4.0

import { 
  API_CONFIG,
  REQUEST_HEADERS,
  ERROR_HANDLING,
  AUTH_CONFIG
} from '../config/api-config';

import { STORAGE_KEYS } from '../config/constants';
import { getStoredItem } from '../utils/storage-utils';
import { ApiResponse, ApiError } from '../types/api.types';

/**
 * Creates and configures an Axios instance with interceptors for the Freight Price Movement Agent
 * 
 * @returns Configured Axios instance for API communication
 */
function createApiClient(): AxiosInstance {
  // Create Axios instance with base configuration
  const instance = axios.create({
    baseURL: `${API_CONFIG.BASE_URL}${API_CONFIG.API_PATH}/${API_CONFIG.VERSION}`,
    timeout: API_CONFIG.TIMEOUT,
    headers: REQUEST_HEADERS.DEFAULT
  });

  // Request interceptor for setting default headers
  instance.interceptors.request.use(
    (config) => {
      // Merge default headers with request-specific headers
      config.headers = {
        ...REQUEST_HEADERS.DEFAULT,
        ...config.headers
      };

      return config;
    },
    (error) => Promise.reject(error)
  );

  // Request interceptor for authentication
  instance.interceptors.request.use(
    (config) => {
      // Get auth token from storage
      const token = getStoredItem<string>(STORAGE_KEYS.AUTH_TOKEN, null);
      
      // Add token to headers if available
      if (token) {
        config.headers = {
          ...config.headers,
          'Authorization': `${AUTH_CONFIG.TOKEN_TYPE} ${token}`
        };
      }
      
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for successful responses
  instance.interceptors.response.use(
    (response) => {
      // If response is already in the expected format, return it directly
      if (response.data && (response.data.success !== undefined)) {
        return response.data;
      }
      
      // Wrap in standard response format if not already formatted
      const apiResponse: ApiResponse = {
        success: true,
        data: response.data,
        error: null,
        meta: {
          timestamp: new Date().toISOString(),
          requestId: response.headers['x-request-id'] || null,
          processingTime: response.headers['x-processing-time'] ? 
                          parseInt(response.headers['x-processing-time'], 10) : null,
          pagination: null
        }
      };
      
      return apiResponse;
    }
  );

  // Response interceptor for errors
  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      // Handle 401 Unauthorized errors
      if (error.response?.status === 401) {
        // Clear the auth header - token refresh would be implemented here
        clearAuthorizationHeader();
      }
      
      // Attempt to retry the request if applicable
      if (error.config) {
        // Add a custom property to track retry attempts
        const retryCount = (error.config as any)._retryCount || 0;
        
        try {
          return await retryRequest(error, retryCount);
        } catch (retryError) {
          // If retry fails, handle the error
          return Promise.reject(handleApiError(error));
        }
      }
      
      // If not retryable, handle the error
      return Promise.reject(handleApiError(error));
    }
  );

  return instance;
}

/**
 * Sets the Authorization header with the provided token
 * 
 * @param token - Authentication token
 */
function setAuthorizationHeader(token: string): void {
  if (!token) {
    return;
  }
  
  // Set the Authorization header in the default headers
  REQUEST_HEADERS.DEFAULT['Authorization'] = `${AUTH_CONFIG.TOKEN_TYPE} ${token}`;
  
  // Log success in development
  if (process.env.NODE_ENV === 'development') {
    console.log('Authorization header set successfully');
  }
}

/**
 * Clears the Authorization header from API requests
 */
function clearAuthorizationHeader(): void {
  // Remove Authorization header
  delete REQUEST_HEADERS.DEFAULT['Authorization'];
  
  // Log success in development
  if (process.env.NODE_ENV === 'development') {
    console.log('Authorization header cleared successfully');
  }
}

/**
 * Constructs a complete API URL with proper path and version
 * 
 * @param endpoint - The endpoint path
 * @param params - Optional path parameters to replace in the URL
 * @returns Complete API URL with path parameters replaced
 */
function buildUrl(endpoint: string, params?: Record<string, string | number>): string {
  // Start with base API path
  let url = `${API_CONFIG.API_PATH}/${API_CONFIG.VERSION}`;
  
  // Append endpoint, ensuring it starts with a slash
  url += endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Replace path parameters if provided
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url = url.replace(`:${key}`, String(value));
    });
  }
  
  return url;
}

/**
 * Processes Axios errors into standardized API error responses
 * 
 * @param error - Axios error object
 * @returns Standardized error response
 */
function handleApiError(error: AxiosError): ApiResponse {
  let errorResponse: ApiError = {
    code: 'UNKNOWN_ERROR',
    message: ERROR_HANDLING.DEFAULT_ERROR_MESSAGE,
    details: null,
    path: error.config?.url || null
  };
  
  // If server responded with an error
  if (error.response) {
    const responseData = error.response.data as any;
    
    // Use error data from response if available
    if (responseData && responseData.error) {
      errorResponse = {
        ...errorResponse,
        ...responseData.error
      };
    } else if (responseData && responseData.message) {
      // Sometimes error is in a message field
      errorResponse.message = responseData.message;
      errorResponse.code = responseData.code || error.response.status;
    } else {
      // Create error from status
      errorResponse.code = error.response.status;
      errorResponse.message = error.response.statusText || ERROR_HANDLING.DEFAULT_ERROR_MESSAGE;
    }
  } 
  // If error occurred during request setup
  else if (error.request) {
    errorResponse.code = 'NETWORK_ERROR';
    errorResponse.message = 'Network error occurred. Please check your connection.';
  }
  
  // Create standardized response format
  const standardizedResponse: ApiResponse = {
    success: false,
    data: null,
    error: errorResponse,
    meta: {
      timestamp: new Date().toISOString(),
      requestId: null,
      processingTime: null,
      pagination: null
    }
  };
  
  // Log error in development
  if (process.env.NODE_ENV === 'development') {
    console.error('API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      error: errorResponse
    });
  }
  
  return standardizedResponse;
}

/**
 * Implements retry logic for failed API requests
 * 
 * @param error - Axios error that occurred
 * @param retryCount - Current retry attempt count
 * @returns Promise resolving to successful response or rejecting with error
 */
async function retryRequest(error: AxiosError, retryCount: number): Promise<AxiosResponse> {
  const status = error.response?.status;
  
  // Don't retry client errors except for specific status codes
  if (
    status && 
    ERROR_HANDLING.RETRY_STATUS_CODES.includes(status) && 
    retryCount < API_CONFIG.RETRY_ATTEMPTS
  ) {
    // Exponential backoff with jitter
    const delay = ERROR_HANDLING.RETRY_DELAY * Math.pow(2, retryCount) + Math.random() * 100;
    
    // Wait for delay
    await new Promise(resolve => setTimeout(resolve, delay));
    
    // Get the original request configuration
    const config = error.config;
    
    if (config) {
      // Increment retry count
      (config as any)._retryCount = retryCount + 1;
      
      // Log retry attempt in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`Retrying request (${retryCount + 1}/${API_CONFIG.RETRY_ATTEMPTS}): ${config.url}`);
      }
      
      // Retry the request
      return axios(config);
    }
  }
  
  // If not retryable or max retries reached, reject
  return Promise.reject(error);
}

// Create the API client instance
const apiClient = createApiClient();

// Export the API client and utility functions
export {
  apiClient,
  setAuthorizationHeader,
  clearAuthorizationHeader,
  buildUrl
};