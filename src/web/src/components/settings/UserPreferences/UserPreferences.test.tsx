# src/web/src/components/settings/UserPreferences/UserPreferences.test.tsx
```typescript
import React from 'react'; // ^18.2.0
import { render, act } from '@testing-library/react'; // ^14.0.0
import { vi } from 'vitest'; // ^0.34.0
import UserPreferences from './UserPreferences';
import {
  renderWithAuth,
  renderWithTheme,
  screen,
  waitFor,
  fireEvent,
  userEvent,
  createMockUser,
} from '../../../utils/test-utils';
import { Theme, DateFormat } from '../../../types/user.types';
import { updateCurrentUserPreferences } from '../../../api/user-api';

// Mock the updateCurrentUserPreferences API function
vi.mock('../../../api/user-api', () => ({
  updateCurrentUserPreferences: vi.fn(),
}));

describe('UserPreferences component', () => {
  // Setup function that runs before each test
  let mockUser = createMockUser();

  beforeEach(() => {
    // Mock the updateCurrentUserPreferences API function
    (updateCurrentUserPreferences as vi.Mock).mockResolvedValue({ success: true, data: mockUser });

    // Create a mock user with default preferences
    mockUser = createMockUser();
  });

  // Cleanup function that runs after each test
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should render the component with user preferences', async () => {
    // Render the UserPreferences component with auth context
    renderWithAuth(<UserPreferences />, { state: { user: mockUser } });

    // Verify that form fields are populated with user preferences
    expect(screen.getByDisplayValue(mockUser.firstName || '')).toBeInTheDocument();
    expect(screen.getByDisplayValue(mockUser.email || '')).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: /default currency/i })).toHaveValue(mockUser.defaultCurrency || '');
    expect(screen.getByRole('combobox', { name: /date format/i })).toHaveValue(mockUser.dateFormat || '');
    expect(screen.getByRole('radio', { name: /light/i })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: /email notifications/i })).toBeChecked();

    // Check that display name, email, and other fields are rendered correctly
    expect(screen.getByText(`${mockUser.firstName} ${mockUser.lastName}`)).toBeInTheDocument();
  });

  it('should handle form submission correctly', async () => {
    // Render the UserPreferences component with auth context
    renderWithAuth(<UserPreferences />, { state: { user: mockUser } });

    // Fill out the form with updated preferences
    fireEvent.change(screen.getByRole('combobox', { name: /default currency/i }), {
      target: { value: 'EUR' },
    });
    fireEvent.click(screen.getByRole('checkbox', { name: /sms notifications/i }));

    // Submit the form
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /save/i }));
    });

    // Verify that updateCurrentUserPreferences was called with correct data
    expect(updateCurrentUserPreferences).toHaveBeenCalledTimes(1);
    expect(updateCurrentUserPreferences).toHaveBeenCalledWith(
      expect.objectContaining({
        defaultCurrency: 'EUR',
        smsNotifications: true,
      })
    );

    // Check that success message is displayed
    await waitFor(() => {
      expect(screen.getByText(/preferences updated successfully!/i)).toBeInTheDocument();
    });
  });

  it('should handle theme change immediately', async () => {
    // Render the UserPreferences component with auth and theme context
    renderWithTheme(<UserPreferences />);

    // Change the theme selection
    fireEvent.click(screen.getByLabelText(/dark/i));

    // Verify that theme context is updated immediately
    expect(document.body.classList.contains('dark-theme')).toBe(true);

    // Submit the form
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /save/i }));
    });

    // Verify that updateCurrentUserPreferences was called with the new theme
    expect(updateCurrentUserPreferences).toHaveBeenCalledTimes(1);
    expect(updateCurrentUserPreferences).toHaveBeenCalledWith(
      expect.objectContaining({
        theme: Theme.DARK,
      })
    );
  });

  it('should display error message on submission failure', async () => {
    // Mock updateCurrentUserPreferences to reject with an error
    (updateCurrentUserPreferences as vi.Mock).mockRejectedValue(new Error('API error'));

    // Render the UserPreferences component with auth context
    renderWithAuth(<UserPreferences />, { state: { user: mockUser } });

    // Submit the form
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /save/i }));
    });

    // Verify that error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/an unexpected error occurred./i)).toBeInTheDocument();
    });

    // Check that form remains in editable state
    expect(screen.getByRole('button', { name: /save/i })).toBeEnabled();
  });

  it('should validate form fields', async () => {
    // Render the UserPreferences component with auth context
    renderWithAuth(<UserPreferences />, { state: { user: mockUser } });

    // Clear required fields
    fireEvent.change(screen.getByRole('combobox', { name: /default currency/i }), {
      target: { value: '' },
    });

    // Submit the form
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /save/i }));
    });

    // Verify that validation errors are displayed
    await waitFor(() => {
      expect(screen.getByText(/this field is required/i)).toBeInTheDocument();
    });

    // Verify that updateCurrentUserPreferences was not called
    expect(updateCurrentUserPreferences).not.toHaveBeenCalled();
  });
});