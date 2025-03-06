"""
Pydantic schemas for the admin module of the Freight Price Movement Agent.

This module defines the data validation schemas for system configuration,
admin activity logging, and maintenance scheduling.
"""

from typing import Dict, Optional
import datetime
import uuid

from pydantic import validator

from ...core.schemas import BaseModel
from ...schemas.common import IDModel, TimestampModel, AuditableModel
from ...models.enums import SystemConfigType
from .models import SystemConfig, AdminActivity, MaintenanceSchedule


class SystemConfigBase(BaseModel):
    """Base schema for system configuration with common fields."""
    key: str
    description: Optional[str] = None
    config_type: SystemConfigType = SystemConfigType.GENERAL
    is_encrypted: bool = False

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "key": "smtp_server",
                "description": "SMTP server address for email notifications",
                "config_type": "INTEGRATION",
                "is_encrypted": False
            }
        }


class SystemConfigCreate(SystemConfigBase):
    """Schema for creating a new system configuration."""
    value: str
    created_by_id: str

    @validator('key')
    def validate_key(cls, v, values):
        """Validates that the key is in lowercase with underscores."""
        normalized_key = v.lower().replace(' ', '_')
        return normalized_key


class SystemConfigUpdate(BaseModel):
    """Schema for updating an existing system configuration."""
    value: Optional[str] = None
    description: Optional[str] = None
    config_type: Optional[SystemConfigType] = None
    is_encrypted: Optional[bool] = None

    class Config:
        extra = "forbid"


class SystemConfigResponse(IDModel, TimestampModel):
    """Schema for system configuration response."""
    key: str
    value: str
    description: Optional[str] = None
    config_type: SystemConfigType
    is_encrypted: bool
    created_by_id: uuid.UUID

    class Config:
        orm_mode = True


class AdminActivityBase(BaseModel):
    """Base schema for admin activity with common fields."""
    action: str
    details: Dict
    resource_type: str
    resource_id: Optional[str] = None

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "action": "UPDATE_SYSTEM_CONFIG",
                "details": {"key": "smtp_server", "old_value": "mail.example.com", "new_value": "smtp.example.com"},
                "resource_type": "system_config",
                "resource_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class AdminActivityCreate(AdminActivityBase):
    """Schema for creating a new admin activity log."""
    user_id: str


class AdminActivityResponse(IDModel):
    """Schema for admin activity response."""
    user_id: str
    action: str
    details: Dict
    ip_address: Optional[str]
    timestamp: datetime.datetime
    resource_type: str
    resource_id: Optional[str]

    class Config:
        orm_mode = True


class MaintenanceScheduleBase(BaseModel):
    """Base schema for maintenance schedule with common fields."""
    title: str
    description: Optional[str] = None
    start_time: datetime.datetime
    end_time: datetime.datetime
    is_active: bool = True

    @validator('end_time')
    def validate_time_period(cls, v, values):
        """Validates that the end_time is after start_time."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "title": "Scheduled Database Maintenance",
                "description": "Regular index rebuilding and vacuum",
                "start_time": "2023-06-15T01:00:00Z",
                "end_time": "2023-06-15T03:00:00Z",
                "is_active": True
            }
        }


class MaintenanceScheduleCreate(MaintenanceScheduleBase):
    """Schema for creating a new maintenance schedule."""
    created_by_id: str


class MaintenanceScheduleUpdate(BaseModel):
    """Schema for updating an existing maintenance schedule."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    is_active: Optional[bool] = None

    @validator('end_time')
    def validate_time_period(cls, v, values):
        """Validates that the end_time is after start_time if both are provided."""
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

    class Config:
        extra = "forbid"


class MaintenanceScheduleResponse(IDModel, TimestampModel):
    """Schema for maintenance schedule response."""
    title: str
    description: Optional[str] = None
    start_time: datetime.datetime
    end_time: datetime.datetime
    is_active: bool
    is_active_now: bool
    created_by_id: uuid.UUID

    class Config:
        orm_mode = True