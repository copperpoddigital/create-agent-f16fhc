import React from 'react';
import { describe, it, expect } from 'vitest'; // ^0.30.1
import AnalysisResultsTable from './AnalysisResultsTable';
import { createMockAnalysisResult, screen, render } from '../../../utils/test-utils';
import { TrendDirection } from '../../../types';

/**
 * Creates an array of mock detailed results for testing
 * @param count Number of detailed results to create
 * @returns Array of mock detailed results
 */
function createMockDetailedResults(count: number) {
  const results = [];
  
  for (let i = 0; i < count; i++) {
    let trendDirection = null;
    let absoluteChange = null;
    let percentageChange = null;
    
    // First item has null values for changes since it's the baseline
    if (i > 0) {
      // Alternate between increasing, decreasing, and stable trends
      if (i % 3 === 1) {
        trendDirection = TrendDirection.INCREASING;
        percentageChange = 1.25;
        absoluteChange = 50;
      } else if (i % 3 === 2) {
        trendDirection = TrendDirection.DECREASING;
        percentageChange = -1.5;
        absoluteChange = -30;
      } else {
        trendDirection = TrendDirection.STABLE;
        percentageChange = 0.2;
        absoluteChange = 10;
      }
    }
    
    results.push({
      period: `Period ${i + 1}`,
      price: 1000 + (i * 100),
      absolute_change: absoluteChange,
      percentage_change: percentageChange,
      trend_direction: trendDirection
    });
  }
  
  return results;
}

describe('AnalysisResultsTable', () => {
  it('renders correctly with valid data', () => {
    const mockResult = createMockAnalysisResult();
    render(<AnalysisResultsTable result={mockResult} />);
    
    // Check for column headers
    expect(screen.getByText('Period')).toBeInTheDocument();
    expect(screen.getByText(`Price (${mockResult.currency})`)).toBeInTheDocument();
    expect(screen.getByText('Absolute Change')).toBeInTheDocument();
    expect(screen.getByText('Percentage Change')).toBeInTheDocument();
    
    // Check for data from detailed results
    mockResult.detailed_results.forEach(item => {
      expect(screen.getByText(item.period)).toBeInTheDocument();
    });
  });

  it('displays loading state correctly', () => {
    const mockResult = createMockAnalysisResult();
    render(<AnalysisResultsTable result={mockResult} isLoading={true} />);
    
    // Check for loading indicator
    const loadingElement = screen.getByRole('status');
    expect(loadingElement).toBeInTheDocument();
    expect(loadingElement.textContent).toContain('Loading');
  });

  it('handles empty detailed results', () => {
    const mockResult = createMockAnalysisResult({
      detailed_results: []
    });
    
    render(<AnalysisResultsTable result={mockResult} />);
    
    // Check for empty state message
    expect(screen.getByText('No detailed results available.')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const mockResult = createMockAnalysisResult();
    const customClass = 'custom-table-class';
    
    const { container } = render(
      <AnalysisResultsTable result={mockResult} className={customClass} />
    );
    
    // The Table component applies the className to the table element
    // But the exact structure might vary, so we check if the class exists anywhere
    expect(container.innerHTML).toContain(customClass);
  });

  it('renders trend indicators correctly', () => {
    // Create mock result with known trend directions
    const mockResult = createMockAnalysisResult({
      detailed_results: createMockDetailedResults(4)
    });
    
    render(<AnalysisResultsTable result={mockResult} />);
    
    // Look for trend indicators based on their role and content
    const statusElements = screen.getAllByRole('status');
    
    // Filter out any loading indicators
    const trendIndicators = statusElements.filter(el => {
      const ariaLabel = el.getAttribute('aria-label') || '';
      return ariaLabel.includes('Increasing') || 
             ariaLabel.includes('Decreasing') || 
             ariaLabel.includes('Stable');
    });
    
    // Should have 3 trend indicators (one for each row after the first)
    expect(trendIndicators.length).toBe(3);
    
    // Check that we have one of each trend direction
    const hasIncreasing = trendIndicators.some(el => 
      (el.getAttribute('aria-label') || '').includes('Increasing'));
    const hasDecreasing = trendIndicators.some(el => 
      (el.getAttribute('aria-label') || '').includes('Decreasing'));
    const hasStable = trendIndicators.some(el => 
      (el.getAttribute('aria-label') || '').includes('Stable'));
    
    expect(hasIncreasing).toBe(true);
    expect(hasDecreasing).toBe(true);
    expect(hasStable).toBe(true);
  });

  it('formats currency values correctly', () => {
    const mockResult = createMockAnalysisResult({
      currency: 'USD',
      detailed_results: [
        {
          period: 'Period 1',
          price: 1000,
          absolute_change: null,
          percentage_change: null,
          trend_direction: null
        },
        {
          period: 'Period 2',
          price: 1500,
          absolute_change: 500,
          percentage_change: 50,
          trend_direction: TrendDirection.INCREASING
        }
      ]
    });
    
    render(<AnalysisResultsTable result={mockResult} />);
    
    // Find all table cells and check for formatted values
    const cells = screen.getAllByRole('cell');
    
    // Check for the presence of formatted values in the cells
    const cellTexts = cells.map(cell => cell.textContent);
    
    // Check for formatted price values
    expect(cellTexts.some(text => text?.includes('$1,000.00'))).toBe(true);
    expect(cellTexts.some(text => text?.includes('$1,500.00'))).toBe(true);
    
    // Check for formatted absolute change (should include + sign)
    expect(cellTexts.some(text => text?.includes('+$500.00'))).toBe(true);
  });

  it('handles pagination correctly when enabled', () => {
    // Create a result with many detailed results to trigger pagination
    const mockResult = createMockAnalysisResult({
      detailed_results: createMockDetailedResults(15)
    });
    
    render(
      <AnalysisResultsTable 
        result={mockResult} 
        isPaginated={true} 
        itemsPerPage={10} 
      />
    );
    
    // Check that pagination controls are rendered
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    
    // Check that only the first page of results is shown
    expect(screen.getByText('Period 1')).toBeInTheDocument();
    expect(screen.getByText('Period 10')).toBeInTheDocument();
    
    // Item on second page should not be visible
    expect(screen.queryByText('Period 11')).not.toBeInTheDocument();
  });

  it('disables sorting when isSortable is false', () => {
    const mockResult = createMockAnalysisResult();
    
    render(<AnalysisResultsTable result={mockResult} isSortable={false} />);
    
    // Get all column headers
    const headerCells = screen.getAllByRole('columnheader');
    
    // None of them should have sortable attributes or classes
    headerCells.forEach(header => {
      // Headers shouldn't be sortable
      expect(header).not.toHaveAttribute('aria-sort');
      
      // Headers shouldn't have tabindex for keyboard sorting
      expect(header).not.toHaveAttribute('tabindex', '0');
    });
  });
});