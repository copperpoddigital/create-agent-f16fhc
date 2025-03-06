import React from 'react';
import { vi } from 'vitest';
import { render, screen, fireEvent } from '../../../utils/test-utils';
import PageHeader from './PageHeader';
import Button from '../../common/Button';

// Mock the useMediaQuery hook to control isMobile value
vi.mock('../../../hooks/useMediaQuery', () => ({
  default: vi.fn()
}));

// Import the mocked module to control its return value
import useMediaQuery from '../../../hooks/useMediaQuery';

/**
 * Mocks the useMediaQuery hook to simulate different screen sizes
 * @param matches Whether the media query should match
 */
function mockMediaQuery(matches: boolean): void {
  (useMediaQuery as any).mockReturnValue(matches);
}

describe('PageHeader', () => {
  // Reset mocks before each test
  beforeEach(() => {
    vi.clearAllMocks();
    // Default to desktop view
    mockMediaQuery(false);
  });

  it('renders the title correctly', () => {
    render(<PageHeader title="Test Title" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Test Title');
  });

  it('renders action buttons when provided', () => {
    const testActions = [
      <Button key="1">Action 1</Button>,
      <Button key="2">Action 2</Button>
    ];

    render(<PageHeader title="Test Title" actions={testActions} />);
    
    expect(screen.getByText('Action 1')).toBeInTheDocument();
    expect(screen.getByText('Action 2')).toBeInTheDocument();
    expect(screen.getByRole('toolbar', { name: 'Page actions' })).toBeInTheDocument();
  });

  it('handles button clicks correctly', () => {
    const handleClick = vi.fn();
    const testActions = [
      <Button key="1" onClick={handleClick}>Action Button</Button>
    ];

    render(<PageHeader title="Test Title" actions={testActions} />);
    
    const button = screen.getByText('Action Button');
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies custom className when provided', () => {
    const customClass = 'custom-header-class';
    render(<PageHeader title="Test Title" className={customClass} />);
    
    const header = screen.getByRole('banner'); // header element has an implicit 'banner' role
    expect(header).toHaveClass(customClass);
    expect(header).toHaveClass('page-header');
  });

  it('renders differently on mobile screens', () => {
    // Mock mobile view
    mockMediaQuery(true);
    
    const testActions = [
      <Button key="1">Mobile Action</Button>
    ];

    render(<PageHeader title="Mobile Title" actions={testActions} />);
    
    const header = screen.getByRole('banner');
    expect(header).toHaveClass('page-header--mobile');
    
    const actionContainer = screen.getByRole('toolbar');
    expect(actionContainer).toHaveClass('page-header__actions--mobile');
    
    // Check that action items also have mobile class
    const actionItem = screen.getByText('Mobile Action').closest('.page-header__action');
    expect(actionItem).toHaveClass('page-header__action--mobile');
  });

  it('does not render actions container when no actions are provided', () => {
    render(<PageHeader title="Test Title" />);
    expect(screen.queryByRole('toolbar')).not.toBeInTheDocument();
  });
});