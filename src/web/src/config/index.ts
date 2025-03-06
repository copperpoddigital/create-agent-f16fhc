/**
 * index.ts
 * 
 * Central export file for all configuration modules in the Freight Price Movement Agent web application.
 * This file aggregates and re-exports configuration constants, API settings, chart configurations,
 * route definitions, and theme utilities to provide a single import point for application configuration.
 * 
 * This approach ensures consistent configuration usage across components and simplifies imports
 * throughout the application.
 */

// Import all configuration modules
import * as constants from './constants';
import * as apiConfig from './api-config';
import * as chartConfig from './chart-config';
import * as routes from './routes';
import * as theme from './theme';

// Re-export all module exports
export * from './constants';
export * from './api-config';
export * from './chart-config';
export * from './routes';
export * from './theme';

/**
 * Consolidated configuration object with key application settings
 * 
 * This object provides easy access to the most commonly used configuration values.
 * It centralizes core settings to maintain consistency across the application.
 */
export const CONFIG = {
  /** The name of the application */
  APP_NAME: constants.APP_NAME,
  
  /** The current version of the application */
  APP_VERSION: constants.APP_VERSION,
  
  /** The API version being used */
  API_VERSION: constants.API_VERSION,
  
  /** The default theme setting (light, dark, or system) */
  DEFAULT_THEME: constants.DEFAULT_THEME as theme.ThemeType,
  
  /** The default currency for displaying monetary values */
  DEFAULT_CURRENCY: constants.DEFAULT_CURRENCY,
  
  /** The default date format for displaying dates */
  DEFAULT_DATE_FORMAT: constants.DEFAULT_DATE_FORMAT
};