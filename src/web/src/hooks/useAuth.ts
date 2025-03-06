/**
 * useAuth.ts
 * 
 * A custom React hook that provides access to authentication context and functionality
 * throughout the Freight Price Movement Agent web application. This hook simplifies
 * authentication operations by exposing login, logout, and token management functions
 * to components.
 */

import React, { useContext } from 'react'; // ^18.2.0
import { AuthContext } from '../contexts/AuthContext';
import { AuthContextType } from '../types/auth.types';

/**
 * Custom hook that provides access to authentication context and functionality
 * throughout the application
 * 
 * @returns Authentication context containing state and functions including:
 *   - state: Current authentication state (user, tokens, loading status)
 *   - login: Function to authenticate a user
 *   - logout: Function to log out the current user
 *   - refreshSession: Function to refresh the authentication token
 *   - changePassword: Function to change the user's password
 *   - resetPassword: Function to initiate a password reset
 *   - confirmPasswordReset: Function to complete a password reset
 * 
 * @throws Error if used outside of an AuthProvider
 */
const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default useAuth;