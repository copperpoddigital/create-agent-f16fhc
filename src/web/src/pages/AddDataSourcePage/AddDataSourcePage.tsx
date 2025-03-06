import React from 'react'; // ^18.2.0
import { useNavigate } from 'react-router-dom'; // ^6.10.0

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import DataSourceForm from '../../components/forms/DataSourceForm';
import Button from '../../components/common/Button';
import useAlert from '../../hooks/useAlert';
import { ROUTES } from '../../config/routes';

/**
 * Page component for adding a new data source
 * @returns {JSX.Element} The rendered AddDataSourcePage component
 */
const AddDataSourcePage: React.FC = () => {
  // Initialize navigate function from useNavigate hook
  const navigate = useNavigate();

  // Initialize showAlert function from useAlert hook
  const { showSuccess, showError } = useAlert();

  /**
   * Define handleCancel function to navigate back to data sources page
   */
  const handleCancel = () => {
    navigate(ROUTES.DATA_SOURCES.path);
  };

  /**
   * Define handleSubmit function to handle form submission and navigate on success
   * @param {any} dataSource - The created data source object
   */
  const handleSubmit = (dataSource: any) => {
    navigate(ROUTES.DATA_SOURCES.path);
  };

  // Render the page with MainLayout, PageHeader, and DataSourceForm components
  return (
    <MainLayout>
      {/* Set up appropriate page title and back button in PageHeader */}
      <PageHeader
        title="Add Data Source"
        actions={[
          <Button variant="secondary" onClick={handleCancel}>
            <span data-testid="cancel-button">Cancel</span>
          </Button>,
        ]}
      />
      {/* Pass form submission and cancel handlers to DataSourceForm */}
      <DataSourceForm onSubmit={handleSubmit} onCancel={handleCancel} />
    </MainLayout>
  );
};

// Export the AddDataSourcePage component as the default export
export default AddDataSourcePage;