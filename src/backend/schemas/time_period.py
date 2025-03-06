"""
Defines Pydantic schema models for time periods used in the Freight Price Movement Agent.
These schemas provide validation, serialization, and deserialization of time period data for
API requests and responses.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import uuid
from pydantic import validator

from ..core.schemas import BaseModel
from .common import IDModel, TimestampModel
from ..models.enums import GranularityType


class TimePeriodBase(BaseModel):
    """Base schema for time period data with common fields."""
    name: str
    start_date: datetime
    end_date: datetime
    granularity: GranularityType = GranularityType.DAILY
    custom_interval_days: Optional[int] = None
    is_custom: bool = False
    
    @validator('end_date')
    def validate_dates(cls, v, values) -> datetime:
        """Validates that the start date is before the end date."""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @validator('is_custom', always=True)
    def validate_granularity(cls, v, values) -> bool:
        """Validates that custom_interval_days is provided when granularity is CUSTOM."""
        granularity = values.get('granularity')
        custom_interval_days = values.get('custom_interval_days')
        
        if granularity == GranularityType.CUSTOM and custom_interval_days is None:
            raise ValueError('custom_interval_days is required when granularity is CUSTOM')
        
        # Set is_custom to True if custom_interval_days is provided but granularity is not CUSTOM
        if granularity != GranularityType.CUSTOM and custom_interval_days is not None:
            return True
        
        return v
    
    class Config:
        orm_mode = True
        extra = 'forbid'


class TimePeriodCreate(TimePeriodBase):
    """Schema for creating a new time period."""
    pass


class TimePeriodUpdate(BaseModel):
    """Schema for updating an existing time period."""
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    granularity: Optional[GranularityType] = None
    custom_interval_days: Optional[int] = None
    is_custom: Optional[bool] = None
    
    @validator('end_date')
    def validate_dates(cls, v, values) -> Optional[datetime]:
        """Validates that the start date is before the end date if both are provided."""
        if v is not None and 'start_date' in values and values['start_date'] is not None and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @validator('is_custom', always=True)
    def validate_granularity(cls, v, values) -> Optional[bool]:
        """Validates that custom_interval_days is provided when granularity is CUSTOM."""
        granularity = values.get('granularity')
        custom_interval_days = values.get('custom_interval_days')
        
        if granularity == GranularityType.CUSTOM and custom_interval_days is None:
            raise ValueError('custom_interval_days is required when granularity is CUSTOM')
        
        # Set is_custom to True if custom_interval_days is provided but granularity is not CUSTOM
        if granularity is not None and granularity != GranularityType.CUSTOM and custom_interval_days is not None:
            return True
        
        return v
    
    class Config:
        orm_mode = True
        extra = 'forbid'


class TimePeriod(IDModel, TimestampModel, TimePeriodBase):
    """Complete schema for time period with ID and timestamps."""
    created_by: Optional[uuid.UUID] = None
    
    def get_duration_days(self) -> int:
        """Calculates the duration of the time period in days."""
        delta = self.end_date - self.start_date
        return delta.days
    
    def get_interval_days(self) -> int:
        """Gets the number of days for the granularity interval."""
        if self.granularity == GranularityType.CUSTOM:
            return self.custom_interval_days
        
        # Standard intervals for non-custom granularity
        granularity_days = {
            GranularityType.DAILY: 1,
            GranularityType.WEEKLY: 7,
            GranularityType.MONTHLY: 30,
            GranularityType.QUARTERLY: 90
        }
        
        return granularity_days.get(self.granularity, 1)
    
    def get_periods(self) -> List[Tuple[datetime, datetime]]:
        """Generates a list of time periods based on the granularity."""
        interval_days = self.get_interval_days()
        periods = []
        
        current_start = self.start_date
        while current_start < self.end_date:
            # Calculate the end of this period
            current_end = current_start + timedelta(days=interval_days)
            
            # Ensure we don't go beyond the overall end date
            if current_end > self.end_date:
                current_end = self.end_date
            
            periods.append((current_start, current_end))
            
            # Move to the next period
            current_start = current_end
        
        return periods
    
    @classmethod
    def from_orm(cls, obj: Any) -> 'TimePeriod':
        """Creates a TimePeriod instance from an ORM model."""
        return super().from_orm(obj)
    
    class Config:
        orm_mode = True
        extra = 'forbid'


class TimePeriodFilter(BaseModel):
    """Schema for filtering time periods in queries."""
    name: Optional[str] = None
    start_date_after: Optional[datetime] = None
    start_date_before: Optional[datetime] = None
    end_date_after: Optional[datetime] = None
    end_date_before: Optional[datetime] = None
    granularity: Optional[GranularityType] = None
    is_custom: Optional[bool] = None
    created_by: Optional[uuid.UUID] = None
    
    def to_query_params(self) -> dict:
        """Converts filter parameters to query parameters."""
        params = self.dict(exclude_none=True)
        
        # Handle date range filters
        query_params = {}
        for key, value in params.items():
            if key == 'start_date_after':
                query_params['start_date__gte'] = value
            elif key == 'start_date_before':
                query_params['start_date__lte'] = value
            elif key == 'end_date_after':
                query_params['end_date__gte'] = value
            elif key == 'end_date_before':
                query_params['end_date__lte'] = value
            else:
                query_params[key] = value
        
        return query_params
    
    class Config:
        extra = 'forbid'