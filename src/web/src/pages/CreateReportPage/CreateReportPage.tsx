import React, { useState, useEffect } from 'react'; // ^18.2.0
import { useNavigate, useLocation } from 'react-router-dom'; // version specified in the documentation
import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import ReportForm from '../../components/forms/ReportForm';
import Button from '../../components/common/Button';
import Spinner from '../../components/common/Spinner';
import useAlert from '../../hooks/useAlert';
import { ROUTES } from '../../config/routes';
import { Report } from '../../types/report.types';

/**
 * Page component for creating new reports based on analysis results
 * This page allows users to select an analysis result and configure report settings such as name, description, output format, and visualization options.
 */
const CreateReportPage: React.FC = () => {
  // Initialize navigate function using useNavigate hook
  const navigate = useNavigate();

  // Initialize location object using useLocation hook
  const location = useLocation();

  // Extract analysisId from location.search query parameters if present
  const analysisId = new URLSearchParams(location.search).get('analysisId');

  // Initialize loading state with useState(false)
  const [loading, setLoading] = useState<boolean>(false);

  // Get showAlert function from useAlert hook
  const { showAlert } = useAlert();

  /**
   * Define handleSubmit function to handle successful form submission
   * @param report The created report object
   */
  const handleSubmit = (report: Report) => {
    showAlert('success', 'Report created successfully!');
    navigate(`${ROUTES.REPORTS.path}/${report.id}`);
  };

  /**
   * Define handleCancel function to navigate back to reports page
   */
  const handleCancel = () => {
    navigate(ROUTES.REPORTS.path);
  };

  // Render the page with MainLayout, PageHeader, and ReportForm components
  return (
    <MainLayout>
      <PageHeader
        title="Create Report"
        actions={[
          <Button variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>,
        ]}
      />
      {loading ? (
        <Spinner />
      ) : (
        <ReportForm
          report={null}
          analysisId={analysisId || null}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      )}
    </MainLayout>
  );
};

export default CreateReportPage;