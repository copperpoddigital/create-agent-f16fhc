import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../../utils/test-utils';
import FieldMapping from './FieldMapping';
import { FieldMapping as FieldMappingType } from '../../../types/data-source.types';
import { describe, it, expect, vi } from 'vitest';

/**
 * Helper function to set up the component for testing
 */
const setup = (props: Partial<React.ComponentProps<typeof FieldMapping>> = {}) => {
  // Default source fields
  const defaultSourceFields = ['field1', 'field2', 'field3', 'field4', 'field5', 'field6'];
  
  // Default field mapping
  const defaultFieldMapping: FieldMappingType = {
    freight_charge: 'field1',
    currency: 'field2',
    origin: 'field3',
    destination: 'field4',
    date_time: 'field5',
    carrier: null,
    mode: null,
    service_level: null
  };
  
  // Mock onChange handler
  const onChange = vi.fn();
  
  // Merge default props with provided props
  const mergedProps = {
    sourceFields: defaultSourceFields,
    value: defaultFieldMapping,
    onChange,
    ...props
  };
  
  // Render the component
  const utils = render(<FieldMapping {...mergedProps} />);
  
  return {
    ...utils,
    props: mergedProps,
    onChange
  };
};

describe('FieldMapping component', () => {
  it('renders correctly with required props', () => {
    setup();
    
    // Check that the component renders with the correct heading
    expect(screen.getByText('Field Mapping')).toBeInTheDocument();
    
    // Verify that all required field selects are rendered
    expect(screen.getByLabelText('Freight Charge')).toBeInTheDocument();
    expect(screen.getByLabelText('Currency')).toBeInTheDocument();
    expect(screen.getByLabelText('Origin')).toBeInTheDocument();
    expect(screen.getByLabelText('Destination')).toBeInTheDocument();
    expect(screen.getByLabelText('Date/Time')).toBeInTheDocument();
    
    // Verify that all optional field selects are rendered
    expect(screen.getByLabelText('Carrier')).toBeInTheDocument();
    expect(screen.getByLabelText('Transport Mode')).toBeInTheDocument();
    expect(screen.getByLabelText('Service Level')).toBeInTheDocument();
  });

  it('displays source fields in dropdown options', () => {
    const sourceFields = ['price', 'currency_code', 'from', 'to', 'date', 'carrier_name'];
    setup({ sourceFields });
    
    // Get the select element
    const currencySelect = screen.getByLabelText('Currency');
    
    // Check that all source fields appear as options in the select
    sourceFields.forEach(field => {
      const option = Array.from(currencySelect.querySelectorAll('option')).find(
        opt => opt.textContent === field
      );
      expect(option).toBeInTheDocument();
    });
  });

  it('calls onChange when a field mapping is changed', () => {
    const { onChange } = setup();
    
    // Select a different value for currency
    const currencySelect = screen.getByLabelText('Currency');
    fireEvent.change(currencySelect, { target: { value: 'field6' } });
    
    // Check that onChange was called with the updated mapping
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith({
      freight_charge: 'field1',
      currency: 'field6', // Changed from field2 to field6
      origin: 'field3',
      destination: 'field4',
      date_time: 'field5',
      carrier: null,
      mode: null,
      service_level: null
    });
  });

  it('updates the UI when value prop changes', async () => {
    const { rerender, props } = setup();
    
    // Initial values should be set
    expect(screen.getByLabelText('Currency')).toHaveValue('field2');
    
    // Create new field mapping
    const newFieldMapping: FieldMappingType = {
      freight_charge: 'field2',
      currency: 'field3',
      origin: 'field4',
      destination: 'field5',
      date_time: 'field1',
      carrier: 'field6',
      mode: null,
      service_level: null
    };
    
    // Re-render with new value
    rerender(
      <FieldMapping 
        {...props}
        value={newFieldMapping}
      />
    );
    
    // Wait for the component to update
    await waitFor(() => {
      expect(screen.getByLabelText('Freight Charge')).toHaveValue('field2');
      expect(screen.getByLabelText('Currency')).toHaveValue('field3');
      expect(screen.getByLabelText('Carrier')).toHaveValue('field6');
    });
  });

  it('applies validation styling when isValid/isInvalid props are set', () => {
    const { rerender, props } = setup({ isValid: true });
    
    // Check for valid styling
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
      expect(group).toHaveClass('is-valid');
    });
    
    // Re-render with isInvalid=true and a validation message
    rerender(
      <FieldMapping 
        {...props}
        isValid={false}
        isInvalid={true}
        validationMessage="Please map all required fields"
      />
    );
    
    // Check for invalid styling
    formGroups.forEach(group => {
      expect(group).toHaveClass('is-invalid');
    });
    
    // Should show validation message
    expect(screen.getByText('Please map all required fields')).toBeInTheDocument();
  });

  it('handles empty source fields gracefully', () => {
    setup({ sourceFields: [] });
    
    // Should still render the selects
    const selects = screen.getAllByRole('combobox');
    
    // Should have 8 select elements (5 required + 3 optional)
    expect(selects.length).toBe(8);
    
    // Each select should have minimal options (empty option for optional fields)
    const optionalSelects = [
      screen.getByLabelText('Carrier'),
      screen.getByLabelText('Transport Mode'),
      screen.getByLabelText('Service Level')
    ];
    
    optionalSelects.forEach(select => {
      expect(select.querySelectorAll('option').length).toBe(1);
      expect(select.querySelector('option')?.textContent).toBe('-- None --');
    });
  });
});