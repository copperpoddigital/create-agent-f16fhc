import { useState, useEffect, useMemo, useCallback } from 'react'; // ^18.2.0
import useLocalStorage from './useLocalStorage';

/**
 * Options for configuring the pagination behavior
 */
interface PaginationOptions {
  totalItems: number;
  itemsPerPage: number;
  initialPage?: number;
  maxVisiblePages?: number;
  storageKey?: string;
}

/**
 * Result object returned by the usePagination hook
 */
interface PaginationResult {
  currentPage: number;
  totalPages: number;
  visiblePageNumbers: number[];
  goToPage: (page: number) => void;
  goToNextPage: () => void;
  goToPreviousPage: () => void;
  isFirstPage: boolean;
  isLastPage: boolean;
  startIndex: number;
  endIndex: number;
}

/**
 * A custom React hook that provides pagination functionality for data collections.
 * This hook manages pagination state, calculates page ranges, and provides navigation
 * functions for paginated data display.
 *
 * @param options - Configuration options for pagination behavior
 * @returns Object with pagination state and navigation functions
 */
const usePagination = ({
  totalItems,
  itemsPerPage,
  initialPage = 1,
  maxVisiblePages = 5,
  storageKey
}: PaginationOptions): PaginationResult => {
  // Calculate total pages
  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
  
  // Use localStorage for persistence if storageKey is provided
  const [currentPage, setCurrentPage] = storageKey
    ? useLocalStorage<number>(`${storageKey}_page`, initialPage)
    : useState<number>(initialPage);
  
  // Function to navigate to a specific page
  const goToPage = useCallback((page: number) => {
    const pageNumber = Math.max(1, Math.min(page, totalPages));
    setCurrentPage(pageNumber);
  }, [totalPages, setCurrentPage]);
  
  // Function to navigate to the next page
  const goToNextPage = useCallback(() => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  }, [currentPage, totalPages, setCurrentPage]);
  
  // Function to navigate to the previous page
  const goToPreviousPage = useCallback(() => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  }, [currentPage, setCurrentPage]);
  
  // Calculate if current page is first or last page
  const isFirstPage = currentPage === 1;
  const isLastPage = currentPage === totalPages;
  
  // Calculate start and end index for the current page
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = Math.min(startIndex + itemsPerPage - 1, totalItems - 1);
  
  // Calculate visible page numbers for pagination controls
  const visiblePageNumbers = useMemo(() => {
    // Calculate how many pages to show on each side of the current page
    const halfVisible = Math.floor(maxVisiblePages / 2);
    
    // Calculate start and end pages to display
    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // Adjust startPage if endPage is at the maximum
    if (endPage === totalPages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // Generate the array of page numbers to display
    const pages = [];
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    return pages;
  }, [currentPage, totalPages, maxVisiblePages]);
  
  // Reset to first page when totalItems or itemsPerPage changes
  useEffect(() => {
    setCurrentPage(1);
  }, [totalItems, itemsPerPage, setCurrentPage]);
  
  // Ensure currentPage is valid when total pages changes
  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage, setCurrentPage]);
  
  return {
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
  };
};

export default usePagination;