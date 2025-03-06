/**
 * AuthContext.tsx
 * 
 * Authentication context provider for the Freight Price Movement Agent web application.
 * Manages user authentication state, login/logout operations, token refresh, and
 * other authentication-related functionality throughout the application.
 * 
 * Implements OAuth 2.0 / JWT based authentication with secure token handling
 * and session management as specified in the Security Architecture section.
 */

import { createContext, useReducer, useEffect, useCallback, ReactNode, FC, useRef } from 'react'; // ^18.2.0
import { 
  AuthState, 
  AuthAction, 
  AuthActionType, 
  AuthContextType, 
  LoginCredentials 
} from '../types/auth.types';
import { 
  login as apiLogin, 
  logout as apiLogout, 
  refreshToken as apiRefreshToken, 
  getUserInfo, 
  changePassword as apiChangePassword, 
  resetPassword as apiResetPassword, 
  confirmPasswordReset as apiConfirmPasswordReset 
} from '../api/auth-api';
import { 
  getAuthToken, 
  setAuthToken, 
  removeAuthToken, 
  getLocalStorageItem, 
  setLocalStorageItem, 
  removeLocalStorageItem 
} from '../utils/storage-utils';
import { TIMEOUTS, STORAGE_KEYS } from '../config/constants';

/**
 * Initial authentication state with no user and no tokens
 */
export const initialAuthState: AuthState = {
  isAuthenticated: false,
  user: null,
  accessToken: null,
  refreshToken: null,
  expiresAt: null,
  isLoading: false,
  error: null
};

/**
 * Create the authentication context with initial values
 */
export const AuthContext = createContext<AuthContextType>({
  state: initialAuthState,
  login: async () => {},
  logout: async () => {},
  refreshSession: async () => false,
  changePassword: async () => {},
  resetPassword: async () => {},
  confirmPasswordReset: async () => {}
});

/**
 * Reducer function for managing authentication state transitions
 * 
 * @param state - Current authentication state
 * @param action - Action to perform on the state
 * @returns Updated authentication state
 */
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case AuthActionType.LOGIN_REQUEST:
      return {
        ...state,
        isLoading: true,
        error: null
      };
    case AuthActionType.LOGIN_SUCCESS:
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        expiresAt: action.payload.expiresAt,
        isLoading: false,
        error: null
      };
    case AuthActionType.LOGIN_FAILURE:
      return {
        ...state,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload.error
      };
    case AuthActionType.LOGOUT:
      return initialAuthState;
    case AuthActionType.REFRESH_TOKEN:
      return {
        ...state,
        accessToken: action.payload.accessToken,
        refreshToken: action.payload.refreshToken,
        expiresAt: action.payload.expiresAt,
        error: null
      };
    case AuthActionType.SET_USER:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true
      };
    case AuthActionType.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    default:
      return state;
  }
};

/**
 * Authentication Provider component that manages authentication state
 * and provides auth context to the application
 */
export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialAuthState);
  // Reference to store timeout ID for token refresh
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Authenticates a user with username and password
   * 
   * @param username - User's username
   * @param password - User's password
   * @param rememberMe - Optional parameter to extend token lifetime
   */
  const login = async (username: string, password: string, rememberMe = false): Promise<void> => {
    dispatch({ type: AuthActionType.LOGIN_REQUEST });
    
    try {
      // Call login API with credentials
      const response = await apiLogin(username, password, rememberMe);
      
      if (response.success && response.data) {
        // Get token data from response
        const { accessToken, refreshToken, expiresAt } = response.data;
        
        // Store tokens in localStorage
        setAuthToken(accessToken);
        setLocalStorageItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
        
        // Get user info using the new token
        const userResponse = await getUserInfo();
        
        if (userResponse.success && userResponse.data) {
          // Update auth state with user and token info
          dispatch({
            type: AuthActionType.LOGIN_SUCCESS,
            payload: {
              user: userResponse.data,
              accessToken,
              refreshToken,
              expiresAt
            }
          });
          
          // Setup token refresh
          setupTokenRefresh(expiresAt);
        } else {
          throw new Error('Failed to get user information');
        }
      } else {
        throw new Error(response.error?.message || 'Login failed');
      }
    } catch (error) {
      dispatch({
        type: AuthActionType.LOGIN_FAILURE,
        payload: {
          error: error instanceof Error ? error.message : 'An unknown error occurred'
        }
      });
    }
  };

  /**
   * Logs out the current user by revoking tokens and clearing state
   */
  const logout = async (): Promise<void> => {
    try {
      // Call logout API if authenticated
      if (state.isAuthenticated) {
        await apiLogout();
      }
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      // Always clear tokens and state even if API call fails
      removeAuthToken();
      removeLocalStorageItem(STORAGE_KEYS.REFRESH_TOKEN);
      
      // Clear refresh timer
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
        refreshTimeoutRef.current = null;
      }
      
      // Reset auth state
      dispatch({ type: AuthActionType.LOGOUT });
    }
  };

  /**
   * Refreshes the authentication session using the refresh token
   * 
   * @returns Promise resolving to true if refresh was successful, false otherwise
   */
  const refreshSession = async (): Promise<boolean> => {
    // Get current refresh token
    const currentRefreshToken = state.refreshToken || 
                              getLocalStorageItem<string>(STORAGE_KEYS.REFRESH_TOKEN);
    
    if (!currentRefreshToken) {
      return false;
    }
    
    try {
      // Call refresh token API
      const response = await apiRefreshToken(currentRefreshToken);
      
      if (response.success && response.data) {
        // Get new token data
        const { accessToken, refreshToken: newRefreshToken, expiresAt } = response.data;
        
        // Update stored tokens
        setAuthToken(accessToken);
        setLocalStorageItem(STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken);
        
        // Update auth state
        dispatch({
          type: AuthActionType.REFRESH_TOKEN,
          payload: {
            accessToken,
            refreshToken: newRefreshToken,
            expiresAt
          }
        });
        
        // Setup new refresh timer
        setupTokenRefresh(expiresAt);
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error refreshing token:', error);
      
      // Handle token expiration by logging out
      await logout();
      
      return false;
    }
  };

  /**
   * Sets up automatic token refresh before expiration
   * 
   * @param expiresAt - Timestamp when the token expires
   */
  const setupTokenRefresh = useCallback((expiresAt: number): void => {
    // Clear any existing refresh timer
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }
    
    // Calculate time until expiration in milliseconds
    const currentTime = Date.now();
    const timeUntilExpiry = expiresAt - currentTime;
    
    // Set the refresh to happen 5 minutes before expiration
    // or immediately if less than 5 minutes remain
    const refreshTime = Math.max(0, timeUntilExpiry - (5 * 60 * 1000));
    
    // Set timeout to refresh the token
    refreshTimeoutRef.current = setTimeout(() => {
      refreshSession();
    }, refreshTime);
  }, []);

  /**
   * Checks for existing authentication on component mount
   */
  const checkInitialAuth = useCallback(async (): Promise<void> => {
    const storedToken = getAuthToken();
    
    if (storedToken) {
      try {
        // Attempt to refresh the token or validate it
        const isValid = await refreshSession();
        
        if (isValid) {
          // Get user info
          const userResponse = await getUserInfo();
          
          if (userResponse.success && userResponse.data) {
            // Update auth state with user info
            dispatch({
              type: AuthActionType.SET_USER,
              payload: {
                user: userResponse.data
              }
            });
          }
        }
      } catch (error) {
        console.error('Error checking initial auth:', error);
        
        // Handle any errors by logging out
        await logout();
      }
    }
  }, []);

  /**
   * Changes the user's password
   * 
   * @param currentPassword - Current password for verification
   * @param newPassword - New password to set
   * @param confirmPassword - Confirmation of new password
   */
  const changePassword = async (
    currentPassword: string, 
    newPassword: string, 
    confirmPassword: string
  ): Promise<void> => {
    try {
      // Call change password API
      const response = await apiChangePassword(currentPassword, newPassword, confirmPassword);
      
      if (!response.success) {
        throw new Error(response.error?.message || 'Failed to change password');
      }
    } catch (error) {
      console.error('Error changing password:', error);
      throw error; // Let the UI handle the error
    }
  };

  /**
   * Initiates password reset process
   * 
   * @param email - Email address for the account
   */
  const resetPassword = async (email: string): Promise<void> => {
    try {
      // Call reset password API
      const response = await apiResetPassword(email);
      
      if (!response.success) {
        throw new Error(response.error?.message || 'Failed to reset password');
      }
    } catch (error) {
      console.error('Error resetting password:', error);
      throw error; // Let the UI handle the error
    }
  };

  /**
   * Completes password reset process
   * 
   * @param token - Password reset token from email
   * @param newPassword - New password to set
   * @param confirmPassword - Confirmation of new password
   */
  const confirmPasswordReset = async (
    token: string, 
    newPassword: string, 
    confirmPassword: string
  ): Promise<void> => {
    try {
      // Call confirm password reset API
      const response = await apiConfirmPasswordReset(token, newPassword, confirmPassword);
      
      if (!response.success) {
        throw new Error(response.error?.message || 'Failed to confirm password reset');
      }
    } catch (error) {
      console.error('Error confirming password reset:', error);
      throw error; // Let the UI handle the error
    }
  };

  // Check initial auth on mount and setup session timeout
  useEffect(() => {
    checkInitialAuth();
    
    // Set up session timeout for inactivity
    const sessionTimeoutId = setTimeout(() => {
      // Only logout if the user is authenticated
      if (state.isAuthenticated) {
        logout();
      }
    }, TIMEOUTS.SESSION_IDLE);
    
    // Cleanup refresh timer and session timeout on unmount
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
      clearTimeout(sessionTimeoutId);
    };
  }, [checkInitialAuth]);

  // Context value
  const contextValue: AuthContextType = {
    state,
    login,
    logout,
    refreshSession,
    changePassword,
    resetPassword,
    confirmPasswordReset
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};