import React from 'react';
import { render } from '@testing-library/react';
import { act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import AuthLayout from './AuthLayout';
import { renderWithAuth, screen, waitFor } from '../../../utils/test-utils';
import { ROUTES } from '../../../config/routes';
import { createMockUser } from '../../../utils/test-utils';

// Mock react-router-dom's useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock the useMediaQuery hook
jest.mock('../../../hooks/useMediaQuery', () => jest.fn(() => false));

import useMediaQuery from '../../../hooks/useMediaQuery';

describe('AuthLayout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Default to desktop view
    (useMediaQuery as jest.Mock).mockReturnValue(false);
  });

  test('renders correctly with title and subtitle', () => {
    renderWithAuth(
      <MemoryRouter>
        <AuthLayout 
          title="Test Title" 
          subtitle="Test Subtitle"
        >
          <p>Test content</p>
        </AuthLayout>
      </MemoryRouter>
    );

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  test('redirects authenticated users to dashboard', async () => {
    const mockUser = createMockUser();
    
    renderWithAuth(
      <MemoryRouter>
        <AuthLayout>
          <p>Test content</p>
        </AuthLayout>
      </MemoryRouter>,
      {
        isAuthenticated: true,
        user: mockUser,
        accessToken: 'mock-token',
        refreshToken: 'mock-refresh-token',
        expiresAt: Date.now() + 3600000,
        isLoading: false,
        error: null
      }
    );

    // Wait for the useEffect to run
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(ROUTES.DASHBOARD.path);
    });
  });

  test('does not redirect when redirectAuthenticated is false', async () => {
    const mockUser = createMockUser();
    
    renderWithAuth(
      <MemoryRouter>
        <AuthLayout redirectAuthenticated={false}>
          <p>Test content</p>
        </AuthLayout>
      </MemoryRouter>,
      {
        isAuthenticated: true,
        user: mockUser,
        accessToken: 'mock-token',
        refreshToken: 'mock-refresh-token',
        expiresAt: Date.now() + 3600000,
        isLoading: false,
        error: null
      }
    );

    // Wait to ensure any potential redirections would have occurred
    await waitFor(() => {});
    
    // The navigate function should not have been called
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('applies mobile styling on small screens', () => {
    // Mock the hook to return true for mobile screens
    (useMediaQuery as jest.Mock).mockReturnValue(true);
    
    renderWithAuth(
      <MemoryRouter>
        <AuthLayout>
          <p>Test content</p>
        </AuthLayout>
      </MemoryRouter>
    );

    // Check for mobile class
    const container = screen.getByTestId('auth-layout');
    expect(container.classList).contains('auth-layout--mobile');
  });

  test('applies additional className when provided', () => {
    renderWithAuth(
      <MemoryRouter>
        <AuthLayout className="custom-class">
          <p>Test content</p>
        </AuthLayout>
      </MemoryRouter>
    );

    const container = screen.getByTestId('auth-layout');
    expect(container.classList).contains('custom-class');
  });
});