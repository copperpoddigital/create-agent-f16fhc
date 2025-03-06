import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import classNames from 'classnames'; // ^2.3.2

import Button from '../../common/Button';
import Icon from '../../common/Icon';
import useAuth from '../../../hooks/useAuth';
import useTheme from '../../../hooks/useTheme';

/**
 * Props interface for the Header component
 */
interface HeaderProps {
  toggleSidebar: () => void;
  isSidebarExpanded: boolean;
}

/**
 * Header component that displays at the top of the application layout.
 * Provides navigation, user information, theme switching, and application controls.
 */
const Header: React.FC<HeaderProps> = ({ toggleSidebar, isSidebarExpanded }) => {
  // Get authentication state and logout function
  const { state: authState, logout } = useAuth();
  
  // Get theme state and theme functions
  const { theme, toggleTheme } = useTheme();
  
  // Get navigation function
  const navigate = useNavigate();
  
  // State for user menu dropdown
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  
  // Reference to the user menu dropdown for click outside detection
  const userMenuRef = useRef<HTMLDivElement>(null);
  
  // Handle click outside to close user menu
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };
    
    // Add event listener only when menu is open
    if (isUserMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    
    // Cleanup event listener
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isUserMenuOpen]);
  
  /**
   * Toggles the user menu dropdown
   */
  const handleUserMenuToggle = () => {
    setIsUserMenuOpen(!isUserMenuOpen);
  };
  
  /**
   * Handles user logout
   */
  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };
  
  /**
   * Handles theme toggling
   */
  const handleThemeToggle = () => {
    toggleTheme();
  };
  
  /**
   * Navigates to settings page
   */
  const handleSettings = () => {
    navigate('/settings');
  };
  
  /**
   * Navigates to help/documentation
   */
  const handleHelp = () => {
    navigate('/help');
  };
  
  // Get user display name
  const userDisplayName = authState.user 
    ? `${authState.user.firstName || ''} ${authState.user.lastName || ''}`.trim() || authState.user.username 
    : 'User';
  
  return (
    <header className="header">
      <div className="header__container">
        {/* Left section with logo and sidebar toggle */}
        <div className="header__left">
          <button 
            className="header__sidebar-toggle"
            onClick={toggleSidebar}
            aria-label={isSidebarExpanded ? 'Collapse sidebar' : 'Expand sidebar'}
            data-testid="sidebar-toggle"
          >
            <Icon name="hamburger" size="md" aria-hidden="true" />
          </button>
          
          <Link to="/dashboard" className="header__logo">
            <h1 className="header__title">Freight Price Movement Agent</h1>
          </Link>
        </div>
        
        {/* Right section with actions and user info */}
        <div className="header__right">
          {/* Theme toggle button */}
          <Button 
            variant="link" 
            className="header__action-button"
            onClick={handleThemeToggle}
            ariaLabel="Toggle theme"
            data-testid="theme-toggle"
          >
            <Icon 
              name="equals" 
              size="md"
              aria-hidden="true" 
            />
          </Button>
          
          {/* Help button */}
          <Button 
            variant="link" 
            className="header__action-button"
            onClick={handleHelp}
            ariaLabel="Help"
            data-testid="help-button"
          >
            <Icon 
              name="question" 
              size="md"
              aria-hidden="true" 
            />
          </Button>
          
          {/* User menu */}
          <div className="header__user-menu" ref={userMenuRef}>
            <button 
              className="header__user-button"
              onClick={handleUserMenuToggle}
              aria-expanded={isUserMenuOpen}
              aria-haspopup="true"
              data-testid="user-menu-button"
            >
              <Icon 
                name="at" 
                className="header__user-icon" 
                size="md"
                aria-hidden="true" 
              />
              <span className="header__user-name">
                {userDisplayName}
              </span>
              <Icon 
                name={isUserMenuOpen ? 'arrow-up' : 'arrow-down'} 
                className="header__dropdown-icon" 
                size="sm"
                aria-hidden="true" 
              />
            </button>
            
            {/* User dropdown menu */}
            {isUserMenuOpen && (
              <div className="header__dropdown" data-testid="user-dropdown">
                <div className="header__dropdown-header">
                  <span className="header__dropdown-username">
                    {authState.user?.username || 'User'}
                  </span>
                  <span className="header__dropdown-email">
                    {authState.user?.email || ''}
                  </span>
                </div>
                
                <div className="header__dropdown-divider" />
                
                <button 
                  className="header__dropdown-item"
                  onClick={handleSettings}
                  data-testid="settings-button"
                >
                  <Icon 
                    name="settings" 
                    className="header__dropdown-icon" 
                    size="md"
                    aria-hidden="true" 
                  />
                  <span>Settings</span>
                </button>
                
                <button 
                  className="header__dropdown-item"
                  onClick={handleLogout}
                  data-testid="logout-button"
                >
                  <Icon 
                    name="arrow-right" 
                    className="header__dropdown-icon" 
                    size="md"
                    aria-hidden="true" 
                  />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;