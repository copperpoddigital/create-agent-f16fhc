/**
 * auth-api.ts
 * 
 * Implementation of the authentication API for the Freight Price Movement Agent web application.
 * Provides functions for user authentication, token management, password operations, and user
 * profile management, implementing OAuth 2.0/JWT based authentication flow.
 */

import { apiClient, buildUrl } from './api-client';
import { ApiResponse, ApiEndpoints, HttpMethod } from '../types/api.types';
import { 
  LoginCredentials, 
  AuthTokens, 
  PasswordChangeRequest, 
  PasswordResetRequest, 
  PasswordResetConfirmRequest 
} from '../types/auth.types';
import { User } from '../types/user.types';

/**
 * Authenticates a user with username and password credentials
 * 
 * @param username - User's username
 * @param password - User's password
 * @param rememberMe - Whether to extend token lifetime
 * @returns Promise resolving to API response containing authentication tokens
 */
export async function login(
  username: string,
  password: string,
  rememberMe: boolean
): Promise<ApiResponse<AuthTokens>> {
  // Construct credentials object for login request
  const credentials: LoginCredentials = {
    username,
    password,
    rememberMe
  };

  // Build URL for the login endpoint
  const url = buildUrl(`${ApiEndpoints.AUTH}/token`);

  // Send login request
  return apiClient.request({
    url,
    method: HttpMethod.POST,
    data: credentials
  });
}

/**
 * Logs out the current user by invalidating their session
 * 
 * @returns Promise resolving to API response indicating logout success
 */
export async function logout(): Promise<ApiResponse<void>> {
  // Build URL for the logout endpoint
  const url = buildUrl(`${ApiEndpoints.AUTH}/revoke`);

  // Send logout request
  return apiClient.request({
    url,
    method: HttpMethod.POST
  });
}

/**
 * Refreshes the authentication token using a refresh token
 * 
 * @param refreshToken - Current refresh token
 * @returns Promise resolving to API response containing new authentication tokens
 */
export async function refreshToken(refreshToken: string): Promise<ApiResponse<AuthTokens>> {
  // Build URL for the token refresh endpoint
  const url = buildUrl(`${ApiEndpoints.AUTH}/refresh`);

  // Send refresh token request
  return apiClient.request({
    url,
    method: HttpMethod.POST,
    data: { refreshToken }
  });
}

/**
 * Retrieves the current user's profile information
 * 
 * @returns Promise resolving to API response containing user information
 */
export async function getUserInfo(): Promise<ApiResponse<User>> {
  // Build URL for the user info endpoint
  const url = buildUrl(`${ApiEndpoints.AUTH}/me`);

  // Send request to get user info
  return apiClient.request({
    url,
    method: HttpMethod.GET
  });
}

/**
 * Changes the current user's password
 * 
 * @param currentPassword - User's current password
 * @param newPassword - User's new password
 * @param confirmPassword - Confirmation of new password
 * @returns Promise resolving to API response indicating password change success
 */
export async function changePassword(
  currentPassword: string,
  newPassword: string,
  confirmPassword: string
): Promise<ApiResponse<void>> {
  // Validate that new password and confirmation match
  if (newPassword !== confirmPassword) {
    throw new Error('New password and confirmation do not match');
  }

  // Construct password change request
  const passwordChangeRequest: PasswordChangeRequest = {
    currentPassword,
    newPassword,
    confirmPassword
  };

  // Build URL for the password change endpoint
  const url = buildUrl(`${ApiEndpoints.AUTH}/password`);

  // Send password change request
  return apiClient.request({
    url,
    method: HttpMethod.POST,
    data: passwordChangeRequest
  });
}

/**
 * Initiates a password reset process for a user
 * 
 * @param email - Email address of the user account
 * @returns Promise resolving to API response indicating reset initiation success
 */
export async function resetPassword(email: string): Promise<ApiResponse<void>> {
  // Construct password reset request
  const passwordResetRequest: PasswordResetRequest = {
    email
  };

  // Build URL for the password reset endpoint
  const url = buildUrl(`${ApiEndpoints.AUTH}/password/reset`);

  // Send password reset request
  return apiClient.request({
    url,
    method: HttpMethod.POST,
    data: passwordResetRequest
  });
}

/**
 * Completes the password reset process with a token and new password
 * 
 * @param token - Password reset token received via email
 * @param newPassword - New password to set
 * @param confirmPassword - Confirmation of new password
 * @returns Promise resolving to API response indicating reset completion success
 */
export async function confirmPasswordReset(
  token: string,
  newPassword: string,
  confirmPassword: string
): Promise<ApiResponse<void>> {
  // Validate that new password and confirmation match
  if (newPassword !== confirmPassword) {
    throw new Error('New password and confirmation do not match');
  }

  // Construct password reset confirmation request
  const passwordResetConfirmRequest: PasswordResetConfirmRequest = {
    token,
    newPassword,
    confirmPassword
  };

  // Build URL for the password reset confirmation endpoint
  const url = buildUrl(`${ApiEndpoints.AUTH}/password/reset/confirm`);

  // Send password reset confirmation request
  return apiClient.request({
    url,
    method: HttpMethod.POST,
    data: passwordResetConfirmRequest
  });
}

/**
 * Validates if the current authentication token is still valid
 * 
 * @returns Promise resolving to API response indicating token validity
 */
export async function validateToken(): Promise<ApiResponse<boolean>> {
  // Build URL for the token validation endpoint
  const url = buildUrl(`${ApiEndpoints.AUTH}/validate`);

  // Send token validation request
  return apiClient.request({
    url,
    method: HttpMethod.GET
  });
}