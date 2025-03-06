/**
 * LineChart.tsx
 *
 * A React component that renders a line chart for visualizing freight price movement data over time.
 * This component uses Chart.js to create responsive, interactive time series visualizations with
 * customizable styling and behavior.
 *
 * This component implements requirements from:
 * - Technical Specifications/2.1 FEATURE CATALOG/2.1.4 Result Presentation
 * - Technical Specifications/6.3 PRESENTATION SERVICE/6.3.3 Visualization Types
 * - Technical Specifications/7.5 RESPONSIVE DESIGN
 * - Technical Specifications/7.8 COMPONENT LIBRARY/7.8.2 Data Visualization Components
 */

import React, { useRef, useEffect, useState, useMemo } from 'react';
import { Chart, ChartOptions } from 'chart.js'; // v4.3.0
import { Line } from 'react-chartjs-2'; // v5.2.0

import { 
  createTimeSeriesChartData, 
  getChartOptions, 
  getResponsiveChartDimensions, 
  applyChartTheme,
  destroyChart
} from '../../../utils/chart-utils';
import { LINE_CHART_CONFIG } from '../../../config/chart-config';
import useTheme from '../../../hooks/useTheme';
import useMediaQuery from '../../../hooks/useMediaQuery';
import { TrendDirection } from '../../../types';

/**
 * Interface for a single data point in a time series
 */
interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
}

/**
 * Props interface for the LineChart component
 */
interface LineChartProps {
  /** Array of time series data points with timestamp and value */
  data: TimeSeriesDataPoint[];
  /** Chart title */
  title?: string;
  /** Label for the x-axis */
  xAxisLabel?: string;
  /** Label for the y-axis */
  yAxisLabel?: string;
  /** Currency code for formatting price values */
  currencyCode?: string;
  /** Direction of the trend for styling */
  trendDirection?: TrendDirection;
  /** Additional Chart.js options to override defaults */
  chartOptions?: ChartOptions<'line'>;
  /** Additional CSS class names */
  className?: string;
  /** Whether the chart should be responsive */
  responsive?: boolean;
  /** Fixed height for the chart (overrides responsive) */
  height?: number;
  /** Fixed width for the chart (overrides responsive) */
  width?: number;
  /** Test ID for automated testing */
  testId?: string;
}

/**
 * A component that renders a line chart for visualizing freight price movement data over time.
 * It supports responsive sizing, theme-based styling, and customization via props.
 */
const LineChart: React.FC<LineChartProps> = ({
  data = [],
  title,
  xAxisLabel = 'Time',
  yAxisLabel = 'Price',
  currencyCode = 'USD',
  trendDirection,
  chartOptions = {},
  className = '',
  responsive = true,
  height,
  width,
  testId = 'line-chart'
}) => {
  // Create refs for chart container and instance
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<Chart | null>(null);
  
  // Get current theme
  const { theme } = useTheme();
  
  // Set up state for chart dimensions
  const [dimensions, setDimensions] = useState<{ width: number; height: number }>({
    width: width || 600,
    height: height || 400
  });
  
  // Use media query hook to detect screen size changes
  const isMobile = useMediaQuery('(max-width: 767px)');
  const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 991px)');
  const isLaptop = useMediaQuery('(min-width: 992px) and (max-width: 1199px)');
  
  // Create memoized chart data with appropriate styling based on trend direction
  const chartData = useMemo(() => {
    return createTimeSeriesChartData(data, {
      label: title || 'Freight Price',
      // Let chart-utils handle the color based on trend direction if provided
    });
  }, [data, title]);
  
  // Create memoized chart options with appropriate styling and configuration
  const options = useMemo(() => {
    // Start with the base config for line charts
    const baseOptions = { ...LINE_CHART_CONFIG.options };
    
    // Update titles and labels
    if (baseOptions.plugins && baseOptions.plugins.title) {
      baseOptions.plugins.title.text = title || 'Freight Price Movement';
    }
    
    // Configure axes
    if (baseOptions.scales) {
      // X-axis configuration
      if (baseOptions.scales.x) {
        baseOptions.scales.x.title = { display: true, text: xAxisLabel };
      }
      
      // Y-axis configuration with currency formatting
      if (baseOptions.scales.y) {
        baseOptions.scales.y.title = { display: true, text: yAxisLabel };
        if (baseOptions.scales.y.ticks) {
          baseOptions.scales.y.ticks.callback = (value) => {
            return new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: currencyCode,
              minimumFractionDigits: 0
            }).format(value as number);
          };
        }
      }
    }
    
    // Merge base options with custom options provided via props
    let mergedOptions = getChartOptions<'line'>(baseOptions, chartOptions, trendDirection);
    
    // Apply theme-specific styling (light/dark mode)
    mergedOptions = applyChartTheme(mergedOptions, theme);
    
    // Apply fixed dimensions if provided (overrides responsive behavior)
    if (!responsive && (width || height)) {
      mergedOptions.responsive = false;
      mergedOptions.maintainAspectRatio = false;
    }
    
    return mergedOptions;
  }, [title, xAxisLabel, yAxisLabel, currencyCode, chartOptions, trendDirection, theme, responsive, width, height]);
  
  // Handle responsive resizing when container width changes
  useEffect(() => {
    if (!responsive || !containerRef.current) {
      return;
    }
    
    // Function to calculate and update dimensions based on container width
    const handleResize = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        const newDimensions = getResponsiveChartDimensions(containerWidth);
        setDimensions(newDimensions);
      }
    };
    
    // Initial calculation
    handleResize();
    
    // Set up resize listener
    window.addEventListener('resize', handleResize);
    
    // Clean up
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [responsive, isMobile, isTablet, isLaptop]);
  
  // Clean up chart instance on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      destroyChart(chartRef.current);
    };
  }, []);
  
  // If no data is available, display a message instead of an empty chart
  if (!data || data.length === 0) {
    return (
      <div 
        className={`line-chart-container empty ${className}`}
        ref={containerRef}
        data-testid={`${testId}-empty`}
        style={{ 
          height: dimensions.height, 
          width: dimensions.width,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: '1px solid #E0E0E0',
          borderRadius: '4px',
          padding: '20px'
        }}
      >
        <p>No data available for visualization</p>
      </div>
    );
  }
  
  // Render the chart with the calculated dimensions and options
  return (
    <div 
      className={`line-chart-container ${className}`}
      ref={containerRef}
      data-testid={testId}
      style={{ 
        height: dimensions.height, 
        width: dimensions.width 
      }}
    >
      <Line
        data={chartData}
        options={options}
        // Get chart instance reference for potential usage and cleanup
        ref={(reference) => {
          if (reference) {
            // Access chart instance when available
            chartRef.current = reference.chart;
          }
        }}
      />
    </div>
  );
};

export default LineChart;