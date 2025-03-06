/**
 * Barrel file that exports all analysis-related components from a single entry point,
 * simplifying imports throughout the application. This includes components for time period
 * selection, data filtering, analysis options configuration, and results visualization.
 */

// Import TimePeriodSelector component
import TimePeriodSelector, { TimePeriodSelectorProps } from './TimePeriodSelector'; // Import the TimePeriodSelector component for time period configuration
// Import DataFilterSelector component
import DataFilterSelector, { DataFilterSelectorProps } from './DataFilterSelector'; // Import the DataFilterSelector component for data filtering options
// Import AnalysisOptions component
import AnalysisOptions, { AnalysisOptionsProps } from './AnalysisOptions'; // Import the AnalysisOptions component for analysis configuration options
// Import AnalysisResultsChart component
import AnalysisResultsChart, { AnalysisResultsChartProps } from './AnalysisResultsChart'; // Import the AnalysisResultsChart component for visualizing analysis results
// Import AnalysisResultsSummary component
import AnalysisResultsSummary, { AnalysisResultsSummaryProps } from './AnalysisResultsSummary'; // Import the AnalysisResultsSummary component for displaying analysis summary
// Import AnalysisResultsTable component
import AnalysisResultsTable, { AnalysisResultsTableProps } from './AnalysisResultsTable'; // Import the AnalysisResultsTable component for displaying detailed analysis results

// Export TimePeriodSelector component
export { TimePeriodSelector }; // Export the TimePeriodSelector component for time period configuration
export type { TimePeriodSelectorProps };
// Export DataFilterSelector component
export { DataFilterSelector }; // Export the DataFilterSelector component for data filtering options
export type { DataFilterSelectorProps };
// Export AnalysisOptions component
export { AnalysisOptions }; // Export the AnalysisOptions component for analysis configuration options
export type { AnalysisOptionsProps };
// Export AnalysisResultsChart component
export { AnalysisResultsChart }; // Export the AnalysisResultsChart component for visualizing analysis results
export type { AnalysisResultsChartProps };
// Export AnalysisResultsSummary component
export { AnalysisResultsSummary }; // Export the AnalysisResultsSummary component for displaying analysis summary
export type { AnalysisResultsSummaryProps };
// Export AnalysisResultsTable component
export { AnalysisResultsTable }; // Export the AnalysisResultsTable component for displaying detailed analysis results
export type { AnalysisResultsTableProps };