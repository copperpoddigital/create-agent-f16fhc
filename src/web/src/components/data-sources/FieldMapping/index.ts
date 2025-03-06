/**
 * Barrel file for FieldMapping component
 * 
 * This file exports the FieldMapping component to provide a cleaner 
 * import path for consumers of this component. Instead of importing 
 * directly from the component file, consumers can import from the 
 * directory, simplifying imports throughout the application.
 * 
 * The FieldMapping component allows users to map source data fields to
 * standardized freight data fields, supporting the data normalization 
 * requirements of the Data Collection & Ingestion feature.
 */

import FieldMapping from './FieldMapping';

export default FieldMapping;