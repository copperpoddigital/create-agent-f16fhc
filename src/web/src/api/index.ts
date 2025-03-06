/**
 * API Module
 * 
 * Centralizes and exports all API client functions for the Freight Price Movement Agent
 * web application. This file serves as the main entry point for API interactions,
 * aggregating specialized API modules for different functional areas.
 * 
 * @module api
 */

/**
 * Core API client and utilities
 */
export {
  apiClient,
  setAuthorizationHeader,
  clearAuthorizationHeader,
  buildUrl
} from './api-client';

/**
 * Authentication API functions
 */
export {
  login,
  logout,
  refreshToken,
  getUserInfo,
  changePassword,
  resetPassword,
  confirmPasswordReset,
  validateToken
} from './auth-api';

/**
 * Analysis API functions
 */
export {
  // Time period functions
  createTimePeriod,
  getTimePeriods,
  getTimePeriod,
  updateTimePeriod,
  deleteTimePeriod,
  
  // Analysis request functions
  createAnalysisRequest,
  getAnalysisRequests,
  getAnalysisRequest,
  updateAnalysisRequest,
  deleteAnalysisRequest,
  
  // Analysis execution and results
  runAnalysis,
  getAnalysisResult,
  getAnalysisResults,
  getRecentAnalysisResults,
  exportAnalysisResult
} from './analysis-api';

/**
 * Data Source API functions
 */
export {
  // Data source retrieval
  getDataSources,
  getDataSourceById,
  
  // Data source creation by type
  createCSVDataSource,
  createDatabaseDataSource,
  createAPIDataSource,
  createTMSDataSource,
  createERPDataSource,
  
  // Data source management
  updateDataSource,
  deleteDataSource,
  testConnection,
  syncDataSource,
  
  // Data source logs and status
  getDataSourceLogs,
  getDataSourceSyncStatus
} from './data-source-api';

/**
 * Report API functions
 */
export {
  // Report CRUD operations
  createReport,
  getReports,
  getReport,
  updateReport,
  deleteReport,
  runReport,
  getRecentReports,
  
  // Report templates
  createReportTemplate,
  getReportTemplates,
  getReportTemplate,
  updateReportTemplate,
  deleteReportTemplate,
  
  // Scheduled reports
  createScheduledReport,
  getScheduledReports,
  getScheduledReport,
  updateScheduledReport,
  deleteScheduledReport,
  
  // Report history and outputs
  getReportRunHistory,
  downloadReportOutput
} from './report-api';

/**
 * User API functions
 */
export {
  // User management
  getUsers,
  getUserById,
  createUser,
  updateUserProfile,
  updateUserPreferences,
  updateUserRole,
  updateUserStatus,
  updateUserNotificationSettings,
  deleteUser,
  
  // Current user operations
  getCurrentUser,
  updateCurrentUserProfile,
  updateCurrentUserPreferences,
  updateCurrentUserNotificationSettings
} from './user-api';