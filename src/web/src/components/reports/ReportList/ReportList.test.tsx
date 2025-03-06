import React from 'react';
import { vi } from 'vitest';
import { customRender, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';
import ReportList from './ReportList';
import { getReports, deleteReport, runReport } from '../../../api/report-api';
import { Report, ReportStatus } from '../../../types/report.types';

// Mock the API functions
vi.mock('../../../api/report-api', () => ({
  getReports: vi.fn(),
  deleteReport: vi.fn(),
  runReport: vi.fn()
}));

// Mock the useAlert hook
vi.mock('../../../hooks/useAlert', () => ({
  default: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn()
  })
}));

// Mock URL.createObjectURL and URL.revokeObjectURL for file download testing
Object.defineProperty(window.URL, 'createObjectURL', {
  writable: true,
  value: vi.fn().mockReturnValue('blob:mock-url')
});

Object.defineProperty(window.URL, 'revokeObjectURL', {
  writable: true,
  value: vi.fn()
});

/**
 * Creates a mock report object for testing
 */
const createMockReport = (overrides: Partial<Report> = {}): Report => {
  return {
    id: `report-${Math.random().toString(36).substr(2, 9)}`,
    name: 'Test Report',
    description: 'Test report description',
    type: 'standard',
    status: ReportStatus.ACTIVE,
    analysis_id: 'analysis-123',
    analysis_result: null,
    output_format: 'json',
    include_visualization: true,
    created_by: 'user-123',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    last_run_at: null,
    ...overrides
  };
};

/**
 * Creates an array of mock reports for testing
 */
const createMockReports = (count: number): Report[] => {
  return Array.from({ length: count }).map((_, index) => 
    createMockReport({
      id: `report-${index}`,
      name: `Test Report ${index}`,
      created_at: `2023-01-0${index + 1}T00:00:00Z`,
      last_run_at: index % 2 === 0 ? `2023-01-0${index + 1}T12:00:00Z` : null
    })
  );
};

describe('ReportList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly with reports', async () => {
    const mockReports = createMockReports(3);
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: mockReports,
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 3 
          } 
        }
      },
      error: null
    });

    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Check reports are rendered
    for (const report of mockReports) {
      expect(screen.getByText(report.name)).toBeInTheDocument();
    }
    
    // Check action buttons are rendered
    expect(screen.getAllByTitle('Run Report').length).toBe(mockReports.length);
    expect(screen.getAllByTitle('Delete Report').length).toBe(mockReports.length);
  });

  it('displays loading state', async () => {
    // Create a promise that won't resolve immediately
    let resolvePromise: (value: any) => void;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    
    getReports.mockReturnValue(promise);
    
    customRender(<ReportList />);
    
    // Check loading state is displayed
    expect(screen.getByLabelText('Loading table data...')).toBeInTheDocument();
    
    // Resolve the promise to complete the test
    resolvePromise({
      success: true,
      data: {
        data: createMockReports(1),
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 1 
          } 
        }
      },
      error: null
    });
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
  });

  it('handles empty state', async () => {
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: [],
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 0, 
            totalItems: 0 
          } 
        }
      },
      error: null
    });
    
    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    expect(screen.getByText('No reports found')).toBeInTheDocument();
  });

  it('handles filtering', async () => {
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: createMockReports(3),
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 3 
          } 
        }
      },
      error: null
    });
    
    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Clear the mock to track new calls
    getReports.mockClear();
    
    // Type filter text
    const filterInput = screen.getByPlaceholderText('Filter reports...');
    fireEvent.change(filterInput, { target: { value: 'Test' } });
    
    // Click apply
    const applyButton = screen.getByRole('button', { name: /apply/i });
    fireEvent.click(applyButton);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledWith(expect.objectContaining({ 
        filter: 'Test' 
      }));
    });
  });

  it('handles pagination', async () => {
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: createMockReports(10),
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 2, 
            totalItems: 15,
            hasNext: true,
            hasPrevious: false
          } 
        }
      },
      error: null
    });
    
    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Clear the mock to track new calls
    getReports.mockClear();
    
    // Second page of results
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: createMockReports(5),
        meta: { 
          pagination: { 
            page: 2, 
            pageSize: 10,
            totalPages: 2, 
            totalItems: 15,
            hasNext: false,
            hasPrevious: true
          } 
        }
      },
      error: null
    });
    
    // Click next page
    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledWith(expect.objectContaining({ 
        page: 2 
      }));
    });
  });

  it('handles sorting', async () => {
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: createMockReports(3),
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 3 
          } 
        }
      },
      error: null
    });
    
    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Clear the mock to track new calls
    getReports.mockClear();
    
    // Find a sortable column header (Name)
    const nameHeader = screen.getByText('Name');
    fireEvent.click(nameHeader);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledWith(expect.objectContaining({ 
        sortBy: 'name',
        sortDirection: 'asc'
      }));
    });
    
    // Sort by name in descending order
    getReports.mockClear();
    fireEvent.click(nameHeader);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledWith(expect.objectContaining({ 
        sortBy: 'name',
        sortDirection: 'desc'
      }));
    });
  });

  it('handles run report action', async () => {
    const mockReports = createMockReports(1);
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: mockReports,
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 1 
          } 
        }
      },
      error: null
    });
    
    // Mock the runReport function
    const mockBlob = new Blob(['test data'], { type: 'text/csv' });
    runReport.mockResolvedValue({
      success: true,
      data: mockBlob,
      error: null
    });
    
    // Mock document.createElement and click
    const mockLink = {
      href: '',
      download: '',
      click: vi.fn()
    };
    document.createElement = vi.fn().mockReturnValue(mockLink);
    document.body.appendChild = vi.fn();
    document.body.removeChild = vi.fn();
    
    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Click run button
    const runButton = screen.getByTitle('Run report Test Report 0');
    fireEvent.click(runButton);
    
    await waitFor(() => {
      expect(runReport).toHaveBeenCalledWith(mockReports[0].id);
      expect(window.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
      expect(mockLink.click).toHaveBeenCalled();
      expect(window.URL.revokeObjectURL).toHaveBeenCalled();
    });
  });

  it('handles edit report action', async () => {
    const mockReports = createMockReports(1);
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: mockReports,
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 1 
          } 
        }
      },
      error: null
    });
    
    const onEditReport = vi.fn();
    
    customRender(<ReportList onEditReport={onEditReport} />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Click edit button
    const editButton = screen.getByTitle('Edit report Test Report 0');
    fireEvent.click(editButton);
    
    expect(onEditReport).toHaveBeenCalledWith(mockReports[0].id);
  });

  it('handles view report action', async () => {
    const mockReports = createMockReports(1);
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: mockReports,
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 1 
          } 
        }
      },
      error: null
    });
    
    const onViewReport = vi.fn();
    
    customRender(<ReportList onViewReport={onViewReport} />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Find the row and click it (should trigger view action)
    const reportRow = screen.getByText('Test Report 0').closest('tr');
    fireEvent.click(reportRow!);
    
    expect(onViewReport).toHaveBeenCalledWith(mockReports[0].id);
  });

  it('handles delete report action', async () => {
    const mockReports = createMockReports(1);
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: mockReports,
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 1 
          } 
        }
      },
      error: null
    });
    
    deleteReport.mockResolvedValue({
      success: true,
      data: null,
      error: null
    });
    
    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Click delete button
    const deleteButton = screen.getByTitle('Delete report Test Report 0');
    fireEvent.click(deleteButton);
    
    // Check that confirmation modal is displayed
    expect(screen.getByText(/are you sure you want to delete this report/i)).toBeInTheDocument();
    
    // Confirm deletion
    const confirmButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(confirmButton);
    
    await waitFor(() => {
      expect(deleteReport).toHaveBeenCalledWith(mockReports[0].id);
      expect(getReports).toHaveBeenCalledTimes(2); // Called again to refresh the list
    });
  });

  it('handles cancel delete action', async () => {
    const mockReports = createMockReports(1);
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: mockReports,
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 1 
          } 
        }
      },
      error: null
    });
    
    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Click delete button
    const deleteButton = screen.getByTitle('Delete report Test Report 0');
    fireEvent.click(deleteButton);
    
    // Check that confirmation modal is displayed
    expect(screen.getByText(/are you sure you want to delete this report/i)).toBeInTheDocument();
    
    // Cancel deletion
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    
    // Check modal is closed
    await waitFor(() => {
      expect(screen.queryByText(/are you sure you want to delete this report/i)).not.toBeInTheDocument();
    });
    
    // Check deleteReport was not called
    expect(deleteReport).not.toHaveBeenCalled();
  });

  it('handles create report action', async () => {
    getReports.mockResolvedValue({
      success: true,
      data: {
        data: createMockReports(1),
        meta: { 
          pagination: { 
            page: 1, 
            pageSize: 10,
            totalPages: 1, 
            totalItems: 1 
          } 
        }
      },
      error: null
    });
    
    const onCreateReport = vi.fn();
    
    customRender(<ReportList onCreateReport={onCreateReport} />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // Click create report button
    const createButton = screen.getByRole('button', { name: /create report/i });
    fireEvent.click(createButton);
    
    expect(onCreateReport).toHaveBeenCalled();
  });

  it('handles API errors', async () => {
    // Mock API error
    getReports.mockRejectedValue(new Error('Failed to fetch reports'));
    
    customRender(<ReportList />);
    
    await waitFor(() => {
      expect(getReports).toHaveBeenCalledTimes(1);
    });
    
    // The component should handle the error gracefully
    // No table should be rendered when there's an error
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });
});