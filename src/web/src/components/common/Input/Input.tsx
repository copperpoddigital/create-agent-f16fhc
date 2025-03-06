import React, { forwardRef, useRef, useState, InputHTMLAttributes } from 'react';
import classNames from 'classnames'; // v2.3.2

type InputType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'date';
type InputSize = 'sm' | 'md' | 'lg';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /**
   * The ID attribute for the input element
   */
  id?: string;
  /**
   * The name attribute for the input element
   */
  name?: string;
  /**
   * The type of input
   */
  type?: InputType;
  /**
   * The current value of the input
   */
  value?: string;
  /**
   * Placeholder text to display when the input is empty
   */
  placeholder?: string;
  /**
   * The size of the input
   */
  size?: InputSize;
  /**
   * Whether the input is disabled
   */
  disabled?: boolean;
  /**
   * Whether the input is read-only
   */
  readOnly?: boolean;
  /**
   * Whether the input is required
   */
  required?: boolean;
  /**
   * Whether the input has valid data, displays success styling
   */
  isValid?: boolean;
  /**
   * Whether the input has invalid data, displays error styling
   */
  isInvalid?: boolean;
  /**
   * Whether the input should have a clear button when it has a value
   */
  clearable?: boolean;
  /**
   * Icon to display on the left side of the input
   */
  leftIcon?: React.ReactNode;
  /**
   * Icon to display on the right side of the input
   */
  rightIcon?: React.ReactNode;
  /**
   * Additional CSS class names to apply to the input
   */
  className?: string;
  /**
   * Accessible label for the input
   */
  ariaLabel?: string;
  /**
   * ID of the element that describes this input
   */
  ariaDescribedBy?: string;
  /**
   * Function to call when the input value changes
   */
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  /**
   * Function to call when the input loses focus
   */
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  /**
   * Function to call when the input gains focus
   */
  onFocus?: (e: React.FocusEvent<HTMLInputElement>) => void;
  /**
   * Function to call when the clear button is clicked
   */
  onClear?: () => void;
}

/**
 * A customizable text input component that supports different states, sizes, and additional features
 * like icons, clear button, and accessibility attributes.
 */
const Input = forwardRef<HTMLInputElement, InputProps>(({
  id,
  name,
  type = 'text',
  value,
  placeholder,
  size = 'md',
  disabled = false,
  readOnly = false,
  required = false,
  isValid = false,
  isInvalid = false,
  clearable = false,
  leftIcon,
  rightIcon,
  className,
  ariaLabel,
  ariaDescribedBy,
  onChange,
  onBlur,
  onFocus,
  onClear,
  ...rest
}, ref) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  
  // Handle clearing the input
  const handleClear = () => {
    // Call onClear callback
    if (onClear) {
      onClear();
    }
    
    // For controlled inputs, parent component should update value prop
    // For uncontrolled inputs, trigger onChange with empty value
    if (onChange) {
      const changeEvent = {
        target: {
          name,
          value: ''
        }
      } as React.ChangeEvent<HTMLInputElement>;
      onChange(changeEvent);
    }
  };
  
  // Set up classes for the input container
  const containerClasses = classNames(
    'input-container',
    `input-size-${size}`,
    {
      'input-valid': isValid,
      'input-invalid': isInvalid,
      'input-focused': isFocused,
      'input-disabled': disabled,
      'input-readonly': readOnly,
      'input-with-left-icon': leftIcon,
      'input-with-right-icon': rightIcon || (clearable && value),
    },
    className
  );
  
  // Set up classes for the input element
  const inputClasses = classNames(
    'input-field',
    {
      'input-field-with-left-icon': leftIcon,
      'input-field-with-right-icon': rightIcon || (clearable && value),
    }
  );
  
  // Handle custom focus events
  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true);
    if (onFocus) {
      onFocus(e);
    }
  };
  
  // Handle custom blur events
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    if (onBlur) {
      onBlur(e);
    }
  };
  
  const showClearButton = clearable && value && value.length > 0 && !disabled && !readOnly;
  
  // Determine if we need a container for icons
  const hasIcons = leftIcon || rightIcon || showClearButton;
  
  const inputElement = (
    <input
      ref={ref || inputRef}
      id={id}
      name={name}
      type={type}
      value={value}
      placeholder={placeholder}
      disabled={disabled}
      readOnly={readOnly}
      required={required}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      aria-invalid={isInvalid}
      aria-required={required}
      className={hasIcons ? inputClasses : containerClasses}
      onChange={onChange}
      onFocus={handleFocus}
      onBlur={handleBlur}
      {...rest}
    />
  );
  
  // Return plain input if no icons
  if (!hasIcons) {
    return inputElement;
  }
  
  // Return input with icons in a container
  return (
    <div className={containerClasses}>
      {leftIcon && <div className="input-icon input-icon-left" aria-hidden="true">{leftIcon}</div>}
      {inputElement}
      {showClearButton && (
        <button
          type="button"
          className="input-clear-button"
          onClick={handleClear}
          aria-label="Clear input"
          tabIndex={-1}
        >
          ✕
        </button>
      )}
      {rightIcon && <div className="input-icon input-icon-right" aria-hidden="true">{rightIcon}</div>}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;