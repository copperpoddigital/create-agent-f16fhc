import React from 'react';
import { render, screen } from '../../../utils/test-utils';
import Icon from './Icon';
import '@testing-library/jest-dom'; // v5.16.5

describe('Icon Component', () => {
  test('renders with default props', () => {
    render(<Icon name="arrow-up" />);
    const icon = screen.getByTestId('icon');
    
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveAttribute('width', '24'); // Default size is 'md' which is 24px
    expect(icon).toHaveAttribute('height', '24');
    expect(icon).toHaveAttribute('role', 'img');
  });

  test('renders with custom size', () => {
    render(<Icon name="arrow-up" size="lg" />);
    const icon = screen.getByTestId('icon');
    
    expect(icon).toHaveAttribute('width', '32'); // 'lg' size is 32px
    expect(icon).toHaveAttribute('height', '32');
  });

  test('renders with custom color', () => {
    render(<Icon name="arrow-up" color="#ff0000" />);
    const icon = screen.getByTestId('icon');
    
    expect(icon).toHaveAttribute('fill', '#ff0000');
  });

  test('renders with custom className', () => {
    render(<Icon name="arrow-up" className="custom-icon" />);
    const icon = screen.getByTestId('icon');
    
    expect(icon).toHaveClass('custom-icon');
    expect(icon).toHaveClass('icon'); // Should still have the base 'icon' class
  });

  test('renders with accessibility attributes', () => {
    render(<Icon name="arrow-up" ariaLabel="Test Icon" role="graphics-symbol" />);
    const icon = screen.getByTestId('icon');
    
    expect(icon).toHaveAttribute('aria-label', 'Test Icon');
    expect(icon).toHaveAttribute('role', 'graphics-symbol');
  });

  test('renders different icon types correctly', () => {
    // Render arrow-up icon
    const { rerender } = render(<Icon name="arrow-up" />);
    const arrowUpIcon = screen.getByTestId('icon');
    const arrowUpPath = arrowUpIcon.querySelector('path');
    
    expect(arrowUpPath).toHaveAttribute('d', 'M7 14l5-5 5 5z');
    
    // Rerender with arrow-down icon
    rerender(<Icon name="arrow-down" />);
    const arrowDownIcon = screen.getByTestId('icon');
    const arrowDownPath = arrowDownIcon.querySelector('path');
    
    expect(arrowDownPath).toHaveAttribute('d', 'M7 10l5 5 5-5z');
  });

  test('handles unknown icon names gracefully', () => {
    // This should log a warning but not crash
    render(<Icon name="non-existent-icon" />);
    const icon = screen.getByTestId('icon');
    
    expect(icon).toBeInTheDocument();
    // Path should not exist when icon name is unknown
    const path = icon.querySelector('path');
    expect(path).not.toBeInTheDocument();
  });

  test('can be found by testId', () => {
    render(<Icon name="arrow-up" testId="custom-icon-test" />);
    const icon = screen.getByTestId('custom-icon-test');
    
    expect(icon).toBeInTheDocument();
  });
});