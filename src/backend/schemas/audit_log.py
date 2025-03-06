"""
Pydantic schemas for audit log data validation, serialization, and deserialization in the Freight Price Movement Agent.

This module provides schema models used for audit log creation, responses, and filtering in API endpoints.
It supports comprehensive audit logging for compliance, security monitoring, and data retention policies.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

from pydantic import root_validator

from ..core.schemas import BaseModel
from .common import IDModel, TimestampModel
from ..models.audit_log import ActionType
from .user import UserResponse


class AuditLogBase(BaseModel):
    """Base schema for audit log data with common fields."""
    action: ActionType
    resource_type: str
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[dict] = None
    
    class Config:
        """Configuration for the AuditLogBase schema."""
        extra = "forbid"


class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log entry."""
    pass


class AuditLogResponse(AuditLogBase, IDModel, TimestampModel):
    """Schema for audit log data in API responses."""
    user: Optional[UserResponse] = None


class AuditLogFilterParams(BaseModel):
    """Schema for filtering audit logs in list operations."""
    action: Optional[ActionType] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    def to_query_params(self) -> Dict:
        """Converts filter parameters to query parameters.
        
        Returns:
            Dictionary of query parameters
        """
        params = self.dict(exclude_none=True)
        
        # Convert datetime objects to ISO format strings
        if 'start_date' in params:
            params['start_date'] = params['start_date'].isoformat()
        if 'end_date' in params:
            params['end_date'] = params['end_date'].isoformat()
            
        return params
    
    @root_validator
    def validate_dates(cls, values: Dict) -> Dict:
        """Validates that the start date is before or equal to the end date if both are provided.
        
        Args:
            values: Dictionary of field values
            
        Returns:
            Validated values dictionary
            
        Raises:
            ValueError: If end_date is before start_date
        """
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise ValueError("end_date must be after or equal to start_date")
            
        return values


class AuditLogPaginatedResponse(BaseModel):
    """Schema for paginated audit log responses."""
    data: List[AuditLogResponse]
    total: int
    page: int
    page_size: int