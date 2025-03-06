"""
Carrier schema models for the Freight Price Movement Agent.

This module defines Pydantic schema models for carriers, providing
data validation, serialization, and API documentation for carrier-related
operations.
"""

from typing import List, Optional
import uuid

from pydantic import Field  # pydantic version: ^1.10.0

from ..core.schemas import BaseModel
from .common import IDModel, TimestampModel
from ..models.enums import CarrierType


class CarrierBase(BaseModel):
    """Base schema for carrier data with common fields."""
    name: str = Field(..., description="Name of the carrier", example="Maersk")
    code: Optional[str] = Field(None, description="Unique carrier code", example="MAEU")
    type: CarrierType = Field(..., description="Type of carrier", example=CarrierType.OCEAN_CARRIER)
    active: Optional[bool] = Field(True, description="Whether the carrier is active")

    class Config:
        """Pydantic configuration class."""
        orm_mode = True
        use_enum_values = True


class CarrierCreate(CarrierBase):
    """Schema for creating a new carrier."""
    pass


class CarrierUpdate(BaseModel):
    """Schema for updating an existing carrier.
    
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = Field(None, description="Name of the carrier", example="Maersk")
    code: Optional[str] = Field(None, description="Unique carrier code", example="MAEU")
    type: Optional[CarrierType] = Field(None, description="Type of carrier", example=CarrierType.OCEAN_CARRIER)
    active: Optional[bool] = Field(None, description="Whether the carrier is active")

    class Config:
        """Pydantic configuration class."""
        orm_mode = True
        use_enum_values = True


class CarrierResponse(CarrierBase, IDModel, TimestampModel):
    """Schema for carrier responses.
    
    Includes all base carrier fields plus ID and timestamp information.
    """
    pass


class CarrierListResponse(BaseModel):
    """Schema for paginated list of carriers.
    
    Used for endpoints that return multiple carriers with pagination metadata.
    """
    items: List[CarrierResponse] = Field(..., description="List of carriers")
    total: int = Field(..., description="Total number of carriers matching the query")
    page: int = Field(..., description="Current page number", example=1)
    size: int = Field(..., description="Number of items per page", example=20)