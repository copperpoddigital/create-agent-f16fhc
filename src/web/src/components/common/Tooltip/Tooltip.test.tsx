import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act } from '@testing-library/react';
import Tooltip from './Tooltip';
import { renderWithTheme, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';

describe('Tooltip Component', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
  });

  it('renders without crashing', () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    );
    
    expect(screen.getByText('Hover me')).toBeInTheDocument();
  });

  it('shows tooltip on hover', async () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Hover me').closest('.tooltip-trigger');
    expect(triggerElement).toBeInTheDocument();
    
    fireEvent.mouseEnter(triggerElement!);
    
    act(() => {
      vi.advanceTimersByTime(300); // Default delay
    });
    
    expect(screen.getByText('Tooltip content')).toBeInTheDocument();
  });

  it('hides tooltip when mouse leaves', async () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Hover me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Hover me').closest('.tooltip-trigger');
    
    // Show tooltip
    fireEvent.mouseEnter(triggerElement!);
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    // Verify it's visible
    expect(screen.getByText('Tooltip content')).toBeInTheDocument();
    
    // Hide tooltip
    fireEvent.mouseLeave(triggerElement!);
    
    // Verify it's hidden
    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument();
  });

  it('shows tooltip on focus', async () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Focus me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Focus me').closest('.tooltip-trigger');
    
    fireEvent.focus(triggerElement!);
    
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    expect(screen.getByText('Tooltip content')).toBeInTheDocument();
  });

  it('hides tooltip on blur', async () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Focus me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Focus me').closest('.tooltip-trigger');
    
    // Show tooltip
    fireEvent.focus(triggerElement!);
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    // Verify it's visible
    expect(screen.getByText('Tooltip content')).toBeInTheDocument();
    
    // Hide tooltip
    fireEvent.blur(triggerElement!);
    
    // Verify it's hidden
    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument();
  });

  it('shows tooltip on Enter key press', async () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Press Enter</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Press Enter').closest('.tooltip-trigger');
    
    fireEvent.keyDown(triggerElement!, { key: 'Enter' });
    
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    expect(screen.getByText('Tooltip content')).toBeInTheDocument();
  });

  it('hides tooltip on Escape key press', async () => {
    renderWithTheme(
      <Tooltip content="Tooltip content">
        <button>Press Escape</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Press Escape').closest('.tooltip-trigger');
    
    // Show tooltip with hover
    fireEvent.mouseEnter(triggerElement!);
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    // Verify it's visible
    expect(screen.getByText('Tooltip content')).toBeInTheDocument();
    
    // Hide tooltip with Escape key
    fireEvent.keyDown(triggerElement!, { key: 'Escape' });
    
    // Verify it's hidden
    expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument();
  });
  
  it('respects delay prop', async () => {
    const customDelay = 1000;
    
    renderWithTheme(
      <Tooltip content="Delayed tooltip" delay={customDelay}>
        <button>Hover for delay</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Hover for delay').closest('.tooltip-trigger');
    
    // Show tooltip
    fireEvent.mouseEnter(triggerElement!);
    
    // Advance time but not enough to show tooltip
    act(() => {
      vi.advanceTimersByTime(500);
    });
    
    // Tooltip should not be visible yet
    expect(screen.queryByText('Delayed tooltip')).not.toBeInTheDocument();
    
    // Advance time to show tooltip
    act(() => {
      vi.advanceTimersByTime(500);
    });
    
    // Now tooltip should be visible
    expect(screen.getByText('Delayed tooltip')).toBeInTheDocument();
  });

  it('applies correct position class', async () => {
    renderWithTheme(
      <Tooltip content="Right tooltip" position="right">
        <button>Hover me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Hover me').closest('.tooltip-trigger');
    
    // Show tooltip
    fireEvent.mouseEnter(triggerElement!);
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    // Verify position class
    const tooltipElement = screen.getByRole('tooltip');
    expect(tooltipElement).toHaveClass('tooltip-right');
  });

  it('applies custom className', async () => {
    renderWithTheme(
      <Tooltip content="Custom tooltip" className="custom-tooltip-class">
        <button>Hover me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Hover me').closest('.tooltip-trigger');
    
    // Show tooltip
    fireEvent.mouseEnter(triggerElement!);
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    // Verify custom class
    const tooltipElement = screen.getByRole('tooltip');
    expect(tooltipElement).toHaveClass('custom-tooltip-class');
  });

  it('does not show tooltip when disabled', async () => {
    renderWithTheme(
      <Tooltip content="Disabled tooltip" disabled={true}>
        <button>Hover me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Hover me').closest('.tooltip-trigger');
    
    // Try to show tooltip
    fireEvent.mouseEnter(triggerElement!);
    act(() => {
      vi.advanceTimersByTime(1000); // Give plenty of time
    });
    
    // Tooltip should not appear
    expect(screen.queryByText('Disabled tooltip')).not.toBeInTheDocument();
  });

  it('applies maxWidth style when provided', async () => {
    renderWithTheme(
      <Tooltip content="Width limited tooltip" maxWidth={200}>
        <button>Hover me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Hover me').closest('.tooltip-trigger');
    
    // Show tooltip
    fireEvent.mouseEnter(triggerElement!);
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    // Verify maxWidth style
    const tooltipElement = screen.getByRole('tooltip');
    expect(tooltipElement).toHaveStyle('max-width: 200px');
  });

  it('has correct ARIA attributes for accessibility', async () => {
    renderWithTheme(
      <Tooltip content="Accessible tooltip">
        <button>Hover me</button>
      </Tooltip>
    );
    
    const triggerElement = screen.getByText('Hover me').closest('.tooltip-trigger');
    
    // Show tooltip
    fireEvent.mouseEnter(triggerElement!);
    act(() => {
      vi.advanceTimersByTime(300);
    });
    
    // Verify ARIA attributes
    expect(triggerElement).toHaveAttribute('aria-describedby', 'tooltip');
    const tooltipElement = screen.getByRole('tooltip');
    expect(tooltipElement).toHaveAttribute('id', 'tooltip');
  });
});