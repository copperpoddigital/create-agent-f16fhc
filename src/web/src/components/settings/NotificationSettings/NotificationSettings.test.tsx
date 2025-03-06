import React from 'react';
import { render, act } from '@testing-library/react';
import NotificationSettings from './NotificationSettings';
import { customRender, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';
import { getUserNotificationSettings, updateUserNotificationSettings } from '../../../api/user-api';
import { AlertProvider } from '../../../contexts/AlertContext';

// Mock the API functions
jest.mock('../../../api/user-api', () => ({
  getUserNotificationSettings: jest.fn(),
  updateUserNotificationSettings: jest.fn()
}));

describe('NotificationSettings Component', () => {
  // Setup default mock implementations
  beforeEach(() => {
    jest.clearAllMocks();
    // Default mock implementations
    (getUserNotificationSettings as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        emailNotifications: true,
        smsNotifications: false,
        inAppNotifications: true,
        preferences: {
          notifyOnPriceChanges: true,
          notifyOnDataSourceUpdates: true,
          notifyOnSystemMaintenance: false,
          significantPriceChangeThreshold: 5
        }
      },
      error: null
    });

    (updateUserNotificationSettings as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        emailNotifications: true,
        smsNotifications: false,
        inAppNotifications: true,
        preferences: {
          notifyOnPriceChanges: true,
          notifyOnDataSourceUpdates: true,
          notifyOnSystemMaintenance: false,
          significantPriceChangeThreshold: 5
        }
      },
      error: null
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  // Helper function to render component with AlertProvider
  const renderNotificationSettings = () => {
    return customRender(
      <AlertProvider>
        <NotificationSettings />
      </AlertProvider>
    );
  };

  it('renders the component correctly', async () => {
    renderNotificationSettings();

    // Wait for data to load
    await waitFor(() => expect(getUserNotificationSettings).toHaveBeenCalledWith('me'));

    // Check if all expected elements are rendered
    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('Notification Channels')).toBeInTheDocument();
    expect(screen.getByText('Notify me about:')).toBeInTheDocument();
    expect(screen.getByText('Threshold Settings')).toBeInTheDocument();

    // Check form elements
    expect(screen.getByLabelText('Email notifications')).toBeInTheDocument();
    expect(screen.getByLabelText('SMS notifications')).toBeInTheDocument();
    expect(screen.getByLabelText('In-app notifications')).toBeInTheDocument();
    expect(screen.getByLabelText('Significant price changes')).toBeInTheDocument();
    expect(screen.getByLabelText('Data source updates')).toBeInTheDocument();
    expect(screen.getByLabelText('System maintenance')).toBeInTheDocument();
    expect(screen.getByLabelText('Significant price change threshold percentage')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
  });

  it('loads user notification settings on mount', async () => {
    // Mock specific settings for this test
    (getUserNotificationSettings as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        emailNotifications: true,
        smsNotifications: true,
        inAppNotifications: false,
        preferences: {
          notifyOnPriceChanges: true,
          notifyOnDataSourceUpdates: false,
          notifyOnSystemMaintenance: true,
          significantPriceChangeThreshold: 10
        }
      },
      error: null
    });

    renderNotificationSettings();

    // Wait for data to load
    await waitFor(() => expect(getUserNotificationSettings).toHaveBeenCalledWith('me'));

    // Verify form is populated with the loaded settings
    expect(screen.getByLabelText('Email notifications')).toBeChecked();
    expect(screen.getByLabelText('SMS notifications')).toBeChecked();
    expect(screen.getByLabelText('In-app notifications')).not.toBeChecked();
    expect(screen.getByLabelText('Significant price changes')).toBeChecked();
    expect(screen.getByLabelText('Data source updates')).not.toBeChecked();
    expect(screen.getByLabelText('System maintenance')).toBeChecked();
    expect(screen.getByLabelText('Significant price change threshold percentage')).toHaveValue('10');
  });

  it('displays error when initial data loading fails', async () => {
    // Mock API failure
    (getUserNotificationSettings as jest.Mock).mockRejectedValue(
      new Error('Failed to fetch settings')
    );

    renderNotificationSettings();

    // Check for error message
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Failed to load notification settings. Please try again.')).toBeInTheDocument();
    });
  });

  it('displays error when API returns error response', async () => {
    // Mock API returning error
    (getUserNotificationSettings as jest.Mock).mockResolvedValue({
      success: false,
      data: null,
      error: {
        message: 'Failed to fetch settings'
      }
    });

    renderNotificationSettings();

    // Check for error message
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Failed to load notification settings. Please try again.')).toBeInTheDocument();
    });
  });

  it('handles checkbox changes correctly', async () => {
    renderNotificationSettings();

    // Wait for data to load
    await waitFor(() => expect(getUserNotificationSettings).toHaveBeenCalled());

    // Initially checked based on our mock
    const emailCheckbox = screen.getByLabelText('Email notifications');
    expect(emailCheckbox).toBeChecked();

    // Click to uncheck
    await userEvent.click(emailCheckbox);
    expect(emailCheckbox).not.toBeChecked();

    // Click to check again
    await userEvent.click(emailCheckbox);
    expect(emailCheckbox).toBeChecked();
  });

  it('handles threshold input changes correctly', async () => {
    renderNotificationSettings();

    // Wait for data to load
    await waitFor(() => expect(getUserNotificationSettings).toHaveBeenCalled());

    // Get the threshold input
    const thresholdInput = screen.getByLabelText('Significant price change threshold percentage');
    
    // Clear and change value
    await userEvent.clear(thresholdInput);
    await userEvent.type(thresholdInput, '15');
    
    // Check if the value was updated
    expect(thresholdInput).toHaveValue('15');
  });

  it('submits the form with updated settings', async () => {
    renderNotificationSettings();

    // Wait for data to load
    await waitFor(() => expect(getUserNotificationSettings).toHaveBeenCalled());

    // Make changes to form
    const smsCheckbox = screen.getByLabelText('SMS notifications');
    const systemMaintenanceCheckbox = screen.getByLabelText('System maintenance');
    const thresholdInput = screen.getByLabelText('Significant price change threshold percentage');

    // Click checkboxes and update threshold
    await userEvent.click(smsCheckbox);
    await userEvent.click(systemMaintenanceCheckbox);
    await userEvent.clear(thresholdInput);
    await userEvent.type(thresholdInput, '7.5');

    // Submit form
    const saveButton = screen.getByRole('button', { name: 'Save' });
    await userEvent.click(saveButton);

    // Wait for update API to be called with the correct parameters
    await waitFor(() => {
      expect(updateUserNotificationSettings).toHaveBeenCalledWith('me', {
        emailNotifications: true,
        smsNotifications: true,
        inAppNotifications: true,
        notifyOnPriceChanges: true,
        notifyOnDataSourceUpdates: true,
        notifyOnSystemMaintenance: true,
        significantPriceChangeThreshold: 7.5
      });
    });
  });

  it('displays error message when API call fails', async () => {
    // Mock API with a rejected promise
    (updateUserNotificationSettings as jest.Mock).mockRejectedValue(
      new Error('API Error')
    );

    renderNotificationSettings();

    // Wait for data to load
    await waitFor(() => expect(getUserNotificationSettings).toHaveBeenCalled());

    // Submit form
    const saveButton = screen.getByRole('button', { name: 'Save' });
    await userEvent.click(saveButton);

    // Check for error message
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Failed to save notification settings. Please try again.')).toBeInTheDocument();
    });
  });

  it('displays loading state during API calls', async () => {
    // Mock delayed API responses
    (getUserNotificationSettings as jest.Mock).mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            success: true,
            data: {
              emailNotifications: true,
              smsNotifications: false,
              inAppNotifications: true,
              preferences: {
                notifyOnPriceChanges: true,
                notifyOnDataSourceUpdates: true,
                notifyOnSystemMaintenance: false,
                significantPriceChangeThreshold: 5
              }
            },
            error: null
          });
        }, 100);
      });
    });

    (updateUserNotificationSettings as jest.Mock).mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            success: true,
            data: {},
            error: null
          });
        }, 100);
      });
    });

    renderNotificationSettings();

    // Check for loading state during initial load
    expect(screen.getByRole('form')).toHaveAttribute('aria-busy', 'true');
    
    // Wait for data to load
    await waitFor(() => {
      expect(getUserNotificationSettings).toHaveBeenCalled();
    });

    // After loading, aria-busy should no longer be true
    await waitFor(() => {
      const form = screen.getByRole('form');
      expect(form).not.toHaveAttribute('aria-busy', 'true');
    });

    // Submit form to trigger saving
    const saveButton = screen.getByRole('button', { name: 'Save' });
    await userEvent.click(saveButton);

    // Check for loading state during save
    expect(screen.getByRole('form')).toHaveAttribute('aria-busy', 'true');
    
    // Wait for saving to complete
    await waitFor(() => {
      expect(updateUserNotificationSettings).toHaveBeenCalled();
    });

    // After saving, aria-busy should no longer be true
    await waitFor(() => {
      const form = screen.getByRole('form');
      expect(form).not.toHaveAttribute('aria-busy', 'true');
    });
  });
});