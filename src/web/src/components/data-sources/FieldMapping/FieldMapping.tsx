import React, { useState, useEffect } from 'react';
import FormGroup from '../../common/FormGroup';
import Select from '../../common/Select';
import { FieldMapping as FieldMappingType } from '../../../types/data-source.types';

/**
 * Props interface for the FieldMapping component
 */
interface FieldMappingProps {
  /** Current field mapping values */
  value: FieldMappingType;
  /** Available source fields from the data source */
  sourceFields: string[];
  /** Callback function called when mapping changes */
  onChange: (mapping: FieldMappingType) => void;
  /** Whether the field mapping is valid */
  isValid?: boolean;
  /** Whether the field mapping is invalid */
  isInvalid?: boolean;
  /** Validation message to display */
  validationMessage?: string;
}

/**
 * A component for mapping source data fields to standardized freight data fields
 * 
 * This component allows users to select which columns from their data source 
 * correspond to required freight data fields like freight charge, currency,
 * origin, destination, and date/time.
 */
const FieldMapping: React.FC<FieldMappingProps> = ({
  value,
  sourceFields,
  onChange,
  isValid = false,
  isInvalid = false,
  validationMessage,
}) => {
  // State to track current mapping
  const [mapping, setMapping] = useState<FieldMappingType>({ ...value });

  // Update internal state when props change
  useEffect(() => {
    setMapping({ ...value });
  }, [value]);

  /**
   * Handles changes to field mapping selections
   * 
   * @param field - The field being mapped (e.g., 'freight_charge')
   * @param event - The change event from the select input
   */
  const handleFieldChange = (field: string, event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = event.target.value;
    
    // For required fields, always use the selected value
    // For optional fields, use null if the value is empty
    const newValue = selectedValue === '' 
      ? (field === 'carrier' || field === 'mode' || field === 'service_level' ? null : '') 
      : selectedValue;
    
    const newMapping = {
      ...mapping,
      [field]: newValue,
    };
    
    setMapping(newMapping);
    onChange(newMapping);
  };

  /**
   * Renders a select dropdown for a specific field mapping
   * 
   * @param field - The field to map (e.g., 'freight_charge')
   * @param label - Display label for the field
   * @param required - Whether this is a required field
   * @returns A select input wrapped in a FormGroup
   */
  const renderFieldSelect = (field: string, label: string, required: boolean) => {
    const currentValue = mapping[field as keyof FieldMappingType];
    
    // Create options from sourceFields
    const options = sourceFields.map(fieldName => ({
      value: fieldName,
      label: fieldName,
    }));

    // Add empty option for optional fields
    if (!required) {
      options.unshift({ value: '', label: '-- None --' });
    }

    return (
      <FormGroup
        label={label}
        required={required}
        isValid={isValid}
        isInvalid={isInvalid}
      >
        <Select
          value={currentValue === null ? '' : currentValue}
          options={options}
          placeholder="Select field"
          onChange={(e) => handleFieldChange(field, e)}
          required={required}
        />
      </FormGroup>
    );
  };

  return (
    <div className="field-mapping-container">
      <h4>Field Mapping</h4>
      <p>Map your source data fields to the required freight data fields</p>
      
      <div className="required-fields">
        <h5>Required Fields</h5>
        {renderFieldSelect('freight_charge', 'Freight Charge', true)}
        {renderFieldSelect('currency', 'Currency', true)}
        {renderFieldSelect('origin', 'Origin', true)}
        {renderFieldSelect('destination', 'Destination', true)}
        {renderFieldSelect('date_time', 'Date/Time', true)}
      </div>
      
      <div className="optional-fields">
        <h5>Optional Fields</h5>
        {renderFieldSelect('carrier', 'Carrier', false)}
        {renderFieldSelect('mode', 'Transport Mode', false)}
        {renderFieldSelect('service_level', 'Service Level', false)}
      </div>
      
      {validationMessage && isInvalid && (
        <div className="validation-message error">{validationMessage}</div>
      )}
    </div>
  );
};

export default FieldMapping;