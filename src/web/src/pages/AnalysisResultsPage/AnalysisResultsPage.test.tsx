# src/web/src/pages/AnalysisResultsPage/AnalysisResultsPage.test.tsx
```typescript
import React from 'react'; // ^18.2.0
import { render, fireEvent } from '@testing-library/react'; // ^14.0.0
import userEvent from '@testing-library/user-event'; // ^14.4.3
import { vi } from 'vitest'; // ^0.34.0

import AnalysisResultsPage from './AnalysisResultsPage';
import {
  renderWithRouter,
  screen,
  waitFor,
  createMockAnalysisResult,
} from '../../utils/test-utils';
import {
  getAnalysisResult,
  getAnalysisRequest,
  exportAnalysisResult,
} from '../../api/analysis-api';
import {
  AnalysisResult,
  AnalysisRequest,
  OutputFormat,
} from '../../types';
import { ROUTES } from '../../config/routes';

// Mock API functions
vi.mock('../../api/analysis-api', () => ({
  getAnalysisResult: vi.fn(),
  getAnalysisRequest: vi.fn(),
  exportAnalysisResult: vi.fn(),
}));

// Mock useNavigate hook
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

describe('AnalysisResultsPage component', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Clean up after each test
  });

  it('renders loading state initially', async () => {
    // Mock API functions to return promises that don't resolve immediately
    (getAnalysisResult as vi.Mock).mockReturnValue(new Promise(() => { }));
    (getAnalysisRequest as vi.Mock).mockReturnValue(new Promise(() => { }));

    // Render AnalysisResultsPage with a mock result ID
    renderWithRouter(<AnalysisResultsPage />, {}, [{ path: ROUTES.ANALYSIS_RESULTS.path, element: <AnalysisResultsPage /> }]);

    // Verify loading indicators are displayed for summary, chart, and table components
    expect(screen.getByRole('status', { name: /loading summary data/i })).toBeInTheDocument();
    expect(screen.getByRole('status', { name: /loading chart data/i })).toBeInTheDocument();
    expect(screen.getByRole('status', { name: /loading table data/i })).toBeInTheDocument();
  });

  it('displays analysis result data when loaded', async () => {
    // Create mock analysis result data
    const mockAnalysisResult: AnalysisResult = createMockAnalysisResult();

    // Mock API functions to return the mock data
    (getAnalysisResult as vi.Mock).mockResolvedValue(mockAnalysisResult);
    (getAnalysisRequest as vi.Mock).mockResolvedValue({ name: 'Mock Request' } as AnalysisRequest);

    // Render AnalysisResultsPage with a mock result ID
    renderWithRouter(<AnalysisResultsPage />, {}, [{ path: ROUTES.ANALYSIS_RESULTS.path, element: <AnalysisResultsPage /> }]);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/summary/i)).toBeVisible();
    });

    // Verify summary information is displayed correctly
    expect(screen.getByText(/overall change/i)).toBeInTheDocument();
    expect(screen.getByText(/absolute change/i)).toBeInTheDocument();

    // Verify chart is rendered
    expect(screen.getByRole('img', { name: /price movement chart/i })).toBeInTheDocument();

    // Verify detailed results table is displayed
    expect(screen.getByRole('columnheader', { name: /period/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /price/i })).toBeInTheDocument();
  });

  it('displays error message when API request fails', async () => {
    // Mock API functions to reject with an error
    (getAnalysisResult as vi.Mock).mockRejectedValue(new Error('API Error'));
    (getAnalysisRequest as vi.Mock).mockRejectedValue(new Error('API Error'));

    // Render AnalysisResultsPage with a mock result ID
    renderWithRouter(<AnalysisResultsPage />, {}, [{ path: ROUTES.ANALYSIS_RESULTS.path, element: <AnalysisResultsPage /> }]);

    // Wait for error to be caught
    await waitFor(() => {
      expect(screen.getByText(/failed to load analysis results/i)).toBeInTheDocument();
    });
  });

  it('navigates back to analysis page when back button is clicked', async () => {
    // Create mock analysis result and request data
    const mockAnalysisResult: AnalysisResult = createMockAnalysisResult();

    // Mock API functions to return the mock data
    (getAnalysisResult as vi.Mock).mockResolvedValue(mockAnalysisResult);
    (getAnalysisRequest as vi.Mock).mockResolvedValue({ name: 'Mock Request' } as AnalysisRequest);

    // Mock useNavigate
    const navigateMock = vi.fn();
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => navigateMock,
      };
    });

    // Render AnalysisResultsPage with a mock result ID and router
    renderWithRouter(<AnalysisResultsPage />, {}, [{ path: ROUTES.ANALYSIS_RESULTS.path, element: <AnalysisResultsPage /> }]);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/summary/i)).toBeVisible();
    });

    // Click the back button
    const backButton = screen.getByRole('button', { name: /back to analysis/i });
    fireEvent.click(backButton);

    // Verify navigation to the analysis page
    expect(navigateMock).toHaveBeenCalledWith(ROUTES.ANALYSIS.path);
  });

  it('navigates to new analysis page when new analysis button is clicked', async () => {
    // Create mock analysis result data
    const mockAnalysisResult: AnalysisResult = createMockAnalysisResult();

    // Mock API functions to return the mock data
    (getAnalysisResult as vi.Mock).mockResolvedValue(mockAnalysisResult);
    (getAnalysisRequest as vi.Mock).mockResolvedValue({ name: 'Mock Request' } as AnalysisRequest);

    // Mock useNavigate
    const navigateMock = vi.fn();
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => navigateMock,
      };
    });

    // Render AnalysisResultsPage with a mock result ID and router
    renderWithRouter(<AnalysisResultsPage />, {}, [{ path: ROUTES.ANALYSIS_RESULTS.path, element: <AnalysisResultsPage /> }]);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/summary/i)).toBeVisible();
    });

    // Click the new analysis button
    const newAnalysisButton = screen.getByRole('button', { name: /new analysis/i });
    fireEvent.click(newAnalysisButton);

    // Verify navigation to the new analysis page
    expect(navigateMock).toHaveBeenCalledWith(ROUTES.NEW_ANALYSIS.path);
  });

  it('exports analysis results in different formats', async () => {
    // Create mock analysis result data
    const mockAnalysisResult: AnalysisResult = createMockAnalysisResult();

    // Mock API functions including exportAnalysisResult
    (getAnalysisResult as vi.Mock).mockResolvedValue(mockAnalysisResult);
    (getAnalysisRequest as vi.Mock).mockResolvedValue({ name: 'Mock Request' } as AnalysisRequest);
    (exportAnalysisResult as vi.Mock).mockResolvedValue({ data: new Blob() });

    // Render AnalysisResultsPage with a mock result ID
    renderWithRouter(<AnalysisResultsPage />, {}, [{ path: ROUTES.ANALYSIS_RESULTS.path, element: <AnalysisResultsPage /> }]);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/summary/i)).toBeVisible();
    });

    // Click export buttons for different formats (JSON, CSV, TEXT)
    const exportJsonButton = screen.getByRole('button', { name: /export json/i });
    fireEvent.click(exportJsonButton);

    const exportCsvButton = screen.getByRole('button', { name: /export csv/i });
    fireEvent.click(exportCsvButton);

    const exportTextButton = screen.getByRole('button', { name: /export text/i });
    fireEvent.click(exportTextButton);

    // Verify exportAnalysisResult was called with correct parameters for each format
    expect(exportAnalysisResult).toHaveBeenCalledWith(
      mockAnalysisResult.id,
      expect.objectContaining({ format: OutputFormat.JSON })
    );
    expect(exportAnalysisResult).toHaveBeenCalledWith(
      mockAnalysisResult.id,
      expect.objectContaining({ format: OutputFormat.CSV })
    );
    expect(exportAnalysisResult).toHaveBeenCalledWith(
      mockAnalysisResult.id,
      expect.objectContaining({ format: OutputFormat.TEXT })
    );
  });
});