import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import { RouteConfig, isRouteAccessible, ROUTES } from '../config/routes';

/**
 * A higher-order component that protects routes requiring authentication in the
 * Freight Price Movement Agent web application.
 * 
 * This component checks if the user is authenticated and has the required role
 * permissions for accessing a protected route. If not authenticated, it redirects
 * to the login page with the current location stored for return after login.
 * If authenticated but lacking permission, it redirects to the dashboard.
 *
 * @param {Object} props - Component props
 * @param {RouteConfig} props.routeConfig - The route configuration object containing path and permission details
 * @returns {JSX.Element} Either the protected route component or a redirect
 */
const PrivateRoute: React.FC<{ routeConfig: RouteConfig }> = ({ routeConfig }) => {
  // Get the current authentication state using the useAuth hook
  const { state } = useAuth();
  
  // Get the current location to enable return to this URL after login
  const location = useLocation();
  
  // Check if the user is authenticated
  if (!state.isAuthenticated) {
    // Redirect to login page with the current location as the return URL
    return <Navigate to={ROUTES.LOGIN.path} state={{ from: location }} replace />;
  }
  
  // Check if the user has permission to access this route based on their role
  const userRole = state.user?.role || null;
  const hasAccess = isRouteAccessible(routeConfig, userRole);
  
  // If the user doesn't have permission, redirect to dashboard
  if (!hasAccess) {
    return <Navigate to={ROUTES.DASHBOARD.path} replace />;
  }
  
  // User is authenticated and has permission, render the child routes using Outlet
  return <Outlet />;
};

export default PrivateRoute;