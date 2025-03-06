import React from 'react';
import RecentPriceChanges from './RecentPriceChanges';
import { customRender, screen, waitFor } from '../../../utils/test-utils';
import { getRecentAnalysisResults } from '../../../api/analysis-api';
import { TrendDirection } from '../../../types/analysis.types';

// Mock the analysis API
jest.mock('../../../api/analysis-api');

/**
 * Creates mock analysis result data for testing
 */
const mockAnalysisResults = () => [
  {
    id: '1',
    analysis_id: 'a1',
    analysis_name: 'Ocean Freight Analysis',
    time_period_name: 'Last 7 days',
    start_date: '2023-06-01',
    end_date: '2023-06-07',
    percentage_change: 3.2,
    trend_direction: TrendDirection.INCREASING,
    calculated_at: '2023-06-08T00:00:00Z'
  },
  {
    id: '2',
    analysis_id: 'a2',
    analysis_name: 'Air Freight Analysis',
    time_period_name: 'Last 7 days',
    start_date: '2023-06-01',
    end_date: '2023-06-07',
    percentage_change: -1.5,
    trend_direction: TrendDirection.DECREASING,
    calculated_at: '2023-06-08T00:00:00Z'
  },
  {
    id: '3',
    analysis_id: 'a3',
    analysis_name: 'Road Freight Analysis',
    time_period_name: 'Last 7 days',
    start_date: '2023-06-01',
    end_date: '2023-06-07',
    percentage_change: 0.8,
    trend_direction: TrendDirection.INCREASING,
    calculated_at: '2023-06-08T00:00:00Z'
  },
  {
    id: '4',
    analysis_id: 'a4',
    analysis_name: 'Rail Freight Analysis',
    time_period_name: 'Last 7 days',
    start_date: '2023-06-01',
    end_date: '2023-06-07',
    percentage_change: 0.2,
    trend_direction: TrendDirection.STABLE,
    calculated_at: '2023-06-08T00:00:00Z'
  }
];

describe('RecentPriceChanges', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    // Mock getRecentAnalysisResults to return a pending promise
    (getRecentAnalysisResults as jest.Mock).mockReturnValue(new Promise(() => {}));
    
    customRender(<RecentPriceChanges />);
    
    expect(screen.getByText('Loading price changes...')).toBeInTheDocument();
  });

  test('renders error state when API call fails', async () => {
    // Mock getRecentAnalysisResults to reject with an error
    (getRecentAnalysisResults as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    customRender(<RecentPriceChanges />);
    
    await waitFor(() => {
      expect(screen.getByText('Unable to load recent price changes. Please try again later.')).toBeInTheDocument();
    });
  });

  test('renders price changes correctly', async () => {
    // Create mock analysis results with different freight modes and trends
    const mockResults = mockAnalysisResults();
    
    // Mock getRecentAnalysisResults to resolve with the mock data
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({ 
      success: true, 
      data: mockResults, 
      error: null, 
      meta: null 
    });
    
    customRender(<RecentPriceChanges />);
    
    await waitFor(() => {
      // Verify that each freight mode is displayed
      expect(screen.getByText('Ocean:')).toBeInTheDocument();
      expect(screen.getByText('Air:')).toBeInTheDocument();
      expect(screen.getByText('Road:')).toBeInTheDocument();
      expect(screen.getByText('Rail:')).toBeInTheDocument();
      
      // Verify that percentage changes are displayed correctly
      expect(screen.getByText('+3.2%')).toBeInTheDocument();
      expect(screen.getByText('-1.5%')).toBeInTheDocument();
      expect(screen.getByText('+0.8%')).toBeInTheDocument();
      expect(screen.getByText('+0.2%')).toBeInTheDocument();
      
      // Trend indicators are rendered by TrendIndicator component
      // which would be tested separately
    });
  });

  test('handles empty results', async () => {
    // Mock getRecentAnalysisResults to resolve with an empty array
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({ 
      success: true, 
      data: [], 
      error: null, 
      meta: null 
    });
    
    customRender(<RecentPriceChanges />);
    
    await waitFor(() => {
      expect(screen.getByText('No recent price changes available.')).toBeInTheDocument();
    });
  });

  test('calls onViewDetails when button is clicked', async () => {
    // Create a mock function for onViewDetails
    const mockOnViewDetails = jest.fn();
    
    // Mock getRecentAnalysisResults to resolve with mock data
    const mockResults = mockAnalysisResults();
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({ 
      success: true, 
      data: mockResults, 
      error: null, 
      meta: null 
    });
    
    customRender(<RecentPriceChanges onViewDetails={mockOnViewDetails} />);
    
    await waitFor(() => {
      expect(screen.getByText('Ocean:')).toBeInTheDocument();
    });
    
    // Find and click the View Details button
    const viewDetailsButton = screen.getByText('View Details');
    viewDetailsButton.click();
    
    // Verify that the onViewDetails function was called
    expect(mockOnViewDetails).toHaveBeenCalledTimes(1);
  });
});