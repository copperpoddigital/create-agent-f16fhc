import React from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import Button from '../../components/common/Button';
import { ROUTES } from '../../config/routes';

/**
 * Component that renders a 404 Not Found page when users navigate to a non-existent route
 * 
 * @returns The rendered NotFoundPage component
 */
const NotFoundPage: React.FC = () => {
  // Get the navigate function from useNavigate hook
  const navigate = useNavigate();
  
  // Create a handler function to navigate to the dashboard
  const handleGoHome = () => {
    navigate(ROUTES.DASHBOARD.path);
  };
  
  return (
    <MainLayout>
      <PageHeader title="404 - Page Not Found" />
      
      <div className="not-found-page">
        <div className="not-found-page__content">
          <p className="not-found-page__message">
            The page you are looking for does not exist or has been moved.
          </p>
          
          <Button 
            variant="primary" 
            onClick={handleGoHome}
          >
            Go to Dashboard
          </Button>
        </div>
      </div>
    </MainLayout>
  );
};

export default NotFoundPage;