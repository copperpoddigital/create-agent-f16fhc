"""
Data source schema definitions for the Freight Price Movement Agent.

This module provides Pydantic schemas for data validation, serialization, and API
documentation for various types of data sources including CSV, Database, API, TMS,
and ERP systems.
"""

from typing import Dict, List, Optional, Any
import datetime
import uuid

from ../../core/schemas import BaseModel
from ../../schemas/common import IDModel, TimestampModel, AuditableModel
from ../../models/enums import DataSourceType, DataSourceStatus


class DataSourceBase(BaseModel):
    """Base schema for all data source types with common fields."""
    name: str
    description: Optional[str] = None
    source_type: DataSourceType
    status: Optional[DataSourceStatus] = DataSourceStatus.INACTIVE

    class Config:
        orm_mode = True
        use_enum_values = True


class DataSourceCreate(DataSourceBase):
    """Schema for creating a generic data source."""
    pass


class DataSourceUpdate(BaseModel):
    """Schema for updating a generic data source."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DataSourceStatus] = None

    class Config:
        orm_mode = True
        use_enum_values = True


class DataSourceResponse(DataSourceBase, IDModel, TimestampModel):
    """Schema for data source responses."""
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None
    last_run_at: Optional[datetime.datetime] = None
    last_run_by: Optional[str] = None

    class Config:
        orm_mode = True
        use_enum_values = True


class CSVDataSourceBase(DataSourceBase):
    """Base schema for CSV data sources."""
    file_path: str
    delimiter: Optional[str] = ","
    encoding: Optional[str] = "utf-8"
    field_mapping: Dict[str, str]
    has_header: Optional[bool] = True
    date_format: Optional[str] = "%Y-%m-%d"


class CSVDataSourceCreate(CSVDataSourceBase):
    """Schema for creating a CSV data source."""
    source_type: DataSourceType = DataSourceType.CSV


class CSVDataSourceUpdate(DataSourceUpdate):
    """Schema for updating a CSV data source."""
    file_path: Optional[str] = None
    delimiter: Optional[str] = None
    encoding: Optional[str] = None
    field_mapping: Optional[Dict[str, str]] = None
    has_header: Optional[bool] = None
    date_format: Optional[str] = None


class CSVDataSourceResponse(DataSourceResponse):
    """Schema for CSV data source responses."""
    file_path: str
    delimiter: str
    encoding: str
    field_mapping: Dict[str, str]
    has_header: bool
    date_format: str


class DatabaseDataSourceBase(DataSourceBase):
    """Base schema for database data sources."""
    connection_string: str
    query: str
    field_mapping: Dict[str, str]
    username: str
    password: Optional[str] = None


class DatabaseDataSourceCreate(DatabaseDataSourceBase):
    """Schema for creating a database data source."""
    source_type: DataSourceType = DataSourceType.DATABASE


class DatabaseDataSourceUpdate(DataSourceUpdate):
    """Schema for updating a database data source."""
    connection_string: Optional[str] = None
    query: Optional[str] = None
    field_mapping: Optional[Dict[str, str]] = None
    username: Optional[str] = None
    password: Optional[str] = None


class DatabaseDataSourceResponse(DataSourceResponse):
    """Schema for database data source responses."""
    connection_string: str
    query: str
    field_mapping: Dict[str, str]
    username: str  # Intentionally exclude password for security


class APIDataSourceBase(DataSourceBase):
    """Base schema for API data sources."""
    endpoint_url: str
    method: Optional[str] = "GET"
    headers: Optional[Dict[str, str]] = None
    parameters: Optional[Dict[str, Any]] = None
    auth_config: Optional[Dict[str, Any]] = None
    field_mapping: Dict[str, str]
    timeout: Optional[int] = 30


class APIDataSourceCreate(APIDataSourceBase):
    """Schema for creating an API data source."""
    source_type: DataSourceType = DataSourceType.API


class APIDataSourceUpdate(DataSourceUpdate):
    """Schema for updating an API data source."""
    endpoint_url: Optional[str] = None
    method: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    parameters: Optional[Dict[str, Any]] = None
    auth_config: Optional[Dict[str, Any]] = None
    field_mapping: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None


class APIDataSourceResponse(DataSourceResponse):
    """Schema for API data source responses."""
    endpoint_url: str
    method: str
    headers: Dict[str, str]
    parameters: Dict[str, Any]
    auth_config: Dict[str, Any]
    field_mapping: Dict[str, str]
    timeout: int


class TMSDataSourceBase(DataSourceBase):
    """Base schema for Transportation Management System data sources."""
    tms_type: str
    connection_string: str
    auth_config: Optional[Dict[str, Any]] = None
    field_mapping: Dict[str, str]
    extraction_config: Optional[Dict[str, Any]] = None


class TMSDataSourceCreate(TMSDataSourceBase):
    """Schema for creating a TMS data source."""
    source_type: DataSourceType = DataSourceType.TMS


class TMSDataSourceUpdate(DataSourceUpdate):
    """Schema for updating a TMS data source."""
    tms_type: Optional[str] = None
    connection_string: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    field_mapping: Optional[Dict[str, str]] = None
    extraction_config: Optional[Dict[str, Any]] = None


class TMSDataSourceResponse(DataSourceResponse):
    """Schema for TMS data source responses."""
    tms_type: str
    connection_string: str
    auth_config: Dict[str, Any]
    field_mapping: Dict[str, str]
    extraction_config: Dict[str, Any]


class ERPDataSourceBase(DataSourceBase):
    """Base schema for Enterprise Resource Planning system data sources."""
    erp_type: str
    connection_string: str
    auth_config: Optional[Dict[str, Any]] = None
    field_mapping: Dict[str, str]
    extraction_config: Optional[Dict[str, Any]] = None


class ERPDataSourceCreate(ERPDataSourceBase):
    """Schema for creating an ERP data source."""
    source_type: DataSourceType = DataSourceType.ERP


class ERPDataSourceUpdate(DataSourceUpdate):
    """Schema for updating an ERP data source."""
    erp_type: Optional[str] = None
    connection_string: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    field_mapping: Optional[Dict[str, str]] = None
    extraction_config: Optional[Dict[str, Any]] = None


class ERPDataSourceResponse(DataSourceResponse):
    """Schema for ERP data source responses."""
    erp_type: str
    connection_string: str
    auth_config: Dict[str, Any]
    field_mapping: Dict[str, str]
    extraction_config: Dict[str, Any]


class DataSourceListResponse(BaseModel):
    """Schema for paginated list of data sources."""
    items: List[DataSourceResponse]
    total: int
    page: int
    size: int


class DataSourceLogResponse(BaseModel):
    """Schema for data source log entries."""
    id: uuid.UUID
    data_source_id: uuid.UUID
    operation: str
    status: str
    message: Optional[str] = None
    records_processed: int
    records_failed: int
    details: Optional[Dict[str, Any]] = None
    performed_by: Optional[uuid.UUID] = None
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class TestConnectionRequest(BaseModel):
    """Schema for test connection requests."""
    data_source_id: uuid.UUID


class TestConnectionResponse(BaseModel):
    """Schema for test connection responses."""
    success: bool
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None