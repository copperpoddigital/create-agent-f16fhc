import React, { useState, useRef, useEffect, ReactNode, CSSProperties } from 'react'; // ^18.2.0
import classNames from 'classnames'; // ^2.3.2
import useTheme from '../../../hooks/useTheme';
import { ThemeType } from '../../../config/theme';

/**
 * Props interface for the Tooltip component
 */
export interface TooltipProps {
  /** Content to display inside the tooltip */
  content: ReactNode;
  /** Element that triggers the tooltip */
  children: ReactNode;
  /** Position of the tooltip relative to the trigger element */
  position?: 'top' | 'right' | 'bottom' | 'left';
  /** Additional CSS class names */
  className?: string;
  /** Whether the tooltip is disabled */
  disabled?: boolean;
  /** Delay before showing the tooltip (in milliseconds) */
  delay?: number;
  /** Maximum width of the tooltip */
  maxWidth?: number | string;
}

/**
 * A reusable tooltip component that displays additional information
 * when users hover over or focus on an element.
 * 
 * @example
 * ```tsx
 * <Tooltip content="This is helpful information">
 *   <button>Hover Me</button>
 * </Tooltip>
 * ```
 */
const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  className = '',
  disabled = false,
  delay = 300,
  maxWidth,
}) => {
  // State to control tooltip visibility
  const [isVisible, setIsVisible] = useState(false);
  
  // Refs for DOM elements
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);
  
  // Get current theme
  const { theme } = useTheme();
  
  // Ref for timeout to handle delay
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  /**
   * Shows the tooltip after the specified delay
   */
  const showTooltip = () => {
    if (disabled) return;
    
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    // Set timeout for showing tooltip
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };
  
  /**
   * Hides the tooltip and clears any pending timeouts
   */
  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setIsVisible(false);
  };
  
  // Event handlers
  const handleMouseEnter = () => showTooltip();
  const handleMouseLeave = () => hideTooltip();
  const handleFocus = () => showTooltip();
  const handleBlur = () => hideTooltip();
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Show tooltip on Enter or Space key
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      showTooltip();
    }
    // Hide tooltip on Escape key
    if (e.key === 'Escape') {
      hideTooltip();
    }
  };
  
  // Clean up timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  // Generate tooltip styles
  const tooltipStyle: CSSProperties = {
    ...(maxWidth && { maxWidth: typeof maxWidth === 'number' ? `${maxWidth}px` : maxWidth }),
  };
  
  // Determine theme class
  const themeClass = theme === ThemeType.SYSTEM 
    ? 'tooltip-system' 
    : `tooltip-${theme}`;
  
  return (
    <div className="tooltip-container">
      <div
        ref={triggerRef}
        className="tooltip-trigger"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        tabIndex={disabled ? undefined : 0}
        aria-describedby={isVisible ? 'tooltip' : undefined}
      >
        {children}
      </div>
      
      {isVisible && (
        <div
          id="tooltip"
          ref={tooltipRef}
          role="tooltip"
          className={classNames(
            'tooltip',
            `tooltip-${position}`,
            themeClass,
            className
          )}
          style={tooltipStyle}
          aria-hidden={!isVisible}
        >
          <div className="tooltip-arrow" aria-hidden="true" />
          <div className="tooltip-content">{content}</div>
        </div>
      )}
    </div>
  );
};

export default Tooltip;