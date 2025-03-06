import { UserRole, Theme, DateFormat } from '../src/types/user.types';
import { 
  DataSourceType, 
  DataSourceStatus, 
  DatabaseType, 
  TMSType, 
  ERPType, 
  AuthType 
} from '../src/types/data-source.types';
import { 
  TimeGranularity, 
  AnalysisStatus, 
  TrendDirection, 
  OutputFormat 
} from '../src/types/analysis.types';

/**
 * Mock Users
 * Array of mock user objects for testing authentication and user management features
 */
export const mockUsers = [
  {
    id: 'user-1',
    username: 'admin',
    email: 'admin@example.com',
    firstName: 'Admin',
    lastName: 'User',
    role: 'UserRole.ADMIN',
    isActive: true,
    isLocked: false,
    lastLogin: '2023-06-15T10:30:00Z',
    defaultCurrency: 'USD',
    dateFormat: 'DateFormat.MM_DD_YYYY',
    theme: 'Theme.DARK',
    emailNotifications: true,
    smsNotifications: false,
    inAppNotifications: true,
    preferences: {
      significantPriceChangeThreshold: 5,
      defaultView: 'dashboard',
      dashboardLayout: {},
      notifyOnPriceChanges: true,
      notifyOnDataSourceUpdates: true,
      notifyOnSystemMaintenance: false
    },
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-06-15T10:30:00Z'
  },
  {
    id: 'user-2',
    username: 'analyst',
    email: 'analyst@example.com',
    firstName: 'Analyst',
    lastName: 'User',
    role: 'UserRole.ANALYST',
    isActive: true,
    isLocked: false,
    lastLogin: '2023-06-14T15:45:00Z',
    defaultCurrency: 'EUR',
    dateFormat: 'DateFormat.DD_MM_YYYY',
    theme: 'Theme.LIGHT',
    emailNotifications: true,
    smsNotifications: false,
    inAppNotifications: true,
    preferences: {
      significantPriceChangeThreshold: 3,
      defaultView: 'analysis',
      dashboardLayout: {},
      notifyOnPriceChanges: true,
      notifyOnDataSourceUpdates: false,
      notifyOnSystemMaintenance: false
    },
    createdAt: '2023-01-15T00:00:00Z',
    updatedAt: '2023-06-14T15:45:00Z'
  }
];

/**
 * Mock Authentication Tokens
 * Object representing authentication tokens for testing auth flows
 */
export const mockAuthTokens = {
  accessToken: 'mock-access-token-very-long-string',
  refreshToken: 'mock-refresh-token-very-long-string',
  expiresAt: 1687104000000, // Unix timestamp for token expiration
  tokenType: 'Bearer'
};

/**
 * Mock Data Sources
 * Array of mock data source objects for testing data source management features
 */
export const mockDataSources = [
  {
    id: 'ds-1',
    name: 'TMS Export',
    description: 'Daily export from transportation management system',
    source_type: 'DataSourceType.CSV',
    status: 'DataSourceStatus.ACTIVE',
    created_at: '2023-05-01T10:00:00Z',
    updated_at: '2023-06-15T08:30:00Z',
    last_sync: '2023-06-15T08:30:00Z',
    field_mapping: {
      freight_charge: 'price',
      currency: 'currency_code',
      origin: 'origin',
      destination: 'destination',
      date_time: 'quote_date',
      carrier: 'carrier_name',
      mode: 'transport_mode',
      service_level: 'service_type'
    },
    file_path: '/uploads/tms_export.csv',
    file_name: 'tms_export.csv',
    delimiter: ',',
    has_header: true,
    date_format: 'YYYY-MM-DD'
  },
  {
    id: 'ds-2',
    name: 'ERP Database',
    description: 'Connection to enterprise resource planning system',
    source_type: 'DataSourceType.DATABASE',
    status: 'DataSourceStatus.ACTIVE',
    created_at: '2023-04-15T14:20:00Z',
    updated_at: '2023-06-10T11:45:00Z',
    last_sync: '2023-06-14T23:00:00Z',
    field_mapping: {
      freight_charge: 'freight_cost',
      currency: 'currency',
      origin: 'origin_location',
      destination: 'destination_location',
      date_time: 'transaction_date',
      carrier: 'vendor_name',
      mode: 'shipping_method',
      service_level: 'service_level'
    },
    database_type: 'DatabaseType.POSTGRESQL',
    host: 'erp-db.example.com',
    port: 5432,
    database: 'erp_production',
    username: 'readonly_user',
    query: "SELECT * FROM freight_transactions WHERE transaction_date > '2023-01-01'"
  },
  {
    id: 'ds-3',
    name: 'Carrier API',
    description: 'Direct connection to carrier rate API',
    source_type: 'DataSourceType.API',
    status: 'DataSourceStatus.WARNING',
    created_at: '2023-03-10T09:15:00Z',
    updated_at: '2023-06-12T16:30:00Z',
    last_sync: '2023-06-12T16:30:00Z',
    field_mapping: {
      freight_charge: 'rate.amount',
      currency: 'rate.currency',
      origin: 'route.origin',
      destination: 'route.destination',
      date_time: 'rate.effectiveDate',
      carrier: 'carrier.name',
      mode: 'service.mode',
      service_level: 'service.level'
    },
    url: 'https://api.carrier.example.com/rates',
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: null,
    auth_type: 'AuthType.API_KEY',
    auth_config: {
      apiKey: 'x-api-key',
      apiKeyValue: 'mock-api-key-value'
    },
    response_path: 'data.rates'
  }
];

/**
 * Mock Time Periods
 * Array of mock time period objects for testing time period selection features
 */
export const mockTimePeriods = [
  {
    id: 'tp-1',
    name: 'Q1 2023',
    start_date: '2023-01-01T00:00:00Z',
    end_date: '2023-03-31T23:59:59Z',
    granularity: 'TimeGranularity.MONTHLY',
    custom_interval: null,
    is_custom: false,
    created_by: 'user-1',
    created_at: '2023-04-01T10:00:00Z'
  },
  {
    id: 'tp-2',
    name: 'Last 30 Days',
    start_date: '2023-05-16T00:00:00Z',
    end_date: '2023-06-15T23:59:59Z',
    granularity: 'TimeGranularity.DAILY',
    custom_interval: null,
    is_custom: false,
    created_by: 'user-2',
    created_at: '2023-06-15T09:30:00Z'
  },
  {
    id: 'tp-3',
    name: 'Custom Weekly',
    start_date: '2023-04-01T00:00:00Z',
    end_date: '2023-06-15T23:59:59Z',
    granularity: 'TimeGranularity.CUSTOM',
    custom_interval: '7d',
    is_custom: true,
    created_by: 'user-1',
    created_at: '2023-06-10T14:15:00Z'
  }
];

/**
 * Mock Analysis Results
 * Array of mock analysis result objects for testing analysis features
 */
export const mockAnalysisResults = [
  {
    id: 'ar-1',
    analysis_id: 'a-1',
    time_period: {
      id: 'tp-1',
      name: 'Q1 2023',
      start_date: '2023-01-01T00:00:00Z',
      end_date: '2023-03-31T23:59:59Z',
      granularity: 'TimeGranularity.MONTHLY',
      custom_interval: null,
      is_custom: false,
      created_by: 'user-1',
      created_at: '2023-04-01T10:00:00Z'
    },
    filters: [
      { field: 'origin', operator: 'equals', value: 'Shanghai' },
      { field: 'destination', operator: 'equals', value: 'Rotterdam' }
    ],
    start_value: 4120.0,
    end_value: 4365.0,
    currency: 'USD',
    price_change: {
      absolute_change: 245.0,
      percentage_change: 5.95,
      trend_direction: 'TrendDirection.INCREASING'
    },
    aggregates: {
      average: 4245.33,
      minimum: 4120.0,
      maximum: 4450.0
    },
    time_series: [
      { timestamp: '2023-01-31T23:59:59Z', value: 4120.0 },
      { timestamp: '2023-02-28T23:59:59Z', value: 4450.0 },
      { timestamp: '2023-03-31T23:59:59Z', value: 4365.0 }
    ],
    detailed_results: [
      { 
        period: 'January 2023', 
        price: 4120.0, 
        absolute_change: null, 
        percentage_change: null, 
        trend_direction: null 
      },
      { 
        period: 'February 2023', 
        price: 4450.0, 
        absolute_change: 330.0, 
        percentage_change: 8.01, 
        trend_direction: 'TrendDirection.INCREASING' 
      },
      { 
        period: 'March 2023', 
        price: 4365.0, 
        absolute_change: -85.0, 
        percentage_change: -1.91, 
        trend_direction: 'TrendDirection.DECREASING' 
      }
    ],
    baseline_comparison: null,
    calculated_at: '2023-04-01T10:15:00Z'
  },
  {
    id: 'ar-2',
    analysis_id: 'a-2',
    time_period: {
      id: 'tp-2',
      name: 'Last 30 Days',
      start_date: '2023-05-16T00:00:00Z',
      end_date: '2023-06-15T23:59:59Z',
      granularity: 'TimeGranularity.WEEKLY',
      custom_interval: null,
      is_custom: false,
      created_by: 'user-2',
      created_at: '2023-06-15T09:30:00Z'
    },
    filters: [
      { field: 'mode', operator: 'equals', value: 'Air' }
    ],
    start_value: 8750.0,
    end_value: 8620.0,
    currency: 'USD',
    price_change: {
      absolute_change: -130.0,
      percentage_change: -1.49,
      trend_direction: 'TrendDirection.DECREASING'
    },
    aggregates: {
      average: 8685.0,
      minimum: 8620.0,
      maximum: 8750.0
    },
    time_series: [
      { timestamp: '2023-05-22T23:59:59Z', value: 8750.0 },
      { timestamp: '2023-05-29T23:59:59Z', value: 8720.0 },
      { timestamp: '2023-06-05T23:59:59Z', value: 8650.0 },
      { timestamp: '2023-06-12T23:59:59Z', value: 8620.0 }
    ],
    detailed_results: [
      { 
        period: 'Week of May 16-22', 
        price: 8750.0, 
        absolute_change: null, 
        percentage_change: null, 
        trend_direction: null 
      },
      { 
        period: 'Week of May 23-29', 
        price: 8720.0, 
        absolute_change: -30.0, 
        percentage_change: -0.34, 
        trend_direction: 'TrendDirection.STABLE' 
      },
      { 
        period: 'Week of May 30-Jun 5', 
        price: 8650.0, 
        absolute_change: -70.0, 
        percentage_change: -0.8, 
        trend_direction: 'TrendDirection.STABLE' 
      },
      { 
        period: 'Week of Jun 6-12', 
        price: 8620.0, 
        absolute_change: -30.0, 
        percentage_change: -0.35, 
        trend_direction: 'TrendDirection.STABLE' 
      }
    ],
    baseline_comparison: null,
    calculated_at: '2023-06-15T09:45:00Z'
  }
];

/**
 * Mock Time Series Data
 * Array of mock time series data objects for testing chart visualization
 */
export const mockTimeSeriesData = [
  {
    id: 'ts-1',
    name: 'Ocean Freight Shanghai to Rotterdam',
    data: [
      { timestamp: '2023-01-01T00:00:00Z', value: 4120.0 },
      { timestamp: '2023-01-08T00:00:00Z', value: 4150.0 },
      { timestamp: '2023-01-15T00:00:00Z', value: 4320.0 },
      { timestamp: '2023-01-22T00:00:00Z', value: 4280.0 },
      { timestamp: '2023-01-29T00:00:00Z', value: 4350.0 },
      { timestamp: '2023-02-05T00:00:00Z', value: 4400.0 },
      { timestamp: '2023-02-12T00:00:00Z', value: 4450.0 },
      { timestamp: '2023-02-19T00:00:00Z', value: 4430.0 },
      { timestamp: '2023-02-26T00:00:00Z', value: 4420.0 },
      { timestamp: '2023-03-05T00:00:00Z', value: 4400.0 },
      { timestamp: '2023-03-12T00:00:00Z', value: 4380.0 },
      { timestamp: '2023-03-19T00:00:00Z', value: 4370.0 },
      { timestamp: '2023-03-26T00:00:00Z', value: 4365.0 }
    ],
    currency: 'USD',
    start_date: '2023-01-01T00:00:00Z',
    end_date: '2023-03-31T23:59:59Z'
  },
  {
    id: 'ts-2',
    name: 'Air Freight Global Average',
    data: [
      { timestamp: '2023-05-16T00:00:00Z', value: 8750.0 },
      { timestamp: '2023-05-23T00:00:00Z', value: 8720.0 },
      { timestamp: '2023-05-30T00:00:00Z', value: 8650.0 },
      { timestamp: '2023-06-06T00:00:00Z', value: 8620.0 },
      { timestamp: '2023-06-13T00:00:00Z', value: 8620.0 }
    ],
    currency: 'USD',
    start_date: '2023-05-16T00:00:00Z',
    end_date: '2023-06-15T23:59:59Z'
  }
];

/**
 * Mock Reports
 * Array of mock report objects for testing report management features
 */
export const mockReports = [
  {
    id: 'r-1',
    name: 'Q1 Ocean Rates',
    description: 'Quarterly analysis of ocean freight rates',
    analysis_id: 'a-1',
    created_by: 'user-1',
    created_at: '2023-04-01T11:30:00Z',
    last_run: '2023-06-01T08:15:00Z',
    schedule: {
      frequency: 'monthly',
      day: 1,
      time: '08:00:00',
      timezone: 'UTC',
      recipients: ['admin@example.com', 'analyst@example.com'],
      format: 'PDF'
    },
    is_scheduled: true,
    status: 'active'
  },
  {
    id: 'r-2',
    name: 'APAC Air Cargo',
    description: 'Analysis of air cargo rates in Asia-Pacific region',
    analysis_id: 'a-2',
    created_by: 'user-2',
    created_at: '2023-05-15T14:45:00Z',
    last_run: '2023-06-14T09:30:00Z',
    schedule: null,
    is_scheduled: false,
    status: 'active'
  }
];