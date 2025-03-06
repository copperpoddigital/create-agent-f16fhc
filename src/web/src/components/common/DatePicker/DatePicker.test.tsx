import React from 'react';
import { act } from 'react-dom/test-utils';
import { format, addDays, subDays } from 'date-fns';
import DatePicker from './DatePicker';
import { render, screen, fireEvent, waitFor, userEvent } from '../../../utils/test-utils';
import { formatDate, parseDate } from '../../../utils/date-utils';
import { DATE_FORMATS, DEFAULT_DATE_FORMAT } from '../../../config/constants';

// Setup helper function for common test cases
const setup = (props = {}) => {
  const onChange = jest.fn();
  const onBlur = jest.fn();
  const utils = render(
    <DatePicker
      value={null}
      onChange={onChange}
      onBlur={onBlur}
      {...props}
    />
  );

  return {
    ...utils,
    onChange,
    onBlur,
    input: screen.getByRole('textbox'),
    calendarIcon: screen.getByLabelText('Toggle calendar')
  };
};

describe('DatePicker Component', () => {
  it('renders with default props', () => {
    const { input, calendarIcon } = setup();
    
    expect(input).toBeInTheDocument();
    expect(calendarIcon).toBeInTheDocument();
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument(); // Calendar not visible initially
  });

  it('displays label when provided', () => {
    const labelText = 'Test Label';
    const { getByText, input } = setup({ label: labelText, id: 'test-date' });
    
    const label = getByText(labelText);
    expect(label).toBeInTheDocument();
    expect(label.tagName).toBe('LABEL');
    expect(label).toHaveAttribute('for', 'test-date');
  });

  it('shows placeholder when no value is selected', () => {
    const placeholder = 'Choose a date';
    const { input } = setup({ placeholder });
    
    expect(input).toHaveAttribute('placeholder', placeholder);
  });

  it('displays formatted date when value is provided', () => {
    const testDate = new Date(2023, 5, 15); // June 15, 2023
    const { input } = setup({ value: testDate });
    
    expect(input).toHaveValue(formatDate(testDate, DEFAULT_DATE_FORMAT));
  });

  it('toggles calendar visibility when icon is clicked', () => {
    const { calendarIcon } = setup();
    
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    
    fireEvent.click(calendarIcon);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    
    fireEvent.click(calendarIcon);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('selects date when clicked in calendar', async () => {
    const { calendarIcon, onChange } = setup();
    
    // Open the calendar
    fireEvent.click(calendarIcon);
    
    // Find and click on a date (15th of the current month)
    const dateButton = screen.getByRole('gridcell', { name: new RegExp('15(st|th|nd|rd)') });
    fireEvent.click(dateButton);
    
    // Check that onChange was called with the selected date
    expect(onChange).toHaveBeenCalled();
    const selectedDate = onChange.mock.calls[0][0];
    expect(selectedDate.getDate()).toBe(15);
    
    // Calendar should be closed after selection
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('navigates between months in calendar', () => {
    const testDate = new Date();
    const { calendarIcon } = setup({ value: testDate });
    
    // Open the calendar
    fireEvent.click(calendarIcon);
    
    // Get current month display
    const currentMonthYear = format(testDate, 'MMMM yyyy');
    expect(screen.getByText(currentMonthYear)).toBeInTheDocument();
    
    // Click next month button
    const nextMonthButton = screen.getByLabelText('Next month');
    fireEvent.click(nextMonthButton);
    
    // Verify month changed
    const nextMonth = addDays(testDate, 31); // Approximate next month
    const nextMonthYear = format(nextMonth, 'MMMM yyyy');
    expect(screen.getByText(nextMonthYear)).toBeInTheDocument();
    
    // Click previous month button to go back
    const prevMonthButton = screen.getByLabelText('Previous month');
    fireEvent.click(prevMonthButton);
    
    // Verify month changed back
    expect(screen.getByText(currentMonthYear)).toBeInTheDocument();
  });

  it('handles manual date input', async () => {
    const { input, onChange, onBlur } = setup();
    const testDateStr = '06/15/2023';
    
    // Type in a date
    fireEvent.change(input, { target: { value: testDateStr } });
    
    // Trigger blur to process the input
    fireEvent.blur(input);
    
    // Check that onChange was called
    expect(onChange).toHaveBeenCalled();
    
    // The selected date should match what was typed
    const expectedDate = parseDate(testDateStr, DEFAULT_DATE_FORMAT);
    expect(onChange.mock.calls[0][0].toDateString()).toBe(expectedDate?.toDateString());
    
    // Blur handler should be called
    expect(onBlur).toHaveBeenCalled();
  });

  it('validates date input', async () => {
    const { input, onChange, onBlur } = setup();
    const invalidDateStr = 'not-a-date';
    
    // Type in an invalid date
    fireEvent.change(input, { target: { value: invalidDateStr } });
    
    // Trigger blur to process the input
    fireEvent.blur(input);
    
    // Check that onChange was called with null for invalid date
    expect(onChange).toHaveBeenCalledWith(null);
    
    // Input should be cleared after blur
    expect(input).toHaveValue('');
    
    // Blur handler should be called
    expect(onBlur).toHaveBeenCalled();
  });

  it('respects min and max date constraints', () => {
    const testDate = new Date(2023, 5, 15); // June 15, 2023
    const minDate = subDays(testDate, 5); // June 10, 2023
    const maxDate = addDays(testDate, 5); // June 20, 2023
    
    const { calendarIcon } = setup({ value: testDate, minDate, maxDate });
    
    // Open the calendar
    fireEvent.click(calendarIcon);
    
    // Dates before min and after max should be disabled
    const earlierDate = subDays(minDate, 1);
    const laterDate = addDays(maxDate, 1);
    
    // Find dates by format pattern that will appear in the aria-label
    const earlierDateLabel = format(earlierDate, 'PPPP');
    const laterDateLabel = format(laterDate, 'PPPP');
    
    // Find buttons with these dates and check if they're disabled
    const earlierDateButton = screen.getByLabelText(earlierDateLabel);
    const laterDateButton = screen.getByLabelText(laterDateLabel);
    
    expect(earlierDateButton).toHaveAttribute('disabled');
    expect(laterDateButton).toHaveAttribute('disabled');
    
    // Date within range should be enabled
    const validDateLabel = format(testDate, 'PPPP');
    const validDateButton = screen.getByLabelText(validDateLabel);
    expect(validDateButton).not.toHaveAttribute('disabled');
  });

  it('supports different date formats', () => {
    // Test with MM/DD/YYYY format
    const testDate = new Date(2023, 5, 15); // June 15, 2023
    const { input: mmddyyyyInput, rerender } = setup({ 
      value: testDate, 
      format: DATE_FORMATS.MM_DD_YYYY 
    });
    
    expect(mmddyyyyInput).toHaveValue('06/15/2023');
    
    // Test with DD/MM/YYYY format
    rerender(
      <DatePicker
        value={testDate}
        onChange={jest.fn()}
        format={DATE_FORMATS.DD_MM_YYYY}
      />
    );
    
    const ddmmyyyyInput = screen.getByRole('textbox');
    expect(ddmmyyyyInput).toHaveValue('15/06/2023');
    
    // Test with YYYY-MM-DD format
    rerender(
      <DatePicker
        value={testDate}
        onChange={jest.fn()}
        format={DATE_FORMATS.YYYY_MM_DD}
      />
    );
    
    const yyyymmddInput = screen.getByRole('textbox');
    expect(yyyymmddInput).toHaveValue('2023-06-15');
  });

  it('handles disabled state', () => {
    const { input, calendarIcon } = setup({ disabled: true });
    
    expect(input).toBeDisabled();
    
    // Calendar shouldn't open when icon is clicked in disabled state
    fireEvent.click(calendarIcon);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    
    // Typing should be prevented
    fireEvent.change(input, { target: { value: '06/15/2023' } });
    expect(input).toHaveValue(''); // Input value shouldn't change
  });

  it('handles read-only state', () => {
    const { input, calendarIcon } = setup({ readOnly: true });
    
    expect(input).toHaveAttribute('readOnly');
    
    // Calendar shouldn't open when icon is clicked in read-only state
    fireEvent.click(calendarIcon);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    
    // Typing should be prevented
    fireEvent.change(input, { target: { value: '06/15/2023' } });
    expect(input).toHaveValue(''); // Input value shouldn't change
  });

  it('supports keyboard navigation in calendar', async () => {
    const user = userEvent.setup();
    const { calendarIcon, onChange } = setup();
    
    // Open the calendar
    fireEvent.click(calendarIcon);
    
    // The calendar should be in focus
    const calendar = screen.getByRole('dialog');
    
    // Simulate keyboard navigation
    await act(async () => {
      // Press arrow keys to navigate
      await user.keyboard('{ArrowRight}');
      await user.keyboard('{ArrowDown}');
      
      // Press Enter to select the focused date
      await user.keyboard('{Enter}');
    });
    
    // Check that onChange was called
    expect(onChange).toHaveBeenCalled();
    
    // Calendar should be closed after selection
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    
    // Open calendar again to test Escape key
    fireEvent.click(calendarIcon);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    
    // Press Escape to close
    await act(async () => {
      await user.keyboard('{Escape}');
    });
    
    // Calendar should be closed
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('closes calendar when clicking outside', () => {
    const { calendarIcon } = setup();
    
    // Open the calendar
    fireEvent.click(calendarIcon);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    
    // Simulate click outside
    fireEvent.mouseDown(document.body);
    
    // Calendar should be closed
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('shows validation state correctly', () => {
    // Test valid state
    const { input: validInput, rerender } = setup({ 
      isValid: true,
      value: new Date()
    });
    
    expect(validInput.parentElement?.parentElement).toHaveClass('is-valid');
    
    // Test invalid state
    rerender(
      <DatePicker
        value={null}
        onChange={jest.fn()}
        isInvalid={true}
        validationMessage="Please enter a valid date"
      />
    );
    
    const invalidInput = screen.getByRole('textbox');
    expect(invalidInput.parentElement?.parentElement).toHaveClass('is-invalid');
    
    // Check validation message is displayed
    expect(screen.getByText('Please enter a valid date')).toBeInTheDocument();
  });
});