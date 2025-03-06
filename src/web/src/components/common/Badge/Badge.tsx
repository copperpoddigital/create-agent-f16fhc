import React, { HTMLAttributes, ReactNode } from 'react';
import classNames from 'classnames'; // v2.3.2
import Icon from '../Icon';

/**
 * Props interface for the Badge component
 */
export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  /** The visual style variant of the badge */
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  /** The size of the badge */
  size?: 'sm' | 'md' | 'lg';
  /** Whether the badge has pill-shaped corners */
  pill?: boolean;
  /** Icon to display in the badge (icon name) */
  icon?: string;
  /** Additional CSS class names */
  className?: string;
  /** Content of the badge */
  children?: ReactNode;
  /** Test ID for automated testing */
  testId?: string;
}

/**
 * A customizable badge component that displays short status indicators, labels, or counts
 */
const Badge: React.FC<BadgeProps> = ({
  variant = 'primary',
  size = 'md',
  pill = false,
  icon,
  className,
  children,
  testId = 'badge',
  ...restProps
}) => {
  // Map badge size to icon size to ensure proper proportions
  const iconSize = size === 'lg' ? 'md' : 'sm';
  
  // Construct CSS class names based on props
  const badgeClassName = classNames(
    'badge',
    `badge--${variant}`,
    `badge--${size}`,
    pill && 'badge--pill',
    className
  );

  return (
    <span className={badgeClassName} data-testid={testId} {...restProps}>
      {icon && <Icon name={icon} size={iconSize} className="badge__icon" />}
      {children}
    </span>
  );
};

export default Badge;