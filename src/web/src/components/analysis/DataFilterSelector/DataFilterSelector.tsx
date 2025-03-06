import React, { useState, useEffect, useCallback } from 'react'; // ^18.2.0
import { FormGroup, Select, Button } from '../../common';
import { DataFilter } from '../../../types/analysis.types';
import { getDataSources } from '../../../api/data-source-api';
import useAlert from '../../../hooks/useAlert';

/**
 * Props interface for the DataFilterSelector component
 */
interface DataFilterSelectorProps {
  dataSourceIds: string[] | null;
  origins: string[] | null;
  destinations: string[] | null;
  carriers: string[] | null;
  transportModes: string[] | null;
  currency: string | null;
  onDataSourcesChange: (ids: string[]) => void;
  onOriginsChange: (origins: string[]) => void;
  onDestinationsChange: (destinations: string[]) => void;
  onCarriersChange: (carriers: string[]) => void;
  onTransportModesChange: (modes: string[]) => void;
  onCurrencyChange: (currency: string) => void;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
}

/**
 * Interface for data source select options
 */
interface DataSourceOption {
  value: string;
  label: string;
}

/**
 * Interface for location (origin/destination) select options
 */
interface LocationOption {
  value: string;
  label: string;
}

/**
 * Interface for carrier select options
 */
interface CarrierOption {
  value: string;
  label: string;
}

/**
 * Interface for transport mode select options
 */
interface TransportModeOption {
  value: string;
  label: string;
}

/**
 * Interface for currency select options
 */
interface CurrencyOption {
  value: string;
  label: string;
}

/**
 * A React component that allows users to configure data filters for freight price movement analysis.
 * This component provides selection interfaces for data sources, origins, destinations, carriers,
 * transport modes, and currency filters.
 */
const DataFilterSelector: React.FC<DataFilterSelectorProps> = ({
  dataSourceIds,
  origins,
  destinations,
  carriers,
  transportModes,
  currency,
  onDataSourcesChange,
  onOriginsChange,
  onDestinationsChange,
  onCarriersChange,
  onTransportModesChange,
  onCurrencyChange,
  errors,
  touched,
}) => {
  // State for available options
  const [dataSources, setDataSources] = useState<DataSourceOption[]>([]);
  const [originOptions, setOriginOptions] = useState<LocationOption[]>([]);
  const [destinationOptions, setDestinationOptions] = useState<LocationOption[]>([]);
  const [carrierOptions, setCarrierOptions] = useState<CarrierOption[]>([]);
  const [transportModeOptions, setTransportModeOptions] = useState<TransportModeOption[]>([]);
  const [currencyOptions, setCurrencyOptions] = useState<CurrencyOption[]>([]);

  // Loading states
  const [isLoadingDataSources, setIsLoadingDataSources] = useState(false);
  const [isLoadingOrigins, setIsLoadingOrigins] = useState(false);
  const [isLoadingDestinations, setIsLoadingDestinations] = useState(false);
  const [isLoadingCarriers, setIsLoadingCarriers] = useState(false);
  const [isLoadingTransportModes, setIsLoadingTransportModes] = useState(false);

  // Use alert hook for error notifications
  const { showAlert } = useAlert();

  // Fetch data sources on component mount
  const fetchDataSources = useCallback(async () => {
    setIsLoadingDataSources(true);
    try {
      const response = await getDataSources({ 
        page: 1, 
        pageSize: 100,
        sortBy: 'name',
        sortDirection: 'asc'
      });
      
      if (response.success && response.data) {
        const formattedOptions = response.data.map(ds => ({
          value: ds.id,
          label: ds.name
        }));
        setDataSources(formattedOptions);
      } else {
        showAlert('error', 'Failed to load data sources', { 
          dismissible: true, 
          duration: 5000 
        });
      }
    } catch (error) {
      console.error('Error fetching data sources:', error);
      showAlert('error', 'Failed to load data sources. Please try again later.', { 
        dismissible: true, 
        duration: 5000 
      });
    } finally {
      setIsLoadingDataSources(false);
    }
  }, [showAlert]);

  // Fetch filter options based on selected data sources
  const fetchFilterOptions = useCallback(async () => {
    if (!dataSourceIds || dataSourceIds.length === 0) {
      return;
    }

    // Set loading states
    setIsLoadingOrigins(true);
    setIsLoadingDestinations(true);
    setIsLoadingCarriers(true);
    setIsLoadingTransportModes(true);

    try {
      // In a production environment, we would make API calls to fetch these options
      // based on the selected data sources. For now, we'll use sample data.
      
      // Simulate API calls with setTimeout
      setTimeout(() => {
        const mockOrigins = [
          { value: 'us-nyc', label: 'New York, USA' },
          { value: 'us-lax', label: 'Los Angeles, USA' },
          { value: 'cn-sha', label: 'Shanghai, China' },
          { value: 'nl-rot', label: 'Rotterdam, Netherlands' },
          { value: 'sg-sin', label: 'Singapore' }
        ];
        setOriginOptions(mockOrigins);
        setIsLoadingOrigins(false);
      }, 500);
      
      setTimeout(() => {
        const mockDestinations = [
          { value: 'us-nyc', label: 'New York, USA' },
          { value: 'us-lax', label: 'Los Angeles, USA' },
          { value: 'cn-sha', label: 'Shanghai, China' },
          { value: 'nl-rot', label: 'Rotterdam, Netherlands' },
          { value: 'sg-sin', label: 'Singapore' }
        ];
        setDestinationOptions(mockDestinations);
        setIsLoadingDestinations(false);
      }, 700);
      
      setTimeout(() => {
        const mockCarriers = [
          { value: 'maersk', label: 'Maersk' },
          { value: 'msc', label: 'Mediterranean Shipping Company' },
          { value: 'cosco', label: 'COSCO Shipping' },
          { value: 'cma-cgm', label: 'CMA CGM' },
          { value: 'hapag-lloyd', label: 'Hapag-Lloyd' }
        ];
        setCarrierOptions(mockCarriers);
        setIsLoadingCarriers(false);
      }, 600);
      
      setTimeout(() => {
        const mockTransportModes = [
          { value: 'ocean', label: 'Ocean' },
          { value: 'air', label: 'Air' },
          { value: 'road', label: 'Road' },
          { value: 'rail', label: 'Rail' }
        ];
        setTransportModeOptions(mockTransportModes);
        setIsLoadingTransportModes(false);
      }, 400);
      
      // Set currency options (these are typically static)
      setCurrencyOptions([
        { value: 'USD', label: 'USD - US Dollar' },
        { value: 'EUR', label: 'EUR - Euro' },
        { value: 'GBP', label: 'GBP - British Pound' },
        { value: 'CNY', label: 'CNY - Chinese Yuan' },
        { value: 'JPY', label: 'JPY - Japanese Yen' }
      ]);
      
    } catch (error) {
      console.error('Error fetching filter options:', error);
      showAlert('error', 'Failed to load filter options. Please try again later.', {
        dismissible: true,
        duration: 5000
      });
      
      // Reset loading states on error
      setIsLoadingOrigins(false);
      setIsLoadingDestinations(false);
      setIsLoadingCarriers(false);
      setIsLoadingTransportModes(false);
    }
  }, [dataSourceIds, showAlert]);

  // Fetch data sources on mount
  useEffect(() => {
    fetchDataSources();
  }, [fetchDataSources]);

  // Fetch filter options when data sources change
  useEffect(() => {
    fetchFilterOptions();
  }, [dataSourceIds, fetchFilterOptions]);

  // Handle data source change
  const handleDataSourceChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOptions = Array.from(event.target.selectedOptions, option => option.value);
    onDataSourcesChange(selectedOptions);
  };

  // Handle origin change
  const handleOriginChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOptions = Array.from(event.target.selectedOptions, option => option.value);
    onOriginsChange(selectedOptions);
  };

  // Handle destination change
  const handleDestinationChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOptions = Array.from(event.target.selectedOptions, option => option.value);
    onDestinationsChange(selectedOptions);
  };

  // Handle carrier change
  const handleCarrierChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOptions = Array.from(event.target.selectedOptions, option => option.value);
    onCarriersChange(selectedOptions);
  };

  // Handle transport mode change
  const handleTransportModeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOptions = Array.from(event.target.selectedOptions, option => option.value);
    onTransportModesChange(selectedOptions);
  };

  // Handle currency change
  const handleCurrencyChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onCurrencyChange(event.target.value);
  };

  return (
    <div className="data-filter-selector">
      <FormGroup
        label="Data Sources"
        required
        isInvalid={Boolean(errors.dataSourceIds && touched.dataSourceIds)}
        validationMessage={errors.dataSourceIds}
      >
        <Select
          id="dataSourceIds"
          name="dataSourceIds"
          value={dataSourceIds?.join(',') || ''}
          options={dataSources}
          onChange={handleDataSourceChange}
          placeholder="Select data sources"
          isInvalid={Boolean(errors.dataSourceIds && touched.dataSourceIds)}
          disabled={isLoadingDataSources}
          multiple
        />
      </FormGroup>

      <FormGroup
        label="Origins"
        isInvalid={Boolean(errors.origins && touched.origins)}
        validationMessage={errors.origins}
      >
        <Select
          id="origins"
          name="origins"
          value={origins?.join(',') || ''}
          options={originOptions}
          onChange={handleOriginChange}
          placeholder="All Origins"
          isInvalid={Boolean(errors.origins && touched.origins)}
          disabled={isLoadingOrigins || !dataSourceIds?.length}
          multiple
        />
      </FormGroup>

      <FormGroup
        label="Destinations"
        isInvalid={Boolean(errors.destinations && touched.destinations)}
        validationMessage={errors.destinations}
      >
        <Select
          id="destinations"
          name="destinations"
          value={destinations?.join(',') || ''}
          options={destinationOptions}
          onChange={handleDestinationChange}
          placeholder="All Destinations"
          isInvalid={Boolean(errors.destinations && touched.destinations)}
          disabled={isLoadingDestinations || !dataSourceIds?.length}
          multiple
        />
      </FormGroup>

      <FormGroup
        label="Carriers"
        isInvalid={Boolean(errors.carriers && touched.carriers)}
        validationMessage={errors.carriers}
      >
        <Select
          id="carriers"
          name="carriers"
          value={carriers?.join(',') || ''}
          options={carrierOptions}
          onChange={handleCarrierChange}
          placeholder="All Carriers"
          isInvalid={Boolean(errors.carriers && touched.carriers)}
          disabled={isLoadingCarriers || !dataSourceIds?.length}
          multiple
        />
      </FormGroup>

      <FormGroup
        label="Transport Modes"
        isInvalid={Boolean(errors.transportModes && touched.transportModes)}
        validationMessage={errors.transportModes}
      >
        <Select
          id="transportModes"
          name="transportModes"
          value={transportModes?.join(',') || ''}
          options={transportModeOptions}
          onChange={handleTransportModeChange}
          placeholder="All Transport Modes"
          isInvalid={Boolean(errors.transportModes && touched.transportModes)}
          disabled={isLoadingTransportModes || !dataSourceIds?.length}
          multiple
        />
      </FormGroup>

      <FormGroup
        label="Currency"
        isInvalid={Boolean(errors.currency && touched.currency)}
        validationMessage={errors.currency}
      >
        <Select
          id="currency"
          name="currency"
          value={currency || ''}
          options={currencyOptions}
          onChange={handleCurrencyChange}
          placeholder="Select Currency"
          isInvalid={Boolean(errors.currency && touched.currency)}
          disabled={!dataSourceIds?.length}
        />
      </FormGroup>

      <div className="filter-actions">
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={() => {
            // Reset filters logic
            onOriginsChange([]);
            onDestinationsChange([]);
            onCarriersChange([]);
            onTransportModesChange([]);
            onCurrencyChange('');
          }}
          disabled={!dataSourceIds?.length}
        >
          Reset Filters
        </Button>
      </div>
    </div>
  );
};

export default DataFilterSelector;