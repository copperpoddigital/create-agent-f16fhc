import React from 'react';
import { vi } from 'vitest';
import PasswordChangeForm from './PasswordChangeForm';
import { renderWithAuth, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';

// Mock hooks
vi.mock('../../../hooks/useAuth', () => ({
  default: vi.fn().mockReturnValue({
    changePassword: vi.fn().mockResolvedValue(undefined)
  })
}));

vi.mock('../../../hooks/useAlert', () => ({
  default: vi.fn().mockReturnValue({
    showSuccess: vi.fn(),
    showError: vi.fn()
  })
}));

describe('PasswordChangeForm component', () => {
  test('renders the form correctly', () => {
    renderWithAuth(<PasswordChangeForm />);
    
    // Check that all form elements are present
    expect(screen.getByLabelText(/Current Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/New Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Confirm New Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Change Password/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Show Password/i)).toBeInTheDocument();
    
    // Verify help text
    expect(screen.getByText(/Password must be at least 12 characters and include uppercase, lowercase, number, and special character/i)).toBeInTheDocument();
  });

  test('toggles password visibility when checkbox is clicked', async () => {
    renderWithAuth(<PasswordChangeForm />);
    
    const currentPasswordInput = screen.getByLabelText(/Current Password/i);
    const newPasswordInput = screen.getByLabelText(/New Password/i);
    const confirmPasswordInput = screen.getByLabelText(/Confirm New Password/i);
    
    // Initially password type
    expect(currentPasswordInput).toHaveAttribute('type', 'password');
    expect(newPasswordInput).toHaveAttribute('type', 'password');
    expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    
    // Toggle visibility
    const showPasswordCheckbox = screen.getByLabelText(/Show Password/i);
    await userEvent.click(showPasswordCheckbox);
    
    // Now text type
    expect(currentPasswordInput).toHaveAttribute('type', 'text');
    expect(newPasswordInput).toHaveAttribute('type', 'text');
    expect(confirmPasswordInput).toHaveAttribute('type', 'text');
    
    // Toggle back
    await userEvent.click(showPasswordCheckbox);
    
    // Back to password type
    expect(currentPasswordInput).toHaveAttribute('type', 'password');
    expect(newPasswordInput).toHaveAttribute('type', 'password');
    expect(confirmPasswordInput).toHaveAttribute('type', 'password');
  });

  test('validates current password is required', async () => {
    renderWithAuth(<PasswordChangeForm />);
    
    // Focus and blur empty field
    const currentPasswordInput = screen.getByLabelText(/Current Password/i);
    await userEvent.click(currentPasswordInput);
    await userEvent.tab(); // Move focus away
    
    // Expect error message
    expect(await screen.findByText(/Current password is required/i)).toBeInTheDocument();
  });

  test('validates new password complexity requirements', async () => {
    renderWithAuth(<PasswordChangeForm />);
    
    // Enter simple password
    const newPasswordInput = screen.getByLabelText(/New Password/i);
    await userEvent.type(newPasswordInput, 'simple');
    await userEvent.tab(); // Move focus away
    
    // Expect error about complexity
    expect(await screen.findByText(/Password must be at least 12 characters/i)).toBeInTheDocument();
    
    // Enter valid complex password
    await userEvent.clear(newPasswordInput);
    await userEvent.type(newPasswordInput, 'ComplexP@ssw0rd123');
    await userEvent.tab(); // Move focus away
    
    // Error should be gone
    await waitFor(() => {
      expect(screen.queryByText(/Password must be at least 12 characters/i)).not.toBeInTheDocument();
    });
  });

  test('validates password confirmation matches new password', async () => {
    renderWithAuth(<PasswordChangeForm />);
    
    // Enter new password
    const newPasswordInput = screen.getByLabelText(/New Password/i);
    await userEvent.type(newPasswordInput, 'ComplexP@ssw0rd123');
    
    // Enter different confirmation
    const confirmPasswordInput = screen.getByLabelText(/Confirm New Password/i);
    await userEvent.type(confirmPasswordInput, 'DifferentP@ssw0rd');
    await userEvent.tab(); // Move focus away
    
    // Expect mismatch error
    expect(await screen.findByText(/Passwords do not match/i)).toBeInTheDocument();
    
    // Enter matching confirmation
    await userEvent.clear(confirmPasswordInput);
    await userEvent.type(confirmPasswordInput, 'ComplexP@ssw0rd123');
    await userEvent.tab(); // Move focus away
    
    // Error should be gone
    await waitFor(() => {
      expect(screen.queryByText(/Passwords do not match/i)).not.toBeInTheDocument();
    });
  });

  test('submits the form with valid data', async () => {
    // Set up mocks
    const changePasswordMock = vi.fn().mockResolvedValue(undefined);
    const showSuccessMock = vi.fn();
    const onSuccessMock = vi.fn();
    
    // Override mocks
    vi.mocked(require('../../../hooks/useAuth').default).mockReturnValue({
      changePassword: changePasswordMock
    });
    
    vi.mocked(require('../../../hooks/useAlert').default).mockReturnValue({
      showSuccess: showSuccessMock,
      showError: vi.fn()
    });
    
    renderWithAuth(<PasswordChangeForm onSuccess={onSuccessMock} />);
    
    // Fill form with valid data
    await userEvent.type(screen.getByLabelText(/Current Password/i), 'CurrentPassword123!');
    await userEvent.type(screen.getByLabelText(/New Password/i), 'NewComplexP@ssw0rd123');
    await userEvent.type(screen.getByLabelText(/Confirm New Password/i), 'NewComplexP@ssw0rd123');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /Change Password/i });
    await userEvent.click(submitButton);
    
    // Verify correct calls
    await waitFor(() => {
      expect(changePasswordMock).toHaveBeenCalledWith(
        'CurrentPassword123!',
        'NewComplexP@ssw0rd123',
        'NewComplexP@ssw0rd123'
      );
      expect(showSuccessMock).toHaveBeenCalledWith('Password changed successfully');
      expect(onSuccessMock).toHaveBeenCalled();
    });
  });

  test('shows error message when password change fails', async () => {
    // Set up mocks
    const errorMessage = 'Invalid current password';
    const changePasswordMock = vi.fn().mockRejectedValue(new Error(errorMessage));
    const showErrorMock = vi.fn();
    
    // Override mocks
    vi.mocked(require('../../../hooks/useAuth').default).mockReturnValue({
      changePassword: changePasswordMock
    });
    
    vi.mocked(require('../../../hooks/useAlert').default).mockReturnValue({
      showSuccess: vi.fn(),
      showError: showErrorMock
    });
    
    renderWithAuth(<PasswordChangeForm />);
    
    // Fill form with valid data
    await userEvent.type(screen.getByLabelText(/Current Password/i), 'CurrentPassword123!');
    await userEvent.type(screen.getByLabelText(/New Password/i), 'NewComplexP@ssw0rd123');
    await userEvent.type(screen.getByLabelText(/Confirm New Password/i), 'NewComplexP@ssw0rd123');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /Change Password/i });
    await userEvent.click(submitButton);
    
    // Verify error handling
    await waitFor(() => {
      expect(changePasswordMock).toHaveBeenCalled();
      expect(showErrorMock).toHaveBeenCalledWith(errorMessage);
    });
  });

  test('disables form fields during submission', async () => {
    // Set up delayed promise
    let resolveChangePassword: (value: unknown) => void;
    const changePasswordPromise = new Promise((resolve) => {
      resolveChangePassword = resolve;
    });
    
    const changePasswordMock = vi.fn().mockImplementation(() => changePasswordPromise);
    
    vi.mocked(require('../../../hooks/useAuth').default).mockReturnValue({
      changePassword: changePasswordMock
    });
    
    renderWithAuth(<PasswordChangeForm />);
    
    // Fill form with valid data
    await userEvent.type(screen.getByLabelText(/Current Password/i), 'CurrentPassword123!');
    await userEvent.type(screen.getByLabelText(/New Password/i), 'NewComplexP@ssw0rd123');
    await userEvent.type(screen.getByLabelText(/Confirm New Password/i), 'NewComplexP@ssw0rd123');
    
    // Submit form
    const submitButton = screen.getByRole('button', { name: /Change Password/i });
    await userEvent.click(submitButton);
    
    // Verify fields are disabled
    expect(screen.getByLabelText(/Current Password/i)).toBeDisabled();
    expect(screen.getByLabelText(/New Password/i)).toBeDisabled();
    expect(screen.getByLabelText(/Confirm New Password/i)).toBeDisabled();
    expect(submitButton).toBeDisabled();
    
    // Resolve promise to complete submission
    if (resolveChangePassword) {
      resolveChangePassword(undefined);
    }
    
    // Verify fields are enabled again
    await waitFor(() => {
      expect(screen.getByLabelText(/Current Password/i)).not.toBeDisabled();
      expect(screen.getByLabelText(/New Password/i)).not.toBeDisabled();
      expect(screen.getByLabelText(/Confirm New Password/i)).not.toBeDisabled();
      expect(submitButton).not.toBeDisabled();
    });
  });
});