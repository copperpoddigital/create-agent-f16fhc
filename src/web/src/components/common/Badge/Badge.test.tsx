import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../utils/test-utils';
import Badge from './Badge';

describe('Badge component', () => {
  it('renders correctly with default props', () => {
    render(<Badge>Test Badge</Badge>);
    
    const badge = screen.getByTestId('badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('badge', 'badge--primary', 'badge--md');
    expect(badge).toHaveTextContent('Test Badge');
  });

  it('renders with different variants', () => {
    // Test secondary variant
    render(<Badge variant="secondary">Secondary Badge</Badge>);
    expect(screen.getByTestId('badge')).toHaveClass('badge--secondary');
    
    // Test success variant
    render(<Badge variant="success">Success Badge</Badge>);
    expect(screen.getByTestId('badge')).toHaveClass('badge--success');
    
    // Test warning variant
    render(<Badge variant="warning">Warning Badge</Badge>);
    expect(screen.getByTestId('badge')).toHaveClass('badge--warning');
    
    // Test danger variant
    render(<Badge variant="danger">Danger Badge</Badge>);
    expect(screen.getByTestId('badge')).toHaveClass('badge--danger');
  });

  it('renders with different sizes', () => {
    // Test small size
    render(<Badge size="sm">Small Badge</Badge>);
    expect(screen.getByTestId('badge')).toHaveClass('badge--sm');
    
    // Test medium size
    render(<Badge size="md">Medium Badge</Badge>);
    expect(screen.getByTestId('badge')).toHaveClass('badge--md');
    
    // Test large size
    render(<Badge size="lg">Large Badge</Badge>);
    expect(screen.getByTestId('badge')).toHaveClass('badge--lg');
  });

  it('renders with pill shape when pill prop is true', () => {
    render(<Badge pill>Pill Badge</Badge>);
    expect(screen.getByTestId('badge')).toHaveClass('badge--pill');
  });

  it('renders with an icon when icon prop is provided', () => {
    render(<Badge icon="arrow-up">Badge with Icon</Badge>);
    
    const badge = screen.getByTestId('badge');
    const icon = screen.getByTestId('icon');
    
    expect(badge).toContainElement(icon);
    expect(icon).toHaveClass('icon--arrow-up');
  });

  it('applies additional className when provided', () => {
    render(<Badge className="custom-badge">Custom Badge</Badge>);
    
    const badge = screen.getByTestId('badge');
    expect(badge).toHaveClass('badge', 'custom-badge');
  });

  it('renders children correctly', () => {
    render(
      <Badge>
        <span data-testid="child-element">Complex Child</span>
        <span>Another child</span>
      </Badge>
    );
    
    const badge = screen.getByTestId('badge');
    const childElement = screen.getByTestId('child-element');
    
    expect(badge).toContainElement(childElement);
    expect(badge).toHaveTextContent('Complex ChildAnother child');
  });

  it('applies correct test ID when provided', () => {
    render(<Badge testId="custom-badge-id">Test ID Badge</Badge>);
    
    const badge = screen.getByTestId('custom-badge-id');
    expect(badge).toBeInTheDocument();
  });
});