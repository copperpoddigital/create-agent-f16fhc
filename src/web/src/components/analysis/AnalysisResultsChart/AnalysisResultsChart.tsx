import React from 'react';
import classNames from 'classnames'; // v2.3.2
import LineChart from '../../charts/LineChart';
import Card from '../../common/Card';
import Spinner from '../../common/Spinner';
import { AnalysisResult, TrendDirection, TimeGranularity } from '../../../types';
import { formatCurrency } from '../../../utils/currency-utils';
import { formatDate } from '../../../utils/date-utils';

/**
 * Props interface for the AnalysisResultsChart component
 */
interface AnalysisResultsChartProps {
  /** The analysis result data containing time series data and metadata */
  result: AnalysisResult;
  /** Whether the result is currently loading */
  loading?: boolean;
  /** Whether an error occurred while fetching the result */
  error?: boolean;
  /** Error message to display if error is true */
  errorMessage?: string;
  /** Additional CSS class names to apply to the component */
  className?: string;
  /** Test ID for automated testing */
  testId?: string;
}

/**
 * A component that renders a chart visualization of freight price movement analysis results
 */
const AnalysisResultsChart: React.FC<AnalysisResultsChartProps> = ({
  result,
  loading = false,
  error = false,
  errorMessage,
  className,
  testId = 'analysis-results-chart',
}) => {
  // Handle loading state
  if (loading) {
    return (
      <Card
        title="Price Movement Chart"
        className={classNames('analysis-results-chart', 'analysis-results-chart--loading', className)}
        testId={`${testId}-loading`}
      >
        <div className="analysis-results-chart__spinner-container">
          <Spinner size="lg" />
          <p>Loading chart data...</p>
        </div>
      </Card>
    );
  }

  // Handle error state
  if (error) {
    return (
      <Card
        title="Price Movement Chart"
        className={classNames('analysis-results-chart', 'analysis-results-chart--error', className)}
        testId={`${testId}-error`}
      >
        <div className="analysis-results-chart__message-container">
          <p className="analysis-results-chart__error-message">
            {errorMessage || 'An error occurred while loading the chart data.'}
          </p>
        </div>
      </Card>
    );
  }

  // Handle missing result
  if (!result) {
    return (
      <Card
        title="Price Movement Chart"
        className={classNames('analysis-results-chart', 'analysis-results-chart--no-data', className)}
        testId={`${testId}-no-data`}
      >
        <div className="analysis-results-chart__message-container">
          <p className="analysis-results-chart__no-data-message">
            No analysis data available.
          </p>
        </div>
      </Card>
    );
  }

  // Extract time series data and metadata from the result
  const { time_series = [], currency = 'USD' } = result;
  
  // Handle potential missing or malformed price_change property
  const trend_direction = result.price_change?.trend_direction || TrendDirection.STABLE;
  
  // Extract time period information with fallbacks for missing data
  const start_date = result.time_period?.start_date || '';
  const end_date = result.time_period?.end_date || '';
  const granularity = result.time_period?.granularity || TimeGranularity.DAILY;

  // Check for empty time series data
  if (!time_series || time_series.length === 0) {
    return (
      <Card
        title="Price Movement Chart"
        className={classNames('analysis-results-chart', 'analysis-results-chart--empty', className)}
        testId={`${testId}-empty`}
      >
        <div className="analysis-results-chart__message-container">
          <p className="analysis-results-chart__empty-message">
            No data available for visualization.
          </p>
        </div>
      </Card>
    );
  }

  // Prepare chart labels and title
  const xAxisLabel = 'Time';
  const yAxisLabel = `Price (${currency})`;
  
  // Format the time period for the chart title based on granularity
  let periodLabel = '';
  if (start_date && end_date) {
    switch (granularity) {
      case TimeGranularity.DAILY:
        periodLabel = `Daily: ${formatDate(start_date)} - ${formatDate(end_date)}`;
        break;
      case TimeGranularity.WEEKLY:
        periodLabel = `Weekly: ${formatDate(start_date)} - ${formatDate(end_date)}`;
        break;
      case TimeGranularity.MONTHLY:
        periodLabel = `Monthly: ${formatDate(start_date)} - ${formatDate(end_date)}`;
        break;
      case TimeGranularity.CUSTOM:
        periodLabel = `Custom: ${formatDate(start_date)} - ${formatDate(end_date)}`;
        break;
      default:
        periodLabel = `${formatDate(start_date)} - ${formatDate(end_date)}`;
    }
  } else {
    periodLabel = 'Time Period Not Specified';
  }
  
  const chartTitle = `Price Movement: ${periodLabel}`;

  // Render the chart
  return (
    <Card
      title="Price Movement Chart"
      className={classNames(
        'analysis-results-chart', 
        `analysis-results-chart--${trend_direction}`,
        className
      )}
      testId={testId}
    >
      <LineChart 
        data={time_series}
        title={chartTitle}
        xAxisLabel={xAxisLabel}
        yAxisLabel={yAxisLabel}
        currencyCode={currency}
        trendDirection={trend_direction}
        responsive={true}
        testId={`${testId}-line-chart`}
      />
    </Card>
  );
};

export default AnalysisResultsChart;