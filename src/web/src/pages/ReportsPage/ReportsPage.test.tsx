import React from 'react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, cleanup } from '@testing-library/react';
import { renderWithRouter, screen, fireEvent, waitFor } from '../../utils/test-utils';
import { ROUTES } from '../../config/routes';

// Mock the useNavigate hook
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock the ReportList component
vi.mock('../../components/reports/ReportList', () => ({
  __esModule: true,
  default: vi.fn(() => <div data-testid="report-list">Mock Report List</div>)
}));

// Import the component under test and the mocked component
import ReportsPage from './ReportsPage';
import ReportList from '../../components/reports/ReportList';

describe('ReportsPage', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });
  
  afterEach(() => {
    // Clean up after each test
    cleanup();
  });
  
  it('renders the reports page with title and create button', () => {
    renderWithRouter(<ReportsPage />);
    
    // Check for the page title
    expect(screen.getByText('Reports')).toBeInTheDocument();
    
    // Check for the create button
    expect(screen.getByText('Create Report')).toBeInTheDocument();
  });
  
  it('navigates to create report page when create button is clicked', () => {
    renderWithRouter(<ReportsPage />);
    
    // Find and click the create button
    const createButton = screen.getByText('Create Report');
    fireEvent.click(createButton);
    
    // Verify the navigation
    expect(mockNavigate).toHaveBeenCalledWith('/reports/create');
  });
  
  it('navigates to edit report page when edit button is clicked', () => {
    renderWithRouter(<ReportsPage />);
    
    // Get the props passed to ReportList
    const reportListProps = (ReportList as vi.MockedFunction<typeof ReportList>).mock.calls[0][0];
    
    // Simulate the edit callback being called
    reportListProps.onEditReport('123');
    
    // Verify the navigation
    expect(mockNavigate).toHaveBeenCalledWith('/reports/edit/123');
  });
  
  it('navigates to report details page when view button is clicked', () => {
    renderWithRouter(<ReportsPage />);
    
    // Get the props passed to ReportList
    const reportListProps = (ReportList as vi.MockedFunction<typeof ReportList>).mock.calls[0][0];
    
    // Simulate the view callback being called
    reportListProps.onViewReport('123');
    
    // Verify the navigation
    expect(mockNavigate).toHaveBeenCalledWith('/reports/123');
  });
  
  it('renders the ReportList component with correct props', () => {
    renderWithRouter(<ReportsPage />);
    
    // Verify the ReportList component is rendered
    expect(screen.getByTestId('report-list')).toBeInTheDocument();
    
    // Verify the props passed to ReportList
    const reportListProps = (ReportList as vi.MockedFunction<typeof ReportList>).mock.calls[0][0];
    expect(typeof reportListProps.onCreateReport).toBe('function');
    expect(typeof reportListProps.onEditReport).toBe('function');
    expect(typeof reportListProps.onViewReport).toBe('function');
    expect(reportListProps['aria-label']).toBe('List of saved reports');
  });
});