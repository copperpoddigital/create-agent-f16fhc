import React, { ButtonHTMLAttributes } from 'react';
import classNames from 'classnames'; // v2.3.2
import Spinner from '../Spinner';

/**
 * Props interface for the Button component
 */
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * The content to display inside the button
   */
  children: React.ReactNode;
  /**
   * The visual style variant of the button
   */
  variant?: 'primary' | 'secondary' | 'outline-primary' | 'outline-secondary' | 'success' | 'danger' | 'warning' | 'link';
  /**
   * The size of the button
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * Whether the button is disabled
   */
  disabled?: boolean;
  /**
   * Whether the button is in a loading state
   */
  isLoading?: boolean;
  /**
   * Whether the button should take up the full width of its container
   */
  fullWidth?: boolean;
  /**
   * Icon to display on the left side of the button text
   */
  leftIcon?: React.ReactNode;
  /**
   * Icon to display on the right side of the button text
   */
  rightIcon?: React.ReactNode;
  /**
   * Additional CSS class names to apply to the button
   */
  className?: string;
  /**
   * Accessible label for the button
   */
  ariaLabel?: string;
  /**
   * Function to call when the button is clicked
   */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

/**
 * A customizable button component that supports different variants, sizes, states, and icon placement.
 * 
 * @example
 * // Basic primary button
 * <Button>Click Me</Button>
 * 
 * @example
 * // Secondary button with loading state
 * <Button variant="secondary" isLoading>Processing</Button>
 * 
 * @example
 * // Button with left icon
 * <Button leftIcon={<Icon name="download" />}>Download Report</Button>
 */
const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled = false,
  isLoading = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  className,
  ariaLabel,
  onClick,
  ...rest
}) => {
  // Determine if the button should be disabled (explicitly disabled or in loading state)
  const isDisabled = disabled || isLoading;

  // Construct CSS class names based on props
  const buttonClasses = classNames(
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    {
      'btn--loading': isLoading,
      'btn--full-width': fullWidth,
      'btn--with-left-icon': leftIcon,
      'btn--with-right-icon': rightIcon,
    },
    className
  );

  // Handle click event, preventing it when button is loading
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (isLoading || !onClick) return;
    onClick(event);
  };

  return (
    <button
      type={type}
      className={buttonClasses}
      disabled={isDisabled}
      aria-label={ariaLabel}
      aria-busy={isLoading}
      aria-disabled={isDisabled}
      onClick={handleClick}
      {...rest}
    >
      {/* Loading spinner displayed when isLoading is true */}
      {isLoading && (
        <span className="btn__spinner">
          <Spinner size={size === 'lg' ? 'md' : 'sm'} color="white" inline />
        </span>
      )}
      
      {/* Left icon */}
      {leftIcon && <span className="btn__icon btn__icon--left">{leftIcon}</span>}
      
      {/* Button content (text) */}
      <span className="btn__content">{children}</span>
      
      {/* Right icon */}
      {rightIcon && <span className="btn__icon btn__icon--right">{rightIcon}</span>}
    </button>
  );
};

export default Button;