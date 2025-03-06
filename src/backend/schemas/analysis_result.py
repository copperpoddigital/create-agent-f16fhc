"""
Defines Pydantic schema models for analysis results in the Freight Price Movement Agent.

This module provides schemas for validating, serializing, and deserializing analysis result data,
including price movement calculations, trend directions, and related metadata.
"""

from typing import Dict, List, Optional, Tuple, Any
import datetime
import uuid
import decimal

from pydantic import Field

from ..core.schemas import BaseModel
from .common import IDModel, TimestampModel, CurrencyAmount, PercentageChange
from .time_period import TimePeriod
from ..models.enums import TrendDirection, AnalysisStatus, OutputFormat
from .responses import PriceMovementResponse


class AnalysisResultBase(BaseModel):
    """Base schema for analysis result data with common fields."""
    name: Optional[str] = None
    time_period_id: uuid.UUID
    status: AnalysisStatus = AnalysisStatus.PENDING
    parameters: Optional[Dict[str, Any]] = None
    start_value: Optional[decimal.Decimal] = None
    end_value: Optional[decimal.Decimal] = None
    absolute_change: Optional[decimal.Decimal] = None
    percentage_change: Optional[decimal.Decimal] = None
    trend_direction: Optional[TrendDirection] = None
    currency_code: str = "USD"
    output_format: OutputFormat = OutputFormat.JSON
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    calculated_at: Optional[datetime.datetime] = None
    is_cached: bool = False
    cache_expires_at: Optional[datetime.datetime] = None

    class Config:
        """Pydantic configuration class."""
        orm_mode = True
        extra = "forbid"


class AnalysisResultCreate(AnalysisResultBase):
    """Schema for creating a new analysis result."""
    pass


class AnalysisResultUpdate(BaseModel):
    """Schema for updating an existing analysis result."""
    name: Optional[str] = None
    status: Optional[AnalysisStatus] = None
    parameters: Optional[Dict[str, Any]] = None
    start_value: Optional[decimal.Decimal] = None
    end_value: Optional[decimal.Decimal] = None
    absolute_change: Optional[decimal.Decimal] = None
    percentage_change: Optional[decimal.Decimal] = None
    trend_direction: Optional[TrendDirection] = None
    currency_code: Optional[str] = None
    output_format: Optional[OutputFormat] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    calculated_at: Optional[datetime.datetime] = None
    is_cached: Optional[bool] = None
    cache_expires_at: Optional[datetime.datetime] = None

    class Config:
        """Pydantic configuration class."""
        orm_mode = True
        extra = "forbid"


class AnalysisResult(IDModel, TimestampModel, AnalysisResultBase):
    """Complete schema for analysis result with ID and timestamps."""
    time_period: Optional[TimePeriod] = None
    created_by: Optional[uuid.UUID] = None

    def get_formatted_changes(self) -> Tuple[Optional[CurrencyAmount], Optional[PercentageChange]]:
        """
        Returns formatted currency and percentage changes.
        
        Returns:
            Tuple of formatted currency amount and percentage change
        """
        formatted_absolute_change = None
        formatted_percentage_change = None
        
        if self.absolute_change is not None:
            formatted_absolute_change = CurrencyAmount(
                amount=self.absolute_change,
                currency_code=self.currency_code
            )
            
        if self.percentage_change is not None:
            direction = self.trend_direction or TrendDirection.STABLE
            formatted_percentage_change = PercentageChange(
                value=self.percentage_change,
                direction=direction
            )
            
        return (formatted_absolute_change, formatted_percentage_change)
    
    def is_cache_valid(self) -> bool:
        """
        Checks if the cached result is still valid.
        
        Returns:
            True if cache is valid, False otherwise
        """
        if not self.is_cached:
            return False
            
        if self.cache_expires_at is None:
            return False
            
        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        if current_time > self.cache_expires_at:
            return False
            
        return True
    
    def to_response(self, include_details: Optional[bool] = False) -> PriceMovementResponse:
        """
        Converts the AnalysisResult model to a PriceMovementResponse.
        
        Args:
            include_details: Whether to include detailed time series and visualization data
            
        Returns:
            Response model for API
        """
        formatted_absolute_change, formatted_percentage_change = self.get_formatted_changes()
        
        response = PriceMovementResponse(
            analysis_id=self.id,
            time_period_id=self.time_period_id,
            start_date=self.time_period.start_date.date() if self.time_period else None,
            end_date=self.time_period.end_date.date() if self.time_period else None,
            granularity=str(self.time_period.granularity) if self.time_period else None,
            absolute_change=self.absolute_change,
            percentage_change=self.percentage_change,
            trend_direction=self.trend_direction,
            absolute_change_formatted=formatted_absolute_change,
            percentage_change_formatted=formatted_percentage_change,
            output_format=self.output_format,
            is_cached=self.is_cached,
            calculated_at=self.calculated_at or self.created_at,
            aggregates=self.results.get("aggregates") if self.results else None
        )
        
        # Include detailed data if requested
        if include_details and self.results:
            response.time_series = self.results.get("time_series", [])
            response.visualization_data = self.results.get("visualization_data")
            
        return response
    
    @classmethod
    def from_orm(cls, obj: Any) -> 'AnalysisResult':
        """
        Creates an AnalysisResult instance from an ORM model.
        
        Args:
            obj: The ORM model instance
            
        Returns:
            New AnalysisResult instance
        """
        return super().from_orm(obj)
    
    class Config:
        """Pydantic configuration class."""
        orm_mode = True
        extra = "forbid"


class AnalysisResultFilter(BaseModel):
    """Schema for filtering analysis results in queries."""
    name: Optional[str] = None
    time_period_id: Optional[uuid.UUID] = None
    status: Optional[AnalysisStatus] = None
    trend_direction: Optional[TrendDirection] = None
    output_format: Optional[OutputFormat] = None
    is_cached: Optional[bool] = None
    calculated_after: Optional[datetime.datetime] = None
    calculated_before: Optional[datetime.datetime] = None
    created_by: Optional[uuid.UUID] = None
    
    def to_query_params(self) -> Dict[str, Any]:
        """
        Converts filter parameters to query parameters.
        
        Returns:
            Dictionary of query parameters
        """
        params = self.dict(exclude_none=True)
        
        # Handle date range filters
        query_params = {}
        for key, value in params.items():
            if key == 'calculated_after':
                query_params['calculated_at__gte'] = value
            elif key == 'calculated_before':
                query_params['calculated_at__lte'] = value
            else:
                query_params[key] = value
        
        return query_params
    
    class Config:
        """Pydantic configuration class."""
        extra = "forbid"