import React, { useState, useEffect } from 'react';
import FormGroup from '../../common/FormGroup';
import Checkbox from '../../common/Checkbox';
import Input from '../../common/Input';
import Button from '../../common/Button';
import useAlert from '../../../hooks/useAlert';
import { getUserNotificationSettings, updateUserNotificationSettings } from '../../../api/user-api';
import { UserNotificationSettingsUpdateRequest } from '../../../types/user.types';

/**
 * Interface for the notification settings state
 */
interface NotificationSettingsState {
  emailNotifications: boolean;
  smsNotifications: boolean;
  inAppNotifications: boolean;
  notifyOnPriceChanges: boolean;
  notifyOnDataSourceUpdates: boolean;
  notifyOnSystemMaintenance: boolean;
  significantPriceChangeThreshold: number;
}

/**
 * Component for configuring user notification preferences in the Freight Price Movement Agent
 * Allows users to manage notification channels, types, and threshold settings
 */
const NotificationSettings: React.FC = () => {
  // Initialize state with default values
  const [settings, setSettings] = useState<NotificationSettingsState>({
    emailNotifications: false,
    smsNotifications: false,
    inAppNotifications: false,
    notifyOnPriceChanges: false,
    notifyOnDataSourceUpdates: false,
    notifyOnSystemMaintenance: false,
    significantPriceChangeThreshold: 5,
  });

  // Loading and error states
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Alert hooks for success/error messages
  const { showSuccess, showError } = useAlert();

  // Fetch user notification settings on component mount
  useEffect(() => {
    const fetchUserSettings = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Get the current user's ID - in a real app this would come from auth context
        // For now, we'll use 'me' to indicate current user
        const userId = 'me';
        
        const response = await getUserNotificationSettings(userId);
        
        if (response.success && response.data) {
          const userData = response.data;
          setSettings({
            emailNotifications: userData.emailNotifications,
            smsNotifications: userData.smsNotifications,
            inAppNotifications: userData.inAppNotifications,
            notifyOnPriceChanges: userData.preferences?.notifyOnPriceChanges || false,
            notifyOnDataSourceUpdates: userData.preferences?.notifyOnDataSourceUpdates || false,
            notifyOnSystemMaintenance: userData.preferences?.notifyOnSystemMaintenance || false,
            significantPriceChangeThreshold: userData.preferences?.significantPriceChangeThreshold || 5,
          });
        } else {
          throw new Error(response.error?.message || 'Failed to fetch notification settings');
        }
      } catch (err) {
        console.error('Error fetching notification settings:', err);
        setError('Failed to load notification settings. Please try again.');
        showError('Failed to load notification settings');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserSettings();
  }, [showError]);

  // Handle checkbox changes
  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    setSettings(prev => ({
      ...prev,
      [name]: checked,
    }));
  };

  // Handle input changes for numeric values
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    
    // For the threshold, we want to ensure it's a valid number
    if (name === 'significantPriceChangeThreshold') {
      // Convert to number and ensure it's positive
      const numValue = Math.max(0, parseFloat(value) || 0);
      setSettings(prev => ({
        ...prev,
        [name]: numValue,
      }));
    } else {
      setSettings(prev => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  // Handle form submission
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    try {
      setIsSaving(true);
      setError(null);
      
      // Get the current user's ID - in a real app this would come from auth context
      const userId = 'me';
      
      // Prepare update request object
      const updateRequest: UserNotificationSettingsUpdateRequest = {
        emailNotifications: settings.emailNotifications,
        smsNotifications: settings.smsNotifications,
        inAppNotifications: settings.inAppNotifications,
        notifyOnPriceChanges: settings.notifyOnPriceChanges,
        notifyOnDataSourceUpdates: settings.notifyOnDataSourceUpdates,
        notifyOnSystemMaintenance: settings.notifyOnSystemMaintenance,
        significantPriceChangeThreshold: settings.significantPriceChangeThreshold,
      };
      
      const response = await updateUserNotificationSettings(userId, updateRequest);
      
      if (response.success) {
        showSuccess('Notification settings updated successfully');
      } else {
        throw new Error(response.error?.message || 'Failed to update notification settings');
      }
    } catch (err) {
      console.error('Error updating notification settings:', err);
      setError('Failed to save notification settings. Please try again.');
      showError('Failed to save notification settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} aria-busy={isLoading || isSaving}>
      <h2>Notifications</h2>
      
      {error && <div className="error-message" role="alert">{error}</div>}
      
      <div className="notification-settings">
        <div className="notification-section">
          <h3>Notification Channels</h3>
          
          <div className="checkbox-group">
            <Checkbox
              id="emailNotifications"
              name="emailNotifications"
              label="Email notifications"
              checked={settings.emailNotifications}
              onChange={handleCheckboxChange}
              disabled={isLoading || isSaving}
            />
            
            <Checkbox
              id="smsNotifications"
              name="smsNotifications"
              label="SMS notifications"
              checked={settings.smsNotifications}
              onChange={handleCheckboxChange}
              disabled={isLoading || isSaving}
            />
            
            <Checkbox
              id="inAppNotifications"
              name="inAppNotifications"
              label="In-app notifications"
              checked={settings.inAppNotifications}
              onChange={handleCheckboxChange}
              disabled={isLoading || isSaving}
            />
          </div>
        </div>
        
        <div className="notification-section">
          <h3>Notify me about:</h3>
          
          <div className="checkbox-group">
            <Checkbox
              id="notifyOnPriceChanges"
              name="notifyOnPriceChanges"
              label="Significant price changes"
              checked={settings.notifyOnPriceChanges}
              onChange={handleCheckboxChange}
              disabled={isLoading || isSaving}
            />
            
            <Checkbox
              id="notifyOnDataSourceUpdates"
              name="notifyOnDataSourceUpdates"
              label="Data source updates"
              checked={settings.notifyOnDataSourceUpdates}
              onChange={handleCheckboxChange}
              disabled={isLoading || isSaving}
            />
            
            <Checkbox
              id="notifyOnSystemMaintenance"
              name="notifyOnSystemMaintenance"
              label="System maintenance"
              checked={settings.notifyOnSystemMaintenance}
              onChange={handleCheckboxChange}
              disabled={isLoading || isSaving}
            />
          </div>
        </div>
        
        <div className="notification-section">
          <h3>Threshold Settings</h3>
          
          <FormGroup
            id="significantPriceChangeThreshold"
            label="Significant price change threshold (%)"
            helpText="You will be notified when price changes exceed this percentage"
          >
            <Input
              id="significantPriceChangeThreshold"
              name="significantPriceChangeThreshold"
              type="number"
              value={settings.significantPriceChangeThreshold.toString()}
              onChange={handleInputChange}
              disabled={isLoading || isSaving}
              min="0"
              max="100"
              step="0.1"
              aria-label="Significant price change threshold percentage"
            />
          </FormGroup>
        </div>
      </div>
      
      <div className="form-actions">
        <Button 
          type="submit"
          isLoading={isSaving}
          disabled={isLoading || isSaving}
        >
          Save
        </Button>
      </div>
    </form>
  );
};

export default NotificationSettings;