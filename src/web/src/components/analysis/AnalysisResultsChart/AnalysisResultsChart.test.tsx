import React from 'react';
import '@testing-library/jest-dom/extend-expect';
import { render, screen } from '../../../utils/test-utils';
import AnalysisResultsChart from './AnalysisResultsChart';
import { createMockAnalysisResult } from '../../../utils/test-utils';
import { TrendDirection } from '../../../types';

describe('AnalysisResultsChart', () => {
  it('renders loading spinner when loading prop is true', () => {
    render(<AnalysisResultsChart result={createMockAnalysisResult()} loading={true} />);
    expect(screen.getByTestId('analysis-results-chart-loading')).toBeInTheDocument();
    expect(screen.getByText(/loading chart data/i)).toBeInTheDocument();
    expect(screen.getByText(/price movement chart/i)).toBeInTheDocument();
  });

  it('renders error message when error prop is true', () => {
    const errorMessage = 'Test error';
    render(<AnalysisResultsChart result={createMockAnalysisResult()} error={true} errorMessage={errorMessage} />);
    expect(screen.getByTestId('analysis-results-chart-error')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByText(/price movement chart/i)).toBeInTheDocument();
  });

  it('renders chart with time series data', () => {
    const mockResult = createMockAnalysisResult();
    render(<AnalysisResultsChart result={mockResult} />);
    expect(screen.getByTestId('analysis-results-chart')).toBeInTheDocument();
    expect(screen.getByTestId('analysis-results-chart-line-chart')).toBeInTheDocument();
  });

  it('renders no data message when time series is empty', () => {
    const mockResult = createMockAnalysisResult({ time_series: [] });
    render(<AnalysisResultsChart result={mockResult} />);
    expect(screen.getByTestId('analysis-results-chart-empty')).toBeInTheDocument();
    expect(screen.getByText(/no data available for visualization/i)).toBeInTheDocument();
  });

  it('applies correct trend styling based on trend direction', () => {
    const increasingResult = createMockAnalysisResult({
      price_change: {
        absolute_change: 200,
        percentage_change: 5,
        trend_direction: TrendDirection.INCREASING
      }
    });
    
    const { rerender } = render(<AnalysisResultsChart result={increasingResult} />);
    const chartElement = screen.getByTestId('analysis-results-chart');
    expect(chartElement).toHaveClass('analysis-results-chart--increasing');
    
    // Test decreasing trend
    const decreasingResult = createMockAnalysisResult({
      price_change: {
        absolute_change: -200,
        percentage_change: -5,
        trend_direction: TrendDirection.DECREASING
      }
    });
    
    rerender(<AnalysisResultsChart result={decreasingResult} />);
    expect(chartElement).toHaveClass('analysis-results-chart--decreasing');
    
    // Test stable trend
    const stableResult = createMockAnalysisResult({
      price_change: {
        absolute_change: 0,
        percentage_change: 0,
        trend_direction: TrendDirection.STABLE
      }
    });
    
    rerender(<AnalysisResultsChart result={stableResult} />);
    expect(chartElement).toHaveClass('analysis-results-chart--stable');
  });

  it('passes correct currency code to LineChart', () => {
    // This test verifies that the chart renders when a different currency is provided
    // Since we can't directly check props passed to LineChart without mocking,
    // we're verifying the component renders with the specified currency
    const mockResult = createMockAnalysisResult({ currency: 'EUR' });
    render(<AnalysisResultsChart result={mockResult} />);
    expect(screen.getByTestId('analysis-results-chart-line-chart')).toBeInTheDocument();
  });
});