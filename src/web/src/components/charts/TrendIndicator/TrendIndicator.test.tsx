import React from 'react';
import { render, screen } from '../../../utils/test-utils';
import TrendIndicator from './TrendIndicator';
import { TrendDirection } from '../../../types';
import { TREND_INDICATOR_CONFIG } from '../../../config/chart-config';
import '@testing-library/jest-dom/extend-expect';

describe('TrendIndicator component', () => {
  test('renders with increasing trend', () => {
    render(<TrendIndicator direction={TrendDirection.INCREASING} />);
    
    const container = screen.getByTestId('trend-indicator');
    expect(container).toHaveClass('trend-indicator--increasing');
    
    // Verify the correct icon is displayed
    const icon = container.querySelector('.trend-indicator__icon');
    expect(icon).toBeInTheDocument();
    
    // No label by default
    expect(screen.queryByText(TREND_INDICATOR_CONFIG.labels[TrendDirection.INCREASING])).not.toBeInTheDocument();
  });

  test('renders with decreasing trend', () => {
    render(<TrendIndicator direction={TrendDirection.DECREASING} />);
    
    const container = screen.getByTestId('trend-indicator');
    expect(container).toHaveClass('trend-indicator--decreasing');
    
    // Verify the correct icon is displayed
    const icon = container.querySelector('.trend-indicator__icon');
    expect(icon).toBeInTheDocument();
    
    // No label by default
    expect(screen.queryByText(TREND_INDICATOR_CONFIG.labels[TrendDirection.DECREASING])).not.toBeInTheDocument();
  });

  test('renders with stable trend', () => {
    render(<TrendIndicator direction={TrendDirection.STABLE} />);
    
    const container = screen.getByTestId('trend-indicator');
    expect(container).toHaveClass('trend-indicator--stable');
    
    // Verify the correct icon is displayed
    const icon = container.querySelector('.trend-indicator__icon');
    expect(icon).toBeInTheDocument();
    
    // No label by default
    expect(screen.queryByText(TREND_INDICATOR_CONFIG.labels[TrendDirection.STABLE])).not.toBeInTheDocument();
  });

  test('displays label when showLabel is true', () => {
    render(<TrendIndicator direction={TrendDirection.INCREASING} showLabel={true} />);
    
    const labelText = TREND_INDICATOR_CONFIG.labels[TrendDirection.INCREASING];
    expect(screen.getByText(labelText)).toBeInTheDocument();
  });

  test('displays percentage value when provided', () => {
    const testValue = 5.2;
    render(<TrendIndicator direction={TrendDirection.INCREASING} value={testValue} />);
    
    // Using a partial text match for the formatted value
    const formattedValue = `+${testValue.toFixed(1)}%`;
    expect(screen.getByText(formattedValue)).toBeInTheDocument();
  });

  test('applies custom class name', () => {
    const customClass = 'custom-test-class';
    render(<TrendIndicator direction={TrendDirection.INCREASING} className={customClass} />);
    
    const container = screen.getByTestId('trend-indicator');
    expect(container).toHaveClass(customClass);
  });

  test('applies different sizes', () => {
    // Test small size
    const { rerender } = render(<TrendIndicator direction={TrendDirection.INCREASING} size="small" />);
    let container = screen.getByTestId('trend-indicator');
    expect(container).toHaveClass('trend-indicator--small');
    
    // Test large size
    rerender(<TrendIndicator direction={TrendDirection.INCREASING} size="large" />);
    container = screen.getByTestId('trend-indicator');
    expect(container).toHaveClass('trend-indicator--large');
  });

  test('uses custom test ID when provided', () => {
    const customTestId = 'custom-test-id';
    render(<TrendIndicator direction={TrendDirection.INCREASING} testId={customTestId} />);
    
    expect(screen.getByTestId(customTestId)).toBeInTheDocument();
  });
});