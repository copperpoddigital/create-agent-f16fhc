import React from 'react';
import Input from './Input';
import { render, screen, fireEvent, waitFor, userEvent } from '../../utils/test-utils';
import '@testing-library/jest-dom/extend-expect';

describe('Input component', () => {
  // Helper function to get the container of an input element
  const getInputContainer = (input: HTMLElement): HTMLElement => {
    return input.parentElement?.classList.contains('input-container') 
      ? input.parentElement 
      : input;
  };

  test('renders correctly with default props', () => {
    render(<Input />);
    const inputElement = screen.getByRole('textbox');
    expect(inputElement).toBeInTheDocument();
    expect(inputElement).toHaveAttribute('type', 'text');
    expect(inputElement).not.toBeDisabled();
  });

  test('applies different sizes correctly', () => {
    // Test small size
    const { rerender } = render(<Input size="sm" />);
    let inputElement = screen.getByRole('textbox');
    let container = getInputContainer(inputElement);
    expect(container).toHaveClass('input-size-sm');

    // Test medium size
    rerender(<Input size="md" />);
    inputElement = screen.getByRole('textbox');
    container = getInputContainer(inputElement);
    expect(container).toHaveClass('input-size-md');

    // Test large size
    rerender(<Input size="lg" />);
    inputElement = screen.getByRole('textbox');
    container = getInputContainer(inputElement);
    expect(container).toHaveClass('input-size-lg');
  });

  test('handles state changes correctly', () => {
    // Test valid state
    const { rerender } = render(<Input isValid={true} />);
    let inputElement = screen.getByRole('textbox');
    let container = getInputContainer(inputElement);
    expect(container).toHaveClass('input-valid');

    // Test invalid state
    rerender(<Input isInvalid={true} />);
    inputElement = screen.getByRole('textbox');
    container = getInputContainer(inputElement);
    expect(container).toHaveClass('input-invalid');
    expect(inputElement).toHaveAttribute('aria-invalid', 'true');

    // Test disabled state
    rerender(<Input disabled={true} />);
    inputElement = screen.getByRole('textbox');
    expect(inputElement).toBeDisabled();
    container = getInputContainer(inputElement);
    expect(container).toHaveClass('input-disabled');
  });

  test('renders with icons correctly', () => {
    // Test with left icon
    const leftIcon = <span data-testid="left-icon">L</span>;
    const { rerender } = render(<Input leftIcon={leftIcon} />);
    
    // For inputs with icons, we expect a container structure
    let inputElement = screen.getByRole('textbox');
    let container = inputElement.parentElement;
    expect(container).toHaveClass('input-container');
    expect(container).toHaveClass('input-with-left-icon');
    
    // Icon should be inside the container
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    
    // Test with right icon
    const rightIcon = <span data-testid="right-icon">R</span>;
    rerender(<Input rightIcon={rightIcon} />);
    inputElement = screen.getByRole('textbox');
    container = inputElement.parentElement;
    expect(container).toHaveClass('input-with-right-icon');
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
    
    // Test with both icons
    rerender(<Input leftIcon={leftIcon} rightIcon={rightIcon} />);
    inputElement = screen.getByRole('textbox');
    container = inputElement.parentElement;
    expect(container).toHaveClass('input-with-left-icon');
    expect(container).toHaveClass('input-with-right-icon');
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
  });

  test('handles user input correctly', () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} />);
    
    const inputElement = screen.getByRole('textbox');
    fireEvent.change(inputElement, { target: { value: 'test input' } });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(inputElement.value).toBe('test input');
  });

  test('handles clear button correctly', () => {
    const handleChange = jest.fn();
    const handleClear = jest.fn();
    
    // Render with value and clearable=true
    const { rerender } = render(
      <Input 
        value="test input" 
        clearable={true} 
        onChange={handleChange} 
        onClear={handleClear}
      />
    );
    
    // Clear button should be visible
    const clearButton = screen.getByRole('button', { name: /clear input/i });
    expect(clearButton).toBeInTheDocument();
    
    // Click should trigger onClear and onChange
    fireEvent.click(clearButton);
    expect(handleClear).toHaveBeenCalledTimes(1);
    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(handleChange).toHaveBeenCalledWith(
      expect.objectContaining({
        target: expect.objectContaining({
          value: ''
        })
      })
    );
    
    // Test that clear button is not shown when input is disabled
    rerender(
      <Input 
        value="test input" 
        clearable={true} 
        disabled={true}
        onChange={handleChange} 
        onClear={handleClear}
      />
    );
    expect(screen.queryByRole('button', { name: /clear input/i })).not.toBeInTheDocument();
  });

  test('handles focus and blur events correctly', () => {
    const handleFocus = jest.fn();
    const handleBlur = jest.fn();
    
    render(<Input onFocus={handleFocus} onBlur={handleBlur} />);
    
    const inputElement = screen.getByRole('textbox');
    const container = getInputContainer(inputElement);
    
    fireEvent.focus(inputElement);
    expect(handleFocus).toHaveBeenCalledTimes(1);
    expect(container).toHaveClass('input-focused');
    
    fireEvent.blur(inputElement);
    expect(handleBlur).toHaveBeenCalledTimes(1);
    expect(container).not.toHaveClass('input-focused');
  });

  test('forwards ref correctly', () => {
    const ref = React.createRef<HTMLInputElement>();
    
    render(<Input ref={ref} defaultValue="test" />);
    
    expect(ref.current).not.toBeNull();
    expect(ref.current?.value).toBe('test');
    
    // Verify we can interact with the input through the ref
    if (ref.current) {
      ref.current.focus();
      expect(document.activeElement).toBe(ref.current);
    }
  });

  test('applies additional className correctly', () => {
    render(<Input className="custom-class" />);
    
    const inputElement = screen.getByRole('textbox');
    const container = getInputContainer(inputElement);
    
    expect(container).toHaveClass('custom-class');
  });

  test('has proper accessibility attributes', () => {
    render(
      <Input 
        ariaLabel="Test input" 
        ariaDescribedBy="test-description" 
        required={true}
      />
    );
    
    const inputElement = screen.getByRole('textbox');
    expect(inputElement).toHaveAttribute('aria-label', 'Test input');
    expect(inputElement).toHaveAttribute('aria-describedby', 'test-description');
    expect(inputElement).toHaveAttribute('required');
    expect(inputElement).toHaveAttribute('aria-required', 'true');
  });
});