"""
Freight data schema models for the Freight Price Movement Agent.

This module provides Pydantic schema models for freight data validation,
serialization, and API operations, ensuring standardized representation
of freight pricing data for movement analysis over time.
"""

from typing import List, Optional, Dict
import datetime
import uuid
import decimal
from pydantic import validator

from ..core.schemas import BaseModel
from .common import (
    IDModel, 
    TimestampModel, 
    CurrencyAmount, 
    PaginationParams, 
    FilterParams
)
from ..models.enums import TransportMode
from .location import LocationResponse
from .carrier import CarrierResponse
from .route import RouteResponse


def validate_freight_charge(values: Dict) -> Dict:
    """
    Validates that freight charge is a positive number.
    
    Args:
        values: The values dictionary containing the freight_charge field
        
    Returns:
        The validated values dictionary
        
    Raises:
        ValueError: If freight_charge is not positive
    """
    if 'freight_charge' in values and values['freight_charge'] is not None:
        if values['freight_charge'] <= 0:
            raise ValueError('freight_charge must be a positive number')
    return values


class FreightDataBase(BaseModel):
    """
    Base schema for freight data with common fields.
    
    Contains all required fields for representing freight pricing data
    with appropriate validation rules.
    """
    record_date: datetime.datetime
    origin_id: uuid.UUID
    destination_id: uuid.UUID
    carrier_id: uuid.UUID
    freight_charge: decimal.Decimal
    currency_code: str = "USD"
    transport_mode: TransportMode
    service_level: Optional[str] = None
    additional_charges: Optional[dict] = None
    source_system: Optional[str] = None
    data_quality_flag: Optional[str] = None
    
    class Config:
        """Pydantic configuration for the FreightDataBase schema"""
        schema_extra = {
            "example": {
                "record_date": "2023-04-15T14:30:00Z",
                "origin_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "destination_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                "carrier_id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                "freight_charge": 1250.50,
                "currency_code": "USD",
                "transport_mode": "OCEAN",
                "service_level": "Standard",
                "additional_charges": {
                    "fuel_surcharge": 125.00,
                    "handling_fee": 75.00
                },
                "source_system": "TMS-Export",
                "data_quality_flag": None
            }
        }
        extra = "forbid"  # Prevent additional fields
    
    @validator('record_date')
    def validate_dates(cls, v, values) -> datetime.datetime:
        """
        Validates that record_date is not in the future.
        
        Args:
            v: The record_date value
            values: Dict containing previously validated fields
            
        Returns:
            Validated record_date value
            
        Raises:
            ValueError: If record_date is in the future
        """
        now = datetime.datetime.now(tz=v.tzinfo if v.tzinfo else None)
        if v > now:
            raise ValueError("record_date cannot be in the future")
        return v


class FreightDataCreate(FreightDataBase):
    """
    Schema for creating a new freight data record.
    
    Extends the base schema with additional fields needed for
    creation operations.
    """
    route_ids: Optional[List[uuid.UUID]] = None


class FreightDataUpdate(BaseModel):
    """
    Schema for updating an existing freight data record.
    
    All fields are optional to allow partial updates to freight data.
    """
    record_date: Optional[datetime.datetime] = None
    origin_id: Optional[uuid.UUID] = None
    destination_id: Optional[uuid.UUID] = None
    carrier_id: Optional[uuid.UUID] = None
    freight_charge: Optional[decimal.Decimal] = None
    currency_code: Optional[str] = None
    transport_mode: Optional[TransportMode] = None
    service_level: Optional[str] = None
    additional_charges: Optional[dict] = None
    source_system: Optional[str] = None
    data_quality_flag: Optional[str] = None
    route_ids: Optional[List[uuid.UUID]] = None
    
    @validator('record_date')
    def validate_dates(cls, v, values) -> Optional[datetime.datetime]:
        """
        Validates that record_date is not in the future if provided.
        
        Args:
            v: The record_date value
            values: Dict containing previously validated fields
            
        Returns:
            Validated record_date value or None
            
        Raises:
            ValueError: If record_date is in the future
        """
        if v is not None:
            now = datetime.datetime.now(tz=v.tzinfo if v.tzinfo else None)
            if v > now:
                raise ValueError("record_date cannot be in the future")
        return v


class FreightDataInDB(FreightDataBase, IDModel, TimestampModel):
    """
    Schema for freight data retrieved from the database.
    
    Extends the base schema with database-specific fields like ID
    and timestamp information.
    """
    pass


class FreightDataResponse(FreightDataInDB):
    """
    Schema for freight data in API responses.
    
    Extends the database schema with additional related data like
    origin, destination, carrier, and routes information.
    """
    origin: Optional[LocationResponse] = None
    destination: Optional[LocationResponse] = None
    carrier: Optional[CarrierResponse] = None
    routes: Optional[List[RouteResponse]] = []
    
    def formatted_freight_charge(self) -> str:
        """
        Returns the freight charge formatted with currency symbol.
        
        Returns:
            Formatted freight charge string
        """
        return CurrencyAmount(
            amount=self.freight_charge, 
            currency_code=self.currency_code
        ).format(decimal_places=2)


class FreightDataListResponse(BaseModel):
    """
    Schema for paginated list of freight data in API responses.
    
    Provides a standardized format for returning multiple freight data
    records with pagination metadata.
    """
    items: List[FreightDataResponse] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    pages: int = 0


class FreightDataFilterParams(FilterParams):
    """
    Schema for filtering freight data in API requests.
    
    Extends the base filter parameters with freight data specific filters.
    """
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    origin_id: Optional[uuid.UUID] = None
    destination_id: Optional[uuid.UUID] = None
    carrier_id: Optional[uuid.UUID] = None
    transport_mode: Optional[TransportMode] = None
    service_level: Optional[str] = None
    source_system: Optional[str] = None
    data_quality_flag: Optional[str] = None
    
    @validator('end_date')
    def validate_dates(cls, v, values) -> Optional[datetime.date]:
        """
        Validates that start_date is before or equal to end_date if both are provided.
        
        Args:
            v: The end_date value
            values: Dict containing previously validated fields
            
        Returns:
            Validated end_date value
            
        Raises:
            ValueError: If end_date is before start_date
        """
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError("end_date must be after or equal to start_date")
        return v
    
    def to_query_params(self) -> dict:
        """
        Converts filter parameters to query parameters.
        
        Returns:
            Dictionary of query parameters
        """
        params = super().to_query_params()
        
        # Add freight data-specific parameters
        if self.start_date:
            params['start_date'] = self.start_date.isoformat()
        if self.end_date:
            params['end_date'] = self.end_date.isoformat()
        if self.origin_id:
            params['origin_id'] = str(self.origin_id)
        if self.destination_id:
            params['destination_id'] = str(self.destination_id)
        if self.carrier_id:
            params['carrier_id'] = str(self.carrier_id)
        if self.transport_mode:
            params['transport_mode'] = str(self.transport_mode)
        if self.service_level:
            params['service_level'] = self.service_level
        if self.source_system:
            params['source_system'] = self.source_system
        if self.data_quality_flag:
            params['data_quality_flag'] = self.data_quality_flag
            
        # Remove None values
        return {k: v for k, v in params.items() if v is not None}