/**
 * Application-wide constants for the Freight Price Movement Agent
 * This file centralizes configuration values, API endpoints, and other constants
 * to ensure consistency and maintainability throughout the application.
 */

// Application information
export const APP_NAME = "Freight Price Movement Agent";
export const APP_VERSION = "1.0.0";
export const API_VERSION = "v1";

// Default preferences
export const DEFAULT_CURRENCY = "USD";
export const DEFAULT_DATE_FORMAT = "MM/DD/YYYY";
export const DEFAULT_THEME = "light"; // Options: light, dark, system

// Storage keys for localStorage
export const STORAGE_KEYS = {
  AUTH_TOKEN: "fpma_auth_token",
  REFRESH_TOKEN: "fpma_refresh_token",
  USER_PREFERENCES: "fpma_user_prefs",
  THEME: "fpma_theme"
};

// API endpoints structured by resource
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `/api/${API_VERSION}/auth/token`,
    REFRESH: `/api/${API_VERSION}/auth/refresh`,
    REVOKE: `/api/${API_VERSION}/auth/revoke`
  },
  DATA_SOURCES: {
    BASE: `/api/${API_VERSION}/data/sources`,
    IMPORT: `/api/${API_VERSION}/data/import`,
    CONNECT: `/api/${API_VERSION}/integration/connect`,
    STATUS: `/api/${API_VERSION}/integration/status`
  },
  ANALYSIS: {
    BASE: `/api/${API_VERSION}/analysis`,
    PRICE_MOVEMENT: `/api/${API_VERSION}/analysis/price-movement`,
    RESULTS: `/api/${API_VERSION}/results`
  },
  REPORTS: {
    BASE: `/api/${API_VERSION}/reports`,
    EXPORT: `/api/${API_VERSION}/export`
  },
  USERS: {
    BASE: `/api/${API_VERSION}/users`,
    PROFILE: `/api/${API_VERSION}/users/profile`,
    PREFERENCES: `/api/${API_VERSION}/users/preferences`
  }
};

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [10, 25, 50, 100]
};

// Date format patterns
export const DATE_FORMATS = {
  MM_DD_YYYY: "MM/DD/YYYY",
  DD_MM_YYYY: "DD/MM/YYYY",
  YYYY_MM_DD: "YYYY-MM-DD",
  API_FORMAT: "YYYY-MM-DD" // Format used for API requests
};

// Threshold values for trend determination based on spec section 2.1.3
export const TREND_THRESHOLDS = {
  INCREASING: 1, // Greater than 1% means increasing
  DECREASING: -1, // Less than -1% means decreasing
  SIGNIFICANT_CHANGE: 5 // Threshold for significant change notifications
};

// Supported currencies based on common freight currencies
export const SUPPORTED_CURRENCIES = [
  "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CNY", "HKD", "SGD"
];

// Supported languages for internationalization
export const SUPPORTED_LANGUAGES = {
  EN: "en-US",
  ES: "es-ES",
  FR: "fr-FR"
};

// Chart color palette based on section 7.6.1
export const CHART_COLORS = {
  PRIMARY: "#1A5276", // Deep Blue
  SECONDARY: "#148F77", // Teal
  SUCCESS: "#27AE60", // Green
  WARNING: "#F39C12", // Amber
  DANGER: "#C0392B" // Red
};

// Validation constants based on section 6.4.1
export const VALIDATION = {
  PASSWORD_MIN_LENGTH: 12,
  USERNAME_MIN_LENGTH: 5,
  PASSWORD_PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$/,
  EMAIL_PATTERN: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
};

// Standard error messages for consistent user experience
export const ERROR_MESSAGES = {
  GENERIC_ERROR: "An unexpected error occurred. Please try again.",
  NETWORK_ERROR: "Unable to connect to the server. Please check your internet connection.",
  AUTHENTICATION_ERROR: "Authentication failed. Please login again.",
  VALIDATION_ERROR: "Please check your input and try again.",
  NOT_FOUND_ERROR: "The requested resource was not found."
};

// Feature flags to enable/disable features
export const FEATURE_FLAGS = {
  ENABLE_NOTIFICATIONS: true,
  ENABLE_ADVANCED_ANALYSIS: true,
  ENABLE_EXPORT_FEATURES: true,
  ENABLE_DARK_MODE: true
};

// Routes for navigation based on section 7.3
export const ROUTES = {
  LOGIN: "/login",
  DASHBOARD: "/dashboard",
  DATA_SOURCES: "/data-sources",
  ANALYSIS: "/analysis",
  REPORTS: "/reports",
  SETTINGS: "/settings"
};

// Timeout values (in milliseconds)
export const TIMEOUTS = {
  API_REQUEST: 30000, // 30 seconds
  SESSION_IDLE: 1800000, // 30 minutes (section 6.4.1 session timeout)
  TOAST_NOTIFICATION: 5000 // 5 seconds
};

// Debounce delay values (in milliseconds) for performance optimization
export const DEBOUNCE_DELAYS = {
  SEARCH: 300,
  FORM_INPUT: 500,
  RESIZE: 200
};