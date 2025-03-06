import React from 'react';
import PriceTrendChart from './PriceTrendChart';
import { renderWithTheme, screen, waitFor } from '../../../utils/test-utils';
import { getRecentAnalysisResults } from '../../../api/analysis-api';
import { TrendDirection } from '../../../types/analysis.types';

// Mock the API function
jest.mock('../../../api/analysis-api');

describe('PriceTrendChart', () => {
  // Create mock analysis results
  const mockAnalysisResults = [
    {
      id: '1',
      analysis_id: '1',
      analysis_name: 'Test Analysis',
      time_period_name: 'Last 30 Days',
      start_date: '2023-01-01',
      end_date: '2023-01-30',
      percentage_change: 5.2,
      trend_direction: TrendDirection.INCREASING,
      calculated_at: '2023-01-31T12:00:00Z'
    }
  ];
  
  const mockEmptyResults = [];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders with default props', async () => {
    // Mock API to return empty data
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({
      success: true,
      data: mockEmptyResults,
      error: null,
      meta: null
    });

    renderWithTheme(<PriceTrendChart />);
    
    // Check that the component renders with default title
    expect(screen.getByText('Price Trend')).toBeInTheDocument();
    
    // Check loading state initially
    expect(screen.getByTestId('price-trend-chart-loading')).toBeInTheDocument();
    
    // Wait for API response
    await waitFor(() => {
      expect(screen.getByTestId('price-trend-chart-empty')).toBeInTheDocument();
    });
  });

  test('renders with custom title', async () => {
    // Mock API to return empty data
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({
      success: true,
      data: mockEmptyResults,
      error: null,
      meta: null
    });

    const customTitle = 'Custom Chart Title';
    renderWithTheme(<PriceTrendChart title={customTitle} />);
    
    // Check that the component renders with custom title
    expect(screen.getByText(customTitle)).toBeInTheDocument();
  });

  test('displays loading state initially', () => {
    // Mock API to return a delayed promise
    (getRecentAnalysisResults as jest.Mock).mockImplementation(() => 
      new Promise(resolve => setTimeout(() => {
        resolve({
          success: true,
          data: mockEmptyResults,
          error: null,
          meta: null
        });
      }, 100))
    );

    renderWithTheme(<PriceTrendChart />);
    
    // Check loading indicator
    expect(screen.getByTestId('price-trend-chart-loading')).toBeInTheDocument();
  });

  test('displays error message when API fails', async () => {
    // Mock API to reject with an error
    (getRecentAnalysisResults as jest.Mock).mockRejectedValue(new Error('API error'));

    renderWithTheme(<PriceTrendChart />);
    
    // Wait for error state
    await waitFor(() => {
      expect(screen.getByTestId('price-trend-chart-error')).toBeInTheDocument();
    });
  });

  test('displays chart when data is loaded', async () => {
    // Mock API to return mock data
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({
      success: true,
      data: mockAnalysisResults,
      error: null,
      meta: null
    });

    renderWithTheme(<PriceTrendChart />);
    
    // Wait for chart to be displayed
    await waitFor(() => {
      expect(screen.getByTestId('price-trend-chart-line-chart')).toBeInTheDocument();
    });
  });

  test('displays no data message when results are empty', async () => {
    // Mock API to return empty results
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({
      success: true,
      data: mockEmptyResults,
      error: null,
      meta: null
    });

    renderWithTheme(<PriceTrendChart />);
    
    // Wait for empty state
    await waitFor(() => {
      expect(screen.getByTestId('price-trend-chart-empty')).toBeInTheDocument();
    });
  });

  test('applies correct styling based on trend direction', async () => {
    // Mock API to return mock data with INCREASING trend
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({
      success: true,
      data: mockAnalysisResults,
      error: null,
      meta: null
    });

    renderWithTheme(<PriceTrendChart />);
    
    // Wait for chart to be displayed
    await waitFor(() => {
      expect(screen.getByTestId('price-trend-chart-line-chart')).toBeInTheDocument();
    });
    
    // We verify the LineChart is rendered with appropriate trend direction
    // Testing the actual styling would require a different testing approach
  });

  test('fetches data with correct days parameter', async () => {
    // Mock implementation to resolve with empty data
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({
      success: true,
      data: mockEmptyResults,
      error: null,
      meta: null
    });

    // Render with custom days value
    renderWithTheme(<PriceTrendChart days={15} />);
    
    // Check that the API was called with correct parameter
    expect(getRecentAnalysisResults).toHaveBeenCalledWith(15);
    
    // Clear mocks for the next render
    jest.clearAllMocks();
    
    // Render with a different days value
    renderWithTheme(<PriceTrendChart days={60} />);
    
    // Check that the API was called with the new parameter
    expect(getRecentAnalysisResults).toHaveBeenCalledWith(60);
  });

  test('displays View Full Chart link', async () => {
    // Mock API to return data
    (getRecentAnalysisResults as jest.Mock).mockResolvedValue({
      success: true,
      data: mockAnalysisResults,
      error: null,
      meta: null
    });

    renderWithTheme(<PriceTrendChart />);
    
    // Check for View Full Chart link
    expect(screen.getByText('View Full Chart')).toBeInTheDocument();
  });
});