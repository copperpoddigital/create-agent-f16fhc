import React from 'react';
import classNames from 'classnames'; // v2.3.2
import Card from '../../common/Card';
import TrendIndicator from '../../charts/TrendIndicator';
import { formatCurrency, formatAbsoluteChange } from '../../../utils/currency-utils';
import { formatTimePeriod } from '../../../utils/format-utils';
import { formatDate } from '../../../utils/date-utils';
import { AnalysisResult } from '../../../types';

/**
 * Props interface for the AnalysisResultsSummary component
 */
interface AnalysisResultsSummaryProps {
  /** The analysis result to display in the summary */
  result: AnalysisResult;
  /** Whether the summary is in a loading state */
  isLoading?: boolean;
  /** Additional CSS class names to apply to the summary */
  className?: string;
  /** Whether to show the time period information */
  showTimePeriod?: boolean;
  /** Whether to show the data sources information */
  showDataSources?: boolean;
  /** Whether to show when the analysis was calculated */
  showCalculatedAt?: boolean;
}

/**
 * A component that displays a summary of freight price movement analysis results
 */
const AnalysisResultsSummary: React.FC<AnalysisResultsSummaryProps> = ({
  result,
  isLoading = false,
  className,
  showTimePeriod = true,
  showDataSources = true,
  showCalculatedAt = true,
}) => {
  // Combine class names
  const summaryClasses = classNames('analysis-results-summary', className);

  // Handle loading state with skeleton placeholders
  if (isLoading) {
    return (
      <Card title="SUMMARY" className={summaryClasses}>
        <div className="skeleton-loading" aria-busy="true" aria-label="Loading summary data">
          <div className="skeleton-line skeleton-line--medium"></div>
          <div className="skeleton-line skeleton-line--small"></div>
          <div className="skeleton-line skeleton-line--large"></div>
          <div className="skeleton-line skeleton-line--medium"></div>
          <div className="skeleton-line skeleton-line--medium"></div>
        </div>
      </Card>
    );
  }

  // Error handling for missing result data
  if (!result) {
    return (
      <Card title="SUMMARY" className={classNames(summaryClasses, 'analysis-results-summary--error')}>
        <div className="summary-error">
          <p>No analysis results available.</p>
        </div>
      </Card>
    );
  }

  // Extract relevant data from the result with safe defaults
  const {
    time_period = { start_date: '', end_date: '', granularity: '' },
    price_change = { absolute_change: 0, percentage_change: 0, trend_direction: 'stable' },
    start_value = 0,
    end_value = 0,
    currency = 'USD',
    filters = [],
    calculated_at = '',
  } = result;

  // Format time period
  const formattedTimePeriod = time_period.start_date && time_period.end_date 
    ? formatTimePeriod(time_period.start_date, time_period.end_date, time_period.granularity)
    : 'N/A';

  // Format start and end values
  const formattedStartValue = formatCurrency(start_value, currency);
  const formattedEndValue = formatCurrency(end_value, currency);

  // Format the absolute change
  const formattedAbsoluteChange = formatAbsoluteChange(price_change.absolute_change, currency);

  // Format the calculated_at date
  const formattedCalculatedAt = calculated_at ? formatDate(calculated_at) : 'N/A';

  return (
    <Card title="SUMMARY" className={summaryClasses}>
      <div className="analysis-results-summary__content">
        {showTimePeriod && (
          <div className="summary-item summary-item--time-period">
            <span className="summary-label">Time Period:</span>
            <span className="summary-value">{formattedTimePeriod}</span>
          </div>
        )}

        {showDataSources && filters && filters.length > 0 && (
          <div className="summary-item summary-item--filters">
            <span className="summary-label">Filters:</span>
            <span className="summary-value">
              {filters.map((filter, index) => (
                <span key={index}>
                  {filter.field}: {filter.value}
                  {index < filters.length - 1 && ', '}
                </span>
              ))}
            </span>
          </div>
        )}

        <div className="summary-item summary-item--overall-change">
          <span className="summary-label">Overall Change:</span>
          <div className="summary-value summary-value--with-indicator">
            <TrendIndicator 
              direction={price_change.trend_direction} 
              value={price_change.percentage_change} 
              showLabel={false}
            />
          </div>
        </div>

        <div className="summary-item summary-item--absolute-change">
          <span className="summary-label">Absolute Change:</span>
          <span className="summary-value">{formattedAbsoluteChange}</span>
        </div>

        <div className="summary-item summary-item--price-range">
          <span className="summary-label">Starting Price:</span>
          <span className="summary-value">{formattedStartValue}</span>
        </div>

        <div className="summary-item summary-item--price-range">
          <span className="summary-label">Ending Price:</span>
          <span className="summary-value">{formattedEndValue}</span>
        </div>

        {showCalculatedAt && calculated_at && (
          <div className="summary-item summary-item--calculated-at">
            <span className="summary-label">Calculated At:</span>
            <span className="summary-value">{formattedCalculatedAt}</span>
          </div>
        )}
      </div>
    </Card>
  );
};

export default AnalysisResultsSummary;