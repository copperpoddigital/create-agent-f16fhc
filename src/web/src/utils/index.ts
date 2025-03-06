/**
 * utils/index.ts
 *
 * Central export file for utility functions used throughout the Freight Price Movement Agent web application.
 * This file aggregates and re-exports all utility functions from specialized utility modules to provide
 * a single import point for consumers.
 */

// Re-export all date utility functions
export * from './date-utils';

// Re-export all currency utility functions
export * from './currency-utils';

// Re-export all formatting utility functions
export * from './format-utils';

// Re-export all validation utility functions
export * from './validation-utils';

// Re-export all storage utility functions
export * from './storage-utils';

// Re-export all chart utility functions
export * from './chart-utils';

// Re-export test utility functions (only in non-production environments)
if (process.env.NODE_ENV !== 'production') {
  export * from './test-utils';
}