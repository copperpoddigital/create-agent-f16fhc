import React, { useState } from 'react'; // ^18.2.0
import { useNavigate } from 'react-router-dom'; // ^6.10.0

import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import AnalysisForm, { AnalysisFormValues } from '../../components/forms/AnalysisForm';
import Button from '../../components/common/Button';
import useAlert from '../../hooks/useAlert';
import { ROUTES } from '../../config/routes';

/**
 * Page component for creating a new freight price movement analysis
 */
const NewAnalysisPage: React.FC = () => {
  // LD1: Initialize loading state with useState(false)
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // LD1: Get navigation function using useNavigate hook
  const navigate = useNavigate();

  // LD1: Get alert functions using useAlert hook
  const { showSuccess, showError } = useAlert();

  // LD1: Define handleSubmit function to handle form submission
  const handleSubmit = async (values: AnalysisFormValues) => {
    // S1: Set isLoading to true
    setIsLoading(true);
    try {
      // S1: Show success alert for analysis creation
      showSuccess('Analysis created successfully!');

      // S1: Navigate to analysis results page with the new analysis ID
      // TODO: Replace 'new-analysis-id' with the actual ID from the API response
      navigate(ROUTES.ANALYSIS_RESULTS.path.replace(':id', 'new-analysis-id'));
    } catch (error) {
      // S1: Handle any errors by showing error alert
      console.error('Error creating analysis:', error);
      showError('Failed to create analysis. Please try again.');
    } finally {
      // S1: Set isLoading to false
      setIsLoading(false);
    }
  };

  // LD1: Define handleCancel function to navigate back to analysis list
  const handleCancel = () => {
    // S1: Navigate back to analysis list page
    navigate(ROUTES.ANALYSIS.path);
  };

  // LD1: Render the page with MainLayout, PageHeader, and AnalysisForm components
  return (
    <MainLayout>
      <PageHeader
        title="New Analysis"
        actions={[
          // IE1: Button component imported from '../../components/common/Button'
          // S1: Button component used for cancel action
          <Button key="cancel" variant="secondary" onClick={handleCancel} disabled={isLoading}>
            Cancel
          </Button>,
        ]}
      />
      <div className="page-content">
        {/* IE1: AnalysisForm component imported from '../../components/forms/AnalysisForm' */}
        {/* S1: AnalysisForm component used for configuring analysis parameters */}
        <AnalysisForm onSubmit={handleSubmit} onCancel={handleCancel} isLoading={isLoading} />
      </div>
    </MainLayout>
  );
};

// IE3: Export the NewAnalysisPage component as the default export
export default NewAnalysisPage;