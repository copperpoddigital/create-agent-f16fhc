import React, { ReactNode } from 'react';
import classNames from 'classnames'; // v2.3.2
import Button from '../../common/Button';
import Icon from '../../common/Icon';
import useMediaQuery from '../../../hooks/useMediaQuery';

/**
 * Props interface for the PageHeader component
 */
interface PageHeaderProps {
  /**
   * The title to display in the header
   */
  title: string;
  /**
   * Optional action buttons to display in the header
   */
  actions?: ReactNode[];
  /**
   * Additional CSS class names to apply to the header
   */
  className?: string;
}

/**
 * A page header component that displays a title and optional action buttons.
 * This component provides a consistent header structure across different pages
 * of the Freight Price Movement Agent application.
 *
 * @example
 * // Basic usage with just a title
 * <PageHeader title="Dashboard" />
 *
 * @example
 * // With actions
 * <PageHeader
 *   title="Data Sources"
 *   actions={[
 *     <Button leftIcon={<Icon name="plus" />}>Add Source</Button>,
 *     <Button variant="outline-primary">Export</Button>
 *   ]}
 * />
 */
const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  actions = [],
  className,
}) => {
  // Check if screen is mobile using media query
  const isMobile = useMediaQuery('(max-width: 767px)');

  // Construct CSS class names
  const headerClasses = classNames(
    'page-header',
    {
      'page-header--mobile': isMobile,
    },
    className
  );

  return (
    <header className={headerClasses}>
      <h1 className="page-header__title">{title}</h1>
      
      {actions.length > 0 && (
        <div 
          className={classNames('page-header__actions', {
            'page-header__actions--mobile': isMobile
          })}
          role="toolbar"
          aria-label="Page actions"
        >
          {actions.map((action, index) => (
            <div 
              key={index} 
              className={classNames('page-header__action', {
                'page-header__action--mobile': isMobile
              })}
            >
              {action}
            </div>
          ))}
        </div>
      )}
    </header>
  );
};

export default PageHeader;