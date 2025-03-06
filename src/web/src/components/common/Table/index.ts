/**
 * Table component barrel file
 * Re-exports the Table component and its related types
 * for easier imports throughout the application
 */

// Re-export the Table component as the default export
export { default } from './Table';

// Re-export interfaces for type checking in consuming components
export type { TableProps, TableColumn } from './Table';