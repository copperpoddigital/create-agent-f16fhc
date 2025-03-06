import React from 'react'; // ^18.2.0
import { vi } from 'vitest'; // ^0.30.1
import {
  renderWithRouter,
  screen,
  waitFor,
  fireEvent,
  userEvent,
} from '../../utils/test-utils';
import EditDataSourcePage from './EditDataSourcePage';
import { getDataSourceById, updateDataSource } from '../../api/data-source-api';
import { DataSourceType } from '../../types/data-source.types';
import { ROUTES } from '../../config/routes';

// Mock useNavigate hook
const useNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => useNavigate,
    useParams: () => ({ id: '123' }),
  };
});

// Describe the test suite for EditDataSourcePage component
describe('EditDataSourcePage', () => {
  // Mock API functions
  const mockGetDataSourceById = vi.fn();
  const mockUpdateDataSource = vi.fn();

  // Before each test, reset mocks and setup mock implementations
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock getDataSourceById implementation
    (getDataSourceById as vi.Mock).mockImplementation(mockGetDataSourceById);

    // Mock updateDataSource implementation
    (updateDataSource as vi.Mock).mockImplementation(mockUpdateDataSource);
  });

  // After each test, clear all mocks
  afterEach(() => {
    vi.clearAllMocks();
  });

  // Test case: renders loading state initially
  it('renders loading state initially', () => {
    // Render the EditDataSourcePage component
    renderWithRouter(<EditDataSourcePage />);

    // Verify that loading spinner is displayed
    expect(screen.getByRole('status', { name: /loading data source details.../i })).toBeInTheDocument();
  });

  // Test case: loads and displays data source details
  it('loads and displays data source details', async () => {
    // Mock getDataSourceById to return a data source
    mockGetDataSourceById.mockResolvedValue({
      success: true,
      data: {
        id: '123',
        name: 'Test Data Source',
        description: 'A test data source',
        source_type: DataSourceType.CSV,
        status: 'active',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        last_sync: null,
        field_mapping: {
          freight_charge: 'price',
          currency: 'currency_code',
          origin: 'origin',
          destination: 'destination',
          date_time: 'quote_date',
          carrier: null,
          mode: null,
          service_level: null,
        },
      },
    });

    // Render the EditDataSourcePage component
    renderWithRouter(<EditDataSourcePage />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('status', { name: /loading data source details.../i })).not.toBeInTheDocument();
    });

    // Verify that data source details are displayed in the form
    expect(screen.getByLabelText(/name/i)).toHaveValue('Test Data Source');
    expect(screen.getByLabelText(/description/i)).toHaveValue('A test data source');
  });

  // Test case: handles API error when loading data source
  it('handles API error when loading data source', async () => {
    // Mock getDataSourceById to throw an error
    mockGetDataSourceById.mockRejectedValue(new Error('Failed to fetch data source'));

    // Render the EditDataSourcePage component
    renderWithRouter(<EditDataSourcePage />);

    // Verify that error handling is triggered
    await waitFor(() => {
      expect(useNavigate).toHaveBeenCalledWith(ROUTES.DATA_SOURCES.path);
    });
  });

  // Test case: submits updated data source successfully
  it('submits updated data source successfully', async () => {
    // Mock getDataSourceById to return a data source
    mockGetDataSourceById.mockResolvedValue({
      success: true,
      data: {
        id: '123',
        name: 'Test Data Source',
        description: 'A test data source',
        source_type: DataSourceType.CSV,
        status: 'active',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        last_sync: null,
        field_mapping: {
          freight_charge: 'price',
          currency: 'currency_code',
          origin: 'origin',
          destination: 'destination',
          date_time: 'quote_date',
          carrier: null,
          mode: null,
          service_level: null,
        },
      },
    });

    // Mock updateDataSource to return success
    mockUpdateDataSource.mockResolvedValue({ success: true });

    // Render the EditDataSourcePage component
    renderWithRouter(<EditDataSourcePage />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByLabelText(/name/i)).toHaveValue('Test Data Source');
    });

    // Update form fields
    fireEvent.change(screen.getByLabelText(/name/i), { target: { value: 'Updated Data Source' } });
    fireEvent.change(screen.getByLabelText(/description/i), { target: { value: 'An updated data source' } });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /save source/i }));

    // Verify that updateDataSource was called with correct data
    await waitFor(() => {
      expect(mockUpdateDataSource).toHaveBeenCalledWith('123', expect.objectContaining({
        name: 'Updated Data Source',
        description: 'An updated data source',
      }));
    });

    // Verify that success message is displayed
    await waitFor(() => {
      expect(useNavigate).toHaveBeenCalledWith(ROUTES.DATA_SOURCES.path);
    });
  });

  // Test case: handles API error when updating data source
  it('handles API error when updating data source', async () => {
    // Mock getDataSourceById to return a data source
    mockGetDataSourceById.mockResolvedValue({
      success: true,
      data: {
        id: '123',
        name: 'Test Data Source',
        description: 'A test data source',
        source_type: DataSourceType.CSV,
        status: 'active',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        last_sync: null,
        field_mapping: {
          freight_charge: 'price',
          currency: 'currency_code',
          origin: 'origin',
          destination: 'destination',
          date_time: 'quote_date',
          carrier: null,
          mode: null,
          service_level: null,
        },
      },
    });

    // Mock updateDataSource to throw an error
    mockUpdateDataSource.mockRejectedValue(new Error('Failed to update data source'));

    // Render the EditDataSourcePage component
    renderWithRouter(<EditDataSourcePage />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByLabelText(/name/i)).toHaveValue('Test Data Source');
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /save source/i }));

    // Verify that error handling is triggered
    await waitFor(() => {
      expect(screen.getByText(/failed to update data source/i)).toBeInTheDocument();
    });
  });

  // Test case: navigates back when cancel button is clicked
  it('navigates back when cancel button is clicked', async () => {
    // Mock getDataSourceById to return a data source
    mockGetDataSourceById.mockResolvedValue({
      success: true,
      data: {
        id: '123',
        name: 'Test Data Source',
        description: 'A test data source',
        source_type: DataSourceType.CSV,
        status: 'active',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        last_sync: null,
        field_mapping: {
          freight_charge: 'price',
          currency: 'currency_code',
          origin: 'origin',
          destination: 'destination',
          date_time: 'quote_date',
          carrier: null,
          mode: null,
          service_level: null,
        },
      },
    });

    // Render the EditDataSourcePage component
    renderWithRouter(<EditDataSourcePage />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByLabelText(/name/i)).toHaveValue('Test Data Source');
    });

    // Click the cancel button
    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));

    // Verify that navigation is called to redirect back to data sources list
    expect(useNavigate).toHaveBeenCalledWith(ROUTES.DATA_SOURCES.path);
  });
});