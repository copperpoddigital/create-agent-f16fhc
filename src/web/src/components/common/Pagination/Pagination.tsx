import React from 'react'; // ^18.2.0
import classNames from 'classnames'; // ^2.3.2
import Button from '../Button';
import usePagination from '../../../hooks/usePagination';

/**
 * Props interface for the Pagination component
 */
export interface PaginationProps {
  /** Total number of items to paginate */
  totalItems: number;
  /** Number of items to display per page */
  itemsPerPage: number;
  /** Initial page to display */
  initialPage?: number;
  /** Maximum number of page buttons to display */
  maxVisiblePages?: number;
  /** Additional CSS class names to apply to the component */
  className?: string;
  /** Size of the pagination controls: 'sm', 'md', or 'lg' */
  size?: string;
  /** Whether to display item count information */
  showItemCounts?: boolean;
  /** Key to use for persisting pagination state in localStorage */
  storageKey?: string;
  /** Callback function called when the page changes */
  onPageChange?: (page: number) => void;
}

/**
 * A component that renders pagination controls for navigating through paginated data.
 * Provides page numbers, previous/next buttons, and optionally shows item count information.
 */
const Pagination: React.FC<PaginationProps> = ({
  totalItems,
  itemsPerPage,
  initialPage = 1,
  maxVisiblePages = 5,
  className,
  size = 'md',
  showItemCounts = false,
  storageKey,
  onPageChange
}) => {
  // Use the usePagination hook to manage pagination state
  const {
    currentPage,
    totalPages,
    visiblePageNumbers,
    goToPage,
    goToNextPage,
    goToPreviousPage,
    isFirstPage,
    isLastPage,
    startIndex,
    endIndex
  } = usePagination({
    totalItems,
    itemsPerPage,
    initialPage,
    maxVisiblePages,
    storageKey
  });

  // Handle page change and call the onPageChange callback if provided
  const handlePageChange = (page: number) => {
    goToPage(page);
    if (onPageChange) {
      onPageChange(page);
    }
  };

  // Don't render pagination if there's only one page or no items
  if (totalPages <= 1 || totalItems === 0) {
    return null;
  }

  // Determine button size for the Button component
  const buttonSize = size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'md';

  return (
    <nav 
      className={classNames('pagination', `pagination--${size}`, className)}
      aria-label="Pagination"
    >
      {showItemCounts && totalItems > 0 && (
        <div className="pagination__info" aria-live="polite">
          Showing {startIndex + 1}-{Math.min(endIndex + 1, totalItems)} of {totalItems}
        </div>
      )}

      <div className="pagination__controls">
        {/* Previous button */}
        <Button
          variant="outline-primary"
          size={buttonSize}
          disabled={isFirstPage}
          onClick={() => handlePageChange(currentPage - 1)}
          aria-label="Go to previous page"
          className="pagination__btn pagination__btn--prev"
        >
          &laquo; Previous
        </Button>

        {/* Page number buttons */}
        <div className="pagination__pages" role="group" aria-label="Pagination pages">
          {visiblePageNumbers.map(pageNumber => (
            <Button
              key={pageNumber}
              variant={pageNumber === currentPage ? 'primary' : 'outline-primary'}
              size={buttonSize}
              onClick={() => handlePageChange(pageNumber)}
              aria-label={`Page ${pageNumber}`}
              aria-current={pageNumber === currentPage ? 'page' : undefined}
              className={classNames(
                'pagination__btn',
                'pagination__btn--page',
                { 'pagination__btn--active': pageNumber === currentPage }
              )}
            >
              {pageNumber}
            </Button>
          ))}
        </div>

        {/* Next button */}
        <Button
          variant="outline-primary"
          size={buttonSize}
          disabled={isLastPage}
          onClick={() => handlePageChange(currentPage + 1)}
          aria-label="Go to next page"
          className="pagination__btn pagination__btn--next"
        >
          Next &raquo;
        </Button>
      </div>
    </nav>
  );
};

export default Pagination;