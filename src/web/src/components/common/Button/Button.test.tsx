import React from 'react';
import { render, screen, fireEvent, userEvent, waitFor } from '../../utils/test-utils';
import Button from './Button';
import '@testing-library/jest-dom/extend-expect';

describe('Button Component', () => {
  test('renders with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  test('applies variant class correctly', () => {
    const { rerender } = render(<Button variant="primary">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--primary');
    
    rerender(<Button variant="secondary">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--secondary');
    
    rerender(<Button variant="outline-primary">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--outline-primary');
    
    rerender(<Button variant="success">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--success');
    
    rerender(<Button variant="danger">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--danger');
    
    rerender(<Button variant="warning">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--warning');
    
    rerender(<Button variant="link">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--link');
  });

  test('applies size class correctly', () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--sm');
    
    rerender(<Button size="md">Medium</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--md');
    
    rerender(<Button size="lg">Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--lg');
  });

  test('can be disabled', () => {
    const onClick = jest.fn();
    render(<Button disabled onClick={onClick}>Disabled</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-disabled', 'true');
    
    fireEvent.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  test('shows loading spinner when isLoading is true', () => {
    render(<Button isLoading>Loading</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn--loading');
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(button).toBeDisabled();
    
    // Spinner should be in the document with role="status"
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('displays left and right icons', () => {
    const LeftIcon = () => <span data-testid="left-icon">←</span>;
    const RightIcon = () => <span data-testid="right-icon">→</span>;
    
    render(
      <Button leftIcon={<LeftIcon />} rightIcon={<RightIcon />}>
        With Icons
      </Button>
    );
    
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveClass('btn--with-left-icon');
    expect(screen.getByRole('button')).toHaveClass('btn--with-right-icon');
  });

  test('can take full width', () => {
    render(<Button fullWidth>Full Width</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--full-width');
  });

  test('calls onClick handler when clicked', () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Click Me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  test('has correct ARIA attributes', () => {
    render(<Button ariaLabel="Custom Label">ARIA</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Custom Label');
  });
});