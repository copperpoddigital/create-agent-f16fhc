import React, { useRef, useEffect, useState, useMemo } from 'react';
import { Chart, ChartOptions } from 'chart.js'; // v4.3.0
import { Bar } from 'react-chartjs-2'; // v5.2.0

import { 
  createComparisonChartData, 
  getChartOptions, 
  getResponsiveChartDimensions, 
  applyChartTheme,
  destroyChart
} from '../../../utils/chart-utils';
import { BAR_CHART_CONFIG } from '../../../config/chart-config';
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
 * Props interface for the BarChart component
 */
interface BarChartProps {
  /** Array of primary time series data points with timestamp and value */
  data: TimeSeriesDataPoint[];
  /** Optional array of comparison time series data points */
  comparisonData?: TimeSeriesDataPoint[];
  /** Optional custom labels for the x-axis */
  labels?: string[];
  /** Chart title */
  title?: string;
  /** Label for the x-axis */
  xAxisLabel?: string;
  /** Label for the y-axis */
  yAxisLabel?: string;
  /** Currency code for formatting price values */
  currencyCode?: string;
  /** Label for the primary data series */
  primaryLabel?: string;
  /** Label for the comparison data series */
  comparisonLabel?: string;
  /** Direction of the trend for styling */
  trendDirection?: TrendDirection;
  /** Additional Chart.js options to override defaults */
  chartOptions?: ChartOptions<'bar'>;
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
 * A component that renders a bar chart for visualizing and comparing freight price data.
 * Uses Chart.js to create responsive, interactive bar charts with customizable styling.
 * 
 * @param props Component props
 * @returns A responsive bar chart component
 */
const BarChart: React.FC<BarChartProps> = ({
  data,
  comparisonData,
  labels,
  title,
  xAxisLabel = 'Category',
  yAxisLabel = 'Price',
  currencyCode = 'USD',
  primaryLabel = 'Current Period',
  comparisonLabel = 'Previous Period',
  trendDirection,
  chartOptions = {},
  className,
  responsive = true,
  height,
  width,
  testId = 'bar-chart'
}) => {
  // Create refs for DOM elements and chart instance
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<Chart<'bar'> | null>(null);
  
  // Get current theme (light/dark) from theme context
  const { theme } = useTheme();
  
  // Set initial dimensions, will be updated for responsive mode
  const [dimensions, setDimensions] = useState({
    width: width || 600,
    height: height || 400
  });
  
  // Use media query hook to detect screen size changes
  const isMobile = useMediaQuery('(max-width: 767px)');
  
  // Create memoized chart data structure from time series data
  const chartData = useMemo(() => {
    return createComparisonChartData(
      data,
      comparisonData,
      labels,
      {
        label: primaryLabel,
        comparisonLabel
      }
    );
  }, [data, comparisonData, labels, primaryLabel, comparisonLabel]);
  
  // Create memoized chart options by combining defaults with custom options
  const mergedOptions = useMemo(() => {
    // Start with base options from config
    let options = getChartOptions<'bar'>(
      BAR_CHART_CONFIG.options,
      {
        ...chartOptions,
        responsive,
        maintainAspectRatio: !responsive,
        plugins: {
          ...BAR_CHART_CONFIG.options.plugins,
          ...chartOptions.plugins,
          title: {
            ...BAR_CHART_CONFIG.options.plugins?.title,
            ...chartOptions.plugins?.title,
            display: !!title,
            text: title || 'Price Comparison'
          }
        },
        scales: {
          ...BAR_CHART_CONFIG.options.scales,
          ...chartOptions.scales,
          x: {
            ...BAR_CHART_CONFIG.options.scales?.x,
            ...chartOptions.scales?.x,
            title: {
              ...BAR_CHART_CONFIG.options.scales?.x?.title,
              ...chartOptions.scales?.x?.title,
              display: !!xAxisLabel,
              text: xAxisLabel
            }
          },
          y: {
            ...BAR_CHART_CONFIG.options.scales?.y,
            ...chartOptions.scales?.y,
            title: {
              ...BAR_CHART_CONFIG.options.scales?.y?.title,
              ...chartOptions.scales?.y?.title,
              display: !!yAxisLabel,
              text: yAxisLabel
            },
            ticks: {
              ...BAR_CHART_CONFIG.options.scales?.y?.ticks,
              ...chartOptions.scales?.y?.ticks,
              callback: function(value) {
                // Format currency values appropriately
                return currencyCode ? 
                  new Intl.NumberFormat('en-US', { 
                    style: 'currency', 
                    currency: currencyCode
                  }).format(value as number) : 
                  value;
              }
            }
          }
        }
      },
      trendDirection
    );
    
    // Apply theme-specific styling (light/dark mode)
    options = applyChartTheme<'bar'>(options, theme);
    
    return options;
  }, [chartOptions, title, xAxisLabel, yAxisLabel, currencyCode, trendDirection, theme, responsive]);
  
  // Effect for handling responsive sizing
  useEffect(() => {
    if (!responsive) {
      // If not responsive, use provided dimensions or defaults
      setDimensions({
        width: width || 600,
        height: height || 400
      });
      return;
    }
    
    // Function to update dimensions based on container width
    const updateDimensions = () => {
      if (chartContainerRef.current) {
        const containerWidth = chartContainerRef.current.clientWidth;
        const responsiveDimensions = getResponsiveChartDimensions(containerWidth);
        setDimensions(responsiveDimensions);
      }
    };
    
    // Initial dimensions calculation
    updateDimensions();
    
    // Set up resize listener for responsive mode
    window.addEventListener('resize', updateDimensions);
    
    // Clean up resize listener on unmount
    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, [responsive, width, height]);
  
  // Clean up chart instance on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (chartRef.current) {
        destroyChart(chartRef.current);
        chartRef.current = null;
      }
    };
  }, []);
  
  // Render the bar chart or a "no data" message if data is empty
  return (
    <div 
      ref={chartContainerRef}
      className={`bar-chart-container ${className || ''}`}
      data-testid={testId}
      style={{ width: '100%' }}
    >
      {data && data.length > 0 ? (
        <div style={responsive ? { width: '100%' } : { width: dimensions.width, height: dimensions.height }}>
          <Bar
            data={chartData}
            options={mergedOptions}
            ref={chartRef}
            width={responsive ? undefined : dimensions.width}
            height={responsive ? undefined : dimensions.height}
          />
        </div>
      ) : (
        <div className="no-data-message">
          No data available for visualization
        </div>
      )}
    </div>
  );
};

export default BarChart;