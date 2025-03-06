"""
Location schema models for the Freight Price Movement Agent.

These schemas define the structure and validation rules for geographic
locations used in freight price movement analysis, ensuring data quality
and consistent API interfaces.
"""

from typing import Optional, Dict
import uuid
import datetime
import re
from enum import Enum
from pydantic import validator

from ..core.schemas import BaseModel
from .common import IDModel, TimestampModel


class LocationType(Enum):
    """Enumeration of location types for geographic locations."""
    PORT = "PORT"
    AIRPORT = "AIRPORT"
    CITY = "CITY"
    WAREHOUSE = "WAREHOUSE" 
    DISTRIBUTION_CENTER = "DISTRIBUTION_CENTER"
    TERMINAL = "TERMINAL"
    OTHER = "OTHER"
    
    def __str__(self) -> str:
        """Returns the string representation of the location type."""
        return self.name


class CoordinatesSchema(BaseModel):
    """Schema for geographic coordinates."""
    latitude: float
    longitude: float
    
    @validator('latitude', 'longitude', check_fields=False)
    def validate_coordinates(cls, values) -> Dict:
        """Validates that the coordinates are within valid ranges."""
        if 'latitude' in values and (values['latitude'] < -90 or values['latitude'] > 90):
            raise ValueError('Latitude must be between -90 and 90 degrees')
        if 'longitude' in values and (values['longitude'] < -180 or values['longitude'] > 180):
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return values


class LocationBase(BaseModel):
    """Base schema for location data without ID and timestamps."""
    name: str
    code: str
    country: str
    region: Optional[str] = None
    type: LocationType
    coordinates: Optional[CoordinatesSchema] = None
    active: bool = True
    
    @validator('code')
    def validate_code(cls, code) -> str:
        """Validates and normalizes the location code."""
        code = code.upper()
        if not re.match(r'^[A-Z0-9]{2,50}$', code):
            raise ValueError('Code must be alphanumeric and between 2-50 characters')
        return code
    
    @validator('country')
    def validate_country(cls, country) -> str:
        """Validates and normalizes the country code."""
        country = country.upper()
        if not re.match(r'^[A-Z]{2}$', country):
            raise ValueError('Country must be a valid 2-letter ISO country code')
        return country


class LocationCreate(LocationBase):
    """Schema for creating a new location."""
    pass


class LocationUpdate(BaseModel):
    """Schema for updating an existing location."""
    name: Optional[str] = None
    code: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    type: Optional[LocationType] = None
    coordinates: Optional[CoordinatesSchema] = None
    active: Optional[bool] = None
    
    class Config:
        extra = "forbid"


class LocationResponse(LocationBase, IDModel, TimestampModel):
    """Schema for location response in API."""
    pass


class LocationSearchParams(BaseModel):
    """Schema for location search parameters."""
    name: Optional[str] = None
    code: Optional[str] = None
    country: Optional[str] = None
    type: Optional[LocationType] = None
    active_only: Optional[bool] = True
    limit: Optional[int] = 100
    offset: Optional[int] = 0
    
    @validator('limit')
    def validate_limit(cls, limit) -> int:
        """Validates the limit parameter."""
        if limit is None:
            return 100
        if limit < 1:
            raise ValueError('Limit must be at least 1')
        if limit > 1000:
            return 1000  # Cap at 1000 to prevent excessive queries
        return limit
    
    @validator('offset')
    def validate_offset(cls, offset) -> int:
        """Validates the offset parameter."""
        if offset is None:
            return 0
        if offset < 0:
            raise ValueError('Offset must be non-negative')
        return offset