import React, { useState, useEffect } from 'react'; // ^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // ^6.8.0
import classNames from 'classnames'; // ^2.3.2

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import Button from '../../components/common/Button';
import Icon from '../../components/common/Icon';
import Alert from '../../components/common/Alert';
import AnalysisResultsSummary from '../../components/analysis/AnalysisResultsSummary';
import AnalysisResultsChart from '../../components/analysis/AnalysisResultsChart';
import AnalysisResultsTable from '../../components/analysis/AnalysisResultsTable';
import useApi from '../../hooks/useApi';
import useAlert from '../../hooks/useAlert';
import {
  getAnalysisResult,
  getAnalysisRequest,
  exportAnalysisResult,
} from '../../api/analysis-api';
import {
  AnalysisResult,
  AnalysisRequest,
  OutputFormat,
  AnalysisExportOptions,
} from '../../types';
import { ROUTES } from '../../config/routes';

/**
 * Props interface for export button component
 */
interface ExportButtonProps {
  resultId: string;
  format: OutputFormat;
  label: string;
  onExport: () => void;
}

/**
 * A button component for exporting analysis results in a specific format
 */
const ExportButton: React.FC<ExportButtonProps> = ({ resultId, format, label, onExport }) => {
  // Set up API hook for exporting analysis result
  const { actions: exportActions, state: exportState } = useApi(exportAnalysisResult);

  /**
   * Implement handleClick function to trigger export
   */
  const handleClick = async () => {
    try {
      // Define export options
      const exportOptions: AnalysisExportOptions = {
        format: format,
        include_time_series: true,
        include_detailed_results: true,
        filename: `analysis_result_${resultId}.${format}`,
      };

      // Execute the export action
      await exportActions.execute(resultId, exportOptions);

      // Call the onExport callback after successful export
      onExport();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Render Button component with appropriate label and onClick handler
  return (
    <Button
      variant="secondary"
      onClick={handleClick}
      disabled={exportState.isLoading}
    >
      {label}
    </Button>
  );
};

/**
 * Main component for displaying analysis results
 */
const AnalysisResultsPage: React.FC = () => {
  // Extract resultId from URL parameters using useParams hook
  const { id: resultId } = useParams<{ id: string }>();

  // Initialize navigate function using useNavigate hook
  const navigate = useNavigate();

  // Initialize showAlert function using useAlert hook
  const { showError } = useAlert();

  // Set up state for analysis request data
  const [analysisRequest, setAnalysisRequest] = useState<AnalysisRequest | null>(null);

  // Set up API hooks for fetching analysis result and analysis request
  const { state: resultState, actions: resultActions } = useApi(getAnalysisResult);
  const { actions: requestActions } = useApi(getAnalysisRequest);

  /**
   * Implement useEffect to fetch analysis result when component mounts or resultId changes
   */
  useEffect(() => {
    if (resultId) {
      resultActions.execute(resultId)
        .catch(error => {
          console.error('Failed to fetch analysis result:', error);
          showError('Failed to load analysis results.');
        });
    }
  }, [resultId, resultActions, showError]);

  /**
   * Implement useEffect to fetch analysis request details when result data is available
   */
  useEffect(() => {
    if (resultState.data) {
      requestActions.execute(resultState.data.analysis_id)
        .then(requestData => {
          setAnalysisRequest(requestData);
        })
        .catch(error => {
          console.error('Failed to fetch analysis request:', error);
          showError('Failed to load analysis request details.');
        });
    }
  }, [resultState.data, requestActions, showError]);

  /**
   * Implement handleExport function to export analysis results in different formats
   */
  const handleExport = () => {
    console.log('Exporting analysis results...');
  };

  /**
   * Implement handleBackToAnalysis function to navigate back to the analysis page
   */
  const handleBackToAnalysis = () => {
    navigate(ROUTES.ANALYSIS.path);
  };

  /**
   * Implement handleNewAnalysis function to navigate to the new analysis page
   */
  const handleNewAnalysis = () => {
    navigate(ROUTES.NEW_ANALYSIS.path);
  };

  // Define action buttons for the page header
  const headerActions = [
    <ExportButton
      key="export-json"
      resultId={resultId || ''}
      format={OutputFormat.JSON}
      label="Export JSON"
      onExport={handleExport}
    />,
    <ExportButton
      key="export-csv"
      resultId={resultId || ''}
      format={OutputFormat.CSV}
      label="Export CSV"
      onExport={handleExport}
    />,
    <ExportButton
      key="export-text"
      resultId={resultId || ''}
      format={OutputFormat.TEXT}
      label="Export Text"
      onExport={handleExport}
    />,
  ];

  // Render MainLayout component as the page container
  return (
    <MainLayout>
      {/* Render PageHeader with title and action buttons */}
      <PageHeader title="Analysis Results" actions={headerActions} />

      {/* Render error alert if API request failed */}
      {resultState.error && (
        <Alert type="error" message={resultState.error.message} />
      )}

      {/* Render AnalysisResultsSummary component with result data */}
      <AnalysisResultsSummary result={resultState.data} isLoading={resultState.isLoading} />

      {/* Render AnalysisResultsChart component with result data */}
      <AnalysisResultsChart
        result={resultState.data}
        loading={resultState.isLoading}
        error={resultState.isError}
        errorMessage={resultState.error?.message}
      />

      {/* Render AnalysisResultsTable component with result data */}
      <AnalysisResultsTable result={resultState.data} isLoading={resultState.isLoading} />

      {/* Render navigation buttons at the bottom of the page */}
      <div className="analysis-results-page__navigation">
        <Button variant="secondary" onClick={handleBackToAnalysis}>
          <Icon name="arrow-left" />
          Back to Analysis
        </Button>
        <Button variant="primary" onClick={handleNewAnalysis}>
          New Analysis
          <Icon name="plus" />
        </Button>
      </div>
    </MainLayout>
  );
};

export default AnalysisResultsPage;