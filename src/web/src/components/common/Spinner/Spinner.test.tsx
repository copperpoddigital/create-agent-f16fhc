import React from 'react';
import '@testing-library/jest-dom'; // v5.16.5
import { render, screen } from '../../../utils/test-utils';
import Spinner from './Spinner';

describe('Spinner', () => {
  it('renders without crashing', () => {
    render(<Spinner />);
    const spinner = screen.getByRole('status');
    expect(spinner).toBeInTheDocument();
  });

  it('applies the correct size class based on the size prop', () => {
    const { rerender } = render(<Spinner size="sm" />);
    let spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('spinner--sm');
    
    rerender(<Spinner size="md" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('spinner--md');
    
    rerender(<Spinner size="lg" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('spinner--lg');
  });

  it('applies the correct color class based on the color prop', () => {
    const { rerender } = render(<Spinner color="primary" />);
    let spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('spinner--primary');
    
    rerender(<Spinner color="secondary" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('spinner--secondary');
    
    rerender(<Spinner color="white" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('spinner--white');
  });

  it('applies the inline class when inline prop is true', () => {
    const { rerender } = render(<Spinner inline={true} />);
    let spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('spinner--inline');
    
    rerender(<Spinner inline={false} />);
    spinner = screen.getByRole('status');
    expect(spinner).not.toHaveClass('spinner--inline');
  });

  it('applies additional className when provided', () => {
    render(<Spinner className="custom-class" />);
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('custom-class');
    expect(spinner).toHaveClass('spinner'); // also has the default class
  });

  it('has the correct ARIA attributes for accessibility', () => {
    const { rerender } = render(<Spinner />);
    let spinner = screen.getByRole('status');
    expect(spinner).toHaveAttribute('aria-label', 'Loading...');
    
    rerender(<Spinner ariaLabel="Custom loading message" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveAttribute('aria-label', 'Custom loading message');
  });
});