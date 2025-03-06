import React, { useState, useEffect } from 'react';
import { Card, FormGroup, Input, Select, Button, Alert, Spinner } from '../../common';
import useAuth from '../../../hooks/useAuth';
import useApi from '../../../hooks/useApi';
import { Permission } from '../../../types/auth.types';

/**
 * Interface defining the form values for system settings
 */
interface SystemSettingsFormValues {
  dataRetention: string;
  refreshInterval: string;
  apiRateLimit: number;
  enableAuditLogging: boolean;
  backupSchedule: string;
}

/**
 * Interface defining the API response structure for system settings
 */
interface SystemSettingsResponse {
  dataRetention: string;
  refreshInterval: string;
  apiRateLimit: number;
  enableAuditLogging: boolean;
  backupSchedule: string;
}

/**
 * A React component that provides an interface for administrators to configure
 * system-wide settings for the Freight Price Movement Agent application.
 * 
 * This component is only accessible to users with the CONFIGURE_SYSTEM permission
 * and allows management of data retention policies, refresh intervals, API rate limits,
 * and other system-level configurations.
 */
const SystemSettings: React.FC = () => {
  const { state: authState } = useAuth();
  const [formValues, setFormValues] = useState<SystemSettingsFormValues>({
    dataRetention: '3 years',
    refreshInterval: '24 hours',
    apiRateLimit: 100,
    enableAuditLogging: true,
    backupSchedule: 'Daily'
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Check if user has permission to access system settings
  const hasPermission = authState.user?.role === 'admin' || 
    (authState.user?.permissions && authState.user.permissions.includes(Permission.CONFIGURE_SYSTEM));

  // Use API hook to fetch system settings
  const {
    state: { data, isLoading, isError, error },
    actions: { execute: fetchSettings }
  } = useApi<SystemSettingsResponse>(
    () => fetch('/api/v1/admin/system-settings').then(res => res.json()),
    { immediate: hasPermission }
  );

  // Use API hook to update system settings
  const {
    actions: { execute: updateSettings }
  } = useApi(
    (settings: SystemSettingsFormValues) => 
      fetch('/api/v1/admin/system-settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      }).then(res => res.json())
  );

  // Initialize form with fetched settings
  useEffect(() => {
    if (data) {
      setFormValues({
        dataRetention: data.dataRetention,
        refreshInterval: data.refreshInterval,
        apiRateLimit: data.apiRateLimit,
        enableAuditLogging: data.enableAuditLogging,
        backupSchedule: data.backupSchedule
      });
    }
  }, [data]);

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    setFormValues(prevValues => ({
      ...prevValues,
      [name]: type === 'checkbox' 
        ? (e.target as HTMLInputElement).checked 
        : type === 'number' 
          ? parseInt(value, 10) 
          : value
    }));
  };

  // Handle checkbox changes
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    
    setFormValues(prevValues => ({
      ...prevValues,
      [name]: checked
    }));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Reset status
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);
    
    try {
      await updateSettings(formValues);
      setSubmitSuccess(true);
      
      // Reset success message after 5 seconds
      setTimeout(() => {
        setSubmitSuccess(false);
      }, 5000);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Failed to update system settings');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Data retention options
  const dataRetentionOptions = [
    { value: '1 year', label: '1 year' },
    { value: '3 years', label: '3 years' },
    { value: '5 years', label: '5 years' },
    { value: '7 years', label: '7 years' }
  ];

  // Refresh interval options
  const refreshIntervalOptions = [
    { value: '1 hour', label: '1 hour' },
    { value: '6 hours', label: '6 hours' },
    { value: '12 hours', label: '12 hours' },
    { value: '24 hours', label: '24 hours' }
  ];

  // Backup schedule options
  const backupScheduleOptions = [
    { value: 'Daily', label: 'Daily' },
    { value: 'Weekly', label: 'Weekly' },
    { value: 'Monthly', label: 'Monthly' },
    { value: 'Quarterly', label: 'Quarterly' }
  ];

  // If user doesn't have permission, show access denied message
  if (!hasPermission) {
    return (
      <Card title="System Settings" className="system-settings">
        <Alert type="error" title="Access Denied">
          You do not have permission to access system settings. Please contact an administrator if you require access.
        </Alert>
      </Card>
    );
  }

  // Show loading spinner while fetching settings
  if (isLoading) {
    return (
      <Card title="System Settings" className="system-settings">
        <div className="system-settings__loading">
          <Spinner size="lg" />
          <p>Loading system settings...</p>
        </div>
      </Card>
    );
  }

  // Show error message if fetch fails
  if (isError && error) {
    return (
      <Card title="System Settings" className="system-settings">
        <Alert type="error" title="Error Loading Settings">
          {error.message || 'Failed to load system settings. Please try again later.'}
        </Alert>
        <Button onClick={() => fetchSettings()}>Retry</Button>
      </Card>
    );
  }

  // Render system settings form
  return (
    <Card title="System Settings" className="system-settings">
      {submitSuccess && (
        <Alert type="success" dismissible title="Settings Updated">
          System settings have been successfully updated.
        </Alert>
      )}
      
      {submitError && (
        <Alert type="error" dismissible title="Update Failed">
          {submitError}
        </Alert>
      )}
      
      <form onSubmit={handleSubmit} className="system-settings__form">
        <div className="system-settings__section">
          <h3 className="system-settings__section-title">Data Management</h3>
          
          <FormGroup
            id="dataRetention"
            label="Data Retention"
            required
          >
            <Select
              id="dataRetention"
              name="dataRetention"
              value={formValues.dataRetention}
              options={dataRetentionOptions}
              onChange={handleInputChange}
              disabled={isSubmitting}
            />
          </FormGroup>
          
          <FormGroup
            id="refreshInterval"
            label="Refresh Interval"
            required
          >
            <Select
              id="refreshInterval"
              name="refreshInterval"
              value={formValues.refreshInterval}
              options={refreshIntervalOptions}
              onChange={handleInputChange}
              disabled={isSubmitting}
            />
          </FormGroup>
          
          <FormGroup
            id="apiRateLimit"
            label="API Rate Limit"
            helpText="Maximum number of API requests allowed per minute"
            required
          >
            <Input
              id="apiRateLimit"
              name="apiRateLimit"
              type="number"
              value={formValues.apiRateLimit.toString()}
              onChange={handleInputChange}
              min={1}
              max={1000}
              disabled={isSubmitting}
            />
          </FormGroup>
        </div>
        
        <div className="system-settings__section">
          <h3 className="system-settings__section-title">Security & Compliance</h3>
          
          <FormGroup
            id="enableAuditLogging"
            label="Enable Audit Logging"
            helpText="Track all system actions for compliance and security purposes"
          >
            <div className="checkbox-wrapper">
              <input
                type="checkbox"
                id="enableAuditLogging"
                name="enableAuditLogging"
                checked={formValues.enableAuditLogging}
                onChange={handleCheckboxChange}
                disabled={isSubmitting}
                className="checkbox-input"
              />
              <label htmlFor="enableAuditLogging" className="checkbox-label">
                Enable comprehensive audit logging
              </label>
            </div>
          </FormGroup>
          
          <FormGroup
            id="backupSchedule"
            label="Backup Schedule"
            required
          >
            <Select
              id="backupSchedule"
              name="backupSchedule"
              value={formValues.backupSchedule}
              options={backupScheduleOptions}
              onChange={handleInputChange}
              disabled={isSubmitting}
            />
          </FormGroup>
        </div>
        
        <div className="system-settings__section">
          <h3 className="system-settings__section-title">Administration</h3>
          
          <div className="system-settings__admin-buttons">
            <Button 
              variant="secondary" 
              disabled={isSubmitting}
              onClick={() => window.location.href = '/admin/users'}
            >
              Manage Users
            </Button>
            
            <Button 
              variant="secondary" 
              disabled={isSubmitting}
              onClick={() => window.location.href = '/admin/logs'}
            >
              System Logs
            </Button>
            
            <Button 
              variant="secondary" 
              disabled={isSubmitting}
              onClick={() => window.location.href = '/admin/backup'}
            >
              Backup/Restore
            </Button>
          </div>
        </div>
        
        <div className="system-settings__actions">
          <Button 
            type="submit" 
            disabled={isSubmitting}
            isLoading={isSubmitting}
          >
            Save Settings
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default SystemSettings;