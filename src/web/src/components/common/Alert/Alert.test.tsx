import React from 'react';
import { vi } from 'vitest';
import Alert from './Alert';
import { customRender, screen, fireEvent, userEvent } from '../../../utils/test-utils';

describe('Alert Component', () => {
  test('renders the alert with default props', () => {
    customRender(<Alert>Test alert message</Alert>);
    
    const alert = screen.getByTestId('alert');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveClass('alert', 'alert--info');
    expect(alert).toHaveTextContent('Test alert message');
  });

  test('renders different alert types correctly', () => {
    const types = ['success', 'error', 'warning', 'info'] as const;
    
    types.forEach(type => {
      const { unmount } = customRender(<Alert type={type}>Test {type} alert</Alert>);
      
      const alert = screen.getByTestId('alert');
      expect(alert).toHaveClass(`alert--${type}`);
      
      // Verify the alert has an icon
      const iconContainers = alert.getElementsByClassName('alert__icon');
      expect(iconContainers.length).toBe(1);
      
      // Cleanup before next test
      unmount();
    });
  });

  test('renders with a title when provided', () => {
    const title = 'Alert Title';
    customRender(<Alert title={title}>Test alert message</Alert>);
    
    const titleElement = screen.getByText(title);
    expect(titleElement).toBeInTheDocument();
    expect(titleElement).toHaveClass('alert__title');
  });

  test('renders without an icon when showIcon is false', () => {
    customRender(<Alert showIcon={false}>Test alert message</Alert>);
    
    const alert = screen.getByTestId('alert');
    const iconContainers = alert.getElementsByClassName('alert__icon');
    expect(iconContainers.length).toBe(0);
  });

  test('renders with a dismiss button when dismissible is true', () => {
    customRender(<Alert dismissible>Test alert message</Alert>);
    
    const dismissButton = screen.getByRole('button', { name: /dismiss alert/i });
    expect(dismissButton).toBeInTheDocument();
    expect(dismissButton).toHaveClass('alert__dismiss');
  });

  test('calls onDismiss when the dismiss button is clicked', async () => {
    const handleDismiss = vi.fn();
    customRender(
      <Alert dismissible onDismiss={handleDismiss}>Test alert message</Alert>
    );
    
    const dismissButton = screen.getByRole('button', { name: /dismiss alert/i });
    await userEvent.click(dismissButton);
    
    expect(handleDismiss).toHaveBeenCalledTimes(1);
  });

  test('applies additional className when provided', () => {
    const customClass = 'custom-alert';
    customRender(<Alert className={customClass}>Test alert message</Alert>);
    
    const alert = screen.getByTestId('alert');
    expect(alert).toHaveClass('alert', 'alert--info', customClass);
  });

  test('applies the correct data-testid attribute', () => {
    const testId = 'custom-alert-testid';
    customRender(<Alert testId={testId}>Test alert message</Alert>);
    
    const alert = screen.getByTestId(testId);
    expect(alert).toBeInTheDocument();
  });
});