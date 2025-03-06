import React from 'react';
import { render, screen, fireEvent, waitFor, userEvent } from '../../utils/test-utils';
import '@testing-library/jest-dom/extend-expect';
import Pagination from './Pagination';

describe('Pagination Component', () => {
  test('renders with default props', () => {
    render(<Pagination totalItems={50} itemsPerPage={10} />);
    
    // Check that pagination navigation exists
    const paginationNav = screen.getByRole('navigation', { name: /pagination/i });
    expect(paginationNav).toBeInTheDocument();
    
    // Check that Previous button is rendered and disabled (since we're on page 1)
    const prevButton = screen.getByRole('button', { name: /go to previous page/i });
    expect(prevButton).toBeInTheDocument();
    expect(prevButton).toBeDisabled();
    
    // Check that page 1 button is rendered and has active state
    const page1Button = screen.getByRole('button', { name: /page 1/i });
    expect(page1Button).toBeInTheDocument();
    expect(page1Button).toHaveClass('pagination__btn--active');
    
    // Check that Next button is rendered and enabled
    const nextButton = screen.getByRole('button', { name: /go to next page/i });
    expect(nextButton).toBeInTheDocument();
    expect(nextButton).not.toBeDisabled();
  });

  test('handles page changes correctly', () => {
    const onPageChange = jest.fn();
    render(
      <Pagination 
        totalItems={50} 
        itemsPerPage={10} 
        onPageChange={onPageChange} 
      />
    );
    
    // Click on page 2 button
    const page2Button = screen.getByRole('button', { name: /page 2/i });
    fireEvent.click(page2Button);
    expect(onPageChange).toHaveBeenCalledWith(2);
    
    // Click on Next button
    const nextButton = screen.getByRole('button', { name: /go to next page/i });
    fireEvent.click(nextButton);
    expect(onPageChange).toHaveBeenCalledWith(3);
    
    // Click on Previous button (we're simulating being on page 3 now)
    const prevButton = screen.getByRole('button', { name: /go to previous page/i });
    fireEvent.click(prevButton);
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  test('disables buttons appropriately', () => {
    // Test first page - Previous should be disabled
    const { rerender } = render(
      <Pagination 
        totalItems={50} 
        itemsPerPage={10} 
        initialPage={1} 
      />
    );
    
    let prevButton = screen.getByRole('button', { name: /go to previous page/i });
    let nextButton = screen.getByRole('button', { name: /go to next page/i });
    
    expect(prevButton).toBeDisabled();
    expect(nextButton).not.toBeDisabled();
    
    // Test last page - Next should be disabled
    rerender(
      <Pagination 
        totalItems={50} 
        itemsPerPage={10} 
        initialPage={5} 
      />
    );
    
    prevButton = screen.getByRole('button', { name: /go to previous page/i });
    nextButton = screen.getByRole('button', { name: /go to next page/i });
    
    expect(prevButton).not.toBeDisabled();
    expect(nextButton).toBeDisabled();
  });

  test('shows correct number of page buttons', () => {
    // Create a pagination with many pages but limit visible pages to 5
    render(
      <Pagination 
        totalItems={200} 
        itemsPerPage={10} 
        maxVisiblePages={5} 
      />
    );
    
    // Should initially show 5 page buttons (1-5) out of 20 total
    const pageButtons = screen.getAllByRole('button').filter(button => 
      button.getAttribute('aria-label')?.startsWith('Page ')
    );
    expect(pageButtons).toHaveLength(5);
    
    // Check that we see the expected range (1-5)
    expect(pageButtons[0]).toHaveTextContent('1');
    expect(pageButtons[4]).toHaveTextContent('5');
    
    // Click on the last visible page to shift the range
    fireEvent.click(pageButtons[4]); // Click page 5
    
    // Now we should see a different set of pages centered around page 5
    // Based on the usePagination implementation, we might see pages 3-7
    const updatedPageButtons = screen.getAllByRole('button').filter(button => 
      button.getAttribute('aria-label')?.startsWith('Page ')
    );
    expect(updatedPageButtons).toHaveLength(5);
    
    // The first button should no longer be page 1
    expect(updatedPageButtons[0]).not.toHaveTextContent('1');
  });

  test('shows item counts when enabled', () => {
    render(
      <Pagination 
        totalItems={100} 
        itemsPerPage={10} 
        showItemCounts={true} 
      />
    );
    
    // Check that item count text is displayed and shows correct range
    const itemCountText = screen.getByText(/showing 1-10 of 100/i);
    expect(itemCountText).toBeInTheDocument();
  });

  test('applies size classes correctly', () => {
    const { rerender } = render(
      <Pagination 
        totalItems={50} 
        itemsPerPage={10} 
        size="sm" 
      />
    );
    
    // Check small size class
    const paginationSm = screen.getByRole('navigation');
    expect(paginationSm).toHaveClass('pagination--sm');
    
    // Check large size class
    rerender(
      <Pagination 
        totalItems={50} 
        itemsPerPage={10} 
        size="lg" 
      />
    );
    
    const paginationLg = screen.getByRole('navigation');
    expect(paginationLg).toHaveClass('pagination--lg');
  });

  test('is accessible', () => {
    render(<Pagination totalItems={50} itemsPerPage={10} />);
    
    // Check navigation has proper ARIA attributes
    const navigation = screen.getByRole('navigation');
    expect(navigation).toHaveAttribute('aria-label', 'Pagination');
    
    // Check that the pages group has appropriate ARIA attributes
    const pagesGroup = screen.getByRole('group', { name: /pagination pages/i });
    expect(pagesGroup).toBeInTheDocument();
    
    // Check buttons have accessible labels
    const prevButton = screen.getByRole('button', { name: /go to previous page/i });
    expect(prevButton).toBeInTheDocument();
    
    const nextButton = screen.getByRole('button', { name: /go to next page/i });
    expect(nextButton).toBeInTheDocument();
    
    // Check page buttons
    const pageButton = screen.getByRole('button', { name: /page 1/i });
    expect(pageButton).toBeInTheDocument();
    expect(pageButton).toHaveAttribute('aria-current', 'page');
    
    // Test keyboard navigation through the pagination controls
    const user = userEvent.setup();
    fireEvent.tab(navigation);
    expect(prevButton).toHaveFocus();
    fireEvent.tab(prevButton);
    expect(pageButton).toHaveFocus();
  });
});