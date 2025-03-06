import React from 'react';
import { render, screen, fireEvent } from '../../utils/test-utils';
import '@testing-library/jest-dom/extend-expect';
import FormGroup from './FormGroup';

describe('FormGroup component', () => {
  test('renders with label', () => {
    render(
      <FormGroup id="test-id" label="Test Label">
        <input type="text" />
      </FormGroup>
    );
    
    const label = screen.getByText('Test Label');
    expect(label).toBeInTheDocument();
    expect(label).toHaveAttribute('htmlFor', 'test-id');
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('id', 'test-id');
  });

  test('renders with help text', () => {
    render(
      <FormGroup id="test-id" helpText="This is help text">
        <input type="text" />
      </FormGroup>
    );
    
    const helpText = screen.getByText('This is help text');
    expect(helpText).toBeInTheDocument();
    expect(helpText).toHaveClass('form-text');
  });

  test('renders with required indicator', () => {
    render(
      <FormGroup id="test-id" label="Test Label" required>
        <input type="text" />
      </FormGroup>
    );
    
    const label = screen.getByText('Test Label');
    expect(label).toHaveClass('required');
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('aria-required', 'true');
  });

  test('renders with validation message when invalid', () => {
    render(
      <FormGroup 
        id="test-id" 
        isInvalid 
        validationMessage="This field is required"
      >
        <input type="text" />
      </FormGroup>
    );
    
    const validationMessage = screen.getByText('This field is required');
    expect(validationMessage).toBeInTheDocument();
    expect(validationMessage).toHaveClass('validation-message');
    expect(validationMessage).toHaveClass('is-invalid');
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    
    // Check if input is associated with validation message
    const messageId = validationMessage.getAttribute('id');
    expect(input).toHaveAttribute('aria-describedby', messageId);
  });

  test('applies valid state styling', () => {
    render(
      <FormGroup id="test-id" isValid>
        <input type="text" />
      </FormGroup>
    );
    
    const formGroup = screen.getByRole('textbox').closest('.form-group');
    expect(formGroup).toHaveClass('is-valid');
    
    const input = screen.getByRole('textbox');
    expect(input).not.toHaveAttribute('aria-invalid');
  });

  test('applies custom className', () => {
    render(
      <FormGroup id="test-id" className="custom-class">
        <input type="text" />
      </FormGroup>
    );
    
    const formGroup = screen.getByRole('textbox').closest('.form-group');
    expect(formGroup).toHaveClass('custom-class');
  });

  test('renders children correctly', () => {
    render(
      <FormGroup id="test-id">
        <input type="text" placeholder="First input" />
        <span>Middle content</span>
        <button>Submit</button>
      </FormGroup>
    );
    
    expect(screen.getByPlaceholderText('First input')).toBeInTheDocument();
    expect(screen.getByText('Middle content')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
  });

  test('associates help text and validation message with input via aria-describedby', () => {
    render(
      <FormGroup 
        id="test-id" 
        helpText="This is help text"
        isInvalid
        validationMessage="This field is required"
      >
        <input type="text" />
      </FormGroup>
    );
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('aria-describedby');
    
    const helpTextId = `test-id-help-text`;
    const validationMessageId = `test-id-validation-message`;
    
    // Check that aria-describedby contains both IDs
    const describedBy = input.getAttribute('aria-describedby') || '';
    expect(describedBy.split(' ')).toContain(helpTextId);
    expect(describedBy.split(' ')).toContain(validationMessageId);
    
    // Verify the IDs match the actual elements
    const helpText = screen.getByText('This is help text');
    expect(helpText).toHaveAttribute('id', helpTextId);
    
    const validationMessage = screen.getByText('This field is required');
    expect(validationMessage).toHaveAttribute('id', validationMessageId);
  });
});