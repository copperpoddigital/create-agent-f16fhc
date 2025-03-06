/**
 * Type definitions for user-related data structures in the Freight Price Movement Agent.
 * Provides type definitions for user profiles, preferences, roles, and related request/response objects.
 */

/**
 * Enum defining user roles for authorization.
 * Used for role-based access control throughout the application.
 */
export enum UserRole {
  ADMIN = 'admin',      // Full system access including user management and system settings
  MANAGER = 'manager',  // Access to create and manage analyses, reports, and data sources
  ANALYST = 'analyst',  // Create and run analyses, view reports
  VIEWER = 'viewer'     // Read-only access to view reports and analyses
}

/**
 * Enum defining UI theme options for user preferences.
 */
export enum Theme {
  LIGHT = 'light',   // Light theme
  DARK = 'dark',     // Dark theme
  SYSTEM = 'system'  // Follow system preferences
}

/**
 * Enum defining date format options for user preferences.
 */
export enum DateFormat {
  MM_DD_YYYY = 'MM/DD/YYYY',  // Month/Day/Year format (e.g., 12/31/2023)
  DD_MM_YYYY = 'DD/MM/YYYY',  // Day/Month/Year format (e.g., 31/12/2023)
  YYYY_MM_DD = 'YYYY-MM-DD'   // Year-Month-Day format (e.g., 2023-12-31)
}

/**
 * Interface defining user preference settings.
 */
export interface UserPreferences {
  /** Percentage threshold to trigger notifications for significant price changes */
  significantPriceChangeThreshold: number;
  /** Default view when user logs in (e.g., 'dashboard', 'analysis') */
  defaultView: string;
  /** User's customized dashboard layout configuration */
  dashboardLayout: {
    [key: string]: any;
  };
  /** Whether to notify the user about significant price changes */
  notifyOnPriceChanges: boolean;
  /** Whether to notify the user about data source updates */
  notifyOnDataSourceUpdates: boolean;
  /** Whether to notify the user about scheduled system maintenance */
  notifyOnSystemMaintenance: boolean;
}

/**
 * Interface defining user profile data structure.
 */
export interface User {
  /** Unique identifier for the user */
  id: string;
  /** Username for login */
  username: string;
  /** User's email address */
  email: string;
  /** User's first name */
  firstName: string | null;
  /** User's last name */
  lastName: string | null;
  /** User's role for access control */
  role: UserRole;
  /** Whether the user account is active */
  isActive: boolean;
  /** Whether the user account is locked due to security issues */
  isLocked: boolean;
  /** Timestamp of the user's last login */
  lastLogin: string | null;
  /** User's preferred currency for displaying monetary values */
  defaultCurrency: string | null;
  /** User's preferred date format */
  dateFormat: DateFormat | null;
  /** User's preferred UI theme */
  theme: Theme | null;
  /** Whether the user receives email notifications */
  emailNotifications: boolean;
  /** Whether the user receives SMS notifications */
  smsNotifications: boolean;
  /** Whether the user receives in-app notifications */
  inAppNotifications: boolean;
  /** User's additional preference settings */
  preferences: UserPreferences | null;
  /** Timestamp when the user account was created */
  createdAt: string;
  /** Timestamp when the user account was last updated */
  updatedAt: string;
}

/**
 * Interface for user profile update request payload.
 */
export interface UserProfileUpdateRequest {
  /** Updated first name */
  firstName: string;
  /** Updated last name */
  lastName: string;
  /** Updated email address */
  email: string;
}

/**
 * Interface for user preferences update request payload.
 */
export interface UserPreferencesUpdateRequest {
  /** Updated default currency */
  defaultCurrency: string;
  /** Updated date format preference */
  dateFormat: DateFormat;
  /** Updated theme preference */
  theme: Theme;
  /** Updated email notification setting */
  emailNotifications: boolean;
  /** Updated SMS notification setting */
  smsNotifications: boolean;
  /** Updated in-app notification setting */
  inAppNotifications: boolean;
  /** Updated additional preferences */
  preferences: Partial<UserPreferences>;
}

/**
 * Interface for user creation request payload.
 */
export interface UserCreateRequest {
  /** New user's username */
  username: string;
  /** New user's email address */
  email: string;
  /** New user's initial password */
  password: string;
  /** New user's first name */
  firstName: string;
  /** New user's last name */
  lastName: string;
  /** New user's role */
  role: UserRole;
}

/**
 * Interface for user role update request payload.
 */
export interface UserRoleUpdateRequest {
  /** Updated user role */
  role: UserRole;
}

/**
 * Interface for user status update request payload.
 */
export interface UserStatusUpdateRequest {
  /** Updated active status */
  isActive: boolean;
}

/**
 * Interface for user notification settings update request payload.
 */
export interface UserNotificationSettingsUpdateRequest {
  /** Whether to enable email notifications */
  emailNotifications: boolean;
  /** Whether to enable SMS notifications */
  smsNotifications: boolean;
  /** Whether to enable in-app notifications */
  inAppNotifications: boolean;
  /** Whether to notify on significant price changes */
  notifyOnPriceChanges: boolean;
  /** Whether to notify on data source updates */
  notifyOnDataSourceUpdates: boolean;
  /** Whether to notify on system maintenance */
  notifyOnSystemMaintenance: boolean;
  /** Percentage threshold for significant price change notifications */
  significantPriceChangeThreshold: number;
}