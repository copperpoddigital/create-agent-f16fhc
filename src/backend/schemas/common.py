"""
Common schema models for the Freight Price Movement Agent.

This module provides reusable schema components for date ranges, currency amounts,
percentage changes, and base models with common fields like IDs and timestamps.
"""

from typing import Dict, Optional
import datetime
import uuid
import decimal
from pydantic import validator

from ..core.schemas import BaseModel
from ..models.enums import TrendDirection, OutputFormat, GranularityType


def format_currency(amount: decimal.Decimal, currency_code: str, decimal_places: int = 2) -> str:
    """
    Formats a decimal amount with currency symbol and proper decimal places.
    
    Args:
        amount: The amount to format
        currency_code: The ISO currency code (e.g., USD, EUR)
        decimal_places: Number of decimal places to round to
        
    Returns:
        Formatted currency string
    """
    # Round the amount to the specified decimal places
    rounded_amount = round(amount, decimal_places)
    
    # Format with currency symbols
    if currency_code == "USD":
        return f"${rounded_amount:.{decimal_places}f}"
    elif currency_code == "EUR":
        return f"€{rounded_amount:.{decimal_places}f}"
    elif currency_code == "GBP":
        return f"£{rounded_amount:.{decimal_places}f}"
    else:
        # For other currencies, use the code as prefix
        return f"{currency_code} {rounded_amount:.{decimal_places}f}"


def format_percentage(value: decimal.Decimal, decimal_places: int = 2) -> str:
    """
    Formats a decimal value as a percentage with proper decimal places.
    
    Args:
        value: The value to format as percentage
        decimal_places: Number of decimal places to round to
        
    Returns:
        Formatted percentage string
    """
    # Round the value to the specified decimal places
    rounded_value = round(value, decimal_places)
    
    # Format as percentage
    return f"{rounded_value:.{decimal_places}f}%"


class DateRange(BaseModel):
    """Schema for date range selection without time component."""
    start_date: datetime.date
    end_date: datetime.date
    
    @validator('end_date')
    def validate_dates(cls, v, values) -> datetime.date:
        """
        Validates that the start date is before or equal to the end date.
        
        Args:
            v: The end_date value
            values: Dict containing previously validated fields
            
        Returns:
            Validated end_date value
        """
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v


class DateTimeRange(BaseModel):
    """Schema for datetime range selection with time component."""
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    
    @validator('end_datetime')
    def validate_datetimes(cls, v, values) -> datetime.datetime:
        """
        Validates that the start datetime is before or equal to the end datetime.
        
        Args:
            v: The end_datetime value
            values: Dict containing previously validated fields
            
        Returns:
            Validated end_datetime value
        """
        if 'start_datetime' in values and v < values['start_datetime']:
            raise ValueError('end_datetime must be after or equal to start_datetime')
        return v


class CurrencyAmount(BaseModel):
    """Schema for currency amount with formatting capabilities."""
    amount: decimal.Decimal
    currency_code: str = "USD"
    
    def format(self, decimal_places: int = 2) -> str:
        """
        Formats the currency amount as a string.
        
        Args:
            decimal_places: Number of decimal places to round to
            
        Returns:
            Formatted currency string
        """
        return format_currency(self.amount, self.currency_code, decimal_places)


class PercentageChange(BaseModel):
    """Schema for percentage change with formatting capabilities."""
    value: decimal.Decimal
    direction: TrendDirection
    
    @validator('direction', pre=True, always=True)
    def set_direction(cls, v, values) -> TrendDirection:
        """
        Sets the direction based on the value if not provided.
        
        Args:
            v: The direction value
            values: Dict containing previously validated fields
            
        Returns:
            Calculated direction based on value
        """
        if v is not None:
            return v
            
        if 'value' in values:
            return TrendDirection.from_percentage(float(values['value']))
        
        return TrendDirection.STABLE
    
    def format(self, decimal_places: int = 2) -> str:
        """
        Formats the percentage change as a string with direction indicator.
        
        Args:
            decimal_places: Number of decimal places to round to
            
        Returns:
            Formatted percentage string with direction indicator
        """
        formatted_value = format_percentage(self.value, decimal_places)
        
        if self.direction == TrendDirection.INCREASING:
            return f"{formatted_value} [↑]"
        elif self.direction == TrendDirection.DECREASING:
            return f"{formatted_value} [↓]"
        else:  # STABLE
            return f"{formatted_value} [→]"


class IDModel(BaseModel):
    """Base schema for models with UUID identifiers."""
    id: uuid.UUID


class TimestampModel(BaseModel):
    """Base schema for models with timestamp fields."""
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class OutputFormatParams(BaseModel):
    """Schema for output format parameters."""
    format: OutputFormat = OutputFormat.JSON
    include_visualization: Optional[bool] = False


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = 1
    page_size: int = 20


class TimeRangeParams(BaseModel):
    """Schema for time range parameters."""
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    granularity: GranularityType = GranularityType.DAILY
    
    @validator('end_date')
    def validate_dates(cls, v, values) -> Optional[datetime.date]:
        """
        Validates that the start date is before or equal to the end date if both are provided.
        
        Args:
            v: The end_date value
            values: Dict containing previously validated fields
            
        Returns:
            Validated end_date value
        """
        if v and 'start_date' in values and values['start_date'] and v < values['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v