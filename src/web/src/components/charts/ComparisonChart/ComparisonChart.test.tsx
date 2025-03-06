import React from 'react';
import { render, cleanup } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import { Chart } from 'chart.js';
import ComparisonChart from './ComparisonChart';
import { renderWithTheme, screen, waitFor } from '../../../utils/test-utils';
import { TrendDirection } from '../../../types';

// Helper function to create mock time series data
function createMockTimeSeriesData(count: number, startValue: number, increment: number) {
  const data = [];
  const now = new Date();
  for (let i = 0; i < count; i++) {
    const timestamp = new Date(now);
    timestamp.setDate(now.getDate() - i);
    data.push({
      timestamp: timestamp.toISOString(),
      value: startValue + (increment * i)
    });
  }
  return data;
}

describe('ComparisonChart', () => {
  afterEach(cleanup);

  it('renders without crashing', () => {
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    renderWithTheme(<ComparisonChart primaryData={primaryData} />);
    expect(screen.getByTestId('comparison-chart')).toBeInTheDocument();
  });

  it('renders with primary data only', () => {
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    renderWithTheme(
      <ComparisonChart 
        primaryData={primaryData} 
        title="Test Chart" 
      />
    );
    
    // Check component is rendered with the right aria-label
    expect(screen.getByTestId('comparison-chart')).toHaveAttribute('aria-label', 'Test Chart');
    
    // Chart container should be present for non-empty data
    expect(screen.getByTestId('comparison-chart').querySelector('.comparison-chart__container')).toBeInTheDocument();
  });

  it('renders with primary and comparison data', () => {
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    const comparisonData = createMockTimeSeriesData(5, 900, 90);
    
    renderWithTheme(
      <ComparisonChart 
        primaryData={primaryData} 
        comparisonData={comparisonData}
        title="Comparison Test" 
      />
    );
    
    // Chart container should be present
    expect(screen.getByTestId('comparison-chart').querySelector('.comparison-chart__container')).toBeInTheDocument();
  });

  it('displays trend indicator when trend direction and percentage change are provided', () => {
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    
    renderWithTheme(
      <ComparisonChart 
        primaryData={primaryData}
        trendDirection={TrendDirection.INCREASING}
        percentageChange={5.2}
      />
    );
    
    // Trend indicator should be present
    expect(screen.getByTestId('trend-indicator')).toBeInTheDocument();
    
    // Should display percentage change
    expect(screen.getByTestId('trend-indicator').textContent).toContain('5.2');
  });

  it('does not display trend indicator when trend data is missing', () => {
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    
    renderWithTheme(
      <ComparisonChart 
        primaryData={primaryData}
      />
    );
    
    // Trend indicator should not be present
    expect(screen.queryByTestId('trend-indicator')).not.toBeInTheDocument();
  });

  it('applies custom class name when provided', () => {
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    
    renderWithTheme(
      <ComparisonChart 
        primaryData={primaryData}
        className="custom-class"
      />
    );
    
    // Custom class should be applied
    expect(screen.getByTestId('comparison-chart')).toHaveClass('custom-class');
  });

  it('displays "No data available" message when data is empty', () => {
    renderWithTheme(
      <ComparisonChart 
        primaryData={[]}
      />
    );
    
    // No data message should be displayed
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });

  it('applies responsive dimensions when responsive prop is true', async () => {
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    
    // Mock getBoundingClientRect to return a fixed size
    Element.prototype.getBoundingClientRect = jest.fn().mockReturnValue({
      width: 800,
      height: 400
    });
    
    renderWithTheme(
      <ComparisonChart 
        primaryData={primaryData}
        responsive={true}
      />
    );
    
    // Chart container should have responsive width
    const container = screen.getByTestId('comparison-chart').querySelector('.comparison-chart__container');
    expect(container).toHaveStyle('width: 100%');
  });

  it('applies fixed dimensions when height and width props are provided', () => {
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    
    renderWithTheme(
      <ComparisonChart 
        primaryData={primaryData}
        height={300}
        width={500}
        responsive={false}
      />
    );
    
    // Chart container should have fixed dimensions
    const container = screen.getByTestId('comparison-chart').querySelector('.comparison-chart__container');
    expect(container).toHaveStyle('width: 500px');
    expect(container).toHaveStyle('height: 300px');
  });

  it('cleans up chart instance on unmount', () => {
    // Mock the destroyChart function
    const originalDestroy = Chart.prototype.destroy;
    Chart.prototype.destroy = jest.fn();
    
    const primaryData = createMockTimeSeriesData(5, 1000, 100);
    
    const { unmount } = renderWithTheme(
      <ComparisonChart 
        primaryData={primaryData}
      />
    );
    
    // Unmount component
    unmount();
    
    // Restore original function after test
    Chart.prototype.destroy = originalDestroy;
  });
});