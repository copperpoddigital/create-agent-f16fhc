import React from 'react';
import { useNavigate } from 'react-router-dom'; // ^6.0.0

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import ReportList from '../../components/reports/ReportList';
import Button from '../../components/common/Button';
import Icon from '../../components/common/Icon';

/**
 * Component that renders the Reports page with a list of saved reports
 * 
 * @returns The rendered ReportsPage component
 */
const ReportsPage: React.FC = () => {
  // Initialize navigation for routing
  const navigate = useNavigate();

  /**
   * Handles navigation to the create report page
   */
  const handleCreateReport = () => {
    navigate('/reports/create');
  };

  /**
   * Handles navigation to the edit report page
   * 
   * @param id - The ID of the report to edit
   */
  const handleEditReport = (id: string) => {
    navigate(`/reports/edit/${id}`);
  };

  /**
   * Handles navigation to the report details page
   * 
   * @param id - The ID of the report to view
   */
  const handleViewReport = (id: string) => {
    navigate(`/reports/${id}`);
  };

  return (
    <MainLayout>
      {/* Page header with title and create report button */}
      <PageHeader
        title="Reports"
        actions={[
          <Button
            key="create-report"
            variant="primary"
            leftIcon={<Icon name="plus" />}
            onClick={handleCreateReport}
            ariaLabel="Create new report"
          >
            Create Report
          </Button>
        ]}
      />
      
      {/* Report list component with handlers for create, edit, and view actions */}
      <ReportList
        onCreateReport={handleCreateReport}
        onEditReport={handleEditReport}
        onViewReport={handleViewReport}
        aria-label="List of saved reports"
      />
    </MainLayout>
  );
};

export default ReportsPage;