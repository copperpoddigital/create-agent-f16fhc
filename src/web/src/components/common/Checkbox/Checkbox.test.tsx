import React from 'react';
import Checkbox from './Checkbox';
import { renderWithTheme, screen, fireEvent, userEvent } from '../../../utils/test-utils';

describe('Checkbox Component', () => {
  test('renders with label', () => {
    renderWithTheme(<Checkbox label="Test Checkbox" onChange={() => {}} />);
    expect(screen.getByText('Test Checkbox')).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });

  test('can be checked and unchecked', () => {
    const handleChange = jest.fn();
    renderWithTheme(<Checkbox label="Test Checkbox" onChange={handleChange} />);
    
    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).not.toBeChecked();
    
    fireEvent.click(checkbox);
    expect(handleChange).toHaveBeenCalledTimes(1);
    
    // We're testing the event handler call, not internal state
    // since this is a controlled component, actual checked state
    // would depend on parent component updating the prop
  });

  test('can be disabled', () => {
    const handleChange = jest.fn();
    renderWithTheme(
      <Checkbox 
        label="Disabled Checkbox" 
        disabled={true}
        onChange={handleChange}
      />
    );
    
    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeDisabled();
    
    fireEvent.click(checkbox);
    expect(handleChange).not.toHaveBeenCalled();
  });

  test('displays validation states correctly', () => {
    // Test valid state
    const { rerender } = renderWithTheme(
      <Checkbox 
        label="Valid Checkbox" 
        isValid={true}
        onChange={() => {}}
      />
    );
    
    const container = screen.getByText('Valid Checkbox').closest('.checkbox-container');
    expect(container).toHaveClass('checkbox--valid');
    
    // Test invalid state
    rerender(
      <Checkbox 
        label="Invalid Checkbox" 
        isInvalid={true}
        onChange={() => {}}
      />
    );
    
    const invalidContainer = screen.getByText('Invalid Checkbox').closest('.checkbox-container');
    expect(invalidContainer).toHaveClass('checkbox--invalid');
    
    // Test validation message
    rerender(
      <Checkbox 
        label="Checkbox with validation" 
        isInvalid={true}
        validationMessage="This field is required"
        onChange={() => {}}
      />
    );
    
    expect(screen.getByText('This field is required')).toBeInTheDocument();
    expect(screen.getByText('This field is required').className).toContain('checkbox-validation--error');
  });

  test('is accessible', () => {
    renderWithTheme(
      <Checkbox 
        id="test-checkbox"
        label="Accessible Checkbox" 
        onChange={() => {}}
      />
    );
    
    const checkbox = screen.getByRole('checkbox');
    const label = screen.getByText('Accessible Checkbox');
    
    // Check if label is associated with input
    expect(checkbox.id).toBe('test-checkbox');
    expect(label.tagName).toBe('LABEL');
    expect(label).toHaveAttribute('for', 'test-checkbox');
    
    // Check ARIA attributes
    expect(checkbox).toHaveAttribute('aria-invalid', 'false');
    
    // With validation message, check aria-describedby
    renderWithTheme(
      <Checkbox 
        id="described-checkbox"
        label="Described Checkbox"
        validationMessage="Validation info" 
        onChange={() => {}}
      />
    );
    
    const describedCheckbox = screen.getByRole('checkbox');
    expect(describedCheckbox).toHaveAttribute('aria-describedby', 'described-checkbox-validation');
  });

  test('works with keyboard navigation', async () => {
    const handleChange = jest.fn();
    renderWithTheme(<Checkbox label="Keyboard Checkbox" onChange={handleChange} />);
    
    const checkbox = screen.getByRole('checkbox');
    
    // Focus the checkbox
    checkbox.focus();
    expect(document.activeElement).toBe(checkbox);
    
    // Press space to toggle
    fireEvent.keyDown(checkbox, { key: ' ', code: 'Space' });
    fireEvent.keyUp(checkbox, { key: ' ', code: 'Space' });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
  });
});