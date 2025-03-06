import React, { useState } from 'react';
import { FormGroup, Input, Select, Button, Alert } from '../../common';
import { 
  DataSourceType, 
  DatabaseType, 
  TMSType, 
  ERPType, 
  AuthType 
} from '../../../types/data-source.types';
import { testConnection } from '../../../api/data-source-api';

interface ConnectionDetailsProps {
  sourceType: DataSourceType;
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  onBlur: (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => void;
  setFieldValue: (field: string, value: any) => void;
  isEdit?: boolean;
}

const ConnectionDetails: React.FC<ConnectionDetailsProps> = ({
  sourceType,
  values,
  errors,
  touched,
  onChange,
  onBlur,
  setFieldValue,
  isEdit = false,
}) => {
  const [isTestingConnection, setIsTestingConnection] = useState<boolean>(false);
  const [connectionTestResult, setConnectionTestResult] = useState<{ 
    success: boolean; 
    message: string 
  } | null>(null);

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
            date_format: values.date_format
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
            query: values.query
          };
          break;
        case DataSourceType.API:
          connectionParams = {
            url: values.url,
            method: values.method,
            headers: typeof values.headers === 'string' ? 
              JSON.parse(values.headers) : values.headers,
            body: values.body,
            auth_type: values.auth_type,
            auth_config: values.auth_config
          };
          break;
        case DataSourceType.TMS:
          connectionParams = {
            tms_type: values.tms_type,
            connection_url: values.connection_url,
            username: values.username,
            password: values.password,
            api_key: values.api_key,
            custom_parameters: typeof values.custom_parameters === 'string' ? 
              JSON.parse(values.custom_parameters) : values.custom_parameters
          };
          break;
        case DataSourceType.ERP:
          connectionParams = {
            erp_type: values.erp_type,
            connection_url: values.connection_url,
            username: values.username,
            password: values.password,
            api_key: values.api_key,
            custom_parameters: typeof values.custom_parameters === 'string' ? 
              JSON.parse(values.custom_parameters) : values.custom_parameters
          };
          break;
      }

      const response = await testConnection({
        source_type: sourceType,
        connection_params: connectionParams
      });

      setConnectionTestResult({
        success: response.success,
        message: response.data?.message || (response.success ? 'Connection successful!' : 'Connection failed.')
      });
    } catch (error) {
      setConnectionTestResult({
        success: false,
        message: 'An error occurred while testing the connection.'
      });
    } finally {
      setIsTestingConnection(false);
    }
  };

  const renderCSVConnectionFields = () => {
    return (
      <>
        <FormGroup
          id="file_upload"
          label="File Upload"
          required
          isValid={touched.file_path && !errors.file_path}
          isInvalid={touched.file_path && !!errors.file_path}
          validationMessage={touched.file_path ? errors.file_path : undefined}
        >
          <Input
            type="file"
            name="file_path"
            value={values.file_path || ''}
            onChange={onChange}
            onBlur={onBlur}
            disabled={isEdit}
          />
        </FormGroup>
        <FormGroup
          id="delimiter"
          label="Delimiter"
          required
          isValid={touched.delimiter && !errors.delimiter}
          isInvalid={touched.delimiter && !!errors.delimiter}
          validationMessage={touched.delimiter ? errors.delimiter : undefined}
        >
          <Input
            type="text"
            name="delimiter"
            value={values.delimiter || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., ,"
          />
        </FormGroup>
        <FormGroup
          id="has_header"
          label="Has Header Row"
        >
          <input
            type="checkbox"
            name="has_header"
            checked={values.has_header || false}
            onChange={(e) => setFieldValue('has_header', e.target.checked)}
            id="has_header"
          />
        </FormGroup>
        <FormGroup
          id="date_format"
          label="Date Format"
          required
          isValid={touched.date_format && !errors.date_format}
          isInvalid={touched.date_format && !!errors.date_format}
          validationMessage={touched.date_format ? errors.date_format : undefined}
        >
          <Input
            type="text"
            name="date_format"
            value={values.date_format || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., YYYY-MM-DD"
          />
        </FormGroup>
      </>
    );
  };

  const renderDatabaseConnectionFields = () => {
    return (
      <>
        <FormGroup
          id="database_type"
          label="Database Type"
          required
          isValid={touched.database_type && !errors.database_type}
          isInvalid={touched.database_type && !!errors.database_type}
          validationMessage={touched.database_type ? errors.database_type : undefined}
        >
          <Select
            name="database_type"
            value={values.database_type || ''}
            onChange={onChange}
            onBlur={onBlur}
            options={Object.values(DatabaseType).map(type => ({
              value: type,
              label: type === DatabaseType.POSTGRESQL ? 'PostgreSQL' :
                     type === DatabaseType.MYSQL ? 'MySQL' :
                     type === DatabaseType.SQLSERVER ? 'SQL Server' : 'Oracle'
            }))}
            placeholder="Select database type"
          />
        </FormGroup>
        <FormGroup
          id="host"
          label="Host"
          required
          isValid={touched.host && !errors.host}
          isInvalid={touched.host && !!errors.host}
          validationMessage={touched.host ? errors.host : undefined}
        >
          <Input
            type="text"
            name="host"
            value={values.host || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., localhost or db.example.com"
          />
        </FormGroup>
        <FormGroup
          id="port"
          label="Port"
          required
          isValid={touched.port && !errors.port}
          isInvalid={touched.port && !!errors.port}
          validationMessage={touched.port ? errors.port : undefined}
        >
          <Input
            type="number"
            name="port"
            value={values.port || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., 5432"
          />
        </FormGroup>
        <FormGroup
          id="database"
          label="Database Name"
          required
          isValid={touched.database && !errors.database}
          isInvalid={touched.database && !!errors.database}
          validationMessage={touched.database ? errors.database : undefined}
        >
          <Input
            type="text"
            name="database"
            value={values.database || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., my_database"
          />
        </FormGroup>
        <FormGroup
          id="username"
          label="Username"
          required
          isValid={touched.username && !errors.username}
          isInvalid={touched.username && !!errors.username}
          validationMessage={touched.username ? errors.username : undefined}
        >
          <Input
            type="text"
            name="username"
            value={values.username || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="Database username"
          />
        </FormGroup>
        <FormGroup
          id="password"
          label="Password"
          required={!isEdit}
          isValid={touched.password && !errors.password}
          isInvalid={touched.password && !!errors.password}
          validationMessage={touched.password ? errors.password : undefined}
        >
          <Input
            type="password"
            name="password"
            value={values.password || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder={isEdit ? "Leave blank to keep current password" : "Database password"}
          />
        </FormGroup>
        <FormGroup
          id="query"
          label="SQL Query"
          required
          isValid={touched.query && !errors.query}
          isInvalid={touched.query && !!errors.query}
          validationMessage={touched.query ? errors.query : undefined}
        >
          <Input
            type="text"
            name="query"
            value={values.query || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., SELECT * FROM freight_data"
          />
        </FormGroup>
      </>
    );
  };

  const renderAPIConnectionFields = () => {
    return (
      <>
        <FormGroup
          id="url"
          label="API URL"
          required
          isValid={touched.url && !errors.url}
          isInvalid={touched.url && !!errors.url}
          validationMessage={touched.url ? errors.url : undefined}
        >
          <Input
            type="text"
            name="url"
            value={values.url || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., https://api.example.com/freight"
          />
        </FormGroup>
        <FormGroup
          id="method"
          label="Method"
          required
          isValid={touched.method && !errors.method}
          isInvalid={touched.method && !!errors.method}
          validationMessage={touched.method ? errors.method : undefined}
        >
          <Select
            name="method"
            value={values.method || ''}
            onChange={onChange}
            onBlur={onBlur}
            options={[
              { value: 'GET', label: 'GET' },
              { value: 'POST', label: 'POST' },
              { value: 'PUT', label: 'PUT' },
              { value: 'PATCH', label: 'PATCH' },
              { value: 'DELETE', label: 'DELETE' }
            ]}
            placeholder="Select request method"
          />
        </FormGroup>
        <FormGroup
          id="headers"
          label="Headers"
          isValid={touched.headers && !errors.headers}
          isInvalid={touched.headers && !!errors.headers}
          validationMessage={touched.headers ? errors.headers : undefined}
        >
          <Input
            type="text"
            name="headers"
            value={values.headers || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder='e.g., {"Content-Type": "application/json"}'
          />
        </FormGroup>
        <FormGroup
          id="body"
          label="Request Body"
          isValid={touched.body && !errors.body}
          isInvalid={touched.body && !!errors.body}
          validationMessage={touched.body ? errors.body : undefined}
        >
          <Input
            type="text"
            name="body"
            value={values.body || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="Request body in JSON format"
          />
        </FormGroup>
        <FormGroup
          id="auth_type"
          label="Authentication Type"
          isValid={touched.auth_type && !errors.auth_type}
          isInvalid={touched.auth_type && !!errors.auth_type}
          validationMessage={touched.auth_type ? errors.auth_type : undefined}
        >
          <Select
            name="auth_type"
            value={values.auth_type || ''}
            onChange={onChange}
            onBlur={onBlur}
            options={Object.values(AuthType).map(type => ({
              value: type,
              label: type === AuthType.NONE ? 'None' :
                     type === AuthType.BASIC ? 'Basic Auth' :
                     type === AuthType.API_KEY ? 'API Key' : 'OAuth 2.0'
            }))}
            placeholder="Select authentication type"
          />
        </FormGroup>
        {values.auth_type === AuthType.BASIC && (
          <>
            <FormGroup
              id="auth_config_username"
              label="Username"
              required
              isValid={touched['auth_config.username'] && !errors['auth_config.username']}
              isInvalid={touched['auth_config.username'] && !!errors['auth_config.username']}
              validationMessage={touched['auth_config.username'] ? errors['auth_config.username'] : undefined}
            >
              <Input
                type="text"
                name="auth_config.username"
                value={values.auth_config?.username || ''}
                onChange={onChange}
                onBlur={onBlur}
                placeholder="API username"
              />
            </FormGroup>
            <FormGroup
              id="auth_config_password"
              label="Password"
              required
              isValid={touched['auth_config.password'] && !errors['auth_config.password']}
              isInvalid={touched['auth_config.password'] && !!errors['auth_config.password']}
              validationMessage={touched['auth_config.password'] ? errors['auth_config.password'] : undefined}
            >
              <Input
                type="password"
                name="auth_config.password"
                value={values.auth_config?.password || ''}
                onChange={onChange}
                onBlur={onBlur}
                placeholder="API password"
              />
            </FormGroup>
          </>
        )}
        {values.auth_type === AuthType.API_KEY && (
          <>
            <FormGroup
              id="auth_config_key_name"
              label="API Key Name"
              required
              isValid={touched['auth_config.key_name'] && !errors['auth_config.key_name']}
              isInvalid={touched['auth_config.key_name'] && !!errors['auth_config.key_name']}
              validationMessage={touched['auth_config.key_name'] ? errors['auth_config.key_name'] : undefined}
            >
              <Input
                type="text"
                name="auth_config.key_name"
                value={values.auth_config?.key_name || ''}
                onChange={onChange}
                onBlur={onBlur}
                placeholder="e.g., X-API-Key or api_key"
              />
            </FormGroup>
            <FormGroup
              id="auth_config_key_value"
              label="API Key Value"
              required
              isValid={touched['auth_config.key_value'] && !errors['auth_config.key_value']}
              isInvalid={touched['auth_config.key_value'] && !!errors['auth_config.key_value']}
              validationMessage={touched['auth_config.key_value'] ? errors['auth_config.key_value'] : undefined}
            >
              <Input
                type="text"
                name="auth_config.key_value"
                value={values.auth_config?.key_value || ''}
                onChange={onChange}
                onBlur={onBlur}
                placeholder="Your API key"
              />
            </FormGroup>
            <FormGroup
              id="auth_config_key_location"
              label="API Key Location"
              required
              isValid={touched['auth_config.key_location'] && !errors['auth_config.key_location']}
              isInvalid={touched['auth_config.key_location'] && !!errors['auth_config.key_location']}
              validationMessage={touched['auth_config.key_location'] ? errors['auth_config.key_location'] : undefined}
            >
              <Select
                name="auth_config.key_location"
                value={values.auth_config?.key_location || ''}
                onChange={onChange}
                onBlur={onBlur}
                options={[
                  { value: 'header', label: 'Header' },
                  { value: 'query', label: 'Query Parameter' },
                  { value: 'body', label: 'Request Body' }
                ]}
                placeholder="Select key location"
              />
            </FormGroup>
          </>
        )}
        {values.auth_type === AuthType.OAUTH2 && (
          <>
            <FormGroup
              id="auth_config_client_id"
              label="Client ID"
              required
              isValid={touched['auth_config.client_id'] && !errors['auth_config.client_id']}
              isInvalid={touched['auth_config.client_id'] && !!errors['auth_config.client_id']}
              validationMessage={touched['auth_config.client_id'] ? errors['auth_config.client_id'] : undefined}
            >
              <Input
                type="text"
                name="auth_config.client_id"
                value={values.auth_config?.client_id || ''}
                onChange={onChange}
                onBlur={onBlur}
                placeholder="OAuth client ID"
              />
            </FormGroup>
            <FormGroup
              id="auth_config_client_secret"
              label="Client Secret"
              required
              isValid={touched['auth_config.client_secret'] && !errors['auth_config.client_secret']}
              isInvalid={touched['auth_config.client_secret'] && !!errors['auth_config.client_secret']}
              validationMessage={touched['auth_config.client_secret'] ? errors['auth_config.client_secret'] : undefined}
            >
              <Input
                type="password"
                name="auth_config.client_secret"
                value={values.auth_config?.client_secret || ''}
                onChange={onChange}
                onBlur={onBlur}
                placeholder="OAuth client secret"
              />
            </FormGroup>
            <FormGroup
              id="auth_config_token_url"
              label="Token URL"
              required
              isValid={touched['auth_config.token_url'] && !errors['auth_config.token_url']}
              isInvalid={touched['auth_config.token_url'] && !!errors['auth_config.token_url']}
              validationMessage={touched['auth_config.token_url'] ? errors['auth_config.token_url'] : undefined}
            >
              <Input
                type="text"
                name="auth_config.token_url"
                value={values.auth_config?.token_url || ''}
                onChange={onChange}
                onBlur={onBlur}
                placeholder="e.g., https://api.example.com/oauth/token"
              />
            </FormGroup>
          </>
        )}
        <FormGroup
          id="response_path"
          label="Response Path"
          isValid={touched.response_path && !errors.response_path}
          isInvalid={touched.response_path && !!errors.response_path}
          validationMessage={touched.response_path ? errors.response_path : undefined}
        >
          <Input
            type="text"
            name="response_path"
            value={values.response_path || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., data.items or leave empty for root"
          />
        </FormGroup>
      </>
    );
  };

  const renderTMSConnectionFields = () => {
    return (
      <>
        <FormGroup
          id="tms_type"
          label="TMS Type"
          required
          isValid={touched.tms_type && !errors.tms_type}
          isInvalid={touched.tms_type && !!errors.tms_type}
          validationMessage={touched.tms_type ? errors.tms_type : undefined}
        >
          <Select
            name="tms_type"
            value={values.tms_type || ''}
            onChange={onChange}
            onBlur={onBlur}
            options={Object.values(TMSType).map(type => ({
              value: type,
              label: type === TMSType.SAP_TM ? 'SAP TM' :
                     type === TMSType.ORACLE_TMS ? 'Oracle TMS' :
                     type === TMSType.JDA_TMS ? 'JDA TMS' : 'Custom'
            }))}
            placeholder="Select TMS type"
          />
        </FormGroup>
        <FormGroup
          id="connection_url"
          label="Connection URL"
          required
          isValid={touched.connection_url && !errors.connection_url}
          isInvalid={touched.connection_url && !!errors.connection_url}
          validationMessage={touched.connection_url ? errors.connection_url : undefined}
        >
          <Input
            type="text"
            name="connection_url"
            value={values.connection_url || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., https://tms.example.com/api"
          />
        </FormGroup>
        <FormGroup
          id="username"
          label="Username"
          required
          isValid={touched.username && !errors.username}
          isInvalid={touched.username && !!errors.username}
          validationMessage={touched.username ? errors.username : undefined}
        >
          <Input
            type="text"
            name="username"
            value={values.username || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="TMS username"
          />
        </FormGroup>
        {!isEdit && (
          <FormGroup
            id="password"
            label="Password"
            required
            isValid={touched.password && !errors.password}
            isInvalid={touched.password && !!errors.password}
            validationMessage={touched.password ? errors.password : undefined}
          >
            <Input
              type="password"
              name="password"
              value={values.password || ''}
              onChange={onChange}
              onBlur={onBlur}
              placeholder="TMS password"
            />
          </FormGroup>
        )}
        <FormGroup
          id="api_key"
          label="API Key"
          isValid={touched.api_key && !errors.api_key}
          isInvalid={touched.api_key && !!errors.api_key}
          validationMessage={touched.api_key ? errors.api_key : undefined}
        >
          <Input
            type="text"
            name="api_key"
            value={values.api_key || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="Optional API key"
          />
        </FormGroup>
        <FormGroup
          id="custom_parameters"
          label="Custom Parameters"
          isValid={touched.custom_parameters && !errors.custom_parameters}
          isInvalid={touched.custom_parameters && !!errors.custom_parameters}
          validationMessage={touched.custom_parameters ? errors.custom_parameters : undefined}
        >
          <Input
            type="text"
            name="custom_parameters"
            value={values.custom_parameters || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder='e.g., {"param1": "value1", "param2": "value2"}'
          />
        </FormGroup>
      </>
    );
  };

  const renderERPConnectionFields = () => {
    return (
      <>
        <FormGroup
          id="erp_type"
          label="ERP Type"
          required
          isValid={touched.erp_type && !errors.erp_type}
          isInvalid={touched.erp_type && !!errors.erp_type}
          validationMessage={touched.erp_type ? errors.erp_type : undefined}
        >
          <Select
            name="erp_type"
            value={values.erp_type || ''}
            onChange={onChange}
            onBlur={onBlur}
            options={Object.values(ERPType).map(type => ({
              value: type,
              label: type === ERPType.SAP_ERP ? 'SAP ERP' :
                     type === ERPType.ORACLE_ERP ? 'Oracle ERP' :
                     type === ERPType.MICROSOFT_DYNAMICS ? 'Microsoft Dynamics' : 'Custom'
            }))}
            placeholder="Select ERP type"
          />
        </FormGroup>
        <FormGroup
          id="connection_url"
          label="Connection URL"
          required
          isValid={touched.connection_url && !errors.connection_url}
          isInvalid={touched.connection_url && !!errors.connection_url}
          validationMessage={touched.connection_url ? errors.connection_url : undefined}
        >
          <Input
            type="text"
            name="connection_url"
            value={values.connection_url || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="e.g., https://erp.example.com/api"
          />
        </FormGroup>
        <FormGroup
          id="username"
          label="Username"
          required
          isValid={touched.username && !errors.username}
          isInvalid={touched.username && !!errors.username}
          validationMessage={touched.username ? errors.username : undefined}
        >
          <Input
            type="text"
            name="username"
            value={values.username || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="ERP username"
          />
        </FormGroup>
        {!isEdit && (
          <FormGroup
            id="password"
            label="Password"
            required
            isValid={touched.password && !errors.password}
            isInvalid={touched.password && !!errors.password}
            validationMessage={touched.password ? errors.password : undefined}
          >
            <Input
              type="password"
              name="password"
              value={values.password || ''}
              onChange={onChange}
              onBlur={onBlur}
              placeholder="ERP password"
            />
          </FormGroup>
        )}
        <FormGroup
          id="api_key"
          label="API Key"
          isValid={touched.api_key && !errors.api_key}
          isInvalid={touched.api_key && !!errors.api_key}
          validationMessage={touched.api_key ? errors.api_key : undefined}
        >
          <Input
            type="text"
            name="api_key"
            value={values.api_key || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder="Optional API key"
          />
        </FormGroup>
        <FormGroup
          id="custom_parameters"
          label="Custom Parameters"
          isValid={touched.custom_parameters && !errors.custom_parameters}
          isInvalid={touched.custom_parameters && !!errors.custom_parameters}
          validationMessage={touched.custom_parameters ? errors.custom_parameters : undefined}
        >
          <Input
            type="text"
            name="custom_parameters"
            value={values.custom_parameters || ''}
            onChange={onChange}
            onBlur={onBlur}
            placeholder='e.g., {"param1": "value1", "param2": "value2"}'
          />
        </FormGroup>
      </>
    );
  };

  const renderConnectionTestResult = () => {
    if (!connectionTestResult) return null;

    return (
      <Alert
        type={connectionTestResult.success ? 'success' : 'error'}
        title={connectionTestResult.success ? 'Connection Successful' : 'Connection Failed'}
      >
        {connectionTestResult.message}
      </Alert>
    );
  };

  return (
    <div className="connection-details">
      <h3>Connection Details</h3>
      {sourceType === DataSourceType.CSV && renderCSVConnectionFields()}
      {sourceType === DataSourceType.DATABASE && renderDatabaseConnectionFields()}
      {sourceType === DataSourceType.API && renderAPIConnectionFields()}
      {sourceType === DataSourceType.TMS && renderTMSConnectionFields()}
      {sourceType === DataSourceType.ERP && renderERPConnectionFields()}
      
      <div className="connection-test">
        <Button 
          variant="secondary"
          onClick={handleTestConnection}
          isLoading={isTestingConnection}
          disabled={isTestingConnection}
        >
          Test Connection
        </Button>
      </div>
      {renderConnectionTestResult()}
    </div>
  );
};

export default ConnectionDetails;