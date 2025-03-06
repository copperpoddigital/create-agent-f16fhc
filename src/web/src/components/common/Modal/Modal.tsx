import React, { useEffect, useRef } from 'react';
import classNames from 'classnames'; // v2.3.2
import FocusTrap from 'focus-trap-react'; // v10.0.0
import Button from '../Button';

/**
 * Custom hook to handle Escape key press to close the modal
 */
const useEscapeKey = (
  onEscape: () => void,
  isActive: boolean
): void => {
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (isActive && event.key === 'Escape') {
        onEscape();
      }
    };

    document.addEventListener('keydown', handleEscapeKey);
    
    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [onEscape, isActive]);
};

/**
 * Props interface for the Modal component
 */
export interface ModalProps {
  /**
   * Whether the modal is visible
   */
  isOpen: boolean;
  
  /**
   * Function to call when the modal should close
   */
  onClose: () => void;
  
  /**
   * Title text to display in the modal header
   */
  title?: string;
  
  /**
   * Content to display in the modal body
   */
  children: React.ReactNode;
  
  /**
   * Content to display in the modal footer
   */
  footer?: React.ReactNode;
  
  /**
   * Size of the modal
   */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  
  /**
   * Whether to close the modal when the Escape key is pressed
   */
  closeOnEscape?: boolean;
  
  /**
   * Whether to close the modal when clicking the overlay background
   */
  closeOnOverlayClick?: boolean;
  
  /**
   * Additional CSS class names to apply to the modal
   */
  className?: string;
  
  /**
   * Whether to show the close button in the header
   */
  showCloseButton?: boolean;
  
  /**
   * ID of the element that labels the modal for accessibility
   */
  ariaLabelledBy?: string;
  
  /**
   * ID of the element that describes the modal for accessibility
   */
  ariaDescribedBy?: string;
}

/**
 * A customizable modal dialog component that can be shown or hidden.
 * Provides features like different sizes, close on escape/overlay click,
 * customizable header and footer, and accessibility support.
 * 
 * @example
 * // Basic usage
 * <Modal isOpen={isModalOpen} onClose={handleClose} title="Confirmation">
 *   <p>Are you sure you want to continue?</p>
 * </Modal>
 * 
 * @example
 * // With custom footer and size
 * <Modal 
 *   isOpen={isModalOpen} 
 *   onClose={handleClose} 
 *   title="Save Analysis"
 *   size="lg"
 *   footer={
 *     <>
 *       <Button onClick={handleSave}>Save</Button>
 *       <Button variant="secondary" onClick={handleClose}>Cancel</Button>
 *     </>
 *   }
 * >
 *   <AnalysisForm data={analysisData} />
 * </Modal>
 */
const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnEscape = true,
  closeOnOverlayClick = true,
  className,
  showCloseButton = true,
  ariaLabelledBy = 'modal-title',
  ariaDescribedBy,
}) => {
  // Store the element that was focused before the modal opened
  const previousActiveElement = useRef<Element | null>(null);

  // Use the escape key hook if closeOnEscape is true
  useEscapeKey(onClose, isOpen && closeOnEscape);

  // Handle clicks on the modal overlay
  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    // Only close if the click was on the overlay itself (not its children)
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  };

  // Handle close button click
  const handleCloseButtonClick = () => {
    onClose();
  };

  // Store the active element and add body class when the modal opens
  useEffect(() => {
    if (isOpen) {
      // Store the current active element
      previousActiveElement.current = document.activeElement;
      
      // Add class to body to prevent scrolling
      document.body.classList.add('modal-open');
    } else {
      // Remove class from body when modal closes
      document.body.classList.remove('modal-open');
      
      // Return focus to the previously active element
      if (previousActiveElement.current && 'focus' in previousActiveElement.current) {
        (previousActiveElement.current as HTMLElement).focus();
      }
    }
    
    // Clean up by removing the body class when the component unmounts
    return () => {
      document.body.classList.remove('modal-open');
    };
  }, [isOpen]);

  // Don't render anything if the modal is not open
  if (!isOpen) {
    return null;
  }

  // Create the modal element
  return (
    <FocusTrap>
      <div 
        className="modal-overlay" 
        onClick={handleOverlayClick} 
        role="dialog" 
        aria-modal="true" 
        aria-labelledby={ariaLabelledBy} 
        aria-describedby={ariaDescribedBy}
      >
        <div className={classNames('modal-dialog', `modal-${size}`, className)}>
          {/* Modal header */}
          {(title || showCloseButton) && (
            <div className="modal-header">
              {title && <h2 className="modal-title" id={ariaLabelledBy}>{title}</h2>}
              {showCloseButton && (
                <button
                  type="button"
                  className="modal-close"
                  aria-label="Close modal"
                  onClick={handleCloseButtonClick}
                >
                  ×
                </button>
              )}
            </div>
          )}
          
          {/* Modal body */}
          <div className="modal-body">
            {children}
          </div>
          
          {/* Modal footer */}
          {footer && (
            <div className="modal-footer">
              {footer}
            </div>
          )}
        </div>
      </div>
    </FocusTrap>
  );
};

export default Modal;