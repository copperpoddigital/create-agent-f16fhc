/**
 * report-api.ts
 *
 * Implements API client functions for report management in the Freight Price Movement Agent
 * web application. This file provides functions to create, retrieve, update, and delete reports,
 * as well as manage scheduled reports and report templates.
 */

import { apiClient, buildUrl } from './api-client';
import { 
  ApiResponse, 
  HttpMethod, 
  PaginationParams
} from '../types/api.types';
import { 
  Report, 
  ReportCreateParams,
  ReportUpdateParams,
  ReportSummary,
  ReportTemplate,
  ReportTemplateCreateParams,
  ScheduledReport,
  ScheduledReportCreateParams,
  ScheduledReportUpdateParams,
  ReportRunHistory,
} from '../types/report.types';
import { OutputFormat } from '../types/analysis.types';

// Base API path for reports
const REPORTS_API_PATH = '/api/v1/reports';

/**
 * Creates a new report based on analysis results
 * 
 * @param params - Report creation parameters
 * @returns Promise resolving to API response containing the created report
 */
export const createReport = async (params: ReportCreateParams): Promise<ApiResponse<Report>> => {
  const url = buildUrl(REPORTS_API_PATH);
  return apiClient.post(url, params);
};

/**
 * Retrieves a paginated list of reports
 * 
 * @param params - Pagination parameters
 * @returns Promise resolving to API response containing an array of reports
 */
export const getReports = async (params: PaginationParams): Promise<ApiResponse<Report[]>> => {
  const url = buildUrl(REPORTS_API_PATH);
  return apiClient.get(url, { params });
};

/**
 * Retrieves a specific report by ID
 * 
 * @param id - Report ID
 * @returns Promise resolving to API response containing the requested report
 */
export const getReport = async (id: string): Promise<ApiResponse<Report>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/${id}`);
  return apiClient.get(url);
};

/**
 * Updates an existing report
 * 
 * @param id - Report ID
 * @param params - Updated report parameters
 * @returns Promise resolving to API response containing the updated report
 */
export const updateReport = async (id: string, params: ReportUpdateParams): Promise<ApiResponse<Report>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/${id}`);
  return apiClient.put(url, params);
};

/**
 * Deletes a report by ID
 * 
 * @param id - Report ID
 * @returns Promise resolving to API response indicating success or failure
 */
export const deleteReport = async (id: string): Promise<ApiResponse<void>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/${id}`);
  return apiClient.delete(url);
};

/**
 * Executes a report and returns the results
 * 
 * @param id - Report ID
 * @returns Promise resolving to API response containing the report output as a Blob
 */
export const runReport = async (id: string): Promise<ApiResponse<Blob>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/${id}/run`);
  return apiClient.post(url, null, { 
    responseType: 'blob' 
  });
};

/**
 * Retrieves recent reports for dashboard display
 * 
 * @param limit - Maximum number of reports to retrieve
 * @returns Promise resolving to API response containing an array of report summaries
 */
export const getRecentReports = async (limit: number): Promise<ApiResponse<ReportSummary[]>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/recent`);
  return apiClient.get(url, { params: { limit } });
};

/**
 * Creates a new report template
 * 
 * @param params - Template creation parameters
 * @returns Promise resolving to API response containing the created report template
 */
export const createReportTemplate = async (params: ReportTemplateCreateParams): Promise<ApiResponse<ReportTemplate>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/templates`);
  return apiClient.post(url, params);
};

/**
 * Retrieves a paginated list of report templates
 * 
 * @param params - Pagination parameters
 * @returns Promise resolving to API response containing an array of report templates
 */
export const getReportTemplates = async (params: PaginationParams): Promise<ApiResponse<ReportTemplate[]>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/templates`);
  return apiClient.get(url, { params });
};

/**
 * Retrieves a specific report template by ID
 * 
 * @param id - Template ID
 * @returns Promise resolving to API response containing the requested report template
 */
export const getReportTemplate = async (id: string): Promise<ApiResponse<ReportTemplate>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/templates/${id}`);
  return apiClient.get(url);
};

/**
 * Updates an existing report template
 * 
 * @param id - Template ID
 * @param params - Updated template parameters
 * @returns Promise resolving to API response containing the updated report template
 */
export const updateReportTemplate = async (id: string, params: Partial<ReportTemplateCreateParams>): Promise<ApiResponse<ReportTemplate>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/templates/${id}`);
  return apiClient.put(url, params);
};

/**
 * Deletes a report template by ID
 * 
 * @param id - Template ID
 * @returns Promise resolving to API response indicating success or failure
 */
export const deleteReportTemplate = async (id: string): Promise<ApiResponse<void>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/templates/${id}`);
  return apiClient.delete(url);
};

/**
 * Creates a new scheduled report
 * 
 * @param params - Scheduled report creation parameters
 * @returns Promise resolving to API response containing the created scheduled report
 */
export const createScheduledReport = async (params: ScheduledReportCreateParams): Promise<ApiResponse<ScheduledReport>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/scheduled`);
  return apiClient.post(url, params);
};

/**
 * Retrieves a paginated list of scheduled reports
 * 
 * @param params - Pagination parameters
 * @returns Promise resolving to API response containing an array of scheduled reports
 */
export const getScheduledReports = async (params: PaginationParams): Promise<ApiResponse<ScheduledReport[]>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/scheduled`);
  return apiClient.get(url, { params });
};

/**
 * Retrieves a specific scheduled report by ID
 * 
 * @param id - Scheduled report ID
 * @returns Promise resolving to API response containing the requested scheduled report
 */
export const getScheduledReport = async (id: string): Promise<ApiResponse<ScheduledReport>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/scheduled/${id}`);
  return apiClient.get(url);
};

/**
 * Updates an existing scheduled report
 * 
 * @param id - Scheduled report ID
 * @param params - Updated scheduled report parameters
 * @returns Promise resolving to API response containing the updated scheduled report
 */
export const updateScheduledReport = async (id: string, params: ScheduledReportUpdateParams): Promise<ApiResponse<ScheduledReport>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/scheduled/${id}`);
  return apiClient.put(url, params);
};

/**
 * Deletes a scheduled report by ID
 * 
 * @param id - Scheduled report ID
 * @returns Promise resolving to API response indicating success or failure
 */
export const deleteScheduledReport = async (id: string): Promise<ApiResponse<void>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/scheduled/${id}`);
  return apiClient.delete(url);
};

/**
 * Retrieves the execution history for a specific report
 * 
 * @param reportId - Report ID
 * @param params - Pagination parameters
 * @returns Promise resolving to API response containing an array of report run history entries
 */
export const getReportRunHistory = async (reportId: string, params: PaginationParams): Promise<ApiResponse<ReportRunHistory[]>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/${reportId}/history`);
  return apiClient.get(url, { params });
};

/**
 * Downloads a previously generated report output
 * 
 * @param reportRunId - Report run ID
 * @returns Promise resolving to API response containing the report output as a Blob
 */
export const downloadReportOutput = async (reportRunId: string): Promise<ApiResponse<Blob>> => {
  const url = buildUrl(`${REPORTS_API_PATH}/output/${reportRunId}`);
  return apiClient.get(url, { 
    responseType: 'blob' 
  });
};