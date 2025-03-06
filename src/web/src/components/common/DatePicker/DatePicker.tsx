import React, { useState, useRef, useEffect, forwardRef } from 'react';
import classNames from 'classnames'; // v2.3.2
import { format, parse, isValid, addMonths, subMonths, addDays, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isAfter, isBefore } from 'date-fns'; // v2.30.0

import FormGroup from '../FormGroup';
import Input from '../Input';
import Icon from '../Icon';
import { formatDate, parseDate, isValidDate } from '../../../utils/date-utils';
import { DATE_FORMATS, DEFAULT_DATE_FORMAT } from '../../../config/constants';

/**
 * Props interface for the DatePicker component
 */
interface DatePickerProps {
  /** Unique identifier for the date picker */
  id?: string;
  /** Name attribute for the input element */
  name?: string;
  /** Label text for the date picker */
  label?: string;
  /** Currently selected date */
  value: Date | null;
  /** Placeholder text for the input when no date is selected */
  placeholder?: string;
  /** Date format string (e.g., 'MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD') */
  format?: string;
  /** Whether the date picker is required */
  required?: boolean;
  /** Whether the date picker is disabled */
  disabled?: boolean;
  /** Whether the date picker is read-only */
  readOnly?: boolean;
  /** Minimum selectable date */
  minDate?: Date | null;
  /** Maximum selectable date */
  maxDate?: Date | null;
  /** Whether to show the calendar icon button */
  showCalendarIcon?: boolean;
  /** Whether the current value is valid */
  isValid?: boolean;
  /** Whether the current value is invalid */
  isInvalid?: boolean;
  /** Validation message to display */
  validationMessage?: string;
  /** Additional CSS class names */
  className?: string;
  /** Callback function when date changes */
  onChange: (date: Date | null) => void;
  /** Callback function when input loses focus */
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
}

/**
 * A date picker component that combines text input with a calendar popup for selecting dates
 */
const DatePicker = forwardRef<HTMLInputElement, DatePickerProps>((props, ref) => {
  const {
    id,
    name,
    label,
    value,
    placeholder = 'Select date...',
    format = DEFAULT_DATE_FORMAT,
    required = false,
    disabled = false,
    readOnly = false,
    minDate = null,
    maxDate = null,
    showCalendarIcon = true,
    isValid = false,
    isInvalid = false,
    validationMessage,
    className,
    onChange,
    onBlur,
  } = props;

  // State for input value and calendar visibility
  const [inputValue, setInputValue] = useState<string>(value ? formatDate(value, format) : '');
  const [isCalendarVisible, setIsCalendarVisible] = useState<boolean>(false);
  const [currentMonth, setCurrentMonth] = useState<Date>(value || new Date());
  const [focusedDate, setFocusedDate] = useState<Date | null>(null);

  // References for DOM elements and event handling
  const inputRef = useRef<HTMLInputElement>(null);
  const calendarRef = useRef<HTMLDivElement>(null);
  const clickListenerRef = useRef<(event: MouseEvent) => void>();

  // Update input value when value prop changes
  useEffect(() => {
    setInputValue(value ? formatDate(value, format) : '');
  }, [value, format]);

  // Handle outside clicks to close calendar
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        isCalendarVisible && 
        calendarRef.current && 
        !calendarRef.current.contains(event.target as Node) && 
        inputRef.current && 
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsCalendarVisible(false);
      }
    };

    clickListenerRef.current = handleClickOutside;
    
    if (isCalendarVisible) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    
    return () => {
      if (clickListenerRef.current) {
        document.removeEventListener('mousedown', clickListenerRef.current);
      }
    };
  }, [isCalendarVisible]);

  // Focus the first day of the month when calendar opens
  useEffect(() => {
    if (isCalendarVisible) {
      const firstDay = startOfMonth(currentMonth);
      setFocusedDate(firstDay);
    } else {
      setFocusedDate(null);
    }
  }, [isCalendarVisible, currentMonth]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newInputValue = e.target.value;
    setInputValue(newInputValue);

    if (newInputValue === '') {
      onChange(null);
      return;
    }

    if (isValidDate(newInputValue, format)) {
      const date = parseDate(newInputValue, format);
      if (date && isDateInRange(date)) {
        onChange(date);
        setCurrentMonth(date);
      }
    }
  };

  // Handle input blur
  const handleInputBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    // Validate and format on blur
    if (inputValue !== '' && !isValidDate(inputValue, format)) {
      // If invalid, revert to last valid value
      setInputValue(value ? formatDate(value, format) : '');
    } else if (inputValue !== '' && isValidDate(inputValue, format)) {
      // If valid but out of range, revert to last valid value
      const date = parseDate(inputValue, format);
      if (date && !isDateInRange(date)) {
        setInputValue(value ? formatDate(value, format) : '');
      }
    }

    if (onBlur) {
      onBlur(e);
    }
  };

  // Toggle calendar visibility
  const toggleCalendar = () => {
    if (!disabled && !readOnly) {
      const newIsVisible = !isCalendarVisible;
      setIsCalendarVisible(newIsVisible);
      
      if (newIsVisible && value) {
        setCurrentMonth(value);
      }
    }
  };

  // Handle date selection from calendar
  const handleDateSelect = (date: Date) => {
    if (isDateInRange(date)) {
      onChange(date);
      setInputValue(formatDate(date, format));
      setIsCalendarVisible(false);
      inputRef.current?.focus();
    }
  };

  // Navigate to previous month
  const handlePrevMonth = () => {
    setCurrentMonth(prevMonth => subMonths(prevMonth, 1));
  };

  // Navigate to next month
  const handleNextMonth = () => {
    setCurrentMonth(prevMonth => addMonths(prevMonth, 1));
  };

  // Check if a date is disabled (outside min/max range)
  const isDateDisabled = (date: Date): boolean => {
    if (minDate && isBefore(date, minDate)) {
      return true;
    }
    if (maxDate && isAfter(date, maxDate)) {
      return true;
    }
    return false;
  };

  // Check if a date is in the allowed range
  const isDateInRange = (date: Date): boolean => {
    return !isDateDisabled(date);
  };

  // Handle keyboard navigation in calendar
  const handleCalendarKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!focusedDate) return;

    let newFocusedDate = focusedDate;
    let handled = true;
    
    switch (e.key) {
      case 'ArrowLeft':
        newFocusedDate = addDays(focusedDate, -1);
        break;
      case 'ArrowRight':
        newFocusedDate = addDays(focusedDate, 1);
        break;
      case 'ArrowUp':
        newFocusedDate = addDays(focusedDate, -7);
        break;
      case 'ArrowDown':
        newFocusedDate = addDays(focusedDate, 7);
        break;
      case 'Home':
        newFocusedDate = startOfMonth(focusedDate);
        break;
      case 'End':
        newFocusedDate = endOfMonth(focusedDate);
        break;
      case 'PageUp':
        newFocusedDate = subMonths(focusedDate, 1);
        break;
      case 'PageDown':
        newFocusedDate = addMonths(focusedDate, 1);
        break;
      case 'Enter':
      case ' ':
        if (!isDateDisabled(focusedDate)) {
          handleDateSelect(focusedDate);
        }
        break;
      case 'Escape':
        setIsCalendarVisible(false);
        inputRef.current?.focus();
        break;
      default:
        handled = false;
        break;
    }
    
    if (handled) {
      e.preventDefault();
      
      // If the new focused date is in a different month, update current month
      if (newFocusedDate.getMonth() !== currentMonth.getMonth() || 
          newFocusedDate.getFullYear() !== currentMonth.getFullYear()) {
        setCurrentMonth(newFocusedDate);
      }
      
      setFocusedDate(newFocusedDate);
    }
  };

  // Render calendar popup
  const renderCalendar = () => {
    if (!isCalendarVisible) return null;

    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(monthStart);
    
    // Get all days in the month
    const days = eachDayOfInterval({ start: monthStart, end: monthEnd });
    
    // Calculate the first day of the week (0-6, 0 = Sunday)
    const startDayOfWeek = monthStart.getDay();
    
    // Add padding days at the start
    const paddingDaysBefore = new Array(startDayOfWeek).fill(null);
    
    // Calculate days for each week row (7 days per week)
    const daysByWeek: (Date | null)[][] = [];
    const allDays = [...paddingDaysBefore, ...days];
    
    while (allDays.length > 0) {
      daysByWeek.push(allDays.splice(0, 7));
    }
    
    // If the last row is not complete, add padding
    const lastWeek = daysByWeek[daysByWeek.length - 1];
    if (lastWeek.length < 7) {
      const paddingDaysAfter = new Array(7 - lastWeek.length).fill(null);
      daysByWeek[daysByWeek.length - 1] = [...lastWeek, ...paddingDaysAfter];
    }
    
    const weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

    return (
      <div 
        ref={calendarRef} 
        className="datepicker__calendar" 
        onKeyDown={handleCalendarKeyDown}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-label="Date picker"
      >
        <div className="datepicker__header">
          <button 
            type="button" 
            className="datepicker__nav datepicker__nav--prev" 
            onClick={handlePrevMonth}
            aria-label="Previous month"
          >
            <Icon name="arrow-left" size="sm" />
          </button>
          <div className="datepicker__current-month">
            {format(currentMonth, 'MMMM yyyy')}
          </div>
          <button 
            type="button" 
            className="datepicker__nav datepicker__nav--next" 
            onClick={handleNextMonth}
            aria-label="Next month"
          >
            <Icon name="arrow-right" size="sm" />
          </button>
        </div>
        
        <div className="datepicker__weekdays" role="row">
          {weekdays.map(day => (
            <div key={day} className="datepicker__weekday" role="columnheader" aria-label={day}>
              {day}
            </div>
          ))}
        </div>
        
        <div className="datepicker__days" role="grid">
          {daysByWeek.map((week, weekIndex) => (
            <div key={weekIndex} className="datepicker__week" role="row">
              {week.map((day, dayIndex) => {
                if (!day) {
                  return (
                    <div 
                      key={`empty-${dayIndex}`} 
                      className="datepicker__day datepicker__day--empty" 
                      role="gridcell"
                      aria-hidden="true"
                    />
                  );
                }
                
                const isSelected = value ? isSameDay(day, value) : false;
                const isDisabled = isDateDisabled(day);
                const isToday = isSameDay(day, new Date());
                const isFocused = focusedDate ? isSameDay(day, focusedDate) : false;
                
                return (
                  <button
                    key={format(day, 'yyyy-MM-dd')}
                    type="button"
                    className={classNames(
                      'datepicker__day',
                      {
                        'datepicker__day--selected': isSelected,
                        'datepicker__day--today': isToday,
                        'datepicker__day--disabled': isDisabled,
                        'datepicker__day--focused': isFocused && !isSelected,
                      }
                    )}
                    onClick={() => handleDateSelect(day)}
                    disabled={isDisabled}
                    tabIndex={isFocused ? 0 : -1}
                    aria-selected={isSelected}
                    aria-disabled={isDisabled}
                    aria-label={format(day, 'PPPP')} // Full date format for screen readers
                    role="gridcell"
                  >
                    {format(day, 'd')}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <FormGroup
      id={id}
      label={label}
      required={required}
      isValid={isValid}
      isInvalid={isInvalid}
      validationMessage={validationMessage}
      className={classNames('datepicker', className)}
    >
      <div className="datepicker__input-container">
        <Input
          ref={ref || inputRef}
          id={id}
          name={name}
          type="text"
          value={inputValue}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readOnly}
          required={required}
          isValid={isValid}
          isInvalid={isInvalid}
          onChange={handleInputChange}
          onBlur={handleInputBlur}
          onClick={() => {
            if (!readOnly && !disabled) {
              setIsCalendarVisible(true);
            }
          }}
          aria-haspopup="dialog"
          aria-expanded={isCalendarVisible}
          rightIcon={
            showCalendarIcon ? (
              <button
                type="button"
                className={classNames('datepicker__calendar-button', { 
                  'datepicker__calendar-button--disabled': disabled || readOnly 
                })}
                onClick={toggleCalendar}
                tabIndex={-1}
                aria-label="Toggle calendar"
                disabled={disabled || readOnly}
              >
                <Icon name="calendar" size="sm" />
              </button>
            ) : undefined
          }
        />
        {renderCalendar()}
      </div>
    </FormGroup>
  );
});

DatePicker.displayName = 'DatePicker';

export default DatePicker;