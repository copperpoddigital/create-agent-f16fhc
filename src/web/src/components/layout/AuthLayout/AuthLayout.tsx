import React, { ReactNode, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import classNames from 'classnames'; // ^2.3.2

import useAuth from '../../../hooks/useAuth';
import useMediaQuery from '../../../hooks/useMediaQuery';
import Alert from '../../common/Alert';
import { ROUTES } from '../../../config/routes';

/**
 * Props interface for the AuthLayout component
 */
interface AuthLayoutProps {
  /** The content to render within the layout */
  children: ReactNode;
  /** The main title displayed on the authentication page */
  title?: string;
  /** The subtitle displayed below the title */
  subtitle?: string;
  /** Additional CSS class names to apply to the layout */
  className?: string;
  /** Whether to redirect authenticated users to the dashboard */
  redirectAuthenticated?: boolean;
}

/**
 * A layout component that provides the structure for authentication-related pages
 * such as login, password reset, and registration in the Freight Price Movement 
 * Agent web application. This component creates a consistent, branded layout
 * for all authentication screens.
 */
const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  title = 'FREIGHT PRICE MOVEMENT AGENT',
  subtitle = '',
  className = '',
  redirectAuthenticated = true,
}) => {
  const { state } = useAuth();
  const navigate = useNavigate();
  const isMobile = useMediaQuery('(max-width: 767px)');

  // Redirect authenticated users to the dashboard if requested
  useEffect(() => {
    if (redirectAuthenticated && state.isAuthenticated && state.user) {
      navigate(ROUTES.DASHBOARD.path);
    }
  }, [state.isAuthenticated, state.user, navigate, redirectAuthenticated]);

  return (
    <div 
      className={classNames(
        'auth-layout',
        isMobile ? 'auth-layout--mobile' : '',
        className
      )}
      data-testid="auth-layout"
    >
      <div className="auth-layout__container">
        <div className="auth-layout__header">
          <h1 className="auth-layout__brand">
            {title}
          </h1>
          {subtitle && (
            <p className="auth-layout__subtitle">{subtitle}</p>
          )}
        </div>

        <div className="auth-layout__card">
          {children}
        </div>

        {state.error && (
          <div className="auth-layout__alert">
            <Alert 
              type="error" 
              title="Authentication Error"
              dismissible
              showIcon
            >
              {state.error}
            </Alert>
          </div>
        )}

        <div className="auth-layout__footer">
          <p className="auth-layout__footer-text">
            Please contact your administrator if you need access
          </p>
          <p className="auth-layout__copyright">
            &copy; {new Date().getFullYear()} Freight Price Movement Agent
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;