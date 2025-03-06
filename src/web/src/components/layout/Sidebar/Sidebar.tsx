import React from 'react';
import { NavLink, useLocation } from 'react-router-dom'; // ^6.10.0
import classNames from 'classnames'; // ^2.3.2

import Icon from '../../common/Icon';
import useAuth from '../../../hooks/useAuth';
import { ROUTES, isRouteAccessible } from '../../../config/routes';

/**
 * Props interface for the Sidebar component
 */
interface SidebarProps {
  expanded: boolean;
  onToggle: () => void;
}

/**
 * Interface for navigation items in the sidebar
 */
interface NavigationItem {
  path: string;
  icon: string;
  title: string;
  route: typeof ROUTES[keyof typeof ROUTES];
}

/**
 * Sidebar component that provides navigation links for the application
 */
const Sidebar: React.FC<SidebarProps> = ({ expanded, onToggle }) => {
  const location = useLocation();
  const { state: authState } = useAuth();
  
  // Get user role
  const userRole = authState.user?.role || null;
  
  // Map user role to route role
  const roleMapping: Record<string, string> = {
    'admin': 'Administrator',
    'manager': 'Data Manager',
    'analyst': 'Analyst',
    'viewer': 'Viewer'
  };
  
  // Get the mapped role string
  const mappedRole = userRole ? roleMapping[userRole] || null : null;

  // Define navigation items
  const navigationItems: NavigationItem[] = [
    { path: ROUTES.DASHBOARD.path, icon: 'chart', title: 'Dashboard', route: ROUTES.DASHBOARD },
    { path: ROUTES.DATA_SOURCES.path, icon: 'import', title: 'Data Sources', route: ROUTES.DATA_SOURCES },
    { path: ROUTES.ANALYSIS.path, icon: 'chart', title: 'Analysis', route: ROUTES.ANALYSIS },
    { path: ROUTES.REPORTS.path, icon: 'export', title: 'Reports', route: ROUTES.REPORTS },
    { path: ROUTES.SETTINGS.path, icon: 'settings', title: 'Settings', route: ROUTES.SETTINGS },
  ];

  // Filter navigation items based on user permissions
  const accessibleItems = navigationItems.filter(item => 
    isRouteAccessible(item.route, mappedRole)
  );

  return (
    <aside 
      className={classNames('sidebar', { 
        'sidebar--expanded': expanded,
        'sidebar--collapsed': !expanded
      })}
      data-testid="sidebar"
    >
      {/* Logo and brand */}
      <div className="sidebar__brand">
        <div className="sidebar__logo">
          <Icon name="chart" size="lg" />
        </div>
        {expanded && <span className="sidebar__brand-name">Freight Price Movement Agent</span>}
      </div>

      {/* Toggle button */}
      <button 
        className="sidebar__toggle" 
        onClick={onToggle}
        aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
      >
        <Icon name={expanded ? "arrow-left" : "arrow-right"} />
      </button>

      {/* Navigation items */}
      <nav className="sidebar__nav">
        <ul className="sidebar__nav-list">
          {accessibleItems.map((item) => (
            <li className="sidebar__nav-item" key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) => 
                  classNames('sidebar__nav-link', {
                    'sidebar__nav-link--active': isActive
                  })
                }
                title={!expanded ? item.title : undefined}
              >
                <span className="sidebar__nav-icon">
                  <Icon name={item.icon} />
                </span>
                {expanded && (
                  <span className="sidebar__nav-text">{item.title}</span>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;