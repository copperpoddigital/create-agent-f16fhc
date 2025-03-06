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
import TrendIndicator from '../TrendIndicator';

/**
 * Interface for a single data point in a time series
 */
interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
}

/**
 * Props interface for the ComparisonChart component
 */
interface ComparisonChartProps {
  primaryData: TimeSeriesDataPoint[];
  comparisonData?: TimeSeriesDataPoint[];
  labels?: string[];
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  primaryLabel?: string;
  comparisonLabel?: string;
  currencyCode?: string;
  trendDirection?: TrendDirection;
  percentageChange?: number;
  chartOptions?: ChartOptions<'bar'>;
  className?: string;
  responsive?: boolean;
  height?: number;
  width?: number;
  testId?: string;
}

/**
 * A component that renders a bar chart for comparing freight price data between two time periods
 */
const ComparisonChart: React.FC<ComparisonChartProps> = ({
  primaryData,
  comparisonData = [],
  labels,
  title,
  xAxisLabel = 'Period',
  yAxisLabel = 'Price',
  primaryLabel = 'Current Period',
  comparisonLabel = 'Previous Period',
  currencyCode = 'USD',
  trendDirection,
  percentageChange,
  chartOptions = {},
  className,
  responsive = true,
  height,
  width,
  testId = 'comparison-chart'
}) => {
  // Create refs for chart container and chart instance
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<Chart | null>(null);
  
  // Get current theme
  const { theme } = useTheme();
  
  // State for chart dimensions
  const [dimensions, setDimensions] = useState<{ width: number; height: number }>({
    width: width || 0,
    height: height || 0
  });
  
  // Use media query for responsive behavior
  const isMobile = useMediaQuery('(max-width: 768px)');
  
  // Create chart data with memoization
  const chartData = useMemo(() => {
    return createComparisonChartData(
      primaryData,
      comparisonData,
      labels,
      {
        label: primaryLabel,
        comparisonLabel: comparisonLabel
      }
    );
  }, [primaryData, comparisonData, labels, primaryLabel, comparisonLabel]);
  
  // Create chart options with memoization
  const mergedOptions = useMemo(() => {
    // Start with base options from config
    let baseOptions = getChartOptions<'bar'>(
      BAR_CHART_CONFIG.options,
      {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: !!title,
            text: title || 'Price Comparison'
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const value = context.parsed.y;
                return `${context.dataset.label}: ${currencyCode} ${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: !!xAxisLabel,
              text: xAxisLabel
            }
          },
          y: {
            title: {
              display: !!yAxisLabel,
              text: yAxisLabel
            },
            ticks: {
              callback: function(value) {
                return `${currencyCode} ${value.toLocaleString('en-US')}`;
              }
            }
          }
        }
      },
      trendDirection // Pass trend direction to style accordingly
    );
    
    // Apply theme-specific styling
    baseOptions = applyChartTheme(baseOptions, theme);
    
    // Merge with custom options
    return { ...baseOptions, ...chartOptions };
  }, [title, xAxisLabel, yAxisLabel, currencyCode, theme, trendDirection, chartOptions]);
  
  // Handle responsive dimensions
  useEffect(() => {
    if (!responsive || !containerRef.current) return;
    
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width: containerWidth } = containerRef.current.getBoundingClientRect();
        const newDimensions = getResponsiveChartDimensions(containerWidth);
        setDimensions(newDimensions);
      }
    };
    
    // Initial dimensions update
    updateDimensions();
    
    // Update dimensions on resize with debounce
    const resizeHandler = () => {
      updateDimensions();
    };
    
    window.addEventListener('resize', resizeHandler);
    
    // Clean up
    return () => {
      window.removeEventListener('resize', resizeHandler);
    };
  }, [responsive]);
  
  // Update dimensions when fixed width/height props change
  useEffect(() => {
    if (width && height && !responsive) {
      setDimensions({ width, height });
    }
  }, [width, height, responsive]);
  
  // Effect to initialize and update chart when data or options change
  useEffect(() => {
    if (!chartData.datasets.length) return;
    
    // Clean up existing chart
    if (chartRef.current) {
      destroyChart(chartRef.current);
      chartRef.current = null;
    }
    
    return () => {
      if (chartRef.current) {
        destroyChart(chartRef.current);
        chartRef.current = null;
      }
    };
  }, [chartData, mergedOptions]);
  
  return (
    <div 
      ref={containerRef}
      className={`comparison-chart ${className || ''}`}
      data-testid={testId}
      aria-label={title || "Price comparison chart"}
    >
      {primaryData.length > 0 ? (
        <>
          <div 
            className="comparison-chart__container"
            style={{ 
              width: dimensions.width || '100%', 
              height: dimensions.height || 300 
            }}
          >
            <Bar 
              data={chartData}
              options={mergedOptions}
              ref={(reference) => {
                if (reference) {
                  chartRef.current = reference.current;
                }
              }}
            />
          </div>
          
          {trendDirection !== undefined && percentageChange !== undefined && (
            <div className="comparison-chart__trend">
              <TrendIndicator 
                direction={trendDirection}
                value={percentageChange}
                showLabel={!isMobile}
              />
            </div>
          )}
        </>
      ) : (
        <div className="comparison-chart__no-data">
          No data available
        </div>
      )}
    </div>
  );
};

export default ComparisonChart;