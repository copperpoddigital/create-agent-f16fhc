/**
 * Type definitions for authentication-related data structures in the Freight Price Movement Agent.
 * Provides type definitions for authentication state, tokens, context, and actions.
 */

import { User } from './user.types';

/**
 * Interface for authentication tokens returned from the API.
 * Follows OAuth 2.0/JWT token structure.
 */
export interface AuthTokens {
  /** JWT access token for API authorization */
  accessToken: string;
  /** Refresh token for obtaining new access tokens */
  refreshToken: string;
  /** Timestamp when the access token expires (Unix timestamp in milliseconds) */
  expiresAt: number;
  /** Type of token, typically "Bearer" */
  tokenType: string;
}

/**
 * Interface for authentication state in the application.
 * Tracks current user session information.
 */
export interface AuthState {
  /** Whether the user is currently authenticated */
  isAuthenticated: boolean;
  /** The currently authenticated user, if any */
  user: User | null;
  /** The current JWT access token */
  accessToken: string | null;
  /** The current refresh token */
  refreshToken: string | null;
  /** Timestamp when the current access token expires */
  expiresAt: number | null;
  /** Whether an authentication operation is in progress */
  isLoading: boolean;
  /** Error message from failed authentication, if any */
  error: string | null;
}

/**
 * Enum of action types for authentication state management.
 * Used in the auth reducer for state transitions.
 */
export enum AuthActionType {
  /** Action dispatched when a login request is initiated */
  LOGIN_REQUEST = 'LOGIN_REQUEST',
  /** Action dispatched when a login request succeeds */
  LOGIN_SUCCESS = 'LOGIN_SUCCESS',
  /** Action dispatched when a login request fails */
  LOGIN_FAILURE = 'LOGIN_FAILURE',
  /** Action dispatched when the user logs out */
  LOGOUT = 'LOGOUT',
  /** Action dispatched when the access token is refreshed */
  REFRESH_TOKEN = 'REFRESH_TOKEN',
  /** Action dispatched when the user profile is updated */
  SET_USER = 'SET_USER',
  /** Action dispatched to clear authentication errors */
  CLEAR_ERROR = 'CLEAR_ERROR'
}

/**
 * Union type for authentication actions in the reducer.
 * Defines the shape of each action and its payload.
 */
export type AuthAction =
  | { type: AuthActionType.LOGIN_REQUEST }
  | { 
      type: AuthActionType.LOGIN_SUCCESS; 
      payload: { 
        user: User; 
        accessToken: string; 
        refreshToken: string; 
        expiresAt: number; 
      }
    }
  | { 
      type: AuthActionType.LOGIN_FAILURE; 
      payload: { 
        error: string 
      }
    }
  | { type: AuthActionType.LOGOUT }
  | { 
      type: AuthActionType.REFRESH_TOKEN; 
      payload: { 
        accessToken: string; 
        refreshToken: string; 
        expiresAt: number; 
      }
    }
  | { 
      type: AuthActionType.SET_USER; 
      payload: { 
        user: User 
      }
    }
  | { type: AuthActionType.CLEAR_ERROR };

/**
 * Interface for the authentication context provided to components.
 * Defines methods for authentication operations.
 */
export interface AuthContextType {
  /** Current authentication state */
  state: AuthState;
  /** Method to authenticate a user with username and password */
  login: (username: string, password: string) => Promise<void>;
  /** Method to log out the current user */
  logout: () => Promise<void>;
  /** Method to refresh the current session using the refresh token */
  refreshSession: () => Promise<boolean>;
  /** Method to change the user's password */
  changePassword: (currentPassword: string, newPassword: string, confirmPassword: string) => Promise<void>;
  /** Method to initiate a password reset */
  resetPassword: (email: string) => Promise<void>;
  /** Method to confirm a password reset with a token */
  confirmPasswordReset: (token: string, newPassword: string, confirmPassword: string) => Promise<void>;
}

/**
 * Interface for login form credentials.
 */
export interface LoginCredentials {
  /** Username for authentication */
  username: string;
  /** Password for authentication */
  password: string;
  /** Whether to persist the session beyond the browser session */
  rememberMe: boolean;
}

/**
 * Interface for password change request.
 */
export interface PasswordChangeRequest {
  /** User's current password for verification */
  currentPassword: string;
  /** User's new password */
  newPassword: string;
  /** Confirmation of the new password to prevent typos */
  confirmPassword: string;
}

/**
 * Interface for password reset request.
 */
export interface PasswordResetRequest {
  /** Email address for the account to reset */
  email: string;
}

/**
 * Interface for password reset confirmation request.
 */
export interface PasswordResetConfirmRequest {
  /** Token received via email to verify the reset request */
  token: string;
  /** New password to set */
  newPassword: string;
  /** Confirmation of the new password to prevent typos */
  confirmPassword: string;
}