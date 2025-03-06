import React from 'react';
import { vi } from 'vitest';
import DataSourceList from './DataSourceList';
import { customRender, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';
import { DataSourceType, DataSourceStatus } from '../../../types/data-source.types';
import { getDataSources, deleteDataSource, syncDataSource } from '../../../api/data-source-api';

// Mock API functions
vi.mock('../../../api/data-source-api', () => ({
  getDataSources: vi.fn(),
  deleteDataSource: vi.fn(),
  syncDataSource: vi.fn()
}));

// Mock data for testing
const mockDataSources = [
  {
    id: '1',
    name: 'TMS Export',
    description: 'Daily export from transportation management system',
    source_type: DataSourceType.TMS,
    status: DataSourceStatus.ACTIVE,
    created_at: '2023-04-01T10:00:00Z',
    updated_at: '2023-04-01T10:00:00Z',
    last_sync: '2023-04-01T10:00:00Z'
  },
  {
    id: '2',
    name: 'ERP Database',
    description: 'Connection to enterprise resource planning system',
    source_type: DataSourceType.DATABASE,
    status: DataSourceStatus.ACTIVE,
    created_at: '2023-03-15T08:30:00Z',
    updated_at: '2023-03-15T08:30:00Z',
    last_sync: '2023-04-01T09:00:00Z'
  },
  {
    id: '3',
    name: 'Carrier API',
    description: 'External carrier rate API',
    source_type: DataSourceType.API,
    status: DataSourceStatus.WARNING,
    created_at: '2023-02-20T14:15:00Z',
    updated_at: '2023-02-20T14:15:00Z',
    last_sync: '2023-03-29T11:30:00Z'
  },
  {
    id: '4',
    name: 'Legacy System',
    description: 'CSV export from legacy system',
    source_type: DataSourceType.CSV,
    status: DataSourceStatus.INACTIVE,
    created_at: '2023-01-10T09:45:00Z',
    updated_at: '2023-01-10T09:45:00Z',
    last_sync: '2023-03-22T16:00:00Z'
  },
  {
    id: '5',
    name: 'Market Rates',
    description: 'Market rate API integration',
    source_type: DataSourceType.API,
    status: DataSourceStatus.ERROR,
    created_at: '2023-03-05T11:20:00Z',
    updated_at: '2023-03-05T11:20:00Z',
    last_sync: '2023-04-01T08:15:00Z'
  }
];

// Mock API response structure
const mockApiResponse = {
  data: [],
  meta: {
    pagination: {
      total: 0,
      page: 1,
      pageSize: 10,
      totalPages: 1
    }
  },
  success: true,
  message: 'Success',
  error: null
};

describe('DataSourceList Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the data source list correctly', async () => {
    // Mock getDataSources to return a list of test data sources
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);

    // Render the DataSourceList component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for the component to load data
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Verify that the table headers are displayed
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Type')).toBeInTheDocument();
    expect(screen.getByText('Last Update')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();

    // Verify that the data sources are displayed in the table
    expect(screen.getByText('TMS Export')).toBeInTheDocument();
    expect(screen.getByText('ERP Database')).toBeInTheDocument();
    expect(screen.getByText('Carrier API')).toBeInTheDocument();
    expect(screen.getByText('Legacy System')).toBeInTheDocument();
    expect(screen.getByText('Market Rates')).toBeInTheDocument();

    // Verify the correct number of data sources
    const rows = screen.getAllByRole('row');
    // +1 for the header row
    expect(rows.length).toBe(mockDataSources.length + 1);
  });

  it('displays loading state while fetching data', async () => {
    // Create a promise that won't resolve immediately to simulate loading
    let resolvePromise: (value: any) => void;
    const loadingPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    
    // Mock getDataSources to return the delayed promise
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockReturnValue(loadingPromise);

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Verify loading state is displayed
    expect(screen.getByLabelText('Loading table data...')).toBeInTheDocument();

    // Resolve the promise to complete loading
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    resolvePromise(response);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByLabelText('Loading table data...')).not.toBeInTheDocument();
    });

    // Verify data is displayed
    expect(screen.getByText('TMS Export')).toBeInTheDocument();
  });

  it('displays error state when data fetching fails', async () => {
    // Mock getDataSources to reject with an error
    const errorMessage = 'Failed to fetch data sources';
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(new Error(errorMessage));

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for the error state
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Verify empty message is displayed
    expect(screen.getByText(/No data sources found. Click 'Add Source' to create one./i)).toBeInTheDocument();
  });

  it('filters data sources based on search input', async () => {
    // Mock getDataSources for initial load
    const initialResponse = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(initialResponse);
    
    // Mock getDataSources for filtered results
    const filteredResponse = { 
      ...mockApiResponse, 
      data: [mockDataSources[0]], // Only return the first data source
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: 1
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(filteredResponse);

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for initial data load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalledTimes(1);
    });

    // Type in the search input
    const searchInput = screen.getByPlaceholderText('Filter by name...');
    await userEvent.type(searchInput, 'TMS');
    
    // Wait for debounced search to trigger API call
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalledTimes(2);
    }, { timeout: 500 }); // Increased timeout for debounce

    // Verify the API was called with the correct filter
    expect(getDataSources).toHaveBeenLastCalledWith(
      expect.objectContaining({}),
      expect.arrayContaining([
        expect.objectContaining({
          field: 'name',
          operator: 'contains',
          value: 'TMS'
        })
      ])
    );
  });

  it('handles pagination correctly', async () => {
    // Mock initial page response
    const page1Response = { 
      ...mockApiResponse, 
      data: mockDataSources.slice(0, 3),
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          page: 1,
          totalPages: 2,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(page1Response);
    
    // Mock next page response
    const page2Response = { 
      ...mockApiResponse, 
      data: mockDataSources.slice(3),
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          page: 2,
          totalPages: 2,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValueOnce(page2Response);

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for initial data load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalledTimes(1);
    });

    // Click on the next page button
    const nextPageButton = screen.getByLabelText('Go to next page');
    await userEvent.click(nextPageButton);
    
    // Verify pagination API call
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalledTimes(2);
    });
    
    // Verify the API was called with the correct page parameter
    expect(getDataSources).toHaveBeenLastCalledWith(
      expect.objectContaining({
        page: 2
      }),
      undefined
    );
  });

  it('calls onEditDataSource when edit button is clicked', async () => {
    // Mock getDataSources to return a list of test data sources
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);

    // Create mock function for onEditDataSource
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    
    // Render the component
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Find and click the edit button for the first data source
    const editButton = screen.getByLabelText('Edit TMS Export');
    await userEvent.click(editButton);
    
    // Verify onEditDataSource was called with the correct ID
    expect(onEditDataSource).toHaveBeenCalledWith('1');
  });

  it('shows delete confirmation modal when delete button is clicked', async () => {
    // Mock getDataSources to return a list of test data sources
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Find and click the delete button for the first data source
    const deleteButton = screen.getByLabelText('Delete TMS Export');
    await userEvent.click(deleteButton);
    
    // Verify that the delete confirmation modal is displayed
    expect(screen.getByText('Confirm Deletion')).toBeInTheDocument();
    
    // Verify that the modal contains the data source name
    expect(screen.getByText(/Are you sure you want to delete the data source "TMS Export"/i)).toBeInTheDocument();
  });

  it('deletes data source when confirmation is confirmed', async () => {
    // Mock getDataSources to return a list of test data sources
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);
    
    // Mock deleteDataSource to return a success response
    const deleteResponse = { success: true, data: null, error: null, meta: null };
    (deleteDataSource as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(deleteResponse);

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Find and click the delete button for the first data source
    const deleteButton = screen.getByLabelText('Delete TMS Export');
    await userEvent.click(deleteButton);
    
    // Click the confirm button in the delete confirmation modal
    const confirmButton = screen.getByRole('button', { name: 'Delete' });
    await userEvent.click(confirmButton);
    
    // Verify deleteDataSource was called with the correct ID
    expect(deleteDataSource).toHaveBeenCalledWith('1');
    
    // Verify getDataSources was called again to refresh the list
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalledTimes(2);
    });
  });

  it('syncs data source when sync button is clicked', async () => {
    // Mock getDataSources to return a list of test data sources
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);
    
    // Mock syncDataSource to return a success response
    const syncResponse = { success: true, data: { jobId: '123' }, error: null, meta: null };
    (syncDataSource as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(syncResponse);

    // Use fake timers for setTimeout
    vi.useFakeTimers();

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Find and click the sync button for the first data source
    const syncButton = screen.getByLabelText('Synchronize TMS Export');
    await userEvent.click(syncButton);
    
    // Verify syncDataSource was called with the correct ID
    expect(syncDataSource).toHaveBeenCalledWith('1');
    
    // Fast-forward timers to trigger the setTimeout
    vi.advanceTimersByTime(1000);
    
    // Wait for refresh API call after sync
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalledTimes(2);
    });
    
    // Restore real timers
    vi.useRealTimers();
  });

  it('handles sync error correctly', async () => {
    // Mock getDataSources to return a list of test data sources
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);
    
    // Mock syncDataSource to return an error
    const errorMessage = 'Failed to sync data source';
    (syncDataSource as unknown as ReturnType<typeof vi.fn>).mockRejectedValue(new Error(errorMessage));

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Find and click the sync button for the first data source
    const syncButton = screen.getByLabelText('Synchronize TMS Export');
    await userEvent.click(syncButton);
    
    // Verify syncDataSource was called with the correct ID
    expect(syncDataSource).toHaveBeenCalledWith('1');
  });

  it('renders correct status badges for different data source statuses', async () => {
    // Mock getDataSources to return data sources with different statuses
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Verify that statuses are present
    expect(screen.getAllByText(DataSourceStatus.ACTIVE)).toHaveLength(2);
    expect(screen.getByText(DataSourceStatus.INACTIVE)).toBeInTheDocument();
    expect(screen.getByText(DataSourceStatus.WARNING)).toBeInTheDocument();
    expect(screen.getByText(DataSourceStatus.ERROR)).toBeInTheDocument();
  });

  it('renders correct icons for different data source types', async () => {
    // Mock getDataSources to return data sources with different types
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);

    // Render the component
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Check for source type text content
    expect(screen.getByText(DataSourceType.CSV)).toBeInTheDocument();
    expect(screen.getByText(DataSourceType.DATABASE)).toBeInTheDocument();
    expect(screen.getAllByText(DataSourceType.API)).toHaveLength(2); // Two API sources
    expect(screen.getByText(DataSourceType.TMS)).toBeInTheDocument();
  });

  it('calls onAddDataSource when add button is clicked', async () => {
    // Mock getDataSources to return a list of test data sources
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);

    // Create mock function for onAddDataSource
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    
    // Render the component
    customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalled();
    });

    // Find and click the add data source button
    const addButton = screen.getByText('Add Source');
    await userEvent.click(addButton);
    
    // Verify onAddDataSource was called
    expect(onAddDataSource).toHaveBeenCalled();
  });

  it('refreshes data when refreshTrigger prop changes', async () => {
    // Mock getDataSources to return a list of test data sources
    const response = { 
      ...mockApiResponse, 
      data: mockDataSources,
      meta: {
        ...mockApiResponse.meta,
        pagination: {
          ...mockApiResponse.meta.pagination,
          total: mockDataSources.length
        }
      }
    };
    (getDataSources as unknown as ReturnType<typeof vi.fn>).mockResolvedValue(response);

    // Render the component with refreshTrigger=false
    const onAddDataSource = vi.fn();
    const onEditDataSource = vi.fn();
    const { rerender } = customRender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
        refreshTrigger={false}
      />
    );

    // Wait for initial data load
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalledTimes(1);
    });

    // Re-render with refreshTrigger=true
    rerender(
      <DataSourceList 
        onAddDataSource={onAddDataSource} 
        onEditDataSource={onEditDataSource}
        refreshTrigger={true}
      />
    );
    
    // Verify getDataSources was called again
    await waitFor(() => {
      expect(getDataSources).toHaveBeenCalledTimes(2);
    });
  });
});