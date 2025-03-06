import React from 'react'; // ^18.2.0
import { vi } from 'vitest'; // ^0.30.1
import {
  renderWithRouter,
  screen,
  waitFor,
  fireEvent,
  userEvent,
} from '../../utils/test-utils';
import NewAnalysisPage from './NewAnalysisPage';
import { ROUTES } from '../../config/routes';
import { AnalysisFormValues } from '../../components/forms/AnalysisForm';

// Mock useNavigate hook from react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

// Mock useAlert hook
const mockShowSuccess = vi.fn();
const mockShowError = vi.fn();
vi.mock('../../hooks/useAlert', () => ({
  default: () => ({ showSuccess: mockShowSuccess, showError: mockShowError }),
}));

describe('NewAnalysisPage component', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    mockShowSuccess.mockReset();
    mockShowError.mockReset();
  });

  it('should render the page with correct title', async () => {
    renderWithRouter(<NewAnalysisPage />);
    expect(screen.getByText('New Analysis')).toBeInTheDocument();
    expect(screen.getByLabelText('Analysis Name')).toBeInTheDocument();
  });

  it('should handle form submission successfully', async () => {
    renderWithRouter(<NewAnalysisPage />);

    // Fill in required form fields
    const nameInput = screen.getByLabelText<HTMLInputElement>('Analysis Name');
    fireEvent.change(nameInput, { target: { value: 'Test Analysis' } });

    // Click the submit button
    const submitButton = screen.getByRole('button', { name: /Create Analysis/i });
    fireEvent.click(submitButton);

    // Verify that success alert was shown
    await waitFor(() => {
      expect(mockShowSuccess).toHaveBeenCalledWith('Analysis created successfully!');
    });

    // Verify that navigation to results page occurred with correct ID
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        ROUTES.ANALYSIS_RESULTS.path.replace(':id', 'new-analysis-id')
      );
    });
  });

  it('should handle form submission errors', async () => {
    renderWithRouter(<NewAnalysisPage />);

    // Fill in required form fields
    const nameInput = screen.getByLabelText<HTMLInputElement>('Analysis Name');
    fireEvent.change(nameInput, { target: { value: 'Test Analysis' } });

    // Mock API to throw an error
    mockShowSuccess.mockImplementation(() => {
      throw new Error('API error');
    });

    // Click the submit button
    const submitButton = screen.getByRole('button', { name: /Create Analysis/i });
    fireEvent.click(submitButton);

    // Verify that error alert was shown
    await waitFor(() => {
      expect(mockShowError).toHaveBeenCalledWith(
        'Failed to create analysis. Please try again.'
      );
    });

    // Verify that navigation did not occur
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('should navigate back to analysis list on cancel', async () => {
    renderWithRouter(<NewAnalysisPage />);

    // Click the cancel button
    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    fireEvent.click(cancelButton);

    // Verify that navigation to analysis list page occurred
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(ROUTES.ANALYSIS.path);
    });
  });
});