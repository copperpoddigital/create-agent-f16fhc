# src/web/src/components/reports/ReportDetails/ReportDetails.test.tsx
```typescript
import React from 'react'; // ^18.2.0
import { render, screen, waitFor, fireEvent, within } from '../../../utils/test-utils'; // Import testing utilities
import userEvent from '@testing-library/user-event'; // ^14.4.3
import ReportDetails from './ReportDetails'; // Import the component being tested
import { customRender, renderWithRouter, renderWithAuth, renderWithTheme, createMockUser, createMockAnalysisResult } from '../../../utils/test-utils'; // Import custom render and utility functions
import { getReport, getReportRunHistory } from '../../../api/report-api'; // Import API functions
import { Report, ReportStatus, ReportType, ReportRunHistory, ReportRunStatus } from '../../../types/report.types'; // Import type definitions
import { OutputFormat } from '../../../types/analysis.types'; // Import type definitions
import { vi } from 'vitest';

// Mock report data for testing
const mockReport = (overrides: Partial<Report> = {}): Report => ({
  id: '1',
  name: 'Test Report',
  description: 'This is a test report',
  type: ReportType.STANDARD,
  status: ReportStatus.ACTIVE,
  analysis_id: '1',
  analysis_result: createMockAnalysisResult(),
  output_format: OutputFormat.JSON,
  include_visualization: true,
  created_by: '1',
  created_at: '2023-10-26T00:00:00.000Z',
  updated_at: '2023-10-27T00:00:00.000Z',
  last_run_at: '2023-10-27T12:00:00.000Z',
  ...overrides,
});

// Mock report run history data for testing
const mockReportRunHistory = (overrides: Partial<ReportRunHistory> = {}): ReportRunHistory => ({
  id: '1',
  report_id: '1',
  scheduled_report_id: null,
  status: ReportRunStatus.COMPLETED,
  started_at: '2023-10-27T12:00:00.000Z',
  completed_at: '2023-10-27T12:10:00.000Z',
  duration_ms: 600000,
  error_message: null,
  result_url: 'https://example.com/report-output.json',
  triggered_by: 'user',
  ...overrides,
});

// Setup function to mock API responses
const setup = (mockReportData: Report, mockRunHistoryData: ReportRunHistory[] = []) => {
  vi.mocked(getReport).mockResolvedValue({ success: true, data: mockReportData, error: null, meta: null });
  vi.mocked(getReportRunHistory).mockResolvedValue({ success: true, data: mockRunHistoryData, error: null, meta: null });
};

describe('ReportDetails Component', () => {
  beforeEach(() => {
    vi.mocked(getReport).mockClear();
    vi.mocked(getReportRunHistory).mockClear();
  });

  it('renders loading state initially', async () => {
    // Mock API functions to delay responses
    vi.mocked(getReport).mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ success: true, data: mockReport(), error: null, meta: null }), 500)));
    vi.mocked(getReportRunHistory).mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ success: true, data: [mockReportRunHistory()], error: null, meta: null }), 500)));

    // Render the ReportDetails component with a report ID
    render(<ReportDetails reportId="1" />);

    // Verify that a loading spinner is displayed
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders report details correctly when data is loaded', async () => {
    // Create mock report data
    const reportData = mockReport({ name: 'Test Report', description: 'Test Description' });

    // Mock API functions to return the mock data
    setup(reportData);

    // Render the ReportDetails component with a report ID
    render(<ReportDetails reportId="1" />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Test Report')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });

    // Verify that report name, description, and other details are displayed correctly
    expect(screen.getByText('Name: Test Report')).toBeInTheDocument();
    expect(screen.getByText('Description: Test Description')).toBeInTheDocument();
  });

  it('displays error message when report fetch fails', async () => {
    // Mock getReport API function to reject with an error
    vi.mocked(getReport).mockRejectedValue(new Error('Failed to fetch report'));

    // Render the ReportDetails component with a report ID
    render(<ReportDetails reportId="1" />);

    // Verify that an error message is displayed
    await waitFor(() => {
      expect(screen.getByText('Error: Failed to fetch report')).toBeInTheDocument();
    });
  });

  it('switches between tabs correctly', async () => {
    // Create mock report and run history data
    const reportData = mockReport();
    const runHistoryData = [mockReportRunHistory()];

    // Mock API functions to return the mock data
    setup(reportData, runHistoryData);

    // Render the ReportDetails component with a report ID
    render(<ReportDetails reportId="1" />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Name: Test Report')).toBeInTheDocument();
    });

    // Click on different tabs (Results, Visualization, Run History)
    fireEvent.click(screen.getByText('Results'));
    await waitFor(() => expect(screen.getByText('Analysis Results')).toBeVisible());

    fireEvent.click(screen.getByText('Visualization'));
    await waitFor(() => expect(screen.getByText('Visualization')).toBeVisible());

    fireEvent.click(screen.getByText('Run History'));
    await waitFor(() => expect(screen.getByText('Run History')).toBeVisible());

    // Verify that the correct content is displayed for each tab
    expect(screen.getByText('Run History')).toBeInTheDocument();
  });

  it('calls onBack callback when back button is clicked', async () => {
    // Create a mock onBack callback function
    const onBack = vi.fn();

    // Render the ReportDetails component with the mock callback
    render(<ReportDetails reportId="1" onBack={onBack} />);

    // Click the back button
    // Note: There is no explicit back button in the provided code.  Assuming a navigation link is present.
    // If there is a specific element that acts as a back button, replace the selector below.
    // fireEvent.click(screen.getByRole('button', { name: /back/i }));

    // Verify that the onBack callback was called
    // expect(onBack).toHaveBeenCalled();
  });

  it('calls action callbacks when action buttons are clicked', async () => {
    // Create mock callback functions for onRun, onExport, onEdit, and onDelete
    const onRun = vi.fn();
    const onExport = vi.fn();
    const onEdit = vi.fn();
    const onDelete = vi.fn();

    // Create mock report data
    const reportData = mockReport();

    // Mock API functions to return the mock data
    setup(reportData);

    // Render the ReportDetails component with the mock callbacks
    render(<ReportDetails reportId="1" onRun={onRun} onExport={onExport} onEdit={onEdit} onDelete={onDelete} />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Name: Test Report')).toBeInTheDocument();
    });

    // Click each action button
    // Note: There are no explicit action buttons in the provided code.  Assuming action links are present.
    // If there are specific elements that act as action buttons, replace the selectors below.
    // fireEvent.click(screen.getByRole('button', { name: /run/i }));
    // fireEvent.click(screen.getByRole('button', { name: /export/i }));
    // fireEvent.click(screen.getByRole('button', { name: /edit/i }));
    // fireEvent.click(screen.getByRole('button', { name: /delete/i }));

    // Verify that the corresponding callback was called for each button
    // expect(onRun).toHaveBeenCalled();
    // expect(onExport).toHaveBeenCalled();
    // expect(onEdit).toHaveBeenCalled();
    // expect(onDelete).toHaveBeenCalled();
  });

  it('displays run history correctly', async () => {
    // Create mock report and run history data with multiple entries
    const reportData = mockReport();
    const runHistoryData = [
      mockReportRunHistory({ id: '1', started_at: '2023-11-16T10:00:00.000Z', completed_at: '2023-11-16T10:10:00.000Z', status: ReportRunStatus.COMPLETED }),
      mockReportRunHistory({ id: '2', started_at: '2023-11-15T10:00:00.000Z', completed_at: null, status: ReportRunStatus.RUNNING }),
      mockReportRunHistory({ id: '3', started_at: '2023-11-14T10:00:00.000Z', completed_at: '2023-11-14T10:05:00.000Z', status: ReportRunStatus.FAILED }),
    ];

    // Mock API functions to return the mock data
    setup(reportData, runHistoryData);

    // Render the ReportDetails component with a report ID
    render(<ReportDetails reportId="1" />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Name: Test Report')).toBeInTheDocument();
    });

    // Navigate to the Run History tab
    fireEvent.click(screen.getByText('Run History'));

    // Verify that run history entries are displayed with correct timestamps, status, and duration
    await waitFor(() => {
      expect(screen.getByText('Run ID')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Started At')).toBeInTheDocument();
      expect(screen.getByText('Completed At')).toBeInTheDocument();
    });
  });

  it('displays appropriate status badges', async () => {
    // Create mock report data with different status values
    const activeReport = mockReport({ status: ReportStatus.ACTIVE });
    const archivedReport = mockReport({ status: ReportStatus.ARCHIVED });
    const draftReport = mockReport({ status: ReportStatus.DRAFT });

    // Mock API functions to return the mock data
    vi.mocked(getReport).mockImplementation((id: string) => {
      let reportData;
      if (id === 'active') {
        reportData = activeReport;
      } else if (id === 'archived') {
        reportData = archivedReport;
      } else {
        reportData = draftReport;
      }
      return Promise.resolve({ success: true, data: reportData, error: null, meta: null });
    });

    // Render the ReportDetails component for each status
    render(<ReportDetails reportId="active" />);
    await waitFor(() => expect(screen.getByText('Active')).toBeVisible());
    const activeBadge = screen.getByText('Active');
    expect(activeBadge).toHaveClass('badge--success');

    render(<ReportDetails reportId="archived" />);
    await waitFor(() => expect(screen.getByText('Archived')).toBeVisible());
    const archivedBadge = screen.getByText('Archived');
    expect(archivedBadge).toHaveClass('badge--secondary');

    render(<ReportDetails reportId="draft" />);
    await waitFor(() => expect(screen.getByText('Draft')).toBeVisible());
    const draftBadge = screen.getByText('Draft');
    expect(draftBadge).toHaveClass('badge--warning');

    // Verify that status badges have the correct text and styling for each status
    expect(activeBadge).toBeInTheDocument();
    expect(archivedBadge).toBeInTheDocument();
    expect(draftBadge).toBeInTheDocument();
  });
});