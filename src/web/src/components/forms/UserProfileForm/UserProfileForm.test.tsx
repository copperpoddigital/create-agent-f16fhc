import React from 'react';
import UserProfileForm from './UserProfileForm';
import { renderWithAuth, screen, waitFor, fireEvent, userEvent, createMockUser } from '../../../utils/test-utils';
import { Theme, DateFormat } from '../../../types/user.types';
import { updateCurrentUserProfile, updateCurrentUserPreferences } from '../../../api/user-api';

// Mock the API functions
jest.mock('../../../api/user-api', () => ({
  updateCurrentUserProfile: jest.fn().mockResolvedValue({ data: {}, success: true }),
  updateCurrentUserPreferences: jest.fn().mockResolvedValue({ data: {}, success: true })
}));

// Mock the useAlert hook
jest.mock('../../../hooks/useAlert', () => ({
  __esModule: true,
  default: () => ({
    showSuccess: jest.fn(),
    showError: jest.fn()
  })
}));

describe('UserProfileForm', () => {
  let mockUser;

  beforeEach(() => {
    mockUser = createMockUser();
    // Reset mocks before each test
    jest.clearAllMocks();
  });

  test('renders correctly with user data', () => {
    renderWithAuth(<UserProfileForm />, { state: { user: mockUser } });

    // Check profile information fields
    expect(screen.getByLabelText(/First Name/i)).toHaveValue(mockUser.firstName);
    expect(screen.getByLabelText(/Last Name/i)).toHaveValue(mockUser.lastName);
    expect(screen.getByLabelText(/Email/i)).toHaveValue(mockUser.email);

    // Check preference fields
    expect(screen.getByLabelText(/Default Currency/i)).toHaveValue(mockUser.defaultCurrency);
    expect(screen.getByLabelText(/Date Format/i)).toHaveValue(mockUser.dateFormat);
    expect(screen.getByLabelText(/Theme/i)).toHaveValue(mockUser.theme);

    // Check notification checkboxes
    expect(screen.getByLabelText(/Email notifications/i)).toBeChecked();
    expect(screen.getByLabelText(/SMS notifications/i)).not.toBeChecked();
    expect(screen.getByLabelText(/In-app notifications/i)).toBeChecked();
    expect(screen.getByLabelText(/Significant price changes/i)).toBeChecked();
    expect(screen.getByLabelText(/Data source updates/i)).toBeChecked();
    expect(screen.getByLabelText(/System maintenance/i)).not.toBeChecked();
  });

  test('validates required fields', async () => {
    renderWithAuth(<UserProfileForm />, { state: { user: mockUser } });

    // Clear first name and submit
    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: '' } });
    fireEvent.blur(screen.getByLabelText(/First Name/i));
    fireEvent.click(screen.getByRole('button', { name: /Save Changes/i }));

    await waitFor(() => {
      expect(screen.getByText(/This field is required/i)).toBeInTheDocument();
    });

    // Clear last name and submit
    fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: '' } });
    fireEvent.blur(screen.getByLabelText(/Last Name/i));
    fireEvent.click(screen.getByRole('button', { name: /Save Changes/i }));

    await waitFor(() => {
      expect(screen.getAllByText(/This field is required/i).length).toBeGreaterThan(1);
    });

    // Clear email and submit
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: '' } });
    fireEvent.blur(screen.getByLabelText(/Email/i));
    fireEvent.click(screen.getByRole('button', { name: /Save Changes/i }));

    await waitFor(() => {
      expect(screen.getAllByText(/This field is required/i).length).toBeGreaterThan(2);
    });
  });

  test('validates email format', async () => {
    renderWithAuth(<UserProfileForm />, { state: { user: mockUser } });

    // Enter invalid email format
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'invalid-email' } });
    fireEvent.blur(screen.getByLabelText(/Email/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  test('submits form successfully', async () => {
    const onSuccess = jest.fn();
    renderWithAuth(<UserProfileForm onSuccess={onSuccess} />, { state: { user: mockUser } });

    // Update form fields
    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'New Name' } });
    fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'Updated Last' } });
    
    // Change dropdown value
    fireEvent.change(screen.getByLabelText(/Default Currency/i), { target: { value: 'EUR' } });
    
    // Toggle checkboxes
    fireEvent.click(screen.getByLabelText(/System maintenance/i));
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Save Changes/i }));

    await waitFor(() => {
      // Check that API functions were called with correct data
      expect(updateCurrentUserProfile).toHaveBeenCalledWith({
        firstName: 'New Name',
        lastName: 'Updated Last',
        email: mockUser.email
      });
      
      expect(updateCurrentUserPreferences).toHaveBeenCalledWith(expect.objectContaining({
        defaultCurrency: 'EUR',
        theme: mockUser.theme,
        dateFormat: mockUser.dateFormat,
        notifyOnSystemMaintenance: true
      }));
      
      // Check that success callback was called
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  test('handles API errors correctly', async () => {
    // Mock API to reject with error
    updateCurrentUserProfile.mockRejectedValueOnce(new Error('Failed to update profile'));

    renderWithAuth(<UserProfileForm />, { state: { user: mockUser } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /Save Changes/i }));

    await waitFor(() => {
      // Form should no longer be in submitting state
      expect(screen.getByRole('button', { name: /Save Changes/i })).not.toBeDisabled();
    });
  });

  test('calls onCancel when cancel button is clicked', () => {
    const onCancel = jest.fn();
    renderWithAuth(<UserProfileForm onCancel={onCancel} />, { state: { user: mockUser } });

    // Click cancel button
    fireEvent.click(screen.getByRole('button', { name: /Cancel/i }));

    // Check that onCancel was called
    expect(onCancel).toHaveBeenCalled();
  });
});