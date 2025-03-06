import React, { useState } from 'react';
import FormGroup from '../../common/FormGroup';
import Input from '../../common/Input';
import Select from '../../common/Select';
import Button from '../../common/Button';
import useForm from '../../../hooks/useForm';
import useAuth from '../../../hooks/useAuth';
import useAlert from '../../../hooks/useAlert';
import { validateEmail, isRequired } from '../../../utils/validation-utils';
import { 
  updateCurrentUserProfile, 
  updateCurrentUserPreferences 
} from '../../../api/user-api';
import { 
  Theme, 
  DateFormat, 
  UserProfileUpdateRequest,
  UserPreferencesUpdateRequest
} from '../../../types/user.types';

interface UserProfileFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

// Validation function for the user profile form
const validateUserProfile = (values: Record<string, any>): Record<string, string> => {
  const errors: Record<string, string> = {};

  // First Name validation
  const firstNameError = isRequired(values.firstName);
  if (firstNameError) {
    errors.firstName = firstNameError;
  }

  // Last Name validation
  const lastNameError = isRequired(values.lastName);
  if (lastNameError) {
    errors.lastName = lastNameError;
  }

  // Email validation
  const emailError = validateEmail(values.email);
  if (emailError) {
    errors.email = emailError;
  }

  return errors;
};

const UserProfileForm: React.FC<UserProfileFormProps> = ({ onSuccess, onCancel }) => {
  const { state: authState } = useAuth();
  const { showSuccess, showError } = useAlert();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Get the current user from auth state
  const user = authState.user;
  
  // Initialize form with current user data
  const { 
    values, 
    errors, 
    touched, 
    handleChange, 
    handleBlur, 
    handleSubmit,
    setFieldValue 
  } = useForm({
    initialValues: {
      firstName: user?.firstName || '',
      lastName: user?.lastName || '',
      email: user?.email || '',
      defaultCurrency: user?.defaultCurrency || 'USD',
      dateFormat: user?.dateFormat || DateFormat.MM_DD_YYYY,
      theme: user?.theme || Theme.LIGHT,
      emailNotifications: user?.emailNotifications || false,
      smsNotifications: user?.smsNotifications || false,
      inAppNotifications: user?.inAppNotifications || false,
      notifyOnPriceChanges: user?.preferences?.notifyOnPriceChanges || false,
      notifyOnDataSourceUpdates: user?.preferences?.notifyOnDataSourceUpdates || false,
      notifyOnSystemMaintenance: user?.preferences?.notifyOnSystemMaintenance || false,
    },
    validate: validateUserProfile,
    onSubmit: handleFormSubmit,
    validateOnBlur: true
  });
  
  // Handle checkbox change
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFieldValue(name, checked);
  };

  // Handle form submission
  async function handleFormSubmit(formValues: Record<string, any>) {
    if (!user) {
      showError('User information is not available');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Prepare profile update request
      const profileUpdate: UserProfileUpdateRequest = {
        firstName: formValues.firstName,
        lastName: formValues.lastName,
        email: formValues.email
      };
      
      // Prepare preferences update request
      const preferencesUpdate: UserPreferencesUpdateRequest = {
        defaultCurrency: formValues.defaultCurrency,
        dateFormat: formValues.dateFormat as DateFormat,
        theme: formValues.theme as Theme,
        emailNotifications: formValues.emailNotifications,
        smsNotifications: formValues.smsNotifications,
        inAppNotifications: formValues.inAppNotifications,
        preferences: {
          notifyOnPriceChanges: formValues.notifyOnPriceChanges,
          notifyOnDataSourceUpdates: formValues.notifyOnDataSourceUpdates,
          notifyOnSystemMaintenance: formValues.notifyOnSystemMaintenance,
          // Maintain existing values or use defaults
          significantPriceChangeThreshold: user.preferences?.significantPriceChangeThreshold || 5,
          defaultView: user.preferences?.defaultView || 'dashboard',
          dashboardLayout: user.preferences?.dashboardLayout || {}
        }
      };
      
      // Update profile
      const profileResponse = await updateCurrentUserProfile(profileUpdate);
      if (!profileResponse.success) {
        throw new Error(profileResponse.error?.message || 'Failed to update profile');
      }
      
      // Update preferences
      const preferencesResponse = await updateCurrentUserPreferences(preferencesUpdate);
      if (!preferencesResponse.success) {
        throw new Error(preferencesResponse.error?.message || 'Failed to update preferences');
      }
      
      showSuccess('Profile updated successfully');
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      showError(error instanceof Error ? error.message : 'An error occurred while updating your profile');
    } finally {
      setIsSubmitting(false);
    }
  }

  // Dropdown options
  const currencyOptions = [
    { value: 'USD', label: 'USD - US Dollar' },
    { value: 'EUR', label: 'EUR - Euro' },
    { value: 'GBP', label: 'GBP - British Pound' },
    { value: 'JPY', label: 'JPY - Japanese Yen' },
    { value: 'CAD', label: 'CAD - Canadian Dollar' },
    { value: 'AUD', label: 'AUD - Australian Dollar' },
    { value: 'CNY', label: 'CNY - Chinese Yuan' },
    { value: 'HKD', label: 'HKD - Hong Kong Dollar' },
    { value: 'SGD', label: 'SGD - Singapore Dollar' }
  ];
  
  const dateFormatOptions = [
    { value: DateFormat.MM_DD_YYYY, label: 'MM/DD/YYYY' },
    { value: DateFormat.DD_MM_YYYY, label: 'DD/MM/YYYY' },
    { value: DateFormat.YYYY_MM_DD, label: 'YYYY-MM-DD' }
  ];
  
  const themeOptions = [
    { value: Theme.LIGHT, label: 'Light' },
    { value: Theme.DARK, label: 'Dark' },
    { value: Theme.SYSTEM, label: 'System' }
  ];

  // Handle cancel button click
  const handleCancel = (e: React.MouseEvent) => {
    e.preventDefault();
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="user-profile-form">
      <div className="form-section">
        <h3>Profile Information</h3>
        
        <FormGroup
          id="firstName"
          label="First Name"
          required
          isValid={touched.firstName && !errors.firstName}
          isInvalid={touched.firstName && !!errors.firstName}
          validationMessage={touched.firstName ? errors.firstName : undefined}
        >
          <Input
            name="firstName"
            value={values.firstName}
            onChange={handleChange}
            onBlur={handleBlur}
            disabled={isSubmitting}
            required
          />
        </FormGroup>
        
        <FormGroup
          id="lastName"
          label="Last Name"
          required
          isValid={touched.lastName && !errors.lastName}
          isInvalid={touched.lastName && !!errors.lastName}
          validationMessage={touched.lastName ? errors.lastName : undefined}
        >
          <Input
            name="lastName"
            value={values.lastName}
            onChange={handleChange}
            onBlur={handleBlur}
            disabled={isSubmitting}
            required
          />
        </FormGroup>
        
        <FormGroup
          id="email"
          label="Email"
          required
          isValid={touched.email && !errors.email}
          isInvalid={touched.email && !!errors.email}
          validationMessage={touched.email ? errors.email : undefined}
        >
          <Input
            name="email"
            type="email"
            value={values.email}
            onChange={handleChange}
            onBlur={handleBlur}
            disabled={isSubmitting}
            required
          />
        </FormGroup>
      </div>
      
      <div className="form-section">
        <h3>Preferences</h3>
        
        <FormGroup
          id="defaultCurrency"
          label="Default Currency"
        >
          <Select
            name="defaultCurrency"
            value={values.defaultCurrency}
            options={currencyOptions}
            onChange={handleChange}
            onBlur={handleBlur}
            disabled={isSubmitting}
          />
        </FormGroup>
        
        <FormGroup
          id="dateFormat"
          label="Date Format"
        >
          <Select
            name="dateFormat"
            value={values.dateFormat}
            options={dateFormatOptions}
            onChange={handleChange}
            onBlur={handleBlur}
            disabled={isSubmitting}
          />
        </FormGroup>
        
        <FormGroup
          id="theme"
          label="Theme"
        >
          <Select
            name="theme"
            value={values.theme}
            options={themeOptions}
            onChange={handleChange}
            onBlur={handleBlur}
            disabled={isSubmitting}
          />
        </FormGroup>
      </div>
      
      <div className="form-section">
        <h3>Notifications</h3>
        
        <div className="notification-channels">
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="emailNotifications"
              name="emailNotifications"
              checked={values.emailNotifications}
              onChange={handleCheckboxChange}
              disabled={isSubmitting}
            />
            <label htmlFor="emailNotifications">Email notifications</label>
          </div>
          
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="smsNotifications"
              name="smsNotifications"
              checked={values.smsNotifications}
              onChange={handleCheckboxChange}
              disabled={isSubmitting}
            />
            <label htmlFor="smsNotifications">SMS notifications</label>
          </div>
          
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="inAppNotifications"
              name="inAppNotifications"
              checked={values.inAppNotifications}
              onChange={handleCheckboxChange}
              disabled={isSubmitting}
            />
            <label htmlFor="inAppNotifications">In-app notifications</label>
          </div>
        </div>
        
        <div className="notification-types">
          <h4>Notify me about:</h4>
          
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="notifyOnPriceChanges"
              name="notifyOnPriceChanges"
              checked={values.notifyOnPriceChanges}
              onChange={handleCheckboxChange}
              disabled={isSubmitting}
            />
            <label htmlFor="notifyOnPriceChanges">Significant price changes (>5%)</label>
          </div>
          
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="notifyOnDataSourceUpdates"
              name="notifyOnDataSourceUpdates"
              checked={values.notifyOnDataSourceUpdates}
              onChange={handleCheckboxChange}
              disabled={isSubmitting}
            />
            <label htmlFor="notifyOnDataSourceUpdates">Data source updates</label>
          </div>
          
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="notifyOnSystemMaintenance"
              name="notifyOnSystemMaintenance"
              checked={values.notifyOnSystemMaintenance}
              onChange={handleCheckboxChange}
              disabled={isSubmitting}
            />
            <label htmlFor="notifyOnSystemMaintenance">System maintenance</label>
          </div>
        </div>
      </div>
      
      <div className="form-actions">
        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting}
          isLoading={isSubmitting}
        >
          Save Changes
        </Button>
        
        <Button
          type="button"
          variant="outline-secondary"
          onClick={handleCancel}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
      </div>
    </form>
  );
};

export default UserProfileForm;