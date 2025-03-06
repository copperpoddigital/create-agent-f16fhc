import React from 'react';
import classNames from 'classnames'; // v2.3.2
import Table, { TableColumn } from '../../common/Table';
import TrendIndicator from '../../charts/TrendIndicator';
import { formatCurrency, formatAbsoluteChange } from '../../../utils/currency-utils';
import { AnalysisResult, DetailedResult } from '../../../types';

/**
 * Props interface for the AnalysisResultsTable component
 */
interface AnalysisResultsTableProps {
  /** The analysis result containing detailed period-by-period data */
  result: AnalysisResult;
  /** Whether the table is in a loading state */
  isLoading?: boolean;
  /** Additional CSS class names to apply to the component */
  className?: string;
  /** Whether the table columns are sortable */
  isSortable?: boolean;
  /** Whether the table should include pagination */
  isPaginated?: boolean;
  /** Number of items to display per page when pagination is enabled */
  itemsPerPage?: number;
}

/**
 * A component that displays detailed freight price movement analysis results in a tabular format
 */
const AnalysisResultsTable: React.FC<AnalysisResultsTableProps> = ({
  result,
  isLoading = false,
  className,
  isSortable = true,
  isPaginated = true,
  itemsPerPage = 10
}) => {
  // Extract detailed results and currency from the result object with fallbacks
  const detailed_results = result?.detailed_results || [];
  const currency = result?.currency || 'USD';

  // Define the table columns
  const columns: TableColumn<DetailedResult>[] = [
    {
      key: 'period',
      header: 'Period',
      sortable: true,
      render: (item: DetailedResult) => item.period
    },
    {
      key: 'price',
      header: `Price (${currency})`,
      sortable: true,
      align: 'right',
      className: 'price-column',
      render: (item: DetailedResult) => formatCurrency(item.price, currency)
    },
    {
      key: 'absolute_change',
      header: 'Absolute Change',
      sortable: true,
      align: 'right',
      className: 'change-column',
      render: (item: DetailedResult, index: number) => {
        // For the first row or if the value is null, display a dash
        if (index === 0 || item.absolute_change === null) {
          return '-';
        }
        return formatAbsoluteChange(item.absolute_change, currency);
      }
    },
    {
      key: 'percentage_change',
      header: 'Percentage Change',
      sortable: true,
      align: 'right',
      className: 'change-column',
      render: (item: DetailedResult, index: number) => {
        // For the first row or if the value is null, display a dash
        if (index === 0 || item.percentage_change === null || item.trend_direction === null) {
          return '-';
        }
        return (
          <TrendIndicator 
            direction={item.trend_direction} 
            value={item.percentage_change}
            size="small"
          />
        );
      }
    }
  ];

  // Construct CSS class names
  const tableClassName = classNames('analysis-results-table', className);

  return (
    <Table
      data={detailed_results}
      columns={columns}
      className={tableClassName}
      isLoading={isLoading}
      isStriped={true}
      isBordered={true}
      isHoverable={true}
      isSortable={isSortable}
      isPaginated={isPaginated}
      itemsPerPage={itemsPerPage}
      emptyMessage="No detailed results available."
    />
  );
};

export default AnalysisResultsTable;