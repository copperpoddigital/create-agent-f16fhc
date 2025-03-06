import React from 'react';
import classNames from 'classnames'; // v2.3.2
import Icon from '../Icon';

/**
 * Props interface for the Alert component
 */
export interface AlertProps {
  /** The content of the alert */
  children: React.ReactNode;
  /** The type/severity of the alert */
  type?: 'success' | 'error' | 'warning' | 'info';
  /** Optional title for the alert */
  title?: string;
  /** Whether the alert can be dismissed */
  dismissible?: boolean;
  /** Whether to show an icon based on the alert type */
  showIcon?: boolean;
  /** Callback function when the alert is dismissed */
  onDismiss?: () => void;
  /** Additional CSS class names to apply to the alert */
  className?: string;
  /** HTML ID attribute for the alert element */
  id?: string;
  /** Test ID for automated testing */
  testId?: string;
}

/**
 * A customizable alert component that displays notifications with different severity levels
 */
const Alert: React.FC<AlertProps> = ({
  children,
  type = 'info',
  title,
  dismissible = false,
  showIcon = true,
  onDismiss,
  className,
  id,
  testId = 'alert',
}) => {
  // Define the icon name based on alert type
  const iconMap: Record<string, string> = {
    success: 'check',
    error: 'error',
    warning: 'warning',
    info: 'info',
  };

  const iconName = iconMap[type] || 'info';

  // Construct CSS class names
  const alertClasses = classNames(
    'alert',
    `alert--${type}`,
    dismissible && 'alert--dismissible',
    className
  );

  // Handle dismiss button click
  const handleDismiss = () => {
    if (onDismiss) {
      onDismiss();
    }
  };

  return (
    <div
      className={alertClasses}
      role="alert"
      id={id}
      data-testid={testId}
    >
      {showIcon && (
        <div className="alert__icon">
          <Icon name={iconName} size="md" />
        </div>
      )}
      <div className="alert__content">
        {title && <h4 className="alert__title">{title}</h4>}
        <div className="alert__message">{children}</div>
      </div>
      {dismissible && (
        <button
          type="button"
          className="alert__dismiss"
          aria-label="Dismiss alert"
          onClick={handleDismiss}
        >
          <Icon name="close" size="sm" />
        </button>
      )}
    </div>
  );
};

export default Alert;