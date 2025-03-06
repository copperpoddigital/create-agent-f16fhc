import React, { useState, useEffect, useCallback } from 'react';
import DatePicker from '../../common/DatePicker';
import RadioButton from '../../common/RadioButton';
import FormGroup from '../../common/FormGroup';
import Input from '../../common/Input';
import Select from '../../common/Select';
import { TimeGranularity } from '../../../types/analysis.types';
import { formatDate, isValidDate } from '../../../utils/date-utils';
import { DATE_FORMATS } from '../../../config/constants';
import useApi from '../../../hooks/useApi';

/**
 * Props interface for the TimePeriodSelector component
 */
interface TimePeriodSelectorProps {
  selectedPeriodId: string | null;
  startDate: string | null;
  endDate: string | null;
  granularity: TimeGranularity;
  customInterval: string | null;
  onPeriodSelect: (id: string) => void;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onGranularityChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onCustomIntervalChange: (value: string) => void;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
}

/**
 * A component for selecting time periods for freight price movement analysis.
 * It allows users to either choose from existing saved time periods or create
 * a custom time period by specifying start date, end date, and granularity.
 */
const TimePeriodSelector: React.FC<TimePeriodSelectorProps> = ({
  selectedPeriodId,
  startDate,
  endDate,
  granularity,
  customInterval,
  onPeriodSelect,
  onStartDateChange,
  onEndDateChange,
  onGranularityChange,
  onCustomIntervalChange,
  errors = {},
  touched = {},
}) => {
  // State for tracking whether to use a saved period or create a custom one
  const [useCustomPeriod, setUseCustomPeriod] = useState<boolean>(!selectedPeriodId);
  
  // State for showing custom interval input when granularity is CUSTOM
  const [showCustomInterval, setShowCustomInterval] = useState<boolean>(granularity === TimeGranularity.CUSTOM);
  
  // State for storing saved time periods fetched from API
  const [savedPeriods, setSavedPeriods] = useState<Array<{ id: string; name: string }>>([]);
  
  // Setup API hook for fetching saved periods
  const { get, isLoading: isLoadingPeriods } = useApi();

  // Fetch saved time periods on component mount
  const fetchSavedPeriods = async () => {
    try {
      const response = await get('/api/v1/analysis/time-periods');
      if (response?.success && Array.isArray(response.data)) {
        setSavedPeriods(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch saved time periods:', error);
    }
  };

  useEffect(() => {
    fetchSavedPeriods();
  }, []);

  // Update showCustomInterval when granularity changes
  useEffect(() => {
    setShowCustomInterval(granularity === TimeGranularity.CUSTOM);
  }, [granularity]);

  // Update useCustomPeriod when selectedPeriodId changes
  useEffect(() => {
    setUseCustomPeriod(!selectedPeriodId);
  }, [selectedPeriodId]);

  // Handle change between saved and custom period types
  const handlePeriodTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const useCustom = e.target.value === 'custom';
    setUseCustomPeriod(useCustom);
    
    // If switching to saved period and there are saved periods, select the first one
    if (!useCustom && savedPeriods.length > 0 && !selectedPeriodId) {
      onPeriodSelect(savedPeriods[0].id);
    }
    
    // If switching to custom period, clear the selected period ID
    if (useCustom && selectedPeriodId) {
      onPeriodSelect('');
    }
  };

  // Handle selection of a saved time period
  const handleSavedPeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const periodId = e.target.value;
    onPeriodSelect(periodId);
  };

  return (
    <div className="time-period-selector">
      <div className="period-type-selection">
        <RadioButton
          id="period-type-saved"
          name="period-type"
          value="saved"
          label="Use Saved Period"
          checked={!useCustomPeriod}
          onChange={handlePeriodTypeChange}
        />
        <RadioButton
          id="period-type-custom"
          name="period-type"
          value="custom"
          label="Create Custom Period"
          checked={useCustomPeriod}
          onChange={handlePeriodTypeChange}
        />
      </div>

      <div className="period-selection-content">
        {!useCustomPeriod ? (
          <FormGroup
            id="saved-period"
            label="Select Time Period"
            isInvalid={Boolean(errors.timePeriodId && touched.timePeriodId)}
            validationMessage={errors.timePeriodId}
          >
            <Select
              id="saved-period"
              value={selectedPeriodId || ''}
              onChange={handleSavedPeriodChange}
              isLoading={isLoadingPeriods}
              placeholder="Select a saved time period"
              options={savedPeriods.map(period => ({ 
                value: period.id, 
                label: period.name 
              }))}
            />
          </FormGroup>
        ) : (
          <div className="custom-period-inputs">
            <FormGroup
              id="start-date"
              label="Start Date"
              required
              isInvalid={Boolean(errors.startDate && touched.startDate)}
              validationMessage={errors.startDate}
            >
              <DatePicker
                id="start-date"
                value={startDate ? new Date(startDate) : null}
                onChange={(date) => onStartDateChange(date ? formatDate(date, DATE_FORMATS.YYYY_MM_DD) : '')}
                placeholder="Select start date"
                format={DATE_FORMATS.MM_DD_YYYY}
                maxDate={endDate ? new Date(endDate) : undefined}
              />
            </FormGroup>

            <FormGroup
              id="end-date"
              label="End Date"
              required
              isInvalid={Boolean(errors.endDate && touched.endDate)}
              validationMessage={errors.endDate}
            >
              <DatePicker
                id="end-date"
                value={endDate ? new Date(endDate) : null}
                onChange={(date) => onEndDateChange(date ? formatDate(date, DATE_FORMATS.YYYY_MM_DD) : '')}
                placeholder="Select end date"
                format={DATE_FORMATS.MM_DD_YYYY}
                minDate={startDate ? new Date(startDate) : undefined}
              />
            </FormGroup>

            <FormGroup
              id="granularity"
              label="Granularity"
              required
              isInvalid={Boolean(errors.granularity && touched.granularity)}
              validationMessage={errors.granularity}
            >
              <div className="granularity-options">
                <RadioButton
                  id="granularity-daily"
                  name="granularity"
                  value={TimeGranularity.DAILY}
                  label="Daily"
                  checked={granularity === TimeGranularity.DAILY}
                  onChange={onGranularityChange}
                />
                <RadioButton
                  id="granularity-weekly"
                  name="granularity"
                  value={TimeGranularity.WEEKLY}
                  label="Weekly"
                  checked={granularity === TimeGranularity.WEEKLY}
                  onChange={onGranularityChange}
                />
                <RadioButton
                  id="granularity-monthly"
                  name="granularity"
                  value={TimeGranularity.MONTHLY}
                  label="Monthly"
                  checked={granularity === TimeGranularity.MONTHLY}
                  onChange={onGranularityChange}
                />
                <RadioButton
                  id="granularity-custom"
                  name="granularity"
                  value={TimeGranularity.CUSTOM}
                  label="Custom"
                  checked={granularity === TimeGranularity.CUSTOM}
                  onChange={onGranularityChange}
                />
              </div>
            </FormGroup>

            {showCustomInterval && (
              <FormGroup
                id="custom-interval"
                label="Custom Interval (days)"
                required
                isInvalid={Boolean(errors.customInterval && touched.customInterval)}
                validationMessage={errors.customInterval}
                helpText="Enter the number of days for each interval"
              >
                <Input
                  id="custom-interval"
                  type="number"
                  min="1"
                  value={customInterval || ''}
                  onChange={(e) => onCustomIntervalChange(e.target.value)}
                  placeholder="Enter interval in days"
                />
              </FormGroup>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TimePeriodSelector;