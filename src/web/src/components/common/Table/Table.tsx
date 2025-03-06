import React, { useState, useEffect, useMemo, useCallback } from 'react'; // ^18.2.0
import classNames from 'classnames'; // ^2.3.2
import Spinner from '../Spinner';
import Pagination from '../Pagination';
import Icon from '../Icon';
import usePagination from '../../../hooks/usePagination';

/**
 * Interface defining the structure of a table column configuration
 */
export interface TableColumn<T> {
  key: string;
  header: string;
  sortable?: boolean;
  width?: string;
  align?: string;
  render?: (item: T, index: number) => React.ReactNode;
  className?: string;
}

/**
 * Interface defining the props for the Table component
 */
export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  className?: string;
  isLoading?: boolean;
  isStriped?: boolean;
  isBordered?: boolean;
  isHoverable?: boolean;
  isSortable?: boolean;
  isPaginated?: boolean;
  itemsPerPage?: number;
  emptyMessage?: string;
  storageKey?: string;
  onRowClick?: (item: T, index: number) => void;
  sortColumn?: string;
  sortDirection?: string;
  onSort?: (column: string, direction: string) => void;
  showHeader?: boolean;
  size?: string;
}

/**
 * Sorts the table data based on the current sort column and direction
 * 
 * @param data - Array of data items to sort
 * @param sortColumn - Column key to sort by
 * @param sortDirection - Sort direction ('asc', 'desc', or 'none')
 * @returns Sorted array of data items
 */
function getSortedData<T>(data: T[], sortColumn: string, sortDirection: string): T[] {
  // Return original data if no sorting is needed
  if (!sortColumn || sortDirection === 'none') {
    return data;
  }
  
  // Create a copy of the array to avoid mutating the original
  const dataCopy = [...data];
  
  // Sort the copied array
  return dataCopy.sort((a, b) => {
    // Get values to compare (supporting nested properties with dot notation)
    const aValue = sortColumn.split('.').reduce((obj, key) => obj && obj[key], a as any);
    const bValue = sortColumn.split('.').reduce((obj, key) => obj && obj[key], b as any);
    
    // Handle different data types
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    }
    
    // Handle dates
    if (aValue instanceof Date && bValue instanceof Date) {
      return sortDirection === 'asc' 
        ? aValue.getTime() - bValue.getTime() 
        : bValue.getTime() - aValue.getTime();
    }
    
    // Handle strings and everything else
    const aString = String(aValue || '').toLowerCase();
    const bString = String(bValue || '').toLowerCase();
    
    return sortDirection === 'asc' 
      ? aString.localeCompare(bString) 
      : bString.localeCompare(aString);
  });
}

/**
 * A reusable table component that displays data in rows and columns with support for
 * sorting, pagination, and custom rendering
 */
const Table = <T extends object>({
  data,
  columns,
  className,
  isLoading = false,
  isStriped = false,
  isBordered = false,
  isHoverable = false,
  isSortable = false,
  isPaginated = false,
  itemsPerPage = 10,
  emptyMessage = 'No data available',
  storageKey,
  onRowClick,
  sortColumn: externalSortColumn,
  sortDirection: externalSortDirection = 'none',
  onSort,
  showHeader = true,
  size = 'md',
}: TableProps<T>): React.ReactElement => {
  // State for internal sorting (used when not controlled externally)
  const [internalSortColumn, setInternalSortColumn] = useState<string>('');
  const [internalSortDirection, setInternalSortDirection] = useState<string>('none');
  
  // Determine whether to use controlled or uncontrolled sorting
  const isControlledSort = externalSortColumn !== undefined && onSort !== undefined;
  const currentSortColumn = isControlledSort ? externalSortColumn : internalSortColumn;
  const currentSortDirection = isControlledSort ? externalSortDirection : internalSortDirection;
  
  // Use pagination hook if pagination is enabled
  const pagination = isPaginated 
    ? usePagination({
        totalItems: data.length,
        itemsPerPage,
        initialPage: 1,
        maxVisiblePages: 5,
        storageKey: storageKey ? `${storageKey}_pagination` : undefined,
      })
    : null;
  
  // Sort the data
  const sortedData = useMemo(() => 
    getSortedData(data, currentSortColumn, currentSortDirection),
    [data, currentSortColumn, currentSortDirection]
  );
  
  // Apply pagination to the sorted data if needed
  const displayData = useMemo(() => {
    if (!isPaginated || !pagination) return sortedData;
    
    const { startIndex, endIndex } = pagination;
    return sortedData.slice(startIndex, endIndex + 1);
  }, [sortedData, isPaginated, pagination]);
  
  // Handle column header click for sorting
  const handleHeaderClick = useCallback((column: TableColumn<T>) => {
    if (!isSortable || !column.sortable) return;
    
    let newDirection = 'asc';
    
    // Toggle direction if the same column is clicked
    if (column.key === currentSortColumn) {
      if (currentSortDirection === 'asc') {
        newDirection = 'desc';
      } else if (currentSortDirection === 'desc') {
        newDirection = 'none';
      }
    }
    
    if (isControlledSort && onSort) {
      // Call external handler for controlled mode
      onSort(column.key, newDirection);
    } else {
      // Update internal state for uncontrolled mode
      setInternalSortColumn(newDirection === 'none' ? '' : column.key);
      setInternalSortDirection(newDirection);
    }
  }, [isSortable, currentSortColumn, currentSortDirection, isControlledSort, onSort]);
  
  // Get appropriate CSS classes for the table
  const tableClasses = classNames(
    'table',
    `table--${size}`,
    {
      'table--striped': isStriped,
      'table--bordered': isBordered,
      'table--hoverable': isHoverable,
    },
    className
  );
  
  // If there's no data and we're not loading, show the empty message
  if (data.length === 0 && !isLoading) {
    return (
      <div className="table__empty" role="status">
        {emptyMessage}
      </div>
    );
  }
  
  return (
    <div className="table-container">
      <table 
        className={tableClasses}
        role="table"
        aria-busy={isLoading}
        aria-rowcount={data.length}
        aria-colcount={columns.length}
      >
        {showHeader && (
          <thead className="table__header">
            <tr className="table__row" role="row">
              {columns.map((column) => {
                const isSortableColumn = isSortable && column.sortable;
                const isColumnSorted = isSortableColumn && currentSortColumn === column.key;
                
                const headerCellClasses = classNames(
                  'table__header-cell',
                  {
                    'table__header-cell--sortable': isSortableColumn,
                    'table__header-cell--sorted': isColumnSorted,
                    [`table__header-cell--align-${column.align}`]: column.align,
                  },
                  column.className
                );
                
                const sortIcon = isColumnSorted
                  ? currentSortDirection === 'asc' 
                    ? 'arrow-up' 
                    : 'arrow-down'
                  : undefined;
                
                const sortLabel = isSortableColumn
                  ? `Sort by ${column.header} ${
                      isColumnSorted
                        ? currentSortDirection === 'asc'
                          ? '(currently ascending)'
                          : '(currently descending)'
                        : ''
                    }`
                  : undefined;
                
                return (
                  <th 
                    key={column.key}
                    className={headerCellClasses}
                    style={{ width: column.width }}
                    onClick={() => isSortableColumn && handleHeaderClick(column)}
                    aria-sort={
                      isColumnSorted
                        ? currentSortDirection === 'asc'
                          ? 'ascending'
                          : 'descending'
                        : undefined
                    }
                    aria-label={sortLabel}
                    role="columnheader"
                    tabIndex={isSortableColumn ? 0 : undefined}
                  >
                    <div className="table__header-content">
                      <span>{column.header}</span>
                      {isSortableColumn && (
                        <span className="table__sort-icon">
                          {isColumnSorted ? (
                            <Icon name={sortIcon} size="sm" aria-hidden="true" />
                          ) : (
                            <Icon name="arrow-up" size="sm" className="table__sort-icon--inactive" aria-hidden="true" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
        )}
        
        <tbody className="table__body">
          {displayData.map((item, rowIndex) => {
            const rowClasses = classNames(
              'table__row',
              {
                'table__row--clickable': !!onRowClick,
              }
            );
            
            return (
              <tr 
                key={rowIndex}
                className={rowClasses}
                onClick={() => onRowClick && onRowClick(item, rowIndex)}
                tabIndex={onRowClick ? 0 : undefined}
                role="row"
              >
                {columns.map((column, colIndex) => {
                  const cellClasses = classNames(
                    'table__cell',
                    {
                      [`table__cell--align-${column.align}`]: column.align,
                    },
                    column.className
                  );
                  
                  let cellContent;
                  if (column.render) {
                    // Use custom render function if provided
                    cellContent = column.render(item, rowIndex);
                  } else {
                    // Otherwise display the value at the key path
                    cellContent = column.key.split('.').reduce((obj, key) => obj && obj[key], item as any);
                  }
                  
                  return (
                    <td 
                      key={`${rowIndex}-${colIndex}`} 
                      className={cellClasses}
                      role="cell"
                    >
                      {cellContent}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
      
      {isLoading && (
        <div className="table__loading" aria-hidden="true">
          <Spinner size="lg" ariaLabel="Loading table data..." />
        </div>
      )}
      
      {isPaginated && pagination && data.length > 0 && (
        <div className="table__pagination">
          <Pagination
            totalItems={data.length}
            itemsPerPage={itemsPerPage}
            initialPage={pagination.currentPage}
            onPageChange={pagination.goToPage}
            className="table-pagination"
            showItemCounts={true}
            storageKey={storageKey ? `${storageKey}_pagination` : undefined}
          />
        </div>
      )}
    </div>
  );
};

export default Table;