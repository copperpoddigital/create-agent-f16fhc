import React from 'react';
import { vi } from 'vitest';
import AlertsWidget from './AlertsWidget';
import { customRender, screen, waitFor } from '../../../utils/test-utils';
import { getSystemAlerts } from '../../../api';
import { Alert as AlertType } from '../../../types';
import userEvent from '@testing-library/user-event';

// Mock the API and the useApi hook
vi.mock('../../../api', () => ({ getSystemAlerts: vi.fn() }));
vi.mock('../../../hooks/useApi', () => ({ default: vi.fn() }));

describe('AlertsWidget', () => {
  // Mock data
  const mockAlerts: AlertType[] = [
    { id: '1', type: 'warning', message: 'Significant price increase detected on APAC routes' },
    { id: '2', type: 'info', message: '3 data sources need updating' },
    { id: '3', type: 'error', message: 'Integration failed with external system' }
  ];

  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('should show loading state initially', async () => {
    // Mock useApi to return loading state
    const useApiMock = require('../../../hooks/useApi').default;
    useApiMock.mockReturnValue({
      state: {
        isLoading: true,
        isError: false,
        data: null,
        error: null
      },
      actions: {
        execute: vi.fn()
      }
    });

    // Render component
    customRender(<AlertsWidget />);
    
    // Check if loading spinner is visible
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('should render alerts when data is loaded', async () => {
    // Mock useApi to return success state with data
    const useApiMock = require('../../../hooks/useApi').default;
    useApiMock.mockReturnValue({
      state: {
        isLoading: false,
        isError: false,
        data: mockAlerts,
        error: null
      },
      actions: {
        execute: vi.fn()
      }
    });

    // Render component
    customRender(<AlertsWidget />);
    
    // Check if alerts are rendered with correct text
    expect(screen.getByText('Significant price increase detected on APAC routes')).toBeInTheDocument();
    expect(screen.getByText('3 data sources need updating')).toBeInTheDocument();
    expect(screen.getByText('Integration failed with external system')).toBeInTheDocument();
    
    // Check alert elements exist with correct test IDs
    expect(screen.getByTestId('alert-1')).toBeInTheDocument();
    expect(screen.getByTestId('alert-2')).toBeInTheDocument();
    expect(screen.getByTestId('alert-3')).toBeInTheDocument();
  });

  it('should render error message when API call fails', async () => {
    // Mock useApi to return error state
    const useApiMock = require('../../../hooks/useApi').default;
    useApiMock.mockReturnValue({
      state: {
        isLoading: false,
        isError: true,
        data: null,
        error: { message: 'Failed to fetch alerts' }
      },
      actions: {
        execute: vi.fn()
      }
    });

    // Render component
    customRender(<AlertsWidget />);
    
    // Check if error message is displayed
    expect(screen.getByText(/Failed to load alerts/)).toBeInTheDocument();
    expect(screen.getByText(/Failed to fetch alerts/)).toBeInTheDocument();
  });

  it('should render empty state when no alerts are available', async () => {
    // Mock useApi to return success state with empty array
    const useApiMock = require('../../../hooks/useApi').default;
    useApiMock.mockReturnValue({
      state: {
        isLoading: false,
        isError: false,
        data: [],
        error: null
      },
      actions: {
        execute: vi.fn()
      }
    });

    // Render component
    customRender(<AlertsWidget />);
    
    // Check if empty state message is displayed
    expect(screen.getByText('No alerts at this time')).toBeInTheDocument();
  });

  it('should handle alert dismissal correctly', async () => {
    // Setup user event
    const user = userEvent.setup();
    
    // Mock useApi to return success state with data
    const useApiMock = require('../../../hooks/useApi').default;
    useApiMock.mockReturnValue({
      state: {
        isLoading: false,
        isError: false,
        data: mockAlerts,
        error: null
      },
      actions: {
        execute: vi.fn()
      }
    });

    // Render component
    customRender(<AlertsWidget />);
    
    // Verify all alerts are initially displayed
    expect(screen.getAllByRole('alert').length).toBe(3);
    
    // Find and click the dismiss button on the first alert
    const dismissButtons = screen.getAllByRole('button', { name: /Dismiss alert/i });
    await user.click(dismissButtons[0]);
    
    // Verify that the dismissed alert is no longer displayed
    await waitFor(() => {
      expect(screen.queryByText('Significant price increase detected on APAC routes')).not.toBeInTheDocument();
    });
    
    // Verify other alerts are still displayed
    expect(screen.getByText('3 data sources need updating')).toBeInTheDocument();
    expect(screen.getByText('Integration failed with external system')).toBeInTheDocument();
    expect(screen.getAllByRole('alert').length).toBe(2);
  });
});