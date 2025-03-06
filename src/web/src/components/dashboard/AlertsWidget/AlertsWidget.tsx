import React, { useState, useEffect, useCallback } from 'react';
import Card from '../../common/Card';
import Alert from '../../common/Alert';
import Spinner from '../../common/Spinner';
import useApi from '../../../hooks/useApi';
import { getSystemAlerts } from '../../../api';
import { Alert as AlertType } from '../../../types';

/**
 * Props interface for the AlertsWidget component
 */
interface AlertsWidgetProps {
  /** Additional CSS class names */
  className?: string;
  /** Test ID for testing purposes */
  testId?: string;
}

/**
 * A dashboard widget that displays system alerts and notifications related to
 * freight price movements, data sources, and system status.
 */
const AlertsWidget: React.FC<AlertsWidgetProps> = ({ 
  className, 
  testId = 'alerts-widget' 
}) => {
  // State to track dismissed alerts by ID
  const [dismissedAlerts, setDismissedAlerts] = useState<string[]>([]);

  // Use the API hook to fetch system alerts
  const { state, actions } = useApi(getSystemAlerts);

  // Handle dismissing an alert
  const handleDismiss = useCallback((alertId: string) => {
    setDismissedAlerts(prev => [...prev, alertId]);
  }, []);

  // Fetch alerts when component mounts
  useEffect(() => {
    actions.execute();
  }, [actions]);

  // Safely extract alerts from the API response
  const alerts = (Array.isArray(state.data) ? state.data : []) as AlertType[];
  
  // Filter out dismissed alerts
  const filteredAlerts = alerts.filter(alert => 
    alert && alert.id && !dismissedAlerts.includes(alert.id)
  );

  return (
    <Card 
      title="Alerts" 
      className={className} 
      testId={testId}
    >
      {state.isLoading && (
        <div className="alerts-widget__loading">
          <Spinner />
        </div>
      )}
      
      {state.isError && state.error && (
        <Alert 
          type="error"
        >
          Failed to load alerts: {state.error.message || 'Unknown error'}
        </Alert>
      )}
      
      {!state.isLoading && !state.isError && filteredAlerts.length === 0 && (
        <div className="alerts-widget__empty">
          No alerts at this time
        </div>
      )}
      
      {filteredAlerts.map((alert) => (
        <Alert
          key={alert.id}
          type={alert.type || 'info'}
          dismissible={true}
          onDismiss={() => handleDismiss(alert.id)}
          testId={`alert-${alert.id}`}
        >
          {alert.message}
        </Alert>
      ))}
    </Card>
  );
};

export default AlertsWidget;