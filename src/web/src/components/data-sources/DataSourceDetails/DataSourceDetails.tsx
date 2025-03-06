import React, { useState, useEffect, useCallback } from 'react'; // ^18.2.0
import classNames from 'classnames'; // ^2.3.2
import Card from '../../common/Card';
import Badge from '../../common/Badge';
import Button from '../../common/Button';
import Icon from '../../common/Icon';
import { 
  DataSource, 
  DataSourceType, 
  DataSourceStatus,
  CSVDataSource,
  DatabaseDataSource,
  APIDataSource,
  TMSDataSource,
  ERPDataSource,
  DataSourceLog
} from '../../../types/data-source.types';
import { formatDate } from '../../../utils/date-utils';
import { 
  getDataSourceById,
  syncDataSource,
  getDataSourceLogs
} from '../../../api/data-source-api';
import useApi from '../../../hooks/useApi';
import useAlert from '../../../hooks/useAlert';

/**
 * Props interface for the DataSourceDetails component
 */
interface DataSourceDetailsProps {
  dataSourceId: string;
  className?: string;
  onEdit?: () => void;
  onDelete?: () => void;
  onBack?: () => void;
}

/**
 * Component that displays detailed information about a data source in the Freight Price Movement Agent
 * Shows connection details, field mappings, and status information for different types of data sources
 */
const DataSourceDetails: React.FC<DataSourceDetailsProps> = ({
  dataSourceId,
  className,
  onEdit,
  onDelete,
  onBack
}) => {
  // State for component data
  const [dataSource, setDataSource] = useState<DataSource | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<DataSourceLog[]>([]);
  const [logsLoading, setLogsLoading] = useState<boolean>(false);
  const [syncInProgress, setSyncInProgress] = useState<boolean>(false);

  // Get alert functionality from context
  const { showAlert } = useAlert();

  // Create API handlers using the useApi hook
  const dataSourceApi = useApi(getDataSourceById);
  const syncDataSourceApi = useApi(syncDataSource);
  const logsApi = useApi(getDataSourceLogs);

  // Fetch data source details
  const fetchDataSource = useCallback(async () => {
    try {
      setLoading(true);
      const response = await dataSourceApi.actions.execute(dataSourceId);
      setDataSource(response);
      setError(null);
    } catch (err: any) {
      setError(err?.message || 'Failed to load data source details');
    } finally {
      setLoading(false);
    }
  }, [dataSourceId, dataSourceApi.actions]);

  // Fetch data source logs
  const fetchLogs = useCallback(async () => {
    if (!dataSourceId) return;
    
    try {
      setLogsLoading(true);
      const response = await logsApi.actions.execute(
        dataSourceId, 
        { page: 1, pageSize: 10, sortBy: 'started_at', sortDirection: 'desc' }
      );
      setLogs(response);
    } catch (err) {
      showAlert('error', 'Failed to load operation logs');
    } finally {
      setLogsLoading(false);
    }
  }, [dataSourceId, logsApi.actions, showAlert]);

  // Handle triggering data source synchronization
  const handleSync = useCallback(async () => {
    if (!dataSourceId || syncInProgress) return;
    
    try {
      setSyncInProgress(true);
      await syncDataSourceApi.actions.execute(dataSourceId);
      showAlert('success', 'Synchronization started successfully');
      
      // Refresh data source details and logs after a short delay
      setTimeout(() => {
        fetchDataSource();
        fetchLogs();
      }, 2000);
    } catch (err) {
      showAlert('error', 'Failed to start synchronization');
    } finally {
      setSyncInProgress(false);
    }
  }, [dataSourceId, syncInProgress, syncDataSourceApi.actions, fetchDataSource, fetchLogs, showAlert]);

  // Fetch data source details on mount
  useEffect(() => {
    fetchDataSource();
  }, [fetchDataSource]);

  // Fetch logs when data source is loaded
  useEffect(() => {
    if (dataSource) {
      fetchLogs();
    }
  }, [dataSource, fetchLogs]);

  // Render status badge based on data source status
  const renderStatusBadge = () => {
    let variant: 'success' | 'warning' | 'danger' | 'primary' = 'primary';
    
    switch (dataSource?.status) {
      case DataSourceStatus.ACTIVE:
        variant = 'success';
        break;
      case DataSourceStatus.WARNING:
        variant = 'warning';
        break;
      case DataSourceStatus.ERROR:
        variant = 'danger';
        break;
      case DataSourceStatus.INACTIVE:
      default:
        variant = 'primary';
        break;
    }
    
    return <Badge variant={variant}>{dataSource?.status}</Badge>;
  };

  // Render connection details based on data source type
  const renderConnectionDetails = () => {
    if (!dataSource) return null;

    switch (dataSource.source_type) {
      case DataSourceType.CSV:
        const csvSource = dataSource as CSVDataSource;
        return (
          <div className="data-source-details__section">
            <h4>File Details</h4>
            <div className="data-source-details__field-group">
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">File Name:</span>
                <span className="data-source-details__field-value">{csvSource.file_name}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Delimiter:</span>
                <span className="data-source-details__field-value">{csvSource.delimiter}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Has Header:</span>
                <span className="data-source-details__field-value">{csvSource.has_header ? 'Yes' : 'No'}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Date Format:</span>
                <span className="data-source-details__field-value">{csvSource.date_format}</span>
              </div>
            </div>
          </div>
        );
      
      case DataSourceType.DATABASE:
        const dbSource = dataSource as DatabaseDataSource;
        return (
          <div className="data-source-details__section">
            <h4>Database Connection</h4>
            <div className="data-source-details__field-group">
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Database Type:</span>
                <span className="data-source-details__field-value">{dbSource.database_type}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Host:</span>
                <span className="data-source-details__field-value">{dbSource.host}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Port:</span>
                <span className="data-source-details__field-value">{dbSource.port}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Database:</span>
                <span className="data-source-details__field-value">{dbSource.database}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Username:</span>
                <span className="data-source-details__field-value">{dbSource.username}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Query:</span>
                <span className="data-source-details__field-value code">{dbSource.query}</span>
              </div>
            </div>
          </div>
        );
      
      case DataSourceType.API:
        const apiSource = dataSource as APIDataSource;
        return (
          <div className="data-source-details__section">
            <h4>API Connection</h4>
            <div className="data-source-details__field-group">
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">URL:</span>
                <span className="data-source-details__field-value">{apiSource.url}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Method:</span>
                <span className="data-source-details__field-value">{apiSource.method}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Authentication:</span>
                <span className="data-source-details__field-value">{apiSource.auth_type}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Response Path:</span>
                <span className="data-source-details__field-value">{apiSource.response_path}</span>
              </div>
              
              {apiSource.headers && Object.keys(apiSource.headers).length > 0 && (
                <div className="data-source-details__field">
                  <span className="data-source-details__field-label">Headers:</span>
                  <div className="data-source-details__field-value code">
                    {Object.entries(apiSource.headers).map(([key, value]) => (
                      <div key={key}>{key}: {value}</div>
                    ))}
                  </div>
                </div>
              )}
              
              {apiSource.body && (
                <div className="data-source-details__field">
                  <span className="data-source-details__field-label">Request Body:</span>
                  <span className="data-source-details__field-value code">{apiSource.body}</span>
                </div>
              )}
            </div>
          </div>
        );
      
      case DataSourceType.TMS:
        const tmsSource = dataSource as TMSDataSource;
        return (
          <div className="data-source-details__section">
            <h4>TMS Connection</h4>
            <div className="data-source-details__field-group">
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">TMS Type:</span>
                <span className="data-source-details__field-value">{tmsSource.tms_type}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Connection URL:</span>
                <span className="data-source-details__field-value">{tmsSource.connection_url}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Username:</span>
                <span className="data-source-details__field-value">{tmsSource.username}</span>
              </div>
              
              {tmsSource.custom_parameters && Object.keys(tmsSource.custom_parameters).length > 0 && (
                <div className="data-source-details__field">
                  <span className="data-source-details__field-label">Custom Parameters:</span>
                  <div className="data-source-details__field-value code">
                    {Object.entries(tmsSource.custom_parameters).map(([key, value]) => (
                      <div key={key}>{key}: {value}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      
      case DataSourceType.ERP:
        const erpSource = dataSource as ERPDataSource;
        return (
          <div className="data-source-details__section">
            <h4>ERP Connection</h4>
            <div className="data-source-details__field-group">
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">ERP Type:</span>
                <span className="data-source-details__field-value">{erpSource.erp_type}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Connection URL:</span>
                <span className="data-source-details__field-value">{erpSource.connection_url}</span>
              </div>
              <div className="data-source-details__field">
                <span className="data-source-details__field-label">Username:</span>
                <span className="data-source-details__field-value">{erpSource.username}</span>
              </div>
              
              {erpSource.custom_parameters && Object.keys(erpSource.custom_parameters).length > 0 && (
                <div className="data-source-details__field">
                  <span className="data-source-details__field-label">Custom Parameters:</span>
                  <div className="data-source-details__field-value code">
                    {Object.entries(erpSource.custom_parameters).map(([key, value]) => (
                      <div key={key}>{key}: {value}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      
      default:
        return (
          <div className="data-source-details__section">
            <p>No connection details available for this data source type.</p>
          </div>
        );
    }
  };

  // Render field mapping table
  const renderFieldMapping = () => {
    if (!dataSource?.field_mapping) {
      return (
        <div className="data-source-details__section">
          <h4>Field Mapping</h4>
          <p>No field mapping information available.</p>
        </div>
      );
    }

    const { field_mapping } = dataSource;
    
    return (
      <div className="data-source-details__section">
        <h4>Field Mapping</h4>
        <table className="data-source-details__table">
          <thead>
            <tr>
              <th>Freight Data Field</th>
              <th>Source Field</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Freight Charge</td>
              <td>{field_mapping.freight_charge}</td>
            </tr>
            <tr>
              <td>Currency</td>
              <td>{field_mapping.currency}</td>
            </tr>
            <tr>
              <td>Origin</td>
              <td>{field_mapping.origin}</td>
            </tr>
            <tr>
              <td>Destination</td>
              <td>{field_mapping.destination}</td>
            </tr>
            <tr>
              <td>Date/Time</td>
              <td>{field_mapping.date_time}</td>
            </tr>
            {field_mapping.carrier && (
              <tr>
                <td>Carrier</td>
                <td>{field_mapping.carrier}</td>
              </tr>
            )}
            {field_mapping.mode && (
              <tr>
                <td>Transport Mode</td>
                <td>{field_mapping.mode}</td>
              </tr>
            )}
            {field_mapping.service_level && (
              <tr>
                <td>Service Level</td>
                <td>{field_mapping.service_level}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    );
  };

  // Render operation logs
  const renderLogs = () => {
    return (
      <div className="data-source-details__section">
        <h4>Recent Operations</h4>
        
        {logsLoading ? (
          <p>Loading logs...</p>
        ) : logs.length === 0 ? (
          <p>No operation logs available.</p>
        ) : (
          <table className="data-source-details__table">
            <thead>
              <tr>
                <th>Operation</th>
                <th>Status</th>
                <th>Timestamp</th>
                <th>Records</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.operation}</td>
                  <td>
                    <Badge 
                      variant={
                        log.status === 'success' ? 'success' :
                        log.status === 'failed' ? 'danger' :
                        log.status === 'warning' ? 'warning' :
                        'primary'
                      }
                    >
                      {log.status}
                    </Badge>
                  </td>
                  <td>{formatDate(log.started_at)}</td>
                  <td>
                    {log.records_processed !== null 
                      ? `${log.records_succeeded || 0}/${log.records_processed} processed` 
                      : '-'}
                  </td>
                  <td>{log.duration_seconds ? `${log.duration_seconds}s` : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    );
  };

  // Show loading state
  if (loading) {
    return (
      <Card className={classNames('data-source-details', 'is-loading', className)}>
        <div className="data-source-details__loading">
          <p>Loading data source details...</p>
        </div>
      </Card>
    );
  }

  // Show error state
  if (error) {
    return (
      <Card className={classNames('data-source-details', 'has-error', className)}>
        <div className="data-source-details__error">
          <p>Error: {error}</p>
          <Button onClick={fetchDataSource}>Retry</Button>
          {onBack && (
            <Button variant="outline-primary" onClick={onBack}>
              Back
            </Button>
          )}
        </div>
      </Card>
    );
  }

  // Show not found state
  if (!dataSource) {
    return (
      <Card className={classNames('data-source-details', 'not-found', className)}>
        <div className="data-source-details__not-found">
          <p>Data source not found.</p>
          {onBack && (
            <Button variant="outline-primary" onClick={onBack}>
              Back
            </Button>
          )}
        </div>
      </Card>
    );
  }

  // Render the data source details
  return (
    <Card 
      className={classNames('data-source-details', className)}
      title={dataSource.name}
      subtitle={`Data Source (${dataSource.source_type.toUpperCase()})`}
    >
      <div className="data-source-details__content">
        {/* Header with status and actions */}
        <div className="data-source-details__header">
          <div className="data-source-details__status">
            {renderStatusBadge()}
          </div>
          <div className="data-source-details__actions">
            {onEdit && (
              <Button 
                variant="outline-primary" 
                onClick={onEdit}
                leftIcon={<Icon name="edit" />}
              >
                Edit
              </Button>
            )}
            {onDelete && (
              <Button 
                variant="outline-danger" 
                onClick={onDelete}
                leftIcon={<Icon name="delete" />}
              >
                Delete
              </Button>
            )}
            <Button 
              variant="outline-secondary" 
              onClick={handleSync}
              disabled={syncInProgress}
              leftIcon={<Icon name="refresh" />}
            >
              {syncInProgress ? 'Syncing...' : 'Sync Now'}
            </Button>
          </div>
        </div>

        {/* Description */}
        {dataSource.description && (
          <div className="data-source-details__description">
            <p>{dataSource.description}</p>
          </div>
        )}

        {/* Metadata */}
        <div className="data-source-details__metadata">
          <div className="data-source-details__field">
            <span className="data-source-details__field-label">Created:</span>
            <span className="data-source-details__field-value">{formatDate(dataSource.created_at)}</span>
          </div>
          <div className="data-source-details__field">
            <span className="data-source-details__field-label">Last Updated:</span>
            <span className="data-source-details__field-value">{formatDate(dataSource.updated_at)}</span>
          </div>
          {dataSource.last_sync && (
            <div className="data-source-details__field">
              <span className="data-source-details__field-label">Last Synchronized:</span>
              <span className="data-source-details__field-value">{formatDate(dataSource.last_sync)}</span>
            </div>
          )}
        </div>

        {/* Connection details */}
        {renderConnectionDetails()}

        {/* Field mapping */}
        {renderFieldMapping()}

        {/* Operation logs */}
        {renderLogs()}
      </div>

      {/* Footer with back button */}
      <div className="data-source-details__footer">
        {onBack && (
          <Button 
            variant="outline-primary" 
            onClick={onBack}
            leftIcon={<Icon name="arrow-left" />}
          >
            Back to Data Sources
          </Button>
        )}
      </div>
    </Card>
  );
};

export default DataSourceDetails;