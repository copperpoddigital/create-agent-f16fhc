import React, { useState, useEffect, useCallback } from 'react'; // ^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // ^6.10.0
import classNames from 'classnames'; // ^2.3.2

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import ReportDetails from '../../components/reports/ReportDetails';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import Spinner from '../../components/common/Spinner';
import useApi from '../../hooks/useApi';
import useAlert from '../../hooks/useAlert';
import { getReport, runReport, deleteReport, downloadReportOutput } from '../../api/report-api';

/**
 * Page component that displays detailed information about a specific report
 */
const ReportDetailsPage: React.FC = () => {
  // Extract reportId from URL parameters using useParams hook
  const { id: reportId } = useParams<{ id: string }>();

  // Initialize navigate function using useNavigate hook
  const navigate = useNavigate();

  // Initialize state for delete confirmation modal visibility
  const [showDeleteModal, setShowDeleteModal] = useState<boolean>(false);

  // Use useApi hook to fetch report data by ID
  const { state: reportState, actions: reportActions } = useApi(getReport);

  // Use useApi hook for report execution functionality
  const { state: runState, actions: runActions } = useApi(runReport);

  // Use useApi hook for report deletion functionality
  const { state: deleteState, actions: deleteActions } = useApi(deleteReport);

  // Use useAlert hook for displaying notifications
  const { showError, showSuccess } = useAlert();

  // Implement useEffect to fetch report data when component mounts or reportId changes
  useEffect(() => {
    if (reportId) {
      reportActions.execute(reportId);
    }
  }, [reportId, reportActions]);

  // Implement handleBack function to navigate back to reports list page
  const handleBack = useCallback(() => {
    navigate('/reports');
  }, [navigate]);

  // Implement handleRun function to execute the report
  const handleRun = useCallback(async () => {
    if (reportId) {
      try {
        await runActions.execute(reportId);
        showSuccess('Report run started successfully!');
      } catch (error: any) {
        showError(error.message || 'Failed to run report');
      }
    }
  }, [reportId, runActions, showSuccess, showError]);

  // Implement handleExport function to download the report output
  const handleExport = useCallback(async () => {
    if (reportId) {
      try {
        const response = await downloadReportOutput(reportId);
        const blob = new Blob([response.data], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report-${reportId}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        showSuccess('Report downloaded successfully!');
      } catch (error: any) {
        showError(error.message || 'Failed to download report');
      }
    }
  }, [reportId, showSuccess, showError]);

  // Implement handleEdit function to navigate to report edit page
  const handleEdit = useCallback(() => {
    if (reportId) {
      navigate(`/reports/edit/${reportId}`);
    }
  }, [reportId, navigate]);

  // Implement handleDelete function to show delete confirmation modal
  const handleDelete = useCallback(() => {
    setShowDeleteModal(true);
  }, []);

  // Implement confirmDelete function to delete the report and navigate back to reports list
  const confirmDelete = useCallback(async () => {
    if (reportId) {
      try {
        await deleteActions.execute(reportId);
        showSuccess('Report deleted successfully!');
        navigate('/reports');
      } catch (error: any) {
        showError(error.message || 'Failed to delete report');
      } finally {
        setShowDeleteModal(false);
      }
    }
  }, [reportId, deleteActions, navigate, showSuccess, showError]);

  // Implement cancelDelete function to hide delete confirmation modal
  const cancelDelete = useCallback(() => {
    setShowDeleteModal(false);
  }, []);

  // Create action buttons for the page header
  const actions = [
    <Button key="back" variant="secondary" onClick={handleBack}>
      Back
    </Button>,
    <Button key="run" isLoading={runState.isLoading} onClick={handleRun}>
      Run Report
    </Button>,
    <Button key="export" onClick={handleExport}>
      Export
    </Button>,
    <Button key="edit" onClick={handleEdit}>
      Edit
    </Button>,
    <Button key="delete" variant="danger" onClick={handleDelete}>
      Delete
    </Button>,
  ];

  // Render loading spinner when data is being fetched
  if (reportState.isLoading) {
    return (
      <MainLayout>
        <Spinner />
      </MainLayout>
    );
  }

  // Render error message if data fetching fails
  if (reportState.error) {
    return (
      <MainLayout>
        <p>Error: {reportState.error.message}</p>
      </MainLayout>
    );
  }

  // Render MainLayout with PageHeader and ReportDetails components
  return (
    <MainLayout>
      <PageHeader title="Report Details" actions={actions} />
      <ReportDetails reportId={reportId || ''} />

      {/* Render delete confirmation modal when showDeleteModal is true */}
      <Modal
        isOpen={showDeleteModal}
        onClose={cancelDelete}
        title="Confirm Delete"
        footer={
          <>
            <Button variant="secondary" onClick={cancelDelete}>
              Cancel
            </Button>
            <Button variant="danger" isLoading={deleteState.isLoading} onClick={confirmDelete}>
              Delete
            </Button>
          </>
        }
      >
        <p>Are you sure you want to delete this report?</p>
      </Modal>
    </MainLayout>
  );
};

export default ReportDetailsPage;