import React, { useState, useEffect, useCallback } from 'react'; // ^18.2.0
import classNames from 'classnames'; // ^2.3.2

import Table from '../../common/Table';
import Button from '../../common/Button';
import Modal from '../../common/Modal';
import Input from '../../common/Input';
import Icon from '../../common/Icon';

import useApi from '../../../hooks/useApi';
import useAlert from '../../../hooks/useAlert';
import { getReports, deleteReport, runReport } from '../../../api/report-api';
import { Report, ReportStatus } from '../../../types/report.types';
import { formatDate } from '../../../utils/date-utils';

/**
 * Props interface for the ReportList component
 */
export interface ReportListProps {
  /** Additional CSS class names to apply to the component */
  className?: string;
  /** Callback function when the Create Report button is clicked */
  onCreateReport?: () => void;
  /** Callback function when the Edit button for a report is clicked */
  onEditReport?: (id: string) => void;
  /** Callback function when the View button for a report is clicked */
  onViewReport?: (id: string) => void;
}

/**
 * Component that displays a list of reports with filtering, pagination, and action buttons
 * for running, editing, and deleting reports.
 */
const ReportList: React.FC<ReportListProps> = ({
  className,
  onCreateReport,
  onEditReport,
  onViewReport,
}) => {
  // State for filtering and pagination
  const [filter, setFilter] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortColumn, setSortColumn] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');
  
  // State for delete confirmation modal
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<string | null>(null);
  
  // API hooks
  const getReportsApi = useApi(getReports);
  const deleteReportApi = useApi(deleteReport);
  const runReportApi = useApi(runReport);
  
  // Alert hook for notifications
  const alert = useAlert();
  
  // Fetch reports with pagination, filtering and sorting
  const fetchReports = useCallback(async () => {
    try {
      await getReportsApi.actions.execute({
        page,
        pageSize,
        sortBy: sortColumn,
        sortDirection,
        filter: filter || undefined
      });
    } catch (error) {
      // Error is handled by useApi hook via the alert context
    }
  }, [getReportsApi.actions, page, pageSize, sortColumn, sortDirection, filter]);
  
  // Initial data fetch and refetch when parameters change
  useEffect(() => {
    fetchReports();
  }, [fetchReports]);
  
  // Handle filter change
  const handleFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilter(event.target.value);
  };
  
  // Handle clear filter
  const handleClearFilter = () => {
    setFilter('');
    setPage(1);
    fetchReports();
  };
  
  // Handle page change
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };
  
  // Handle sort change
  const handleSort = (column: string, direction: string) => {
    setSortColumn(column);
    setSortDirection(direction);
  };
  
  // Handle run report
  const handleRunReport = async (id: string) => {
    try {
      const response = await runReportApi.actions.execute(id);
      
      // response.data is the Blob
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `report-${id}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url); // Clean up
      
      alert.showSuccess('Report generated successfully');
    } catch (error) {
      // Error is handled by useApi hook via the alert context
    }
  };
  
  // Handle delete button click
  const handleDeleteClick = (id: string) => {
    setReportToDelete(id);
    setDeleteModalOpen(true);
  };
  
  // Handle confirm delete
  const handleConfirmDelete = async () => {
    if (!reportToDelete) return;
    
    try {
      await deleteReportApi.actions.execute(reportToDelete);
      setDeleteModalOpen(false);
      setReportToDelete(null);
      alert.showSuccess('Report deleted successfully');
      fetchReports(); // Refresh the list
    } catch (error) {
      // Error is handled by useApi hook via the alert context
    }
  };
  
  // Handle cancel delete
  const handleCancelDelete = () => {
    setDeleteModalOpen(false);
    setReportToDelete(null);
  };
  
  // Table columns configuration
  const columns = [
    {
      key: 'name',
      header: 'Name',
      sortable: true,
      width: '40%',
    },
    {
      key: 'created_at',
      header: 'Created',
      sortable: true,
      width: '20%',
      render: (report: Report) => formatDate(report.created_at),
    },
    {
      key: 'last_run_at',
      header: 'Last Run',
      sortable: true,
      width: '20%',
      render: (report: Report) => report.last_run_at ? formatDate(report.last_run_at) : 'Never',
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      width: '20%',
      align: 'right',
      render: (report: Report) => (
        <div className="report-actions">
          <Button
            variant="outline-primary"
            size="sm"
            title="Run Report"
            onClick={(e) => {
              e.stopPropagation();
              handleRunReport(report.id);
            }}
            ariaLabel={`Run report ${report.name}`}
          >
            <Icon name="play" size="sm" />
          </Button>
          {onEditReport && (
            <Button
              variant="outline-primary"
              size="sm"
              title="Edit Report"
              onClick={(e) => {
                e.stopPropagation();
                onEditReport(report.id);
              }}
              ariaLabel={`Edit report ${report.name}`}
            >
              <Icon name="edit" size="sm" />
            </Button>
          )}
          <Button
            variant="outline-danger"
            size="sm"
            title="Delete Report"
            onClick={(e) => {
              e.stopPropagation();
              handleDeleteClick(report.id);
            }}
            ariaLabel={`Delete report ${report.name}`}
          >
            <Icon name="delete" size="sm" />
          </Button>
        </div>
      ),
    },
  ];
  
  const isLoading = getReportsApi.state.isLoading || deleteReportApi.state.isLoading || runReportApi.state.isLoading;
  const reports = getReportsApi.state.data?.data || [];
  
  return (
    <div className={classNames('report-list', className)}>
      <div className="report-list__header">
        <h2 className="report-list__title">Saved Reports</h2>
        {onCreateReport && (
          <Button
            variant="primary"
            onClick={onCreateReport}
            leftIcon={<Icon name="plus" size="sm" />}
          >
            Create Report
          </Button>
        )}
      </div>
      
      <div className="report-list__filter">
        <Input
          type="search"
          placeholder="Filter reports..."
          value={filter}
          onChange={handleFilterChange}
          leftIcon={<Icon name="search" size="sm" />}
          clearable
        />
        <Button 
          variant="outline-primary" 
          size="sm"
          onClick={fetchReports}
        >
          Apply
        </Button>
        <Button 
          variant="outline-secondary" 
          size="sm"
          onClick={handleClearFilter}
        >
          Clear
        </Button>
      </div>
      
      <Table
        data={reports}
        columns={columns}
        isLoading={isLoading}
        isStriped
        isHoverable
        isSortable
        isPaginated
        itemsPerPage={pageSize}
        emptyMessage="No reports found"
        onSort={handleSort}
        sortColumn={sortColumn}
        sortDirection={sortDirection}
        storageKey="fpma_reports_table"
        onRowClick={onViewReport ? (item) => onViewReport(item.id) : undefined}
      />
      
      <Modal
        isOpen={deleteModalOpen}
        onClose={handleCancelDelete}
        title="Confirm Delete"
        size="sm"
        closeOnEscape
        closeOnOverlayClick
        footer={
          <>
            <Button
              variant="danger"
              onClick={handleConfirmDelete}
              isLoading={deleteReportApi.state.isLoading}
            >
              Delete
            </Button>
            <Button variant="outline-secondary" onClick={handleCancelDelete}>
              Cancel
            </Button>
          </>
        }
      >
        <p>Are you sure you want to delete this report? This action cannot be undone.</p>
      </Modal>
    </div>
  );
};

export default ReportList;