/**
 * storage-utils.ts
 * 
 * Utility functions for browser storage operations in the Freight Price Movement Agent
 * web application. Provides type-safe wrappers around localStorage and sessionStorage
 * with JSON serialization/deserialization support, error handling, and specialized
 * functions for common storage operations.
 */

import { STORAGE_KEYS } from '../config/constants';
import { UserPreferences } from '../types/user.types';
import { AnalysisResult } from '../types/analysis.types';

/**
 * Interface for storage objects with optional expiration
 */
interface StorageObject<T> {
  value: T;
  expiry?: number; // Timestamp in milliseconds
}

/**
 * Checks if a specific storage type is available in the browser
 * 
 * @param type - Storage type ('localStorage' or 'sessionStorage')
 * @returns True if storage is available, false otherwise
 */
export function isStorageAvailable(type: string): boolean {
  try {
    const storage = window[type as keyof Window] as Storage;
    const testKey = `__storage_test__${Math.random()}`;
    storage.setItem(testKey, testKey);
    const result = storage.getItem(testKey) === testKey;
    storage.removeItem(testKey);
    return result;
  } catch (e) {
    // Storage might be unavailable or disabled (e.g., private browsing mode)
    return false;
  }
}

/**
 * Stores an item in localStorage with JSON serialization
 * 
 * @param key - Storage key
 * @param value - Value to store
 * @param expirationInMinutes - Optional expiration time in minutes
 * @returns True if storage succeeded, false otherwise
 */
export function setLocalStorageItem<T>(
  key: string,
  value: T,
  expirationInMinutes?: number
): boolean {
  if (!isStorageAvailable('localStorage')) {
    return false;
  }

  try {
    const storageObj: StorageObject<T> = {
      value: value
    };

    // Set expiration if provided
    if (expirationInMinutes) {
      const now = new Date();
      storageObj.expiry = now.getTime() + expirationInMinutes * 60 * 1000;
    }

    localStorage.setItem(key, JSON.stringify(storageObj));
    return true;
  } catch (error) {
    console.error('Error storing item in localStorage:', error);
    return false;
  }
}

/**
 * Retrieves an item from localStorage with JSON parsing and expiration check
 * 
 * @param key - Storage key
 * @param defaultValue - Default value if key not found or expired
 * @returns The stored value or defaultValue if not found or expired
 */
export function getLocalStorageItem<T>(key: string, defaultValue: T | null = null): T | null {
  if (!isStorageAvailable('localStorage')) {
    return defaultValue;
  }

  try {
    const itemStr = localStorage.getItem(key);
    if (!itemStr) {
      return defaultValue;
    }

    const storageObj: StorageObject<T> = JSON.parse(itemStr);
    
    // Check if item has expired
    if (storageObj.expiry && new Date().getTime() > storageObj.expiry) {
      removeLocalStorageItem(key);
      return defaultValue;
    }

    return storageObj.value;
  } catch (error) {
    console.error('Error retrieving item from localStorage:', error);
    return defaultValue;
  }
}

/**
 * Removes an item from localStorage
 * 
 * @param key - Storage key
 * @returns True if removal succeeded, false otherwise
 */
export function removeLocalStorageItem(key: string): boolean {
  if (!isStorageAvailable('localStorage')) {
    return false;
  }

  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error('Error removing item from localStorage:', error);
    return false;
  }
}

/**
 * Clears all items from localStorage
 * 
 * @returns True if clearing succeeded, false otherwise
 */
export function clearLocalStorage(): boolean {
  if (!isStorageAvailable('localStorage')) {
    return false;
  }

  try {
    localStorage.clear();
    return true;
  } catch (error) {
    console.error('Error clearing localStorage:', error);
    return false;
  }
}

/**
 * Stores an item in sessionStorage with JSON serialization
 * 
 * @param key - Storage key
 * @param value - Value to store
 * @returns True if storage succeeded, false otherwise
 */
export function setSessionStorageItem<T>(key: string, value: T): boolean {
  if (!isStorageAvailable('sessionStorage')) {
    return false;
  }

  try {
    sessionStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error('Error storing item in sessionStorage:', error);
    return false;
  }
}

/**
 * Retrieves an item from sessionStorage with JSON parsing
 * 
 * @param key - Storage key
 * @param defaultValue - Default value if key not found
 * @returns The stored value or defaultValue if not found
 */
export function getSessionStorageItem<T>(key: string, defaultValue: T | null = null): T | null {
  if (!isStorageAvailable('sessionStorage')) {
    return defaultValue;
  }

  try {
    const itemStr = sessionStorage.getItem(key);
    if (!itemStr) {
      return defaultValue;
    }

    return JSON.parse(itemStr);
  } catch (error) {
    console.error('Error retrieving item from sessionStorage:', error);
    return defaultValue;
  }
}

/**
 * Removes an item from sessionStorage
 * 
 * @param key - Storage key
 * @returns True if removal succeeded, false otherwise
 */
export function removeSessionStorageItem(key: string): boolean {
  if (!isStorageAvailable('sessionStorage')) {
    return false;
  }

  try {
    sessionStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error('Error removing item from sessionStorage:', error);
    return false;
  }
}

/**
 * Clears all items from sessionStorage
 * 
 * @returns True if clearing succeeded, false otherwise
 */
export function clearSessionStorage(): boolean {
  if (!isStorageAvailable('sessionStorage')) {
    return false;
  }

  try {
    sessionStorage.clear();
    return true;
  } catch (error) {
    console.error('Error clearing sessionStorage:', error);
    return false;
  }
}

/**
 * Retrieves the authentication token from storage
 * 
 * @returns The authentication token or null if not found
 */
export function getAuthToken(): string | null {
  return getLocalStorageItem<string>(STORAGE_KEYS.AUTH_TOKEN);
}

/**
 * Stores the authentication token in storage with optional expiration
 * 
 * @param token - Authentication token
 * @param expirationInMinutes - Optional expiration time in minutes
 * @returns True if storage succeeded, false otherwise
 */
export function setAuthToken(token: string, expirationInMinutes?: number): boolean {
  return setLocalStorageItem<string>(STORAGE_KEYS.AUTH_TOKEN, token, expirationInMinutes);
}

/**
 * Removes the authentication token from storage
 * 
 * @returns True if removal succeeded, false otherwise
 */
export function removeAuthToken(): boolean {
  return removeLocalStorageItem(STORAGE_KEYS.AUTH_TOKEN);
}

/**
 * Retrieves user preferences from storage
 * 
 * @returns The user preferences or null if not found
 */
export function getUserPreferences(): UserPreferences | null {
  return getLocalStorageItem<UserPreferences>(STORAGE_KEYS.USER_PREFERENCES);
}

/**
 * Stores user preferences in storage
 * 
 * @param preferences - User preferences object
 * @returns True if storage succeeded, false otherwise
 */
export function setUserPreferences(preferences: UserPreferences): boolean {
  return setLocalStorageItem<UserPreferences>(STORAGE_KEYS.USER_PREFERENCES, preferences);
}

/**
 * Retrieves the last analysis result from storage
 * 
 * @returns The last analysis result or null if not found
 */
export function getLastAnalysis(): AnalysisResult | null {
  return getLocalStorageItem<AnalysisResult>('fpma_last_analysis');
}

/**
 * Stores the last analysis result in storage
 * 
 * @param analysisResult - Analysis result object
 * @returns True if storage succeeded, false otherwise
 */
export function setLastAnalysis(analysisResult: AnalysisResult): boolean {
  return setLocalStorageItem<AnalysisResult>('fpma_last_analysis', analysisResult);
}