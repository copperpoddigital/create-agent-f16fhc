import React, { useState } from 'react';
import FormGroup from '../../common/FormGroup';
import Input from '../../common/Input';
import Button from '../../common/Button';
import useForm from '../../../hooks/useForm';
import useAuth from '../../../hooks/useAuth';
import useAlert from '../../../hooks/useAlert';
import { validatePassword, validatePasswordMatch } from '../../../utils/validation-utils';

interface PasswordChangeFormProps {
  onSuccess?: () => void;
}

const PasswordChangeForm: React.FC<PasswordChangeFormProps> = ({ onSuccess }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const { changePassword } = useAuth();
  const { showSuccess, showError } = useAlert();
  
  const { values, errors, touched, handleChange, handleBlur, handleSubmit } = useForm({
    initialValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    },
    validate: (values) => {
      const errors: Record<string, string> = {};
      
      // Validate current password (required)
      if (!values.currentPassword) {
        errors.currentPassword = 'Current password is required';
      }
      
      // Validate new password
      const passwordError = validatePassword(values.newPassword);
      if (passwordError) {
        errors.newPassword = passwordError;
      }
      
      // Validate password confirmation
      const passwordMatchError = validatePasswordMatch(values.newPassword, values.confirmPassword);
      if (passwordMatchError) {
        errors.confirmPassword = passwordMatchError;
      }
      
      return errors;
    },
    onSubmit: async (values) => {
      try {
        setIsSubmitting(true);
        
        // Call the changePassword function from the auth hook
        await changePassword(
          values.currentPassword,
          values.newPassword,
          values.confirmPassword
        );
        
        // Show success message
        showSuccess('Password changed successfully');
        
        // Reset form or call onSuccess callback
        if (onSuccess) {
          onSuccess();
        }
      } catch (error) {
        // Show error message
        showError(error instanceof Error ? error.message : 'Failed to change password');
      } finally {
        setIsSubmitting(false);
      }
    }
  });
  
  // Toggle password visibility
  const toggleShowPassword = () => {
    setShowPassword(prevState => !prevState);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <FormGroup
        label="Current Password"
        required
        isInvalid={touched.currentPassword && Boolean(errors.currentPassword)}
        validationMessage={touched.currentPassword ? errors.currentPassword : undefined}
      >
        <Input
          type={showPassword ? 'text' : 'password'}
          name="currentPassword"
          value={values.currentPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isSubmitting}
        />
      </FormGroup>
      
      <FormGroup
        label="New Password"
        required
        isInvalid={touched.newPassword && Boolean(errors.newPassword)}
        validationMessage={touched.newPassword ? errors.newPassword : undefined}
        helpText="Password must be at least 12 characters and include uppercase, lowercase, number, and special character"
      >
        <Input
          type={showPassword ? 'text' : 'password'}
          name="newPassword"
          value={values.newPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isSubmitting}
        />
      </FormGroup>
      
      <FormGroup
        label="Confirm New Password"
        required
        isInvalid={touched.confirmPassword && Boolean(errors.confirmPassword)}
        validationMessage={touched.confirmPassword ? errors.confirmPassword : undefined}
      >
        <Input
          type={showPassword ? 'text' : 'password'}
          name="confirmPassword"
          value={values.confirmPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isSubmitting}
        />
      </FormGroup>
      
      <div className="form-check mb-3">
        <input
          type="checkbox"
          id="showPassword"
          className="form-check-input"
          checked={showPassword}
          onChange={toggleShowPassword}
          disabled={isSubmitting}
        />
        <label htmlFor="showPassword" className="form-check-label">
          Show Password
        </label>
      </div>
      
      <div className="d-flex justify-content-end">
        <Button
          type="submit"
          variant="primary"
          isLoading={isSubmitting}
          disabled={isSubmitting}
        >
          Change Password
        </Button>
      </div>
    </form>
  );
};

export default PasswordChangeForm;