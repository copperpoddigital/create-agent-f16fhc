import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

import MainLayout from './MainLayout';
import { AlertContext, AlertType } from '../../../contexts/AlertContext';

// Mock useMediaQuery hook to control responsive behavior in tests
const mockMediaQuery = vi.fn().mockReturnValue(false);
vi.mock('../../../hooks/useMediaQuery', () => ({
  default: () => mockMediaQuery()
}));

/**
 * Helper function to render the MainLayout with necessary providers and mocks
 * @param children Content to render inside the MainLayout
 * @param alertContextValue Mock values for the AlertContext
 * @returns The result of rendering with testing-library
 */
const renderWithProviders = (
  children: React.ReactNode, 
  alertContextValue = {}
) => {
  // Create default alert context value if not provided
  const defaultAlertContextValue = {
    alerts: [],
    hideAlert: vi.fn(),
    ...alertContextValue
  };

  // Render the component with required providers
  return render(
    <MemoryRouter>
      <AlertContext.Provider value={defaultAlertContextValue}>
        <MainLayout>
          {children}
        </MainLayout>
      </AlertContext.Provider>
    </MemoryRouter>
  );
};

describe('MainLayout', () => {
  it('renders the layout with header, sidebar, content, and footer', () => {
    // Render MainLayout with a test child component
    renderWithProviders(<div data-testid="test-content">Test Content</div>);
    
    // Verify header is rendered
    expect(screen.getByRole('banner')).toBeInTheDocument();
    // Verify sidebar is rendered
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    // Verify content area is rendered with the child component
    expect(screen.getByTestId('test-content')).toBeInTheDocument();
    // Verify footer is rendered
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
  });

  it('toggles sidebar when header toggle button is clicked', () => {
    // Render MainLayout component
    renderWithProviders(<div>Test Content</div>);
    
    // Find sidebar toggle button in header
    const toggleButton = screen.getByTestId('sidebar-toggle');
    // Verify sidebar is initially expanded
    expect(screen.getByTestId('main-layout')).toHaveClass('main-layout--sidebar-expanded');
    
    // Click the toggle button
    fireEvent.click(toggleButton);
    // Verify sidebar is collapsed
    expect(screen.getByTestId('main-layout')).toHaveClass('main-layout--sidebar-collapsed');
    
    // Click the toggle button again
    fireEvent.click(toggleButton);
    // Verify sidebar is expanded again
    expect(screen.getByTestId('main-layout')).toHaveClass('main-layout--sidebar-expanded');
  });

  it('collapses sidebar on mobile screens', () => {
    // Mock useMediaQuery to return true (mobile screen)
    mockMediaQuery.mockReturnValue(true);
    
    // Render MainLayout component
    renderWithProviders(<div>Test Content</div>);
    
    // Verify sidebar is collapsed by default on mobile
    expect(screen.getByTestId('main-layout')).toHaveClass('main-layout--sidebar-collapsed');
  });

  it('renders alerts from context', () => {
    // Create mock alerts array with success and error alerts
    const mockAlerts = [
      { 
        id: '1', 
        type: AlertType.SUCCESS, 
        message: 'Success alert', 
        dismissible: true,
        createdAt: Date.now() 
      },
      { 
        id: '2', 
        type: AlertType.ERROR, 
        message: 'Error alert', 
        dismissible: true,
        createdAt: Date.now() 
      }
    ];
    // Create mock hideAlert function
    const mockHideAlert = vi.fn();
    
    // Render MainLayout with mocked alert context
    renderWithProviders(
      <div>Test Content</div>,
      { alerts: mockAlerts, hideAlert: mockHideAlert }
    );
    
    // Verify both alerts are rendered with correct messages
    expect(screen.getByText('Success alert')).toBeInTheDocument();
    expect(screen.getByText('Error alert')).toBeInTheDocument();
    
    // Verify alert types are correctly applied
    const alerts = screen.getAllByRole('alert');
    expect(alerts[0]).toHaveClass('alert--success');
    expect(alerts[1]).toHaveClass('alert--error');
    
    // Click dismiss button on an alert
    const dismissButtons = screen.getAllByLabelText('Dismiss alert');
    fireEvent.click(dismissButtons[0]);
    // Verify hideAlert was called with correct alert ID
    expect(mockHideAlert).toHaveBeenCalledWith('1');
  });
});