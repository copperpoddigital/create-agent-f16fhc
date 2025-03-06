import React from 'react';
import { render } from '@testing-library/react';
import { vi } from 'vitest';
import Sidebar from './Sidebar';
import { renderWithRouter, renderWithAuth, screen, fireEvent, userEvent } from '../../../utils/test-utils';
import { ROUTES } from '../../../config/routes';
import * as useAuthModule from '../../../hooks/useAuth';

// Mock useAuth hook
const mockUseAuth = (mockAuthState: any) => {
  return vi.spyOn(useAuthModule, 'default').mockImplementation(() => ({
    state: mockAuthState,
    login: vi.fn(),
    logout: vi.fn(),
    refreshSession: vi.fn().mockResolvedValue(true),
    changePassword: vi.fn(),
    resetPassword: vi.fn(),
    confirmPasswordReset: vi.fn()
  }));
};

describe('Sidebar component', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders the sidebar in expanded state', () => {
    mockUseAuth({ user: { role: 'admin' }, isAuthenticated: true });
    renderWithRouter(<Sidebar expanded={true} onToggle={() => {}} />);
    
    const sidebar = screen.getByTestId('sidebar');
    expect(sidebar).toBeInTheDocument();
    expect(sidebar).toHaveClass('sidebar--expanded');
    expect(screen.getByText('Freight Price Movement Agent')).toBeInTheDocument();
    
    // Navigation item texts should be visible in expanded state
    expect(screen.getByText('Dashboard')).toBeVisible();
    expect(screen.getByText('Settings')).toBeVisible();
  });

  it('renders the sidebar in collapsed state', () => {
    mockUseAuth({ user: { role: 'admin' }, isAuthenticated: true });
    renderWithRouter(<Sidebar expanded={false} onToggle={() => {}} />);
    
    const sidebar = screen.getByTestId('sidebar');
    expect(sidebar).toBeInTheDocument();
    expect(sidebar).toHaveClass('sidebar--collapsed');
    
    // Brand name should not be visible
    expect(screen.queryByText('Freight Price Movement Agent')).not.toBeInTheDocument();
    
    // Navigation item texts should not be visible in collapsed state
    expect(screen.queryAllByClassName('sidebar__nav-text')).toHaveLength(0);
  });

  it('toggles sidebar expansion when toggle button is clicked', () => {
    mockUseAuth({ user: { role: 'admin' }, isAuthenticated: true });
    const onToggleMock = vi.fn();
    renderWithRouter(<Sidebar expanded={true} onToggle={onToggleMock} />);
    
    const toggleButton = screen.getByRole('button', { name: /collapse sidebar/i });
    fireEvent.click(toggleButton);
    
    expect(onToggleMock).toHaveBeenCalledTimes(1);
  });

  it('renders navigation items based on user permissions for Administrator', () => {
    const authStateMock = {
      isAuthenticated: true,
      user: {
        role: 'admin'
      }
    };
    
    mockUseAuth(authStateMock);
    
    renderWithRouter(<Sidebar expanded={true} onToggle={() => {}} />);
    
    // Admin should see all navigation items
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Data Sources')).toBeInTheDocument();
    expect(screen.getByText('Analysis')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders navigation items based on user permissions for Viewer', () => {
    const authStateMock = {
      isAuthenticated: true,
      user: {
        role: 'viewer'
      }
    };
    
    mockUseAuth(authStateMock);
    
    renderWithRouter(<Sidebar expanded={true} onToggle={() => {}} />);
    
    // Based on route permissions, Viewer should see Dashboard, Analysis, Reports, and Settings
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.queryByText('Data Sources')).not.toBeInTheDocument(); // Should not see Data Sources
    expect(screen.getByText('Analysis')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('applies active class to current route', () => {
    mockUseAuth({ user: { role: 'admin' }, isAuthenticated: true });
    
    // Mock useLocation to return a specific path
    const useLocationMock = vi.fn().mockReturnValue({ pathname: ROUTES.DASHBOARD.path });
    vi.spyOn(require('react-router-dom'), 'useLocation').mockImplementation(useLocationMock);
    
    renderWithRouter(<Sidebar expanded={true} onToggle={() => {}} />);
    
    // Find the dashboard navigation link
    const dashboardLink = screen.getByText('Dashboard').closest('a');
    expect(dashboardLink).toHaveClass('sidebar__nav-link--active');
  });

  it('handles null or undefined user gracefully', () => {
    const authStateMock = {
      isAuthenticated: false,
      user: null // Null user
    };
    
    mockUseAuth(authStateMock);
    
    renderWithRouter(<Sidebar expanded={true} onToggle={() => {}} />);
    
    // Sidebar should render, but no navigation items should be visible
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.queryAllByRole('link')).toHaveLength(0);
  });
});