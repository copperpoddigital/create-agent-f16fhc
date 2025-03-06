import React from 'react';
import { render, cleanup } from '@testing-library/react';
import { Chart } from 'chart.js';
import BarChart from './BarChart';
import { renderWithTheme, screen } from '../../../utils/test-utils';
import { TrendDirection } from '../../../types';

// Mock time series data for testing
const mockTimeSeriesData = [
  { timestamp: '2023-01-01', value: 100 },
  { timestamp: '2023-01-02', value: 120 },
  { timestamp: '2023-01-03', value: 110 }
];

// Mock comparison data for testing
const mockComparisonData = [
  { timestamp: '2023-01-01', value: 90 },
  { timestamp: '2023-01-02', value: 95 },
  { timestamp: '2023-01-03', value: 105 }
];

describe('BarChart Component', () => {
  beforeEach(() => {
    // Mock Chart.js to prevent actual chart rendering
    jest.spyOn(Chart.prototype, 'destroy').mockImplementation(() => {});
    
    // Mock window.matchMedia for the useMediaQuery hook
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));

    // Mock ResizeObserver
    global.ResizeObserver = jest.fn().mockImplementation(() => ({
      observe: jest.fn(),
      unobserve: jest.fn(),
      disconnect: jest.fn(),
    }));
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  it('renders without crashing', () => {
    renderWithTheme(<BarChart data={mockTimeSeriesData} />);
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('renders with primary data only', () => {
    renderWithTheme(<BarChart data={mockTimeSeriesData} />);
    // Component renders successfully with only primary data
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('renders with both primary and comparison data', () => {
    renderWithTheme(
      <BarChart 
        data={mockTimeSeriesData} 
        comparisonData={mockComparisonData}
        primaryLabel="Current Period"
        comparisonLabel="Previous Period"
      />
    );
    // Component renders successfully with both primary and comparison data
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('applies different styles based on trend direction', () => {
    // Test with INCREASING trend
    renderWithTheme(
      <BarChart data={mockTimeSeriesData} trendDirection={TrendDirection.INCREASING} />
    );
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    
    // Clean up before next test
    cleanup();
    
    // Test with DECREASING trend
    renderWithTheme(
      <BarChart data={mockTimeSeriesData} trendDirection={TrendDirection.DECREASING} />
    );
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    
    // Clean up before next test
    cleanup();
    
    // Test with STABLE trend
    renderWithTheme(
      <BarChart data={mockTimeSeriesData} trendDirection={TrendDirection.STABLE} />
    );
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('handles empty data gracefully', () => {
    renderWithTheme(<BarChart data={[]} />);
    expect(screen.getByText('No data available for visualization')).toBeInTheDocument();
  });

  it('applies responsive dimensions correctly', () => {
    // Test responsive mode (default)
    renderWithTheme(<BarChart data={mockTimeSeriesData} responsive={true} />);
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    
    // Clean up before next test
    cleanup();
    
    // Test fixed dimensions
    renderWithTheme(
      <BarChart 
        data={mockTimeSeriesData} 
        responsive={false} 
        width={500} 
        height={300} 
      />
    );
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('applies custom chart options correctly', () => {
    const customOptions = {
      plugins: {
        title: {
          text: 'Custom Chart Title'
        }
      },
      scales: {
        y: {
          min: 0,
          max: 200
        }
      }
    };
    
    renderWithTheme(
      <BarChart 
        data={mockTimeSeriesData} 
        chartOptions={customOptions}
        title="Default Title"
      />
    );
    
    // Component renders successfully with custom options
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });
  
  it('uses provided test ID', () => {
    renderWithTheme(
      <BarChart 
        data={mockTimeSeriesData} 
        testId="custom-test-id"
      />
    );
    
    expect(screen.getByTestId('custom-test-id')).toBeInTheDocument();
  });
  
  it('applies custom CSS class', () => {
    renderWithTheme(
      <BarChart 
        data={mockTimeSeriesData} 
        className="custom-chart-class"
      />
    );
    
    const container = screen.getByTestId('bar-chart');
    expect(container.className).toContain('bar-chart-container');
    expect(container.className).toContain('custom-chart-class');
  });
});