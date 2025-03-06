import React from 'react';
import { vi } from 'vitest';
import DataSourceDetails from './DataSourceDetails';
import { customRender, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';
import { getDataSourceById, syncDataSource, getDataSourceLogs } from '../../../api/data-source-api';
import { DataSourceType, DataSourceStatus } from '../../../types/data-source.types';

// Mock the API functions
vi.mock('../../../api/data-source-api');

// Helper function to create a mock data source for testing
function createMockDataSource(overrides = {}) {
  return {
    id: 'test-id',
    name: 'Test Data Source',
    description: 'Test description',
    source_type: DataSourceType.CSV,
    status: DataSourceStatus.ACTIVE,
    created_at: '2023-06-15T10:00:00Z',
    updated_at: '2023-06-15T11:00:00Z',
    last_sync: '2023-06-15T11:00:00Z',
    field_mapping: {
      freight_charge: 'price',
      currency: 'currency_code',
      origin: 'origin',
      destination: 'destination',
      date_time: 'quote_date',
      carrier: 'carrier',
      mode: 'transport_mode',
      service_level: 'service_level'
    },
    // CSV specific properties
    file_path: '/uploads/test.csv',
    file_name: 'test.csv',
    delimiter: ',',
    has_header: true,
    date_format: 'YYYY-MM-DD',
    ...overrides
  };
}

// Helper function to create a mock data source log for testing
function createMockDataSourceLog(overrides = {}) {
  return {
    id: 'log-id',
    data_source_id: 'test-id',
    operation: 'sync',
    status: 'success',
    message: 'Data synchronized successfully',
    details: null,
    records_processed: 100,
    records_succeeded: 98,
    records_failed: 2,
    started_at: '2023-06-15T11:00:00Z',
    completed_at: '2023-06-15T11:01:00Z',
    duration_seconds: 60,
    ...overrides
  };
}

describe('DataSourceDetails', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    vi.resetAllMocks();
    
    // Setup mock implementations for API functions
    (getDataSourceById as any).mockResolvedValue(createMockDataSource());
    (getDataSourceLogs as any).mockResolvedValue([createMockDataSourceLog()]);
    (syncDataSource as any).mockResolvedValue({ jobId: 'test-job-id' });
  });

  test('renders loading state initially', () => {
    // Mock getDataSourceById to return a promise that doesn't resolve immediately
    (getDataSourceById as any).mockImplementation(() => new Promise(() => {}));
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    expect(screen.getByText(/loading data source details/i)).toBeInTheDocument();
  });
  
  test('renders error state when data fetching fails', async () => {
    // Mock getDataSourceById to reject with an error
    (getDataSourceById as any).mockRejectedValue(new Error('Failed to fetch data source'));
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the error state to be displayed
    await waitFor(() => {
      expect(screen.getByText(/error:/i)).toBeInTheDocument();
      expect(screen.getByText(/failed to fetch data source/i)).toBeInTheDocument();
    });
  });
  
  test('renders CSV data source details correctly', async () => {
    const csvDataSource = createMockDataSource();
    (getDataSourceById as any).mockResolvedValue(csvDataSource);
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    // Check data source type and status
    expect(screen.getByText(/CSV/i)).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    
    // Check CSV specific details
    expect(screen.getByText(/file name:/i)).toBeInTheDocument();
    expect(screen.getByText('test.csv')).toBeInTheDocument();
    expect(screen.getByText(/delimiter:/i)).toBeInTheDocument();
    expect(screen.getByText(',')).toBeInTheDocument();
    
    // Check field mappings
    expect(screen.getByText(/freight charge/i)).toBeInTheDocument();
    expect(screen.getByText('price')).toBeInTheDocument();
  });
  
  test('renders Database data source details correctly', async () => {
    const dbDataSource = createMockDataSource({
      source_type: DataSourceType.DATABASE,
      database_type: 'postgresql',
      host: 'localhost',
      port: 5432,
      database: 'freight_db',
      username: 'freight_user',
      query: 'SELECT * FROM freight_data'
    });
    
    (getDataSourceById as any).mockResolvedValue(dbDataSource);
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    // Check data source type and status
    expect(screen.getByText(/DATABASE/i)).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    
    // Check Database specific details
    expect(screen.getByText(/database type:/i)).toBeInTheDocument();
    expect(screen.getByText('postgresql')).toBeInTheDocument();
    expect(screen.getByText(/host:/i)).toBeInTheDocument();
    expect(screen.getByText('localhost')).toBeInTheDocument();
    expect(screen.getByText(/port:/i)).toBeInTheDocument();
    expect(screen.getByText('5432')).toBeInTheDocument();
  });
  
  test('renders API data source details correctly', async () => {
    const apiDataSource = createMockDataSource({
      source_type: DataSourceType.API,
      url: 'https://api.example.com/freight',
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      auth_type: 'api_key',
      response_path: 'data.freight',
      body: '{"request": "data"}'
    });
    
    (getDataSourceById as any).mockResolvedValue(apiDataSource);
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    // Check data source type and status
    expect(screen.getByText(/API/i)).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    
    // Check API specific details
    expect(screen.getByText(/url:/i)).toBeInTheDocument();
    expect(screen.getByText('https://api.example.com/freight')).toBeInTheDocument();
    expect(screen.getByText(/method:/i)).toBeInTheDocument();
    expect(screen.getByText('GET')).toBeInTheDocument();
    expect(screen.getByText(/Content-Type:/i)).toBeInTheDocument();
    expect(screen.getByText(/request body:/i)).toBeInTheDocument();
  });
  
  test('renders TMS data source details correctly', async () => {
    const tmsDataSource = createMockDataSource({
      source_type: DataSourceType.TMS,
      tms_type: 'sap_tm',
      connection_url: 'https://sap-tm.example.com',
      username: 'tms_user',
      custom_parameters: { system: 'prod' }
    });
    
    (getDataSourceById as any).mockResolvedValue(tmsDataSource);
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    // Check data source type and status
    expect(screen.getByText(/TMS/i)).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    
    // Check TMS specific details
    expect(screen.getByText(/tms type:/i)).toBeInTheDocument();
    expect(screen.getByText('sap_tm')).toBeInTheDocument();
    expect(screen.getByText(/connection url:/i)).toBeInTheDocument();
    expect(screen.getByText('https://sap-tm.example.com')).toBeInTheDocument();
    expect(screen.getByText(/system:/i)).toBeInTheDocument();
    expect(screen.getByText('prod')).toBeInTheDocument();
  });
  
  test('renders ERP data source details correctly', async () => {
    const erpDataSource = createMockDataSource({
      source_type: DataSourceType.ERP,
      erp_type: 'sap_erp',
      connection_url: 'https://sap-erp.example.com',
      username: 'erp_user',
      custom_parameters: { system: 'prod' }
    });
    
    (getDataSourceById as any).mockResolvedValue(erpDataSource);
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    // Check data source type and status
    expect(screen.getByText(/ERP/i)).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
    
    // Check ERP specific details
    expect(screen.getByText(/erp type:/i)).toBeInTheDocument();
    expect(screen.getByText('sap_erp')).toBeInTheDocument();
    expect(screen.getByText(/connection url:/i)).toBeInTheDocument();
    expect(screen.getByText('https://sap-erp.example.com')).toBeInTheDocument();
  });
  
  test('calls onEdit when edit button is clicked', async () => {
    const mockDataSource = createMockDataSource();
    (getDataSourceById as any).mockResolvedValue(mockDataSource);
    
    const onEdit = vi.fn();
    customRender(<DataSourceDetails dataSourceId="test-id" onEdit={onEdit} />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);
    
    expect(onEdit).toHaveBeenCalled();
  });
  
  test('calls onDelete when delete button is clicked', async () => {
    const mockDataSource = createMockDataSource();
    (getDataSourceById as any).mockResolvedValue(mockDataSource);
    
    const onDelete = vi.fn();
    customRender(<DataSourceDetails dataSourceId="test-id" onDelete={onDelete} />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);
    
    expect(onDelete).toHaveBeenCalled();
  });
  
  test('calls onBack when back button is clicked', async () => {
    const mockDataSource = createMockDataSource();
    (getDataSourceById as any).mockResolvedValue(mockDataSource);
    
    const onBack = vi.fn();
    customRender(<DataSourceDetails dataSourceId="test-id" onBack={onBack} />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    const backButton = screen.getByText(/back to data sources/i);
    fireEvent.click(backButton);
    
    expect(onBack).toHaveBeenCalled();
  });
  
  test('triggers sync when sync button is clicked', async () => {
    const mockDataSource = createMockDataSource();
    (getDataSourceById as any).mockResolvedValue(mockDataSource);
    (syncDataSource as any).mockResolvedValue({ jobId: 'job-id' });
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    const syncButton = screen.getByText('Sync Now');
    fireEvent.click(syncButton);
    
    expect(syncDataSource).toHaveBeenCalledWith('test-id');
    
    // Wait for the sync in progress state to be shown
    await waitFor(() => {
      expect(screen.getByText('Syncing...')).toBeInTheDocument();
    });
    
    // Wait for the sync to complete
    await waitFor(() => {
      expect(screen.getByText('Sync Now')).toBeInTheDocument();
    });
    
    // Verify that getDataSourceById is called again to refresh the data
    expect(getDataSourceById).toHaveBeenCalledTimes(2);
  });
  
  test('displays logs correctly', async () => {
    const mockDataSource = createMockDataSource();
    const mockLogs = [
      createMockDataSourceLog(),
      createMockDataSourceLog({
        id: 'log-id-2',
        operation: 'import',
        status: 'failed',
        message: 'Import failed',
        started_at: '2023-06-14T10:00:00Z',
        completed_at: '2023-06-14T10:01:00Z'
      })
    ];
    
    (getDataSourceById as any).mockResolvedValue(mockDataSource);
    (getDataSourceLogs as any).mockResolvedValue(mockLogs);
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the data and logs to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    // Check logs section
    expect(screen.getByText('Recent Operations')).toBeInTheDocument();
    expect(screen.getByText('sync')).toBeInTheDocument();
    expect(screen.getByText('import')).toBeInTheDocument();
    expect(screen.getByText('success')).toBeInTheDocument();
    expect(screen.getByText('failed')).toBeInTheDocument();
    expect(screen.getByText('98/100 processed')).toBeInTheDocument();
  });
  
  test('handles log loading errors gracefully', async () => {
    const mockDataSource = createMockDataSource();
    (getDataSourceById as any).mockResolvedValue(mockDataSource);
    (getDataSourceLogs as any).mockRejectedValue(new Error('Failed to load logs'));
    
    customRender(<DataSourceDetails dataSourceId="test-id" />);
    
    // Wait for the data to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test Data Source')).toBeInTheDocument();
    });
    
    // The component shouldn't crash when logs fail to load
    expect(screen.getByText(/file name:/i)).toBeInTheDocument();
    expect(screen.getByText('test.csv')).toBeInTheDocument();
    
    // The component will show the "Recent Operations" section but might show a loading state or error message
    expect(screen.getByText('Recent Operations')).toBeInTheDocument();
  });
});