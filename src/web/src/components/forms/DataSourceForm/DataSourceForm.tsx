import React, { useState, useEffect } from 'react'; // ^18.2.0
import FormGroup from '../../common/FormGroup';
import Input from '../../common/Input';
import Select from '../../common/Select';
import Button from '../../common/Button';
import FieldMapping from '../../data-sources/FieldMapping';
import ConnectionDetails from '../../data-sources/ConnectionDetails';
import useForm from '../../../hooks/useForm';
import useAlert from '../../../hooks/useAlert';
import {
  DataSourceType,
  DatabaseType,
  TMSType,
  ERPType,
  AuthType,
  FieldMapping as FieldMappingType,
  DataSource,
} from '../../../types/data-source.types';
import {
  testConnection,
  createCSVDataSource,
  createDatabaseDataSource,
  createAPIDataSource,
  createTMSDataSource,
  createERPDataSource,
  updateDataSource,
} from '../../../api/data-source-api';

/**
 * Interface defining the props for the DataSourceForm component
 */
interface DataSourceFormProps {
  /** Initial values for the form fields */
  initialValues?: Partial<DataSource>;
  /** Whether the form is in edit mode */
  isEdit?: boolean;
  /** Callback function called when the form is submitted */
  onSubmit: (dataSource: any) => void;
  /** Callback function called when the form is cancelled */
  onCancel: () => void;
}

/**
 * A form component for creating and editing data sources
 */
const DataSourceForm: React.FC<DataSourceFormProps> = ({
  initialValues = {},
  isEdit = false,
  onSubmit,
  onCancel,
}) => {
  // Initialize alert hook for displaying messages
  const { showError, showSuccess } = useAlert();

  // Define default field mapping values
  const defaultFieldMapping: FieldMappingType = {
    freight_charge: '',
    currency: '',
    origin: '',
    destination: '',
    date_time: '',
    carrier: null,
    mode: null,
    service_level: null,
  };

  // Initialize form state using the useForm hook
  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    setFieldValue,
    handleSubmit,
  } = useForm({
    initialValues: {
      name: '',
      description: '',
      source_type: DataSourceType.CSV,
      file_path: '',
      delimiter: ',',
      has_header: true,
      date_format: 'YYYY-MM-DD',
      database_type: DatabaseType.POSTGRESQL,
      host: '',
      port: 5432,
      database: '',
      username: '',
      password: '',
      query: '',
      url: '',
      method: 'GET',
      headers: '',
      body: '',
      auth_type: AuthType.NONE,
      auth_config: {
        username: '',
        password: '',
        key_name: '',
        key_value: '',
        key_location: 'header',
        client_id: '',
        client_secret: '',
        token_url: '',
      },
      response_path: '',
      tms_type: TMSType.SAP_TM,
      connection_url: '',
      api_key: '',
      custom_parameters: '',
      field_mapping: defaultFieldMapping,
      ...initialValues, // Override with initial values if provided
    },
    onSubmit: handleSubmitForm,
    validate: validateForm,
  });

  // Initialize component state
  const [sourceType, setSourceType] = useState<DataSourceType>(
    (initialValues?.source_type as DataSourceType) || DataSourceType.CSV
  );
  const [isTestingConnection, setIsTestingConnection] = useState<boolean>(false);
  const [connectionTestResult, setConnectionTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  const [fieldMappingValues, setFieldMappingValues] = useState<FieldMappingType>(
    initialValues?.field_mapping || defaultFieldMapping
  );

  // Update form values when initialValues prop changes (for edit mode)
  useEffect(() => {
    if (initialValues) {
      Object.keys(initialValues).forEach(key => {
        setFieldValue(key, initialValues[key]);
      });
      if (initialValues.source_type) {
        setSourceType(initialValues.source_type);
      }
    }
  }, [initialValues, setFieldValue]);

  // Update form values when sourceType changes
  useEffect(() => {
    setFieldValue('source_type', sourceType);
  }, [sourceType, setFieldValue]);

  /**
   * Handles changes to the data source type
   * @param event React.ChangeEvent<HTMLSelectElement>
   */
  const handleSourceTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newSourceType = event.target.value as DataSourceType;
    setSourceType(newSourceType);
    setConnectionTestResult(null);

    // Reset form values based on the new source type
    setFieldValue('file_path', '');
    setFieldValue('delimiter', ',');
    setFieldValue('has_header', true);
    setFieldValue('date_format', 'YYYY-MM-DD');
    setFieldValue('database_type', DatabaseType.POSTGRESQL);
    setFieldValue('host', '');
    setFieldValue('port', 5432);
    setFieldValue('database', '');
    setFieldValue('username', '');
    setFieldValue('password', '');
    setFieldValue('query', '');
    setFieldValue('url', '');
    setFieldValue('method', 'GET');
    setFieldValue('headers', '');
    setFieldValue('body', '');
    setFieldValue('auth_type', AuthType.NONE);
    setFieldValue('auth_config', {
      username: '',
      password: '',
      key_name: '',
      key_value: '',
      key_location: 'header',
      client_id: '',
      client_secret: '',
      token_url: '',
    });
    setFieldValue('response_path', '');
    setFieldValue('tms_type', TMSType.SAP_TM);
    setFieldValue('connection_url', '');
    setFieldValue('api_key', '');
    setFieldValue('custom_parameters', '');
  };

  /**
   * Tests the connection to the data source
   */
  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    setConnectionTestResult(null);

    try {
      let connectionParams: Record<string, any> = {};

      // Prepare connection parameters based on the source type
      switch (sourceType) {
        case DataSourceType.CSV:
          connectionParams = {
            file_path: values.file_path,
            delimiter: values.delimiter,
            has_header: values.has_header,
            date_format: values.date_format,
          };
          break;
        case DataSourceType.DATABASE:
          connectionParams = {
            database_type: values.database_type,
            host: values.host,
            port: values.port,
            database: values.database,
            username: values.username,
            password: values.password,
            query: values.query,
          };
          break;
        case DataSourceType.API:
          connectionParams = {
            url: values.url,
            method: values.method,
            headers: typeof values.headers === 'string' ? JSON.parse(values.headers) : values.headers,
            body: values.body,
            auth_type: values.auth_type,
            auth_config: values.auth_config,
          };
          break;
        case DataSourceType.TMS:
          connectionParams = {
            tms_type: values.tms_type,
            connection_url: values.connection_url,
            username: values.username,
            password: values.password,
            api_key: values.api_key,
            custom_parameters: typeof values.custom_parameters === 'string' ? JSON.parse(values.custom_parameters) : values.custom_parameters,
          };
          break;
        case DataSourceType.ERP:
          connectionParams = {
            erp_type: values.erp_type,
            connection_url: values.connection_url,
            username: values.username,
            password: values.password,
            api_key: values.api_key,
            custom_parameters: typeof values.custom_parameters === 'string' ? JSON.parse(values.custom_parameters) : values.custom_parameters,
          };
          break;
      }

      const response = await testConnection({
        source_type: sourceType,
        connection_params: connectionParams,
      });

      setConnectionTestResult({
        success: response.success,
        message: response.data?.message || (response.success ? 'Connection successful!' : 'Connection failed.'),
      });
      if (response.success) {
        showSuccess(response.data?.message || 'Connection successful!');
      } else {
        showError(response.data?.message || 'Connection failed!');
      }
    } catch (error: any) {
      setConnectionTestResult({
        success: false,
        message: 'An error occurred while testing the connection.',
      });
      showError('An error occurred while testing the connection.');
    } finally {
      setIsTestingConnection(false);
    }
  };

  /**
   * Handles changes to the field mapping
   * @param mapping FieldMapping
   */
  const handleFieldMappingChange = (mapping: FieldMappingType) => {
    setFieldMappingValues(mapping);
    setFieldValue('field_mapping', mapping);
  };

  /**
   * Handles form submission
   * @param values any
   */
  const handleSubmitForm = async (values: any) => {
    try {
      let result;
      if (isEdit) {
        // Call updateDataSource API function
        result = await updateDataSource(initialValues?.id || '', values);
      } else {
        // Call appropriate create API function based on source type
        switch (sourceType) {
          case DataSourceType.CSV:
            result = await createCSVDataSource(values);
            break;
          case DataSourceType.DATABASE:
            result = await createDatabaseDataSource(values);
            break;
          case DataSourceType.API:
            result = await createAPIDataSource(values);
            break;
          case DataSourceType.TMS:
            result = await createTMSDataSource(values);
            break;
          case DataSourceType.ERP:
            result = await createERPDataSource(values);
            break;
          default:
            throw new Error('Invalid data source type');
        }
      }

      // Call onSubmit prop with the result
      if (result?.success) {
        onSubmit(result.data);
        showSuccess(`Data source ${isEdit ? 'updated' : 'created'} successfully!`);
      } else {
        showError(result?.error?.message || 'Failed to create data source.');
      }
    } catch (error: any) {
      console.error('Failed to create data source', error);
      showError(error?.message || 'Failed to create data source.');
    }
  };

  /**
   * Validates the form data
   * @param values any
   * @returns Record<string, string>
   */
  const validateForm = (values: any): Record<string, string> => {
    const errors: Record<string, string> = {};

    if (!values.name) {
      errors.name = 'Name is required';
    }

    return errors;
  };

  /**
   * Renders the source type selection section
   * @returns JSX.Element
   */
  const renderSourceTypeSection = (): JSX.Element => {
    return (
      <FormGroup id="source_type" label="Source Type" required>
        <Select
          name="source_type"
          value={sourceType}
          onChange={handleSourceTypeChange}
          onBlur={handleBlur}
          options={[
            { value: DataSourceType.CSV, label: 'CSV File' },
            { value: DataSourceType.DATABASE, label: 'Database' },
            { value: DataSourceType.API, label: 'API' },
            { value: DataSourceType.TMS, label: 'TMS' },
            { value: DataSourceType.ERP, label: 'ERP' },
          ]}
          placeholder="Select source type"
        />
      </FormGroup>
    );
  };

  /**
   * Renders the source details section
   * @returns JSX.Element
   */
  const renderSourceDetailsSection = (): JSX.Element => {
    return (
      <>
        <FormGroup
          id="name"
          label="Name"
          required
          isValid={touched.name && !errors.name}
          isInvalid={touched.name && !!errors.name}
          validationMessage={touched.name ? errors.name : undefined}
        >
          <Input
            type="text"
            name="name"
            value={values.name || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Data Source Name"
          />
        </FormGroup>
        <FormGroup id="description" label="Description">
          <Input
            type="text"
            name="description"
            value={values.description || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Data Source Description"
          />
        </FormGroup>
      </>
    );
  };

  /**
   * Renders the connection details section based on source type
   * @returns JSX.Element
   */
  const renderConnectionDetailsSection = (): JSX.Element => {
    return (
      <ConnectionDetails
        sourceType={sourceType}
        values={values}
        errors={errors}
        touched={touched}
        onChange={handleChange}
        onBlur={handleBlur}
        setFieldValue={setFieldValue}
        isEdit={isEdit}
      />
    );
  };

  /**
   * Renders the field mapping section
   * @returns JSX.Element
   */
  const renderFieldMappingSection = (): JSX.Element => {
    return (
      <FieldMapping
        value={fieldMappingValues}
        sourceFields={[]} // TODO: Populate with actual source fields
        onChange={handleFieldMappingChange}
        isValid={true}
        isInvalid={false}
        validationMessage={undefined}
      />
    );
  };

  /**
   * Renders the form action buttons
   * @returns JSX.Element
   */
  const renderFormActions = (): JSX.Element => {
    return (
      <>
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={isSubmitting}>
          Save Source
        </Button>
      </>
    );
  };

  return (
    <form onSubmit={handleSubmit}>
      {renderSourceTypeSection()}
      {renderSourceDetailsSection()}
      {renderConnectionDetailsSection()}
      {renderFieldMappingSection()}
      {renderFormActions()}
    </form>
  );
};

export default DataSourceForm;