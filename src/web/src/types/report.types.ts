/**
 * report.types.ts
 * 
 * This file defines TypeScript interfaces and types for reports in the Freight Price Movement Agent.
 * It provides type definitions for reports, report templates, scheduled reports,
 * and related data structures to ensure type safety throughout the reporting workflow.
 */

import { AnalysisResult, OutputFormat, TimePeriod } from '../types/analysis.types';

/**
 * Enumeration of possible report status values
 */
export enum ReportStatus {
    DRAFT = 'draft',
    ACTIVE = 'active',
    ARCHIVED = 'archived'
}

/**
 * Enumeration of report types
 */
export enum ReportType {
    STANDARD = 'standard',
    CUSTOM = 'custom',
    TEMPLATE = 'template'
}

/**
 * Enumeration of scheduled report frequency options
 */
export enum ScheduleFrequency {
    DAILY = 'daily',
    WEEKLY = 'weekly',
    MONTHLY = 'monthly',
    QUARTERLY = 'quarterly'
}

/**
 * Enumeration of report delivery methods
 */
export enum DeliveryMethod {
    EMAIL = 'email',
    DOWNLOAD = 'download',
    API = 'api'
}

/**
 * Enumeration of report run status values
 */
export enum ReportRunStatus {
    PENDING = 'pending',
    RUNNING = 'running',
    COMPLETED = 'completed',
    FAILED = 'failed'
}

/**
 * Interface for report data structure
 */
export interface Report {
    id: string;
    name: string;
    description: string;
    type: ReportType;
    status: ReportStatus;
    analysis_id: string;
    analysis_result: AnalysisResult | null;
    output_format: OutputFormat;
    include_visualization: boolean;
    created_by: string;
    created_at: string;
    updated_at: string;
    last_run_at: string | null;
}

/**
 * Interface for creating a new report
 */
export interface ReportCreateParams {
    name: string;
    description: string;
    type: ReportType;
    analysis_id: string;
    output_format: OutputFormat;
    include_visualization: boolean;
}

/**
 * Interface for updating an existing report
 */
export interface ReportUpdateParams {
    name: string;
    description: string;
    status: ReportStatus;
    output_format: OutputFormat;
    include_visualization: boolean;
}

/**
 * Interface for summarized report information for dashboard display
 */
export interface ReportSummary {
    id: string;
    name: string;
    status: ReportStatus;
    created_at: string;
    last_run_at: string | null;
}

/**
 * Interface for report template data structure
 */
export interface ReportTemplate {
    id: string;
    name: string;
    description: string;
    configuration: Record<string, any>;
    output_format: OutputFormat;
    include_visualization: boolean;
    created_by: string;
    created_at: string;
    updated_at: string;
}

/**
 * Interface for creating a new report template
 */
export interface ReportTemplateCreateParams {
    name: string;
    description: string;
    configuration: Record<string, any>;
    output_format: OutputFormat;
    include_visualization: boolean;
}

/**
 * Interface for scheduled report data structure
 */
export interface ScheduledReport {
    id: string;
    report_id: string;
    name: string;
    description: string;
    frequency: ScheduleFrequency;
    day_of_week: number | null;
    day_of_month: number | null;
    hour: number;
    minute: number;
    timezone: string;
    delivery_method: DeliveryMethod;
    delivery_config: Record<string, any>;
    is_active: boolean;
    created_by: string;
    created_at: string;
    updated_at: string;
    last_run_at: string | null;
    next_run_at: string | null;
}

/**
 * Interface for creating a new scheduled report
 */
export interface ScheduledReportCreateParams {
    report_id: string;
    name: string;
    description: string;
    frequency: ScheduleFrequency;
    day_of_week: number | null;
    day_of_month: number | null;
    hour: number;
    minute: number;
    timezone: string;
    delivery_method: DeliveryMethod;
    delivery_config: Record<string, any>;
    is_active: boolean;
}

/**
 * Interface for updating an existing scheduled report
 */
export interface ScheduledReportUpdateParams {
    name: string;
    description: string;
    frequency: ScheduleFrequency;
    day_of_week: number | null;
    day_of_month: number | null;
    hour: number;
    minute: number;
    timezone: string;
    delivery_method: DeliveryMethod;
    delivery_config: Record<string, any>;
    is_active: boolean;
}

/**
 * Interface for report execution history
 */
export interface ReportRunHistory {
    id: string;
    report_id: string;
    scheduled_report_id: string | null;
    status: ReportRunStatus;
    started_at: string;
    completed_at: string | null;
    duration_ms: number | null;
    error_message: string | null;
    result_url: string | null;
    triggered_by: string;
}

/**
 * Interface for email delivery configuration
 */
export interface EmailDeliveryConfig {
    recipients: string[];
    cc: string[] | null;
    bcc: string[] | null;
    subject_template: string | null;
    body_template: string | null;
    include_attachment: boolean;
}

/**
 * Interface for API webhook delivery configuration
 */
export interface ApiDeliveryConfig {
    endpoint_url: string;
    method: string;
    headers: Record<string, string> | null;
    authentication: Record<string, any> | null;
}