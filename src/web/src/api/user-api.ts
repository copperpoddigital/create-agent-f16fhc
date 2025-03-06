/**
 * User Management API functions for the Freight Price Movement Agent web application.
 * Provides methods for retrieving, creating, updating, and managing user accounts and their preferences.
 * 
 * This module implements the requirements from:
 * - Technical Specifications/6.4 SECURITY ARCHITECTURE/6.4.1 AUTHENTICATION FRAMEWORK
 * - Technical Specifications/6.4 SECURITY ARCHITECTURE/6.4.2 AUTHORIZATION SYSTEM
 * - Technical Specifications/7.7 ACCESSIBILITY CONSIDERATIONS
 */

import { 
  apiClient, 
  buildUrl 
} from './api-client';

import { 
  ApiResponse,
  ApiEndpoints,
  HttpMethod,
  PaginationParams
} from '../types/api.types';

import {
  User,
  UserProfileUpdateRequest,
  UserPreferencesUpdateRequest,
  UserCreateRequest,
  UserRoleUpdateRequest,
  UserStatusUpdateRequest,
  UserNotificationSettingsUpdateRequest
} from '../types/user.types';

/**
 * Retrieves a paginated list of users
 * 
 * @param paginationParams - Pagination and sorting parameters
 * @returns Promise resolving to API response containing array of users
 */
export async function getUsers(paginationParams: PaginationParams): Promise<ApiResponse<User[]>> {
  const url = buildUrl(`${ApiEndpoints.USERS}`);
  return await apiClient.request({
    url,
    method: HttpMethod.GET,
    params: paginationParams
  });
}

/**
 * Retrieves a specific user by ID
 * 
 * @param userId - ID of the user to retrieve
 * @returns Promise resolving to API response containing user data
 */
export async function getUserById(userId: string): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/${userId}`);
  return await apiClient.request({
    url,
    method: HttpMethod.GET
  });
}

/**
 * Creates a new user account
 * 
 * @param userData - User creation request data
 * @returns Promise resolving to API response containing created user data
 */
export async function createUser(userData: UserCreateRequest): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}`);
  return await apiClient.request({
    url,
    method: HttpMethod.POST,
    data: userData
  });
}

/**
 * Updates a user's profile information
 * 
 * @param userId - ID of the user to update
 * @param profileData - Profile update request data
 * @returns Promise resolving to API response containing updated user data
 */
export async function updateUserProfile(
  userId: string, 
  profileData: UserProfileUpdateRequest
): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/${userId}/profile`);
  return await apiClient.request({
    url,
    method: HttpMethod.PUT,
    data: profileData
  });
}

/**
 * Updates a user's preferences settings
 * 
 * @param userId - ID of the user to update
 * @param preferencesData - Preferences update request data
 * @returns Promise resolving to API response containing updated user data
 */
export async function updateUserPreferences(
  userId: string,
  preferencesData: UserPreferencesUpdateRequest
): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/${userId}/preferences`);
  return await apiClient.request({
    url,
    method: HttpMethod.PATCH,
    data: preferencesData
  });
}

/**
 * Updates a user's role
 * 
 * @param userId - ID of the user to update
 * @param roleData - Role update request data
 * @returns Promise resolving to API response containing updated user data
 */
export async function updateUserRole(
  userId: string,
  roleData: UserRoleUpdateRequest
): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/${userId}/role`);
  return await apiClient.request({
    url,
    method: HttpMethod.PATCH,
    data: roleData
  });
}

/**
 * Updates a user's active status
 * 
 * @param userId - ID of the user to update
 * @param statusData - Status update request data
 * @returns Promise resolving to API response containing updated user data
 */
export async function updateUserStatus(
  userId: string,
  statusData: UserStatusUpdateRequest
): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/${userId}/status`);
  return await apiClient.request({
    url,
    method: HttpMethod.PATCH,
    data: statusData
  });
}

/**
 * Updates a user's notification preferences
 * 
 * @param userId - ID of the user to update
 * @param notificationSettings - Notification settings update request data
 * @returns Promise resolving to API response containing updated user data
 */
export async function updateUserNotificationSettings(
  userId: string,
  notificationSettings: UserNotificationSettingsUpdateRequest
): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/${userId}/notifications`);
  return await apiClient.request({
    url,
    method: HttpMethod.PATCH,
    data: notificationSettings
  });
}

/**
 * Deletes a user account
 * 
 * @param userId - ID of the user to delete
 * @returns Promise resolving to API response indicating deletion success
 */
export async function deleteUser(userId: string): Promise<ApiResponse<void>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/${userId}`);
  return await apiClient.request({
    url,
    method: HttpMethod.DELETE
  });
}

/**
 * Retrieves the current authenticated user's profile
 * 
 * @returns Promise resolving to API response containing current user data
 */
export async function getCurrentUser(): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/me`);
  return await apiClient.request({
    url,
    method: HttpMethod.GET
  });
}

/**
 * Updates the current user's profile information
 * 
 * @param profileData - Profile update request data
 * @returns Promise resolving to API response containing updated user data
 */
export async function updateCurrentUserProfile(
  profileData: UserProfileUpdateRequest
): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/me/profile`);
  return await apiClient.request({
    url,
    method: HttpMethod.PUT,
    data: profileData
  });
}

/**
 * Updates the current user's preferences settings
 * 
 * @param preferencesData - Preferences update request data
 * @returns Promise resolving to API response containing updated user data
 */
export async function updateCurrentUserPreferences(
  preferencesData: UserPreferencesUpdateRequest
): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/me/preferences`);
  return await apiClient.request({
    url,
    method: HttpMethod.PATCH,
    data: preferencesData
  });
}

/**
 * Updates the current user's notification preferences
 * 
 * @param notificationSettings - Notification settings update request data
 * @returns Promise resolving to API response containing updated user data
 */
export async function updateCurrentUserNotificationSettings(
  notificationSettings: UserNotificationSettingsUpdateRequest
): Promise<ApiResponse<User>> {
  const url = buildUrl(`${ApiEndpoints.USERS}/me/notifications`);
  return await apiClient.request({
    url,
    method: HttpMethod.PATCH,
    data: notificationSettings
  });
}