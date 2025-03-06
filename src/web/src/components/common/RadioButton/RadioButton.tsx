import React from 'react';
import classNames from 'classnames'; // v2.3.2

/**
 * Props interface for the RadioButton component
 */
interface RadioButtonProps {
  id: string;
  name: string;
  value: string;
  label: string;
  checked: boolean;
  disabled?: boolean;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  error?: string;
}

/**
 * A reusable radio button component that provides a styled, accessible radio input
 * for selecting a single option from a group of choices.
 * 
 * This component follows the design system guidelines and supports various states
 * including checked, disabled, and error states.
 */
const RadioButton: React.FC<RadioButtonProps> = ({
  id,
  name,
  value,
  label,
  checked,
  disabled = false,
  onChange,
  className,
  error,
}) => {
  const radioClasses = classNames(
    'custom-radio',
    {
      'is-checked': checked,
      'is-disabled': disabled,
      'has-error': !!error
    },
    className
  );

  return (
    <div className={radioClasses}>
      <input
        id={id}
        type="radio"
        name={name}
        value={value}
        checked={checked}
        disabled={disabled}
        onChange={onChange}
        className="custom-radio-input"
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
      />
      <label htmlFor={id} className="custom-radio-label">
        {label}
      </label>
      {error && (
        <div 
          id={`${id}-error`} 
          className="validation-message is-invalid"
          role="alert"
        >
          {error}
        </div>
      )}
    </div>
  );
};

export default RadioButton;