# src/web/src/components/forms/ReportForm/ReportForm.test.tsx
```typescript
import React from 'react'; // ^18.2.0
import { vi } from 'vitest'; // ^0.30.1
import ReportForm from './ReportForm';
import { customRender, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';
import { createReport, updateReport } from '../../../api/report-api';
import { getAnalysisResults } from '../../../api/analysis-api';
import { mockAnalysisResults, mockReports, generateMockReport, generateMockAnalysisResult } from '../../../../tests/mocks/data';
import { ReportType } from '../../../types/report.types';
import { OutputFormat } from '../../../types/analysis.types';

// Mock the API functions
vi.mock('../../../api/report-api');
vi.mock('../../../api/analysis-api');

// Setup function to mock API calls and prepare the test environment
const setup = () => {
  // Mock getAnalysisResults API function to return mock analysis results
  (getAnalysisResults as vi.Mock).mockResolvedValue({
    success: true,
    data: mockAnalysisResults,
    error: null,
    meta: null,
  });

  // Mock createReport API function to return a success response
  (createReport as vi.Mock).mockResolvedValue({
    success: true,
    data: generateMockReport(),
    error: null,
    meta: null,
  });

  // Mock updateReport API function to return a success response
  (updateReport as vi.Mock).mockResolvedValue({
    success: true,
    data: generateMockReport(),
    error: null,
    meta: null,
  });
};

describe('ReportForm Component', () => {
  beforeEach(() => {
    setup();
  });

  it('renders the form correctly in create mode', () => {
    // Render the ReportForm component with required props
    customRender(<ReportForm onSubmit={() => {}} onCancel={() => {}} />);

    // Check that all form elements are present
    expect(screen.getByLabelText('Report Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByLabelText('Analysis Result')).toBeInTheDocument();
    expect(screen.getByLabelText('Output Format')).toBeInTheDocument();
    expect(screen.getByLabelText('Include visualization')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Report' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();

    // Verify form is in create mode with empty fields
    expect(screen.getByLabelText('Report Name')).toHaveValue('');
    expect(screen.getByLabelText('Description')).toHaveValue('');
  });

  it('renders the form correctly in edit mode', () => {
    // Create a mock report for editing
    const mockReport = generateMockReport({
      name: 'Test Report',
      description: 'Test Description',
      analysis_id: 'ar-1',
      output_format: OutputFormat.CSV,
      include_visualization: true,
    });

    // Render the ReportForm component with the mock report
    customRender(<ReportForm report={mockReport} onSubmit={() => {}} onCancel={() => {}} />);

    // Check that all form elements are present
    expect(screen.getByLabelText('Report Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByLabelText('Analysis Result')).toBeInTheDocument();
    expect(screen.getByLabelText('Output Format')).toBeInTheDocument();
    expect(screen.getByLabelText('Include visualization')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Update Report' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();

    // Verify form fields are populated with report data
    expect(screen.getByLabelText('Report Name')).toHaveValue(mockReport.name);
    expect(screen.getByLabelText('Description')).toHaveValue(mockReport.description);
  });

  it('loads analysis results on mount', async () => {
    // Render the ReportForm component
    customRender(<ReportForm onSubmit={() => {}} onCancel={() => {}} />);

    // Wait for the analysis results to load
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Analysis Result' })).toBeInTheDocument();
    });

    // Verify that the analysis select dropdown contains the expected options
    const analysisSelect = screen.getByRole('combobox', { name: 'Analysis Result' });
    expect(analysisSelect).toBeInTheDocument();
    expect(analysisSelect).not.toBeDisabled();
  });

  it('validates required fields', async () => {
    // Render the ReportForm component
    customRender(<ReportForm onSubmit={() => {}} onCancel={() => {}} />);

    // Submit the form without filling required fields
    fireEvent.click(screen.getByRole('button', { name: 'Create Report' }));

    // Verify validation error messages are displayed
    await waitFor(() => {
      expect(screen.getByText('Report name is required')).toBeInTheDocument();
      expect(screen.getByText('Analysis result is required')).toBeInTheDocument();
    });

    // Fill in required fields
    fireEvent.change(screen.getByLabelText('Report Name'), { target: { value: 'Test Report' } });
    fireEvent.change(screen.getByRole('combobox', { name: 'Analysis Result' }), { target: { value: 'ar-1' } });

    // Verify validation errors are cleared
    await waitFor(() => {
      expect(screen.queryByText('Report name is required')).not.toBeInTheDocument();
      expect(screen.queryByText('Analysis result is required')).not.toBeInTheDocument();
    });
  });

  it('handles form submission for creating a new report', async () => {
    // Render the ReportForm component
    const onSubmit = vi.fn();
    customRender(<ReportForm onSubmit={onSubmit} onCancel={() => {}} />);

    // Fill in all required fields
    fireEvent.change(screen.getByLabelText('Report Name'), { target: { value: 'Test Report' } });
    fireEvent.change(screen.getByLabelText('Description'), { target: { value: 'Test Description' } });
    fireEvent.selectOptions(screen.getByRole('combobox', { name: 'Analysis Result' }), 'ar-1');
    fireEvent.selectOptions(screen.getByRole('combobox', { name: 'Output Format' }), OutputFormat.CSV);
    fireEvent.click(screen.getByLabelText('Include visualization'));

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Create Report' }));

    // Verify createReport API was called with correct parameters
    await waitFor(() => {
      expect(createReport).toHaveBeenCalledWith({
        name: 'Test Report',
        description: 'Test Description',
        type: ReportType.STANDARD,
        analysis_id: 'ar-1',
        output_format: OutputFormat.CSV,
        include_visualization: true,
      });
    });

    // Verify onSubmit callback was called with the created report
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalled();
    });
  });

  it('handles form submission for updating an existing report', async () => {
    // Create a mock report for editing
    const mockReport = generateMockReport({
      id: 'r-1',
      name: 'Test Report',
      description: 'Test Description',
      analysis_id: 'ar-1',
      output_format: OutputFormat.CSV,
      include_visualization: true,
    });

    // Render the ReportForm component with the mock report
    const onSubmit = vi.fn();
    customRender(<ReportForm report={mockReport} onSubmit={onSubmit} onCancel={() => {}} />);

    // Modify some fields
    fireEvent.change(screen.getByLabelText('Report Name'), { target: { value: 'Updated Report' } });
    fireEvent.change(screen.getByLabelText('Description'), { target: { value: 'Updated Description' } });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Update Report' }));

    // Verify updateReport API was called with correct parameters
    await waitFor(() => {
      expect(updateReport).toHaveBeenCalledWith('r-1', {
        name: 'Updated Report',
        description: 'Updated Description',
        status: 'active',
        output_format: OutputFormat.CSV,
        include_visualization: true,
      });
    });

    // Verify onSubmit callback was called with the updated report
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalled();
    });
  });

  it('handles cancellation correctly', () => {
    // Render the ReportForm component
    const onCancel = vi.fn();
    customRender(<ReportForm onSubmit={() => {}} onCancel={onCancel} />);

    // Click the cancel button
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));

    // Verify onCancel callback was called
    expect(onCancel).toHaveBeenCalled();
  });

  it('pre-selects analysis ID when provided', () => {
    // Create a mock analysis ID
    const analysisId = 'ar-1';

    // Render the ReportForm component with the analysisId prop
    customRender(<ReportForm onSubmit={() => {}} onCancel={() => {}} analysisId={analysisId} />);

    // Verify the analysis select field has the correct value selected
    expect((screen.getByRole('combobox', { name: 'Analysis Result' }) as HTMLSelectElement).value).toBe(analysisId);
  });

  it('disables submit button when form is invalid', async () => {
    // Render the ReportForm component
    customRender(<ReportForm onSubmit={() => {}} onCancel={() => {}} />);

    // Check that submit button is disabled initially
    expect(screen.getByRole('button', { name: 'Create Report' })).toBeDisabled();

    // Fill in required fields
    fireEvent.change(screen.getByLabelText('Report Name'), { target: { value: 'Test Report' } });
    fireEvent.selectOptions(screen.getByRole('combobox', { name: 'Analysis Result' }), 'ar-1');

    // Verify submit button becomes enabled
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Create Report' })).not.toBeDisabled();
    });
  });

  it('shows loading state during submission', async () => {
    // Mock API functions to delay response
    (createReport as vi.Mock).mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            success: true,
            data: generateMockReport(),
            error: null,
            meta: null,
          });
        }, 1000); // Delay for 1 second
      });
    });

    // Render the ReportForm component
    customRender(<ReportForm onSubmit={() => {}} onCancel={() => {}} />);

    // Fill in required fields
    fireEvent.change(screen.getByLabelText('Report Name'), { target: { value: 'Test Report' } });
    fireEvent.selectOptions(screen.getByRole('combobox', { name: 'Analysis Result' }), 'ar-1');

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Create Report' }));

    // Verify loading state is shown
    expect(screen.getByRole('button', { name: 'Create Report' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Create Report' })).toHaveTextContent('Create Report');

    // Wait for submission to complete
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Create Report' })).not.toBeDisabled();
    });

    // Verify loading state is removed
    expect(screen.getByRole('button', { name: 'Create Report' })).toHaveTextContent('Create Report');
  });
});