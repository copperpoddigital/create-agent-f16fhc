/**
 * data-source-api.ts
 * 
 * API client functions for data source management in the Freight Price Movement Agent.
 * Provides methods for creating, retrieving, updating, and deleting data sources,
 * as well as testing connections and managing data source operations.
 */

import { apiClient, buildUrl } from './api-client';
import { 
  ApiEndpoints, 
  ApiResponse, 
  PaginationParams, 
  FilterParams 
} from '../types/api.types';
import {
  DataSource,
  DataSourceType,
  CSVDataSourceCreate,
  DatabaseDataSourceCreate,
  APIDataSourceCreate,
  TMSDataSourceCreate,
  ERPDataSourceCreate,
  TestConnectionRequest,
  DataSourceLog
} from '../types/data-source.types';

/**
 * Retrieves a paginated list of data sources with optional filtering
 * 
 * @param pagination - Pagination parameters (page, pageSize, sortBy, sortDirection)
 * @param filters - Optional array of filter parameters for filtering results
 * @returns Promise resolving to a list of data sources
 */
export async function getDataSources(
  pagination: PaginationParams,
  filters?: FilterParams[]
): Promise<ApiResponse<DataSource[]>> {
  const url = buildUrl(ApiEndpoints.DATA_SOURCES);
  
  // Prepare query parameters including pagination and filters
  const params: Record<string, any> = {
    page: pagination.page,
    pageSize: pagination.pageSize
  };

  // Add sorting if specified
  if (pagination.sortBy) {
    params.sortBy = pagination.sortBy;
    params.sortDirection = pagination.sortDirection;
  }

  // Add filters if provided
  if (filters && filters.length > 0) {
    filters.forEach((filter, index) => {
      params[`filters[${index}][field]`] = filter.field;
      params[`filters[${index}][operator]`] = filter.operator;
      params[`filters[${index}][value]`] = filter.value;
    });
  }

  return apiClient.get(url, { params });
}

/**
 * Retrieves a single data source by its ID
 * 
 * @param id - The ID of the data source to retrieve
 * @returns Promise resolving to a single data source
 */
export async function getDataSourceById(id: string): Promise<ApiResponse<DataSource>> {
  const url = buildUrl(`${ApiEndpoints.DATA_SOURCES}/${id}`);
  return apiClient.get(url);
}

/**
 * Creates a new CSV file data source
 * 
 * @param dataSource - CSV data source creation parameters
 * @returns Promise resolving to the created data source
 */
export async function createCSVDataSource(
  dataSource: CSVDataSourceCreate
): Promise<ApiResponse<DataSource>> {
  const url = buildUrl(ApiEndpoints.DATA_SOURCES);
  
  // Create a FormData object for file upload
  const formData = new FormData();
  
  // Append the file
  formData.append('file', dataSource.file);
  
  // Append other data source properties
  formData.append('name', dataSource.name);
  if (dataSource.description !== null) {
    formData.append('description', dataSource.description);
  }
  formData.append('source_type', DataSourceType.CSV);
  formData.append('delimiter', dataSource.delimiter);
  formData.append('has_header', String(dataSource.has_header));
  formData.append('date_format', dataSource.date_format);
  
  // Append field mapping as JSON string
  formData.append('field_mapping', JSON.stringify(dataSource.field_mapping));
  
  return apiClient.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

/**
 * Creates a new database data source
 * 
 * @param dataSource - Database data source creation parameters
 * @returns Promise resolving to the created data source
 */
export async function createDatabaseDataSource(
  dataSource: DatabaseDataSourceCreate
): Promise<ApiResponse<DataSource>> {
  const url = buildUrl(ApiEndpoints.DATA_SOURCES);
  
  // Prepare the request payload
  const payload = {
    ...dataSource,
    source_type: DataSourceType.DATABASE
  };
  
  return apiClient.post(url, payload);
}

/**
 * Creates a new API data source
 * 
 * @param dataSource - API data source creation parameters
 * @returns Promise resolving to the created data source
 */
export async function createAPIDataSource(
  dataSource: APIDataSourceCreate
): Promise<ApiResponse<DataSource>> {
  const url = buildUrl(ApiEndpoints.DATA_SOURCES);
  
  // Prepare the request payload
  const payload = {
    ...dataSource,
    source_type: DataSourceType.API
  };
  
  return apiClient.post(url, payload);
}

/**
 * Creates a new TMS data source
 * 
 * @param dataSource - TMS data source creation parameters
 * @returns Promise resolving to the created data source
 */
export async function createTMSDataSource(
  dataSource: TMSDataSourceCreate
): Promise<ApiResponse<DataSource>> {
  const url = buildUrl(ApiEndpoints.DATA_SOURCES);
  
  // Prepare the request payload
  const payload = {
    ...dataSource,
    source_type: DataSourceType.TMS
  };
  
  return apiClient.post(url, payload);
}

/**
 * Creates a new ERP data source
 * 
 * @param dataSource - ERP data source creation parameters
 * @returns Promise resolving to the created data source
 */
export async function createERPDataSource(
  dataSource: ERPDataSourceCreate
): Promise<ApiResponse<DataSource>> {
  const url = buildUrl(ApiEndpoints.DATA_SOURCES);
  
  // Prepare the request payload
  const payload = {
    ...dataSource,
    source_type: DataSourceType.ERP
  };
  
  return apiClient.post(url, payload);
}

/**
 * Updates an existing data source
 * 
 * @param id - The ID of the data source to update
 * @param dataSource - Partial data source object with fields to update
 * @returns Promise resolving to the updated data source
 */
export async function updateDataSource(
  id: string,
  dataSource: Partial<DataSource>
): Promise<ApiResponse<DataSource>> {
  const url = buildUrl(`${ApiEndpoints.DATA_SOURCES}/${id}`);
  return apiClient.put(url, dataSource);
}

/**
 * Deletes a data source by its ID
 * 
 * @param id - The ID of the data source to delete
 * @returns Promise resolving to a success response
 */
export async function deleteDataSource(id: string): Promise<ApiResponse<void>> {
  const url = buildUrl(`${ApiEndpoints.DATA_SOURCES}/${id}`);
  return apiClient.delete(url);
}

/**
 * Tests the connection to a data source before creating it
 * 
 * @param request - Connection test request parameters
 * @returns Promise resolving to connection test results
 */
export async function testConnection(
  request: TestConnectionRequest
): Promise<ApiResponse<{ success: boolean; message: string }>> {
  const url = buildUrl(`${ApiEndpoints.DATA_SOURCES}/test-connection`);
  return apiClient.post(url, request);
}

/**
 * Triggers a manual synchronization of a data source
 * 
 * @param id - The ID of the data source to synchronize
 * @returns Promise resolving to a job ID for tracking the sync operation
 */
export async function syncDataSource(id: string): Promise<ApiResponse<{ jobId: string }>> {
  const url = buildUrl(`${ApiEndpoints.DATA_SOURCES}/${id}/sync`);
  return apiClient.post(url);
}

/**
 * Retrieves operation logs for a specific data source
 * 
 * @param id - The ID of the data source
 * @param pagination - Pagination parameters
 * @returns Promise resolving to a list of data source logs
 */
export async function getDataSourceLogs(
  id: string,
  pagination: PaginationParams
): Promise<ApiResponse<DataSourceLog[]>> {
  const url = buildUrl(`${ApiEndpoints.DATA_SOURCES}/${id}/logs`);
  
  const params = {
    page: pagination.page,
    pageSize: pagination.pageSize
  };
  
  if (pagination.sortBy) {
    params.sortBy = pagination.sortBy;
    params.sortDirection = pagination.sortDirection;
  }
  
  return apiClient.get(url, { params });
}

/**
 * Checks the status of a data source synchronization job
 * 
 * @param jobId - The ID of the sync job to check
 * @returns Promise resolving to the sync job status
 */
export async function getDataSourceSyncStatus(
  jobId: string
): Promise<ApiResponse<{ status: string; progress: number; message: string }>> {
  const url = buildUrl(`${ApiEndpoints.DATA_SOURCES}/sync/${jobId}/status`);
  return apiClient.get(url);
}