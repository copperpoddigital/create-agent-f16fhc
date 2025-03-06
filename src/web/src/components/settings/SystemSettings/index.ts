/**
 * Index file for System Settings component
 * 
 * This file exports the SystemSettings component which provides administrators
 * with an interface to configure system-wide settings for the Freight Price
 * Movement Agent application, including data retention policies, refresh intervals,
 * API rate limits, and other system-level configurations.
 */

// Import the SystemSettings component for re-export
import SystemSettingsComponent from './SystemSettings';

// Re-export as default export
export default SystemSettingsComponent;

// Also re-export as named export for more flexible importing options
export { SystemSettingsComponent };