import React from 'react';
import { render, screen, fireEvent, userEvent } from '../../utils/test-utils';
import '@testing-library/jest-dom/extend-expect';
import RadioButton from './RadioButton';

describe('RadioButton', () => {
  it('renders correctly', () => {
    render(
      <RadioButton
        id="test-radio"
        name="test-group"
        value="test-value"
        label="Test Label"
        checked={false}
      />
    );
    
    const radioInput = screen.getByRole('radio');
    expect(radioInput).toBeInTheDocument();
    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('handles checked state correctly', () => {
    // Test checked state
    render(
      <RadioButton
        id="test-radio"
        name="test-group"
        value="test-value"
        label="Test Label"
        checked={true}
      />
    );
    
    expect(screen.getByRole('radio')).toBeChecked();
    
    // Test unchecked state
    render(
      <RadioButton
        id="test-radio-2"
        name="test-group"
        value="test-value-2"
        label="Test Label 2"
        checked={false}
      />
    );
    
    expect(screen.getByRole('radio', { name: 'Test Label 2' })).not.toBeChecked();
  });

  it('handles disabled state correctly', () => {
    render(
      <RadioButton
        id="test-radio"
        name="test-group"
        value="test-value"
        label="Test Label"
        checked={false}
        disabled={true}
      />
    );
    
    const radioInput = screen.getByRole('radio');
    expect(radioInput).toBeDisabled();
    expect(radioInput.closest('.custom-radio')).toHaveClass('is-disabled');
  });

  it('calls onChange when clicked', () => {
    const handleChange = jest.fn();
    
    render(
      <RadioButton
        id="test-radio"
        name="test-group"
        value="test-value"
        label="Test Label"
        checked={false}
        onChange={handleChange}
      />
    );
    
    fireEvent.click(screen.getByRole('radio'));
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  it('displays error message when provided', () => {
    render(
      <RadioButton
        id="test-radio"
        name="test-group"
        value="test-value"
        label="Test Label"
        checked={false}
        error="This is an error message"
      />
    );
    
    expect(screen.getByText('This is an error message')).toBeInTheDocument();
    expect(screen.getByRole('radio')).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByRole('radio')).toHaveAttribute('aria-describedby', 'test-radio-error');
    expect(screen.getByRole('alert')).toHaveTextContent('This is an error message');
    expect(screen.getByRole('radio').closest('.custom-radio')).toHaveClass('has-error');
  });

  it('applies custom className when provided', () => {
    render(
      <RadioButton
        id="test-radio"
        name="test-group"
        value="test-value"
        label="Test Label"
        checked={false}
        className="custom-class"
      />
    );
    
    expect(screen.getByRole('radio').closest('.custom-radio')).toHaveClass('custom-class');
  });

  it('is accessible with keyboard navigation', async () => {
    const handleChange = jest.fn();
    
    render(
      <RadioButton
        id="test-radio"
        name="test-group"
        value="test-value"
        label="Test Label"
        checked={false}
        onChange={handleChange}
      />
    );
    
    const user = userEvent.setup();
    
    // Set focus to the element
    await user.tab();
    
    const radioInput = screen.getByRole('radio');
    expect(radioInput).toHaveFocus();
    
    // Trigger with space key
    await user.keyboard(' ');
    expect(handleChange).toHaveBeenCalledTimes(1);
  });
});