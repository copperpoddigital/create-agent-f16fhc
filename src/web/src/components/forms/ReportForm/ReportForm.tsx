import React, { useState, useEffect } from 'react';
import FormGroup from '../../common/FormGroup';
import Input from '../../common/Input';
import Select from '../../common/Select';
import Checkbox from '../../common/Checkbox';
import Button from '../../common/Button';
import useForm from '../../../hooks/useForm';
import useAlert from '../../../hooks/useAlert';
import { ReportType, ReportCreateParams, ReportUpdateParams, Report } from '../../../types/report.types';
import { OutputFormat, AnalysisResult } from '../../../types/analysis.types';
import { createReport, updateReport } from '../../../api/report-api';
import { getAnalysisResults } from '../../../api/analysis-api';

/**
 * Props interface for the ReportForm component
 */
interface ReportFormProps {
  /**
   * Existing report for editing mode, null for creation mode
   */
  report: Report | null;
  /**
   * Pre-selected analysis ID when creating from an analysis result
   */
  analysisId: string | null;
  /**
   * Callback function called when form is successfully submitted
   */
  onSubmit: (report: Report) => void;
  /**
   * Callback function called when form is cancelled
   */
  onCancel: () => void;
}

/**
 * Form component for creating and editing reports based on analysis results
 * 
 * This component allows users to specify report details, select an analysis result,
 * configure output format, and manage visualization options.
 */
const ReportForm: React.FC<ReportFormProps> = ({
  report = null,
  analysisId = null,
  onSubmit,
  onCancel
}) => {
  // State management
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  
  // Hooks
  const { showSuccess, showError } = useAlert();
  
  // Initialize form with useForm hook
  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit
  } = useForm({
    initialValues: {
      name: report?.name || '',
      description: report?.description || '',
      type: report?.type || ReportType.STANDARD,
      analysis_id: report?.analysis_id || analysisId || '',
      output_format: report?.output_format || OutputFormat.JSON,
      include_visualization: report?.include_visualization || false
    },
    validate: (values) => {
      const errors: Record<string, string> = {};
      if (!values.name.trim()) {
        errors.name = 'Report name is required';
      }
      if (!values.analysis_id) {
        errors.analysis_id = 'Analysis result is required';
      }
      return errors;
    },
    onSubmit: async (values) => {
      await handleSubmit(values);
    }
  });

  /**
   * Handles form submission
   */
  const handleSubmit = async (values: Record<string, any>) => {
    setIsSubmitting(true);
    try {
      // Create report parameters from form values
      const reportParams: ReportCreateParams | ReportUpdateParams = {
        name: values.name,
        description: values.description,
        type: values.type as ReportType,
        analysis_id: values.analysis_id,
        output_format: values.output_format as OutputFormat,
        include_visualization: values.include_visualization
      };

      let result;
      if (report) {
        // Update existing report
        result = await updateReport(report.id, reportParams as ReportUpdateParams);
        showSuccess('Report updated successfully');
      } else {
        // Create new report
        result = await createReport(reportParams as ReportCreateParams);
        showSuccess('Report created successfully');
      }

      if (result.success && result.data) {
        onSubmit(result.data);
      } else {
        showError(result.error?.message || 'Failed to save report');
      }
    } catch (error) {
      console.error('Error submitting report:', error);
      showError('Failed to save report. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Fetches available analysis results from the API
   */
  const fetchAnalysisResults = async () => {
    setIsLoading(true);
    try {
      // In a production app, we would want a dedicated API endpoint for fetching
      // all available analysis results. For now, we're using the available API function
      // with default pagination parameters.
      const response = await getAnalysisResults(analysisId || '', {
        page: 1,
        pageSize: 100,
        sortBy: 'calculated_at',
        sortDirection: 'desc'
      });
      
      if (response.success && response.data) {
        setAnalysisResults(response.data);
      } else {
        showError(response.error?.message || 'Failed to load analysis results');
      }
    } catch (error) {
      console.error('Error fetching analysis results:', error);
      showError('Failed to load analysis results. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Load analysis results when component mounts
  useEffect(() => {
    fetchAnalysisResults();
  }, []);

  return (
    <form onSubmit={handleSubmit} className="report-form">
      {/* Report Name */}
      <FormGroup
        id="name"
        label="Report Name"
        required
        isInvalid={touched.name && !!errors.name}
        validationMessage={errors.name}
      >
        <Input
          id="name"
          name="name"
          value={values.name}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Enter report name"
          isInvalid={touched.name && !!errors.name}
        />
      </FormGroup>

      {/* Description */}
      <FormGroup
        id="description"
        label="Description"
      >
        <Input
          id="description"
          name="description"
          value={values.description}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Enter report description"
        />
      </FormGroup>

      {/* Analysis Result Selection */}
      <FormGroup
        id="analysis_id"
        label="Analysis Result"
        required
        isInvalid={touched.analysis_id && !!errors.analysis_id}
        validationMessage={errors.analysis_id}
      >
        <Select
          id="analysis_id"
          name="analysis_id"
          value={values.analysis_id}
          onChange={handleChange}
          onBlur={handleBlur}
          options={analysisResults.map(result => ({
            value: result.id,
            label: result.name || `Analysis from ${new Date(result.calculated_at).toLocaleDateString()}`
          }))}
          placeholder="Select an analysis result"
          isInvalid={touched.analysis_id && !!errors.analysis_id}
          disabled={isLoading}
        />
      </FormGroup>

      {/* Output Format */}
      <FormGroup
        id="output_format"
        label="Output Format"
        required
      >
        <Select
          id="output_format"
          name="output_format"
          value={values.output_format}
          onChange={handleChange}
          options={[
            { value: OutputFormat.JSON, label: 'JSON' },
            { value: OutputFormat.CSV, label: 'CSV' },
            { value: OutputFormat.TEXT, label: 'Text Summary' }
          ]}
        />
      </FormGroup>

      {/* Include Visualization */}
      <FormGroup
        id="include_visualization"
      >
        <Checkbox
          id="include_visualization"
          name="include_visualization"
          label="Include visualization"
          checked={values.include_visualization}
          onChange={handleChange}
        />
      </FormGroup>

      {/* Form Actions */}
      <div className="form-actions">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting || isLoading || Object.keys(errors).length > 0}
          isLoading={isSubmitting}
        >
          {report ? 'Update Report' : 'Create Report'}
        </Button>
      </div>
    </form>
  );
};

export default ReportForm;