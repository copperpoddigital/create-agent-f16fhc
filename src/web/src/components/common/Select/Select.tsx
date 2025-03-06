import React, { useState, useRef, forwardRef, ReactNode } from 'react'; // ^18.2.0
import classNames from 'classnames'; // ^2.3.2
import Icon from '../Icon';
import useTheme from '../../../hooks/useTheme';

/**
 * Interface for select option items
 */
export interface SelectOption {
  /** The value of the option */
  value: string;
  /** The display label for the option */
  label: string;
  /** Whether the option is disabled */
  disabled?: boolean;
}

/**
 * Props interface for the Select component
 */
export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  /** The ID attribute for the select element */
  id?: string;
  /** The name attribute for the select element */
  name?: string;
  /** The current value of the select element */
  value?: string;
  /** Array of options to display in the dropdown */
  options: SelectOption[];
  /** Placeholder text to display when no option is selected */
  placeholder?: string;
  /** Whether the select element is disabled */
  disabled?: boolean;
  /** Whether the select element is required */
  required?: boolean;
  /** Whether the select element has valid data */
  isValid?: boolean;
  /** Whether the select element has invalid data */
  isInvalid?: boolean;
  /** Validation message to display */
  validationMessage?: string;
  /** The size of the select element */
  size?: 'sm' | 'md' | 'lg';
  /** Icon to display on the left side of the select element */
  leftIcon?: ReactNode;
  /** Whether the select element can be cleared */
  clearable?: boolean;
  /** Additional CSS class names to apply to the select element */
  className?: string;
  /** Test ID for automated testing */
  testId?: string;
  /** Event handler for when the select value changes */
  onChange?: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  /** Event handler for when the select value is cleared */
  onClear?: () => void;
  /** Event handler for when the select element receives focus */
  onFocus?: (event: React.FocusEvent<HTMLSelectElement>) => void;
  /** Event handler for when the select element loses focus */
  onBlur?: (event: React.FocusEvent<HTMLSelectElement>) => void;
}

/**
 * A customizable dropdown select component with support for validation states, icons, and clearable functionality
 */
const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      id,
      name,
      value,
      options,
      placeholder,
      disabled = false,
      required = false,
      isValid = false,
      isInvalid = false,
      validationMessage,
      size = 'md',
      leftIcon,
      clearable = false,
      className,
      testId = 'select',
      onChange,
      onClear,
      onFocus,
      onBlur,
      ...restProps
    },
    ref
  ) => {
    // Create a ref if one is not provided
    const selectRef = useRef<HTMLSelectElement>(null);
    const resolvedRef = ref || selectRef;

    // State to track focus
    const [isFocused, setIsFocused] = useState(false);

    // Get current theme context
    const { theme } = useTheme();

    // Handle focus event
    const handleFocus = (event: React.FocusEvent<HTMLSelectElement>) => {
      setIsFocused(true);
      if (onFocus) {
        onFocus(event);
      }
    };

    // Handle blur event
    const handleBlur = (event: React.FocusEvent<HTMLSelectElement>) => {
      setIsFocused(false);
      if (onBlur) {
        onBlur(event);
      }
    };

    // Handle clear button click
    const handleClear = (event: React.MouseEvent<HTMLButtonElement>) => {
      // Prevent event propagation to avoid triggering select dropdown
      event.stopPropagation();
      
      if (onClear) {
        onClear();
      }
      
      // Focus the select element after clearing
      if (resolvedRef && 'current' in resolvedRef && resolvedRef.current) {
        resolvedRef.current.focus();
      }
    };

    // Construct CSS class names
    const selectContainerClasses = classNames(
      'select-container',
      {
        [`select-container--${size}`]: size,
        'select-container--disabled': disabled,
        'select-container--valid': isValid,
        'select-container--invalid': isInvalid,
        'select-container--focused': isFocused,
        'select-container--with-icon': leftIcon,
        'select-container--clearable': clearable && value,
        'select-container--dark': theme === 'dark',
      },
      className
    );

    const selectClasses = classNames(
      'select',
      {
        [`select--${size}`]: size,
        'select--disabled': disabled,
        'select--valid': isValid,
        'select--invalid': isInvalid,
        'select--with-icon': leftIcon,
        'select--dark': theme === 'dark',
      }
    );

    return (
      <div className={selectContainerClasses}>
        {/* Left icon if provided */}
        {leftIcon && <div className="select-icon-left">{leftIcon}</div>}
        
        {/* Select element */}
        <select
          ref={resolvedRef}
          id={id}
          name={name}
          value={value}
          disabled={disabled}
          required={required}
          className={selectClasses}
          onChange={onChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          aria-invalid={isInvalid}
          aria-required={required}
          data-testid={testId}
          {...restProps}
        >
          {/* Placeholder option */}
          {placeholder && (
            <option value="" disabled={required}>
              {placeholder}
            </option>
          )}
          
          {/* Map through options */}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        
        {/* Dropdown arrow icon */}
        <div className="select-dropdown-icon">
          <Icon 
            name="arrow-down" 
            size={size === 'lg' ? 'md' : 'sm'} 
            color="currentColor"
            aria-hidden="true"
          />
        </div>
        
        {/* Clear button */}
        {clearable && value && (
          <button
            type="button"
            className="select-clear-button"
            onClick={handleClear}
            tabIndex={-1} // Prevent tabbing to the clear button
            aria-label="Clear selection"
            data-testid={`${testId}-clear-button`}
          >
            <Icon
              name="close"
              size="sm"
              aria-hidden="true"
            />
          </button>
        )}
        
        {/* Validation message */}
        {(isValid || isInvalid) && validationMessage && (
          <div
            className={classNames('select-validation-message', {
              'select-validation-message--valid': isValid,
              'select-validation-message--invalid': isInvalid,
            })}
          >
            {validationMessage}
          </div>
        )}
      </div>
    );
  }
);

// Display name for debugging
Select.displayName = 'Select';

export default Select;