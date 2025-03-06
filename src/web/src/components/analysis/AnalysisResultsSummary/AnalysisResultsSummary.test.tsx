import React from 'react';
import { screen, render, createMockAnalysisResult } from '../../../utils/test-utils';
import AnalysisResultsSummary from './AnalysisResultsSummary';
import { TrendDirection } from '../../../types';

describe('AnalysisResultsSummary', () => {
  let mockResult;

  beforeEach(() => {
    // Create a common mock result for tests
    mockResult = createMockAnalysisResult();
  });

  it('renders the component with all information', () => {
    render(<AnalysisResultsSummary result={mockResult} />);

    // Check time period information is displayed
    expect(screen.getByText('Time Period:')).toBeInTheDocument();
    
    // Check data sources information is displayed
    expect(screen.getByText('Filters:')).toBeInTheDocument();
    
    // Check price change information is displayed
    expect(screen.getByText('Overall Change:')).toBeInTheDocument();
    expect(screen.getByText('Absolute Change:')).toBeInTheDocument();
    
    // Check starting and ending price
    expect(screen.getByText('Starting Price:')).toBeInTheDocument();
    expect(screen.getByText('$4,000.00')).toBeInTheDocument();
    expect(screen.getByText('Ending Price:')).toBeInTheDocument();
    expect(screen.getByText('$4,200.00')).toBeInTheDocument();
    
    // Check calculated at date is displayed
    expect(screen.getByText('Calculated At:')).toBeInTheDocument();
  });

  it('renders loading state correctly', () => {
    render(<AnalysisResultsSummary result={mockResult} isLoading={true} />);
    
    expect(screen.getByLabelText('Loading summary data')).toBeInTheDocument();
    expect(screen.getAllByClassName('skeleton-line').length).toBeGreaterThan(0);
  });

  it('hides time period when showTimePeriod is false', () => {
    render(<AnalysisResultsSummary result={mockResult} showTimePeriod={false} />);
    
    expect(screen.queryByText('Time Period:')).not.toBeInTheDocument();
  });

  it('hides data sources when showDataSources is false', () => {
    render(<AnalysisResultsSummary result={mockResult} showDataSources={false} />);
    
    expect(screen.queryByText('Filters:')).not.toBeInTheDocument();
  });

  it('hides calculated at date when showCalculatedAt is false', () => {
    render(<AnalysisResultsSummary result={mockResult} showCalculatedAt={false} />);
    
    expect(screen.queryByText('Calculated At:')).not.toBeInTheDocument();
  });

  it('displays increasing trend correctly', () => {
    const increasingResult = createMockAnalysisResult({
      price_change: {
        absolute_change: 200,
        percentage_change: 5,
        trend_direction: TrendDirection.INCREASING
      }
    });
    
    render(<AnalysisResultsSummary result={increasingResult} />);
    
    // Check for trend indicator
    const trendIndicator = screen.getByTestId('trend-indicator');
    expect(trendIndicator).toHaveClass('trend-indicator--increasing');
  });

  it('displays decreasing trend correctly', () => {
    const decreasingResult = createMockAnalysisResult({
      price_change: {
        absolute_change: -200,
        percentage_change: -5,
        trend_direction: TrendDirection.DECREASING
      }
    });
    
    render(<AnalysisResultsSummary result={decreasingResult} />);
    
    // Check for trend indicator
    const trendIndicator = screen.getByTestId('trend-indicator');
    expect(trendIndicator).toHaveClass('trend-indicator--decreasing');
  });

  it('displays stable trend correctly', () => {
    const stableResult = createMockAnalysisResult({
      price_change: {
        absolute_change: 10,
        percentage_change: 0.25,
        trend_direction: TrendDirection.STABLE
      }
    });
    
    render(<AnalysisResultsSummary result={stableResult} />);
    
    // Check for trend indicator
    const trendIndicator = screen.getByTestId('trend-indicator');
    expect(trendIndicator).toHaveClass('trend-indicator--stable');
  });

  it('formats currency values correctly', () => {
    const currencyResult = createMockAnalysisResult({
      start_value: 5000,
      end_value: 5500,
      currency: 'EUR',
      price_change: {
        absolute_change: 500,
        percentage_change: 10,
        trend_direction: TrendDirection.INCREASING
      }
    });
    
    render(<AnalysisResultsSummary result={currencyResult} />);
    
    // Check for correctly formatted currency values
    expect(screen.getByText('€5,000.00')).toBeInTheDocument();
    expect(screen.getByText('€5,500.00')).toBeInTheDocument();
    expect(screen.getByText('+€500.00')).toBeInTheDocument();
  });
});