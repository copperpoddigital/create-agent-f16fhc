/**
 * api.types.ts
 *
 * This file defines TypeScript interfaces and types for API communication
 * in the Freight Price Movement Agent web application. It provides common
 * type definitions for API requests, responses, error handling, and HTTP
 * methods to ensure type safety and consistency across all API interactions.
 *
 * These types implement the specifications defined in:
 * - Technical Specifications/6.3 INTEGRATION ARCHITECTURE/6.3.1 API DESIGN
 * - Technical Specifications/6.3 INTEGRATION ARCHITECTURE/6.3.2 MESSAGE PROCESSING
 */

/**
 * HTTP methods supported by the API
 */
export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  PATCH = 'PATCH',
  DELETE = 'DELETE'
}

/**
 * API endpoint categories for the Freight Price Movement Agent
 */
export enum ApiEndpoints {
  AUTH = '/api/v1/auth',
  DATA_SOURCES = '/api/v1/data-sources',
  ANALYSIS = '/api/v1/analysis',
  REPORTS = '/api/v1/reports',
  USERS = '/api/v1/users'
}

/**
 * Generic interface for API responses with consistent structure
 */
export interface ApiResponse {
  success: boolean;
  data: any;
  error: ApiError | null;
  meta: ApiResponseMeta | null;
}

/**
 * Interface for standardized API error information
 */
export interface ApiError {
  code: string | number;
  message: string;
  details: Record<string, any> | null;
  path: string | null;
}

/**
 * Interface for metadata included in API responses
 */
export interface ApiResponseMeta {
  pagination: PaginationMeta | null;
  timestamp: string;
  requestId: string | null;
  processingTime: number | null;
}

/**
 * Interface for pagination metadata in API responses
 */
export interface PaginationMeta {
  page: number;
  pageSize: number;
  totalPages: number;
  totalItems: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

/**
 * Interface for pagination parameters in API requests
 */
export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy: string | null;
  sortDirection: SortDirection | null;
}

/**
 * Sort direction options for paginated requests
 */
export enum SortDirection {
  ASC = 'asc',
  DESC = 'desc'
}

/**
 * Interface for filter parameters in API requests
 */
export interface FilterParams {
  field: string;
  operator: FilterOperator;
  value: any;
}

/**
 * Filter operators for query parameters
 */
export enum FilterOperator {
  EQUALS = 'eq',
  NOT_EQUALS = 'neq',
  GREATER_THAN = 'gt',
  LESS_THAN = 'lt',
  CONTAINS = 'contains',
  IN = 'in',
  BETWEEN = 'between'
}

/**
 * Interface for API request configuration options
 */
export interface ApiRequestConfig {
  url: string;
  method: HttpMethod;
  data: any | null;
  params: Record<string, any> | null;
  headers: Record<string, string> | null;
  timeout: number | null;
  withCredentials: boolean;
}

/**
 * Enumeration of API error types for error categorization
 */
export enum ApiErrorType {
  VALIDATION = 'validation',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  NOT_FOUND = 'not_found',
  CONFLICT = 'conflict',
  SERVER_ERROR = 'server_error',
  NETWORK_ERROR = 'network_error',
  TIMEOUT = 'timeout',
  UNKNOWN = 'unknown'
}

/**
 * Interface for field-level validation errors
 */
export interface ValidationError {
  field: string;
  message: string;
  code: string | null;
}

/**
 * Interface for API health/status information
 */
export interface ApiStatus {
  status: string;
  version: string;
  uptime: number;
  timestamp: string;
}

/**
 * Interface for API version information
 */
export interface ApiVersionInfo {
  version: string;
  releaseDate: string;
  deprecated: boolean;
  endOfLife: string | null;
}

/**
 * Interface for API feature flag configuration
 */
export interface ApiFeatureFlag {
  name: string;
  enabled: boolean;
  description: string | null;
}

/**
 * Interface for API error responses with consistent structure
 */
export interface ApiErrorResponse {
  success: boolean;
  error: ApiError;
  meta: ApiResponseMeta | null;
}

/**
 * Interface for API success responses with consistent structure
 */
export interface ApiSuccessResponse {
  success: boolean;
  data: any;
  meta: ApiResponseMeta | null;
}

/**
 * Interface for paginated API responses
 */
export interface ApiPaginatedResponse {
  success: boolean;
  data: any[];
  meta: ApiResponseMeta;
}

/**
 * Interface for configuring API request options
 */
export interface ApiRequestOptions {
  retryAttempts: number | null;
  retryDelay: number | null;
  timeout: number | null;
  withCredentials: boolean;
  responseType: string | null;
}

/**
 * Interface for API hook state management
 */
export interface ApiHookState {
  data: any | null;
  error: ApiError | null;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
}

/**
 * Interface for API hook actions
 */
export interface ApiHookActions {
  execute: (...args: any[]) => Promise<any>;
  reset: () => void;
  cancel: () => void;
}

/**
 * Interface for API hook result combining state and actions
 */
export interface ApiHookResult {
  state: ApiHookState;
  actions: ApiHookActions;
}