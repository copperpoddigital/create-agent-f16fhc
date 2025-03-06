import React from 'react';
import '@testing-library/jest-dom/extend-expect';
import Card from './Card';
import { renderWithTheme, screen, fireEvent, userEvent } from '../../../utils/test-utils';

describe('Card Component', () => {
  test('renders correctly with default props', () => {
    renderWithTheme(<Card>Card content</Card>);
    const card = screen.getByTestId('card');
    expect(card).toBeInTheDocument();
    expect(card).toHaveClass('card');
  });

  test('renders with a title', () => {
    renderWithTheme(<Card title="Card Title">Card content</Card>);
    expect(screen.getByText('Card Title')).toBeInTheDocument();
  });

  test('renders with a subtitle', () => {
    renderWithTheme(<Card subtitle="Card Subtitle">Card content</Card>);
    expect(screen.getByText('Card Subtitle')).toBeInTheDocument();
  });

  test('renders with a custom header', () => {
    const customHeader = <div data-testid="custom-header">Custom Header</div>;
    renderWithTheme(<Card header={customHeader}>Card content</Card>);
    expect(screen.getByTestId('custom-header')).toBeInTheDocument();
  });

  test('renders with a footer', () => {
    const footer = <div data-testid="footer">Footer Content</div>;
    renderWithTheme(<Card footer={footer}>Card content</Card>);
    expect(screen.getByTestId('footer')).toBeInTheDocument();
  });

  test('applies variant classes correctly', () => {
    // Test primary variant
    renderWithTheme(<Card variant="primary">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-primary');
    
    // Test secondary variant
    renderWithTheme(<Card variant="secondary">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-secondary');
    
    // Test accent variant
    renderWithTheme(<Card variant="accent">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-accent');
    
    // Test success variant
    renderWithTheme(<Card variant="success">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-success');
    
    // Test warning variant
    renderWithTheme(<Card variant="warning">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-warning');
    
    // Test danger variant
    renderWithTheme(<Card variant="danger">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-danger');
  });

  test('applies size classes correctly', () => {
    // Test small size
    renderWithTheme(<Card size="small">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-small');
    
    // Test medium size
    renderWithTheme(<Card size="medium">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-medium');
    
    // Test large size
    renderWithTheme(<Card size="large">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-large');
  });

  test('applies outline class when outline prop is true', () => {
    renderWithTheme(<Card outline>Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-outline');
  });

  test('applies clickable class when clickable prop is true', () => {
    renderWithTheme(<Card clickable>Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('card-clickable');
  });

  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    renderWithTheme(<Card clickable onClick={handleClick}>Card content</Card>);
    const card = screen.getByTestId('card');
    fireEvent.click(card);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('is keyboard accessible when clickable', () => {
    const handleClick = jest.fn();
    renderWithTheme(<Card clickable onClick={handleClick}>Card content</Card>);
    const card = screen.getByTestId('card');
    
    // Verify accessibility attributes
    expect(card).toHaveAttribute('tabIndex', '0');
    expect(card).toHaveAttribute('role', 'button');
    
    // In a real browser, pressing Enter on an element with role="button" triggers a click
    // We'll simulate this behavior with a keyDown event
    fireEvent.keyDown(card, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies custom className when provided', () => {
    renderWithTheme(<Card className="custom-class">Card content</Card>);
    expect(screen.getByTestId('card')).toHaveClass('custom-class');
  });

  test('renders children correctly', () => {
    renderWithTheme(
      <Card>
        <div data-testid="child">Child content</div>
      </Card>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
    expect(screen.getByTestId('child')).toHaveTextContent('Child content');
  });
});