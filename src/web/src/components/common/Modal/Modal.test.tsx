import React from 'react';
import Modal from './Modal';
import Button from '../Button';
import { render, screen, fireEvent, waitFor, userEvent } from '../../utils/test-utils';

describe('Modal component', () => {
  // Helper function to set up a test Modal with specified props
  const setup = (props = {}) => {
    const defaultProps = {
      isOpen: true,
      onClose: jest.fn(),
      title: 'Test Modal',
      children: <div>Modal content</div>
    };
    
    const mergedProps = { ...defaultProps, ...props };
    return {
      onClose: mergedProps.onClose,
      ...render(<Modal {...mergedProps} />)
    };
  };

  test('renders nothing when isOpen is false', () => {
    setup({ isOpen: false });
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument();
  });

  test('renders modal content when isOpen is true', () => {
    setup();
    expect(screen.getByText('Modal content')).toBeInTheDocument();
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  test('renders title when provided', () => {
    setup({ title: 'Custom Title' });
    const titleElement = screen.getByText('Custom Title');
    expect(titleElement).toBeInTheDocument();
    expect(titleElement).toHaveClass('modal-title');
  });

  test('renders close button by default', () => {
    setup();
    const closeButton = screen.getByRole('button', { name: /close modal/i });
    expect(closeButton).toBeInTheDocument();
    expect(closeButton).toHaveClass('modal-close');
  });

  test('does not render close button when showCloseButton is false', () => {
    setup({ showCloseButton: false });
    expect(screen.queryByRole('button', { name: /close modal/i })).not.toBeInTheDocument();
  });

  test('calls onClose when close button is clicked', () => {
    const onClose = jest.fn();
    setup({ onClose });
    
    const closeButton = screen.getByRole('button', { name: /close modal/i });
    fireEvent.click(closeButton);
    
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('calls onClose when overlay is clicked and closeOnOverlayClick is true', () => {
    const onClose = jest.fn();
    setup({ onClose, closeOnOverlayClick: true });
    
    const overlay = screen.getByRole('dialog').closest('.modal-overlay');
    fireEvent.click(overlay);
    
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('does not call onClose when overlay is clicked and closeOnOverlayClick is false', () => {
    const onClose = jest.fn();
    setup({ onClose, closeOnOverlayClick: false });
    
    const overlay = screen.getByRole('dialog').closest('.modal-overlay');
    fireEvent.click(overlay);
    
    expect(onClose).not.toHaveBeenCalled();
  });

  test('calls onClose when Escape key is pressed and closeOnEscape is true', () => {
    const onClose = jest.fn();
    setup({ onClose, closeOnEscape: true });
    
    fireEvent.keyDown(document, { key: 'Escape' });
    
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('does not call onClose when Escape key is pressed and closeOnEscape is false', () => {
    const onClose = jest.fn();
    setup({ onClose, closeOnEscape: false });
    
    fireEvent.keyDown(document, { key: 'Escape' });
    
    expect(onClose).not.toHaveBeenCalled();
  });

  test('renders with different size classes', () => {
    const sizes = ['sm', 'md', 'lg', 'xl', 'full'] as const;
    
    sizes.forEach(size => {
      const { unmount } = setup({ size });
      const dialog = document.querySelector('.modal-dialog');
      expect(dialog).toHaveClass(`modal-${size}`);
      unmount();
    });
  });

  test('renders footer content when provided', () => {
    const footerContent = <Button>Save</Button>;
    setup({ footer: footerContent });
    
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    const footer = document.querySelector('.modal-footer');
    expect(footer).toBeInTheDocument();
    expect(footer).toContainElement(screen.getByRole('button', { name: /save/i }));
  });

  test('applies custom className when provided', () => {
    setup({ className: 'custom-modal-class' });
    
    const dialog = document.querySelector('.modal-dialog');
    expect(dialog).toHaveClass('custom-modal-class');
  });

  test('sets correct ARIA attributes', () => {
    setup({ 
      ariaLabelledBy: 'custom-title-id',
      ariaDescribedBy: 'custom-description-id'
    });
    
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'custom-title-id');
    expect(dialog).toHaveAttribute('aria-describedby', 'custom-description-id');
  });

  test('traps focus within the modal', async () => {
    const user = userEvent.setup();
    setup({
      children: (
        <>
          <input data-testid="first-input" />
          <Button>Middle Button</Button>
          <input data-testid="last-input" />
        </>
      )
    });
    
    // Get the focusable elements
    const firstInput = screen.getByTestId('first-input');
    const middleButton = screen.getByRole('button', { name: /middle button/i });
    const lastInput = screen.getByTestId('last-input');
    const closeButton = screen.getByRole('button', { name: /close modal/i });
    
    // Focus should be trapped within the modal
    firstInput.focus();
    expect(document.activeElement).toBe(firstInput);
    
    // Tab through all focusable elements
    await user.tab();
    expect(document.activeElement).toBe(middleButton);
    
    await user.tab();
    expect(document.activeElement).toBe(lastInput);
    
    await user.tab();
    expect(document.activeElement).toBe(closeButton);
    
    // Tab should cycle back to first element (focus trap behavior)
    await user.tab();
    expect(document.activeElement).not.toBe(document.body);
    expect(document.activeElement?.closest('.modal-overlay')).toBeInTheDocument();
  });
});