import React from 'react';
import { waitFor } from '@testing-library/react';
import { Chart } from 'chart.js';
import LineChart from './LineChart';
import { renderWithTheme, screen } from '../../../utils/test-utils';
import { TrendDirection } from '../../../types';

// Mock chart-utils
jest.mock('../../../utils/chart-utils', () => ({
  createTimeSeriesChartData: jest.fn().mockReturnValue({ datasets: [], labels: [] }),
  getChartOptions: jest.fn().mockReturnValue({}),
  getResponsiveChartDimensions: jest.fn().mockReturnValue({ width: 800, height: 400 }),
  applyChartTheme: jest.fn(options => options),
  destroyChart: jest.fn()
}));

describe('LineChart', () => {
  // Test data
  const mockData = [
    { timestamp: '2023-01-01T00:00:00Z', value: 4000 },
    { timestamp: '2023-01-08T00:00:00Z', value: 4050 },
    { timestamp: '2023-01-15T00:00:00Z', value: 4100 },
    { timestamp: '2023-01-22T00:00:00Z', value: 4150 },
    { timestamp: '2023-01-29T00:00:00Z', value: 4200 }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should render with minimal props', () => {
    renderWithTheme(<LineChart data={mockData} />);
    
    const container = screen.getByTestId('line-chart');
    expect(container).toBeInTheDocument();
    expect(container.querySelector('canvas')).toBeInTheDocument();
  });

  it('should display a message when data is empty', () => {
    renderWithTheme(<LineChart data={[]} />);
    
    const emptyContainer = screen.getByTestId('line-chart-empty');
    expect(emptyContainer).toBeInTheDocument();
    expect(emptyContainer).toHaveTextContent('No data available for visualization');
  });

  it('should apply custom className', () => {
    const customClass = 'custom-chart-class';
    renderWithTheme(<LineChart data={mockData} className={customClass} />);
    
    const container = screen.getByTestId('line-chart');
    expect(container).toHaveClass(customClass);
  });

  it('should apply trend direction styling', () => {
    const { getChartOptions } = require('../../../utils/chart-utils');
    
    renderWithTheme(<LineChart data={mockData} trendDirection={TrendDirection.INCREASING} />);
    
    expect(getChartOptions).toHaveBeenCalledWith(
      expect.any(Object),
      expect.any(Object),
      TrendDirection.INCREASING
    );
    
    // Test with different trend direction
    jest.clearAllMocks();
    renderWithTheme(<LineChart data={mockData} trendDirection={TrendDirection.DECREASING} />);
    
    expect(getChartOptions).toHaveBeenCalledWith(
      expect.any(Object),
      expect.any(Object),
      TrendDirection.DECREASING
    );
  });

  it('should be responsive by default', () => {
    const { getResponsiveChartDimensions } = require('../../../utils/chart-utils');
    
    renderWithTheme(<LineChart data={mockData} />);
    
    expect(getResponsiveChartDimensions).toHaveBeenCalled();
  });

  it('should use fixed dimensions when provided', () => {
    const { getResponsiveChartDimensions } = require('../../../utils/chart-utils');
    
    const width = 500;
    const height = 300;
    renderWithTheme(<LineChart data={mockData} width={width} height={height} responsive={false} />);
    
    expect(getResponsiveChartDimensions).not.toHaveBeenCalled();
    
    const container = screen.getByTestId('line-chart');
    expect(container.style.width).toBe(`${width}px`);
    expect(container.style.height).toBe(`${height}px`);
  });

  it('should clean up chart instance on unmount', () => {
    const { destroyChart } = require('../../../utils/chart-utils');
    
    const { unmount } = renderWithTheme(<LineChart data={mockData} />);
    unmount();
    
    expect(destroyChart).toHaveBeenCalled();
  });

  it('should apply theme-specific styling', () => {
    const { applyChartTheme } = require('../../../utils/chart-utils');
    
    renderWithTheme(<LineChart data={mockData} />, 'light');
    
    expect(applyChartTheme).toHaveBeenCalledWith(expect.any(Object), 'light');
    
    jest.clearAllMocks();
    renderWithTheme(<LineChart data={mockData} />, 'dark');
    
    expect(applyChartTheme).toHaveBeenCalledWith(expect.any(Object), 'dark');
  });
});