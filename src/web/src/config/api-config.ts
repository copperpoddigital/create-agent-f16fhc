/**
 * API Configuration
 * 
 * Centralized API configuration for the Freight Price Movement Agent web application.
 * This file defines API connection settings, authentication parameters,
 * request headers, and error handling configurations used throughout the
 * application for consistent API communication.
 */

import { API_VERSION, STORAGE_KEYS, TIMEOUTS } from './constants';

/**
 * Core API configuration settings
 */
export const API_CONFIG = {
  // Base URL for API requests, configured for different environments
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // API path prefix
  API_PATH: '/api',
  
  // Request timeout in milliseconds
  TIMEOUT: TIMEOUTS.API_REQUEST,
  
  // Number of retry attempts for failed requests
  RETRY_ATTEMPTS: 3,
  
  // API version from constants
  VERSION: API_VERSION
};

/**
 * Authentication configuration
 */
export const AUTH_CONFIG = {
  // Storage key for authentication token
  TOKEN_KEY: STORAGE_KEYS.AUTH_TOKEN,
  
  // Storage key for refresh token
  REFRESH_TOKEN_KEY: STORAGE_KEYS.REFRESH_TOKEN,
  
  // Buffer time in milliseconds before token expiry to trigger refresh (5 minutes)
  TOKEN_EXPIRY_BUFFER: 5 * 60 * 1000,
  
  // Token type used in Authorization header
  TOKEN_TYPE: 'Bearer'
};

/**
 * Standard request headers for different content types
 */
export const REQUEST_HEADERS = {
  // Default headers for all requests
  DEFAULT: {
    'Accept': 'application/json',
    'Accept-Version': API_VERSION
  },
  
  // Headers for JSON content
  JSON: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Accept-Version': API_VERSION
  },
  
  // Headers for multipart form data (file uploads)
  MULTIPART: {
    'Accept': 'application/json',
    'Accept-Version': API_VERSION
    // Content-Type is automatically set by the browser with the boundary parameter
  }
};

/**
 * Error handling configuration for API requests
 */
export const ERROR_HANDLING = {
  // HTTP status codes that should trigger retry attempts
  RETRY_STATUS_CODES: [408, 429, 500, 502, 503, 504],
  
  // Base delay between retries in milliseconds (increases with backoff)
  RETRY_DELAY: 1000,
  
  // Default error message when no specific message is available
  DEFAULT_ERROR_MESSAGE: 'An error occurred while processing your request. Please try again later.',
  
  // Common error codes and their meanings
  ERROR_CODES: {
    'UNAUTHORIZED': 'Authentication required. Please log in.',
    'FORBIDDEN': 'You do not have permission to perform this action.',
    'NOT_FOUND': 'The requested resource was not found.',
    'VALIDATION_ERROR': 'Please check your input and try again.',
    'RATE_LIMITED': 'Too many requests. Please try again later.',
    'SERVER_ERROR': 'A server error occurred. Please try again later.'
  }
};

/**
 * Environment detection for conditional API behavior
 */
export const ENVIRONMENT = {
  IS_DEVELOPMENT: process.env.NODE_ENV === 'development',
  IS_PRODUCTION: process.env.NODE_ENV === 'production',
  IS_TEST: process.env.NODE_ENV === 'test'
};

/**
 * Utility function to construct complete API URLs
 * 
 * @param endpoint - The API endpoint path (already containing version if needed)
 * @returns The complete API URL
 */
export const buildApiUrl = (endpoint: string): string => {
  // If the endpoint is already a full URL, return it as is
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint;
  }
  
  // Ensure endpoint starts with /
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Return the full URL
  return `${API_CONFIG.BASE_URL}${normalizedEndpoint}`;
};