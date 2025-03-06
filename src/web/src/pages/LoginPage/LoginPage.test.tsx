import React from 'react';
import { vi } from 'vitest';
import LoginPage from './LoginPage';
import { renderWithRouter, renderWithAuth, screen, waitFor, userEvent } from '../../utils/test-utils';
import { ROUTES } from '../../config/routes';
import { createMockUser } from '../../utils/test-utils';

// Mock navigate and login functions
const mockNavigate = vi.fn();
const mockLogin = vi.fn();

// Mock required hooks
vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({
    state: null,
    search: ''
  })
}));

vi.mock('../../hooks/useAuth', () => ({
  default: () => ({
    state: {
      isAuthenticated: false,
      user: null,
      isLoading: false,
      error: null
    },
    login: mockLogin
  })
}));

describe('LoginPage', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks();
    
    // Set up default mock implementations
    mockLogin.mockResolvedValue(undefined);
    mockNavigate.mockImplementation(() => {});
  });

  test('renders the login form', () => {
    renderWithRouter(<LoginPage />);
    
    // Check for form elements
    expect(screen.getByText(/freight price movement agent/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByText(/please contact your administrator if you need access/i)).toBeInTheDocument();
  });

  test('calls login function with correct credentials on form submission', async () => {
    renderWithRouter(<LoginPage />);
    
    // Fill in and submit the form
    await userEvent.type(screen.getByLabelText(/username/i), 'testuser');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // Check login was called with correct credentials
    expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123', false);
  });

  test('navigates to dashboard after successful login', async () => {
    renderWithRouter(<LoginPage />);
    
    // Simulate successful login by triggering onSuccess callback
    const loginForm = screen.getByRole('form');
    const onSuccessProp = loginForm.getAttribute('data-on-success');
    if (onSuccessProp) {
      // Simulate the callback being triggered
      eval(onSuccessProp)();
    }
    
    // Check navigation to dashboard
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.DASHBOARD.path, { replace: true });
  });

  test('navigates to redirect path if provided after successful login', async () => {
    // Override useLocation mock for this test
    vi.mocked(require('react-router-dom').useLocation).mockImplementation(() => ({
      state: { from: '/analysis' },
      search: ''
    }));

    renderWithRouter(<LoginPage />);
    
    // Simulate successful login by triggering onSuccess callback
    const loginForm = screen.getByRole('form');
    const onSuccessProp = loginForm.getAttribute('data-on-success');
    if (onSuccessProp) {
      // Simulate the callback being triggered
      eval(onSuccessProp)();
    }
    
    // Check navigation to redirect path
    expect(mockNavigate).toHaveBeenCalledWith('/analysis', { replace: true });
  });

  test('displays error message on login failure', async () => {
    // Override useAuth mock for this test
    vi.mocked(require('../../hooks/useAuth').default).mockImplementation(() => ({
      state: {
        isAuthenticated: false,
        user: null,
        isLoading: false,
        error: 'Invalid credentials'
      },
      login: mockLogin
    }));
    
    // Make login fail
    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'));

    renderWithRouter(<LoginPage />);
    
    // Submit the form
    await userEvent.type(screen.getByLabelText(/username/i), 'testuser');
    await userEvent.type(screen.getByLabelText(/password/i), 'wrongpassword');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // Check error message
    expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
  });

  test('redirects to dashboard if user is already authenticated', () => {
    // Override useAuth mock for this test
    vi.mocked(require('../../hooks/useAuth').default).mockImplementation(() => ({
      state: {
        isAuthenticated: true,
        user: createMockUser(),
        isLoading: false,
        error: null
      },
      login: mockLogin
    }));

    renderWithRouter(<LoginPage />);
    
    // Check immediate navigation
    expect(mockNavigate).toHaveBeenCalledWith(ROUTES.DASHBOARD.path, { replace: true });
  });
});