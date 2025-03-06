import React from 'react'; // v18.2.0
import { renderWithAuth, screen, waitFor, fireEvent, createMockUser } from '../../utils/test-utils';
import SettingsPage from './SettingsPage';
import { UserRole } from '../../types/user.types';
import { Permission } from '../../types/auth.types';
import userEvent from '@testing-library/user-event'; // ^14.4.3

/**
 * Test suite for the SettingsPage component
 */
describe('SettingsPage', () => {
  /**
   * Tests that the SettingsPage renders correctly
   */
  test('renders the settings page with tabs', async () => {
    // Create a mock user with standard permissions
    const mockUser = createMockUser();

    // Render the SettingsPage component with authentication context
    renderWithAuth(<SettingsPage />, { user: mockUser });

    // Verify that the page title is displayed
    expect(screen.getByText('Settings')).toBeInTheDocument();

    // Verify that the tabs are rendered
    expect(screen.getByRole('tablist')).toBeInTheDocument();

    // Verify that the User Preferences tab is active by default
    expect(screen.getByRole('tab', { name: 'User Preferences' })).toHaveClass('active');
  });

  /**
   * Tests tab switching functionality
   */
  test('switches between tabs when clicked', async () => {
    // Create a mock user with standard permissions
    const mockUser = createMockUser();

    // Render the SettingsPage component with authentication context
    renderWithAuth(<SettingsPage />, { user: mockUser });

    // Verify that the User Preferences tab is active by default
    expect(screen.getByRole('tab', { name: 'User Preferences' })).toHaveClass('active');

    // Click on the Notifications tab
    await userEvent.click(screen.getByRole('tab', { name: 'Notifications' }));

    // Verify that the Notifications tab becomes active
    expect(screen.getByRole('tab', { name: 'Notifications' })).toHaveClass('active');

    // Verify that the Notifications content is displayed
    expect(screen.getByText('Notification Channels')).toBeInTheDocument();
  });

  /**
   * Tests that system settings are visible to admin users
   */
  test('shows system settings tab for admin users', async () => {
    // Create a mock admin user with CONFIGURE_SYSTEM permission
    const mockAdminUser = createMockUser({ role: UserRole.ADMIN, permissions: [Permission.CONFIGURE_SYSTEM] });

    // Render the SettingsPage component with authentication context
    renderWithAuth(<SettingsPage />, { user: mockAdminUser });

    // Verify that the System Settings tab is visible
    expect(screen.getByRole('tab', { name: 'System Settings' })).toBeVisible();

    // Click on the System Settings tab
    await userEvent.click(screen.getByRole('tab', { name: 'System Settings' }));

    // Verify that the System Settings content is displayed
    expect(screen.getByText('Data Management')).toBeInTheDocument();
  });

  /**
   * Tests that system settings are hidden from non-admin users
   */
  test('hides system settings tab for non-admin users', async () => {
    // Create a mock analyst user without CONFIGURE_SYSTEM permission
    const mockAnalystUser = createMockUser({ role: UserRole.ANALYST, permissions: [] });

    // Render the SettingsPage component with authentication context
    renderWithAuth(<SettingsPage />, { user: mockAnalystUser });

    // Verify that the System Settings tab is not visible
    expect(() => screen.getByRole('tab', { name: 'System Settings' })).toThrow();
  });
  
  /**
   * Tests that user preferences component renders correctly
   */
  test('renders user preferences component', async () => {
    // Create a mock user with standard permissions
    const mockUser = createMockUser();

    // Render the SettingsPage component with authentication context
    renderWithAuth(<SettingsPage />, { user: mockUser });

    // Verify that the User Preferences component is rendered
    expect(screen.getByText('Display Name')).toBeInTheDocument();

    // Verify that key user preference fields are displayed (display name, email, theme, etc.)
    expect(screen.getByLabelText('Display Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByText('Default Currency')).toBeInTheDocument();
    expect(screen.getByText('Date Format')).toBeInTheDocument();
    expect(screen.getByText('Theme')).toBeInTheDocument();
  });

  /**
   * Tests that notification settings component renders correctly
   */
  test('renders notification settings component', async () => {
    // Create a mock user with standard permissions
    const mockUser = createMockUser();

    // Render the SettingsPage component with authentication context
    renderWithAuth(<SettingsPage />, { user: mockUser });

    // Click on the Notifications tab
    await userEvent.click(screen.getByRole('tab', { name: 'Notifications' }));

    // Verify that the Notification Settings component is rendered
    expect(screen.getByText('Notification Channels')).toBeInTheDocument();

    // Verify that key notification settings are displayed (email notifications, SMS notifications, etc.)
    expect(screen.getByLabelText('Email notifications')).toBeInTheDocument();
    expect(screen.getByLabelText('SMS notifications')).toBeInTheDocument();
    expect(screen.getByLabelText('In-app notifications')).toBeInTheDocument();
    expect(screen.getByText('Notify me about:')).toBeInTheDocument();
    expect(screen.getByLabelText('Significant price change threshold (%)')).toBeInTheDocument();
  });
});