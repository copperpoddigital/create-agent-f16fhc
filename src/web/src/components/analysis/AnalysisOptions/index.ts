/**
 * Index file that exports the AnalysisOptions component for use throughout the application.
 * This simplifies imports by allowing other components to import from the directory
 * rather than the specific file.
 * 
 * @example
 * // Import in other files
 * import AnalysisOptions from '../../components/analysis/AnalysisOptions';
 */

// Re-export the AnalysisOptions component as the default export
export { default } from './AnalysisOptions';

// Note: AnalysisOptionsProps interface is not exported from this module
// as it's only used internally within the component