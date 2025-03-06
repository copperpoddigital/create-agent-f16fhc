/**
 * analysis-api.ts
 *
 * Implements API client functions for freight price movement analysis operations.
 * This file provides functions to create, retrieve, update, and delete time periods
 * and analysis requests, as well as run analyses and export results.
 */

import { apiClient, buildUrl } from './api-client';
import { 
  ApiResponse, 
  HttpMethod, 
  PaginationParams 
} from '../types/api.types';
import {
  TimePeriod,
  TimePeriodCreateParams,
  AnalysisRequest,
  AnalysisRequestCreateParams,
  AnalysisResult,
  AnalysisResultSummary,
  AnalysisExportOptions,
  OutputFormat
} from '../types/analysis.types';

// Base path for analysis API endpoints
const ANALYSIS_API_PATH = '/api/v1/analysis';

/**
 * Creates a new time period for analysis
 * 
 * @param params - Time period parameters
 * @returns Promise resolving to API response containing the created time period
 */
export async function createTimePeriod(params: TimePeriodCreateParams): Promise<ApiResponse<TimePeriod>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/time-periods`);
  return apiClient.request({
    url,
    method: HttpMethod.POST,
    data: params
  });
}

/**
 * Retrieves a paginated list of time periods
 * 
 * @param params - Pagination parameters
 * @returns Promise resolving to API response containing an array of time periods
 */
export async function getTimePeriods(params: PaginationParams): Promise<ApiResponse<TimePeriod[]>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/time-periods`);
  return apiClient.request({
    url,
    method: HttpMethod.GET,
    params
  });
}

/**
 * Retrieves a specific time period by ID
 * 
 * @param id - Time period ID
 * @returns Promise resolving to API response containing the requested time period
 */
export async function getTimePeriod(id: string): Promise<ApiResponse<TimePeriod>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/time-periods/${id}`);
  return apiClient.request({
    url,
    method: HttpMethod.GET
  });
}

/**
 * Updates an existing time period
 * 
 * @param id - Time period ID
 * @param params - Updated time period parameters
 * @returns Promise resolving to API response containing the updated time period
 */
export async function updateTimePeriod(
  id: string, 
  params: Partial<TimePeriodCreateParams>
): Promise<ApiResponse<TimePeriod>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/time-periods/${id}`);
  return apiClient.request({
    url,
    method: HttpMethod.PUT,
    data: params
  });
}

/**
 * Deletes a time period by ID
 * 
 * @param id - Time period ID
 * @returns Promise resolving to API response indicating success or failure
 */
export async function deleteTimePeriod(id: string): Promise<ApiResponse<void>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/time-periods/${id}`);
  return apiClient.request({
    url,
    method: HttpMethod.DELETE
  });
}

/**
 * Creates a new analysis request
 * 
 * @param params - Analysis request parameters
 * @returns Promise resolving to API response containing the created analysis request
 */
export async function createAnalysisRequest(
  params: AnalysisRequestCreateParams
): Promise<ApiResponse<AnalysisRequest>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/requests`);
  return apiClient.request({
    url,
    method: HttpMethod.POST,
    data: params
  });
}

/**
 * Retrieves a paginated list of analysis requests
 * 
 * @param params - Pagination parameters
 * @returns Promise resolving to API response containing an array of analysis requests
 */
export async function getAnalysisRequests(params: PaginationParams): Promise<ApiResponse<AnalysisRequest[]>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/requests`);
  return apiClient.request({
    url,
    method: HttpMethod.GET,
    params
  });
}

/**
 * Retrieves a specific analysis request by ID
 * 
 * @param id - Analysis request ID
 * @returns Promise resolving to API response containing the requested analysis request
 */
export async function getAnalysisRequest(id: string): Promise<ApiResponse<AnalysisRequest>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/requests/${id}`);
  return apiClient.request({
    url,
    method: HttpMethod.GET
  });
}

/**
 * Updates an existing analysis request
 * 
 * @param id - Analysis request ID
 * @param params - Updated analysis request parameters
 * @returns Promise resolving to API response containing the updated analysis request
 */
export async function updateAnalysisRequest(
  id: string, 
  params: Partial<AnalysisRequestCreateParams>
): Promise<ApiResponse<AnalysisRequest>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/requests/${id}`);
  return apiClient.request({
    url,
    method: HttpMethod.PUT,
    data: params
  });
}

/**
 * Deletes an analysis request by ID
 * 
 * @param id - Analysis request ID
 * @returns Promise resolving to API response indicating success or failure
 */
export async function deleteAnalysisRequest(id: string): Promise<ApiResponse<void>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/requests/${id}`);
  return apiClient.request({
    url,
    method: HttpMethod.DELETE
  });
}

/**
 * Executes an analysis and returns the results
 * 
 * @param id - Analysis request ID
 * @returns Promise resolving to API response containing the analysis results
 */
export async function runAnalysis(id: string): Promise<ApiResponse<AnalysisResult>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/requests/${id}/run`);
  return apiClient.request({
    url,
    method: HttpMethod.POST
  });
}

/**
 * Retrieves a specific analysis result by ID
 * 
 * @param id - Analysis result ID
 * @returns Promise resolving to API response containing the requested analysis result
 */
export async function getAnalysisResult(id: string): Promise<ApiResponse<AnalysisResult>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/results/${id}`);
  return apiClient.request({
    url,
    method: HttpMethod.GET
  });
}

/**
 * Retrieves analysis results for a specific analysis request
 * 
 * @param analysisId - Analysis request ID
 * @param params - Pagination parameters
 * @returns Promise resolving to API response containing an array of analysis results
 */
export async function getAnalysisResults(
  analysisId: string, 
  params: PaginationParams
): Promise<ApiResponse<AnalysisResult[]>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/requests/${analysisId}/results`);
  return apiClient.request({
    url,
    method: HttpMethod.GET,
    params
  });
}

/**
 * Retrieves recent analysis results for dashboard display
 * 
 * @param limit - Maximum number of results to return
 * @returns Promise resolving to API response containing an array of analysis result summaries
 */
export async function getRecentAnalysisResults(limit: number): Promise<ApiResponse<AnalysisResultSummary[]>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/results/recent`);
  return apiClient.request({
    url,
    method: HttpMethod.GET,
    params: { limit }
  });
}

/**
 * Exports an analysis result in the specified format
 * 
 * @param id - Analysis result ID
 * @param options - Export options including format, content to include, and filename
 * @returns Promise resolving to API response containing the exported data as a Blob
 */
export async function exportAnalysisResult(
  id: string, 
  options: AnalysisExportOptions
): Promise<ApiResponse<Blob>> {
  const url = buildUrl(`${ANALYSIS_API_PATH}/results/${id}/export`);
  return apiClient.request({
    url,
    method: HttpMethod.POST,
    data: options,
    responseType: 'blob'
  });
}