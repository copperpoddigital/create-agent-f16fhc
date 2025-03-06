"""
Standardized API response schemas for the Freight Price Movement Agent.

This module defines Pydantic models for consistent API response formats,
including success and error responses, single items, lists, and paginated results.
"""

from typing import Any, Dict, List, Optional
import datetime
import uuid
import decimal

from ..core.schemas import ResponseModel, PaginatedResponse, ErrorResponse, BaseModel
from .common import CurrencyAmount, PercentageChange
from ..models.enums import TrendDirection, OutputFormat


def create_response(data: Any, message: Optional[str] = None) -> ResponseModel:
    """
    Creates a standard API response with the given data and message.
    
    Args:
        data: The data to include in the response
        message: Optional message for the response
        
    Returns:
        ResponseModel: Standardized API response
    """
    response = ResponseModel(data=data, success=True)
    if message:
        response.message = message
    return response


def create_error_response(message: str, errors: Optional[dict] = None) -> ErrorResponse:
    """
    Creates a standard API error response with the given message and errors.
    
    Args:
        message: Error message
        errors: Optional dictionary of detailed errors
        
    Returns:
        ErrorResponse: Standardized API error response
    """
    response = ErrorResponse(message=message, success=False)
    if errors:
        response.errors = errors
    return response


def create_paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: Optional[str] = None
) -> PaginatedResponse:
    """
    Creates a standard paginated API response with the given data and pagination information.
    
    Args:
        data: List of items for the current page
        total: Total number of items across all pages
        page: Current page number
        page_size: Number of items per page
        message: Optional message for the response
        
    Returns:
        PaginatedResponse: Standardized paginated API response
    """
    response = PaginatedResponse(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        success=True
    )
    if message:
        response.message = message
    return response


class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    id: uuid.UUID
    username: str
    email: str
    roles: List[str]
    is_active: bool
    last_login: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    
    class Config:
        orm_mode = True


class UserListResponse(PaginatedResponse):
    """Schema for paginated list of users in API responses."""
    data: List[UserResponse]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class DataSourceResponse(BaseModel):
    """Schema for data source information in API responses."""
    id: uuid.UUID
    name: str
    type: str
    description: Optional[str] = None
    status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    created_by: Optional[uuid.UUID] = None
    last_sync_at: Optional[datetime.datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        orm_mode = True


class DataSourceDetailResponse(DataSourceResponse):
    """Schema for detailed data source information in API responses."""
    field_mapping: Dict[str, str]
    connection_details: Dict[str, Any]
    
    class Config:
        orm_mode = True


class DataSourceListResponse(PaginatedResponse):
    """Schema for paginated list of data sources in API responses."""
    data: List[DataSourceResponse]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class TimePeriodResponse(BaseModel):
    """Schema for time period information in API responses."""
    id: uuid.UUID
    name: str
    start_date: datetime.date
    end_date: datetime.date
    granularity: str
    is_custom: bool
    custom_interval: Optional[str] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    created_by: Optional[uuid.UUID] = None
    
    class Config:
        orm_mode = True


class TimePeriodListResponse(PaginatedResponse):
    """Schema for paginated list of time periods in API responses."""
    data: List[TimePeriodResponse]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class PriceMovementResponse(BaseModel):
    """Schema for price movement analysis results in API responses."""
    analysis_id: uuid.UUID
    time_period_id: Optional[uuid.UUID] = None
    start_date: datetime.date
    end_date: datetime.date
    granularity: str
    absolute_change: Optional[decimal.Decimal] = None
    percentage_change: Optional[decimal.Decimal] = None
    trend_direction: Optional[TrendDirection] = None
    absolute_change_formatted: Optional[CurrencyAmount] = None
    percentage_change_formatted: Optional[PercentageChange] = None
    aggregates: Optional[Dict[str, Any]] = None
    time_series: Optional[List[Dict[str, Any]]] = None
    visualization_data: Optional[Dict[str, Any]] = None
    output_format: OutputFormat
    is_cached: bool
    calculated_at: datetime.datetime
    
    class Config:
        orm_mode = True


class AnalysisRequestResponse(BaseModel):
    """Schema for analysis request information in API responses."""
    id: uuid.UUID
    name: str
    time_period_id: Optional[uuid.UUID] = None
    time_period: Optional[TimePeriodResponse] = None
    data_source_ids: Optional[List[uuid.UUID]] = None
    filters: Optional[Dict[str, Any]] = None
    calculate_absolute_change: bool
    calculate_percentage_change: bool
    identify_trend_direction: bool
    compare_to_baseline: bool
    baseline_period_id: Optional[uuid.UUID] = None
    output_format: OutputFormat
    include_visualization: bool
    status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    created_by: Optional[uuid.UUID] = None
    result_id: Optional[uuid.UUID] = None
    
    class Config:
        orm_mode = True


class AnalysisRequestListResponse(PaginatedResponse):
    """Schema for paginated list of analysis requests in API responses."""
    data: List[AnalysisRequestResponse]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class SavedAnalysisResponse(BaseModel):
    """Schema for saved analysis information in API responses."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    analysis_request_id: uuid.UUID
    analysis_request: Optional[AnalysisRequestResponse] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    created_by: Optional[uuid.UUID] = None
    last_run_at: Optional[datetime.datetime] = None
    
    class Config:
        orm_mode = True


class SavedAnalysisListResponse(PaginatedResponse):
    """Schema for paginated list of saved analyses in API responses."""
    data: List[SavedAnalysisResponse]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class AnalysisScheduleResponse(BaseModel):
    """Schema for analysis schedule information in API responses."""
    id: uuid.UUID
    name: str
    analysis_id: uuid.UUID
    analysis: Optional[AnalysisRequestResponse] = None
    schedule_frequency: str
    next_run_time: Optional[datetime.datetime] = None
    active: bool
    recipients: Optional[List[str]] = None
    output_format: OutputFormat
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    created_by: Optional[uuid.UUID] = None
    last_run_at: Optional[datetime.datetime] = None
    last_run_status: Optional[str] = None
    
    class Config:
        orm_mode = True


class AnalysisScheduleListResponse(PaginatedResponse):
    """Schema for paginated list of analysis schedules in API responses."""
    data: List[AnalysisScheduleResponse]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema for report information in API responses."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    analysis_id: uuid.UUID
    analysis: Optional[AnalysisRequestResponse] = None
    format: OutputFormat
    include_visualization: bool
    scheduled: bool
    schedule_frequency: Optional[str] = None
    recipients: Optional[List[str]] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    created_by: Optional[uuid.UUID] = None
    last_generated_at: Optional[datetime.datetime] = None
    file_url: Optional[str] = None
    
    class Config:
        orm_mode = True


class ReportListResponse(PaginatedResponse):
    """Schema for paginated list of reports in API responses."""
    data: List[ReportResponse]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str = "ok"
    version: str
    components: Dict[str, Any]
    timestamp: datetime.datetime


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    success: bool = False
    message: str = "Validation error"
    errors: Dict[str, List[str]]


class SuccessResponse(BaseModel):
    """Schema for simple success responses."""
    success: bool = True
    message: str