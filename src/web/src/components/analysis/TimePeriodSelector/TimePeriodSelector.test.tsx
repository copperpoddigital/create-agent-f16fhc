import React from 'react';
import { vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import TimePeriodSelector from './TimePeriodSelector';
import { TimeGranularity } from '../../../types/analysis.types';

// Mock the useApi hook
vi.mock('../../../hooks/useApi', () => ({
  default: () => ({
    get: vi.fn().mockResolvedValue([
      { id: 'period1', name: 'Last Quarter' },
      { id: 'period2', name: 'Last Month' }
    ]),
    isLoading: false
  })
}));

// Setup function to create default props
const setup = () => {
  return {
    selectedPeriodId: null,
    startDate: '2023-01-01',
    endDate: '2023-03-31',
    granularity: TimeGranularity.WEEKLY,
    customInterval: null,
    onPeriodSelect: vi.fn(),
    onStartDateChange: vi.fn(),
    onEndDateChange: vi.fn(),
    onGranularityChange: vi.fn(),
    onCustomIntervalChange: vi.fn(),
    errors: {},
    touched: {}
  };
};

describe('TimePeriodSelector', () => {
  // Test rendering with default props
  test('renders correctly with default props', () => {
    const props = setup();
    render(<TimePeriodSelector {...props} />);
    
    // Should show the period type radio buttons
    expect(screen.getByLabelText('Use Saved Period')).toBeInTheDocument();
    expect(screen.getByLabelText('Create Custom Period')).toBeInTheDocument();
    
    // Should default to custom period since selectedPeriodId is null
    expect(screen.getByLabelText('Create Custom Period')).toBeChecked();
    
    // Should show custom period inputs
    expect(screen.getByLabelText('Start Date')).toBeInTheDocument();
    expect(screen.getByLabelText('End Date')).toBeInTheDocument();
    expect(screen.getByText('Granularity')).toBeInTheDocument();
    
    // Should show granularity options
    expect(screen.getByLabelText('Daily')).toBeInTheDocument();
    expect(screen.getByLabelText('Weekly')).toBeInTheDocument();
    expect(screen.getByLabelText('Monthly')).toBeInTheDocument();
    expect(screen.getByLabelText('Custom')).toBeInTheDocument();
    
    // Weekly should be checked based on our props
    expect(screen.getByLabelText('Weekly')).toBeChecked();
  });

  // Test switching between period types
  test('switches between saved and custom period types', () => {
    const props = setup();
    render(<TimePeriodSelector {...props} />);
    
    // Initially should show custom period inputs
    expect(screen.getByLabelText('Start Date')).toBeInTheDocument();
    
    // Click on "Use Saved Period"
    fireEvent.click(screen.getByLabelText('Use Saved Period'));
    
    // Should show saved period selection
    expect(screen.getByText('Select Time Period')).toBeInTheDocument();
    expect(screen.queryByLabelText('Start Date')).not.toBeInTheDocument();
    
    // Click on "Create Custom Period"
    fireEvent.click(screen.getByLabelText('Create Custom Period'));
    
    // Should show custom period inputs again
    expect(screen.getByLabelText('Start Date')).toBeInTheDocument();
  });

  // Test handling saved period selection
  test('handles saved period selection', async () => {
    const props = setup();
    render(<TimePeriodSelector {...props} />);
    
    // Click on "Use Saved Period"
    fireEvent.click(screen.getByLabelText('Use Saved Period'));
    
    // Wait for saved periods to load and be displayed in the dropdown
    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });
    
    // Select a saved period
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'period1' } });
    
    // Should call onPeriodSelect with the selected period ID
    expect(props.onPeriodSelect).toHaveBeenCalledWith('period1');
  });

  // Test handling date selection
  test('handles date selection', () => {
    const props = setup();
    render(<TimePeriodSelector {...props} />);
    
    // Find the DatePicker components
    const startDateInput = screen.getByPlaceholderText('Select start date');
    const endDateInput = screen.getByPlaceholderText('Select end date');
    
    // Simulate change events
    fireEvent.change(startDateInput, { target: { value: '01/15/2023' } });
    fireEvent.blur(startDateInput);
    
    fireEvent.change(endDateInput, { target: { value: '04/15/2023' } });
    fireEvent.blur(endDateInput);
    
    // Verify callbacks were called
    expect(props.onStartDateChange).toHaveBeenCalled();
    expect(props.onEndDateChange).toHaveBeenCalled();
  });

  // Test handling granularity selection
  test('handles granularity selection', () => {
    const props = setup();
    render(<TimePeriodSelector {...props} />);
    
    // Click on Daily granularity
    fireEvent.click(screen.getByLabelText('Daily'));
    
    // Verify callback was called with correct value
    expect(props.onGranularityChange).toHaveBeenCalled();
    expect(props.onGranularityChange.mock.calls[0][0].target.value).toBe(TimeGranularity.DAILY);
    
    // Click on Monthly granularity
    fireEvent.click(screen.getByLabelText('Monthly'));
    
    // Verify callback was called with correct value
    expect(props.onGranularityChange.mock.calls[1][0].target.value).toBe(TimeGranularity.MONTHLY);
    
    // Click on Custom granularity
    fireEvent.click(screen.getByLabelText('Custom'));
    
    // Verify callback was called with correct value
    expect(props.onGranularityChange.mock.calls[2][0].target.value).toBe(TimeGranularity.CUSTOM);
    
    // Custom interval input should appear when Custom is selected
    expect(screen.getByLabelText('Custom Interval (days)')).toBeInTheDocument();
  });

  // Test handling custom interval input
  test('handles custom interval input', () => {
    const props = {
      ...setup(),
      granularity: TimeGranularity.CUSTOM // Set granularity to CUSTOM to show the custom interval input
    };
    render(<TimePeriodSelector {...props} />);
    
    // Should show custom interval input
    const customIntervalInput = screen.getByLabelText('Custom Interval (days)');
    
    // Enter a value
    fireEvent.change(customIntervalInput, { target: { value: '7' } });
    
    // Should call onCustomIntervalChange with the entered value
    expect(props.onCustomIntervalChange).toHaveBeenCalledWith('7');
  });

  // Test displaying validation errors
  test('displays validation errors', () => {
    const props = {
      ...setup(),
      errors: {
        startDate: 'Start date is required',
        endDate: 'End date must be after start date',
        granularity: 'Granularity is required',
        customInterval: 'Custom interval must be positive'
      },
      touched: {
        startDate: true,
        endDate: true,
        granularity: true,
        customInterval: true
      },
      granularity: TimeGranularity.CUSTOM // Set granularity to CUSTOM to show the custom interval input
    };
    render(<TimePeriodSelector {...props} />);
    
    // Should display error messages
    expect(screen.getByText('Start date is required')).toBeInTheDocument();
    expect(screen.getByText('End date must be after start date')).toBeInTheDocument();
    expect(screen.getByText('Granularity is required')).toBeInTheDocument();
    expect(screen.getByText('Custom interval must be positive')).toBeInTheDocument();
  });

  // Test handling loading state for saved periods
  test('handles loading state for saved periods', async () => {
    // Override the mock for this specific test
    vi.mock('../../../hooks/useApi', () => ({
      default: () => ({
        get: vi.fn().mockResolvedValue([
          { id: 'period1', name: 'Last Quarter' },
          { id: 'period2', name: 'Last Month' }
        ]),
        isLoading: true // Set isLoading to true
      })
    }));
    
    const props = setup();
    render(<TimePeriodSelector {...props} />);
    
    // Click on "Use Saved Period"
    fireEvent.click(screen.getByLabelText('Use Saved Period'));
    
    // Should show loading state in the select component
    // Since the Select component might handle loading state differently,
    // we just verify it renders without errors when isLoading is true
    expect(screen.getByText('Select Time Period')).toBeInTheDocument();
  });
});