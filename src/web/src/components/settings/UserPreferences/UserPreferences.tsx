# src/web/src/components/settings/UserPreferences/UserPreferences.tsx
```typescript
import React, { useState, useEffect } from 'react'; // ^18.2.0
import {
  FormGroup,
  Input,
  Select,
  RadioButton,
  Button,
  Checkbox,
} from '../../common';
import { useForm } from '../../../hooks/useForm';
import { useAuth } from '../../../hooks/useAuth';
import { useTheme } from '../../../hooks/useTheme';
import { useAlert } from '../../../hooks/useAlert';
import { updateCurrentUserPreferences } from '../../../api/user-api';
import { Theme, DateFormat, UserPreferencesUpdateRequest } from '../../../types/user.types';
import { SUPPORTED_CURRENCIES } from '../../../config/constants';

/**
 * Component for managing user preferences settings
 * @returns Rendered user preferences form
 */
const UserPreferences: React.FC = () => {
  // Access current user data from authentication context
  const { state: authState, logout, refreshSession } = useAuth();
  const { user } = authState;

  // Access theme management functions
  const { theme, setTheme } = useTheme();

  // Access alert display functions
  const { showSuccess, showError } = useAlert();

  // Track loading state during form submission
  const [isLoading, setIsLoading] = useState(false);

  // Initialize form with current user preferences
  const {
    values,
    handleChange,
    handleSubmit,
    setFieldError,
  } = useForm<UserPreferencesUpdateRequest>({
    initialValues: {
      defaultCurrency: user?.defaultCurrency || 'USD',
      dateFormat: user?.dateFormat || DateFormat.MM_DD_YYYY,
      theme: user?.theme || Theme.SYSTEM,
      emailNotifications: user?.emailNotifications || false,
      smsNotifications: user?.smsNotifications || false,
      inAppNotifications: user?.inAppNotifications || false,
      preferences: user?.preferences || {
        significantPriceChangeThreshold: 5,
        defaultView: 'dashboard',
        dashboardLayout: {},
        notifyOnPriceChanges: true,
        notifyOnDataSourceUpdates: true,
        notifyOnSystemMaintenance: false,
      },
    },
    onSubmit: async (values) => {
      setIsLoading(true);
      try {
        // Call API to update user preferences
        const response = await updateCurrentUserPreferences(values);

        if (response.success) {
          // Display success notification
          showSuccess('Preferences updated successfully!');
          // Refresh the session to update the user object
          await refreshSession();
        } else {
          // Display error notification
          showError(response.error?.message || 'Failed to update preferences.');
        }
      } catch (error: any) {
        // Display generic error notification
        showError(error.message || 'An unexpected error occurred.');
      } finally {
        setIsLoading(false);
      }
    },
  });

  // Handle theme change and apply it immediately
  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    handleChange({
      target: { name: 'theme', value: newTheme },
    } as React.ChangeEvent<HTMLInputElement>);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* User Information */}
      <FormGroup label="Display Name">
        <Input
          type="text"
          value={user?.firstName ? `${user.firstName} ${user.lastName}` : ''}
          readOnly
          disabled
        />
      </FormGroup>
      <FormGroup label="Email">
        <Input type="email" value={user?.email || ''} readOnly disabled />
      </FormGroup>

      {/* Display Preferences */}
      <FormGroup label="Default Currency">
        <Select
          name="defaultCurrency"
          value={values.defaultCurrency}
          onChange={handleChange}
          options={SUPPORTED_CURRENCIES.map((currency) => ({
            value: currency,
            label: currency,
          }))}
        />
      </FormGroup>
      <FormGroup label="Date Format">
        <Select
          name="dateFormat"
          value={values.dateFormat}
          onChange={handleChange}
          options={[
            { value: DateFormat.MM_DD_YYYY, label: 'MM/DD/YYYY' },
            { value: DateFormat.DD_MM_YYYY, label: 'DD/MM/YYYY' },
            { value: DateFormat.YYYY_MM_DD, label: 'YYYY-MM-DD' },
          ]}
        />
      </FormGroup>
      <FormGroup label="Theme">
        <RadioButton
          id="theme-light"
          name="theme"
          value={Theme.LIGHT}
          label="Light"
          checked={values.theme === Theme.LIGHT}
          onChange={() => handleThemeChange(Theme.LIGHT)}
        />
        <RadioButton
          id="theme-dark"
          name="theme"
          value={Theme.DARK}
          label="Dark"
          checked={values.theme === Theme.DARK}
          onChange={() => handleThemeChange(Theme.DARK)}
        />
        <RadioButton
          id="theme-system"
          name="theme"
          value={Theme.SYSTEM}
          label="System"
          checked={values.theme === Theme.SYSTEM}
          onChange={() => handleThemeChange(Theme.SYSTEM)}
        />
      </FormGroup>

      {/* Notification Preferences */}
      <FormGroup label="Notifications">
        <Checkbox
          id="emailNotifications"
          name="emailNotifications"
          label="Email notifications"
          checked={values.emailNotifications}
          onChange={handleChange}
        />
        <Checkbox
          id="smsNotifications"
          name="smsNotifications"
          label="SMS notifications"
          checked={values.smsNotifications}
          onChange={handleChange}
        />
        <Checkbox
          id="inAppNotifications"
          name="inAppNotifications"
          label="In-app notifications"
          checked={values.inAppNotifications}
          onChange={handleChange}
        />
      </FormGroup>

      {/* Form Actions */}
      <Button type="submit" disabled={isLoading}>
        {isLoading ? 'Saving...' : 'Save'}
      </Button>
    </form>
  );
};

export default UserPreferences;