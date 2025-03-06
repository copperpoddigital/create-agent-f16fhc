"""
Models for the admin module of the Freight Price Movement Agent.

This module defines SQLAlchemy models for administrative functions including
system configuration, admin activity logging, and maintenance scheduling.
"""

import datetime
import typing
import uuid

import sqlalchemy
from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ...core.db import Base
from ...models.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin, UserTrackingMixin, AuditableMixin
from ...models.enums import SystemConfigType


class SystemConfig(Base, UUIDMixin, TimestampMixin):
    """
    SQLAlchemy model representing a system configuration setting.
    
    Stores configuration parameters for the application with support for
    encrypted values and categorization by configuration type.
    """
    __tablename__ = 'system_configs'
    
    key = Column(String(255), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    config_type = Column(Enum(SystemConfigType), nullable=False, default=SystemConfigType.GENERAL)
    is_encrypted = Column(Boolean, default=False)
    created_by_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    def __init__(self, key: str, value: typing.Any, description: typing.Optional[str] = None, 
                 config_type: SystemConfigType = SystemConfigType.GENERAL, 
                 is_encrypted: bool = False, created_by_id: str = None):
        """
        Initialize a new SystemConfig instance.
        
        Args:
            key: Unique identifier for the configuration setting
            value: Value of the configuration setting
            description: Optional description of the setting
            config_type: Type category for the setting
            is_encrypted: Flag indicating if the value is encrypted
            created_by_id: ID of the user who created this setting
        """
        # Convert key to lowercase with underscores for consistency
        self.key = key.lower().replace(' ', '_')
        # Convert value to string if it's not already
        self.value = str(value) if value is not None else ""
        self.description = description
        self.config_type = config_type
        self.is_encrypted = is_encrypted
        self.created_by_id = created_by_id
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert the SystemConfig object to a dictionary.
        
        Args:
            include_sensitive: Whether to include sensitive (encrypted) values
            
        Returns:
            Dictionary representation of the system configuration
        """
        result = {
            'id': self.id,
            'key': self.key,
            'value': self.value if (include_sensitive or not self.is_encrypted) else "*****",
            'description': self.description,
            'config_type': self.config_type.name if self.config_type else None,
            'is_encrypted': self.is_encrypted,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        return result


class AdminActivity(Base, UUIDMixin):
    """
    SQLAlchemy model representing an administrative activity log entry.
    
    Records actions performed by administrators for audit and tracking purposes.
    """
    __tablename__ = 'admin_activities'
    
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(255), nullable=True)
    
    def __init__(self, user_id: str, action: str, details: typing.Dict = None, 
                 ip_address: str = None, resource_type: str = None, resource_id: typing.Optional[str] = None):
        """
        Initialize a new AdminActivity instance.
        
        Args:
            user_id: ID of the user who performed the action
            action: Description of the action performed
            details: Additional details about the action
            ip_address: IP address from which the action was performed
            resource_type: Type of resource affected (e.g., 'user', 'config')
            resource_id: ID of the specific resource affected
        """
        self.user_id = user_id
        self.action = action
        self.details = details or {}
        self.ip_address = ip_address
        self.timestamp = datetime.datetime.utcnow()
        self.resource_type = resource_type
        self.resource_id = resource_id
    
    def to_dict(self) -> dict:
        """
        Convert the AdminActivity object to a dictionary.
        
        Returns:
            Dictionary representation of the admin activity
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id
        }


class MaintenanceSchedule(Base, UUIDMixin, TimestampMixin):
    """
    SQLAlchemy model representing a scheduled system maintenance period.
    
    Tracks planned maintenance windows with start/end times and notifications.
    """
    __tablename__ = 'maintenance_schedules'
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    def __init__(self, title: str, start_time: datetime.datetime, end_time: datetime.datetime, 
                 description: typing.Optional[str] = None, is_active: bool = True,
                 created_by_id: str = None):
        """
        Initialize a new MaintenanceSchedule instance.
        
        Args:
            title: Title/name for the maintenance window
            start_time: Starting time of the maintenance window
            end_time: Ending time of the maintenance window
            description: Optional detailed description of the maintenance
            is_active: Whether this maintenance schedule is active
            created_by_id: ID of the user who created this schedule
        """
        # Validate that end_time is after start_time
        if end_time <= start_time:
            raise ValueError("End time must be after start time")
            
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.is_active = is_active
        self.created_by_id = created_by_id
    
    def is_active_now(self) -> bool:
        """
        Check if the maintenance window is currently active.
        
        Returns:
            True if the current time is within the maintenance window and is_active is True
        """
        now = datetime.datetime.utcnow()
        return self.is_active and self.start_time <= now <= self.end_time
    
    def to_dict(self) -> dict:
        """
        Convert the MaintenanceSchedule object to a dictionary.
        
        Returns:
            Dictionary representation of the maintenance schedule
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active,
            'is_active_now': self.is_active_now(),
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }