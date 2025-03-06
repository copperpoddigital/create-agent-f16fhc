import React, { ReactNode } from 'react'; // ^18.2.0
import classNames from 'classnames'; // ^2.3.2
import { useThemeContext } from '../../../contexts/ThemeContext';

/**
 * Props interface for the Card component
 */
interface CardProps {
  /** Style variant of the card */
  variant?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'danger';
  /** Size of the card */
  size?: 'small' | 'medium' | 'large';
  /** Whether to show an outlined version of the card */
  outline?: boolean;
  /** Whether the card is clickable */
  clickable?: boolean;
  /** Custom header content */
  header?: ReactNode;
  /** Card title */
  title?: string;
  /** Card subtitle */
  subtitle?: string;
  /** Custom footer content */
  footer?: ReactNode;
  /** Card content */
  children?: ReactNode;
  /** Additional CSS class names */
  className?: string;
  /** Click handler for the card */
  onClick?: () => void;
  /** Test ID for testing purposes */
  testId?: string;
}

/**
 * A versatile card component that serves as a container for content with various styling options
 */
const Card: React.FC<CardProps> = ({
  variant,
  size,
  outline = false,
  clickable = false,
  header,
  title,
  subtitle,
  footer,
  children,
  className,
  onClick,
  testId = 'card',
}) => {
  // Access theme context for potential theme-specific styling
  const { theme } = useThemeContext();

  // Build the CSS class names
  const cardClasses = classNames(
    'card',
    {
      [`card-${variant}`]: variant,
      [`card-${size}`]: size,
      'card-outline': outline,
      'card-clickable': clickable,
    },
    className
  );

  // Handle card click
  const handleClick = () => {
    if (clickable && onClick) {
      onClick();
    }
  };

  return (
    <div 
      className={cardClasses}
      onClick={handleClick}
      tabIndex={clickable ? 0 : undefined}
      data-testid={testId}
      role={clickable ? 'button' : undefined}
      aria-label={clickable && title ? title : undefined}
    >
      {(title || subtitle || header) && (
        <div className="card-header">
          {header || (
            <>
              {title && <h3 className="card-title">{title}</h3>}
              {subtitle && <div className="card-subtitle">{subtitle}</div>}
            </>
          )}
        </div>
      )}
      <div className="card-body">
        {children}
      </div>
      {footer && (
        <div className="card-footer">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;