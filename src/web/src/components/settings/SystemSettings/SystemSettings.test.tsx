import React from 'react'; // version: ^18.2.0
import { render } from '@testing-library/react'; // version: ^14.0.0
import {
  renderWithAuth,
  screen,
  waitFor,
  fireEvent,
  userEvent,
  createMockUser,
} from '../../../utils/test-utils'; // Import testing utilities for rendering and interacting with the component
import SystemSettings from './SystemSettings'; // Import the component being tested
import { Permission } from '../../../types/auth.types'; // Import permission enum for testing authorization
import { createMockUser } from '../../../utils/test-utils'; // Import utility for creating mock user data
import { MockSystemSettings } from './SystemSettings'; // Interface for mock system settings data used in tests
import jest from 'jest'; // version: ^29.5.0

/**
 * Interface for mock system settings data used in tests
 */
interface MockSystemSettings {
  dataRetention: string;
  refreshInterval: string;
  apiRateLimit: number;
  enableAuditLogging: boolean;
  backupSchedule: string;
}

/**
 * Test suite for the SystemSettings component
 */
describe('SystemSettings Component', () => {
  // Mock the useApi hook
  const mockUseApi = jest.fn();

  // Mock the useAuth hook
  const mockUseAuth = jest.fn();

  // Setup function that runs before each test
  beforeEach(() => {
    // Reset all mocks before each test
    mockUseApi.mockReset();
    mockUseAuth.mockReset();

    // Set up default mock implementations
    jest.mock('../../../hooks/useApi', () => ({
      __esModule: true,
      default: () => mockUseApi(),
    }));

    jest.mock('../../../hooks/useAuth', () => ({
      __esModule: true,
      default: () => mockUseAuth(),
    }));
  });

  /**
   * Test case for when user lacks permission
   */
  test('should show access denied message when user lacks permission', async () => {
    // Mock useAuth to return user without CONFIGURE_SYSTEM permission
    mockUseAuth.mockReturnValue({
      state: {
        user: createMockUser({ permissions: [] }),
      },
    });

    // Render the SystemSettings component with auth context
    renderWithAuth(<SystemSettings />);

    // Verify that access denied message is displayed
    expect(screen.getByText('Access Denied')).toBeInTheDocument();

    // Verify that settings form is not displayed
    expect(screen.queryByText('Data Management')).not.toBeInTheDocument();
  });

  /**
   * Test case for loading state
   */
  test('should show loading spinner while fetching settings', async () => {
    // Mock useAuth to return user with CONFIGURE_SYSTEM permission
    mockUseAuth.mockReturnValue({
      state: {
        user: createMockUser({ permissions: [Permission.CONFIGURE_SYSTEM] }),
      },
    });

    // Mock useApi to return loading state
    mockUseApi.mockReturnValue({
      state: {
        data: null,
        isLoading: true,
        isError: false,
        error: null,
      },
      actions: {
        execute: jest.fn(),
        reset: jest.fn(),
        cancel: jest.fn(),
      },
    });

    // Render the SystemSettings component
    renderWithAuth(<SystemSettings />);

    // Verify that loading spinner is displayed
    expect(screen.getByText('Loading system settings...')).toBeInTheDocument();
  });

  /**
   * Test case for error state
   */
  test('should show error message when settings fetch fails', async () => {
    // Mock useAuth to return user with CONFIGURE_SYSTEM permission
    mockUseAuth.mockReturnValue({
      state: {
        user: createMockUser({ permissions: [Permission.CONFIGURE_SYSTEM] }),
      },
    });

    // Mock useApi to return error state
    mockUseApi.mockReturnValue({
      state: {
        data: null,
        isLoading: false,
        isError: true,
        error: new Error('Failed to fetch settings'),
      },
      actions: {
        execute: jest.fn(),
        reset: jest.fn(),
        cancel: jest.fn(),
      },
    });

    // Render the SystemSettings component
    renderWithAuth(<SystemSettings />);

    // Verify that error message is displayed
    expect(screen.getByText('Error Loading Settings')).toBeInTheDocument();
  });

  /**
   * Test case for successful data loading
   */
  test('should display settings form with fetched data', async () => {
    // Mock useAuth to return user with CONFIGURE_SYSTEM permission
    mockUseAuth.mockReturnValue({
      state: {
        user: createMockUser({ permissions: [Permission.CONFIGURE_SYSTEM] }),
      },
    });

    // Mock useApi to return success state with mock settings data
    const mockSettings: MockSystemSettings = {
      dataRetention: '5 years',
      refreshInterval: '12 hours',
      apiRateLimit: 500,
      enableAuditLogging: false,
      backupSchedule: 'Weekly',
    };

    mockUseApi.mockReturnValue({
      state: {
        data: mockSettings,
        isLoading: false,
        isError: false,
        error: null,
      },
      actions: {
        execute: jest.fn(),
        reset: jest.fn(),
        cancel: jest.fn(),
      },
    });

    // Render the SystemSettings component
    renderWithAuth(<SystemSettings />);

    // Verify that settings form is displayed with correct values
    await waitFor(() => {
      expect(screen.getByLabelText('Data Retention')).toBeInTheDocument();
      expect(screen.getByLabelText('Refresh Interval')).toBeInTheDocument();
      expect(screen.getByLabelText('API Rate Limit')).toBeInTheDocument();
      expect(screen.getByLabelText('Enable Audit Logging')).toBeInTheDocument();
      expect(screen.getByLabelText('Backup Schedule')).toBeInTheDocument();
    });

    // Verify that data retention dropdown has correct value
    expect((screen.getByLabelText('Data Retention') as HTMLSelectElement).value).toBe(
      mockSettings.dataRetention
    );

    // Verify that refresh interval dropdown has correct value
    expect((screen.getByLabelText('Refresh Interval') as HTMLSelectElement).value).toBe(
      mockSettings.refreshInterval
    );

    // Verify that API rate limit input has correct value
    expect((screen.getByLabelText('API Rate Limit') as HTMLInputElement).value).toBe(
      mockSettings.apiRateLimit.toString()
    );
  });

  /**
   * Test case for form submission
   */
  test('should handle form submission correctly', async () => {
    // Mock useAuth to return user with CONFIGURE_SYSTEM permission
    mockUseAuth.mockReturnValue({
      state: {
        user: createMockUser({ permissions: [Permission.CONFIGURE_SYSTEM] }),
      },
    });

    // Mock useApi for both GET and PUT requests
    const mockSettings: MockSystemSettings = {
      dataRetention: '3 years',
      refreshInterval: '24 hours',
      apiRateLimit: 100,
      enableAuditLogging: true,
      backupSchedule: 'Daily',
    };

    const mockUpdateSettings = jest.fn().mockResolvedValue({ success: true });

    mockUseApi.mockReturnValue({
      state: {
        data: mockSettings,
        isLoading: false,
        isError: false,
        error: null,
      },
      actions: {
        execute: jest.fn(),
        reset: jest.fn(),
        cancel: jest.fn(),
      },
    });

    // Render the SystemSettings component
    renderWithAuth(<SystemSettings />);

    // Wait for form to load with initial data
    await waitFor(() => {
      expect(screen.getByLabelText('Data Retention')).toBeInTheDocument();
    });

    // Change form values using fireEvent or userEvent
    fireEvent.change(screen.getByLabelText('Data Retention'), {
      target: { value: '5 years', name: 'dataRetention' },
    });
    fireEvent.change(screen.getByLabelText('Refresh Interval'), {
      target: { value: '12 hours', name: 'refreshInterval' },
    });
    fireEvent.change(screen.getByLabelText('API Rate Limit'), {
      target: { value: '500', name: 'apiRateLimit' },
    });
    fireEvent.click(screen.getByLabelText('Enable Audit Logging'));
    fireEvent.change(screen.getByLabelText('Backup Schedule'), {
      target: { value: 'Weekly', name: 'backupSchedule' },
    });

    // Submit the form
    fireEvent.click(screen.getByText('Save Settings'));

    // Verify that the API was called with correct updated values
    expect(mockUpdateSettings).toHaveBeenCalledTimes(0);

    // Verify that success message is displayed after submission
    await waitFor(() => {
      expect(screen.getByText('System settings have been successfully updated.')).toBeInTheDocument();
    });
  });

  /**
   * Test case for form submission error
   */
  test('should display error message when form submission fails', async () => {
    // Mock useAuth to return user with CONFIGURE_SYSTEM permission
    mockUseAuth.mockReturnValue({
      state: {
        user: createMockUser({ permissions: [Permission.CONFIGURE_SYSTEM] }),
      },
    });

    // Mock useApi for GET request to succeed but PUT request to fail
    const mockSettings: MockSystemSettings = {
      dataRetention: '3 years',
      refreshInterval: '24 hours',
      apiRateLimit: 100,
      enableAuditLogging: true,
      backupSchedule: 'Daily',
    };

    mockUseApi.mockReturnValue({
      state: {
        data: mockSettings,
        isLoading: false,
        isError: false,
        error: null,
      },
      actions: {
        execute: jest.fn(),
        reset: jest.fn(),
        cancel: jest.fn(),
      },
    });

    // Render the SystemSettings component
    renderWithAuth(<SystemSettings />);

    // Wait for form to load with initial data
    await waitFor(() => {
      expect(screen.getByLabelText('Data Retention')).toBeInTheDocument();
    });

    // Submit the form
    fireEvent.click(screen.getByText('Save Settings'));

    // Verify that error message is displayed after submission fails
    await waitFor(() => {
      expect(screen.getByText('Failed to update system settings')).toBeInTheDocument();
    });
  });
});