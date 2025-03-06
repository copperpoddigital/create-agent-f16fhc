import React, { useState, useEffect, useCallback } from 'react';
import Table from '../../common/Table';
import Button from '../../common/Button';
import Input from '../../common/Input';
import Modal from '../../common/Modal';
import Icon from '../../common/Icon';
import Badge from '../../common/Badge';
import { DataSource, DataSourceType, DataSourceStatus } from '../../../types/data-source.types';
import { getDataSources, deleteDataSource, syncDataSource } from '../../../api/data-source-api';
import useApi from '../../../hooks/useApi';
import useAlert from '../../../hooks/useAlert';
import usePagination from '../../../hooks/usePagination';
import useDebounce from '../../../hooks/useDebounce';

/**
 * Props interface for the DataSourceList component
 */
interface DataSourceListProps {
  /** Additional CSS class name */
  className?: string;
  /** Callback when Add Source button is clicked */
  onAddDataSource: () => void;
  /** Callback when Edit action is triggered for a data source */
  onEditDataSource: (id: string) => void;
  /** Boolean to trigger a refresh of the data sources list */
  refreshTrigger?: boolean;
}

/**
 * Component that displays a list of data sources with filtering, pagination, and management actions
 */
const DataSourceList: React.FC<DataSourceListProps> = ({
  className,
  onAddDataSource,
  onEditDataSource,
  refreshTrigger = false,
}) => {
  // State for search term and its debounced version
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  
  // State for delete confirmation
  const [dataSourceToDelete, setDataSourceToDelete] = useState<DataSource | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Setup pagination
  const pagination = usePagination({
    totalItems: 0,
    itemsPerPage: 10,
    initialPage: 1,
    maxVisiblePages: 5,
    storageKey: 'data_sources_pagination'
  });

  // API hooks
  const { 
    state: { data, isLoading, error },
    actions: { execute: fetchDataSourcesExec }
  } = useApi(getDataSources);

  const {
    state: { isLoading: isDeleting },
    actions: { execute: deleteDataSourceExec }
  } = useApi(deleteDataSource);

  const {
    state: { isLoading: isSyncing },
    actions: { execute: syncDataSourceExec }
  } = useApi(syncDataSource);

  // Alerts for user feedback
  const { showSuccess, showError } = useAlert();

  /**
   * Fetches data sources from the API with pagination and filtering
   */
  const fetchDataSources = useCallback(async () => {
    try {
      // Prepare pagination parameters
      const paginationParams = {
        page: pagination.currentPage,
        pageSize: pagination.itemsPerPage,
        sortBy: 'name',
        sortDirection: 'asc'
      };

      // Prepare filter parameters if search term exists
      const filters = debouncedSearchTerm ? [
        {
          field: 'name',
          operator: 'contains',
          value: debouncedSearchTerm
        }
      ] : undefined;

      // Call the API function
      await fetchDataSourcesExec(paginationParams, filters);
    } catch (err) {
      console.error('Failed to fetch data sources:', err);
    }
  }, [fetchDataSourcesExec, pagination.currentPage, pagination.itemsPerPage, debouncedSearchTerm]);

  // Fetch data sources when dependencies change
  useEffect(() => {
    fetchDataSources();
  }, [fetchDataSources, refreshTrigger]);

  // Update pagination total items when data changes
  useEffect(() => {
    if (data?.meta?.pagination?.totalItems !== undefined) {
      // Need to manually update total items as the pagination hook 
      // doesn't automatically synchronize with API responses
      pagination.goToPage(pagination.currentPage);
    }
  }, [data, pagination]);

  /**
   * Handles search input changes
   */
  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    // Reset to first page when search changes
    pagination.goToPage(1);
  };

  /**
   * Handles click on the delete button for a data source
   */
  const handleDeleteClick = (dataSource: DataSource) => {
    setDataSourceToDelete(dataSource);
    setShowDeleteModal(true);
  };

  /**
   * Handles confirmation of data source deletion
   */
  const handleDeleteConfirm = async () => {
    if (!dataSourceToDelete) return;

    try {
      await deleteDataSourceExec(dataSourceToDelete.id);
      setShowDeleteModal(false);
      showSuccess(`Data source "${dataSourceToDelete.name}" was successfully deleted.`);
      fetchDataSources(); // Refresh the list
    } catch (err) {
      showError(`Failed to delete data source: ${err.message || 'Unknown error'}`);
    }
  };

  /**
   * Handles click on the sync button for a data source
   */
  const handleSyncClick = async (dataSource: DataSource) => {
    try {
      await syncDataSourceExec(dataSource.id);
      showSuccess(`Synchronization initiated for "${dataSource.name}".`);
      // Optionally refresh the list after a short delay to show updated status
      setTimeout(() => fetchDataSources(), 1000);
    } catch (err) {
      showError(`Failed to synchronize data source: ${err.message || 'Unknown error'}`);
    }
  };

  /**
   * Renders the data source type with an appropriate icon
   */
  const renderDataSourceType = (dataSource: DataSource) => {
    let iconName: string;
    
    // Determine appropriate icon based on data source type
    switch (dataSource.source_type) {
      case DataSourceType.CSV:
        iconName = 'export'; // Using export icon for CSV files
        break;
      case DataSourceType.DATABASE:
        iconName = 'settings'; // Using settings icon for database connections
        break;
      case DataSourceType.API:
        iconName = 'chart'; // Using chart icon for API data sources
        break;
      case DataSourceType.TMS:
        iconName = 'refresh'; // Using refresh icon for TMS systems
        break;
      case DataSourceType.ERP:
        iconName = 'settings'; // Using settings icon for ERP systems
        break;
      default:
        iconName = 'info';
    }

    return (
      <div className="data-source-type">
        <Icon name={iconName} size="sm" className="data-source-type__icon" />
        <span className="data-source-type__text">{dataSource.source_type}</span>
      </div>
    );
  };

  /**
   * Renders the data source status as a colored badge
   */
  const renderDataSourceStatus = (dataSource: DataSource) => {
    let variant: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
    
    // Determine appropriate color based on status
    switch (dataSource.status) {
      case DataSourceStatus.ACTIVE:
        variant = 'success';
        break;
      case DataSourceStatus.INACTIVE:
        variant = 'secondary';
        break;
      case DataSourceStatus.WARNING:
        variant = 'warning';
        break;
      case DataSourceStatus.ERROR:
        variant = 'danger';
        break;
      default:
        variant = 'primary';
    }

    return <Badge variant={variant}>{dataSource.status}</Badge>;
  };

  /**
   * Renders action buttons for a data source
   */
  const renderActions = (dataSource: DataSource) => {
    return (
      <div className="data-source-actions">
        <Button
          variant="outline-primary"
          size="sm"
          onClick={() => onEditDataSource(dataSource.id)}
          aria-label={`Edit ${dataSource.name}`}
          className="data-source-actions__btn"
        >
          <Icon name="edit" size="sm" />
        </Button>
        
        <Button
          variant="outline-primary"
          size="sm"
          onClick={() => handleSyncClick(dataSource)}
          aria-label={`Synchronize ${dataSource.name}`}
          className="data-source-actions__btn"
          disabled={isSyncing}
        >
          <Icon name="refresh" size="sm" />
        </Button>
        
        <Button
          variant="outline-danger"
          size="sm"
          onClick={() => handleDeleteClick(dataSource)}
          aria-label={`Delete ${dataSource.name}`}
          className="data-source-actions__btn"
          disabled={isDeleting}
        >
          <Icon name="delete" size="sm" />
        </Button>
      </div>
    );
  };

  // Define table columns
  const columns = [
    {
      key: 'name',
      header: 'Name',
      sortable: true
    },
    {
      key: 'source_type',
      header: 'Type',
      render: renderDataSourceType
    },
    {
      key: 'last_sync',
      header: 'Last Update',
      render: (dataSource: DataSource) => {
        if (!dataSource.last_sync) return 'Never';
        
        // Format the date for display
        const date = new Date(dataSource.last_sync);
        const now = new Date();
        const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        
        return date.toLocaleDateString();
      }
    },
    {
      key: 'status',
      header: 'Status',
      render: renderDataSourceStatus
    },
    {
      key: 'actions',
      header: 'Actions',
      render: renderActions,
      align: 'center'
    }
  ];

  return (
    <div className={`data-source-list ${className || ''}`}>
      <div className="data-source-list__header">
        <h2 className="data-source-list__title">DATA SOURCES</h2>
        <Button 
          variant="primary"
          onClick={onAddDataSource}
          leftIcon={<Icon name="plus" size="sm" />}
        >
          Add Source
        </Button>
      </div>

      <div className="data-source-list__filters">
        <div className="data-source-list__filter-input">
          <Input
            type="search"
            placeholder="Filter by name..."
            value={searchTerm}
            onChange={handleSearch}
            leftIcon={<Icon name="search" size="sm" />}
            clearable
            ariaLabel="Filter data sources"
          />
        </div>
      </div>

      <Table
        data={data?.data || []}
        columns={columns}
        isLoading={isLoading}
        isStriped
        isBordered
        isHoverable
        isPaginated
        itemsPerPage={pagination.itemsPerPage}
        emptyMessage="No data sources found. Click 'Add Source' to create one."
        storageKey="data_sources_table"
        isSortable
      />

      {/* Delete confirmation modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Confirm Deletion"
        size="sm"
        footer={
          <>
            <Button
              variant="danger"
              onClick={handleDeleteConfirm}
              isLoading={isDeleting}
            >
              Delete
            </Button>
            <Button
              variant="outline-secondary"
              onClick={() => setShowDeleteModal(false)}
            >
              Cancel
            </Button>
          </>
        }
      >
        <p>
          Are you sure you want to delete the data source "{dataSourceToDelete?.name}"?
          This action cannot be undone and will permanently remove the data source.
        </p>
      </Modal>
    </div>
  );
};

export default DataSourceList;