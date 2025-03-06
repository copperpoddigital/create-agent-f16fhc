import React from 'react';
import { vi } from 'vitest';
import { renderWithRouter, screen, waitFor, userEvent } from '../../utils/test-utils';
import DataSourcesPage from './DataSourcesPage';
import { AlertProvider } from '../../contexts/AlertContext';

// Mock the useNavigate hook from react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({ useNavigate: () => mockNavigate }));

describe('DataSourcesPage', () => {
  beforeEach(() => {
    // Reset mocks before each test
    mockNavigate.mockReset();
    vi.clearAllMocks();
  });

  test('renders the data sources page', async () => {
    renderWithRouter(
      <AlertProvider>
        <DataSourcesPage />
      </AlertProvider>
    );

    // Wait for the page title to be visible
    await waitFor(() => {
      expect(screen.getByText('Data Sources')).toBeInTheDocument();
    });
    
    // Check that the Add button is present
    expect(screen.getByText('Add Source')).toBeInTheDocument();
    
    // Check that the DataSourceList component is rendered
    expect(screen.getByTestId('data-source-list')).toBeInTheDocument();
  });

  test('navigates to add data source page when add button is clicked', async () => {
    renderWithRouter(
      <AlertProvider>
        <DataSourcesPage />
      </AlertProvider>
    );

    // Find the add button and click it
    const addButton = screen.getByText('Add Source');
    await userEvent.click(addButton);

    // Verify navigation was called with the expected path
    expect(mockNavigate).toHaveBeenCalledWith('/data-sources/add');
  });

  test('navigates to edit data source page with correct ID', async () => {
    // Mock the DataSourceList component to access the onEditDataSource prop
    let mockOnEditDataSource;
    vi.mock('../../components/data-sources/DataSourceList', () => ({
      __esModule: true,
      default: (props) => {
        mockOnEditDataSource = props.onEditDataSource;
        return <div data-testid="data-source-list">DataSourceList</div>;
      }
    }));

    renderWithRouter(
      <AlertProvider>
        <DataSourcesPage />
      </AlertProvider>
    );
    
    // Call the onEditDataSource function with a test ID
    mockOnEditDataSource('test-id');
    
    // Verify navigation was called with the expected path
    expect(mockNavigate).toHaveBeenCalledWith('/data-sources/edit/test-id');
  });

  test('refreshes data sources when refresh is triggered', async () => {
    // Mock the DataSourceList component to access the refreshTrigger prop
    let refreshTriggerValue;
    vi.mock('../../components/data-sources/DataSourceList', () => ({
      __esModule: true,
      default: (props) => {
        refreshTriggerValue = props.refreshTrigger;
        return <div data-testid="data-source-list">DataSourceList</div>;
      }
    }));

    renderWithRouter(
      <AlertProvider>
        <DataSourcesPage />
      </AlertProvider>
    );
    
    // Verify that refreshTrigger was passed to DataSourceList
    expect(refreshTriggerValue).toBeDefined();
    expect(typeof refreshTriggerValue).toBe('boolean');
    
    // Store the initial value
    const initialValue = refreshTriggerValue;
    
    // Simulate calling handleRefresh (which toggles the refreshTrigger state)
    // by getting the instance and calling the method
    const dataSourcePage = screen.getByTestId('data-source-list');
    
    // Re-render to trigger state update
    renderWithRouter(
      <AlertProvider>
        <DataSourcesPage />
      </AlertProvider>
    );
    
    // Verify that refreshTrigger prop was updated
    expect(refreshTriggerValue).not.toBe(initialValue);
  });
});