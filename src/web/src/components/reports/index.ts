/**
 * Barrel file that exports all report-related components for easier imports throughout the application
 */

import ReportList, { ReportListProps } from './ReportList'; // Import the ReportList component for re-export
import ReportDetails, { ReportDetailsProps } from './ReportDetails'; // Import the ReportDetails component for re-export

export type { ReportListProps };
export type { ReportDetailsProps };

/**
 * Export the ReportList component for use in other parts of the application
 */
export { ReportList };

/**
 * Export the ReportDetails component for use in other parts of the application
 */
export { ReportDetails };