import React, { useState, useEffect } from 'react'; // ^18.2.0
import Checkbox from '../../common/Checkbox';
import Select from '../../common/Select';
import FormGroup from '../../common/FormGroup';
import { OutputFormat, TrendDirection } from '../../../types/analysis.types';

/**
 * Props interface for the AnalysisOptions component
 */
interface AnalysisOptionsProps {
  /** Whether to calculate absolute price change */
  calculateAbsoluteChange: boolean;
  /** Whether to calculate percentage price change */
  calculatePercentageChange: boolean;
  /** Whether to identify trend direction (increasing, decreasing, stable) */
  identifyTrendDirection: boolean;
  /** Whether to compare results to a historical baseline period */
  compareToHistoricalBaseline: boolean;
  /** ID of the selected baseline period for comparison */
  baselinePeriodId: string | null;
  /** Selected output format for analysis results */
  outputFormat: OutputFormat;
  /** Whether to include visualization in the results */
  includeVisualization: boolean;
  /** Whether to show the baseline period selection UI */
  showBaselinePeriod: boolean;
  /** Callback when absolute change calculation option changes */
  onCalculateAbsoluteChange: (checked: boolean) => void;
  /** Callback when percentage change calculation option changes */
  onCalculatePercentageChange: (checked: boolean) => void;
  /** Callback when trend direction identification option changes */
  onIdentifyTrendDirection: (checked: boolean) => void;
  /** Callback when historical baseline comparison option changes */
  onCompareToHistoricalBaseline: (e: React.ChangeEvent<HTMLInputElement>) => void;
  /** Callback when baseline period selection changes */
  onBaselinePeriodSelect: (id: string) => void;
  /** Callback when output format selection changes */
  onOutputFormatChange: (format: OutputFormat) => void;
  /** Callback when visualization inclusion option changes */
  onIncludeVisualization: (checked: boolean) => void;
  /** Validation errors for form fields */
  errors?: Record<string, string>;
  /** Tracks which form fields have been touched/modified */
  touched?: Record<string, boolean>;
}

/**
 * Component for configuring analysis calculation options, comparison settings, and output preferences
 */
const AnalysisOptions: React.FC<AnalysisOptionsProps> = ({
  calculateAbsoluteChange,
  calculatePercentageChange,
  identifyTrendDirection,
  compareToHistoricalBaseline,
  baselinePeriodId,
  outputFormat,
  includeVisualization,
  showBaselinePeriod,
  onCalculateAbsoluteChange,
  onCalculatePercentageChange,
  onIdentifyTrendDirection,
  onCompareToHistoricalBaseline,
  onBaselinePeriodSelect,
  onOutputFormatChange,
  onIncludeVisualization,
  errors = {},
  touched = {},
}) => {
  // Update UI when compareToHistoricalBaseline changes
  useEffect(() => {
    // This effect handles UI updates based on baseline comparison selection
    // Additional UI logic can be implemented here if needed
  }, [compareToHistoricalBaseline, showBaselinePeriod]);

  /**
   * Handles changes to the output format selection
   */
  const handleOutputFormatChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const format = e.target.value as OutputFormat;
    onOutputFormatChange(format);
  };

  /**
   * Handles changes to the baseline period selection
   */
  const handleBaselinePeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const periodId = e.target.value;
    onBaselinePeriodSelect(periodId);
  };

  return (
    <div className="analysis-options">
      <h4>Calculation Options</h4>
      
      <div className="option-group">
        <Checkbox
          id="calculateAbsoluteChange"
          label="Calculate absolute change"
          checked={calculateAbsoluteChange}
          onChange={(e) => onCalculateAbsoluteChange(e.target.checked)}
        />
        
        <Checkbox
          id="calculatePercentageChange"
          label="Calculate percentage change"
          checked={calculatePercentageChange}
          onChange={(e) => onCalculatePercentageChange(e.target.checked)}
        />
        
        <Checkbox
          id="identifyTrendDirection"
          label="Identify trend direction"
          checked={identifyTrendDirection}
          onChange={(e) => onIdentifyTrendDirection(e.target.checked)}
        />
        
        <Checkbox
          id="compareToHistoricalBaseline"
          label="Compare to historical baseline"
          checked={compareToHistoricalBaseline}
          onChange={onCompareToHistoricalBaseline}
          isInvalid={Boolean(errors.baselinePeriodId && touched.baselinePeriodId)}
          validationMessage={errors.baselinePeriodId}
        />
      </div>
      
      {showBaselinePeriod && (
        <div className="baseline-period-selection">
          <FormGroup
            label="Baseline period"
            required={compareToHistoricalBaseline}
            isInvalid={Boolean(errors.baselinePeriodId && touched.baselinePeriodId)}
            validationMessage={errors.baselinePeriodId}
          >
            <Select
              id="baselinePeriodId"
              name="baselinePeriodId"
              value={baselinePeriodId || ''}
              onChange={handleBaselinePeriodChange}
              placeholder="Select baseline period"
              options={[]} // Would be populated with available time periods from parent component
            />
          </FormGroup>
        </div>
      )}
      
      <h4>Output Options</h4>
      <div className="option-group">
        <FormGroup
          label="Output Format"
          required={true}
        >
          <Select
            id="outputFormat"
            name="outputFormat"
            value={outputFormat}
            onChange={handleOutputFormatChange}
            options={[
              { value: OutputFormat.JSON, label: 'JSON' },
              { value: OutputFormat.CSV, label: 'CSV' },
              { value: OutputFormat.TEXT, label: 'Text Summary' }
            ]}
          />
        </FormGroup>
        
        <Checkbox
          id="includeVisualization"
          label="Include visualization"
          checked={includeVisualization}
          onChange={(e) => onIncludeVisualization(e.target.checked)}
        />
      </div>
    </div>
  );
};

export default AnalysisOptions;