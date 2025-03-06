// Import the ConnectionDetails component for re-export
import ConnectionDetails, { ConnectionDetailsProps } from './ConnectionDetails';
// Import the DataSourceDetails component for re-export
import DataSourceDetails, { DataSourceDetailsProps } from './DataSourceDetails';
// Import the DataSourceList component for re-export
import DataSourceList, { DataSourceListProps } from './DataSourceList';
// Import the FieldMapping component for re-export
import FieldMapping, { FieldMappingProps } from './FieldMapping';

// Export the ConnectionDetails component for use in data source forms
export { ConnectionDetails };

// Export the DataSourceDetails component for use in data source management interfaces
export { DataSourceDetails };

// Export the DataSourceList component for use in data source listing pages
export { DataSourceList };

// Export the FieldMapping component for use in data source configuration forms
export { FieldMapping };

export type {
    ConnectionDetailsProps,
    DataSourceDetailsProps,
    DataSourceListProps,
    FieldMappingProps,
};