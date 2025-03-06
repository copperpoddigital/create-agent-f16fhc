import React from 'react'; // ^18.2.0
import { renderWithRouter, screen, waitFor, userEvent } from '../../utils/test-utils';
import { CreateReportPage } from './CreateReportPage';
import ReportForm from '../../components/forms/ReportForm';
import { mockAnalysisResults, generateMockReport } from '../../tests/mocks/data';
import { server } from '../../tests/mocks/server';
import { ROUTES } from '../../config/routes';
import { rest } from 'msw'; // ^1.0.0

describe('CreateReportPage', () => {
  beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('renders the create report page', async () => {
    renderWithRouter(<CreateReportPage />);

    expect(screen.getByText('Create Report')).toBeInTheDocument();
    expect(screen.getByTestId('report-form')).toBeInTheDocument();
  });

  it('submits the form and navigates to reports page on success', async () => {
    const mockReport = generateMockReport();

    server.use(
      rest.post(`${API_CONFIG.BASE_URL}${API_CONFIG.API_PATH}/${API_CONFIG.VERSION}/reports`, (req, res, ctx) => {
        return res(ctx.status(201), ctx.json({ success: true, data: mockReport }));
      })
    );

    const { history } = renderWithRouter(<CreateReportPage />);

    userEvent.type(screen.getByLabelText('Report Name *'), 'Test Report');
    userEvent.selectOptions(screen.getByLabelText('Analysis Result *'), mockAnalysisResults[0].id);
    userEvent.click(screen.getByRole('button', { name: 'Create Report' }));

    await waitFor(() => {
      expect(history.location.pathname).toBe(`${ROUTES.REPORTS.path}/${mockReport.id}`);
    });

    await waitFor(() => {
      expect(screen.getByText('Report created successfully!')).toBeInTheDocument();
    });
  });

  it('displays validation errors when form is invalid', async () => {
    const { container } = renderWithRouter(<CreateReportPage />);

    userEvent.click(screen.getByRole('button', { name: 'Create Report' }));

    await waitFor(() => {
      expect(screen.getByText('Report name is required')).toBeInTheDocument();
      expect(screen.getByText('Analysis result is required')).toBeInTheDocument();
    });
  });

  it('displays error message when API request fails', async () => {
    server.use(
      rest.post(`${API_CONFIG.BASE_URL}${API_CONFIG.API_PATH}/${API_CONFIG.VERSION}/reports`, (req, res, ctx) => {
        return res(
          ctx.status(500),
          ctx.json({ success: false, error: { message: 'Failed to create report' } })
        );
      })
    );

    const { history } = renderWithRouter(<CreateReportPage />);

    userEvent.type(screen.getByLabelText('Report Name *'), 'Test Report');
    userEvent.selectOptions(screen.getByLabelText('Analysis Result *'), mockAnalysisResults[0].id);
    userEvent.click(screen.getByRole('button', { name: 'Create Report' }));

    await waitFor(() => {
      expect(screen.getByText('Failed to create report')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(history.location.pathname).not.toBe(ROUTES.REPORTS.path);
    });
  });

  it('navigates back to reports page when cancel is clicked', async () => {
    const { history } = renderWithRouter(<CreateReportPage />);

    userEvent.click(screen.getByRole('button', { name: 'Cancel' }));

    await waitFor(() => {
      expect(history.location.pathname).toBe(ROUTES.REPORTS.path);
    });
  });

  it('pre-selects analysis when analysisId is in URL query params', async () => {
    const analysisId = mockAnalysisResults[0].id;
    renderWithRouter(<CreateReportPage />, {}, [`/reports/create?analysisId=${analysisId}`]);

    await waitFor(() => {
      expect((screen.getByLabelText('Analysis Result *') as HTMLSelectElement).value).toBe(analysisId);
    });
  });
});