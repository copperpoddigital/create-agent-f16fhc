import React from 'react';
import { vi } from 'vitest'; // v0.30.1
import Table from './Table';
import { customRender, screen, fireEvent, waitFor, userEvent } from '../../../utils/test-utils';

/**
 * Helper function to set up the test environment with mock data and render the Table component
 */
const setup = (props = {}) => {
  // Create mock data for the table
  const mockData = [
    { id: 1, name: 'Item 1', value: 100, date: new Date('2023-01-01') },
    { id: 2, name: 'Item 2', value: 200, date: new Date('2023-01-02') },
    { id: 3, name: 'Item 3', value: 300, date: new Date('2023-01-03') },
    { id: 4, name: 'Item 4', value: 400, date: new Date('2023-01-04') },
    { id: 5, name: 'Item 5', value: 500, date: new Date('2023-01-05') },
  ];

  // Define column configurations
  const mockColumns = [
    { key: 'id', header: 'ID', sortable: true },
    { key: 'name', header: 'Name', sortable: true },
    { key: 'value', header: 'Value', sortable: true },
    { key: 'date', header: 'Date', sortable: true },
  ];

  // Merge default props with provided props
  const defaultProps = {
    data: mockData,
    columns: mockColumns,
  };
  const finalProps = { ...defaultProps, ...props };

  // Render the Table component with customRender
  const result = customRender(<Table {...finalProps} />);

  return {
    ...result,
    mockData,
    mockColumns,
  };
};

describe('Table Component', () => {
  it('renders correctly with basic props', () => {
    setup();
    
    // Check that the table element is in the document
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
    
    // Verify that the column headers are rendered correctly
    const headers = screen.getAllByRole('columnheader');
    expect(headers).toHaveLength(4); // 4 columns
    expect(headers[0]).toHaveTextContent('ID');
    expect(headers[1]).toHaveTextContent('Name');
    
    // Verify that the correct number of rows are rendered
    const rows = screen.getAllByRole('row');
    expect(rows).toHaveLength(6); // 5 data rows + 1 header row
  });

  it('displays loading state correctly', () => {
    setup({ isLoading: true });
    
    // Check that the loading indicator is displayed
    const loadingSpinner = screen.getByLabelText('Loading table data...');
    expect(loadingSpinner).toBeInTheDocument();
    
    // Verify that the table content is still visible behind the loading overlay
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
  });

  it('displays empty message when data is empty', () => {
    setup({ data: [] });
    
    // Check that the empty message is displayed
    const emptyMessage = screen.getByRole('status');
    expect(emptyMessage).toHaveTextContent('No data available');
    
    // Verify that no table rows are rendered
    const table = screen.queryByRole('table');
    expect(table).not.toBeInTheDocument();
  });

  it('applies styling props correctly', () => {
    setup({
      isStriped: true,
      isBordered: true,
      isHoverable: true,
    });
    
    // Check that the appropriate CSS classes are applied to the table element
    const table = screen.getByRole('table');
    expect(table).toHaveClass('table--striped');
    expect(table).toHaveClass('table--bordered');
    expect(table).toHaveClass('table--hoverable');
  });

  it('handles row click events', () => {
    // Create a mock function for onRowClick
    const onRowClick = vi.fn();
    const { mockData } = setup({ onRowClick });
    
    // Get all rows (excluding header row)
    const rows = screen.getAllByRole('row').slice(1);
    
    // Simulate clicking on a table row
    fireEvent.click(rows[0]);
    
    // Verify that the mock function was called with the correct arguments
    expect(onRowClick).toHaveBeenCalledTimes(1);
    expect(onRowClick).toHaveBeenCalledWith(mockData[0], 0);
  });

  it('sorts data when clicking on sortable column headers', async () => {
    setup({ isSortable: true });
    
    // Get all header cells
    const headers = screen.getAllByRole('columnheader');
    
    // Simulate clicking on a sortable column header
    fireEvent.click(headers[0]); // ID column
    
    // Verify that the sort indicator is displayed
    expect(headers[0]).toHaveAttribute('aria-sort', 'ascending');
    
    // Get all cells in the first column
    let idCells = screen.getAllByRole('cell').filter((_, index) => index % 4 === 0);
    
    // Verify that the data is sorted correctly (already in ascending order by default)
    expect(idCells[0]).toHaveTextContent('1');
    expect(idCells[4]).toHaveTextContent('5');
    
    // Simulate clicking on the same header again
    fireEvent.click(headers[0]);
    
    // Verify that the sort direction is reversed
    expect(headers[0]).toHaveAttribute('aria-sort', 'descending');
    
    // Get cells again (they should now be in reverse order)
    await waitFor(() => {
      idCells = screen.getAllByRole('cell').filter((_, index) => index % 4 === 0);
      expect(idCells[0]).toHaveTextContent('5');
      expect(idCells[4]).toHaveTextContent('1');
    });
  });

  it('calls onSort callback when sorting changes', () => {
    // Create a mock function for onSort
    const onSort = vi.fn();
    setup({ isSortable: true, onSort });
    
    // Get all header cells
    const headers = screen.getAllByRole('columnheader');
    
    // Simulate clicking on a sortable column header
    fireEvent.click(headers[1]); // Name column
    
    // Verify that the mock function was called with the correct arguments
    expect(onSort).toHaveBeenCalledTimes(1);
    expect(onSort).toHaveBeenCalledWith('name', 'asc');
    
    // Simulate clicking on the same header again
    fireEvent.click(headers[1]);
    
    // Verify that the mock function was called with updated sort direction
    expect(onSort).toHaveBeenCalledTimes(2);
    expect(onSort).toHaveBeenCalledWith('name', 'desc');
  });

  it('paginates data correctly', async () => {
    // Create more data for pagination testing
    const moreData = Array.from({ length: 15 }, (_, i) => ({
      id: i + 1,
      name: `Item ${i + 1}`,
      value: (i + 1) * 100,
      date: new Date(`2023-01-${String(i + 1).padStart(2, '0')}`),
    }));
    
    setup({
      data: moreData,
      isPaginated: true,
      itemsPerPage: 5,
    });
    
    // Verify that the pagination controls are displayed
    const pagination = screen.getByRole('navigation', { name: /pagination/i });
    expect(pagination).toBeInTheDocument();
    
    // Verify that the correct number of rows are displayed for the first page
    let rows = screen.getAllByRole('row').slice(1); // Exclude header row
    expect(rows).toHaveLength(5);
    expect(rows[0]).toHaveTextContent('Item 1');
    expect(rows[4]).toHaveTextContent('Item 5');
    
    // Simulate clicking on the next page button
    const nextButton = screen.getByRole('button', { name: /go to next page/i });
    fireEvent.click(nextButton);
    
    // Verify that the next page of data is displayed
    await waitFor(() => {
      rows = screen.getAllByRole('row').slice(1);
      expect(rows).toHaveLength(5);
      expect(rows[0]).toHaveTextContent('Item 6');
      expect(rows[4]).toHaveTextContent('Item 10');
    });
  });

  it('uses custom cell rendering when provided', () => {
    // Create a mock render function for a column
    const renderFn = vi.fn().mockImplementation(item => (
      <span data-testid="custom-cell">{`Custom: ${item.name}`}</span>
    ));
    
    setup({
      columns: [
        { key: 'id', header: 'ID' },
        { key: 'name', header: 'Name', render: renderFn },
        { key: 'value', header: 'Value' },
        { key: 'date', header: 'Date' },
      ],
    });
    
    // Verify that the custom rendered content is displayed in the cells
    expect(renderFn).toHaveBeenCalledTimes(5);
    const customCells = screen.getAllByTestId('custom-cell');
    expect(customCells).toHaveLength(5);
    expect(customCells[0]).toHaveTextContent('Custom: Item 1');
  });

  it('applies correct size classes', () => {
    setup({ size: 'sm' });
    
    // Verify that the correct size class is applied to the table element
    const table = screen.getByRole('table');
    expect(table).toHaveClass('table--sm');
    
    // Clean up and test another size
    setup({ size: 'lg' });
    
    const largeTable = screen.getByRole('table');
    expect(largeTable).toHaveClass('table--lg');
  });

  it('handles controlled sorting correctly', () => {
    // Create a mock function for onSort
    const onSort = vi.fn();
    const { mockData, mockColumns, rerender } = setup({
      isSortable: true,
      sortColumn: 'name',
      sortDirection: 'asc',
      onSort,
    });
    
    // Verify that the initial sort is applied correctly
    const nameHeader = screen.getAllByRole('columnheader')[1];
    expect(nameHeader).toHaveAttribute('aria-sort', 'ascending');
    
    // Simulate clicking on the header to change sort
    fireEvent.click(nameHeader);
    
    // Verify that onSort was called
    expect(onSort).toHaveBeenCalledWith('name', 'desc');
    
    // Simulate parent component updating the sort props
    rerender(
      <Table
        data={mockData}
        columns={mockColumns}
        isSortable={true}
        sortColumn="name"
        sortDirection="desc"
        onSort={onSort}
      />
    );
    
    // Verify that the sort is updated correctly
    expect(nameHeader).toHaveAttribute('aria-sort', 'descending');
  });
});