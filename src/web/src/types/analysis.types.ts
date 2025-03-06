/**
 * analysis.types.ts
 * 
 * This file defines TypeScript interfaces and types for freight price movement analysis.
 * It provides type definitions for analysis requests, results, time periods, and related
 * data structures to ensure type safety throughout the analysis workflow.
 */

/**
 * Enumeration of time granularity options for analysis
 */
export enum TimeGranularity {
    DAILY = 'daily',
    WEEKLY = 'weekly',
    MONTHLY = 'monthly',
    CUSTOM = 'custom'
}

/**
 * Enumeration of analysis request status values
 */
export enum AnalysisStatus {
    PENDING = 'pending',
    RUNNING = 'running',
    COMPLETED = 'completed',
    FAILED = 'failed',
    CANCELLED = 'cancelled'
}

/**
 * Enumeration of trend directions for price movement analysis
 */
export enum TrendDirection {
    INCREASING = 'increasing',
    DECREASING = 'decreasing',
    STABLE = 'stable'
}

/**
 * Enumeration of supported output formats for analysis results
 */
export enum OutputFormat {
    JSON = 'json',
    CSV = 'csv',
    TEXT = 'text'
}

/**
 * Interface for time period definition used in analysis
 */
export interface TimePeriod {
    id: string;
    name: string;
    start_date: string; // ISO 8601 date format (YYYY-MM-DD)
    end_date: string; // ISO 8601 date format (YYYY-MM-DD)
    granularity: TimeGranularity;
    custom_interval: string | null; // Used when granularity is CUSTOM
    is_custom: boolean;
    created_by: string;
    created_at: string; // ISO 8601 datetime format
}

/**
 * Interface for creating a new time period
 */
export interface TimePeriodCreateParams {
    name: string;
    start_date: string; // ISO 8601 date format (YYYY-MM-DD)
    end_date: string; // ISO 8601 date format (YYYY-MM-DD)
    granularity: TimeGranularity;
    custom_interval: string | null; // Used when granularity is CUSTOM
}

/**
 * Interface for data filtering options in analysis
 */
export interface DataFilter {
    field: string;
    operator: string; // e.g., 'eq', 'gt', 'lt', 'contains', etc.
    value: any;
}

/**
 * Interface for analysis configuration options
 */
export interface AnalysisOptions {
    calculate_absolute_change: boolean;
    calculate_percentage_change: boolean;
    identify_trend_direction: boolean;
    compare_to_baseline: boolean;
    baseline_period_id: string | null; // ID of baseline period for comparison
    output_format: OutputFormat;
    include_visualization: boolean;
}

/**
 * Interface for creating a new analysis request
 */
export interface AnalysisRequestCreateParams {
    name: string;
    description: string;
    time_period_id: string;
    data_source_ids: string[]; // IDs of data sources to include
    filters: DataFilter[];
    options: AnalysisOptions;
}

/**
 * Interface for analysis request with complete information
 */
export interface AnalysisRequest {
    id: string;
    name: string;
    description: string;
    time_period_id: string;
    time_period: TimePeriod;
    data_source_ids: string[];
    filters: DataFilter[];
    options: AnalysisOptions;
    status: AnalysisStatus;
    created_by: string;
    created_at: string; // ISO 8601 datetime format
    updated_at: string; // ISO 8601 datetime format
    last_run_at: string | null; // ISO 8601 datetime format
}

/**
 * Interface for a single price data point in time series
 */
export interface PricePoint {
    timestamp: string; // ISO 8601 datetime format
    value: number;
}

/**
 * Interface for price change calculations
 */
export interface PriceChange {
    absolute_change: number;
    percentage_change: number;
    trend_direction: TrendDirection;
}

/**
 * Interface for aggregated price statistics
 */
export interface PriceAggregate {
    average: number;
    minimum: number;
    maximum: number;
}

/**
 * Interface for detailed results per time period
 */
export interface DetailedResult {
    period: string; // Formatted period label (e.g., "Jan 01-07")
    price: number; // Price for this period
    absolute_change: number | null; // Null for first period
    percentage_change: number | null; // Null for first period
    trend_direction: TrendDirection | null; // Null for first period
}

/**
 * Interface for complete analysis result with all data
 */
export interface AnalysisResult {
    id: string;
    analysis_id: string;
    time_period: TimePeriod;
    filters: DataFilter[];
    start_value: number;
    end_value: number;
    currency: string; // Currency code (e.g., "USD")
    price_change: PriceChange;
    aggregates: PriceAggregate;
    time_series: PricePoint[];
    detailed_results: DetailedResult[];
    baseline_comparison: PriceChange | null; // Only present if comparison was requested
    calculated_at: string; // ISO 8601 datetime format
}

/**
 * Interface for summarized analysis result for dashboard display
 */
export interface AnalysisResultSummary {
    id: string;
    analysis_id: string;
    analysis_name: string;
    time_period_name: string;
    start_date: string; // ISO 8601 date format
    end_date: string; // ISO 8601 date format
    percentage_change: number;
    trend_direction: TrendDirection;
    calculated_at: string; // ISO 8601 datetime format
}

/**
 * Interface for configuring analysis result export options
 */
export interface AnalysisExportOptions {
    format: OutputFormat;
    include_time_series: boolean;
    include_detailed_results: boolean;
    filename: string | null; // Optional custom filename
}