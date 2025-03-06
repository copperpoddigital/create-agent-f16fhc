/**
 * Data Source Types
 * 
 * This file defines TypeScript interfaces, types, and enums for data sources in the
 * Freight Price Movement Agent web application. It provides type definitions for various
 * data source types (CSV, Database, API, TMS, ERP), their creation parameters, status tracking,
 * and related operations.
 */

/**
 * Enumeration of supported data source types
 */
export enum DataSourceType {
  CSV = 'csv',
  DATABASE = 'database',
  API = 'api',
  TMS = 'tms',
  ERP = 'erp',
}

/**
 * Enumeration of possible data source statuses
 */
export enum DataSourceStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  WARNING = 'warning',
  ERROR = 'error',
}

/**
 * Enumeration of supported database types for database data sources
 */
export enum DatabaseType {
  POSTGRESQL = 'postgresql',
  MYSQL = 'mysql',
  SQLSERVER = 'sqlserver',
  ORACLE = 'oracle',
}

/**
 * Enumeration of supported TMS types for TMS data sources
 */
export enum TMSType {
  SAP_TM = 'sap_tm',
  ORACLE_TMS = 'oracle_tms',
  JDA_TMS = 'jda_tms',
  CUSTOM = 'custom',
}

/**
 * Enumeration of supported ERP types for ERP data sources
 */
export enum ERPType {
  SAP_ERP = 'sap_erp',
  ORACLE_ERP = 'oracle_erp',
  MICROSOFT_DYNAMICS = 'microsoft_dynamics',
  CUSTOM = 'custom',
}

/**
 * Enumeration of authentication types for API data sources
 */
export enum AuthType {
  NONE = 'none',
  BASIC = 'basic',
  API_KEY = 'api_key',
  OAUTH2 = 'oauth2',
}

/**
 * Interface for mapping source fields to freight data fields
 */
export interface FieldMapping {
  freight_charge: string;
  currency: string;
  origin: string;
  destination: string;
  date_time: string;
  carrier: string | null;
  mode: string | null;
  service_level: string | null;
}

/**
 * Base interface with common properties for all data source types
 */
export interface BaseDataSource {
  id: string;
  name: string;
  description: string | null;
  source_type: DataSourceType;
  status: DataSourceStatus;
  created_at: string;
  updated_at: string;
  last_sync: string | null;
  field_mapping: FieldMapping;
}

/**
 * Interface for CSV file data sources
 */
export interface CSVDataSource extends BaseDataSource {
  source_type: DataSourceType.CSV;
  file_path: string;
  file_name: string;
  delimiter: string;
  has_header: boolean;
  date_format: string;
}

/**
 * Interface for database data sources
 */
export interface DatabaseDataSource extends BaseDataSource {
  source_type: DataSourceType.DATABASE;
  database_type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  query: string;
}

/**
 * Interface for API data sources
 */
export interface APIDataSource extends BaseDataSource {
  source_type: DataSourceType.API;
  url: string;
  method: string;
  headers: Record<string, string>;
  body: string | null;
  auth_type: AuthType;
  auth_config: Record<string, string>;
  response_path: string;
}

/**
 * Interface for TMS data sources
 */
export interface TMSDataSource extends BaseDataSource {
  source_type: DataSourceType.TMS;
  tms_type: TMSType;
  connection_url: string;
  username: string;
  api_key: string | null;
  custom_parameters: Record<string, string>;
}

/**
 * Interface for ERP data sources
 */
export interface ERPDataSource extends BaseDataSource {
  source_type: DataSourceType.ERP;
  erp_type: ERPType;
  connection_url: string;
  username: string;
  api_key: string | null;
  custom_parameters: Record<string, string>;
}

/**
 * Union type of all data source types
 */
export type DataSource = (CSVDataSource | DatabaseDataSource | APIDataSource | TMSDataSource | ERPDataSource) & BaseDataSource;

/**
 * Interface for creating CSV data sources
 */
export interface CSVDataSourceCreate {
  name: string;
  description: string | null;
  file: File;
  delimiter: string;
  has_header: boolean;
  date_format: string;
  field_mapping: FieldMapping;
}

/**
 * Interface for creating database data sources
 */
export interface DatabaseDataSourceCreate {
  name: string;
  description: string | null;
  database_type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  query: string;
  field_mapping: FieldMapping;
}

/**
 * Interface for creating API data sources
 */
export interface APIDataSourceCreate {
  name: string;
  description: string | null;
  url: string;
  method: string;
  headers: Record<string, string>;
  body: string | null;
  auth_type: AuthType;
  auth_config: Record<string, string>;
  response_path: string;
  field_mapping: FieldMapping;
}

/**
 * Interface for creating TMS data sources
 */
export interface TMSDataSourceCreate {
  name: string;
  description: string | null;
  tms_type: TMSType;
  connection_url: string;
  username: string;
  password: string;
  api_key: string | null;
  custom_parameters: Record<string, string>;
  field_mapping: FieldMapping;
}

/**
 * Interface for creating ERP data sources
 */
export interface ERPDataSourceCreate {
  name: string;
  description: string | null;
  erp_type: ERPType;
  connection_url: string;
  username: string;
  password: string;
  api_key: string | null;
  custom_parameters: Record<string, string>;
  field_mapping: FieldMapping;
}

/**
 * Interface for test connection requests
 */
export interface TestConnectionRequest {
  source_type: DataSourceType;
  connection_params: Record<string, any>;
}

/**
 * Interface for data source operation logs
 */
export interface DataSourceLog {
  id: string;
  data_source_id: string;
  operation: string;
  status: string;
  message: string;
  details: Record<string, any> | null;
  records_processed: number | null;
  records_succeeded: number | null;
  records_failed: number | null;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
}