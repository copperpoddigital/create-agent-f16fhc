import React, { useId } from 'react';
import classNames from 'classnames'; // ^2.3.2
import { useThemeContext } from '../../../contexts/ThemeContext';

/**
 * Props interface for the Checkbox component
 */
interface CheckboxProps {
  /** The ID attribute for the checkbox input, used for label association */
  id?: string;
  /** The name attribute for the checkbox input, used for form submission */
  name?: string;
  /** The label text to display next to the checkbox */
  label?: string;
  /** Whether the checkbox is checked */
  checked?: boolean;
  /** Whether the checkbox is disabled */
  disabled?: boolean;
  /** Whether the checkbox has valid data, displays success styling */
  isValid?: boolean;
  /** Whether the checkbox has invalid data, displays error styling */
  isInvalid?: boolean;
  /** Validation message to display (error or success message) */
  validationMessage?: string;
  /** Additional CSS class names to apply to the checkbox container */
  className?: string;
  /** Event handler called when the checkbox state changes */
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

/**
 * A customizable checkbox component with support for labels, validation states, and theming
 * Used throughout the application for boolean selection inputs
 */
const Checkbox: React.FC<CheckboxProps> = ({
  id,
  name,
  label,
  checked = false,
  disabled = false,
  isValid = false,
  isInvalid = false,
  validationMessage,
  className,
  onChange,
}) => {
  // Access theme context (we rely on CSS variables set at the body level for theming)
  useThemeContext();
  
  // Generate a unique ID if one is not provided
  const uniqueId = useId();
  const checkboxId = id || `checkbox-${uniqueId}`;
  
  // Construct CSS class names based on component state
  const containerClasses = classNames(
    'checkbox-container',
    {
      'checkbox--disabled': disabled,
      'checkbox--valid': isValid && !isInvalid,
      'checkbox--invalid': isInvalid,
    },
    className
  );

  return (
    <div className={containerClasses}>
      <div className="checkbox-wrapper">
        {/* Hidden native checkbox for functionality */}
        <input
          type="checkbox"
          id={checkboxId}
          name={name}
          checked={checked}
          disabled={disabled}
          onChange={onChange}
          aria-invalid={isInvalid}
          aria-describedby={validationMessage ? `${checkboxId}-validation` : undefined}
          className="checkbox-input"
        />
        
        {/* Custom checkbox visual element */}
        <span 
          className={classNames('checkbox-custom', {
            'checkbox-custom--checked': checked,
            'checkbox-custom--disabled': disabled
          })} 
          aria-hidden="true"
        ></span>
        
        {/* Label text if provided */}
        {label && (
          <label htmlFor={checkboxId} className="checkbox-label">
            {label}
          </label>
        )}
      </div>
      
      {/* Validation message if provided */}
      {validationMessage && (
        <div 
          id={`${checkboxId}-validation`} 
          className={classNames('checkbox-validation', {
            'checkbox-validation--error': isInvalid,
            'checkbox-validation--success': isValid && !isInvalid,
          })}
        >
          {validationMessage}
        </div>
      )}
    </div>
  );
};

export default Checkbox;