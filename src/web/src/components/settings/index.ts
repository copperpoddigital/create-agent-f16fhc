/**
 * Barrel file that exports all settings-related components for easier imports throughout the application
 * @file src/web/src/components/settings/index.ts
 * @requires module:./NotificationSettings
 * @requires module:./SystemSettings
 * @requires module:./UserPreferences
 * @exports NotificationSettings
 * @exports SystemSettings
 * @exports UserPreferences
 * @see Technical Specifications/7. USER INTERFACE DESIGN/7.3 WIREFRAMES/7.3.8 Settings
 */

// Import the NotificationSettings component for re-export
import NotificationSettings from './NotificationSettings';

// Import the SystemSettings component for re-export
import SystemSettings from './SystemSettings';

// Import the UserPreferences component for re-export
import UserPreferences from './UserPreferences';

/**
 * Export the NotificationSettings component for use in the Settings page
 * @component
 * @exports NotificationSettings
 */
export { NotificationSettings };

/**
 * Export the SystemSettings component for use in the Settings page
 * @component
 * @exports SystemSettings
 */
export { SystemSettings };

/**
 * Export the UserPreferences component for use in the Settings page
 * @component
 * @exports UserPreferences
 */
export { UserPreferences };