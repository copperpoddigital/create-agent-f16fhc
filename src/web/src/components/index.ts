/**
 * Main barrel file that exports all component categories from the Freight Price Movement Agent web application.
 * This file serves as the central entry point for importing components throughout the application, simplifying imports and maintaining a clean project structure.
 * @file src/web/src/components/index.ts
 * @requires module:./common
 * @requires module:./layout
 * @requires module:./charts
 * @requires module:./forms
 * @requires module:./dashboard
 * @requires module:./analysis
 * @requires module:./data-sources
 * @requires module:./reports
 * @requires module:./settings
 * @exports module:./common
 * @exports module:./layout
 * @exports module:./charts
 * @exports module:./forms
 * @exports module:./dashboard
 * @exports module:./analysis
 * @exports module:./data-sources
 * @exports module:./reports
 * @exports module:./settings
 * @see Technical Specifications/7. USER INTERFACE DESIGN
 */

// Import all common UI components for re-export
import * as CommonComponents from './common';
// Import all layout components for re-export
import * as LayoutComponents from './layout';
// Import all chart components for re-export
import * as ChartComponents from './charts';
// Import all form components for re-export
import * as FormComponents from './forms';
// Import all dashboard components for re-export
import * as DashboardComponents from './dashboard';
// Import all analysis components for re-export
import * as AnalysisComponents from './analysis';
// Import all data source components for re-export
import * as DataSourceComponents from './data-sources';
// Import all report components for re-export
import * as ReportComponents from './reports';
// Import all settings components for re-export
import * as SettingsComponents from './settings';

// Re-export all common UI components
export * from './common';
// Re-export all layout components
export * from './layout';
// Re-export all chart components
export * from './charts';
// Re-export all form components
export * from './forms';
// Re-export all dashboard components
export * from './dashboard';
// Re-export all analysis components
export * from './analysis';
// Re-export all data source components
export * from './data-sources';
// Re-export all report components
export * from './reports';
// Re-export all settings components
export * from './settings';