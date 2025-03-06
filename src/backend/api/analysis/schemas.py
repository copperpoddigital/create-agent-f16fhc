"""
Pydantic schema models for the analysis API of the Freight Price Movement Agent.

This module defines schemas for data validation, serialization, and API documentation
of analysis requests, time periods, and analysis results.
"""

from typing import Dict, List, Optional, Any
import datetime
import uuid
import decimal

from ...core.schemas import BaseModel
from ...schemas.common import (
    IDModel, 
    TimestampModel, 
    AuditableModel,
    DateRange, 
    CurrencyAmount, 
    PercentageChange,
    OutputFormatParams,
    AnalysisFilterParams,
    FreightDataFilterParams
)
from ...schemas.time_period import TimePeriod, TimePeriodCreate
from ...schemas.analysis_result import AnalysisResultBase, AnalysisResultDetail
from ...models.enums import (
    GranularityType, 
    TrendDirection, 
    AnalysisStatus,
    OutputFormat
)


class AnalysisRequestBase(BaseModel):
    """Base schema for analysis request data without ID or audit fields."""
    time_period_id: uuid.UUID
    parameters: Dict[str, Any]
    output_format: OutputFormat = OutputFormat.JSON
    include_visualization: bool = False
    result_id: Optional[uuid.UUID] = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    error_message: Optional[str] = None

    class Config:
        orm_mode = True


class AnalysisRequestCreate(AnalysisRequestBase):
    """Schema for creating a new analysis request."""
    user_id: Optional[uuid.UUID] = None
    filters: Optional[List[FreightDataFilterParams]] = None


class AnalysisRequestUpdate(BaseModel):
    """Schema for updating an existing analysis request."""
    time_period_id: Optional[uuid.UUID] = None
    parameters: Optional[Dict[str, Any]] = None
    output_format: Optional[OutputFormat] = None
    include_visualization: Optional[bool] = None
    result_id: Optional[uuid.UUID] = None
    status: Optional[AnalysisStatus] = None
    error_message: Optional[str] = None


class AnalysisRequest(AnalysisRequestBase, IDModel, TimestampModel, AuditableModel):
    """Complete schema for an analysis request with ID and audit fields."""
    pass


class AnalysisRequestResponse(BaseModel):
    """Schema for API responses containing an analysis request."""
    data: AnalysisRequest
    success: bool = True
    message: Optional[str] = None


class AnalysisListResponse(BaseModel):
    """Schema for API responses containing a list of analysis requests."""
    data: List[AnalysisRequest]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class SavedAnalysisBase(BaseModel):
    """Base schema for saved analysis configuration."""
    name: str
    description: Optional[str] = None
    time_period_id: Optional[uuid.UUID] = None
    parameters: Dict[str, Any]
    output_format: OutputFormat = OutputFormat.JSON
    include_visualization: bool = False
    last_run_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


class SavedAnalysisCreate(SavedAnalysisBase):
    """Schema for creating a new saved analysis."""
    user_id: uuid.UUID
    filters: Optional[List[FreightDataFilterParams]] = None


class SavedAnalysis(SavedAnalysisBase, IDModel, TimestampModel, AuditableModel):
    """Complete schema for a saved analysis with ID and audit fields."""
    
    def to_analysis_request(self) -> AnalysisRequestCreate:
        """Converts the saved analysis to an analysis request."""
        return AnalysisRequestCreate(
            time_period_id=self.time_period_id,
            parameters=self.parameters,
            output_format=self.output_format,
            include_visualization=self.include_visualization,
            user_id=self.created_by
        )


class SavedAnalysisResponse(BaseModel):
    """Schema for API responses containing a saved analysis."""
    data: SavedAnalysis
    success: bool = True
    message: Optional[str] = None


class SavedAnalysisListResponse(BaseModel):
    """Schema for API responses containing a list of saved analyses."""
    data: List[SavedAnalysis]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class PriceMovementResult(BaseModel):
    """Schema for price movement analysis results."""
    analysis_id: uuid.UUID
    time_period_id: uuid.UUID
    time_period_name: str
    start_date: datetime.date
    end_date: datetime.date
    granularity: GranularityType
    start_value: Optional[CurrencyAmount] = None
    end_value: Optional[CurrencyAmount] = None
    absolute_change: Optional[CurrencyAmount] = None
    percentage_change: Optional[PercentageChange] = None
    trend_direction: Optional[TrendDirection] = None
    aggregates: Optional[Dict[str, Any]] = None
    time_series: Optional[List[Dict[str, Any]]] = None
    baseline_comparison: Optional[Dict[str, Any]] = None
    calculated_at: datetime.datetime
    is_cached: bool = False

    class Config:
        orm_mode = True


class AnalysisScheduleBase(BaseModel):
    """Base schema for analysis schedule configuration."""
    name: str
    saved_analysis_id: uuid.UUID
    schedule_type: str  # daily, weekly, monthly, cron
    schedule_value: str
    is_active: bool = True
    last_run_at: Optional[datetime.datetime] = None
    next_run_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


class AnalysisScheduleCreate(AnalysisScheduleBase):
    """Schema for creating a new analysis schedule."""
    user_id: uuid.UUID


class AnalysisSchedule(AnalysisScheduleBase, IDModel, TimestampModel, AuditableModel):
    """Complete schema for an analysis schedule with ID and audit fields."""
    pass


class AnalysisScheduleResponse(BaseModel):
    """Schema for API responses containing an analysis schedule."""
    data: AnalysisSchedule
    success: bool = True
    message: Optional[str] = None


class AnalysisScheduleListResponse(BaseModel):
    """Schema for API responses containing a list of analysis schedules."""
    data: List[AnalysisSchedule]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None