import React from 'react';
import { vi } from 'vitest';
import { screen, waitFor, customRender } from '../../../utils/test-utils';
import userEvent from '@testing-library/user-event';
import SavedAnalyses from './SavedAnalyses';
import { getAnalysisRequests } from '../../../api/analysis-api';
import useApi from '../../../hooks/useApi';
import { AnalysisRequest } from '../../../types/analysis.types';

// Mock the useApi hook
vi.mock('../../../hooks/useApi', () => ({
  default: vi.fn()
}));

// Mock the getAnalysisRequests function
vi.mock('../../../api/analysis-api', () => ({
  getAnalysisRequests: vi.fn()
}));

describe('SavedAnalyses', () => {
  // Mock data for analysis requests
  const mockAnalyses: AnalysisRequest[] = [
    {
      id: '1',
      name: 'Q2 Ocean Freight',
      description: 'Price movement analysis for Q2 ocean freight',
      time_period_id: '1',
      time_period: {
        id: '1',
        name: 'Q2 2023',
        start_date: '2023-04-01',
        end_date: '2023-06-30',
        granularity: 'weekly',
        custom_interval: null,
        is_custom: false,
        created_by: 'user1',
        created_at: '2023-04-01T00:00:00Z'
      },
      data_source_ids: ['1', '2'],
      filters: [],
      options: {
        calculate_absolute_change: true,
        calculate_percentage_change: true,
        identify_trend_direction: true,
        compare_to_baseline: false,
        baseline_period_id: null,
        output_format: 'json',
        include_visualization: true
      },
      status: 'completed',
      created_by: 'user1',
      created_at: '2023-04-01T00:00:00Z',
      updated_at: '2023-04-01T12:00:00Z',
      last_run_at: '2023-04-01T12:00:00Z'
    },
    {
      id: '2',
      name: 'Air vs Ocean 2023',
      description: 'Comparative analysis between air and ocean freight in 2023',
      time_period_id: '2',
      time_period: {
        id: '2',
        name: 'Year 2023',
        start_date: '2023-01-01',
        end_date: '2023-12-31',
        granularity: 'monthly',
        custom_interval: null,
        is_custom: false,
        created_by: 'user1',
        created_at: '2023-01-15T00:00:00Z'
      },
      data_source_ids: ['1', '3'],
      filters: [],
      options: {
        calculate_absolute_change: true,
        calculate_percentage_change: true,
        identify_trend_direction: true,
        compare_to_baseline: true,
        baseline_period_id: '3',
        output_format: 'csv',
        include_visualization: true
      },
      status: 'completed',
      created_by: 'user1',
      created_at: '2023-01-15T00:00:00Z',
      updated_at: '2023-01-20T10:30:00Z',
      last_run_at: '2023-01-20T10:30:00Z'
    }
  ];

  beforeEach(() => {
    vi.resetAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('calls execute with correct parameters on mount', () => {
    const executeMock = vi.fn();

    // Mock useApi to return a mock execute function
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { data: null, isLoading: true, isError: false },
      actions: { execute: executeMock }
    });

    // Render with default limit of 5
    customRender(
      <SavedAnalyses 
        onViewAnalysis={vi.fn()} 
        onNewAnalysis={vi.fn()} 
      />
    );

    // Check if execute was called with the correct parameters
    expect(executeMock).toHaveBeenCalledWith({
      page: 1,
      pageSize: 5,
      sortBy: null,
      sortDirection: null
    });
  });

  it('respects the limit prop when calling execute', () => {
    const executeMock = vi.fn();

    // Mock useApi to return a mock execute function
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { data: null, isLoading: true, isError: false },
      actions: { execute: executeMock }
    });

    // Render with a custom limit
    customRender(
      <SavedAnalyses 
        limit={10}
        onViewAnalysis={vi.fn()} 
        onNewAnalysis={vi.fn()} 
      />
    );

    // Check if execute was called with the custom limit
    expect(executeMock).toHaveBeenCalledWith({
      page: 1,
      pageSize: 10,
      sortBy: null,
      sortDirection: null
    });
  });

  it('renders loading state', () => {
    // Mock useApi to return loading state
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { data: null, isLoading: true, isError: false },
      actions: { execute: vi.fn() }
    });

    customRender(
      <SavedAnalyses 
        onViewAnalysis={vi.fn()} 
        onNewAnalysis={vi.fn()} 
      />
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders error state', () => {
    // Mock useApi to return error state
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { data: null, isLoading: false, isError: true },
      actions: { execute: vi.fn() }
    });

    customRender(
      <SavedAnalyses 
        onViewAnalysis={vi.fn()} 
        onNewAnalysis={vi.fn()} 
      />
    );

    expect(screen.getByText(/failed to load saved analyses/i)).toBeInTheDocument();
  });

  it('renders empty state', () => {
    // Mock useApi to return empty data
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { data: { data: [] }, isLoading: false, isError: false },
      actions: { execute: vi.fn() }
    });

    customRender(
      <SavedAnalyses 
        onViewAnalysis={vi.fn()} 
        onNewAnalysis={vi.fn()} 
      />
    );

    expect(screen.getByText(/no saved analyses found/i)).toBeInTheDocument();
  });

  it('renders list of analyses', () => {
    // Mock useApi to return analysis data
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { 
        data: { data: mockAnalyses }, 
        isLoading: false, 
        isError: false 
      },
      actions: { execute: vi.fn() }
    });

    customRender(
      <SavedAnalyses 
        onViewAnalysis={vi.fn()} 
        onNewAnalysis={vi.fn()} 
      />
    );

    expect(screen.getByText('Q2 Ocean Freight')).toBeInTheDocument();
    expect(screen.getByText('Air vs Ocean 2023')).toBeInTheDocument();
    expect(screen.getByText(/last updated:/i)).toBeInTheDocument();
  });

  it('limits number of displayed analyses', () => {
    // Create more mock analyses
    const manyMockAnalyses = [
      ...mockAnalyses,
      {
        ...mockAnalyses[0],
        id: '3',
        name: 'Analysis 3',
      },
      {
        ...mockAnalyses[0],
        id: '4',
        name: 'Analysis 4',
      }
    ];

    // Mock useApi to return more analyses than the limit
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { 
        data: { data: manyMockAnalyses }, 
        isLoading: false, 
        isError: false 
      },
      actions: { execute: vi.fn() }
    });

    // Render with a limit of 2
    customRender(
      <SavedAnalyses 
        limit={2}
        onViewAnalysis={vi.fn()} 
        onNewAnalysis={vi.fn()} 
      />
    );

    // Should only show the first two analyses
    expect(screen.getByText('Q2 Ocean Freight')).toBeInTheDocument();
    expect(screen.getByText('Air vs Ocean 2023')).toBeInTheDocument();
    expect(screen.queryByText('Analysis 3')).not.toBeInTheDocument();
  });

  it('calls onViewAnalysis when analysis is clicked', async () => {
    const user = userEvent.setup();
    const onViewAnalysis = vi.fn();

    // Mock useApi to return analysis data
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { 
        data: { data: mockAnalyses }, 
        isLoading: false, 
        isError: false 
      },
      actions: { execute: vi.fn() }
    });

    customRender(
      <SavedAnalyses 
        onViewAnalysis={onViewAnalysis} 
        onNewAnalysis={vi.fn()} 
      />
    );

    // Click on the first analysis
    const firstAnalysis = screen.getByText('Q2 Ocean Freight').closest('li');
    if (firstAnalysis) {
      await user.click(firstAnalysis);
      
      // Check if onViewAnalysis was called with the correct analysis
      expect(onViewAnalysis).toHaveBeenCalledWith(mockAnalyses[0]);
    }
  });

  it('calls onViewAnalysis when Enter key is pressed on an analysis', async () => {
    const onViewAnalysis = vi.fn();

    // Mock useApi to return analysis data
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { 
        data: { data: mockAnalyses }, 
        isLoading: false, 
        isError: false 
      },
      actions: { execute: vi.fn() }
    });

    customRender(
      <SavedAnalyses 
        onViewAnalysis={onViewAnalysis} 
        onNewAnalysis={vi.fn()} 
      />
    );

    // Find the first analysis and simulate keyDown
    const firstAnalysis = screen.getByText('Q2 Ocean Freight').closest('li');
    if (firstAnalysis) {
      fireEvent.keyDown(firstAnalysis, { key: 'Enter' });
      
      // Check if onViewAnalysis was called with the correct analysis
      expect(onViewAnalysis).toHaveBeenCalledWith(mockAnalyses[0]);
    }
  });

  it('calls onNewAnalysis when button is clicked', async () => {
    const user = userEvent.setup();
    const onNewAnalysis = vi.fn();

    // Mock useApi to return analysis data
    (useApi as unknown as vi.Mock).mockReturnValue({
      state: { 
        data: { data: mockAnalyses }, 
        isLoading: false, 
        isError: false 
      },
      actions: { execute: vi.fn() }
    });

    customRender(
      <SavedAnalyses 
        onViewAnalysis={vi.fn()} 
        onNewAnalysis={onNewAnalysis} 
      />
    );

    // Click on the "New Analysis" button
    const newAnalysisButton = screen.getByText('+ New Analysis');
    await user.click(newAnalysisButton);

    // Check if onNewAnalysis was called
    expect(onNewAnalysis).toHaveBeenCalled();
  });
});