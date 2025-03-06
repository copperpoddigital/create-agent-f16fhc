import React from 'react';
import { describe, it, expect } from '@jest/globals';
import { render, screen, fireEvent } from '../../../utils/test-utils';
import SummaryCard from './SummaryCard';
import { TrendDirection } from '../../../types';

/**
 * Helper function to render the SummaryCard component with default or custom props
 */
const renderSummaryCard = (customProps = {}) => {
  // Default props for the SummaryCard component
  const defaultProps = {
    title: 'Price Movement Summary',
    startValue: 4000,
    endValue: 4200,
    absoluteChange: 200,
    percentageChange: 5,
    trendDirection: TrendDirection.INCREASING,
    currency: 'USD'
  };

  // Merge default props with any custom props provided
  const props = {
    ...defaultProps,
    ...customProps
  };

  // Render the SummaryCard component with the merged props
  return render(<SummaryCard {...props} />);
};

describe('SummaryCard', () => {
  it('renders with default props', () => {
    renderSummaryCard();
    
    // Verify that the component is in the document
    const card = screen.getByTestId('summary-card');
    expect(card).toBeInTheDocument();
    
    // Check that the default title is displayed
    expect(screen.getByText('Price Movement Summary')).toBeInTheDocument();
    
    // Verify that start and end values are formatted correctly
    expect(screen.getByText(/\$4,000\.00/)).toBeInTheDocument();
    expect(screen.getByText(/\$4,200\.00/)).toBeInTheDocument();
  });

  it('renders with custom title and subtitle', () => {
    renderSummaryCard({
      title: 'Custom Title',
      subtitle: 'Custom Subtitle'
    });
    
    expect(screen.getByText('Custom Title')).toBeInTheDocument();
    expect(screen.getByText('Custom Subtitle')).toBeInTheDocument();
  });

  it('displays formatted currency values correctly', () => {
    renderSummaryCard({
      currency: 'EUR',
      startValue: 4000,
      endValue: 4200
    });
    
    // Check for EUR currency symbol in rendered values
    const values = screen.getAllByText(/€/, { exact: false });
    expect(values.length).toBeGreaterThan(0);
  });

  it('displays increasing trend correctly', () => {
    renderSummaryCard({
      percentageChange: 5,
      trendDirection: TrendDirection.INCREASING
    });
    
    // Check for the trend indicator with correct class
    const trendIndicator = screen.getByTestId('trend-indicator');
    expect(trendIndicator).toHaveClass('trend-indicator--increasing');
  });

  it('displays decreasing trend correctly', () => {
    renderSummaryCard({
      percentageChange: -5,
      trendDirection: TrendDirection.DECREASING
    });
    
    // Check for the trend indicator with correct class
    const trendIndicator = screen.getByTestId('trend-indicator');
    expect(trendIndicator).toHaveClass('trend-indicator--decreasing');
  });

  it('displays stable trend correctly', () => {
    renderSummaryCard({
      percentageChange: 0.5,
      trendDirection: TrendDirection.STABLE
    });
    
    // Check for the trend indicator with correct class
    const trendIndicator = screen.getByTestId('trend-indicator');
    expect(trendIndicator).toHaveClass('trend-indicator--stable');
  });

  it('displays time period when provided', () => {
    renderSummaryCard({
      period: 'Jan 2023 - Mar 2023'
    });
    
    // Verify period label and value are displayed
    expect(screen.getByText('Period:')).toBeInTheDocument();
    expect(screen.getByText('Jan 2023 - Mar 2023')).toBeInTheDocument();
  });

  it('calls onClick handler when clicked', () => {
    const mockOnClick = jest.fn();
    renderSummaryCard({
      onClick: mockOnClick
    });
    
    // Find the card and click it
    const card = screen.getByTestId('summary-card');
    fireEvent.click(card);
    
    // Verify that the onClick function was called
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('applies custom className when provided', () => {
    renderSummaryCard({
      className: 'custom-class'
    });
    
    // Verify that the custom class is applied
    const card = screen.getByTestId('summary-card');
    expect(card).toHaveClass('custom-class');
  });
});