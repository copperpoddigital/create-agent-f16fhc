import React, { useState, useCallback, useEffect } from 'react'; // v18.2.0
import TimePeriodSelector from '../../analysis/TimePeriodSelector';
import DataFilterSelector from '../../analysis/DataFilterSelector';
import AnalysisOptions from '../../analysis/AnalysisOptions';
import Button from '../../common/Button';
import FormGroup from '../../common/FormGroup';
import Input from '../../common/Input';
import useForm from '../../../hooks/useForm';
import useAlert from '../../../hooks/useAlert';
import { 
  createTimePeriod, 
  createAnalysisRequest 
} from '../../../api/analysis-api';
import { 
  TimeGranularity, 
  OutputFormat,
  AnalysisRequestCreateParams,
  TimePeriodCreateParams,
  DataFilter
} from '../../../types/analysis.types';

/**
 * Interface for the form values
 */
interface AnalysisFormValues {
  name: string;
  description: string;
  timePeriodId: string;
  startDate: string;
  endDate: string;
  granularity: TimeGranularity;
  customInterval: string;
  dataSourceIds: string[] | null;
  origins: string[] | null;
  destinations: string[] | null;
  carriers: string[] | null;
  transportModes: string[] | null;
  currency: string | null;
  calculateAbsoluteChange: boolean;
  calculatePercentageChange: boolean;
  identifyTrendDirection: boolean;
  compareToHistoricalBaseline: boolean;
  baselinePeriodId: string | null;
  includeAggregates: boolean;
  outputFormat: OutputFormat;
  includeVisualization: boolean;
}

/**
 * Props interface for the AnalysisForm component
 */
interface AnalysisFormProps {
  initialValues?: Partial<AnalysisFormValues>;
  onSubmit: (values: AnalysisFormValues) => void;
  onCancel: () => void;
  isEdit?: boolean;
  isLoading?: boolean;
}

/**
 * A form component for creating and configuring freight price movement analysis
 */
const AnalysisForm: React.FC<AnalysisFormProps> = ({ 
  initialValues = {}, 
  onSubmit, 
  onCancel, 
  isEdit = false,
  isLoading = false
}) => {
  // Define default values for the form
  const defaultValues: AnalysisFormValues = {
    name: '',
    description: '',
    timePeriodId: '',
    startDate: '',
    endDate: '',
    granularity: TimeGranularity.WEEKLY,
    customInterval: '',
    dataSourceIds: null,
    origins: null,
    destinations: null,
    carriers: null,
    transportModes: null,
    currency: null,
    calculateAbsoluteChange: true,
    calculatePercentageChange: true,
    identifyTrendDirection: true,
    compareToHistoricalBaseline: false,
    baselinePeriodId: null,
    includeAggregates: false,
    outputFormat: OutputFormat.JSON,
    includeVisualization: true
  };

  // State for managing the visibility of the baseline period selection
  const [showBaselinePeriod, setShowBaselinePeriod] = useState<boolean>(false);

  // State for tracking whether a time period is being created
  const [isCreatingTimePeriod, setIsCreatingTimePeriod] = useState<boolean>(false);

  // State for tracking whether the form is being submitted
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Use the useForm hook to manage form state and validation
  const { 
    values, 
    errors, 
    touched, 
    isSubmitting: formIsSubmitting,
    handleChange, 
    handleBlur, 
    setFieldValue,
    setFieldTouched,
    validateField,
    validateForm: validateAnalysisForm, 
    resetForm, 
    handleSubmit 
  } = useForm<AnalysisFormValues>({
    initialValues: defaultValues,
    validate: validateAnalysisFormFn,
    onSubmit: handleFormSubmit
  });

  // Use the useAlert hook to display alert notifications
  const { showAlert } = useAlert();

  // Update showBaselinePeriod when compareToHistoricalBaseline changes
  useEffect(() => {
    setShowBaselinePeriod(values.compareToHistoricalBaseline);
  }, [values.compareToHistoricalBaseline]);

  /**
   * Validates the analysis form values
   * @param values - The form values to validate
   * @returns An object containing validation errors
   */
  async function validateAnalysisFormFn(values: AnalysisFormValues): Promise<Record<string, string>> {
    const errors: Record<string, string> = {};

    // Validate name field (required)
    if (!values.name) {
      errors.name = 'Analysis name is required';
    }

    // Validate time period selection (either timePeriodId or startDate/endDate/granularity required)
    if (!values.timePeriodId && (!values.startDate || !values.endDate || !values.granularity)) {
      errors.timePeriod = 'Time period or start date, end date, and granularity are required';
    }

    // Validate custom interval if granularity is CUSTOM
    if (values.granularity === TimeGranularity.CUSTOM && !values.customInterval) {
      errors.customInterval = 'Custom interval is required when granularity is set to Custom';
    }

    // Validate baseline period if compareToHistoricalBaseline is true
    if (values.compareToHistoricalBaseline && !values.baselinePeriodId) {
      errors.baselinePeriodId = 'Baseline period is required when comparing to historical baseline';
    }

    // Validate that at least one calculation option is selected
    if (!values.calculateAbsoluteChange && !values.calculatePercentageChange && !values.identifyTrendDirection) {
      errors.calculationOptions = 'At least one calculation option must be selected';
    }

    return errors;
  }

  /**
   * Handles form submission
   * @param values - The form values to submit
   * @param formHelpers - The form helpers provided by useForm
   */
  async function handleFormSubmit(values: AnalysisFormValues, formHelpers: any): Promise<void> {
    setIsSubmitting(true);
    formHelpers.setSubmitting(true);

    try {
      let timePeriodId = values.timePeriodId;

      // If custom time period is selected, create a new time period
      if (!timePeriodId && values.startDate && values.endDate && values.granularity) {
        try {
          timePeriodId = await handleTimePeriodCreate(values);
        } catch (error) {
          console.error('Error creating time period:', error);
          showAlert('error', 'Failed to create time period. Please check your input and try again.');
          formHelpers.setSubmitting(false);
          setIsSubmitting(false);
          return;
        }
      }

      // Prepare analysis request parameters
      const analysisRequestParams: AnalysisRequestCreateParams = {
        name: values.name,
        description: values.description,
        time_period_id: timePeriodId,
        data_source_ids: values.dataSourceIds || [],
        filters: [] as DataFilter[], // Implement data filter mapping if needed
        options: {
          calculate_absolute_change: values.calculateAbsoluteChange,
          calculate_percentage_change: values.calculatePercentageChange,
          identify_trend_direction: values.identifyTrendDirection,
          compare_to_baseline: values.compareToHistoricalBaseline,
          baseline_period_id: values.baselinePeriodId,
          include_aggregates: values.includeAggregates,
          output_format: values.outputFormat,
          include_visualization: values.includeVisualization
        }
      };

      // Call createAnalysisRequest API function
      await createAnalysisRequest(analysisRequestParams);

      // Call onSubmit callback with form values
      onSubmit(values);
    } catch (error) {
      console.error('Error submitting analysis request:', error);
      showAlert('error', 'Failed to submit analysis request. Please try again later.');
    } finally {
      formHelpers.setSubmitting(false);
      setIsSubmitting(false);
    }
  }

  /**
   * Creates a new time period
   * @param values - The form values containing time period information
   * @returns The ID of the created time period
   */
  async function handleTimePeriodCreate(values: AnalysisFormValues): Promise<string> {
    setIsCreatingTimePeriod(true);

    try {
      // Prepare time period creation parameters
      const timePeriodParams: TimePeriodCreateParams = {
        name: values.name,
        start_date: values.startDate,
        end_date: values.endDate,
        granularity: values.granularity,
        custom_interval: values.customInterval
      };

      // Call createTimePeriod API function
      const response = await createTimePeriod(timePeriodParams);

      if (response?.data?.id) {
        return response.data.id;
      } else {
        throw new Error('Failed to create time period: ' + response?.error?.message);
      }
    } catch (error) {
      console.error('Error creating time period:', error);
      showAlert('error', 'Failed to create time period. Please check your input and try again.');
      throw error; // Re-throw the error to be caught by the parent function
    } finally {
      setIsCreatingTimePeriod(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="analysis-form">
      <section className="form-section">
        <h3>Analysis Details</h3>
        <FormGroup 
          label="Analysis Name" 
          required 
          isInvalid={Boolean(errors.name && touched.name)}
          validationMessage={errors.name}
        >
          <Input 
            id="name" 
            name="name" 
            value={values.name || ''} 
            onChange={handleChange} 
            onBlur={handleBlur}
            placeholder="Enter analysis name" 
          />
        </FormGroup>
        <FormGroup 
          label="Description"
          isInvalid={Boolean(errors.description && touched.description)}
          validationMessage={errors.description}
        >
          <Input 
            id="description" 
            name="description" 
            value={values.description || ''} 
            onChange={handleChange} 
            onBlur={handleBlur}
            placeholder="Enter analysis description" 
            type="textarea"
          />
        </FormGroup>
      </section>

      <section className="form-section">
        <h3>Time Period Selection</h3>
        <TimePeriodSelector
          selectedPeriodId={values.timePeriodId}
          startDate={values.startDate}
          endDate={values.endDate}
          granularity={values.granularity}
          customInterval={values.customInterval}
          onPeriodSelect={(id) => setFieldValue('timePeriodId', id)}
          onStartDateChange={(date) => setFieldValue('startDate', date)}
          onEndDateChange={(date) => setFieldValue('endDate', date)}
          onGranularityChange={(e) => setFieldValue('granularity', e.target.value as TimeGranularity)}
          onCustomIntervalChange={(value) => setFieldValue('customInterval', value)}
          errors={errors}
          touched={touched}
        />
      </section>

      <section className="form-section">
        <h3>Data Filters</h3>
        <DataFilterSelector
          dataSourceIds={values.dataSourceIds}
          origins={values.origins}
          destinations={values.destinations}
          carriers={values.carriers}
          transportModes={values.transportModes}
          currency={values.currency}
          onDataSourcesChange={(ids) => setFieldValue('dataSourceIds', ids)}
          onOriginsChange={(origins) => setFieldValue('origins', origins)}
          onDestinationsChange={(destinations) => setFieldValue('destinations', destinations)}
          onCarriersChange={(carriers) => setFieldValue('carriers', carriers)}
          onTransportModesChange={(modes) => setFieldValue('transportModes', modes)}
          onCurrencyChange={(currency) => setFieldValue('currency', currency)}
          errors={errors}
          touched={touched}
        />
      </section>

      <section className="form-section">
        <h3>Analysis Options</h3>
        <AnalysisOptions
          calculateAbsoluteChange={values.calculateAbsoluteChange}
          calculatePercentageChange={values.calculatePercentageChange}
          identifyTrendDirection={values.identifyTrendDirection}
          compareToHistoricalBaseline={values.compareToHistoricalBaseline}
          baselinePeriodId={values.baselinePeriodId}
          includeAggregates={values.includeAggregates}
          outputFormat={values.outputFormat}
          includeVisualization={values.includeVisualization}
          onCalculateAbsoluteChange={(checked) => setFieldValue('calculateAbsoluteChange', checked)}
          onCalculatePercentageChange={(checked) => setFieldValue('calculatePercentageChange', checked)}
          onIdentifyTrendDirection={(checked) => setFieldValue('identifyTrendDirection', checked)}
          onCompareToHistoricalBaseline={(e) => setFieldValue('compareToHistoricalBaseline', e.target.checked)}
          onBaselinePeriodSelect={(id) => setFieldValue('baselinePeriodId', id)}
          onIncludeAggregates={(checked) => setFieldValue('includeAggregates', checked)}
          onOutputFormatChange={(format) => setFieldValue('outputFormat', format as OutputFormat)}
          onIncludeVisualization={(checked) => setFieldValue('includeVisualization', checked)}
          showBaselinePeriod={showBaselinePeriod}
          errors={errors}
          touched={touched}
        />
      </section>

      <div className="form-actions">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isSubmitting || isLoading}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" isLoading={isSubmitting || isCreatingTimePeriod || isLoading} disabled={isSubmitting || isCreatingTimePeriod || isLoading}>
          {isEdit ? 'Update Analysis' : 'Create Analysis'}
        </Button>
      </div>
    </form>
  );
};

export default AnalysisForm;