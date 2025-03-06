import React from 'react';
import classNames from 'classnames'; // v2.3.2
import Icon from '../../common/Icon';
import { TrendDirection } from '../../../types';
import { TREND_INDICATOR_CONFIG } from '../../../config/chart-config';
import { formatNumber } from '../../../utils/format-utils';

/**
 * Props interface for the TrendIndicator component
 */
interface TrendIndicatorProps {
  /** The trend direction to display (INCREASING, DECREASING, or STABLE) */
  direction: TrendDirection;
  /** The percentage value to display alongside the indicator */
  value?: number;
  /** Whether to show the text label for the trend direction */
  showLabel?: boolean;
  /** Additional CSS class names to apply to the component */
  className?: string;
  /** Size variant of the indicator (small, medium, large) */
  size?: 'small' | 'medium' | 'large';
  /** Test ID for automated testing */
  testId?: string;
}

/**
 * A component that visualizes freight price movement trends with directional indicators
 */
const TrendIndicator: React.FC<TrendIndicatorProps> = ({
  direction,
  value,
  showLabel = false,
  className,
  size = 'medium',
  testId = 'trend-indicator'
}) => {
  // Get the appropriate icon name from configuration
  const iconName = TREND_INDICATOR_CONFIG.icons[direction];
  
  // Get the appropriate label text from configuration
  const labelText = TREND_INDICATOR_CONFIG.labels[direction];
  
  // Determine CSS classes based on direction and size
  const containerClasses = classNames(
    'trend-indicator',
    `trend-indicator--${direction.toLowerCase()}`,
    `trend-indicator--${size}`,
    className
  );
  
  // Format the percentage value if provided
  const formattedValue = value !== undefined 
    ? `${value > 0 ? '+' : ''}${formatNumber(value, 1)}%` 
    : null;
  
  // Map component size to icon size
  const iconSizeMap: Record<string, 'sm' | 'md' | 'lg'> = {
    'small': 'sm',
    'medium': 'md',
    'large': 'lg'
  };
  const iconSize = iconSizeMap[size] || 'md';
  
  return (
    <div 
      className={containerClasses} 
      data-testid={testId}
      role="status"
      aria-label={`${labelText}${value !== undefined ? ` ${formattedValue}` : ''}`}
    >
      <Icon 
        name={iconName} 
        size={iconSize} 
        className="trend-indicator__icon" 
        aria-hidden="true"
      />
      {showLabel && <span className="trend-indicator__label">{labelText}</span>}
      {formattedValue && <span className="trend-indicator__value">{formattedValue}</span>}
    </div>
  );
};

export default TrendIndicator;