import React from 'react';
import AnalysisOptions from './AnalysisOptions';
import { OutputFormat } from '../../../types/analysis.types';
import { render, screen, fireEvent } from '../../../utils/test-utils';

/**
 * Helper function to set up the component with default props for testing
 */
const setup = (props = {}) => {
  // Create mock functions for all callback props
  const mockOnCalculateAbsoluteChange = jest.fn();
  const mockOnCalculatePercentageChange = jest.fn();
  const mockOnIdentifyTrendDirection = jest.fn();
  const mockOnCompareToHistoricalBaseline = jest.fn();
  const mockOnBaselinePeriodSelect = jest.fn();
  const mockOnOutputFormatChange = jest.fn();
  const mockOnIncludeVisualization = jest.fn();
  
  // Default props that match the component's expected props
  const defaultProps = {
    calculateAbsoluteChange: true,
    calculatePercentageChange: true,
    identifyTrendDirection: true,
    compareToHistoricalBaseline: false,
    baselinePeriodId: null,
    outputFormat: OutputFormat.JSON,
    includeVisualization: true,
    showBaselinePeriod: false,
    errors: {},
    touched: {},
    onCalculateAbsoluteChange: mockOnCalculateAbsoluteChange,
    onCalculatePercentageChange: mockOnCalculatePercentageChange,
    onIdentifyTrendDirection: mockOnIdentifyTrendDirection,
    onCompareToHistoricalBaseline: mockOnCompareToHistoricalBaseline,
    onBaselinePeriodSelect: mockOnBaselinePeriodSelect,
    onOutputFormatChange: mockOnOutputFormatChange,
    onIncludeVisualization: mockOnIncludeVisualization,
    ...props
  };
  
  // Render the component with the combined props
  const renderResult = render(<AnalysisOptions {...defaultProps} />);
  
  // Return the render result and the mock functions for assertions
  return {
    ...renderResult,
    mockOnCalculateAbsoluteChange,
    mockOnCalculatePercentageChange,
    mockOnIdentifyTrendDirection,
    mockOnCompareToHistoricalBaseline,
    mockOnBaselinePeriodSelect,
    mockOnOutputFormatChange,
    mockOnIncludeVisualization
  };
};

describe('AnalysisOptions Component', () => {
  test('renders with default props', () => {
    setup();
    
    // Check that all checkboxes are present and have correct checked states
    expect(screen.getByLabelText('Calculate absolute change')).toBeChecked();
    expect(screen.getByLabelText('Calculate percentage change')).toBeChecked();
    expect(screen.getByLabelText('Identify trend direction')).toBeChecked();
    expect(screen.getByLabelText('Compare to historical baseline')).not.toBeChecked();
    
    // Check that visualization is checked
    expect(screen.getByLabelText('Include visualization')).toBeChecked();
    
    // Check that the output format select is present
    expect(screen.getByLabelText('Output Format')).toBeInTheDocument();
    
    // Ensure baseline period selection is not shown
    expect(screen.queryByText('Baseline period')).not.toBeInTheDocument();
  });
  
  test('handles checkbox changes correctly', () => {
    const { 
      mockOnCalculateAbsoluteChange,
      mockOnCalculatePercentageChange,
      mockOnIdentifyTrendDirection,
      mockOnCompareToHistoricalBaseline,
      mockOnIncludeVisualization
    } = setup();
    
    // Test each checkbox change
    
    // Absolute change checkbox
    fireEvent.click(screen.getByLabelText('Calculate absolute change'));
    expect(mockOnCalculateAbsoluteChange).toHaveBeenCalledWith(false); // Toggling from true to false
    
    // Percentage change checkbox
    fireEvent.click(screen.getByLabelText('Calculate percentage change'));
    expect(mockOnCalculatePercentageChange).toHaveBeenCalledWith(false); // Toggling from true to false
    
    // Trend direction checkbox
    fireEvent.click(screen.getByLabelText('Identify trend direction'));
    expect(mockOnIdentifyTrendDirection).toHaveBeenCalledWith(false); // Toggling from true to false
    
    // Compare to historical baseline checkbox
    fireEvent.click(screen.getByLabelText('Compare to historical baseline'));
    // This uses the full event object, so we check it was called but don't test the exact argument
    expect(mockOnCompareToHistoricalBaseline).toHaveBeenCalled();
    
    // Include visualization checkbox
    fireEvent.click(screen.getByLabelText('Include visualization'));
    expect(mockOnIncludeVisualization).toHaveBeenCalledWith(false); // Toggling from true to false
  });
  
  test('shows baseline period selection when compareToHistoricalBaseline is true', () => {
    const { mockOnBaselinePeriodSelect } = setup({
      compareToHistoricalBaseline: true,
      showBaselinePeriod: true,
      // In a real scenario, baselinePeriodOptions would be passed down to the Select component
      // Here we're just testing that the section appears, not the select functionality
    });
    
    // Check that baseline period selection is shown
    expect(screen.getByText('Baseline period')).toBeInTheDocument();
    expect(screen.getByLabelText('Baseline period')).toBeInTheDocument();
    
    // We can't easily test the select interaction since the options come from props
    // and our test doesn't populate them, but we can verify the section is rendered
  });
  
  test('handles output format selection correctly', () => {
    const { mockOnOutputFormatChange } = setup();
    
    // Get the select element
    const selectElement = screen.getByLabelText('Output Format');
    
    // Change the selected option
    fireEvent.change(selectElement, { target: { value: OutputFormat.CSV } });
    
    // Verify the callback was called with the new value
    expect(mockOnOutputFormatChange).toHaveBeenCalledWith(OutputFormat.CSV);
  });
  
  test('displays validation errors correctly', () => {
    setup({
      errors: {
        baselinePeriodId: 'Baseline period is required when comparison is enabled',
      },
      touched: {
        baselinePeriodId: true,
      },
      compareToHistoricalBaseline: true,
      showBaselinePeriod: true
    });
    
    // Check that the error message is displayed
    expect(screen.getByText('Baseline period is required when comparison is enabled')).toBeInTheDocument();
  });
});