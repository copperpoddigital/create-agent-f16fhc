import React, { useState } from 'react';
import { axe, toHaveNoViolations } from 'jest-axe'; // ^7.0.0
import Tabs from './Tabs';
import { customRender, screen, fireEvent, userEvent, waitFor } from '../../utils/test-utils';

// Extend Jest's expect with accessibility testing matchers
expect.extend({ toHaveNoViolations });

describe('Tabs component', () => {
  it('renders tabs correctly', () => {
    // Define mock tabs data
    const tabs = [
      { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
      { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div> },
      { id: 'tab3', label: 'Tab 3', content: <div>Content 3</div> }
    ];

    // Render the Tabs component with the mock data
    customRender(<Tabs tabs={tabs} />);

    // Verify that all tab buttons are rendered
    const tabButtons = screen.getAllByRole('tab');
    expect(tabButtons).toHaveLength(3);
    expect(tabButtons[0]).toHaveTextContent('Tab 1');
    expect(tabButtons[1]).toHaveTextContent('Tab 2');
    expect(tabButtons[2]).toHaveTextContent('Tab 3');

    // Verify that the first tab is active by default
    expect(tabButtons[0]).toHaveAttribute('aria-selected', 'true');
    expect(tabButtons[1]).toHaveAttribute('aria-selected', 'false');
    expect(tabButtons[2]).toHaveAttribute('aria-selected', 'false');

    // Verify that the first tab's content is visible
    const tabPanel = screen.getByRole('tabpanel');
    expect(tabPanel).toBeVisible();
    expect(tabPanel).toHaveTextContent('Content 1');
  });

  it('changes active tab when clicked', () => {
    // Define mock tabs data
    const tabs = [
      { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
      { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div> },
      { id: 'tab3', label: 'Tab 3', content: <div>Content 3</div> }
    ];

    // Render the Tabs component with the mock data
    customRender(<Tabs tabs={tabs} />);

    // Click on the second tab
    const tabButtons = screen.getAllByRole('tab');
    fireEvent.click(tabButtons[1]);

    // Verify that the second tab becomes active
    expect(tabButtons[0]).toHaveAttribute('aria-selected', 'false');
    expect(tabButtons[1]).toHaveAttribute('aria-selected', 'true');
    expect(tabButtons[2]).toHaveAttribute('aria-selected', 'false');

    // Verify that the second tab's content is visible
    const tabPanel = screen.getByRole('tabpanel');
    expect(tabPanel).toBeVisible();
    expect(tabPanel).toHaveTextContent('Content 2');

    // Verify that the first tab's content is hidden
    expect(screen.queryByText('Content 1')).not.toBeVisible();
  });

  it('supports controlled mode with activeTab prop', () => {
    // Define mock tabs data
    const tabs = [
      { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
      { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div> },
      { id: 'tab3', label: 'Tab 3', content: <div>Content 3</div> }
    ];

    // Create a test component that uses Tabs in controlled mode
    const TestComponent = () => {
      const [activeTab, setActiveTab] = useState('tab2');
      return (
        <Tabs 
          tabs={tabs} 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
        />
      );
    };

    // Render the test component
    customRender(<TestComponent />);

    // Verify that the specified active tab is active
    const tabButtons = screen.getAllByRole('tab');
    expect(tabButtons[1]).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tabpanel')).toHaveTextContent('Content 2');

    // Click on another tab
    fireEvent.click(tabButtons[0]);

    // Verify that the active tab changes as expected
    expect(tabButtons[0]).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tabpanel')).toHaveTextContent('Content 1');
  });

  it('calls onTabChange when tab is changed', () => {
    // Define mock tabs data
    const tabs = [
      { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
      { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div> },
      { id: 'tab3', label: 'Tab 3', content: <div>Content 3</div> }
    ];

    // Create a mock function for onTabChange
    const onTabChange = jest.fn();
    
    // Render the Tabs component with the mock data and onTabChange prop
    customRender(<Tabs tabs={tabs} onTabChange={onTabChange} />);

    // Click on the second tab
    const tabButtons = screen.getAllByRole('tab');
    fireEvent.click(tabButtons[1]);

    // Verify that onTabChange was called with the correct tab ID
    expect(onTabChange).toHaveBeenCalledWith('tab2');
  });

  it('supports keyboard navigation', () => {
    // Define mock tabs data
    const tabs = [
      { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
      { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div> },
      { id: 'tab3', label: 'Tab 3', content: <div>Content 3</div> }
    ];

    // Render the Tabs component with the mock data
    customRender(<Tabs tabs={tabs} />);

    // Focus on the first tab
    const tabButtons = screen.getAllByRole('tab');
    tabButtons[0].focus();

    // Press the right arrow key
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'ArrowRight' });
    
    // Verify that the second tab becomes active
    expect(tabButtons[1]).toHaveAttribute('aria-selected', 'true');
    expect(document.activeElement).toBe(tabButtons[1]);

    // Press the right arrow key again
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'ArrowRight' });
    
    // Verify that the third tab becomes active
    expect(tabButtons[2]).toHaveAttribute('aria-selected', 'true');
    expect(document.activeElement).toBe(tabButtons[2]);

    // Press the left arrow key
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'ArrowLeft' });
    
    // Verify that the second tab becomes active again
    expect(tabButtons[1]).toHaveAttribute('aria-selected', 'true');
    expect(document.activeElement).toBe(tabButtons[1]);

    // Press the Home key
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'Home' });
    
    // Verify that the first tab becomes active
    expect(tabButtons[0]).toHaveAttribute('aria-selected', 'true');
    expect(document.activeElement).toBe(tabButtons[0]);

    // Press the End key
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'End' });
    
    // Verify that the last tab becomes active
    expect(tabButtons[2]).toHaveAttribute('aria-selected', 'true');
    expect(document.activeElement).toBe(tabButtons[2]);
  });

  it('supports vertical orientation', () => {
    // Define mock tabs data
    const tabs = [
      { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
      { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div> },
      { id: 'tab3', label: 'Tab 3', content: <div>Content 3</div> }
    ];

    // Render the Tabs component with vertical orientation
    customRender(<Tabs tabs={tabs} orientation="vertical" />);

    // Verify that the tabs container has the vertical class
    const tabsContainer = screen.getByRole('tablist').closest('.tabs-container');
    expect(tabsContainer).toHaveClass('tabs-vertical');

    // Verify that the tab list has the vertical class
    const tabList = screen.getByRole('tablist');
    expect(tabList).toHaveClass('tabs-list-vertical');

    // Focus on the first tab
    const tabButtons = screen.getAllByRole('tab');
    tabButtons[0].focus();

    // Press the down arrow key
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'ArrowDown' });
    
    // Verify that the second tab becomes active
    expect(tabButtons[1]).toHaveAttribute('aria-selected', 'true');
    
    // Press the up arrow key
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'ArrowUp' });
    
    // Verify that the first tab becomes active again
    expect(tabButtons[0]).toHaveAttribute('aria-selected', 'true');
  });

  it('skips disabled tabs during keyboard navigation', () => {
    // Define mock tabs data with a disabled tab
    const tabs = [
      { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
      { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div>, disabled: true },
      { id: 'tab3', label: 'Tab 3', content: <div>Content 3</div> }
    ];

    // Render the Tabs component with the mock data
    customRender(<Tabs tabs={tabs} />);

    // Focus on the first tab
    const tabButtons = screen.getAllByRole('tab');
    tabButtons[0].focus();

    // Press the right arrow key
    fireEvent.keyDown(document.activeElement as HTMLElement, { key: 'ArrowRight' });
    
    // Verify that the navigation skips the disabled tab and activates the next enabled tab
    expect(tabButtons[2]).toHaveAttribute('aria-selected', 'true');
    expect(document.activeElement).toBe(tabButtons[2]);
  });

  it('has no accessibility violations', async () => {
    // Define mock tabs data
    const tabs = [
      { id: 'tab1', label: 'Tab 1', content: <div>Content 1</div> },
      { id: 'tab2', label: 'Tab 2', content: <div>Content 2</div> },
      { id: 'tab3', label: 'Tab 3', content: <div>Content 3</div> }
    ];

    // Render the Tabs component with the mock data
    const { container } = customRender(<Tabs tabs={tabs} />);
    
    // Run axe accessibility tests on the rendered component
    const results = await axe(container);
    
    // Verify that there are no accessibility violations
    expect(results).toHaveNoViolations();
  });
});