"""
Defines Pydantic schema models for validating and processing API request data in the Freight Price Movement Agent.
This module provides standardized request schemas for authentication, data sources, analysis, and reporting operations.
"""

import typing
import datetime
import uuid
import decimal
import re
from pydantic import validator

from ..core.schemas import BaseModel
from .common import DateRange, DateTimeRange, OutputFormatParams, PaginationParams, TimeRangeParams
from ..models.enums import TransportMode, CarrierType, DataSourceType, GranularityType, OutputFormat


class UserCreateRequest(BaseModel):
    """Schema for user creation request"""
    username: str
    email: str
    password: str
    roles: typing.Optional[typing.List[str]] = ["VIEWER"]
    
    @validator('password')
    def validate_password(cls, password: str) -> str:
        """Validates password complexity requirements"""
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[a-z]', password):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[A-Z]', password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', password):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^a-zA-Z0-9]', password):
            raise ValueError('Password must contain at least one special character')
        return password


class UserUpdateRequest(BaseModel):
    """Schema for user update request"""
    email: typing.Optional[str] = None
    roles: typing.Optional[typing.List[str]] = None
    is_active: typing.Optional[bool] = None


class DataSourceCreateRequest(BaseModel):
    """Schema for generic data source creation request"""
    name: str
    type: DataSourceType
    description: typing.Optional[str] = None


class CSVDataSourceCreateRequest(BaseModel):
    """Schema for CSV data source creation request"""
    name: str
    description: typing.Optional[str] = None
    file_path: str
    delimiter: typing.Optional[str] = ","
    encoding: typing.Optional[str] = "utf-8"
    has_header: typing.Optional[bool] = True
    field_mapping: typing.Dict[str, str]
    date_format: typing.Optional[str] = None


class DatabaseDataSourceCreateRequest(BaseModel):
    """Schema for database data source creation request"""
    name: str
    description: typing.Optional[str] = None
    connection_string: str
    query: str
    username: typing.Optional[str] = None
    password: typing.Optional[str] = None
    field_mapping: typing.Dict[str, str]


class APIDataSourceCreateRequest(BaseModel):
    """Schema for API data source creation request"""
    name: str
    description: typing.Optional[str] = None
    url: str
    method: str
    headers: typing.Optional[dict] = None
    params: typing.Optional[dict] = None
    body: typing.Optional[dict] = None
    auth_type: typing.Optional[str] = None
    auth_username: typing.Optional[str] = None
    auth_password: typing.Optional[str] = None
    auth_token: typing.Optional[str] = None
    field_mapping: typing.Dict[str, str]
    response_path: typing.Optional[str] = None


class TMSDataSourceCreateRequest(BaseModel):
    """Schema for TMS data source creation request"""
    name: str
    description: typing.Optional[str] = None
    tms_type: str
    connection_url: str
    username: typing.Optional[str] = None
    password: typing.Optional[str] = None
    api_key: typing.Optional[str] = None
    field_mapping: typing.Dict[str, str]
    additional_settings: typing.Optional[dict] = None


class ERPDataSourceCreateRequest(BaseModel):
    """Schema for ERP data source creation request"""
    name: str
    description: typing.Optional[str] = None
    erp_type: str
    connection_url: str
    username: typing.Optional[str] = None
    password: typing.Optional[str] = None
    api_key: typing.Optional[str] = None
    field_mapping: typing.Dict[str, str]
    additional_settings: typing.Optional[dict] = None


class DataSourceUpdateRequest(BaseModel):
    """Schema for generic data source update request"""
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None


class TestConnectionRequest(BaseModel):
    """Schema for testing data source connection"""
    data_source_id: typing.Optional[uuid.UUID] = None
    type: typing.Optional[DataSourceType] = None
    connection_params: typing.Optional[dict] = None
    
    @validator('connection_params')
    def validate_request(cls, v, values) -> dict:
        """Validates that either data_source_id or both type and connection_params are provided"""
        if not values.get('data_source_id') and (not values.get('type') or not v):
            raise ValueError('Either data_source_id or both type and connection_params must be provided')
        return v


class TimePeriodCreateRequest(BaseModel):
    """Schema for time period creation request"""
    name: str
    start_date: datetime.date
    end_date: datetime.date
    granularity: GranularityType
    is_custom: typing.Optional[bool] = False
    custom_interval: typing.Optional[str] = None
    
    @validator('end_date')
    def validate_dates(cls, v, values) -> datetime.date:
        """Validates that the start date is before or equal to the end date"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v
    
    @validator('custom_interval')
    def validate_custom_interval(cls, v, values) -> typing.Optional[str]:
        """Validates that custom_interval is provided when is_custom is True"""
        if values.get('is_custom') and not v:
            raise ValueError('custom_interval must be provided when is_custom is True')
        return v


class TimePeriodUpdateRequest(BaseModel):
    """Schema for time period update request"""
    name: typing.Optional[str] = None
    start_date: typing.Optional[datetime.date] = None
    end_date: typing.Optional[datetime.date] = None
    granularity: typing.Optional[GranularityType] = None
    is_custom: typing.Optional[bool] = None
    custom_interval: typing.Optional[str] = None
    
    @validator('end_date')
    def validate_dates(cls, v, values) -> typing.Optional[datetime.date]:
        """Validates that the start date is before or equal to the end date if both are provided"""
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v


class AnalysisRequestCreateRequest(BaseModel):
    """Schema for analysis request creation"""
    name: str
    time_period_id: typing.Optional[uuid.UUID] = None
    time_period: typing.Optional[TimePeriodCreateRequest] = None
    data_source_ids: typing.Optional[typing.List[uuid.UUID]] = None
    filters: typing.Optional[typing.Dict[str, typing.Any]] = None
    calculate_absolute_change: typing.Optional[bool] = True
    calculate_percentage_change: typing.Optional[bool] = True
    identify_trend_direction: typing.Optional[bool] = True
    compare_to_baseline: typing.Optional[bool] = False
    baseline_period_id: typing.Optional[uuid.UUID] = None
    output_format: typing.Optional[OutputFormat] = OutputFormat.JSON
    include_visualization: typing.Optional[bool] = False
    
    @validator('time_period')
    def validate_time_period(cls, v, values) -> typing.Optional[TimePeriodCreateRequest]:
        """Validates that either time_period_id or time_period is provided"""
        if not values.get('time_period_id') and not v:
            raise ValueError('Either time_period_id or time_period must be provided')
        return v
    
    @validator('baseline_period_id')
    def validate_baseline(cls, v, values) -> typing.Optional[uuid.UUID]:
        """Validates that baseline_period_id is provided when compare_to_baseline is True"""
        if values.get('compare_to_baseline') and not v:
            raise ValueError('baseline_period_id must be provided when compare_to_baseline is True')
        return v


class AnalysisRequestUpdateRequest(BaseModel):
    """Schema for analysis request update"""
    name: typing.Optional[str] = None
    time_period_id: typing.Optional[uuid.UUID] = None
    data_source_ids: typing.Optional[typing.List[uuid.UUID]] = None
    filters: typing.Optional[typing.Dict[str, typing.Any]] = None
    calculate_absolute_change: typing.Optional[bool] = None
    calculate_percentage_change: typing.Optional[bool] = None
    identify_trend_direction: typing.Optional[bool] = None
    compare_to_baseline: typing.Optional[bool] = None
    baseline_period_id: typing.Optional[uuid.UUID] = None
    output_format: typing.Optional[OutputFormat] = None
    include_visualization: typing.Optional[bool] = None
    
    @validator('baseline_period_id')
    def validate_baseline(cls, v, values) -> typing.Optional[uuid.UUID]:
        """Validates that baseline_period_id is provided when compare_to_baseline is True"""
        if 'compare_to_baseline' in values and values['compare_to_baseline'] and not v:
            raise ValueError('baseline_period_id must be provided when compare_to_baseline is True')
        return v


class SavedAnalysisCreateRequest(BaseModel):
    """Schema for saved analysis creation"""
    name: str
    description: typing.Optional[str] = None
    analysis_request_id: uuid.UUID


class SavedAnalysisUpdateRequest(BaseModel):
    """Schema for saved analysis update"""
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None


class AnalysisScheduleCreateRequest(BaseModel):
    """Schema for analysis schedule creation"""
    name: str
    analysis_id: uuid.UUID
    schedule_frequency: str
    next_run_time: typing.Optional[datetime.datetime] = None
    active: typing.Optional[bool] = True
    recipients: typing.Optional[typing.List[str]] = None
    output_format: typing.Optional[OutputFormat] = OutputFormat.JSON
    
    @validator('schedule_frequency')
    def validate_schedule_frequency(cls, schedule_frequency: str) -> str:
        """Validates that schedule_frequency is in a valid cron format or predefined schedule"""
        # Simple validation - we would implement more robust cron validation in a real system
        valid_predefined = ["hourly", "daily", "weekly", "monthly"]
        if schedule_frequency in valid_predefined:
            return schedule_frequency
        
        # Basic cron validation (very simplified)
        if not re.match(r'^[0-9*,-/\s]+$', schedule_frequency):
            raise ValueError('Invalid cron expression or predefined schedule')
        
        return schedule_frequency


class AnalysisScheduleUpdateRequest(BaseModel):
    """Schema for analysis schedule update"""
    name: typing.Optional[str] = None
    schedule_frequency: typing.Optional[str] = None
    next_run_time: typing.Optional[datetime.datetime] = None
    active: typing.Optional[bool] = None
    recipients: typing.Optional[typing.List[str]] = None
    output_format: typing.Optional[OutputFormat] = None
    
    @validator('schedule_frequency')
    def validate_schedule_frequency(cls, schedule_frequency: typing.Optional[str]) -> typing.Optional[str]:
        """Validates that schedule_frequency is in a valid cron format or predefined schedule if provided"""
        if schedule_frequency is None:
            return None
        
        # Simple validation - we would implement more robust cron validation in a real system
        valid_predefined = ["hourly", "daily", "weekly", "monthly"]
        if schedule_frequency in valid_predefined:
            return schedule_frequency
        
        # Basic cron validation (very simplified)
        if not re.match(r'^[0-9*,-/\s]+$', schedule_frequency):
            raise ValueError('Invalid cron expression or predefined schedule')
        
        return schedule_frequency


class ReportCreateRequest(BaseModel):
    """Schema for report creation"""
    name: str
    description: typing.Optional[str] = None
    analysis_id: uuid.UUID
    format: typing.Optional[OutputFormat] = OutputFormat.JSON
    include_visualization: typing.Optional[bool] = False
    scheduled: typing.Optional[bool] = False
    schedule_frequency: typing.Optional[str] = None
    recipients: typing.Optional[typing.List[str]] = None
    
    @validator('schedule_frequency')
    def validate_schedule(cls, v, values) -> typing.Optional[str]:
        """Validates that schedule_frequency is provided when scheduled is True"""
        if values.get('scheduled') and not v:
            raise ValueError('schedule_frequency must be provided when scheduled is True')
        return v


class ReportUpdateRequest(BaseModel):
    """Schema for report update"""
    name: typing.Optional[str] = None
    description: typing.Optional[str] = None
    format: typing.Optional[OutputFormat] = None
    include_visualization: typing.Optional[bool] = None
    scheduled: typing.Optional[bool] = None
    schedule_frequency: typing.Optional[str] = None
    recipients: typing.Optional[typing.List[str]] = None


class ReportShareCreateRequest(BaseModel):
    """Schema for report share creation"""
    report_id: uuid.UUID
    user_id: uuid.UUID
    can_view: typing.Optional[bool] = True
    can_edit: typing.Optional[bool] = False
    can_delete: typing.Optional[bool] = False
    can_share: typing.Optional[bool] = False


class ReportShareUpdateRequest(BaseModel):
    """Schema for report share update"""
    can_view: typing.Optional[bool] = None
    can_edit: typing.Optional[bool] = None
    can_delete: typing.Optional[bool] = None
    can_share: typing.Optional[bool] = None


class FilterParams(BaseModel):
    """Base schema for filter parameters"""
    search: typing.Optional[str] = None
    created_after: typing.Optional[datetime.datetime] = None
    created_before: typing.Optional[datetime.datetime] = None
    created_by: typing.Optional[uuid.UUID] = None


class DataSourceFilterParams(FilterParams):
    """Schema for data source filter parameters"""
    type: typing.Optional[DataSourceType] = None
    active_only: typing.Optional[bool] = True


class AnalysisFilterParams(FilterParams):
    """Schema for analysis filter parameters"""
    time_period_id: typing.Optional[uuid.UUID] = None
    data_source_id: typing.Optional[uuid.UUID] = None


class ReportFilterParams(FilterParams):
    """Schema for report filter parameters"""
    analysis_id: typing.Optional[uuid.UUID] = None
    scheduled_only: typing.Optional[bool] = False