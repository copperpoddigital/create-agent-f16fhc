# src/web/src/pages/EditDataSourcePage/EditDataSourcePage.tsx
```typescript
import React, { useState, useEffect } from 'react'; // ^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom
import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import DataSourceForm from '../../components/forms/DataSourceForm';
import Button from '../../components/common/Button';
import Spinner from '../../components/common/Spinner';
import useAlert from '../../hooks/useAlert';
import { getDataSourceById, updateDataSource } from '../../api/data-source-api';
import { ROUTES } from '../../config/routes';
import { DataSource } from '../../types/data-source.types';

/**
 * Page component for editing an existing data source
 */
const EditDataSourcePage: React.FC = () => {
  // Get the data source ID from URL parameters using useParams
  const { id } = useParams<{ id: string }>();

  // Initialize state for loading status and data source
  const [loading, setLoading] = useState<boolean>(true);
  const [dataSource, setDataSource] = useState<DataSource | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Get navigation function using useNavigate
  const navigate = useNavigate();

  // Get alert functions from useAlert hook
  const { showSuccess, showError } = useAlert();

  /**
   * Fetches the data source details by ID
   */
  const fetchDataSource = async () => {
    setLoading(true);
    try {
      // Call getDataSourceById API function with the ID from URL params
      const response = await getDataSourceById(id || '');
      if (response.success && response.data) {
        // If successful, set the dataSource state with the response data
        setDataSource(response.data);
      } else {
        // If error occurs, show error message and navigate back to data sources list
        showError(response.error?.message || 'Failed to fetch data source.');
        navigate(ROUTES.DATA_SOURCES.path);
      }
    } catch (error: any) {
      // Handle any unexpected errors
      showError(error?.message || 'An unexpected error occurred.');
      navigate(ROUTES.DATA_SOURCES.path);
    } finally {
      // Set loading state to false regardless of outcome
      setLoading(false);
    }
  };

  // Fetch data source details when component mounts
  useEffect(() => {
    fetchDataSource();
  }, [id]);

  /**
   * Handles form submission for updating the data source
   * @param any updatedDataSource
   */
  const handleSubmit = async (updatedDataSource: any) => {
    setSubmitting(true);
    try {
      // Call updateDataSource API function with the ID and updated data
      const response = await updateDataSource(id || '', updatedDataSource);
      if (response.success) {
        // If successful, show success message and navigate back to data sources list
        showSuccess('Data source updated successfully!');
        navigate(ROUTES.DATA_SOURCES.path);
      } else {
        // If error occurs, show error message
        showError(response.error?.message || 'Failed to update data source.');
      }
    } catch (error: any) {
      // Handle any unexpected errors
      showError(error?.message || 'An unexpected error occurred.');
    } finally {
      // Set submitting state to false regardless of outcome
      setSubmitting(false);
    }
  };

  /**
   * Handles cancellation of the edit process
   */
  const handleCancel = () => {
    // Navigate back to the data sources list page
    navigate(ROUTES.DATA_SOURCES.path);
  };

  // Render the page with MainLayout, PageHeader, and DataSourceForm
  return (
    <MainLayout>
      <PageHeader
        title="Edit Data Source"
        actions={[
          <Button key="cancel" variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>,
        ]}
      />
      {loading ? (
        // Show loading spinner when fetching data
        <Spinner size="lg" ariaLabel="Loading data source details..." />
      ) : dataSource ? (
        // Show data source form when loading is false and dataSource exists
        <DataSourceForm
          initialValues={dataSource}
          isEdit={true}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      ) : (
        // Handle case where data source is not found
        <div>Data source not found.</div>
      )}
    </MainLayout>
  );
};

export default EditDataSourcePage;