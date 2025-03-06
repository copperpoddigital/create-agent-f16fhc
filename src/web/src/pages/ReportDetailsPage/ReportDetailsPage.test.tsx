import React from 'react'; // ^18.2.0
import { renderWithRouter, screen, waitFor, userEvent } from '../../utils/test-utils';
import ReportDetailsPage from './ReportDetailsPage';
import { getReport, runReport, deleteReport, downloadReportOutput } from '../../api/report-api'; // Import API functions
import { jest } from '@jest/globals'; // Testing framework

// Mock the API functions
jest.mock('../../api/report-api');

describe('ReportDetailsPage component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Set up default mock implementations
    (getReport as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        id: '1',
        name: 'Test Report',
        description: 'A test report',
        type: 'standard',
        status: 'active',
        analysis_id: '123',
        analysis_result: null,
        output_format: 'json',
        include_visualization: true,
        created_by: 'user1',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-02T00:00:00Z',
        last_run_at: '2023-01-03T00:00:00Z',
      },
    });
    (runReport as jest.Mock).mockResolvedValue({ success: true });
    (deleteReport as jest.Mock).mockResolvedValue({ success: true });
    (downloadReportOutput as jest.Mock).mockResolvedValue({ success: true, data: 'test data' });
  });

  it('loads and displays report details', async () => {
    renderWithRouter(<ReportDetailsPage />, {}, [{ path: '/reports/:id', element: <ReportDetailsPage /> }]);
    
    // Wait for the report details to load
    await waitFor(() => {
      expect(screen.getByText('Test Report')).toBeInTheDocument();
      expect(screen.getByText('A test report')).toBeInTheDocument();
    });
  });

  it('handles report run action', async () => {
    renderWithRouter(<ReportDetailsPage />, {}, [{ path: '/reports/:id', element: <ReportDetailsPage /> }]);
    
    // Wait for the report details to load
    await waitFor(() => {
      expect(screen.getByText('Test Report')).toBeInTheDocument();
    });

    // Click the "Run Report" button
    const runButton = screen.getByText('Run Report');
    userEvent.click(runButton);

    // Wait for the runReport API to be called
    await waitFor(() => {
      expect(runReport).toHaveBeenCalledWith('1');
    });
  });

  it('handles report export action', async () => {
    renderWithRouter(<ReportDetailsPage />, {}, [{ path: '/reports/:id', element: <ReportDetailsPage /> }]);
    
    // Wait for the report details to load
    await waitFor(() => {
      expect(screen.getByText('Test Report')).toBeInTheDocument();
    });

    // Click the "Export" button
    const exportButton = screen.getByText('Export');
    userEvent.click(exportButton);

    // Wait for the downloadReportOutput API to be called
    await waitFor(() => {
      expect(downloadReportOutput).toHaveBeenCalledWith('1');
    });
  });

  it('handles report edit action', async () => {
    const routes = [{ path: '/reports/:id', element: <ReportDetailsPage /> }, { path: '/reports/edit/:id', element: <div>Edit Report</div> }];
    renderWithRouter(<ReportDetailsPage />, {}, routes);
    
    // Wait for the report details to load
    await waitFor(() => {
      expect(screen.getByText('Test Report')).toBeInTheDocument();
    });

    // Click the "Edit" button
    const editButton = screen.getByText('Edit');
    userEvent.click(editButton);

    // Check if the navigation to the edit page occurred
    await waitFor(() => {
      expect(screen.getByText('Edit Report')).toBeInTheDocument();
    });
  });

  it('handles report delete action and confirmation', async () => {
    const routes = [{ path: '/reports/:id', element: <ReportDetailsPage /> }, { path: '/reports', element: <div>Reports</div> }];
    renderWithRouter(<ReportDetailsPage />, {}, routes);
    
    // Wait for the report details to load
    await waitFor(() => {
      expect(screen.getByText('Test Report')).toBeInTheDocument();
    });

    // Click the "Delete" button
    const deleteButton = screen.getByText('Delete');
    userEvent.click(deleteButton);

    // Confirm the deletion in the modal
    const confirmDeleteButton = screen.getByText('Delete', { selector: 'button' });
    userEvent.click(confirmDeleteButton);

    // Wait for the deleteReport API to be called
    await waitFor(() => {
      expect(deleteReport).toHaveBeenCalledWith('1');
    });

    // Check if the navigation to the reports list occurred
    await waitFor(() => {
      expect(screen.getByText('Reports')).toBeInTheDocument();
    });
  });

  it('handles error when loading report details', async () => {
    (getReport as jest.Mock).mockRejectedValue(new Error('Failed to fetch report'));
    renderWithRouter(<ReportDetailsPage />, {}, [{ path: '/reports/:id', element: <ReportDetailsPage /> }]);
    
    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Error: Failed to fetch report')).toBeInTheDocument();
    });
  });
});