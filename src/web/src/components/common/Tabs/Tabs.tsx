import React, { useState, useEffect, useRef, useCallback, KeyboardEvent } from 'react'; // ^18.2.0

/**
 * Interface defining the structure of a tab item
 */
interface Tab {
  id: string;
  label: string | React.ReactNode;
  content: React.ReactNode;
  disabled?: boolean;
}

/**
 * Props interface for the Tabs component
 */
interface TabsProps {
  /** Array of tab objects with id, label, content, and optional disabled flag */
  tabs: Tab[];
  /** ID of the initially active tab (uncontrolled mode) */
  defaultActiveTab?: string;
  /** ID of the active tab (controlled mode) */
  activeTab?: string;
  /** Callback function when active tab changes */
  onTabChange?: (tabId: string) => void;
  /** Visual variant of the tabs */
  variant?: 'primary' | 'secondary';
  /** Size variant of the tabs */
  size?: 'sm' | 'md' | 'lg';
  /** Orientation of the tab list */
  orientation?: 'horizontal' | 'vertical';
  /** Additional CSS class for the root element */
  className?: string;
  /** Additional CSS class for the tab list element */
  tabListClassName?: string;
  /** Additional CSS class for the tab panel element */
  tabPanelClassName?: string;
}

/**
 * A component that provides a tabbed interface for organizing content into separate views.
 * Supports horizontal and vertical orientations, different visual variants, sizes,
 * and is fully accessible with keyboard navigation and ARIA attributes.
 */
const Tabs: React.FC<TabsProps> = ({
  tabs,
  defaultActiveTab,
  activeTab,
  onTabChange,
  variant = 'primary',
  size = 'md',
  orientation = 'horizontal',
  className = '',
  tabListClassName = '',
  tabPanelClassName = '',
}) => {
  // State for the active tab (controlled or uncontrolled)
  const [internalActiveTab, setInternalActiveTab] = useState<string>(
    defaultActiveTab || tabs[0]?.id || ''
  );

  // Refs for DOM elements
  const tabListRef = useRef<HTMLDivElement>(null);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  // Initialize tabRefs array based on tabs length
  useEffect(() => {
    tabRefs.current = tabRefs.current.slice(0, tabs.length);
    // Fill with nulls if needed
    while (tabRefs.current.length < tabs.length) {
      tabRefs.current.push(null);
    }
  }, [tabs.length]);

  // Update internal state when controlled prop changes
  useEffect(() => {
    if (activeTab !== undefined) {
      setInternalActiveTab(activeTab);
    }
  }, [activeTab]);

  // Get the index of the currently active tab
  const getActiveTabIndex = (): number => {
    const activeIndex = tabs.findIndex(tab => tab.id === internalActiveTab);
    return activeIndex >= 0 ? activeIndex : 0;
  };

  // Focus a tab by index
  const focusTab = (index: number) => {
    const tab = tabRefs.current[index];
    if (tab && !tabs[index].disabled) {
      tab.focus();
    }
  };

  // Handle tab click
  const handleTabClick = useCallback((tabId: string) => {
    // Check if tab is disabled
    if (tabs.find(tab => tab.id === tabId)?.disabled) {
      return;
    }

    // Update internal state if uncontrolled
    if (activeTab === undefined) {
      setInternalActiveTab(tabId);
    }

    // Call the onTabChange callback if provided
    if (onTabChange) {
      onTabChange(tabId);
    }
  }, [tabs, activeTab, onTabChange]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: KeyboardEvent<HTMLDivElement>) => {
    const currentIndex = getActiveTabIndex();
    let newIndex = currentIndex;

    switch (event.key) {
      // Horizontal navigation
      case 'ArrowRight':
        if (orientation === 'horizontal') {
          newIndex = (currentIndex + 1) % tabs.length;
          // Skip disabled tabs
          while (tabs[newIndex].disabled && newIndex !== currentIndex) {
            newIndex = (newIndex + 1) % tabs.length;
          }
          event.preventDefault();
        }
        break;
      case 'ArrowLeft':
        if (orientation === 'horizontal') {
          newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
          // Skip disabled tabs
          while (tabs[newIndex].disabled && newIndex !== currentIndex) {
            newIndex = (newIndex - 1 + tabs.length) % tabs.length;
          }
          event.preventDefault();
        }
        break;
      
      // Vertical navigation
      case 'ArrowDown':
        if (orientation === 'vertical') {
          newIndex = (currentIndex + 1) % tabs.length;
          // Skip disabled tabs
          while (tabs[newIndex].disabled && newIndex !== currentIndex) {
            newIndex = (newIndex + 1) % tabs.length;
          }
          event.preventDefault();
        }
        break;
      case 'ArrowUp':
        if (orientation === 'vertical') {
          newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
          // Skip disabled tabs
          while (tabs[newIndex].disabled && newIndex !== currentIndex) {
            newIndex = (newIndex - 1 + tabs.length) % tabs.length;
          }
          event.preventDefault();
        }
        break;
      
      // First/Last navigation
      case 'Home':
        newIndex = 0;
        // Skip disabled tabs
        while (tabs[newIndex].disabled && newIndex < tabs.length - 1) {
          newIndex++;
        }
        event.preventDefault();
        break;
      case 'End':
        newIndex = tabs.length - 1;
        // Skip disabled tabs
        while (tabs[newIndex].disabled && newIndex > 0) {
          newIndex--;
        }
        event.preventDefault();
        break;
        
      default:
        return; // Do nothing for other keys
    }

    // If index changed and new tab is not disabled, switch to it
    if (newIndex !== currentIndex && !tabs[newIndex].disabled) {
      handleTabClick(tabs[newIndex].id);
      focusTab(newIndex);
    }
  }, [tabs, orientation, handleTabClick]);

  return (
    <div className={`tabs-container ${className} ${orientation === 'vertical' ? 'tabs-vertical' : ''}`}>
      <div
        ref={tabListRef}
        role="tablist"
        className={`tabs-list ${tabListClassName} tabs-${variant} tabs-${size} ${
          orientation === 'vertical' ? 'tabs-list-vertical' : 'tabs-list-horizontal'
        }`}
        aria-orientation={orientation}
        onKeyDown={handleKeyDown}
      >
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            ref={el => (tabRefs.current[index] = el)}
            role="tab"
            className={`tab-button ${internalActiveTab === tab.id ? 'active' : ''} ${
              tab.disabled ? 'disabled' : ''
            }`}
            aria-selected={internalActiveTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            tabIndex={internalActiveTab === tab.id ? 0 : -1}
            disabled={tab.disabled}
            onClick={() => handleTabClick(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className={`tab-panels ${tabPanelClassName}`}>
        {tabs.map(tab => (
          <div
            key={tab.id}
            id={`panel-${tab.id}`}
            role="tabpanel"
            className={`tab-panel ${internalActiveTab === tab.id ? 'active' : 'hidden'}`}
            aria-labelledby={`tab-${tab.id}`}
            tabIndex={0}
            hidden={internalActiveTab !== tab.id}
          >
            {tab.content}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tabs;