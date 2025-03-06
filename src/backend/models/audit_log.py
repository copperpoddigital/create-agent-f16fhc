"""
Defines the AuditLog model for the Freight Price Movement Agent application.

This model records all significant actions performed in the system for compliance,
security monitoring, and troubleshooting purposes. It captures user actions,
affected resources, timestamps, and detailed information about each operation.
"""

import enum
from datetime import datetime
from typing import Optional, Dict, Any

import sqlalchemy
from sqlalchemy.orm import relationship

from ..core.db import Base
from .mixins import UUIDMixin, TimestampMixin


class ActionType(enum.Enum):
    """Enumeration of action types for audit logging."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    CONFIGURATION = "CONFIGURATION"
    
    def __str__(self) -> str:
        """Returns the string representation of the action type."""
        return self.name


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy model for storing audit log entries."""
    
    __tablename__ = "audit_logs"
    
    action = sqlalchemy.Column(sqlalchemy.Enum(ActionType), nullable=False)
    resource_type = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    resource_id = sqlalchemy.Column(sqlalchemy.String(36), nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.String(36), sqlalchemy.ForeignKey('users.id'), nullable=True)
    ip_address = sqlalchemy.Column(sqlalchemy.String(45), nullable=True)  # IPv6 addresses can be up to 45 chars
    details = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    
    # Relationship to User model
    user = relationship('User', backref='audit_logs')
    
    def __init__(
        self,
        action: ActionType,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initializes a new AuditLog instance.
        
        Args:
            action: The action performed (from ActionType enum)
            resource_type: The type of resource affected (e.g., 'user', 'freight_data')
            resource_id: Optional ID of the specific resource affected
            user_id: Optional ID of the user who performed the action
            ip_address: Optional IP address where the action originated
            details: Optional dictionary containing additional details about the action
        """
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.user_id = user_id
        self.ip_address = ip_address
        self.details = details
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the audit log entry to a dictionary representation.
        
        Returns:
            Dictionary representation of the audit log entry
        """
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'action': str(self.action),
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'details': self.details
        }
        return result
    
    @classmethod
    def create_log_entry(
        cls,
        action: ActionType,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> 'AuditLog':
        """Class method to create and return a new audit log entry.
        
        Args:
            action: The action performed (from ActionType enum)
            resource_type: The type of resource affected
            resource_id: Optional ID of the specific resource affected
            user_id: Optional ID of the user who performed the action
            ip_address: Optional IP address where the action originated
            details: Optional dictionary containing additional details
            
        Returns:
            New audit log instance
        """
        return cls(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )