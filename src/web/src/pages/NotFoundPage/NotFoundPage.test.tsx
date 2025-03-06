import { describe, it, expect, vi } from 'vitest';
import NotFoundPage from './NotFoundPage';
import { renderWithRouter, screen, userEvent } from '../../utils/test-utils';
import { ROUTES } from '../../config/routes';

describe('NotFoundPage', () => {
  it('renders the not found page correctly', () => {
    renderWithRouter(<NotFoundPage />);
    
    // Check that the page title is displayed correctly
    expect(screen.getByText('404 - Page Not Found')).toBeInTheDocument();
    
    // Check that the error message is displayed
    expect(
      screen.getByText('The page you are looking for does not exist or has been moved.')
    ).toBeInTheDocument();
    
    // Check that the 'Go to Dashboard' button is rendered
    expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
  });
  
  it('navigates to dashboard when button is clicked', async () => {
    // Create a mock navigate function
    const navigate = vi.fn();
    
    // Mock the useNavigate hook to return the mock navigate function
    vi.mock('react-router-dom', () => ({
      ...vi.importActual('react-router-dom'),
      useNavigate: () => navigate
    }));
    
    renderWithRouter(<NotFoundPage />);
    
    // Find the 'Go to Dashboard' button
    const dashboardButton = screen.getByText('Go to Dashboard');
    
    // Simulate a user clicking the button
    await userEvent.click(dashboardButton);
    
    // Assert that the navigate function was called with the dashboard route
    expect(navigate).toHaveBeenCalledWith(ROUTES.DASHBOARD.path);
  });
});