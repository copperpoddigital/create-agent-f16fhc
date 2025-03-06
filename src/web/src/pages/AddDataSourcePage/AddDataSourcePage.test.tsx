import React from 'react'; // ^18.2.0
import { vi } from 'vitest'; // ^0.29.8
import {
  renderWithRouter,
  screen,
  waitFor,
  fireEvent,
  userEvent,
} from '../../utils/test-utils';
import AddDataSourcePage from './AddDataSourcePage';
import { ROUTES } from '../../config/routes';
import { DataSourceType } from '../../types/data-source.types';

// Mock useNavigate hook
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock useAlert hook
const mockShowAlert = vi.fn();
vi.mock('../../hooks/useAlert', () => ({
  default: () => ({
    showSuccess: mockShowAlert,
    showError: mockShowAlert,
  }),
}));

// Mock the createCSVDataSource API function
vi.mock('../../api/data-source-api', () => ({
  createCSVDataSource: vi.fn().mockResolvedValue({ success: true, data: {} }),
  testConnection: vi.fn().mockResolvedValue({ success: true, data: { message: 'Connection successful!' } }),
}));

describe('AddDataSourcePage component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test('renders correctly', () => {
    renderWithRouter(<AddDataSourcePage />);

    expect(screen.getByText('Add Data Source')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  test('navigates back on cancel', async () => {
    renderWithRouter(<AddDataSourcePage />);

    const cancelButton = screen.getByText('Cancel');
    await userEvent.click(cancelButton);

    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.DATA_SOURCES.path);
  });

  test('handles form submission', async () => {
    const mockCreateCSVDataSource = vi.fn().mockResolvedValue({ success: true, data: {} });
    vi.mock('../../api/data-source-api', () => ({
      createCSVDataSource: mockCreateCSVDataSource,
      testConnection: vi.fn().mockResolvedValue({ success: true, data: { message: 'Connection successful!' } }),
    }));
  
    renderWithRouter(<AddDataSourcePage />);
  
    // Fill out the form
    await userEvent.type(screen.getByPlaceholderText('Data Source Name'), 'Test Data Source');
  
    // Select CSV File as source type
    fireEvent.change(screen.getByRole('combobox', { name: /Source Type/i }), {
      target: { value: DataSourceType.CSV },
    });
  
    // Find the file upload input and trigger a file selection
    const fileInput = screen.getByLabelText(/File Upload/i);
    const file = new File(['test content'], 'test.csv', { type: 'text/csv' });
    fireEvent.change(fileInput, { target: { files: [file] } });
  
    // Submit the form
    const saveButton = screen.getByText('Save Source');
    await userEvent.click(saveButton);
  
    // Wait for the API call to be made
    await waitFor(() => {
      expect(mockCreateCSVDataSource).toHaveBeenCalledTimes(1);
    });
  
    // Verify that the API function was called with the correct data
    expect(mockCreateCSVDataSource).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Test Data Source',
        source_type: DataSourceType.CSV,
      })
    );
  
    // Verify that mockShowAlert was called with success message
    expect(mockShowAlert).toHaveBeenCalledWith('Data source created successfully!');
  
    // Verify that mockNavigate was called with the correct route (ROUTES.DATA_SOURCES)
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.DATA_SOURCES.path);
  });

  test('handles form submission error', async () => {
    const mockCreateCSVDataSource = vi.fn().mockRejectedValue(new Error('API error'));
    vi.mock('../../api/data-source-api', () => ({
      createCSVDataSource: mockCreateCSVDataSource,
      testConnection: vi.fn().mockResolvedValue({ success: true, data: { message: 'Connection successful!' } }),
    }));
  
    renderWithRouter(<AddDataSourcePage />);
  
    // Fill out the form
    await userEvent.type(screen.getByPlaceholderText('Data Source Name'), 'Test Data Source');
  
    // Select CSV File as source type
    fireEvent.change(screen.getByRole('combobox', { name: /Source Type/i }), {
      target: { value: DataSourceType.CSV },
    });
  
    // Find the file upload input and trigger a file selection
    const fileInput = screen.getByLabelText(/File Upload/i);
    const file = new File(['test content'], 'test.csv', { type: 'text/csv' });
    fireEvent.change(fileInput, { target: { files: [file] } });
  
    // Submit the form
    const saveButton = screen.getByText('Save Source');
    await userEvent.click(saveButton);
  
    // Wait for the API call to be made
    await waitFor(() => {
      expect(mockCreateCSVDataSource).toHaveBeenCalledTimes(1);
    });
  
    // Verify that mockShowAlert was called with error message
    expect(mockShowAlert).toHaveBeenCalledWith('API error');
  
    // Verify that mockNavigate was not called
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});