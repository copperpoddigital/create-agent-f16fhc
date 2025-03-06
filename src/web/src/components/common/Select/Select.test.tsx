import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../utils/test-utils';
import userEvent from '@testing-library/user-event';
import Select from './Select';

// Helper function to set up the component with default props for testing
const setup = (props = {}) => {
  const defaultOptions = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' }
  ];
  
  const defaultProps = {
    options: defaultOptions,
    placeholder: 'Select an option',
    onChange: jest.fn(),
  };
  
  const mergedProps = { ...defaultProps, ...props };
  
  return {
    user: userEvent.setup(),
    ...render(<Select {...mergedProps} />),
    defaultOptions,
    onChange: mergedProps.onChange,
  };
};

describe('Select component', () => {
  it('renders correctly with default props', () => {
    const { defaultOptions } = setup();
    
    // Check that select element is rendered
    const selectElement = screen.getByTestId('select');
    expect(selectElement).toBeInTheDocument();
    
    // Check placeholder option is rendered
    const placeholderOption = screen.getByText('Select an option');
    expect(placeholderOption).toBeInTheDocument();
    
    // Check all options are rendered
    defaultOptions.forEach(option => {
      expect(screen.getByText(option.label)).toBeInTheDocument();
    });
  });

  it('handles selection changes', async () => {
    const { onChange, user } = setup();
    
    // Open the select dropdown
    const selectElement = screen.getByTestId('select');
    await user.click(selectElement);
    
    // Select an option
    const option = screen.getByText('Option 2');
    await user.click(option);
    
    // Check if onChange was called with the correct value
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({
      target: expect.objectContaining({
        value: 'option2'
      })
    }));
  });

  it('displays validation states correctly', () => {
    // Test valid state
    const { rerender } = setup({ isValid: true });
    let selectContainer = screen.getByTestId('select').closest('.select-container');
    expect(selectContainer).toHaveClass('select-container--valid');
    
    // Test invalid state with validation message
    rerender(
      <Select 
        options={[
          { value: 'option1', label: 'Option 1' },
          { value: 'option2', label: 'Option 2' },
          { value: 'option3', label: 'Option 3' }
        ]}
        isInvalid={true}
        validationMessage="This field is required"
        onChange={jest.fn()}
      />
    );
    
    selectContainer = screen.getByTestId('select').closest('.select-container');
    expect(selectContainer).toHaveClass('select-container--invalid');
    
    // Check validation message
    const validationMessage = screen.getByText('This field is required');
    expect(validationMessage).toBeInTheDocument();
    expect(validationMessage).toHaveClass('select-validation-message--invalid');
  });

  it('supports clearable functionality', async () => {
    const onClear = jest.fn();
    const { user } = setup({
      clearable: true,
      value: 'option1',
      onClear
    });
    
    // Check if clear button is rendered
    const clearButton = screen.getByTestId('select-clear-button');
    expect(clearButton).toBeInTheDocument();
    
    // Click clear button
    await user.click(clearButton);
    
    // Check if onClear was called
    expect(onClear).toHaveBeenCalledTimes(1);
  });

  it('supports different sizes', () => {
    // Test small size
    const { rerender } = setup({ size: 'sm' });
    let selectContainer = screen.getByTestId('select').closest('.select-container');
    expect(selectContainer).toHaveClass('select-container--sm');
    
    // Test medium size
    rerender(
      <Select 
        options={[
          { value: 'option1', label: 'Option 1' },
          { value: 'option2', label: 'Option 2' },
          { value: 'option3', label: 'Option 3' }
        ]}
        size="md"
        onChange={jest.fn()}
      />
    );
    selectContainer = screen.getByTestId('select').closest('.select-container');
    expect(selectContainer).toHaveClass('select-container--md');
    
    // Test large size
    rerender(
      <Select 
        options={[
          { value: 'option1', label: 'Option 1' },
          { value: 'option2', label: 'Option 2' },
          { value: 'option3', label: 'Option 3' }
        ]}
        size="lg"
        onChange={jest.fn()}
      />
    );
    selectContainer = screen.getByTestId('select').closest('.select-container');
    expect(selectContainer).toHaveClass('select-container--lg');
  });

  it('supports left icon', () => {
    setup({ leftIcon: <div data-testid="test-icon">Icon</div> });
    
    // Check if icon is rendered
    const icon = screen.getByTestId('test-icon');
    expect(icon).toBeInTheDocument();
    
    // Check if container has with-icon class
    const selectContainer = screen.getByTestId('select').closest('.select-container');
    expect(selectContainer).toHaveClass('select-container--with-icon');
  });

  it('handles disabled state', () => {
    setup({ disabled: true });
    
    // Check if select is disabled
    const selectElement = screen.getByTestId('select');
    expect(selectElement).toBeDisabled();
    
    // Check if container has disabled class
    const selectContainer = selectElement.closest('.select-container');
    expect(selectContainer).toHaveClass('select-container--disabled');
  });

  it('handles focus and blur events', async () => {
    const onFocus = jest.fn();
    const onBlur = jest.fn();
    const { user } = setup({ onFocus, onBlur });
    
    const selectElement = screen.getByTestId('select');
    
    // Focus the select element
    await user.click(selectElement);
    
    // Check if onFocus was called
    expect(onFocus).toHaveBeenCalledTimes(1);
    
    // Check if focused class is applied
    const selectContainer = selectElement.closest('.select-container');
    expect(selectContainer).toHaveClass('select-container--focused');
    
    // Blur the select element
    await user.tab(); // Tab to move focus away
    
    // Check if onBlur was called
    expect(onBlur).toHaveBeenCalledTimes(1);
    
    // Check if focused class is removed
    expect(selectContainer).not.toHaveClass('select-container--focused');
  });

  it('supports keyboard navigation', async () => {
    const onChange = jest.fn();
    const { user } = setup({ onChange });
    
    const selectElement = screen.getByTestId('select');
    
    // Focus the select element
    await user.click(selectElement);
    
    // Use keyboard to navigate and select option
    await user.keyboard('{ArrowDown}');
    await user.keyboard('{ArrowDown}');
    await user.keyboard('{Enter}');
    
    // Check if onChange was called with correct value
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({
        target: expect.objectContaining({
          value: expect.any(String)
        })
      })
    );
  });
});