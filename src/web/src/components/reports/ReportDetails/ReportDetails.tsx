import React, { useState, useEffect, useCallback } from 'react'; // ^18.2.0
import classNames from 'classnames'; // ^2.3.2
import {
  Card,
  Tabs,
  Table,
  Badge,
  Spinner,
} from '../../common';
import {
  LineChart,
  BarChart,
  TrendIndicator,
  SummaryCard,
} from '../../charts';
import { useApi, useAlert } from '../../../hooks';
import {
  getReport,
  getReportRunHistory,
  Report,
  ReportRunHistory,
  ReportStatus,
  ReportRunStatus,
} from '../../../api/report-api';
import {
  formatDate,
  formatCurrency,
} from '../../../utils';

/**
 * Props interface for the ReportDetails component
 */
interface ReportDetailsProps {
  reportId: string;
  className?: string;
  onBack?: () => void;
  onRun?: () => void;
  onExport?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

/**
 * Enum for tab types in the report details view
 */
enum TabType {
  SUMMARY = 'SUMMARY',
  RESULTS = 'RESULTS',
  VISUALIZATION = 'VISUALIZATION',
  RUN_HISTORY = 'RUN_HISTORY',
  SCHEDULE = 'SCHEDULE',
}

/**
 * A component that displays detailed information about a specific report
 */
const ReportDetails: React.FC<ReportDetailsProps> = ({
  reportId,
  className,
  onBack,
  onRun,
  onExport,
  onEdit,
  onDelete,
}) => {
  // Initialize state for active tab, report data, run history, and loading states
  const [activeTab, setActiveTab] = useState<TabType>(TabType.SUMMARY);
  const [report, setReport] = useState<Report | null>(null);
  const [runHistory, setRunHistory] = useState<ReportRunHistory[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);

  // Use useApi hook to fetch report data by ID
  const {
    state: reportState,
    actions: reportActions,
  } = useApi(getReport);

  // Use useApi hook to fetch report run history
  const {
    state: historyState,
    actions: historyActions,
  } = useApi(getReportRunHistory);

  // Use useAlert hook for displaying notifications
  const { showError } = useAlert();

  // Implement useEffect to fetch report data when component mounts or reportId changes
  useEffect(() => {
    const fetchReportData = async () => {
      setIsLoading(true);
      try {
        const reportData = await reportActions.execute(reportId);
        setReport(reportData.data);
      } catch (error: any) {
        showError(error.message || 'Failed to load report details');
      } finally {
        setIsLoading(false);
      }
    };

    fetchReportData();
  }, [reportId, reportActions, showError]);

  // Implement useEffect to fetch run history when report data is available
  useEffect(() => {
    const fetchRunHistory = async () => {
      if (report) {
        setIsHistoryLoading(true);
        try {
          const historyData = await historyActions.execute(report.id, { page: 1, pageSize: 5 });
          setRunHistory(historyData.data);
        } catch (error: any) {
          showError(error.message || 'Failed to load report run history');
        } finally {
          setIsHistoryLoading(false);
        }
      }
    };

    fetchRunHistory();
  }, [report, historyActions, showError]);

  // Implement handleTabChange function to switch between tabs
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
  };

  // Implement renderSummaryTab function to display report metadata and summary
  const renderSummaryTab = () => (
    <Card title="Report Summary">
      {report ? (
        <>
          <p>Name: {report.name}</p>
          <p>Description: {report.description}</p>
          <p>Status: {renderStatusBadge(report.status)}</p>
          {report.analysis_id && <p>Analysis ID: {report.analysis_id}</p>}
        </>
      ) : (
        <p>No report data available.</p>
      )}
    </Card>
  );

  // Implement renderResultsTab function to display analysis results
  const renderResultsTab = () => (
    <Card title="Analysis Results">
      {report?.analysis_result ? (
        <>
          <p>Start Value: {formatCurrency(report.analysis_result.start_value)}</p>
          <p>End Value: {formatCurrency(report.analysis_result.end_value)}</p>
          {/* Add more result details here */}
        </>
      ) : (
        <p>No analysis results available.</p>
      )}
    </Card>
  );

  // Implement renderVisualizationTab function to display charts and visualizations
  const renderVisualizationTab = () => (
    <Card title="Visualization">
      {report?.analysis_result ? (
        <>
          {/* Render charts based on report configuration */}
          <LineChart data={report.analysis_result.time_series} />
          <BarChart data={report.analysis_result.time_series} />
        </>
      ) : (
        <p>No visualization available.</p>
      )}
    </Card>
  );

  // Implement renderRunHistoryTab function to display execution history
  const renderRunHistoryTab = () => {
    const columns = [
      { key: 'id', header: 'Run ID' },
      { key: 'status', header: 'Status', render: (item: ReportRunHistory) => renderRunStatusBadge(item.status) },
      { key: 'started_at', header: 'Started At', render: (item: ReportRunHistory) => formatDate(item.started_at) },
      { key: 'completed_at', header: 'Completed At', render: (item: ReportRunHistory) => formatDate(item.completed_at) },
    ];

    return (
      <Card title="Run History">
        {isHistoryLoading ? (
          <Spinner />
        ) : (
          <Table data={runHistory} columns={columns} />
        )}
      </Card>
    );
  };

  // Implement renderScheduleTab function to display scheduled report information if available
  const renderScheduleTab = () => (
    <Card title="Schedule">
      <p>No schedule information available.</p>
    </Card>
  );

  // Implement renderStatusBadge function to display report status with appropriate styling
  const renderStatusBadge = (status: ReportStatus) => {
    switch (status) {
      case ReportStatus.ACTIVE:
        return <Badge variant="success">Active</Badge>;
      case ReportStatus.ARCHIVED:
        return <Badge variant="secondary">Archived</Badge>;
      case ReportStatus.DRAFT:
        return <Badge variant="warning">Draft</Badge>;
      default:
        return <Badge variant="info">Unknown</Badge>;
    }
  };

  // Implement renderRunStatusBadge function to display run status with appropriate styling
  const renderRunStatusBadge = (status: ReportRunStatus) => {
    switch (status) {
      case ReportRunStatus.COMPLETED:
        return <Badge variant="success">Completed</Badge>;
      case ReportRunStatus.FAILED:
        return <Badge variant="danger">Failed</Badge>;
      case ReportRunStatus.PENDING:
        return <Badge variant="warning">Pending</Badge>;
      case ReportRunStatus.RUNNING:
        return <Badge variant="info">Running</Badge>;
      default:
        return <Badge variant="info">Unknown</Badge>;
    }
  };

  // Define tabs configuration
  const tabs = [
    { id: TabType.SUMMARY, label: 'Summary', content: renderSummaryTab() },
    { id: TabType.RESULTS, label: 'Results', content: renderResultsTab() },
    { id: TabType.VISUALIZATION, label: 'Visualization', content: renderVisualizationTab() },
    { id: TabType.RUN_HISTORY, label: 'Run History', content: renderRunHistoryTab() },
    { id: TabType.SCHEDULE, label: 'Schedule', content: renderScheduleTab() },
  ];

  return (
    <div className={classNames('report-details', className)}>
      {isLoading ? (
        <Spinner />
      ) : reportState.error ? (
        <p>Error: {reportState.error.message}</p>
      ) : (
        <>
          <Tabs
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={handleTabChange}
          />
        </>
      )}
    </div>
  );
};

export default ReportDetails;