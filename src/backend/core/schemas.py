import datetime
import typing
import uuid
import decimal
import re
import json
from pydantic import BaseModel as PydanticBaseModel

# Regular expression pattern for converting camelCase
CAMEL_CASE_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')

def convert_datetime_to_iso_8601(dt: datetime.datetime) -> str:
    """
    Converts datetime objects to ISO 8601 formatted strings.
    
    Args:
        dt: The datetime object to convert
        
    Returns:
        ISO 8601 formatted datetime string
    """
    if isinstance(dt, datetime.datetime):
        return dt.isoformat()
    return dt

def convert_field_to_camel_case(snake_case_field: str) -> str:
    """
    Converts snake_case field names to camelCase for API consistency.
    
    Args:
        snake_case_field: The snake_case field name to convert
        
    Returns:
        camelCase field name
    """
    parts = snake_case_field.split('_')
    return parts[0] + ''.join(part.capitalize() for part in parts[1:])

def to_camel_case(snake_case_field: str) -> str:
    """
    Alias for convert_field_to_camel_case for backward compatibility.
    
    Args:
        snake_case_field: The snake_case field name to convert
        
    Returns:
        camelCase field name
    """
    return convert_field_to_camel_case(snake_case_field)

class BaseModel(PydanticBaseModel):
    """
    Base Pydantic model with common configuration for all schemas in the application.
    """
    
    class Config:
        """Pydantic configuration for the BaseModel"""
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime.datetime: lambda v: convert_datetime_to_iso_8601(v),
            uuid.UUID: lambda v: str(v),
            decimal.Decimal: lambda v: float(v)
        }
        alias_generator = convert_field_to_camel_case
    
    def dict(self, *args, **kwargs) -> dict:
        """
        Converts the model to a dictionary with optional customization.
        
        Args:
            by_alias: Whether to use field aliases (defaults to True)
            exclude_none: Whether to exclude None values (defaults to True)
            
        Returns:
            Dictionary representation of the model
        """
        by_alias = kwargs.pop('by_alias', True)
        exclude_none = kwargs.pop('exclude_none', True)
        return super().dict(*args, by_alias=by_alias, exclude_none=exclude_none, **kwargs)
    
    def json(self, *args, **kwargs) -> str:
        """
        Converts the model to a JSON string with optional customization.
        
        Args:
            by_alias: Whether to use field aliases (defaults to True)
            exclude_none: Whether to exclude None values (defaults to True)
            indent: Number of spaces for indentation (defaults to None)
            
        Returns:
            JSON string representation of the model
        """
        by_alias = kwargs.pop('by_alias', True)
        exclude_none = kwargs.pop('exclude_none', True)
        indent = kwargs.pop('indent', None)
        return super().json(*args, by_alias=by_alias, exclude_none=exclude_none, indent=indent, **kwargs)

T = typing.TypeVar('T')

class ResponseModel(BaseModel, typing.Generic[T]):
    """
    Base schema for API responses.
    
    Provides a standardized structure for all API responses with
    a data payload, success indicator, and optional message.
    """
    data: T
    success: bool = True
    message: typing.Optional[str] = None

class PaginatedResponse(BaseModel, typing.Generic[T]):
    """
    Base schema for paginated API responses.
    
    Extends the base response with pagination metadata including
    total count, current page, and page size.
    """
    data: typing.List[T]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: typing.Optional[str] = None

class ErrorResponse(BaseModel):
    """
    Schema for API error responses.
    
    Provides a standardized structure for error responses with
    a success flag (always False), error message, and optional
    detailed errors dictionary.
    """
    success: bool = False
    message: str
    errors: typing.Optional[dict] = None