import React from 'react'; // ^18.2.0
import { render, act } from '@testing-library/react'; // ^14.0.0
import { customRender, screen, waitFor, createMockAnalysisResult } from '../../utils/test-utils';
import { getRecentAnalysisResults } from '../../api/analysis-api';
import DashboardPage from './DashboardPage';
import useMediaQuery from '../../hooks/useMediaQuery';
import { AnalysisResult } from '../../types/analysis.types';
import { Mock } from 'jest'; // ^29.5.0

// Mock the API call
jest.mock('../../api/analysis-api', () => ({
  getRecentAnalysisResults: jest.fn()
}));

// Mock the useMediaQuery hook
jest.mock('../../hooks/useMediaQuery');

describe('DashboardPage component', () => {
  beforeEach(() => {
    (getRecentAnalysisResults as Mock).mockClear();
    (useMediaQuery as Mock).mockImplementation(() => false); // Default to non-mobile
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state', () => {
    (getRecentAnalysisResults as Mock).mockResolvedValue({ success: true, data: [] });

    customRender(<DashboardPage />);

    expect(screen.getByText('Loading dashboard data...')).toBeInTheDocument();
  });

  it('renders error state', async () => {
    (getRecentAnalysisResults as Mock).mockRejectedValue(new Error('API Error'));

    customRender(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Error loading dashboard data. Please try again later.')).toBeInTheDocument();
    });
  });

  it('renders dashboard widgets with data', async () => {
    const mockAnalysisResults: AnalysisResult[] = [
      createMockAnalysisResult({ id: '1', analysis_name: 'Ocean Freight Analysis' }),
      createMockAnalysisResult({ id: '2', analysis_name: 'Air Freight Analysis' })
    ];

    (getRecentAnalysisResults as Mock).mockResolvedValue({ success: true, data: mockAnalysisResults });

    customRender(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Recent Price Changes')).toBeInTheDocument();
      expect(screen.getByText('Price Trend')).toBeInTheDocument();
      expect(screen.getByText('Saved Analyses')).toBeInTheDocument();
      expect(screen.getByText('Alerts')).toBeInTheDocument();
    });
  });

  it('fetches recent analysis results on mount', async () => {
    (getRecentAnalysisResults as Mock).mockResolvedValue({ success: true, data: [] });

    customRender(<DashboardPage />);

    await waitFor(() => {
      expect(getRecentAnalysisResults).toHaveBeenCalledTimes(1);
      expect(getRecentAnalysisResults).toHaveBeenCalledWith(7);
    });
  });

  it('adapts to mobile view', async () => {
    (getRecentAnalysisResults as Mock).mockResolvedValue({ success: true, data: [] });
    (useMediaQuery as Mock).mockImplementation(() => true); // Mock as mobile

    customRender(<DashboardPage />);

    await waitFor(() => {
      expect(useMediaQuery).toHaveBeenCalledWith('(max-width: 767px)');
    });
  });
});