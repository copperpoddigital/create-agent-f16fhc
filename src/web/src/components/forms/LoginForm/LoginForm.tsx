import React, { useState } from 'react';
import { useForm } from '../../../hooks/useForm';
import { useAuth } from '../../../hooks/useAuth';
import Input from '../../common/Input';
import Button from '../../common/Button';
import FormGroup from '../../common/FormGroup';
import { LoginCredentials } from '../../../types/auth.types';

interface LoginFormProps {
  onSuccess?: () => void;
  redirectPath?: string;
}

/**
 * A form component that handles user authentication in the Freight Price Movement Agent web application.
 * Implements the OAuth 2.0/JWT-based authentication flow as specified in the Technical Specifications.
 */
const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, redirectPath }) => {
  const auth = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  // Initialize form with validation and submission handling
  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
  } = useForm({
    initialValues: {
      username: '',
      password: '',
      rememberMe: false,
    },
    validate: (values) => {
      const errors: Record<string, string> = {};
      
      // Validate username
      if (!values.username) {
        errors.username = 'Username is required';
      }
      
      // Validate password
      if (!values.password) {
        errors.password = 'Password is required';
      }
      
      return errors;
    },
    onSubmit: async (values) => {
      try {
        // Call the login function from auth context
        await auth.login(values.username, values.password, values.rememberMe);
        
        // Call onSuccess callback if provided
        if (onSuccess) {
          onSuccess();
        }
      } catch (error) {
        // Error handling is managed by auth context
        console.error('Login failed:', error);
      }
    },
  });

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <h2>Login to your account</h2>
      
      {/* Username field */}
      <FormGroup
        id="username"
        label="Username"
        required
        isInvalid={touched.username && !!errors.username}
        validationMessage={errors.username}
      >
        <Input
          id="username"
          name="username"
          type="text"
          value={values.username}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Enter your username"
          disabled={isSubmitting}
        />
      </FormGroup>
      
      {/* Password field with visibility toggle */}
      <FormGroup
        id="password"
        label="Password"
        required
        isInvalid={touched.password && !!errors.password}
        validationMessage={errors.password}
      >
        <Input
          id="password"
          name="password"
          type={showPassword ? 'text' : 'password'}
          value={values.password}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Enter your password"
          disabled={isSubmitting}
          rightIcon={
            <button
              type="button"
              onClick={togglePasswordVisibility}
              className="password-toggle"
              tabIndex={-1}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          }
        />
      </FormGroup>
      
      {/* Form options: Remember me and Forgot password */}
      <div className="form-options">
        <div className="remember-me">
          <Input
            id="rememberMe"
            name="rememberMe"
            type="checkbox"
            checked={values.rememberMe}
            onChange={handleChange}
          />
          <label htmlFor="rememberMe">Remember me</label>
        </div>
        
        <a href="/forgot-password" className="forgot-password">
          Forgot Password?
        </a>
      </div>
      
      {/* Display authentication errors */}
      {auth.state.error && (
        <div className="form-error" role="alert">
          {auth.state.error}
        </div>
      )}
      
      {/* Submit button */}
      <Button
        type="submit"
        variant="primary"
        fullWidth
        isLoading={isSubmitting || auth.state.isLoading}
        disabled={isSubmitting || auth.state.isLoading}
      >
        Login
      </Button>
    </form>
  );
};

export default LoginForm;