import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import AuthLayout from '../../components/layout/AuthLayout';
import LoginForm from '../../components/forms/LoginForm';
import useAuth from '../../hooks/useAuth';
import { ROUTES } from '../../config/routes';

/**
 * The login page component for the Freight Price Movement Agent web application.
 * Provides the user interface for authentication, allowing users to enter
 * their credentials and access the system.
 * 
 * This component implements the login screen wireframe as specified in the technical
 * specifications and uses the OAuth 2.0/JWT-based authentication framework.
 */
const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { state } = useAuth();
  
  // Extract redirect path from location state or query params
  const from = (location.state as { from?: string })?.from;
  const redirectParam = new URLSearchParams(location.search).get('redirect');
  const redirectPath = from || redirectParam || ROUTES.DASHBOARD.path;
  
  // Redirect authenticated users
  useEffect(() => {
    if (state.isAuthenticated && state.user) {
      navigate(redirectPath, { replace: true });
    }
  }, [state.isAuthenticated, state.user, navigate, redirectPath]);
  
  return (
    <AuthLayout title="FREIGHT PRICE MOVEMENT AGENT">
      <LoginForm 
        onSuccess={() => navigate(redirectPath, { replace: true })}
        redirectPath={redirectPath}
      />
    </AuthLayout>
  );
};

export default LoginPage;