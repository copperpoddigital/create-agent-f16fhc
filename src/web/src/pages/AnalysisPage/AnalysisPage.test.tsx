import React from 'react'; // version ^18.2.0
import { renderWithRouter, screen, waitFor, fireEvent, userEvent } from '../../utils/test-utils';
import AnalysisPage from './AnalysisPage';
import { ROUTES } from '../../config/routes';
import { AnalysisStatus } from '../../types/analysis.types';
import * as jest from 'jest'; // version ^29.5.0

// Mock API functions
const mockGetAnalysisRequests = jest.fn();
const mockDeleteAnalysisRequest = jest.fn();
const mockRunAnalysis = jest.fn();

jest.mock('../../api/analysis-api', () => ({
  getAnalysisRequests: mockGetAnalysisRequests,
  deleteAnalysisRequest: mockDeleteAnalysisRequest,
  runAnalysis: mockRunAnalysis,
}));

// Describe the test suite for the Analysis page component
describe('AnalysisPage Component', () => {
  // Setup function that runs before each test
  beforeEach(() => {
    // Reset all mocks before each test
    mockGetAnalysisRequests.mockReset();
    mockDeleteAnalysisRequest.mockReset();
    mockRunAnalysis.mockReset();
  });

  // Cleanup function that runs after each test
  afterEach(() => {
    jest.clearAllMocks();
  });

  // Helper function to create mock analysis requests for testing
  const mockAnalysisRequests = (count: number) => {
    const requests = [];
    for (let i = 1; i <= count; i++) {
      requests.push({
        id: `analysis-${i}`,
        name: `Analysis ${i}`,
        description: `Description for Analysis ${i}`,
        time_period_id: `time-period-${i}`,
        time_period: {
          id: `time-period-${i}`,
          name: `Time Period ${i}`,
          start_date: '2023-01-01',
          end_date: '2023-01-31',
          granularity: 'monthly',
          custom_interval: null,
          is_custom: false,
          created_by: 'user-1',
          created_at: '2023-01-01T00:00:00Z',
        },
        data_source_ids: ['data-source-1'],
        filters: [],
        options: {
          calculate_absolute_change: true,
          calculate_percentage_change: true,
          identify_trend_direction: true,
          compare_to_baseline: false,
          baseline_period_id: null,
          output_format: 'json',
          include_visualization: true,
        },
        status: AnalysisStatus.COMPLETED,
        created_by: 'user-1',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        last_run_at: '2023-01-02T00:00:00Z',
      });
    }
    return requests;
  };

  // Test case: Renders the Analysis page component
  it('Renders the Analysis page component', async () => {
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: [] });
    renderWithRouter(<AnalysisPage />);
    expect(screen.getByText('Analysis')).toBeInTheDocument();
  });

  // Test case: Displays a loading spinner while fetching data
  it('Displays a loading spinner while fetching data', async () => {
    mockGetAnalysisRequests.mockReturnValue(new Promise(() => {})); // Never resolves
    renderWithRouter(<AnalysisPage />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  // Test case: Displays an error message when data fetching fails
  it('Displays an error message when data fetching fails', async () => {
    mockGetAnalysisRequests.mockRejectedValue(new Error('Failed to fetch data'));
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Failed to fetch data')).toBeInTheDocument());
  });

  // Test case: Displays a list of analysis requests
  it('Displays a list of analysis requests', async () => {
    const mockData = mockAnalysisRequests(3);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    expect(screen.getByText('Analysis 2')).toBeInTheDocument();
    expect(screen.getByText('Analysis 3')).toBeInTheDocument();
  });

  // Test case: Navigates to the new analysis page when the "Create Analysis" button is clicked
  it('Navigates to the new analysis page when the "Create Analysis" button is clicked', async () => {
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: [] });
    const { history } = renderWithRouter(<AnalysisPage />);
    const createButton = screen.getByText('Create Analysis');
    fireEvent.click(createButton);
    expect(history.location.pathname).toBe(ROUTES.NEW_ANALYSIS.path);
  });

  // Test case: Opens the delete confirmation modal when the delete button is clicked
  it('Opens the delete confirmation modal when the delete button is clicked', async () => {
    const mockData = mockAnalysisRequests(1);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    const deleteButton = screen.getByLabelText('Delete analysis Analysis 1');
    fireEvent.click(deleteButton);
    expect(screen.getByText('Are you sure you want to delete this analysis?')).toBeInTheDocument();
  });

  // Test case: Calls the delete API and displays a success message when the delete is confirmed
  it('Calls the delete API and displays a success message when the delete is confirmed', async () => {
    const mockData = mockAnalysisRequests(1);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    mockDeleteAnalysisRequest.mockResolvedValue({ success: true });
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    const deleteButton = screen.getByLabelText('Delete analysis Analysis 1');
    fireEvent.click(deleteButton);

    const confirmDeleteButton = screen.getByText('Delete');
    fireEvent.click(confirmDeleteButton);

    await waitFor(() => expect(screen.getByText('Analysis deleted successfully')).toBeInTheDocument());
    expect(mockDeleteAnalysisRequest).toHaveBeenCalledWith(mockData[0].id);
  });

  // Test case: Displays an error message when the delete API call fails
  it('Displays an error message when the delete API call fails', async () => {
    const mockData = mockAnalysisRequests(1);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    mockDeleteAnalysisRequest.mockRejectedValue(new Error('Failed to delete analysis'));
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    const deleteButton = screen.getByLabelText('Delete analysis Analysis 1');
    fireEvent.click(deleteButton);

    const confirmDeleteButton = screen.getByText('Delete');
    fireEvent.click(confirmDeleteButton);

    await waitFor(() => expect(screen.getByText('Failed to delete analysis')).toBeInTheDocument());
  });

  // Test case: Opens the run confirmation modal when the run button is clicked
  it('Opens the run confirmation modal when the run button is clicked', async () => {
    const mockData = mockAnalysisRequests(1);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    const runButton = screen.getByLabelText('Run analysis Analysis 1');
    fireEvent.click(runButton);
    expect(screen.getByText('Are you sure you want to run this analysis?')).toBeInTheDocument();
  });

  // Test case: Calls the run API and displays a success message when the run is confirmed
  it('Calls the run API and displays a success message when the run is confirmed', async () => {
    const mockData = mockAnalysisRequests(1);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    mockRunAnalysis.mockResolvedValue({ success: true });
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    const runButton = screen.getByLabelText('Run analysis Analysis 1');
    fireEvent.click(runButton);

    const confirmRunButton = screen.getByText('Run');
    fireEvent.click(confirmRunButton);

    await waitFor(() => expect(screen.getByText('Analysis run successfully')).toBeInTheDocument());
    expect(mockRunAnalysis).toHaveBeenCalledWith(mockData[0].id);
  });

  // Test case: Displays an error message when the run API call fails
  it('Displays an error message when the run API call fails', async () => {
    const mockData = mockAnalysisRequests(1);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    mockRunAnalysis.mockRejectedValue(new Error('Failed to run analysis'));
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    const runButton = screen.getByLabelText('Run analysis Analysis 1');
    fireEvent.click(runButton);

    const confirmRunButton = screen.getByText('Run');
    fireEvent.click(confirmRunButton);

    await waitFor(() => expect(screen.getByText('Failed to run analysis')).toBeInTheDocument());
  });

  // Test case: Navigates to the analysis results page when the view button is clicked
  it('Navigates to the analysis results page when the view button is clicked', async () => {
    const mockData = mockAnalysisRequests(1);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    const { history } = renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    const viewButton = screen.getByLabelText('View analysis Analysis 1');
    fireEvent.click(viewButton);
    expect(history.location.pathname).toBe(ROUTES.ANALYSIS_RESULTS.path.replace(':id', mockData[0].id));
  });

  // Test case: Navigates to the edit analysis page when the edit button is clicked
  it('Navigates to the edit analysis page when the edit button is clicked', async () => {
    const mockData = mockAnalysisRequests(1);
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: mockData });
    const { history } = renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('Analysis 1')).toBeInTheDocument());
    const editButton = screen.getByLabelText('Edit analysis Analysis 1');
    fireEvent.click(editButton);
    expect(history.location.pathname).toBe(ROUTES.NEW_ANALYSIS.path);
    expect(history.location.state).toEqual({ analysisId: mockData[0].id });
  });

  // Test case: Displays a message when there are no saved analyses
  it('Displays a message when there are no saved analyses', async () => {
    mockGetAnalysisRequests.mockResolvedValue({ success: true, data: [] });
    renderWithRouter(<AnalysisPage />);
    await waitFor(() => expect(screen.getByText('No saved analyses found.')).toBeInTheDocument());
  });
});