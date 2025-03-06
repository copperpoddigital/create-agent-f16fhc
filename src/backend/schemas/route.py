"""
Route schema models for the Freight Price Movement Agent.

These schemas define the structure and validation rules for route entities
(origin-destination pairs) used in freight price movement analysis, ensuring
data quality and consistent API interfaces.
"""

from typing import Optional
import uuid
import datetime
import decimal
from pydantic import validator

from ..core.schemas import BaseModel
from .common import IDModel, TimestampModel
from ..models.enums import TransportMode
from .location import LocationResponse


class RouteBase(BaseModel):
    """Base schema for route data without ID and timestamps."""
    origin_id: uuid.UUID
    destination_id: uuid.UUID
    transport_mode: TransportMode
    distance: Optional[decimal.Decimal] = None
    active: bool = True
    
    @validator('distance')
    def validate_distance(cls, distance):
        """Validates that the distance is a positive value."""
        if distance is None:
            return None
        if distance <= 0:
            raise ValueError('Distance must be a positive value')
        return distance


class RouteCreate(RouteBase):
    """Schema for creating a new route."""
    
    class Config:
        extra = "forbid"  # Prevent additional fields


class RouteUpdate(BaseModel):
    """Schema for updating an existing route."""
    origin_id: Optional[uuid.UUID] = None
    destination_id: Optional[uuid.UUID] = None
    transport_mode: Optional[TransportMode] = None
    distance: Optional[decimal.Decimal] = None
    active: Optional[bool] = None
    
    class Config:
        extra = "forbid"  # Prevent additional fields


class RouteResponse(RouteBase, IDModel, TimestampModel):
    """Schema for route response in API."""
    origin: Optional[LocationResponse] = None
    destination: Optional[LocationResponse] = None


class RouteSearchParams(BaseModel):
    """Schema for route search parameters."""
    origin_id: Optional[uuid.UUID] = None
    destination_id: Optional[uuid.UUID] = None  
    transport_mode: Optional[TransportMode] = None
    active_only: Optional[bool] = True
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    
    @validator('limit')
    def validate_limit(cls, limit):
        """Validates the limit parameter."""
        if limit is None:
            return 100
        if limit < 1:
            raise ValueError('Limit must be at least 1')
        if limit > 1000:
            return 1000  # Cap at 1000 to prevent excessive queries
        return limit
    
    @validator('offset')
    def validate_offset(cls, offset):
        """Validates the offset parameter."""
        if offset is None:
            return 0
        if offset < 0:
            raise ValueError('Offset must be non-negative')
        return offset