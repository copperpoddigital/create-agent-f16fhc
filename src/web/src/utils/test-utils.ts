import React from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react'; // ^14.0.0
import { screen, waitFor, within } from '@testing-library/react'; // ^14.0.0
import { fireEvent } from '@testing-library/react'; // ^14.0.0
import userEvent from '@testing-library/user-event'; // ^14.4.3
import { MemoryRouter, Routes, Route } from 'react-router-dom'; // ^6.10.0

import { ThemeProvider } from '../contexts/ThemeContext';
import { AuthProvider } from '../contexts/AuthContext';
import { User } from '../types/user.types';
import { AnalysisResult } from '../types/analysis.types';

/**
 * Custom render function that wraps components with necessary providers
 * @param ui Component to render
 * @param options Additional render options
 * @returns Result of rendering the component
 */
function customRender(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
): RenderResult {
  const AllProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
      <ThemeProvider>
        <AuthProvider>
          {children}
        </AuthProvider>
      </ThemeProvider>
    );
  };
  
  return render(ui, { wrapper: AllProviders, ...options });
}

/**
 * Renders a component with React Router providers
 * @param ui Component to render
 * @param options Additional render options
 * @param routes Additional routes to include
 * @returns Result of rendering the component with router
 */
function renderWithRouter(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
  routes: Array<{ path: string, element: React.ReactElement }> = []
): RenderResult {
  const RouterWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
      <MemoryRouter>
        <Routes>
          {routes.map(route => (
            <Route key={route.path} path={route.path} element={route.element} />
          ))}
          <Route path="/" element={children} />
        </Routes>
      </MemoryRouter>
    );
  };
  
  return customRender(ui, { wrapper: RouterWrapper, ...options });
}

/**
 * Renders a component with authentication context
 * @param ui Component to render
 * @param authState Optional auth state overrides
 * @param options Additional render options
 * @returns Result of rendering the component with auth context
 */
function renderWithAuth(
  ui: React.ReactElement,
  authState: any = {},
  options?: Omit<RenderOptions, 'wrapper'>
): RenderResult {
  const AuthWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
      <AuthProvider>
        {children}
      </AuthProvider>
    );
  };
  
  return render(ui, { wrapper: AuthWrapper, ...options });
}

/**
 * Renders a component with theme context
 * @param ui Component to render
 * @param theme Optional theme override
 * @param options Additional render options
 * @returns Result of rendering the component with theme context
 */
function renderWithTheme(
  ui: React.ReactElement,
  theme: string = 'light',
  options?: Omit<RenderOptions, 'wrapper'>
): RenderResult {
  const ThemeWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
      <ThemeProvider>
        {children}
      </ThemeProvider>
    );
  };
  
  return render(ui, { wrapper: ThemeWrapper, ...options });
}

/**
 * Creates a mock user object for testing
 * @param overrides Optional property overrides
 * @returns Mock user object
 */
function createMockUser(overrides: Partial<User> = {}): User {
  const defaultUser: User = {
    id: '1',
    username: 'testuser',
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
    role: 'analyst',
    isActive: true,
    isLocked: false,
    lastLogin: '2023-06-15T10:30:00Z',
    defaultCurrency: 'USD',
    dateFormat: 'MM/DD/YYYY',
    theme: 'light',
    emailNotifications: true,
    smsNotifications: false,
    inAppNotifications: true,
    preferences: {
      significantPriceChangeThreshold: 5,
      defaultView: 'dashboard',
      dashboardLayout: {},
      notifyOnPriceChanges: true,
      notifyOnDataSourceUpdates: true,
      notifyOnSystemMaintenance: false
    },
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-06-15T10:30:00Z'
  } as User;
  
  return { ...defaultUser, ...overrides };
}

/**
 * Creates a mock analysis result object for testing
 * @param overrides Optional property overrides
 * @returns Mock analysis result object
 */
function createMockAnalysisResult(overrides: Partial<AnalysisResult> = {}): AnalysisResult {
  const defaultResult: AnalysisResult = {
    id: '1',
    analysis_id: '1',
    time_period: {
      id: '1',
      name: 'Q1 2023',
      start_date: '2023-01-01',
      end_date: '2023-03-31',
      granularity: 'weekly',
      custom_interval: null,
      is_custom: false,
      created_by: '1',
      created_at: '2023-04-01T00:00:00Z'
    },
    filters: [],
    start_value: 4000,
    end_value: 4200,
    currency: 'USD',
    price_change: {
      absolute_change: 200,
      percentage_change: 5,
      trend_direction: 'increasing'
    },
    aggregates: {
      average: 4100,
      minimum: 4000,
      maximum: 4300
    },
    time_series: [
      { timestamp: '2023-01-01T00:00:00Z', value: 4000 },
      { timestamp: '2023-01-08T00:00:00Z', value: 4050 },
      { timestamp: '2023-01-15T00:00:00Z', value: 4100 },
      { timestamp: '2023-01-22T00:00:00Z', value: 4150 },
      { timestamp: '2023-01-29T00:00:00Z', value: 4200 }
    ],
    detailed_results: [
      {
        period: 'Jan 01-07',
        price: 4000,
        absolute_change: null,
        percentage_change: null,
        trend_direction: null
      },
      {
        period: 'Jan 08-14',
        price: 4050,
        absolute_change: 50,
        percentage_change: 1.25,
        trend_direction: 'increasing'
      },
      {
        period: 'Jan 15-21',
        price: 4100,
        absolute_change: 50,
        percentage_change: 1.23,
        trend_direction: 'increasing'
      },
      {
        period: 'Jan 22-28',
        price: 4150,
        absolute_change: 50,
        percentage_change: 1.22,
        trend_direction: 'increasing'
      },
      {
        period: 'Jan 29-Feb 04',
        price: 4200,
        absolute_change: 50,
        percentage_change: 1.20,
        trend_direction: 'increasing'
      }
    ],
    baseline_comparison: null,
    calculated_at: '2023-04-01T12:00:00Z'
  } as AnalysisResult;
  
  return { ...defaultResult, ...overrides };
}

// Export utility functions and re-export testing library utilities
export {
  customRender,
  renderWithRouter,
  renderWithAuth,
  renderWithTheme,
  createMockUser,
  createMockAnalysisResult,
  screen,
  waitFor,
  fireEvent,
  within,
  userEvent
};