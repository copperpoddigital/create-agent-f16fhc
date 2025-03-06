/**
 * chart-utils.ts
 * 
 * Utility functions for chart creation, configuration, and data transformation in the
 * Freight Price Movement Agent web application. This file provides helper functions
 * for working with Chart.js to visualize freight price movement data in various chart types.
 * 
 * These utilities support requirements from:
 * - Technical Specifications/2.1 FEATURE CATALOG/2.1.4 Result Presentation
 * - Technical Specifications/6.3 PRESENTATION SERVICE/6.3.3 Visualization Types
 * - Technical Specifications/7.5 RESPONSIVE DESIGN
 * - Technical Specifications/7.8 COMPONENT LIBRARY/7.8.2 Data Visualization Components
 */

import { 
  Chart, 
  ChartOptions, 
  ChartData, 
  ChartDataset,
  TooltipItem 
} from 'chart.js'; // v4.3.0

import { 
  CHART_CONFIG, 
  CHART_DIMENSIONS, 
  TREND_COLORS 
} from '../config/chart-config';

import { BREAKPOINTS } from '../config/constants';
import { TimeSeriesDataPoint, TrendDirection } from '../types';
import { formatCurrency } from './currency-utils';
import { formatDate } from './date-utils';

/**
 * Interface for options passed to chart utility functions
 */
export interface ChartUtilsOptions {
  backgroundColor?: string;
  borderColor?: string;
  borderWidth?: number;
  fill?: boolean;
  pointBackgroundColor?: string;
  pointRadius?: number;
  pointHoverRadius?: number;
  label?: string;
  comparisonLabel?: string;
}

/**
 * Creates formatted Chart.js data structure from time series data points for line charts
 * 
 * @param data - Array of time series data points
 * @param options - Optional styling and configuration options
 * @returns Formatted Chart.js data structure for line charts
 */
export function createTimeSeriesChartData(
  data: TimeSeriesDataPoint[],
  options: Partial<ChartUtilsOptions> = {}
): ChartData<'line'> {
  // Extract timestamps and values from data
  const timestamps = data.map(point => point.timestamp);
  const values = data.map(point => point.value);
  
  // Format timestamps for display
  const labels = timestamps.map(timestamp => formatDate(timestamp));
  
  // Create dataset with data points and styling
  const dataset: ChartDataset<'line'> = {
    label: options.label || 'Freight Price',
    data: values,
    backgroundColor: options.backgroundColor || CHART_CONFIG.defaults.backgroundColor,
    borderColor: options.borderColor || TREND_COLORS[TrendDirection.STABLE],
    borderWidth: options.borderWidth || 2,
    fill: options.fill !== undefined ? options.fill : false,
    pointBackgroundColor: options.pointBackgroundColor || TREND_COLORS[TrendDirection.STABLE],
    pointRadius: options.pointRadius || 3,
    pointHoverRadius: options.pointHoverRadius || 5,
    tension: 0.3 // Smooth curve
  };
  
  return {
    labels,
    datasets: [dataset]
  };
}

/**
 * Creates formatted Chart.js data structure for comparison bar charts with two data series
 * 
 * @param primaryData - Primary data series
 * @param comparisonData - Optional comparison data series
 * @param labels - Optional custom labels for the X-axis
 * @param options - Optional styling and configuration options
 * @returns Formatted Chart.js data structure for bar charts
 */
export function createComparisonChartData(
  primaryData: TimeSeriesDataPoint[],
  comparisonData?: TimeSeriesDataPoint[],
  labels?: string[],
  options: Partial<ChartUtilsOptions> = {}
): ChartData<'bar'> {
  // Extract values from data
  const primaryValues = primaryData.map(point => point.value);
  const comparisonValues = comparisonData ? comparisonData.map(point => point.value) : [];
  
  // Use provided labels or generate from primary data timestamps
  const chartLabels = labels || primaryData.map(point => formatDate(point.timestamp));
  
  // Create datasets array starting with primary dataset
  const datasets: ChartDataset<'bar'>[] = [
    {
      label: options.label || 'Current Period',
      data: primaryValues,
      backgroundColor: options.backgroundColor || TREND_COLORS[TrendDirection.INCREASING],
      borderColor: options.borderColor || TREND_COLORS[TrendDirection.INCREASING],
      borderWidth: options.borderWidth || 1,
      borderRadius: 4
    }
  ];
  
  // Add comparison dataset if exists
  if (comparisonData && comparisonData.length > 0) {
    datasets.push({
      label: options.comparisonLabel || 'Comparison Period',
      data: comparisonValues,
      backgroundColor: TREND_COLORS[TrendDirection.STABLE],
      borderColor: TREND_COLORS[TrendDirection.STABLE],
      borderWidth: options.borderWidth || 1,
      borderRadius: 4
    });
  }
  
  return {
    labels: chartLabels,
    datasets
  };
}

/**
 * Generates Chart.js options by merging default options with custom options
 * 
 * @param baseOptions - Base chart options
 * @param customOptions - Custom options to override defaults
 * @param trendDirection - Optional trend direction to apply appropriate styling
 * @returns Merged chart options
 */
export function getChartOptions<T extends 'line' | 'bar'>(
  baseOptions: ChartOptions<T>,
  customOptions: Partial<ChartOptions<T>> = {},
  trendDirection?: TrendDirection
): ChartOptions<T> {
  // Start with default options
  let options: ChartOptions<T> = { ...CHART_CONFIG.defaults, ...baseOptions };
  
  // Apply trend direction styling if provided
  if (trendDirection) {
    const color = TREND_COLORS[trendDirection];
    
    if (options.elements) {
      if (options.elements.line) {
        options.elements.line.borderColor = color;
      }
      
      if (options.elements.point) {
        options.elements.point.backgroundColor = color;
      }
      
      if (options.elements.bar) {
        options.elements.bar.backgroundColor = color;
        options.elements.bar.borderColor = color;
      }
    }
  }
  
  // Merge with custom options
  options = { ...options, ...customOptions };
  
  return options;
}

/**
 * Calculates responsive chart dimensions based on screen size
 * 
 * @param containerWidth - Width of the container element
 * @returns Object with width and height dimensions
 */
export function getResponsiveChartDimensions(containerWidth: number): { width: number, height: number } {
  let dimensions;
  
  // Determine device type based on container width
  if (containerWidth <= BREAKPOINTS.MOBILE) {
    dimensions = CHART_DIMENSIONS.mobile;
  } else if (containerWidth <= BREAKPOINTS.TABLET) {
    dimensions = CHART_DIMENSIONS.tablet;
  } else if (containerWidth <= BREAKPOINTS.LAPTOP) {
    dimensions = CHART_DIMENSIONS.laptop;
  } else {
    dimensions = CHART_DIMENSIONS.desktop;
  }
  
  // Calculate height based on width and aspect ratio
  const width = Math.min(containerWidth - (dimensions.padding * 2), dimensions.maxWidth);
  const height = width / dimensions.aspectRatio;
  
  return {
    width,
    height: Math.min(height, dimensions.height)
  };
}

/**
 * Creates a tooltip formatter function for Chart.js charts
 * 
 * @param currencyCode - Currency code for formatting values
 * @param dateFormat - Date format for formatting labels
 * @returns Tooltip formatter function for Chart.js
 */
export function formatChartTooltip(
  currencyCode?: string, 
  dateFormat?: string
): (tooltipItems: TooltipItem<'line' | 'bar'>[]) => string {
  return (tooltipItems: TooltipItem<'line' | 'bar'>[]) => {
    const item = tooltipItems[0];
    if (!item) return '';
    
    // Format label as date if dateFormat is provided
    const label = dateFormat ? formatDate(item.label, dateFormat) : item.label;
    
    // Format value as currency if currencyCode is provided
    const value = currencyCode 
      ? formatCurrency(item.parsed.y, currencyCode)
      : item.parsed.y.toLocaleString();
    
    return `${label}: ${value}`;
  };
}

/**
 * Applies theme-specific styling to chart options
 * 
 * @param options - Chart options to modify
 * @param theme - Theme to apply ('light' or 'dark')
 * @returns Theme-styled chart options
 */
export function applyChartTheme<T extends 'line' | 'bar'>(
  options: ChartOptions<T>,
  theme: string = 'light'
): ChartOptions<T> {
  const themeColors = theme === 'dark' 
    ? CHART_THEME_COLORS.dark 
    : CHART_THEME_COLORS.light;
  
  const themedOptions = { ...options };
  
  // Update background and text colors
  themedOptions.color = themeColors.text;
  themedOptions.backgroundColor = themeColors.background;
  
  // Update grid lines
  if (themedOptions.scales?.x?.grid) {
    themedOptions.scales.x.grid.color = themeColors.grid;
  }
  
  if (themedOptions.scales?.y?.grid) {
    themedOptions.scales.y.grid.color = themeColors.grid;
  }
  
  // Update tooltip colors
  if (themedOptions.plugins?.tooltip) {
    themedOptions.plugins.tooltip.backgroundColor = themeColors.tooltip.background;
    themedOptions.plugins.tooltip.titleColor = themeColors.tooltip.text;
    themedOptions.plugins.tooltip.bodyColor = themeColors.tooltip.text;
    themedOptions.plugins.tooltip.borderColor = themeColors.tooltip.border;
  }
  
  return themedOptions;
}

/**
 * Gets the appropriate color for a trend direction
 * 
 * @param trendDirection - The trend direction
 * @returns Color code for the trend direction
 */
export function getTrendColor(trendDirection: TrendDirection): string {
  return TREND_COLORS[trendDirection] || TREND_COLORS[TrendDirection.STABLE];
}

/**
 * Creates data for a simple trend indicator chart
 * 
 * @param trendDirection - Direction of the trend
 * @param percentageChange - Percentage change value
 * @returns Chart data for trend indicator
 */
export function createTrendIndicatorData(
  trendDirection: TrendDirection,
  percentageChange: number
): ChartData<'line'> {
  let data: number[];
  
  // Create trend line data based on direction
  switch (trendDirection) {
    case TrendDirection.INCREASING:
      data = [0, 1, 2]; // Upward line
      break;
    case TrendDirection.DECREASING:
      data = [2, 1, 0]; // Downward line
      break;
    case TrendDirection.STABLE:
    default:
      data = [1, 1, 1]; // Flat line
      break;
  }
  
  // Get color based on trend direction
  const color = getTrendColor(trendDirection);
  
  // Format percentage for label
  const formattedPercentage = percentageChange.toFixed(1) + '%';
  const sign = percentageChange > 0 ? '+' : '';
  
  return {
    labels: ['', '', ''],
    datasets: [
      {
        label: `${sign}${formattedPercentage}`,
        data,
        borderColor: color,
        backgroundColor: color,
        borderWidth: 2,
        pointRadius: 0,
        tension: 0,
        fill: false
      }
    ]
  };
}

/**
 * Safely destroys a Chart.js instance to prevent memory leaks
 * 
 * @param chartInstance - Chart instance to destroy
 */
export function destroyChart(chartInstance: Chart | null): void {
  if (chartInstance) {
    chartInstance.destroy();
  }
}