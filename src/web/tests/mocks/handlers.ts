import { rest } from 'msw'; // v1.0.0
import { 
  mockUsers, 
  mockAuthTokens, 
  mockDataSources, 
  mockTimePeriods, 
  mockAnalysisResults, 
  mockTimeSeriesData, 
  mockReports 
} from './data';
import { API_CONFIG } from '../../src/config/api-config';

// Base API path for all endpoints
const API_BASE_PATH = `${API_CONFIG.BASE_URL}${API_CONFIG.API_PATH}/${API_CONFIG.VERSION}`;

/**
 * Creates a standardized success response object for API handlers
 * @param data Any data to include in the response
 * @returns Standardized success response with data and metadata
 */
const createSuccessResponse = (data: any) => {
  return {
    status: 'success',
    data,
    metadata: {
      timestamp: new Date().toISOString(),
      request_id: `req_${Math.random().toString(36).substring(2, 15)}`
    }
  };
};

/**
 * Creates a standardized error response object for API handlers
 * @param message Error message
 * @param status HTTP status code
 * @param code Error code for client reference
 * @returns Standardized error response with message and error details
 */
const createErrorResponse = (message: string, status: number, code: string) => {
  return {
    status: 'error',
    error: {
      message,
      status,
      code
    },
    metadata: {
      timestamp: new Date().toISOString(),
      request_id: `req_${Math.random().toString(36).substring(2, 15)}`
    }
  };
};

// Authentication Handlers
const authHandlers = [
  // Login handler
  rest.post(`${API_BASE_PATH}/auth/login`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ tokens: mockAuthTokens }))
    );
  }),

  // Logout handler
  rest.post(`${API_BASE_PATH}/auth/logout`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Logout successful' }))
    );
  }),

  // Token refresh handler
  rest.post(`${API_BASE_PATH}/auth/refresh`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ tokens: mockAuthTokens }))
    );
  }),

  // Get current user info
  rest.get(`${API_BASE_PATH}/auth/user`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user: mockUsers[0] }))
    );
  }),

  // Change password handler
  rest.post(`${API_BASE_PATH}/auth/password/change`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Password changed successfully' }))
    );
  }),

  // Request password reset handler
  rest.post(`${API_BASE_PATH}/auth/password/reset`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Password reset email sent' }))
    );
  }),

  // Confirm password reset handler
  rest.post(`${API_BASE_PATH}/auth/password/reset/confirm`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Password reset successfully' }))
    );
  }),

  // Validate token handler
  rest.get(`${API_BASE_PATH}/auth/validate`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ valid: true }))
    );
  }),
];

// User Management Handlers
const userHandlers = [
  // Get all users
  rest.get(`${API_BASE_PATH}/users`, (req, res, ctx) => {
    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        users: mockUsers,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: mockUsers.length,
          total_pages: Math.ceil(mockUsers.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Get user by ID
  rest.get(`${API_BASE_PATH}/users/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const user = mockUsers.find(user => user.id === id);

    if (!user) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('User not found', 404, 'USER_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user }))
    );
  }),

  // Create user
  rest.post(`${API_BASE_PATH}/users`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json(createSuccessResponse({ user: mockUsers[0] }))
    );
  }),

  // Update user profile
  rest.put(`${API_BASE_PATH}/users/:id/profile`, (req, res, ctx) => {
    const { id } = req.params;
    const user = mockUsers.find(user => user.id === id);

    if (!user) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('User not found', 404, 'USER_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user }))
    );
  }),

  // Update user preferences
  rest.patch(`${API_BASE_PATH}/users/:id/preferences`, (req, res, ctx) => {
    const { id } = req.params;
    const user = mockUsers.find(user => user.id === id);

    if (!user) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('User not found', 404, 'USER_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user }))
    );
  }),

  // Update user role
  rest.patch(`${API_BASE_PATH}/users/:id/role`, (req, res, ctx) => {
    const { id } = req.params;
    const user = mockUsers.find(user => user.id === id);

    if (!user) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('User not found', 404, 'USER_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user }))
    );
  }),

  // Update user status
  rest.patch(`${API_BASE_PATH}/users/:id/status`, (req, res, ctx) => {
    const { id } = req.params;
    const user = mockUsers.find(user => user.id === id);

    if (!user) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('User not found', 404, 'USER_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user }))
    );
  }),

  // Update user notification settings
  rest.patch(`${API_BASE_PATH}/users/:id/notifications`, (req, res, ctx) => {
    const { id } = req.params;
    const user = mockUsers.find(user => user.id === id);

    if (!user) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('User not found', 404, 'USER_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user }))
    );
  }),

  // Delete user
  rest.delete(`${API_BASE_PATH}/users/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const user = mockUsers.find(user => user.id === id);

    if (!user) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('User not found', 404, 'USER_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'User deleted successfully' }))
    );
  }),

  // Get current user profile
  rest.get(`${API_BASE_PATH}/users/current`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user: mockUsers[0] }))
    );
  }),

  // Update current user profile
  rest.put(`${API_BASE_PATH}/users/current/profile`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user: mockUsers[0] }))
    );
  }),

  // Update current user preferences
  rest.patch(`${API_BASE_PATH}/users/current/preferences`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user: mockUsers[0] }))
    );
  }),

  // Update current user notification settings
  rest.patch(`${API_BASE_PATH}/users/current/notifications`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ user: mockUsers[0] }))
    );
  }),
];

// Data Source Handlers
const dataSourceHandlers = [
  // Get all data sources
  rest.get(`${API_BASE_PATH}/data-sources`, (req, res, ctx) => {
    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        data_sources: mockDataSources,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: mockDataSources.length,
          total_pages: Math.ceil(mockDataSources.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Get data source by ID
  rest.get(`${API_BASE_PATH}/data-sources/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const dataSource = mockDataSources.find(ds => ds.id === id);

    if (!dataSource) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Data source not found', 404, 'DATA_SOURCE_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ data_source: dataSource }))
    );
  }),

  // Create data source
  rest.post(`${API_BASE_PATH}/data-sources`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json(createSuccessResponse({ data_source: mockDataSources[0] }))
    );
  }),

  // Update data source
  rest.put(`${API_BASE_PATH}/data-sources/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const dataSource = mockDataSources.find(ds => ds.id === id);

    if (!dataSource) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Data source not found', 404, 'DATA_SOURCE_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ data_source: dataSource }))
    );
  }),

  // Delete data source
  rest.delete(`${API_BASE_PATH}/data-sources/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const dataSource = mockDataSources.find(ds => ds.id === id);

    if (!dataSource) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Data source not found', 404, 'DATA_SOURCE_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Data source deleted successfully' }))
    );
  }),

  // Test data source connection
  rest.post(`${API_BASE_PATH}/data-sources/test-connection`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ 
        connection_successful: true,
        message: 'Connection test successful' 
      }))
    );
  }),

  // Sync data source
  rest.post(`${API_BASE_PATH}/data-sources/:id/sync`, (req, res, ctx) => {
    const { id } = req.params;
    const dataSource = mockDataSources.find(ds => ds.id === id);

    if (!dataSource) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Data source not found', 404, 'DATA_SOURCE_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ 
        job_id: 'sync-job-123',
        message: 'Sync job started successfully' 
      }))
    );
  }),

  // Get data source logs
  rest.get(`${API_BASE_PATH}/data-sources/:id/logs`, (req, res, ctx) => {
    const { id } = req.params;
    const dataSource = mockDataSources.find(ds => ds.id === id);

    if (!dataSource) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Data source not found', 404, 'DATA_SOURCE_NOT_FOUND'))
      );
    }

    // Generate mock logs
    const mockLogs = [
      {
        id: 'log-1',
        data_source_id: id,
        operation: 'sync',
        status: 'success',
        message: 'Data synchronization completed successfully',
        details: { records_processed: 1500 },
        records_processed: 1500,
        records_succeeded: 1480,
        records_failed: 20,
        started_at: '2023-06-15T08:00:00Z',
        completed_at: '2023-06-15T08:30:00Z',
        duration_seconds: 1800
      },
      {
        id: 'log-2',
        data_source_id: id,
        operation: 'sync',
        status: 'success',
        message: 'Data synchronization completed successfully',
        details: { records_processed: 1200 },
        records_processed: 1200,
        records_succeeded: 1200,
        records_failed: 0,
        started_at: '2023-06-14T08:00:00Z',
        completed_at: '2023-06-14T08:25:00Z',
        duration_seconds: 1500
      }
    ];

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        logs: mockLogs,
        pagination: {
          page: 1,
          page_size: 10,
          total_items: mockLogs.length,
          total_pages: 1
        }
      }))
    );
  }),

  // Get job status
  rest.get(`${API_BASE_PATH}/data-sources/jobs/:jobId`, (req, res, ctx) => {
    const { jobId } = req.params;

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        job_id: jobId,
        status: 'completed',
        progress: 100,
        message: 'Job completed successfully',
        started_at: '2023-06-15T08:00:00Z',
        completed_at: '2023-06-15T08:30:00Z',
        duration_seconds: 1800
      }))
    );
  }),
];

// Analysis Handlers
const analysisHandlers = [
  // Create time period
  rest.post(`${API_BASE_PATH}/analysis/time-periods`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json(createSuccessResponse({ time_period: mockTimePeriods[0] }))
    );
  }),

  // Get all time periods
  rest.get(`${API_BASE_PATH}/analysis/time-periods`, (req, res, ctx) => {
    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        time_periods: mockTimePeriods,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: mockTimePeriods.length,
          total_pages: Math.ceil(mockTimePeriods.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Get time period by ID
  rest.get(`${API_BASE_PATH}/analysis/time-periods/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const timePeriod = mockTimePeriods.find(tp => tp.id === id);

    if (!timePeriod) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Time period not found', 404, 'TIME_PERIOD_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ time_period: timePeriod }))
    );
  }),

  // Update time period
  rest.put(`${API_BASE_PATH}/analysis/time-periods/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const timePeriod = mockTimePeriods.find(tp => tp.id === id);

    if (!timePeriod) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Time period not found', 404, 'TIME_PERIOD_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ time_period: timePeriod }))
    );
  }),

  // Delete time period
  rest.delete(`${API_BASE_PATH}/analysis/time-periods/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const timePeriod = mockTimePeriods.find(tp => tp.id === id);

    if (!timePeriod) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Time period not found', 404, 'TIME_PERIOD_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Time period deleted successfully' }))
    );
  }),

  // Create analysis request
  rest.post(`${API_BASE_PATH}/analysis/requests`, (req, res, ctx) => {
    // Mock analysis request
    const mockAnalysisRequest = {
      id: 'a-1',
      name: 'Q1 Ocean Freight Analysis',
      description: 'Analysis of ocean freight rates for Q1 2023',
      time_period_id: mockTimePeriods[0].id,
      time_period: mockTimePeriods[0],
      data_source_ids: [mockDataSources[0].id],
      filters: [
        { field: 'origin', operator: 'equals', value: 'Shanghai' },
        { field: 'destination', operator: 'equals', value: 'Rotterdam' }
      ],
      options: {
        calculate_absolute_change: true,
        calculate_percentage_change: true,
        identify_trend_direction: true,
        compare_to_baseline: false,
        baseline_period_id: null,
        output_format: 'json',
        include_visualization: true
      },
      status: 'completed',
      created_by: mockUsers[0].id,
      created_at: '2023-04-01T10:00:00Z',
      updated_at: '2023-04-01T10:15:00Z',
      last_run_at: '2023-04-01T10:15:00Z'
    };

    return res(
      ctx.status(201),
      ctx.json(createSuccessResponse({ analysis_request: mockAnalysisRequest }))
    );
  }),

  // Get all analysis requests
  rest.get(`${API_BASE_PATH}/analysis/requests`, (req, res, ctx) => {
    // Mock analysis requests
    const mockAnalysisRequests = [
      {
        id: 'a-1',
        name: 'Q1 Ocean Freight Analysis',
        description: 'Analysis of ocean freight rates for Q1 2023',
        time_period_id: mockTimePeriods[0].id,
        time_period: mockTimePeriods[0],
        data_source_ids: [mockDataSources[0].id],
        filters: [
          { field: 'origin', operator: 'equals', value: 'Shanghai' },
          { field: 'destination', operator: 'equals', value: 'Rotterdam' }
        ],
        options: {
          calculate_absolute_change: true,
          calculate_percentage_change: true,
          identify_trend_direction: true,
          compare_to_baseline: false,
          baseline_period_id: null,
          output_format: 'json',
          include_visualization: true
        },
        status: 'completed',
        created_by: mockUsers[0].id,
        created_at: '2023-04-01T10:00:00Z',
        updated_at: '2023-04-01T10:15:00Z',
        last_run_at: '2023-04-01T10:15:00Z'
      },
      {
        id: 'a-2',
        name: 'Recent Air Freight Analysis',
        description: 'Analysis of air freight rates for the last 30 days',
        time_period_id: mockTimePeriods[1].id,
        time_period: mockTimePeriods[1],
        data_source_ids: [mockDataSources[2].id],
        filters: [
          { field: 'mode', operator: 'equals', value: 'Air' }
        ],
        options: {
          calculate_absolute_change: true,
          calculate_percentage_change: true,
          identify_trend_direction: true,
          compare_to_baseline: false,
          baseline_period_id: null,
          output_format: 'json',
          include_visualization: true
        },
        status: 'completed',
        created_by: mockUsers[1].id,
        created_at: '2023-06-15T09:30:00Z',
        updated_at: '2023-06-15T09:45:00Z',
        last_run_at: '2023-06-15T09:45:00Z'
      }
    ];

    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        analysis_requests: mockAnalysisRequests,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: mockAnalysisRequests.length,
          total_pages: Math.ceil(mockAnalysisRequests.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Get analysis request by ID
  rest.get(`${API_BASE_PATH}/analysis/requests/:id`, (req, res, ctx) => {
    const { id } = req.params;
    // Mock analysis request for ID
    const mockAnalysisRequest = {
      id,
      name: id === 'a-1' ? 'Q1 Ocean Freight Analysis' : 'Recent Air Freight Analysis',
      description: id === 'a-1' 
        ? 'Analysis of ocean freight rates for Q1 2023' 
        : 'Analysis of air freight rates for the last 30 days',
      time_period_id: id === 'a-1' ? mockTimePeriods[0].id : mockTimePeriods[1].id,
      time_period: id === 'a-1' ? mockTimePeriods[0] : mockTimePeriods[1],
      data_source_ids: [id === 'a-1' ? mockDataSources[0].id : mockDataSources[2].id],
      filters: id === 'a-1'
        ? [
            { field: 'origin', operator: 'equals', value: 'Shanghai' },
            { field: 'destination', operator: 'equals', value: 'Rotterdam' }
          ]
        : [
            { field: 'mode', operator: 'equals', value: 'Air' }
          ],
      options: {
        calculate_absolute_change: true,
        calculate_percentage_change: true,
        identify_trend_direction: true,
        compare_to_baseline: false,
        baseline_period_id: null,
        output_format: 'json',
        include_visualization: true
      },
      status: 'completed',
      created_by: id === 'a-1' ? mockUsers[0].id : mockUsers[1].id,
      created_at: id === 'a-1' ? '2023-04-01T10:00:00Z' : '2023-06-15T09:30:00Z',
      updated_at: id === 'a-1' ? '2023-04-01T10:15:00Z' : '2023-06-15T09:45:00Z',
      last_run_at: id === 'a-1' ? '2023-04-01T10:15:00Z' : '2023-06-15T09:45:00Z'
    };

    if (id !== 'a-1' && id !== 'a-2') {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Analysis request not found', 404, 'ANALYSIS_REQUEST_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ analysis_request: mockAnalysisRequest }))
    );
  }),

  // Update analysis request
  rest.put(`${API_BASE_PATH}/analysis/requests/:id`, (req, res, ctx) => {
    const { id } = req.params;
    // Mock analysis request for ID
    const mockAnalysisRequest = {
      id,
      name: id === 'a-1' ? 'Q1 Ocean Freight Analysis' : 'Recent Air Freight Analysis',
      description: id === 'a-1' 
        ? 'Analysis of ocean freight rates for Q1 2023' 
        : 'Analysis of air freight rates for the last 30 days',
      time_period_id: id === 'a-1' ? mockTimePeriods[0].id : mockTimePeriods[1].id,
      time_period: id === 'a-1' ? mockTimePeriods[0] : mockTimePeriods[1],
      data_source_ids: [id === 'a-1' ? mockDataSources[0].id : mockDataSources[2].id],
      filters: id === 'a-1'
        ? [
            { field: 'origin', operator: 'equals', value: 'Shanghai' },
            { field: 'destination', operator: 'equals', value: 'Rotterdam' }
          ]
        : [
            { field: 'mode', operator: 'equals', value: 'Air' }
          ],
      options: {
        calculate_absolute_change: true,
        calculate_percentage_change: true,
        identify_trend_direction: true,
        compare_to_baseline: false,
        baseline_period_id: null,
        output_format: 'json',
        include_visualization: true
      },
      status: 'completed',
      created_by: id === 'a-1' ? mockUsers[0].id : mockUsers[1].id,
      created_at: id === 'a-1' ? '2023-04-01T10:00:00Z' : '2023-06-15T09:30:00Z',
      updated_at: new Date().toISOString(),
      last_run_at: id === 'a-1' ? '2023-04-01T10:15:00Z' : '2023-06-15T09:45:00Z'
    };

    if (id !== 'a-1' && id !== 'a-2') {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Analysis request not found', 404, 'ANALYSIS_REQUEST_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ analysis_request: mockAnalysisRequest }))
    );
  }),

  // Delete analysis request
  rest.delete(`${API_BASE_PATH}/analysis/requests/:id`, (req, res, ctx) => {
    const { id } = req.params;

    if (id !== 'a-1' && id !== 'a-2') {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Analysis request not found', 404, 'ANALYSIS_REQUEST_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Analysis request deleted successfully' }))
    );
  }),

  // Run analysis
  rest.post(`${API_BASE_PATH}/analysis/requests/:id/run`, (req, res, ctx) => {
    const { id } = req.params;
    const analysisResult = mockAnalysisResults.find(ar => ar.analysis_id === id);

    if (!analysisResult) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Analysis request not found', 404, 'ANALYSIS_REQUEST_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ analysis_result: analysisResult }))
    );
  }),

  // Get analysis result by ID
  rest.get(`${API_BASE_PATH}/analysis/results/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const analysisResult = mockAnalysisResults.find(ar => ar.id === id);

    if (!analysisResult) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Analysis result not found', 404, 'ANALYSIS_RESULT_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ analysis_result: analysisResult }))
    );
  }),

  // Get analysis results for a specific analysis
  rest.get(`${API_BASE_PATH}/analysis/requests/:id/results`, (req, res, ctx) => {
    const { id } = req.params;
    const analysisResults = mockAnalysisResults.filter(ar => ar.analysis_id === id);

    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        analysis_results: analysisResults,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: analysisResults.length,
          total_pages: Math.ceil(analysisResults.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Get recent analysis results
  rest.get(`${API_BASE_PATH}/analysis/results/recent`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ analysis_results: mockAnalysisResults }))
    );
  }),

  // Export analysis result
  rest.post(`${API_BASE_PATH}/analysis/results/:id/export`, (req, res, ctx) => {
    const { id } = req.params;
    const analysisResult = mockAnalysisResults.find(ar => ar.id === id);

    if (!analysisResult) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Analysis result not found', 404, 'ANALYSIS_RESULT_NOT_FOUND'))
      );
    }

    // Get the format from the request body, default to JSON
    const body = req.body as any;
    const format = body?.format || 'json';

    // Create a mock response based on the requested format
    let responseData, contentType;
    
    if (format === 'json') {
      responseData = JSON.stringify(analysisResult);
      contentType = 'application/json';
    } else if (format === 'csv') {
      // Mock CSV string
      responseData = 'period,price,absolute_change,percentage_change,trend_direction\n' +
        'January 2023,4120.0,,\n' +
        'February 2023,4450.0,330.0,8.01,increasing\n' +
        'March 2023,4365.0,-85.0,-1.91,decreasing\n';
      contentType = 'text/csv';
    } else if (format === 'text') {
      // Mock text summary
      responseData = 'Freight Price Movement Analysis\n' +
        '==============================\n' +
        'Period: Jan 01, 2023 to Mar 31, 2023 (Monthly)\n' +
        'Generated: ' + analysisResult.calculated_at + '\n\n' +
        'SUMMARY:\n' +
        'Freight charges have increased by 5.95% ($245.00 USD) over the selected period.\n\n' +
        'DETAILS:\n' +
        '- Starting value: $4120.00 USD\n' +
        '- Ending value: $4365.00 USD\n' +
        '- Absolute change: $245.00 USD\n' +
        '- Percentage change: 5.95%\n' +
        '- Trend direction: Increasing\n\n' +
        'STATISTICS:\n' +
        '- Average charge: $4245.33 USD\n' +
        '- Minimum charge: $4120.00 USD\n' +
        '- Maximum charge: $4450.00 USD\n';
      contentType = 'text/plain';
    }

    return res(
      ctx.set('Content-Type', contentType),
      ctx.set('Content-Disposition', `attachment; filename="analysis-result-${id}.${format}"`),
      ctx.body(responseData)
    );
  }),
];

// Report Handlers
const reportHandlers = [
  // Create report
  rest.post(`${API_BASE_PATH}/reports`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json(createSuccessResponse({ report: mockReports[0] }))
    );
  }),

  // Get all reports
  rest.get(`${API_BASE_PATH}/reports`, (req, res, ctx) => {
    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        reports: mockReports,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: mockReports.length,
          total_pages: Math.ceil(mockReports.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Get report by ID
  rest.get(`${API_BASE_PATH}/reports/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const report = mockReports.find(r => r.id === id);

    if (!report) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Report not found', 404, 'REPORT_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ report }))
    );
  }),

  // Update report
  rest.put(`${API_BASE_PATH}/reports/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const report = mockReports.find(r => r.id === id);

    if (!report) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Report not found', 404, 'REPORT_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ report }))
    );
  }),

  // Delete report
  rest.delete(`${API_BASE_PATH}/reports/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const report = mockReports.find(r => r.id === id);

    if (!report) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Report not found', 404, 'REPORT_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Report deleted successfully' }))
    );
  }),

  // Run report
  rest.post(`${API_BASE_PATH}/reports/:id/run`, (req, res, ctx) => {
    const { id } = req.params;
    const report = mockReports.find(r => r.id === id);

    if (!report) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Report not found', 404, 'REPORT_NOT_FOUND'))
      );
    }

    // Mock report output as PDF (binary data)
    const mockPdfData = 'JVBERi0xLjcKJeLjz9MKNSAwIG9iago8PC9GaWx0ZXIvRmxhdGVEZWNvZGUvTGVuZ3RoIDE4Pj4Kc3RyZWFtCnicK+QyCuQAABMmA/8KZW5kc3RyZWFtCmVuZG9iago0IDAgb2JqCjw8L0NvbnRlbnRzIDUgMCBSL01lZGlhQm94WzAgMCA2MTIgNzkyXS9QYXJlbnQgMiAwIFIvUmVzb3VyY2VzPDwvRm9udDw8L0YxIDYgMCBSPj4+Pi9UcmltQm94WzAgMCA2MTIgNzkyXS9UeXBlL1BhZ2U+PgplbmRvYmoKMSAwIG9iago8PC9QYWdlcyAyIDAgUi9UeXBlL0NhdGFsb2c+PgplbmRvYmoKMyAwIG9iago8PC9BdXRob3IoSGVsbG8gV29ybGQpL0NyZWF0aW9uRGF0ZShEOjIwMTcxMTE3MjMxODIzKzAxJzAwJykvQ3JlYXRvcihXb3JkKS9Nb2REYXRlKEQ6MjAxNzExMTcyMzE4MjMrMDEnMDAnKS9Qcm9kdWNlcihXb3JkKT4+CmVuZG9iago2IDAgb2JqCjw8L0Jhc2VGb250L0hlbHZldGljYS9FbmNvZGluZy9XaW5BbnNpRW5jb2RpbmcvU3VidHlwZS9UeXBlMS9UeXBlL0ZvbnQ+PgplbmRvYmoKMiAwIG9iago8PC9Db3VudCAxL0tpZHNbNCAwIFJdL1R5cGUvUGFnZXM+PgplbmRvYmoKeHJlZgowIDcKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMTg0IDAwMDAwIG4gCjAwMDAwMDA0NzQgMDAwMDAgbiAKMDAwMDAwMDIyOSAwMDAwMCBuIAowMDAwMDAwMDgzIDAwMDAwIG4gCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDM4NyAwMDAwMCBuIAp0cmFpbGVyCjw8L0luZm8gMyAwIFIvUm9vdCAxIDAgUi9TaXplIDc+PgpzdGFydHhyZWYKNTI2CiUlRU9GCg==';

    return res(
      ctx.set('Content-Type', 'application/pdf'),
      ctx.set('Content-Disposition', `attachment; filename="report-${id}.pdf"`),
      ctx.body(mockPdfData)
    );
  }),

  // Get recent reports
  rest.get(`${API_BASE_PATH}/reports/recent`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ reports: mockReports }))
    );
  }),

  // Create report template
  rest.post(`${API_BASE_PATH}/reports/templates`, (req, res, ctx) => {
    // Mock report template
    const mockReportTemplate = {
      id: 'rt-1',
      name: 'Standard Monthly Report',
      description: 'Standard monthly report template for freight rate analysis',
      content: '# Monthly Freight Rate Report\n\n## Overview\n\n{{summary}}\n\n## Detailed Analysis\n\n{{detailed_results}}\n\n## Trend Visualization\n\n{{chart}}',
      created_by: mockUsers[0].id,
      created_at: '2023-03-15T14:30:00Z',
      updated_at: '2023-03-15T14:30:00Z'
    };

    return res(
      ctx.status(201),
      ctx.json(createSuccessResponse({ template: mockReportTemplate }))
    );
  }),

  // Get all report templates
  rest.get(`${API_BASE_PATH}/reports/templates`, (req, res, ctx) => {
    // Mock report templates
    const mockReportTemplates = [
      {
        id: 'rt-1',
        name: 'Standard Monthly Report',
        description: 'Standard monthly report template for freight rate analysis',
        content: '# Monthly Freight Rate Report\n\n## Overview\n\n{{summary}}\n\n## Detailed Analysis\n\n{{detailed_results}}\n\n## Trend Visualization\n\n{{chart}}',
        created_by: mockUsers[0].id,
        created_at: '2023-03-15T14:30:00Z',
        updated_at: '2023-03-15T14:30:00Z'
      },
      {
        id: 'rt-2',
        name: 'Executive Summary',
        description: 'Brief executive summary of freight rate trends',
        content: '# Executive Summary\n\n## Key Findings\n\n{{summary}}\n\n## Recommendations\n\n{{recommendations}}',
        created_by: mockUsers[0].id,
        created_at: '2023-03-20T11:15:00Z',
        updated_at: '2023-03-20T11:15:00Z'
      }
    ];

    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        templates: mockReportTemplates,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: mockReportTemplates.length,
          total_pages: Math.ceil(mockReportTemplates.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Get report template by ID
  rest.get(`${API_BASE_PATH}/reports/templates/:id`, (req, res, ctx) => {
    const { id } = req.params;
    // Mock report templates
    const mockReportTemplates = {
      'rt-1': {
        id: 'rt-1',
        name: 'Standard Monthly Report',
        description: 'Standard monthly report template for freight rate analysis',
        content: '# Monthly Freight Rate Report\n\n## Overview\n\n{{summary}}\n\n## Detailed Analysis\n\n{{detailed_results}}\n\n## Trend Visualization\n\n{{chart}}',
        created_by: mockUsers[0].id,
        created_at: '2023-03-15T14:30:00Z',
        updated_at: '2023-03-15T14:30:00Z'
      },
      'rt-2': {
        id: 'rt-2',
        name: 'Executive Summary',
        description: 'Brief executive summary of freight rate trends',
        content: '# Executive Summary\n\n## Key Findings\n\n{{summary}}\n\n## Recommendations\n\n{{recommendations}}',
        created_by: mockUsers[0].id,
        created_at: '2023-03-20T11:15:00Z',
        updated_at: '2023-03-20T11:15:00Z'
      }
    };

    const template = mockReportTemplates[id];

    if (!template) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Report template not found', 404, 'REPORT_TEMPLATE_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ template }))
    );
  }),

  // Update report template
  rest.put(`${API_BASE_PATH}/reports/templates/:id`, (req, res, ctx) => {
    const { id } = req.params;
    // Mock report templates
    const mockReportTemplates = {
      'rt-1': {
        id: 'rt-1',
        name: 'Standard Monthly Report',
        description: 'Standard monthly report template for freight rate analysis',
        content: '# Monthly Freight Rate Report\n\n## Overview\n\n{{summary}}\n\n## Detailed Analysis\n\n{{detailed_results}}\n\n## Trend Visualization\n\n{{chart}}',
        created_by: mockUsers[0].id,
        created_at: '2023-03-15T14:30:00Z',
        updated_at: new Date().toISOString()
      },
      'rt-2': {
        id: 'rt-2',
        name: 'Executive Summary',
        description: 'Brief executive summary of freight rate trends',
        content: '# Executive Summary\n\n## Key Findings\n\n{{summary}}\n\n## Recommendations\n\n{{recommendations}}',
        created_by: mockUsers[0].id,
        created_at: '2023-03-20T11:15:00Z',
        updated_at: new Date().toISOString()
      }
    };

    const template = mockReportTemplates[id];

    if (!template) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Report template not found', 404, 'REPORT_TEMPLATE_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ template }))
    );
  }),

  // Delete report template
  rest.delete(`${API_BASE_PATH}/reports/templates/:id`, (req, res, ctx) => {
    const { id } = req.params;
    // Mock report templates
    const mockReportTemplates = {
      'rt-1': {
        id: 'rt-1',
        name: 'Standard Monthly Report',
        description: 'Standard monthly report template for freight rate analysis',
        content: '# Monthly Freight Rate Report\n\n## Overview\n\n{{summary}}\n\n## Detailed Analysis\n\n{{detailed_results}}\n\n## Trend Visualization\n\n{{chart}}',
        created_by: mockUsers[0].id,
        created_at: '2023-03-15T14:30:00Z',
        updated_at: '2023-03-15T14:30:00Z'
      },
      'rt-2': {
        id: 'rt-2',
        name: 'Executive Summary',
        description: 'Brief executive summary of freight rate trends',
        content: '# Executive Summary\n\n## Key Findings\n\n{{summary}}\n\n## Recommendations\n\n{{recommendations}}',
        created_by: mockUsers[0].id,
        created_at: '2023-03-20T11:15:00Z',
        updated_at: '2023-03-20T11:15:00Z'
      }
    };

    const template = mockReportTemplates[id];

    if (!template) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Report template not found', 404, 'REPORT_TEMPLATE_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Report template deleted successfully' }))
    );
  }),

  // Create scheduled report
  rest.post(`${API_BASE_PATH}/reports/scheduled`, (req, res, ctx) => {
    // Mock scheduled report
    const mockScheduledReport = {
      id: 'sr-1',
      report_id: mockReports[0].id,
      name: 'Monthly Ocean Rates Report',
      description: 'Scheduled monthly report for ocean freight rates',
      schedule: {
        frequency: 'monthly',
        day: 1,
        time: '08:00:00',
        timezone: 'UTC',
        recipients: ['admin@example.com', 'analyst@example.com'],
        format: 'PDF'
      },
      is_active: true,
      created_by: mockUsers[0].id,
      created_at: '2023-04-01T11:35:00Z',
      updated_at: '2023-04-01T11:35:00Z',
      last_run: '2023-06-01T08:15:00Z',
      next_run: '2023-07-01T08:00:00Z'
    };

    return res(
      ctx.status(201),
      ctx.json(createSuccessResponse({ scheduled_report: mockScheduledReport }))
    );
  }),

  // Get all scheduled reports
  rest.get(`${API_BASE_PATH}/reports/scheduled`, (req, res, ctx) => {
    // Mock scheduled reports
    const mockScheduledReports = [
      {
        id: 'sr-1',
        report_id: mockReports[0].id,
        name: 'Monthly Ocean Rates Report',
        description: 'Scheduled monthly report for ocean freight rates',
        schedule: {
          frequency: 'monthly',
          day: 1,
          time: '08:00:00',
          timezone: 'UTC',
          recipients: ['admin@example.com', 'analyst@example.com'],
          format: 'PDF'
        },
        is_active: true,
        created_by: mockUsers[0].id,
        created_at: '2023-04-01T11:35:00Z',
        updated_at: '2023-04-01T11:35:00Z',
        last_run: '2023-06-01T08:15:00Z',
        next_run: '2023-07-01T08:00:00Z'
      },
      {
        id: 'sr-2',
        report_id: mockReports[1].id,
        name: 'Weekly APAC Air Cargo Report',
        description: 'Scheduled weekly report for APAC air cargo rates',
        schedule: {
          frequency: 'weekly',
          day: 1, // Monday
          time: '09:00:00',
          timezone: 'UTC',
          recipients: ['analyst@example.com'],
          format: 'PDF'
        },
        is_active: true,
        created_by: mockUsers[1].id,
        created_at: '2023-05-15T15:00:00Z',
        updated_at: '2023-05-15T15:00:00Z',
        last_run: '2023-06-12T09:00:00Z',
        next_run: '2023-06-19T09:00:00Z'
      }
    ];

    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        scheduled_reports: mockScheduledReports,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: mockScheduledReports.length,
          total_pages: Math.ceil(mockScheduledReports.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Get scheduled report by ID
  rest.get(`${API_BASE_PATH}/reports/scheduled/:id`, (req, res, ctx) => {
    const { id } = req.params;
    // Mock scheduled reports
    const mockScheduledReports = {
      'sr-1': {
        id: 'sr-1',
        report_id: mockReports[0].id,
        name: 'Monthly Ocean Rates Report',
        description: 'Scheduled monthly report for ocean freight rates',
        schedule: {
          frequency: 'monthly',
          day: 1,
          time: '08:00:00',
          timezone: 'UTC',
          recipients: ['admin@example.com', 'analyst@example.com'],
          format: 'PDF'
        },
        is_active: true,
        created_by: mockUsers[0].id,
        created_at: '2023-04-01T11:35:00Z',
        updated_at: '2023-04-01T11:35:00Z',
        last_run: '2023-06-01T08:15:00Z',
        next_run: '2023-07-01T08:00:00Z'
      },
      'sr-2': {
        id: 'sr-2',
        report_id: mockReports[1].id,
        name: 'Weekly APAC Air Cargo Report',
        description: 'Scheduled weekly report for APAC air cargo rates',
        schedule: {
          frequency: 'weekly',
          day: 1, // Monday
          time: '09:00:00',
          timezone: 'UTC',
          recipients: ['analyst@example.com'],
          format: 'PDF'
        },
        is_active: true,
        created_by: mockUsers[1].id,
        created_at: '2023-05-15T15:00:00Z',
        updated_at: '2023-05-15T15:00:00Z',
        last_run: '2023-06-12T09:00:00Z',
        next_run: '2023-06-19T09:00:00Z'
      }
    };

    const scheduledReport = mockScheduledReports[id];

    if (!scheduledReport) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Scheduled report not found', 404, 'SCHEDULED_REPORT_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ scheduled_report: scheduledReport }))
    );
  }),

  // Update scheduled report
  rest.put(`${API_BASE_PATH}/reports/scheduled/:id`, (req, res, ctx) => {
    const { id } = req.params;
    // Mock scheduled reports
    const mockScheduledReports = {
      'sr-1': {
        id: 'sr-1',
        report_id: mockReports[0].id,
        name: 'Monthly Ocean Rates Report',
        description: 'Scheduled monthly report for ocean freight rates',
        schedule: {
          frequency: 'monthly',
          day: 1,
          time: '08:00:00',
          timezone: 'UTC',
          recipients: ['admin@example.com', 'analyst@example.com'],
          format: 'PDF'
        },
        is_active: true,
        created_by: mockUsers[0].id,
        created_at: '2023-04-01T11:35:00Z',
        updated_at: new Date().toISOString(),
        last_run: '2023-06-01T08:15:00Z',
        next_run: '2023-07-01T08:00:00Z'
      },
      'sr-2': {
        id: 'sr-2',
        report_id: mockReports[1].id,
        name: 'Weekly APAC Air Cargo Report',
        description: 'Scheduled weekly report for APAC air cargo rates',
        schedule: {
          frequency: 'weekly',
          day: 1, // Monday
          time: '09:00:00',
          timezone: 'UTC',
          recipients: ['analyst@example.com'],
          format: 'PDF'
        },
        is_active: true,
        created_by: mockUsers[1].id,
        created_at: '2023-05-15T15:00:00Z',
        updated_at: new Date().toISOString(),
        last_run: '2023-06-12T09:00:00Z',
        next_run: '2023-06-19T09:00:00Z'
      }
    };

    const scheduledReport = mockScheduledReports[id];

    if (!scheduledReport) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Scheduled report not found', 404, 'SCHEDULED_REPORT_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ scheduled_report: scheduledReport }))
    );
  }),

  // Delete scheduled report
  rest.delete(`${API_BASE_PATH}/reports/scheduled/:id`, (req, res, ctx) => {
    const { id } = req.params;
    // Mock scheduled reports
    const mockScheduledReports = {
      'sr-1': {
        id: 'sr-1',
        report_id: mockReports[0].id,
        name: 'Monthly Ocean Rates Report',
        description: 'Scheduled monthly report for ocean freight rates',
        schedule: {
          frequency: 'monthly',
          day: 1,
          time: '08:00:00',
          timezone: 'UTC',
          recipients: ['admin@example.com', 'analyst@example.com'],
          format: 'PDF'
        },
        is_active: true,
        created_by: mockUsers[0].id,
        created_at: '2023-04-01T11:35:00Z',
        updated_at: '2023-04-01T11:35:00Z',
        last_run: '2023-06-01T08:15:00Z',
        next_run: '2023-07-01T08:00:00Z'
      },
      'sr-2': {
        id: 'sr-2',
        report_id: mockReports[1].id,
        name: 'Weekly APAC Air Cargo Report',
        description: 'Scheduled weekly report for APAC air cargo rates',
        schedule: {
          frequency: 'weekly',
          day: 1, // Monday
          time: '09:00:00',
          timezone: 'UTC',
          recipients: ['analyst@example.com'],
          format: 'PDF'
        },
        is_active: true,
        created_by: mockUsers[1].id,
        created_at: '2023-05-15T15:00:00Z',
        updated_at: '2023-05-15T15:00:00Z',
        last_run: '2023-06-12T09:00:00Z',
        next_run: '2023-06-19T09:00:00Z'
      }
    };

    const scheduledReport = mockScheduledReports[id];

    if (!scheduledReport) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Scheduled report not found', 404, 'SCHEDULED_REPORT_NOT_FOUND'))
      );
    }

    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({ message: 'Scheduled report deleted successfully' }))
    );
  }),

  // Get report run history
  rest.get(`${API_BASE_PATH}/reports/:id/history`, (req, res, ctx) => {
    const { id } = req.params;
    const report = mockReports.find(r => r.id === id);

    if (!report) {
      return res(
        ctx.status(404),
        ctx.json(createErrorResponse('Report not found', 404, 'REPORT_NOT_FOUND'))
      );
    }

    // Mock report run history
    const mockReportRunHistory = [
      {
        id: 'rh-1',
        report_id: id,
        status: 'completed',
        started_at: '2023-06-01T08:00:00Z',
        completed_at: '2023-06-01T08:15:00Z',
        duration_seconds: 900,
        output_format: 'PDF',
        output_size: 1024567,
        triggered_by: 'scheduler',
        message: 'Report generated successfully'
      },
      {
        id: 'rh-2',
        report_id: id,
        status: 'completed',
        started_at: '2023-05-01T08:00:00Z',
        completed_at: '2023-05-01T08:12:00Z',
        duration_seconds: 720,
        output_format: 'PDF',
        output_size: 985432,
        triggered_by: 'scheduler',
        message: 'Report generated successfully'
      }
    ];

    // Support pagination
    const page = req.url.searchParams.get('page') || '1';
    const page_size = req.url.searchParams.get('page_size') || '10';
    
    return res(
      ctx.status(200),
      ctx.json(createSuccessResponse({
        history: mockReportRunHistory,
        pagination: {
          page: parseInt(page),
          page_size: parseInt(page_size),
          total_items: mockReportRunHistory.length,
          total_pages: Math.ceil(mockReportRunHistory.length / parseInt(page_size))
        }
      }))
    );
  }),

  // Download report output
  rest.get(`${API_BASE_PATH}/reports/output/:runId`, (req, res, ctx) => {
    const { runId } = req.params;

    // Mock PDF data
    const mockPdfData = 'JVBERi0xLjcKJeLjz9MKNSAwIG9iago8PC9GaWx0ZXIvRmxhdGVEZWNvZGUvTGVuZ3RoIDE4Pj4Kc3RyZWFtCnicK+QyCuQAABMmA/8KZW5kc3RyZWFtCmVuZG9iago0IDAgb2JqCjw8L0NvbnRlbnRzIDUgMCBSL01lZGlhQm94WzAgMCA2MTIgNzkyXS9QYXJlbnQgMiAwIFIvUmVzb3VyY2VzPDwvRm9udDw8L0YxIDYgMCBSPj4+Pi9UcmltQm94WzAgMCA2MTIgNzkyXS9UeXBlL1BhZ2U+PgplbmRvYmoKMSAwIG9iago8PC9QYWdlcyAyIDAgUi9UeXBlL0NhdGFsb2c+PgplbmRvYmoKMyAwIG9iago8PC9BdXRob3IoSGVsbG8gV29ybGQpL0NyZWF0aW9uRGF0ZShEOjIwMTcxMTE3MjMxODIzKzAxJzAwJykvQ3JlYXRvcihXb3JkKS9Nb2REYXRlKEQ6MjAxNzExMTcyMzE4MjMrMDEnMDAnKS9Qcm9kdWNlcihXb3JkKT4+CmVuZG9iago2IDAgb2JqCjw8L0Jhc2VGb250L0hlbHZldGljYS9FbmNvZGluZy9XaW5BbnNpRW5jb2RpbmcvU3VidHlwZS9UeXBlMS9UeXBlL0ZvbnQ+PgplbmRvYmoKMiAwIG9iago8PC9Db3VudCAxL0tpZHNbNCAwIFJdL1R5cGUvUGFnZXM+PgplbmRvYmoKeHJlZgowIDcKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMTg0IDAwMDAwIG4gCjAwMDAwMDA0NzQgMDAwMDAgbiAKMDAwMDAwMDIyOSAwMDAwMCBuIAowMDAwMDAwMDgzIDAwMDAwIG4gCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDM4NyAwMDAwMCBuIAp0cmFpbGVyCjw8L0luZm8gMyAwIFIvUm9vdCAxIDAgUi9TaXplIDc+PgpzdGFydHhyZWYKNTI2CiUlRU9GCg==';

    return res(
      ctx.set('Content-Type', 'application/pdf'),
      ctx.set('Content-Disposition', `attachment; filename="report-output-${runId}.pdf"`),
      ctx.body(mockPdfData)
    );
  }),
];

// Combine all handlers
export const handlers = [
  ...authHandlers,
  ...userHandlers,
  ...dataSourceHandlers,
  ...analysisHandlers,
  ...reportHandlers
];