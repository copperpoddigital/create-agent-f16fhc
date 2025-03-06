import React from 'react'; // ^18.2.0
import { Navigate, Outlet } from 'react-router-dom'; // ^6.10.0
import useAuth from '../hooks/useAuth';
import { RouteConfig } from '../config/routes';

/**
 * A component that handles public routes, redirecting authenticated users to the dashboard
 * 
 * @param {object} props - Component props
 * @param {RouteConfig} props.routeConfig - The route configuration object
 * @returns {JSX.Element} Either the public route component or a redirect to the dashboard
 */
const PublicRoute: React.FC<{ routeConfig: RouteConfig }> = ({ routeConfig }) => {
  // Get the current authentication state using the useAuth hook
  const { state } = useAuth();

  // Check if the user is authenticated
  if (state.isAuthenticated) {
    // If authenticated, redirect to the dashboard
    return <Navigate to="/dashboard" replace />;
  }

  // If not authenticated, render the child routes using Outlet component
  return <Outlet />;
};

export default PublicRoute;