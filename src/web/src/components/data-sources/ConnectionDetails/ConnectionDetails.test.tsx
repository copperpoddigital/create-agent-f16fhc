# src/web/src/components/data-sources/ConnectionDetails/ConnectionDetails.test.tsx
```typescript
import React from 'react'; // ^18.2.0
import { customRender, screen, waitFor, fireEvent } from '../../../utils/test-utils'; // Import testing utilities for rendering and interacting with the component
import ConnectionDetails from './ConnectionDetails'; // Import the component being tested
import { DataSourceType, DatabaseType, TMSType, ERPType, AuthType } from '../../../types/data-source.types'; // Import type definitions for data sources
import { testConnection } from '../../../api/data-source-api'; // Import API function to be mocked for testing connection functionality
import { jest } from '@jest/globals'; // Testing framework for mocking functions

// Setup function to create common props for testing the ConnectionDetails component
const setup = (overrides: any = {}) => {
  // Create default props with empty values and no-op functions
  const defaultProps = {
    sourceType: DataSourceType.CSV,
    values: {},
    errors: {},
    touched: {},
    onChange: jest.fn(),
    onBlur: jest.fn(),
    setFieldValue: jest.fn(),
  };

  // Merge the provided overrides with the default props
  const props = { ...defaultProps, ...overrides };

  // Return the complete props object
  return props;
};

// Helper function to render the ConnectionDetails component with given props
const renderComponent = (props: any) => {
  // Call customRender with ConnectionDetails component and provided props
  const renderResult = customRender(<ConnectionDetails {...props} />);

  // Return the render result
  return renderResult;
};

describe('ConnectionDetails', () => {
  // Test suite for the ConnectionDetails component
  it('renders CSV connection fields when sourceType is CSV', () => {
    // Verifies that the correct form fields are rendered for CSV data sources
    // Render ConnectionDetails with sourceType set to DataSourceType.CSV
    renderComponent(setup({ sourceType: DataSourceType.CSV }));

    // Check that file upload input is present
    expect(screen.getByLabelText('File Upload')).toBeInTheDocument();

    // Check that delimiter input is present
    expect(screen.getByLabelText('Delimiter')).toBeInTheDocument();

    // Check that has_header checkbox is present
    expect(screen.getByLabelText('Has Header Row')).toBeInTheDocument();

    // Check that date_format input is present
    expect(screen.getByLabelText('Date Format')).toBeInTheDocument();
  });

  it('renders Database connection fields when sourceType is DATABASE', () => {
    // Verifies that the correct form fields are rendered for Database data sources
    // Render ConnectionDetails with sourceType set to DataSourceType.DATABASE
    renderComponent(setup({ sourceType: DataSourceType.DATABASE }));

    // Check that database_type select is present with options from DatabaseType enum
    expect(screen.getByLabelText('Database Type')).toBeInTheDocument();

    // Check that host input is present
    expect(screen.getByLabelText('Host')).toBeInTheDocument();

    // Check that port input is present
    expect(screen.getByLabelText('Port')).toBeInTheDocument();

    // Check that database name input is present
    expect(screen.getByLabelText('Database Name')).toBeInTheDocument();

    // Check that username input is present
    expect(screen.getByLabelText('Username')).toBeInTheDocument();

    // Check that password input is present
    expect(screen.getByLabelText('Password')).toBeInTheDocument();

    // Check that query input is present
    expect(screen.getByLabelText('SQL Query')).toBeInTheDocument();
  });

  it('renders API connection fields when sourceType is API', () => {
    // Verifies that the correct form fields are rendered for API data sources
    // Render ConnectionDetails with sourceType set to DataSourceType.API
    renderComponent(setup({ sourceType: DataSourceType.API }));

    // Check that url input is present
    expect(screen.getByLabelText('API URL')).toBeInTheDocument();

    // Check that method select is present
    expect(screen.getByLabelText('Method')).toBeInTheDocument();

    // Check that headers input is present
    expect(screen.getByLabelText('Headers')).toBeInTheDocument();

    // Check that body input is present
    expect(screen.getByLabelText('Request Body')).toBeInTheDocument();

    // Check that auth_type select is present with options from AuthType enum
    expect(screen.getByLabelText('Authentication Type')).toBeInTheDocument();

    // Check that response_path input is present
    expect(screen.getByLabelText('Response Path')).toBeInTheDocument();
  });

  it('renders TMS connection fields when sourceType is TMS', () => {
    // Verifies that the correct form fields are rendered for TMS data sources
    // Render ConnectionDetails with sourceType set to DataSourceType.TMS
    renderComponent(setup({ sourceType: DataSourceType.TMS }));

    // Check that tms_type select is present with options from TMSType enum
    expect(screen.getByLabelText('TMS Type')).toBeInTheDocument();

    // Check that connection_url input is present
    expect(screen.getByLabelText('Connection URL')).toBeInTheDocument();

    // Check that username input is present
    expect(screen.getByLabelText('Username')).toBeInTheDocument();

    // Check that password input is present (not shown in edit mode)
    expect(screen.getByLabelText('Password')).toBeInTheDocument();

    // Check that api_key input is present
    expect(screen.getByLabelText('API Key')).toBeInTheDocument();

    // Check that custom_parameters inputs are present
    expect(screen.getByLabelText('Custom Parameters')).toBeInTheDocument();
  });

  it('renders ERP connection fields when sourceType is ERP', () => {
    // Verifies that the correct form fields are rendered for ERP data sources
    // Render ConnectionDetails with sourceType set to DataSourceType.ERP
    renderComponent(setup({ sourceType: DataSourceType.ERP }));

    // Check that erp_type select is present with options from ERPType enum
    expect(screen.getByLabelText('ERP Type')).toBeInTheDocument();

    // Check that connection_url input is present
    expect(screen.getByLabelText('Connection URL')).toBeInTheDocument();

    // Check that username input is present
    expect(screen.getByLabelText('Username')).toBeInTheDocument();

    // Check that password input is present (not shown in edit mode)
    expect(screen.getByLabelText('Password')).toBeInTheDocument();

    // Check that api_key input is present
    expect(screen.getByLabelText('API Key')).toBeInTheDocument();

    // Check that custom_parameters inputs are present
    expect(screen.getByLabelText('Custom Parameters')).toBeInTheDocument();
  });

  it('handles test connection for CSV data source', async () => {
    // Tests the connection testing functionality for CSV data sources
    // Mock testConnection API function to return success
    const mockTestConnection = jest.mocked(testConnection).mockResolvedValue({
      success: true,
      data: { message: 'Connection successful!' },
      error: null,
      meta: null,
    });

    // Render ConnectionDetails with sourceType set to DataSourceType.CSV and appropriate values
    renderComponent(
      setup({
        sourceType: DataSourceType.CSV,
        values: { file_path: 'test.csv', delimiter: ',', has_header: true, date_format: 'YYYY-MM-DD' },
      })
    );

    // Click the Test Connection button
    fireEvent.click(screen.getByText('Test Connection'));

    // Verify that testConnection was called with correct parameters
    await waitFor(() => {
      expect(mockTestConnection).toHaveBeenCalledWith({
        source_type: DataSourceType.CSV,
        connection_params: {
          file_path: 'test.csv',
          delimiter: ',',
          has_header: true,
          date_format: 'YYYY-MM-DD',
        },
      });
    });

    // Wait for success message to be displayed
    await waitFor(() => {
      expect(screen.getByText('Connection successful!')).toBeInTheDocument();
    });
  });

  it('handles test connection for Database data source', async () => {
    // Tests the connection testing functionality for Database data sources
    // Mock testConnection API function to return success
    const mockTestConnection = jest.mocked(testConnection).mockResolvedValue({
      success: true,
      data: { message: 'Connection successful!' },
      error: null,
      meta: null,
    });

    // Render ConnectionDetails with sourceType set to DataSourceType.DATABASE and appropriate values
    renderComponent(
      setup({
        sourceType: DataSourceType.DATABASE,
        values: {
          database_type: DatabaseType.POSTGRESQL,
          host: 'localhost',
          port: 5432,
          database: 'testdb',
          username: 'testuser',
          password: 'testpassword',
          query: 'SELECT * FROM freight_data',
        },
      })
    );

    // Click the Test Connection button
    fireEvent.click(screen.getByText('Test Connection'));

    // Verify that testConnection was called with correct parameters
    await waitFor(() => {
      expect(mockTestConnection).toHaveBeenCalledWith({
        source_type: DataSourceType.DATABASE,
        connection_params: {
          database_type: DatabaseType.POSTGRESQL,
          host: 'localhost',
          port: 5432,
          database: 'testdb',
          username: 'testuser',
          password: 'testpassword',
          query: 'SELECT * FROM freight_data',
        },
      });
    });

    // Wait for success message to be displayed
    await waitFor(() => {
      expect(screen.getByText('Connection successful!')).toBeInTheDocument();
    });
  });

  it('handles test connection for API data source', async () => {
    // Tests the connection testing functionality for API data sources
    // Mock testConnection API function to return success
    const mockTestConnection = jest.mocked(testConnection).mockResolvedValue({
      success: true,
      data: { message: 'Connection successful!' },
      error: null,
      meta: null,
    });

    // Render ConnectionDetails with sourceType set to DataSourceType.API and appropriate values
    renderComponent(
      setup({
        sourceType: DataSourceType.API,
        values: {
          url: 'https://api.example.com/freight',
          method: 'GET',
          headers: '{"Content-Type": "application/json"}',
          body: null,
          auth_type: AuthType.NONE,
          response_path: 'data.items',
        },
      })
    );

    // Click the Test Connection button
    fireEvent.click(screen.getByText('Test Connection'));

    // Verify that testConnection was called with correct parameters
    await waitFor(() => {
      expect(mockTestConnection).toHaveBeenCalledWith({
        source_type: DataSourceType.API,
        connection_params: {
          url: 'https://api.example.com/freight',
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          body: null,
          auth_type: AuthType.NONE,
          auth_config: undefined
        },
      });
    });

    // Wait for success message to be displayed
    await waitFor(() => {
      expect(screen.getByText('Connection successful!')).toBeInTheDocument();
    });
  });

  it('handles test connection for TMS data source', async () => {
    // Tests the connection testing functionality for TMS data sources
    // Mock testConnection API function to return success
    const mockTestConnection = jest.mocked(testConnection).mockResolvedValue({
      success: true,
      data: { message: 'Connection successful!' },
      error: null,
      meta: null,
    });

    // Render ConnectionDetails with sourceType set to DataSourceType.TMS and appropriate values
    renderComponent(
      setup({
        sourceType: DataSourceType.TMS,
        values: {
          tms_type: TMSType.SAP_TM,
          connection_url: 'https://tms.example.com/api',
          username: 'tmsuser',
          password: 'tmspassword',
          api_key: 'tmsapikey',
          custom_parameters: '{"param1": "value1"}',
        },
      })
    );

    // Click the Test Connection button
    fireEvent.click(screen.getByText('Test Connection'));

    // Verify that testConnection was called with correct parameters
    await waitFor(() => {
      expect(mockTestConnection).toHaveBeenCalledWith({
        source_type: DataSourceType.TMS,
        connection_params: {
          tms_type: TMSType.SAP_TM,
          connection_url: 'https://tms.example.com/api',
          username: 'tmsuser',
          password: 'tmspassword',
          api_key: 'tmsapikey',
          custom_parameters: { param1: 'value1' },
        },
      });
    });

    // Wait for success message to be displayed
    await waitFor(() => {
      expect(screen.getByText('Connection successful!')).toBeInTheDocument();
    });
  });

  it('handles test connection for ERP data source', async () => {
    // Tests the connection testing functionality for ERP data sources
    // Mock testConnection API function to return success
    const mockTestConnection = jest.mocked(testConnection).mockResolvedValue({
      success: true,
      data: { message: 'Connection successful!' },
      error: null,
      meta: null,
    });

    // Render ConnectionDetails with sourceType set to DataSourceType.ERP and appropriate values
    renderComponent(
      setup({
        sourceType: DataSourceType.ERP,
        values: {
          erp_type: ERPType.SAP_ERP,
          connection_url: 'https://erp.example.com/api',
          username: 'erpuser',
          password: 'erppassword',
          api_key: 'erpapikey',
          custom_parameters: '{"param1": "value1"}',
        },
      })
    );

    // Click the Test Connection button
    fireEvent.click(screen.getByText('Test Connection'));

    // Verify that testConnection was called with correct parameters
    await waitFor(() => {
      expect(mockTestConnection).toHaveBeenCalledWith({
        source_type: DataSourceType.ERP,
        connection_params: {
          erp_type: ERPType.SAP_ERP,
          connection_url: 'https://erp.example.com/api',
          username: 'erpuser',
          password: 'erppassword',
          api_key: 'erpapikey',
          custom_parameters: { param1: 'value1' },
        },
      });
    });

    // Wait for success message to be displayed
    await waitFor(() => {
      expect(screen.getByText('Connection successful!')).toBeInTheDocument();
    });
  });

  it('displays error message when test connection fails', async () => {
    // Verifies that error messages are displayed when connection testing fails
    // Mock testConnection API function to return an error
    const mockTestConnection = jest.mocked(testConnection).mockResolvedValue({
      success: false,
      data: null,
      error: { code: 'CONNECTION_ERROR', message: 'Failed to connect', details: null, path: null },
      meta: null,
    });

    // Render ConnectionDetails with appropriate values
    renderComponent(setup({ sourceType: DataSourceType.CSV, values: { file_path: 'test.csv', delimiter: ',', has_header: true, date_format: 'YYYY-MM-DD' } }));

    // Click the Test Connection button
    fireEvent.click(screen.getByText('Test Connection'));

    // Wait for error message to be displayed
    await waitFor(() => {
      expect(screen.getByText('Failed to connect')).toBeInTheDocument();
    });
  });

  it('does not show password field in edit mode', () => {
    // Verifies that password fields are not shown when in edit mode
    // Render ConnectionDetails with isEdit set to true
    renderComponent(setup({ sourceType: DataSourceType.DATABASE, isEdit: true }));

    // Verify that password fields are not present in the rendered component
    expect(screen.queryByLabelText('Password')).not.toBeInTheDocument();
  });

  it('calls onChange when input values change', () => {
    // Verifies that the onChange handler is called when input values change
    // Create a mock onChange function
    const onChange = jest.fn();

    // Render ConnectionDetails with the mock onChange function
    renderComponent(setup({ sourceType: DataSourceType.CSV, onChange }));

    // Change the value of an input field
    fireEvent.change(screen.getByLabelText('Delimiter'), { target: { value: ';' } });

    // Verify that onChange was called with the correct event
    expect(onChange).toHaveBeenCalled();
  });

  it('calls onBlur when input loses focus', () => {
    // Verifies that the onBlur handler is called when input loses focus
    // Create a mock onBlur function
    const onBlur = jest.fn();

    // Render ConnectionDetails with the mock onBlur function
    renderComponent(setup({ sourceType: DataSourceType.CSV, onBlur }));

    // Trigger blur event on an input field
    fireEvent.blur(screen.getByLabelText('Delimiter'));

    // Verify that onBlur was called with the correct event
    expect(onBlur).toHaveBeenCalled();
  });
});