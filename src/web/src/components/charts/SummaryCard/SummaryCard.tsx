import React from 'react';
import classNames from 'classnames'; // v2.3.2
import Card from '../../common/Card';
import TrendIndicator from '../TrendIndicator';
import { TrendDirection } from '../../../types';
import { formatCurrency, formatPercentage, formatAbsoluteChange } from '../../../utils/currency-utils';

/**
 * Props interface for the SummaryCard component
 */
interface SummaryCardProps {
  /** Title of the summary card */
  title?: string;
  /** Subtitle or description text for the card */
  subtitle?: string;
  /** Starting freight price value */
  startValue: number;
  /** Ending freight price value */
  endValue: number;
  /** Absolute change in freight price (end - start) */
  absoluteChange: number;
  /** Percentage change in freight price */
  percentageChange: number;
  /** Direction of the price trend (increasing, decreasing, or stable) */
  trendDirection: TrendDirection;
  /** Currency code for monetary values */
  currency?: string;
  /** Time period description for the analysis */
  period?: string;
  /** Additional CSS class names */
  className?: string;
  /** Visual variant of the card */
  variant?: string;
  /** Click handler for the card */
  onClick?: () => void;
  /** Test ID for automated testing */
  testId?: string;
}

/**
 * A card component that displays a summary of freight price movement analysis results
 */
const SummaryCard: React.FC<SummaryCardProps> = ({
  title = 'Price Movement Summary',
  subtitle,
  startValue,
  endValue,
  absoluteChange,
  percentageChange,
  trendDirection,
  currency = 'USD',
  period,
  className,
  variant,
  onClick,
  testId = 'summary-card',
}) => {
  // Format the values for display
  const formattedStartValue = formatCurrency(startValue, currency);
  const formattedEndValue = formatCurrency(endValue, currency);
  const formattedAbsoluteChange = formatAbsoluteChange(absoluteChange, currency);
  
  // Construct CSS class names
  const cardClasses = classNames('summary-card', {
    [`summary-card--${trendDirection.toLowerCase()}`]: trendDirection,
  }, className);
  
  return (
    <Card 
      title={title}
      subtitle={subtitle}
      variant={variant}
      className={cardClasses}
      onClick={onClick}
      testId={testId}
      clickable={!!onClick}
    >
      <div className="summary-card__content">
        <div className="summary-card__values">
          <div className="summary-card__value-item">
            <span className="summary-card__label">Start:</span>
            <span className="summary-card__value">{formattedStartValue}</span>
          </div>
          <div className="summary-card__value-item">
            <span className="summary-card__label">End:</span>
            <span className="summary-card__value">{formattedEndValue}</span>
          </div>
        </div>
        
        <div className="summary-card__changes">
          <div className="summary-card__change-item">
            <span className="summary-card__label">Absolute Change:</span>
            <span className="summary-card__value">{formattedAbsoluteChange}</span>
          </div>
          <div className="summary-card__change-item">
            <span className="summary-card__label">Percentage Change:</span>
            <div className="summary-card__trend">
              <TrendIndicator 
                direction={trendDirection}
                value={percentageChange}
                showLabel={true}
              />
            </div>
          </div>
        </div>
        
        {period && (
          <div className="summary-card__period">
            <span className="summary-card__label">Period:</span>
            <span className="summary-card__value">{period}</span>
          </div>
        )}
      </div>
    </Card>
  );
};

export default SummaryCard;