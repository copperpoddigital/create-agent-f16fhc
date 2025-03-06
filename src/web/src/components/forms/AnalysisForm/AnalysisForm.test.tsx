# src/web/src/components/forms/AnalysisForm/AnalysisForm.test.tsx
```typescript
import React from 'react'; // v18.2.0
import { render, screen as rtlScreen } from '@testing-library/react'; // v14.0.0
import {
  customRender,
  screen,
  waitFor,
  fireEvent,
  userEvent,
} from '../../../utils/test-utils';
import AnalysisForm from './AnalysisForm';
import { createTimePeriod, createAnalysisRequest } from '../../../api/analysis-api';
import { TimeGranularity, OutputFormat } from '../../../types/analysis.types';
import jest from 'jest'; // v29.5.0

// Mock API functions
jest.mock('../../../api/analysis-api', () => ({
  createTimePeriod: jest.fn(),
  createAnalysisRequest: jest.fn(),
}));

// Mock setup function
const setup = () => {
  // Mock API functions
  const mockCreateTimePeriod = createTimePeriod as jest.Mock;
  const mockCreateAnalysisRequest = createAnalysisRequest as jest.Mock;

  // Create onSubmit mock function
  const onSubmit = jest.fn();

  // Create onCancel mock function
  const onCancel = jest.fn();

  return {
    mockCreateTimePeriod,
    mockCreateAnalysisRequest,
    onSubmit,
    onCancel,
  };
};

describe('AnalysisForm', () => {
  it('renders the form with all required sections', () => {
    // Arrange
    const { onCancel, onSubmit } = setup();

    // Act
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={onCancel} />);

    // Assert
    expect(screen.getByText('Analysis Details')).toBeInTheDocument();
    expect(screen.getByText('Time Period Selection')).toBeInTheDocument();
    expect(screen.getByText('Data Filters')).toBeInTheDocument();
    expect(screen.getByText('Analysis Options')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Analysis' })).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    // Arrange
    const { onSubmit, onCancel } = setup();
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={onCancel} />);

    // Act
    fireEvent.click(screen.getByRole('button', { name: 'Create Analysis' }));

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Analysis name is required')).toBeInTheDocument();
      expect(screen.getByText('Time period or start date, end date, and granularity are required')).toBeInTheDocument();
    });
  });

  it('handles time period selection', () => {
    // Arrange
    const { onSubmit, onCancel } = setup();
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={onCancel} />);

    // Act
    fireEvent.click(screen.getByLabelText('Create Custom Period'));
    fireEvent.change(screen.getByLabelText('Start Date'), { target: { value: '2023-01-01' } });
    fireEvent.change(screen.getByLabelText('End Date'), { target: { value: '2023-01-31' } });
    fireEvent.click(screen.getByLabelText('Monthly'));

    // Assert
    expect(screen.getByLabelText('Start Date')).toHaveValue('2023-01-01');
    expect(screen.getByLabelText('End Date')).toHaveValue('2023-01-31');
    expect(screen.getByLabelText('Monthly')).toBeChecked();
  });

  it('handles data filter selection', () => {
    // Arrange
    const { onSubmit, onCancel } = setup();
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={onCancel} />);

    // Act
    fireEvent.mouseDown(screen.getByLabelText('Data Sources'));
    const dataSourceOptions = screen.getAllByRole('option');
    fireEvent.click(dataSourceOptions[0]);
    fireEvent.click(dataSourceOptions[1]);
    fireEvent.keyDown(screen.getByLabelText('Data Sources'), { key: 'Escape' });

    // Assert
    expect(screen.getByLabelText('Data Sources')).toHaveValue('option1,option2');
  });

  it('handles analysis options selection', () => {
    // Arrange
    const { onSubmit, onCancel } = setup();
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={onCancel} />);

    // Act
    fireEvent.click(screen.getByLabelText('Calculate absolute change'));
    fireEvent.click(screen.getByLabelText('Calculate percentage change'));
    fireEvent.click(screen.getByLabelText('Identify trend direction'));
    fireEvent.click(screen.getByLabelText('Compare to historical baseline'));
    fireEvent.change(screen.getByLabelText('Output Format'), { target: { value: 'csv' } });
    fireEvent.click(screen.getByLabelText('Include visualization'));

    // Assert
    expect(screen.getByLabelText('Calculate absolute change')).toBeChecked();
    expect(screen.getByLabelText('Calculate percentage change')).toBeChecked();
    expect(screen.getByLabelText('Identify trend direction')).toBeChecked();
    expect(screen.getByLabelText('Compare to historical baseline')).toBeChecked();
    expect(screen.getByLabelText('Output Format')).toHaveValue('csv');
    expect(screen.getByLabelText('Include visualization')).toBeChecked();
  });

  it('shows baseline period selection when compareToHistoricalBaseline is checked', () => {
    // Arrange
    const { onSubmit, onCancel } = setup();
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={onCancel} />);

    // Act
    fireEvent.click(screen.getByLabelText('Compare to historical baseline'));

    // Assert
    expect(screen.getByText('Baseline period')).toBeInTheDocument();
  });

  it('submits the form with valid data', async () => {
    // Arrange
    const { mockCreateTimePeriod, mockCreateAnalysisRequest, onSubmit } = setup();
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={() => {}} />);

    // Act
    fireEvent.change(screen.getByLabelText('Analysis Name'), { target: { value: 'Test Analysis' } });
    fireEvent.click(screen.getByLabelText('Create Custom Period'));
    fireEvent.change(screen.getByLabelText('Start Date'), { target: { value: '2023-01-01' } });
    fireEvent.change(screen.getByLabelText('End Date'), { target: { value: '2023-01-31' } });
    fireEvent.click(screen.getByLabelText('Monthly'));
    fireEvent.click(screen.getByRole('button', { name: 'Create Analysis' }));

    // Assert
    await waitFor(() => {
      expect(mockCreateTimePeriod).toHaveBeenCalledTimes(0);
      expect(mockCreateAnalysisRequest).toHaveBeenCalledTimes(1);
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });
  });

  it('creates a new time period when custom time period is selected', async () => {
    // Arrange
    const { mockCreateTimePeriod, mockCreateAnalysisRequest, onSubmit } = setup();
    mockCreateTimePeriod.mockResolvedValue({ data: { id: 'new-time-period-id' } });
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={() => {}} />);

    // Act
    fireEvent.change(screen.getByLabelText('Analysis Name'), { target: { value: 'Test Analysis' } });
    fireEvent.click(screen.getByLabelText('Create Custom Period'));
    fireEvent.change(screen.getByLabelText('Start Date'), { target: { value: '2023-01-01' } });
    fireEvent.change(screen.getByLabelText('End Date'), { target: { value: '2023-01-31' } });
    fireEvent.click(screen.getByLabelText('Monthly'));
    fireEvent.click(screen.getByRole('button', { name: 'Create Analysis' }));

    // Assert
    await waitFor(() => {
      expect(mockCreateTimePeriod).toHaveBeenCalledTimes(1);
      expect(mockCreateAnalysisRequest).toHaveBeenCalledTimes(1);
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });
  });

  it('handles API errors during submission', async () => {
    // Arrange
    const { mockCreateTimePeriod, mockCreateAnalysisRequest, onSubmit } = setup();
    mockCreateAnalysisRequest.mockRejectedValue(new Error('API error'));
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={() => {}} />);

    // Act
    fireEvent.change(screen.getByLabelText('Analysis Name'), { target: { value: 'Test Analysis' } });
    fireEvent.click(screen.getByLabelText('Create Custom Period'));
    fireEvent.change(screen.getByLabelText('Start Date'), { target: { value: '2023-01-01' } });
    fireEvent.change(screen.getByLabelText('End Date'), { target: { value: '2023-01-31' } });
    fireEvent.click(screen.getByLabelText('Monthly'));
    fireEvent.click(screen.getByRole('button', { name: 'Create Analysis' }));

    // Assert
    await waitFor(() => {
      expect(mockCreateAnalysisRequest).toHaveBeenCalledTimes(1);
      expect(onSubmit).not.toHaveBeenCalled();
    });
  });

  it('calls onCancel when cancel button is clicked', () => {
    // Arrange
    const { onCancel } = setup();
    customRender(<AnalysisForm onSubmit={() => {}} onCancel={onCancel} />);

    // Act
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));

    // Assert
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('disables form controls during submission', async () => {
    // Arrange
    const { mockCreateTimePeriod, mockCreateAnalysisRequest, onSubmit } = setup();
    mockCreateAnalysisRequest.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    customRender(<AnalysisForm onSubmit={onSubmit} onCancel={() => {}} />);

    // Act
    fireEvent.change(screen.getByLabelText('Analysis Name'), { target: { value: 'Test Analysis' } });
    fireEvent.click(screen.getByLabelText('Create Custom Period'));
    fireEvent.change(screen.getByLabelText('Start Date'), { target: { value: '2023-01-01' } });
    fireEvent.change(screen.getByLabelText('End Date'), { target: { value: '2023-01-31' } });
    fireEvent.click(screen.getByLabelText('Monthly'));
    fireEvent.click(screen.getByRole('button', { name: 'Create Analysis' }));

    // Assert
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Create Analysis' })).toBeDisabled();
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled();
    });
  });

  it('renders with initial values when provided', () => {
    // Arrange
    const { onSubmit, onCancel } = setup();
    const initialValues = {
      name: 'Initial Analysis Name',
      description: 'Initial Description',
      timePeriodId: 'initial-time-period',
      startDate: '2023-02-01',
      endDate: '2023-02-28',
      granularity: TimeGranularity.WEEKLY,
      customInterval: '',
      dataSourceIds: ['ds1', 'ds2'],
      origins: ['origin1', 'origin2'],
      destinations: ['dest1', 'dest2'],
      carriers: ['carrier1', 'carrier2'],
      transportModes: ['ocean', 'air'],
      currency: 'USD',
      calculateAbsoluteChange: true,
      calculatePercentageChange: false,
      identifyTrendDirection: true,
      compareToHistoricalBaseline: false,
      baselinePeriodId: null,
      includeAggregates: false,
      outputFormat: OutputFormat.JSON,
      includeVisualization: true
    };

    // Act
    customRender(<AnalysisForm initialValues={initialValues} onSubmit={onSubmit} onCancel={onCancel} />);

    // Assert
    expect(screen.getByLabelText('Analysis Name')).toHaveValue('Initial Analysis Name');
    expect(screen.getByLabelText('Description')).toHaveValue('Initial Description');
  });
});