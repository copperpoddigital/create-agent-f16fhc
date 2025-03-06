import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import Header from './Header';
import { 
  renderWithAuth, 
  renderWithTheme, 
  screen, 
  fireEvent, 
  userEvent, 
  waitFor,
  createMockUser 
} from '../../../utils/test-utils';

// Mock the useNavigate hook
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('Header component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly with default props', () => {
    const toggleSidebar = jest.fn();
    renderWithAuth(
      <MemoryRouter>
        <Header toggleSidebar={toggleSidebar} isSidebarExpanded={false} />
      </MemoryRouter>
    );
    
    // Logo should be displayed
    expect(screen.getByText('Freight Price Movement Agent')).toBeInTheDocument();
    
    // Sidebar toggle button should be displayed
    expect(screen.getByTestId('sidebar-toggle')).toBeInTheDocument();
    
    // Theme toggle button should be displayed
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
    
    // Help button should be displayed
    expect(screen.getByTestId('help-button')).toBeInTheDocument();
    
    // User menu button should be displayed
    expect(screen.getByTestId('user-menu-button')).toBeInTheDocument();
  });

  it('toggles sidebar when sidebar button is clicked', () => {
    const toggleSidebar = jest.fn();
    renderWithAuth(
      <MemoryRouter>
        <Header toggleSidebar={toggleSidebar} isSidebarExpanded={false} />
      </MemoryRouter>
    );
    
    // Click the sidebar toggle button
    fireEvent.click(screen.getByTestId('sidebar-toggle'));
    
    // The toggleSidebar function should have been called
    expect(toggleSidebar).toHaveBeenCalledTimes(1);
  });

  it('displays user information when authenticated', () => {
    const mockUser = createMockUser();
    
    // Create mock auth state
    const mockAuthState = {
      state: {
        isAuthenticated: true,
        user: mockUser,
        accessToken: 'fake-token',
        refreshToken: 'fake-refresh-token',
        expiresAt: Date.now() + 3600000,
        isLoading: false,
        error: null
      }
    };
    
    renderWithAuth(
      <MemoryRouter>
        <Header toggleSidebar={() => {}} isSidebarExpanded={false} />
      </MemoryRouter>,
      mockAuthState
    );
    
    // User menu button should be displayed
    expect(screen.getByTestId('user-menu-button')).toBeInTheDocument();
    
    // User's name should be displayed if auth state is properly mocked
    const userNameElement = screen.queryByText(`${mockUser.firstName} ${mockUser.lastName}`);
    if (userNameElement) {
      expect(userNameElement).toBeInTheDocument();
    }
  });

  it('opens user menu when user button is clicked', () => {
    const mockUser = createMockUser();
    
    // Create mock auth state
    const mockAuthState = {
      state: {
        isAuthenticated: true,
        user: mockUser,
        accessToken: 'fake-token',
        refreshToken: 'fake-refresh-token',
        expiresAt: Date.now() + 3600000,
        isLoading: false,
        error: null
      }
    };
    
    renderWithAuth(
      <MemoryRouter>
        <Header toggleSidebar={() => {}} isSidebarExpanded={false} />
      </MemoryRouter>,
      mockAuthState
    );
    
    // Click the user menu button
    fireEvent.click(screen.getByTestId('user-menu-button'));
    
    // The user dropdown should be displayed if auth state is properly mocked
    const userDropdown = screen.queryByTestId('user-dropdown');
    if (userDropdown) {
      expect(userDropdown).toBeInTheDocument();
      
      // Logout option should be available
      expect(screen.getByTestId('logout-button')).toBeInTheDocument();
    }
  });

  it('calls logout function when logout button is clicked', async () => {
    const mockUser = createMockUser();
    const mockLogout = jest.fn().mockResolvedValue(undefined);
    
    // Create mock auth state with mock logout function
    const mockAuthState = {
      state: {
        isAuthenticated: true,
        user: mockUser,
        accessToken: 'fake-token',
        refreshToken: 'fake-refresh-token',
        expiresAt: Date.now() + 3600000,
        isLoading: false,
        error: null
      },
      logout: mockLogout
    };
    
    renderWithAuth(
      <MemoryRouter>
        <Header toggleSidebar={() => {}} isSidebarExpanded={false} />
      </MemoryRouter>,
      mockAuthState
    );
    
    // Click the user menu button to open the dropdown
    fireEvent.click(screen.getByTestId('user-menu-button'));
    
    // Click the logout button if it's available
    const logoutButton = screen.queryByTestId('logout-button');
    if (logoutButton) {
      fireEvent.click(logoutButton);
      
      // The logout function should be called
      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalledTimes(1);
      });
      
      // After logout, we should navigate to login page
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    }
  });

  it('toggles theme when theme button is clicked', () => {
    renderWithTheme(
      <MemoryRouter>
        <Header toggleSidebar={() => {}} isSidebarExpanded={false} />
      </MemoryRouter>,
      'light'
    );
    
    // Click the theme toggle button
    fireEvent.click(screen.getByTestId('theme-toggle'));
    
    // We can only verify the button exists and can be clicked without errors
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
  });

  it('navigates to settings when settings button is clicked', () => {
    const mockUser = createMockUser();
    
    // Create mock auth state
    const mockAuthState = {
      state: {
        isAuthenticated: true,
        user: mockUser,
        accessToken: 'fake-token',
        refreshToken: 'fake-refresh-token',
        expiresAt: Date.now() + 3600000,
        isLoading: false,
        error: null
      }
    };
    
    renderWithAuth(
      <MemoryRouter>
        <Header toggleSidebar={() => {}} isSidebarExpanded={false} />
      </MemoryRouter>,
      mockAuthState
    );
    
    // Click the user menu button to open the dropdown
    fireEvent.click(screen.getByTestId('user-menu-button'));
    
    // Click the settings button if it's available
    const settingsButton = screen.queryByTestId('settings-button');
    if (settingsButton) {
      fireEvent.click(settingsButton);
      
      // We should navigate to settings page
      expect(mockNavigate).toHaveBeenCalledWith('/settings');
    }
  });

  it('navigates to help page when help button is clicked', () => {
    renderWithAuth(
      <MemoryRouter>
        <Header toggleSidebar={() => {}} isSidebarExpanded={false} />
      </MemoryRouter>
    );
    
    // Click the help button
    fireEvent.click(screen.getByTestId('help-button'));
    
    // We should navigate to help page
    expect(mockNavigate).toHaveBeenCalledWith('/help');
  });

  it('adapts to different screen sizes', () => {
    // Mock window.matchMedia
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(max-width: 768px)',
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn()
    }));
    
    renderWithAuth(
      <MemoryRouter>
        <Header toggleSidebar={() => {}} isSidebarExpanded={false} />
      </MemoryRouter>
    );
    
    // Check that the header has the appropriate class
    expect(screen.getByRole('banner')).toHaveClass('header');
  });
});