import React from 'react'; // ^18.2.0
import { render, screen, fireEvent, waitFor } from '@testing-library/react'; // ^13.4.0
import userEvent from '@testing-library/user-event'; // ^14.4.3
import { vi } from 'vitest'; // ^0.29.2
import DataSourceForm from './DataSourceForm';
import { DataSourceType } from '../../../types/data-source.types';
import { testConnection } from '../../../api/data-source-api';

// Mock the testConnection API function
vi.mock('../../../api/data-source-api', () => ({
  testConnection: vi.fn(),
}));

// Helper function to render the DataSourceForm component with default props
const setup = (props = {}) => {
  const user = userEvent.setup();
  const renderResult = render(<DataSourceForm onSubmit={() => {}} onCancel={() => {}} {...props} />);
  return { renderResult, user };
};

describe('DataSourceForm', () => {
  it('renders the form with default values', () => {
    const { renderResult } = setup();
    expect(screen.getByLabelText('Source Type')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Data Source Name')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Data Source Description')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Save Source')).toBeInTheDocument();
  });

  it('changes source type correctly', async () => {
    const { user } = setup();
    const sourceTypeSelect = screen.getByLabelText('Source Type');
    await user.selectOptions(sourceTypeSelect, DataSourceType.DATABASE);
    expect(screen.getByLabelText('Database Type')).toBeInTheDocument();

    await user.selectOptions(sourceTypeSelect, DataSourceType.API);
    expect(screen.getByLabelText('API URL')).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    const { user } = setup();
    const saveButton = screen.getByText('Save Source');
    await user.click(saveButton);
    expect(screen.getByText('Name is required')).toBeInTheDocument();
  });

  it('handles form submission correctly', async () => {
    const { user } = setup({ onSubmit: vi.fn() });
    const nameInput = screen.getByPlaceholderText('Data Source Name');
    const saveButton = screen.getByText('Save Source');

    await user.type(nameInput, 'Test Data Source');
    await user.click(saveButton);

    expect(setup({ onSubmit: vi.fn() }).onSubmit).toHaveBeenCalled();
  });

  it('handles connection testing correctly', async () => {
    const mockTestConnection = vi.mocked(testConnection);
    mockTestConnection.mockResolvedValue({ success: true, data: { message: 'Connection successful!' } } as any);

    const { user } = setup();
    const sourceTypeSelect = screen.getByLabelText('Source Type');
    await user.selectOptions(sourceTypeSelect, DataSourceType.CSV);

    const testConnectionButton = screen.getByText('Test Connection');
    await user.click(testConnectionButton);

    expect(mockTestConnection).toHaveBeenCalled();
    await waitFor(() => expect(screen.getByText('Connection successful!')).toBeInTheDocument());
  });

  it('loads initial values correctly in edit mode', () => {
    const initialValues = {
      name: 'Initial Name',
      description: 'Initial Description',
      source_type: DataSourceType.DATABASE,
    };
    setup({ initialValues, isEdit: true });
    expect(screen.getByDisplayValue('Initial Name')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Initial Description')).toBeInTheDocument();
  });

  it('handles field mapping correctly', async () => {
    const { user } = setup();
    const nameInput = screen.getByPlaceholderText('Data Source Name');
    const saveButton = screen.getByText('Save Source');

    await user.type(nameInput, 'Test Data Source');
    await user.click(saveButton);

    expect(setup({ onSubmit: vi.fn() }).onSubmit).toHaveBeenCalled();
  });
});