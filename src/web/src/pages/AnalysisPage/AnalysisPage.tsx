# src/web/src/pages/AnalysisPage/AnalysisPage.tsx
```typescript
import React, { useState, useEffect, useCallback } from 'react'; // version ^18.2.0
import { useNavigate } from 'react-router-dom'; // version ^6.10.0

import { MainLayout, PageHeader } from '../../components/layout';
import { Button, Card, Table, TableColumn, Pagination, Spinner, Modal, Alert, Icon } from '../../components/common';
import { TrendIndicator } from '../../components/charts';
import { useApi, useAlert } from '../../hooks';
import { getAnalysisRequests, deleteAnalysisRequest, runAnalysis } from '../../api/analysis-api';
import { AnalysisRequest, AnalysisStatus, ROUTES, formatDate } from '../../types';
import { PaginationParams } from '../../types/api.types';

/**
 * Main component for the Analysis page that displays a list of saved analyses and provides actions to manage them
 */
const AnalysisPage: React.FC = () => {
  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // State for selected analysis and confirmation modals
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<string | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isRunModalOpen, setIsRunModalOpen] = useState(false);

  // Navigation hook
  const navigate = useNavigate();

  // API hooks for fetching, deleting, and running analyses
  const { state: analysisState, actions: analysisActions } = useApi(getAnalysisRequests);
  const { actions: deleteActions } = useApi(deleteAnalysisRequest);
  const { actions: runActions } = useApi(runAnalysis);

  // Alert hook for displaying notifications
  const { showError, showSuccess } = useAlert();

  /**
   * Fetches analysis requests based on current pagination settings
   */
  const fetchAnalysisRequests = useCallback(async () => {
    try {
      await analysisActions.execute({ page: currentPage, pageSize });
    } catch (error: any) {
      showError(error.message || 'Failed to fetch analysis requests');
    }
  }, [currentPage, pageSize, analysisActions, showError]);

  // Fetch analysis requests on component mount and when pagination changes
  useEffect(() => {
    fetchAnalysisRequests();
  }, [fetchAnalysisRequests]);

  /**
   * Table columns configuration for the analysis list
   */
  const columns: TableColumn<AnalysisRequest>[] = [
    {
      key: 'name',
      header: 'Name',
      sortable: true,
      render: (item) => item.name,
    },
    {
      key: 'time_period.name',
      header: 'Time Period',
      sortable: true,
      render: (item) => item.time_period.name,
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (item) => getStatusBadge(item.status),
    },
    {
      key: 'last_run_at',
      header: 'Last Run',
      sortable: true,
      render: (item) => item.last_run_at ? formatTimeAgo(item.last_run_at) : 'Never',
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (item) => (
        <div className="table-actions">
          <Button variant="link" onClick={() => handleViewAnalysis(item.id)} aria-label={`View analysis ${item.name}`}>
            <Icon name="chart" size="sm" />
          </Button>
          <Button variant="link" onClick={() => handleEditAnalysis(item.id)} aria-label={`Edit analysis ${item.name}`}>
            <Icon name="edit" size="sm" />
          </Button>
          <Button variant="link" onClick={() => handleRunAnalysisConfirmation(item.id)} aria-label={`Run analysis ${item.name}`}>
            <Icon name="play" size="sm" />
          </Button>
          <Button variant="link" onClick={() => handleDeleteAnalysisConfirmation(item.id)} aria-label={`Delete analysis ${item.name}`}>
            <Icon name="close" size="sm" />
          </Button>
        </div>
      ),
    },
  ];

  /**
   * Handlers for creating, viewing, editing, running, and deleting analyses
   */
  const handleCreateAnalysis = () => {
    navigate(ROUTES.NEW_ANALYSIS.path);
  };

  const handleViewAnalysis = (id: string) => {
    navigate(ROUTES.ANALYSIS_RESULTS.path.replace(':id', id));
  };

  const handleEditAnalysis = (id: string) => {
    navigate(ROUTES.NEW_ANALYSIS.path, { state: { analysisId: id } });
  };

  const handleRunAnalysisConfirmation = (id: string) => {
    setSelectedAnalysisId(id);
    setIsRunModalOpen(true);
  };

  const handleRunAnalysis = async () => {
    if (!selectedAnalysisId) return;
    setIsRunModalOpen(false);

    try {
      await runActions.execute(selectedAnalysisId);
      showSuccess('Analysis run successfully');
      fetchAnalysisRequests();
    } catch (error: any) {
      showError(error.message || 'Failed to run analysis');
    } finally {
      setSelectedAnalysisId(null);
    }
  };

  const handleDeleteAnalysisConfirmation = (id: string) => {
    setSelectedAnalysisId(id);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteAnalysis = async () => {
    if (!selectedAnalysisId) return;
    setIsDeleteModalOpen(false);

    try {
      await deleteActions.execute(selectedAnalysisId);
      showSuccess('Analysis deleted successfully');
      fetchAnalysisRequests();
    } catch (error: any) {
      showError(error.message || 'Failed to delete analysis');
    } finally {
      setSelectedAnalysisId(null);
    }
  };

  return (
    <MainLayout>
      <PageHeader
        title="Analysis"
        actions={[
          <Button key="create" leftIcon={<Icon name="plus" />} onClick={handleCreateAnalysis}>
            Create Analysis
          </Button>,
        ]}
      />

      <Card>
        {analysisState.isLoading ? (
          <div className="loading-container">
            <Spinner size="lg" />
          </div>
        ) : analysisState.isError ? (
          <Alert type="error" message={analysisState.error.message} />
        ) : (
          <>
            <Table
              data={analysisState.data || []}
              columns={columns}
              isStriped
              isBordered
              isHoverable
              isSortable
              isPaginated
              itemsPerPage={pageSize}
              storageKey="analysisTable"
              emptyMessage="No saved analyses found."
            />
            {analysisState.data && analysisState.data.length > 0 && (
              <Pagination
                totalItems={analysisState.data.length}
                itemsPerPage={pageSize}
                initialPage={currentPage}
                onPageChange={setCurrentPage}
              />
            )}
          </>
        )}
      </Card>

      {/* Confirmation Modals */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Analysis"
      >
        <p>Are you sure you want to delete this analysis?</p>
        <div className="modal-actions">
          <Button variant="danger" onClick={handleDeleteAnalysis}>
            Delete
          </Button>
          <Button variant="secondary" onClick={() => setIsDeleteModalOpen(false)}>
            Cancel
          </Button>
        </div>
      </Modal>

      <Modal
        isOpen={isRunModalOpen}
        onClose={() => setIsRunModalOpen(false)}
        title="Run Analysis"
      >
        <p>Are you sure you want to run this analysis?</p>
        <div className="modal-actions">
          <Button onClick={handleRunAnalysis}>Run</Button>
          <Button variant="secondary" onClick={() => setIsRunModalOpen(false)}>
            Cancel
          </Button>
        </div>
      </Modal>
    </MainLayout>
  );
};

/**
 * Helper function to render a status badge with appropriate color based on analysis status
 * @param status The status of the analysis
 * @returns Rendered badge component with appropriate styling
 */
const getStatusBadge = (status: AnalysisStatus) => {
  let badgeColor = 'primary';

  switch (status) {
    case AnalysisStatus.COMPLETED:
      badgeColor = 'success';
      break;
    case AnalysisStatus.RUNNING:
      badgeColor = 'warning';
      break;
    case AnalysisStatus.FAILED:
      badgeColor = 'danger';
      break;
    case AnalysisStatus.CANCELLED:
      badgeColor = 'secondary';
      break;
    case AnalysisStatus.PENDING:
    default:
      badgeColor = 'primary';
      break;
  }

  return <span className={`badge badge--${badgeColor}`}>{status}</span>;
};

/**
 * Helper function to format a date as a relative time (e.g., '2 days ago')
 * @param dateString ISO date string to format
 * @returns Formatted relative time string
 */
const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    return `${days} day${days > 1 ? 's' : ''} ago`;
  } else if (hours > 0) {
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else if (minutes > 0) {
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  } else {
    return 'Just now';
  }
};

export default AnalysisPage;