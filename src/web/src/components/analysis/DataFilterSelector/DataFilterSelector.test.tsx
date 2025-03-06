import React from 'react'; // ^18.2.0
import { vi } from 'vitest'; // ^0.29.8
import DataFilterSelector from './DataFilterSelector';
import { customRender, screen, waitFor, fireEvent, userEvent } from '../../../utils/test-utils';

// Mock API functions and hooks
vi.mock('../../../api/data-source-api', () => ({
  getDataSources: vi.fn(),
}));

vi.mock('../../../hooks/useAlert', () => ({
  default: vi.fn(),
}));

// Mock the getDataSources API function
const mockGetDataSources = () => {
  return Promise.resolve({
    success: true,
    data: [
      { id: '1', name: 'DataSource 1' },
      { id: '2', name: 'DataSource 2' },
    ],
  });
};

// Mock implementation for fetching filter options like origins, destinations, carriers, etc.
const mockFetchFilterOptions = () => {
  return Promise.resolve({
    success: true,
    data: [
      { value: 'origin1', label: 'Origin 1' },
      { value: 'origin2', label: 'Origin 2' },
    ],
  });
};

// Helper function to render the DataFilterSelector component with props
const renderDataFilterSelector = (props: object) => {
  // Create default props with mock handlers
  const defaultProps = {
    dataSourceIds: null,
    origins: null,
    destinations: null,
    carriers: null,
    transportModes: null,
    currency: null,
    onDataSourcesChange: vi.fn(),
    onOriginsChange: vi.fn(),
    onDestinationsChange: vi.fn(),
    onCarriersChange: vi.fn(),
    onTransportModesChange: vi.fn(),
    onCurrencyChange: vi.fn(),
    errors: {},
    touched: {},
  };

  // Merge provided props with default props
  const mergedProps = { ...defaultProps, ...props };

  // Render the DataFilterSelector component with customRender
  return customRender(<DataFilterSelector {...mergedProps as any} />);
};

describe('DataFilterSelector', () => {
  it('renders correctly with default props', () => {
    // Render the DataFilterSelector component with default props
    renderDataFilterSelector({});

    // Verify that all filter sections are rendered
    expect(screen.getByLabelText('Data Sources')).toBeInTheDocument();
    expect(screen.getByLabelText('Origins')).toBeInTheDocument();
    expect(screen.getByLabelText('Destinations')).toBeInTheDocument();
    expect(screen.getByLabelText('Carriers')).toBeInTheDocument();
    expect(screen.getByLabelText('Transport Modes')).toBeInTheDocument();
    expect(screen.getByLabelText('Currency')).toBeInTheDocument();

    // Verify that the data sources dropdown is enabled
    expect(screen.getByRole('combobox', { name: 'Data Sources' })).toBeEnabled();

    // Verify that other dropdowns are disabled until data sources are selected
    expect(screen.getByRole('combobox', { name: 'Origins' })).toBeDisabled();
    expect(screen.getByRole('combobox', { name: 'Destinations' })).toBeDisabled();
    expect(screen.getByRole('combobox', { name: 'Carriers' })).toBeDisabled();
    expect(screen.getByRole('combobox', { name: 'Transport Modes' })).toBeDisabled();
    expect(screen.getByRole('combobox', { name: 'Currency' })).toBeDisabled();
  });

  it('fetches data sources on mount', async () => {
    // Mock the getDataSources API function
    (vi.mocked(require('../../../api/data-source-api').getDataSources)).mockImplementation(mockGetDataSources);

    // Render the DataFilterSelector component
    renderDataFilterSelector({});

    // Verify that getDataSources was called
    expect(require('../../../api/data-source-api').getDataSources).toHaveBeenCalled();

    // Verify that data sources are displayed in the dropdown after loading
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Data Sources' })).toHaveTextContent('DataSource 1');
      expect(screen.getByRole('combobox', { name: 'Data Sources' })).toHaveTextContent('DataSource 2');
    });
  });

  it('handles data source selection', async () => {
    // Mock the getDataSources API function
    (vi.mocked(require('../../../api/data-source-api').getDataSources)).mockImplementation(mockGetDataSources);

    // Render the DataFilterSelector component
    const onDataSourcesChange = vi.fn();
    renderDataFilterSelector({ onDataSourcesChange });

    // Wait for data sources to load
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Data Sources' })).toHaveTextContent('DataSource 1');
    });

    // Select a data source from the dropdown
    fireEvent.change(screen.getByRole('combobox', { name: 'Data Sources' }), {
      target: { value: '1' },
    });

    // Verify that onDataSourcesChange callback was called with the selected value
    expect(onDataSourcesChange).toHaveBeenCalledWith(['1']);

    // Verify that other dropdowns are enabled after data source selection
    expect(screen.getByRole('combobox', { name: 'Origins' })).toBeEnabled();
    expect(screen.getByRole('combobox', { name: 'Destinations' })).toBeEnabled();
    expect(screen.getByRole('combobox', { name: 'Carriers' })).toBeEnabled();
    expect(screen.getByRole('combobox', { name: 'Transport Modes' })).toBeEnabled();
    expect(screen.getByRole('combobox', { name: 'Currency' })).toBeEnabled();
  });

  it('fetches filter options when data sources change', async () => {
    // Mock the API functions for fetching data sources and filter options
    (vi.mocked(require('../../../api/data-source-api').getDataSources)).mockImplementation(mockGetDataSources);

    // Mock the API functions for fetching data sources and filter options
    const mockOrigins = [{ value: 'origin1', label: 'Origin 1' }, { value: 'origin2', label: 'Origin 2' }];
    const mockDestinations = [{ value: 'destination1', label: 'Destination 1' }, { value: 'destination2', label: 'Destination 2' }];
    const mockCarriers = [{ value: 'carrier1', label: 'Carrier 1' }, { value: 'carrier2', label: 'Carrier 2' }];
    const mockTransportModes = [{ value: 'mode1', label: 'Mode 1' }, { value: 'mode2', label: 'Mode 2' }];
    const mockCurrencies = [{ value: 'USD', label: 'USD' }, { value: 'EUR', label: 'EUR' }];

    // Render the component with selected data sources
    renderDataFilterSelector({ dataSourceIds: ['1'] });

    // Verify that filter options are fetched
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Origins' })).toHaveTextContent('New York, USA');
      expect(screen.getByRole('combobox', { name: 'Destinations' })).toHaveTextContent('New York, USA');
      expect(screen.getByRole('combobox', { name: 'Carriers' })).toHaveTextContent('Maersk');
      expect(screen.getByRole('combobox', { name: 'Transport Modes' })).toHaveTextContent('Ocean');
      expect(screen.getByRole('combobox', { name: 'Currency' })).toHaveTextContent('USD - US Dollar');
    });
  });

  it('handles origin selection', async () => {
    // Render the component with data sources selected and origin options loaded
    const onOriginsChange = vi.fn();
    renderDataFilterSelector({
      dataSourceIds: ['1'],
      origins: [],
      onOriginsChange,
    });

    // Wait for data sources to load
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Origins' })).toHaveTextContent('New York, USA');
    });

    // Select an origin from the dropdown
    fireEvent.change(screen.getByRole('combobox', { name: 'Origins' }), {
      target: { value: 'us-nyc' },
    });

    // Verify that onOriginsChange callback was called with the selected value
    expect(onOriginsChange).toHaveBeenCalledWith(['us-nyc']);
  });

  it('handles destination selection', async () => {
    // Render the component with data sources selected and destination options loaded
    const onDestinationsChange = vi.fn();
    renderDataFilterSelector({
      dataSourceIds: ['1'],
      destinations: [],
      onDestinationsChange,
    });

    // Wait for data sources to load
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Destinations' })).toHaveTextContent('New York, USA');
    });

    // Select a destination from the dropdown
    fireEvent.change(screen.getByRole('combobox', { name: 'Destinations' }), {
      target: { value: 'us-nyc' },
    });

    // Verify that onDestinationsChange callback was called with the selected value
    expect(onDestinationsChange).toHaveBeenCalledWith(['us-nyc']);
  });

  it('handles carrier selection', async () => {
    // Render the component with data sources selected and carrier options loaded
    const onCarriersChange = vi.fn();
    renderDataFilterSelector({
      dataSourceIds: ['1'],
      carriers: [],
      onCarriersChange,
    });

    // Wait for data sources to load
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Carriers' })).toHaveTextContent('Maersk');
    });

    // Select a carrier from the dropdown
    fireEvent.change(screen.getByRole('combobox', { name: 'Carriers' }), {
      target: { value: 'maersk' },
    });

    // Verify that onCarriersChange callback was called with the selected value
    expect(onCarriersChange).toHaveBeenCalledWith(['maersk']);
  });

  it('handles transport mode selection', async () => {
    // Render the component with data sources selected and transport mode options loaded
    const onTransportModesChange = vi.fn();
    renderDataFilterSelector({
      dataSourceIds: ['1'],
      transportModes: [],
      onTransportModesChange,
    });

    // Wait for data sources to load
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Transport Modes' })).toHaveTextContent('Ocean');
    });

    // Select a transport mode from the dropdown
    fireEvent.change(screen.getByRole('combobox', { name: 'Transport Modes' }), {
      target: { value: 'ocean' },
    });

    // Verify that onTransportModesChange callback was called with the selected value
    expect(onTransportModesChange).toHaveBeenCalledWith(['ocean']);
  });

  it('handles currency selection', async () => {
    // Render the component with data sources selected and currency options loaded
    const onCurrencyChange = vi.fn();
    renderDataFilterSelector({
      dataSourceIds: ['1'],
      currency: '',
      onCurrencyChange,
    });

    // Wait for data sources to load
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Currency' })).toHaveTextContent('USD - US Dollar');
    });

    // Select a currency from the dropdown
    fireEvent.change(screen.getByRole('combobox', { name: 'Currency' }), {
      target: { value: 'USD' },
    });

    // Verify that onCurrencyChange callback was called with the selected value
    expect(onCurrencyChange).toHaveBeenCalledWith('USD');
  });

  it('displays validation errors', () => {
    // Render the component with errors and touched props
    const errors = { dataSourceIds: 'Data source is required' };
    const touched = { dataSourceIds: true };
    renderDataFilterSelector({ errors, touched });

    // Verify that error messages are displayed for the fields with errors
    expect(screen.getByText('Data source is required')).toBeInTheDocument();

    // Verify that fields with errors have the appropriate error styling
    expect(screen.getByRole('combobox', { name: 'Data Sources' })).toHaveClass('is-invalid');
  });

  it('handles loading states correctly', async () => {
    // Mock API functions to delay responses
    (vi.mocked(require('../../../api/data-source-api').getDataSources)).mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(mockGetDataSources());
        }, 500);
      });
    });

    // Render the component
    renderDataFilterSelector({});

    // Verify that loading indicators are shown while data is being fetched
    expect(screen.getByRole('combobox', { name: 'Data Sources' })).toBeDisabled();

    // Verify that loading indicators are removed when data is loaded
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: 'Data Sources' })).toBeEnabled();
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock API functions to reject with errors
    (vi.mocked(require('../../../api/data-source-api').getDataSources)).mockImplementation(() => {
      return Promise.reject(new Error('API error'));
    });

    const mockShowAlert = vi.fn();
    (require('../../../hooks/useAlert') as any).default = () => ({
      showAlert: mockShowAlert,
    });

    // Render the component
    renderDataFilterSelector({});

    // Verify that error alerts are shown when API calls fail
    await waitFor(() => {
      expect(mockShowAlert).toHaveBeenCalledWith(
        'error',
        'Failed to load data sources. Please try again later.',
        { dismissible: true, duration: 5000 }
      );
    });

    // Verify that the component remains usable after API errors
    expect(screen.getByLabelText('Data Sources')).toBeInTheDocument();
  });
});