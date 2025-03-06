import React from 'react';
import classNames from 'classnames'; // v2.3.2

/**
 * Props interface for the Spinner component
 */
export interface SpinnerProps {
  /**
   * Size of the spinner: 'sm', 'md' (default), or 'lg'
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * Color of the spinner: 'primary' (default), 'secondary', or 'white'
   */
  color?: 'primary' | 'secondary' | 'white';
  /**
   * Whether the spinner should be displayed inline or as a block element
   */
  inline?: boolean;
  /**
   * Additional CSS class names to apply to the spinner
   */
  className?: string;
  /**
   * Accessibility label for screen readers
   */
  ariaLabel?: string;
}

/**
 * A loading spinner component that provides visual feedback during asynchronous operations.
 * This component relies on external CSS for the actual animation using keyframes.
 * 
 * @example
 * // Basic usage
 * <Spinner />
 * 
 * @example
 * // Custom size and color
 * <Spinner size="lg" color="secondary" />
 * 
 * @example
 * // Inline spinner with custom label
 * <Spinner inline ariaLabel="Loading data..." />
 */
const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  inline = false,
  className,
  ariaLabel = 'Loading...',
}) => {
  const spinnerClasses = classNames(
    'spinner',
    `spinner--${size}`,
    `spinner--${color}`,
    {
      'spinner--inline': inline,
    },
    className
  );

  return (
    <div 
      className={spinnerClasses} 
      role="status" 
      aria-label={ariaLabel}
    >
      <span className="spinner__visually-hidden">{ariaLabel}</span>
    </div>
  );
};

export default Spinner;