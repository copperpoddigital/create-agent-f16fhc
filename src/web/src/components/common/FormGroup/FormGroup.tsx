import React, { useMemo } from 'react';
import classNames from 'classnames'; // v2.3.2

/**
 * Props interface for the FormGroup component
 */
interface FormGroupProps {
  /** ID to be applied to the form control and associated with the label */
  id?: string;
  /** Label text for the form control */
  label?: string;
  /** Additional help text to display below the form control */
  helpText?: string;
  /** Whether the form control is required, displays a required indicator (*) */
  required?: boolean;
  /** Whether the form control has valid data, displays success styling */
  isValid?: boolean;
  /** Whether the form control has invalid data, displays error styling */
  isInvalid?: boolean;
  /** Validation message to display below the form control */
  validationMessage?: string;
  /** Additional CSS class names to apply to the form group container */
  className?: string;
  /** Form control element(s) to be wrapped by the form group */
  children: React.ReactNode;
}

/**
 * A container component for form elements that provides consistent layout, labeling, and validation display.
 * 
 * This component implements the form group pattern from the UI component library, providing
 * consistent styling and accessibility features for form elements throughout the application.
 */
const FormGroup: React.FC<FormGroupProps> = ({
  id: propId,
  label,
  helpText,
  required = false,
  isValid = false,
  isInvalid = false,
  validationMessage,
  className,
  children,
}) => {
  // Generate a unique ID for the form control if not provided
  const id = useMemo(() => propId || `form-control-${Math.random().toString(36).substring(2, 9)}`, [propId]);
  
  // Generate IDs for help text and validation message for ARIA attributes
  const helpTextId = helpText ? `${id}-help-text` : undefined;
  const validationMessageId = validationMessage && isInvalid ? `${id}-validation-message` : undefined;
  
  // Construct CSS class names based on props
  const groupClassName = classNames(
    'form-group',
    {
      'is-valid': isValid,
      'is-invalid': isInvalid,
    },
    className
  );

  // Determine the describedby value for accessibility
  const describedByIds = [
    helpTextId,
    validationMessageId
  ].filter(Boolean);
  const describedBy = describedByIds.length > 0 ? describedByIds.join(' ') : undefined;

  // Apply accessibility attributes to children
  const accessibleChildren = React.Children.map(children, child => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child, {
        id,
        'aria-required': required || undefined,
        'aria-invalid': isInvalid || undefined,
        'aria-describedby': describedBy || undefined,
      });
    }
    return child;
  });

  return (
    <div className={groupClassName}>
      {label && (
        <label htmlFor={id} className={classNames('form-label', { required })}>
          {label}
        </label>
      )}
      
      {accessibleChildren}
      
      {helpText && (
        <div id={helpTextId} className="form-text">
          {helpText}
        </div>
      )}
      
      {validationMessage && isInvalid && (
        <div id={validationMessageId} className="validation-message is-invalid">
          {validationMessage}
        </div>
      )}
    </div>
  );
};

export default FormGroup;