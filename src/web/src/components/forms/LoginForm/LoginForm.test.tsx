import React from 'react';
import { vi } from 'vitest';
import LoginForm from './LoginForm';
import { renderWithAuth, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';

// Setup function to render the LoginForm component with mocked auth context
const setup = (options = {}) => {
  const mockLogin = vi.fn(options.loginImplementation || (() => Promise.resolve()));
  const mockOnSuccess = vi.fn();
  
  const rendered = renderWithAuth(
    <LoginForm onSuccess={mockOnSuccess} {...options.props} />,
    {
      state: {
        isAuthenticated: false,
        isLoading: options.isLoading || false,
        error: options.authError || null,
        user: null,
        accessToken: null,
        refreshToken: null,
        expiresAt: null
      },
      login: mockLogin,
      logout: vi.fn(),
      refreshSession: vi.fn(),
      changePassword: vi.fn(),
      resetPassword: vi.fn(),
      confirmPasswordReset: vi.fn()
    }
  );
  
  return {
    ...rendered,
    mockLogin,
    mockOnSuccess
  };
};

describe('LoginForm', () => {
  test('renders the login form correctly', () => {
    setup();
    
    expect(screen.getByRole('heading', { name: /Login to your account/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Remember me/i)).toBeInTheDocument();
    expect(screen.getByText(/Forgot Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument();
  });
  
  test('shows validation errors for empty fields on submit', async () => {
    setup();
    
    // Submit the form without entering any data
    await userEvent.click(screen.getByRole('button', { name: /Login/i }));
    
    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeInTheDocument();
      expect(screen.getByText('Password is required')).toBeInTheDocument();
    });
  });
  
  test('shows validation error for invalid username format', async () => {
    setup();
    
    // Focus on the username field and then blur it without typing
    const usernameInput = screen.getByLabelText(/Username/i);
    await userEvent.click(usernameInput);
    await userEvent.tab(); // Tab to next field to trigger blur
    
    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeInTheDocument();
    });
  });
  
  test('shows validation error for invalid password format', async () => {
    setup();
    
    // Focus on the password field and then blur it without typing
    const passwordInput = screen.getByLabelText(/Password/i);
    await userEvent.click(passwordInput);
    await userEvent.tab(); // Tab to next field to trigger blur
    
    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText('Password is required')).toBeInTheDocument();
    });
  });
  
  test('toggles password visibility when clicking the eye icon', async () => {
    setup();
    
    // Check initial type is password (hidden)
    const passwordInput = screen.getByLabelText(/Password/i);
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click the "Show password" button
    const showPasswordButton = screen.getByRole('button', { 
      name: /Show password/i,
    });
    await userEvent.click(showPasswordButton);
    
    // Check type is now text (visible)
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // The button label is now "Hide password"
    const hidePasswordButton = screen.getByRole('button', { 
      name: /Hide password/i,
    });
    await userEvent.click(hidePasswordButton);
    
    // Check type is password again
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
  
  test('calls login function with correct values on valid submission', async () => {
    const { mockLogin } = setup();
    
    // Fill in form with valid data
    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    const rememberMeCheckbox = screen.getByLabelText(/Remember me/i);
    
    await userEvent.type(usernameInput, 'validuser');
    await userEvent.type(passwordInput, 'ValidPassword123!');
    await userEvent.click(rememberMeCheckbox); // Check the remember me checkbox
    
    // Submit the form
    await userEvent.click(screen.getByRole('button', { name: /Login/i }));
    
    // Check login function was called with correct values
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('validuser', 'ValidPassword123!', true);
    });
  });
  
  test('shows loading state during form submission', async () => {
    // Create a promise that we won't resolve within the test
    const loginPromise = new Promise(resolve => {});
    
    setup({
      isLoading: true,
      loginImplementation: () => loginPromise
    });
    
    // Fill in form with valid data
    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    
    await userEvent.type(usernameInput, 'validuser');
    await userEvent.type(passwordInput, 'ValidPassword123!');
    
    // Submit the form
    await userEvent.click(screen.getByRole('button', { name: /Login/i }));
    
    // Check loading state
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Login/i })).toHaveAttribute('aria-busy', 'true');
      expect(usernameInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
    });
  });
  
  test('displays error message when login fails', async () => {
    const errorMessage = 'Invalid credentials. Please try again.';
    setup({ authError: errorMessage });
    
    // Check for error message
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent(errorMessage);
  });
  
  test('calls onSuccess callback after successful login', async () => {
    const { mockLogin, mockOnSuccess } = setup();
    
    // Make login resolve successfully
    mockLogin.mockResolvedValueOnce(undefined);
    
    // Fill in form with valid data
    const usernameInput = screen.getByLabelText(/Username/i);
    const passwordInput = screen.getByLabelText(/Password/i);
    
    await userEvent.type(usernameInput, 'validuser');
    await userEvent.type(passwordInput, 'ValidPassword123!');
    
    // Submit the form
    await userEvent.click(screen.getByRole('button', { name: /Login/i }));
    
    // Verify onSuccess was called
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });
});