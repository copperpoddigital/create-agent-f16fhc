import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import DataSourceList from '../../components/data-sources/DataSourceList';
import Button from '../../components/common/Button';
import Icon from '../../components/common/Icon';
import useAlert from '../../hooks/useAlert';

/**
 * Component that renders the data sources management page for the Freight Price Movement Agent.
 * Provides a user interface for viewing, adding, editing, and managing various types of
 * data sources used for freight price data collection.
 * 
 * This component implements the wireframe specified in the technical requirements
 * (7.3.3 Data Source Management) and supports the Data Collection & Ingestion feature.
 */
const DataSourcesPage: React.FC = () => {
  // State for triggering refresh of data sources list
  const [refreshTrigger, setRefreshTrigger] = useState(false);
  
  // Navigation functions
  const navigate = useNavigate();
  
  // Access alert functionality
  const { showSuccess, showError } = useAlert();
  
  /**
   * Handles navigation to add a new data source
   */
  const handleAddDataSource = () => {
    navigate('/data-sources/add');
  };
  
  /**
   * Handles navigation to edit an existing data source
   * @param id - The ID of the data source to edit
   */
  const handleEditDataSource = (id: string) => {
    navigate(`/data-sources/edit/${id}`);
  };
  
  /**
   * Triggers a refresh of the data sources list
   */
  const handleRefresh = () => {
    setRefreshTrigger(prev => !prev);
  };
  
  return (
    <MainLayout>
      <PageHeader 
        title="Data Sources"
        actions={[
          <Button 
            key="add-source"
            variant="primary"
            leftIcon={<Icon name="plus" size="sm" />}
            onClick={handleAddDataSource}
            ariaLabel="Add new data source"
          >
            Add Source
          </Button>
        ]}
      />
      
      <DataSourceList
        onAddDataSource={handleAddDataSource}
        onEditDataSource={handleEditDataSource}
        refreshTrigger={refreshTrigger}
      />
    </MainLayout>
  );
};

export default DataSourcesPage;