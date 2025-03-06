from datetime import datetime
from typing import Optional
import json

import sqlalchemy
from sqlalchemy.orm import relationship

from ..core.db import Base
from .mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditableMixin
from .enums import UserRole
from ..core.security import get_password_hash, verify_password


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditableMixin):
    """User model representing system users with authentication and authorization capabilities"""
    
    __tablename__ = 'users'
    
    username = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, unique=True)
    password_hash = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    first_name = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    last_name = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    role = sqlalchemy.Column(sqlalchemy.Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    is_locked = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    failed_login_attempts = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    last_login = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    default_currency = sqlalchemy.Column(sqlalchemy.String(50), nullable=True)
    date_format = sqlalchemy.Column(sqlalchemy.String(20), nullable=True)
    preferences = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    theme = sqlalchemy.Column(sqlalchemy.String(50), nullable=True)
    email_notifications = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    sms_notifications = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    in_app_notifications = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    
    analyses = sqlalchemy.orm.relationship('AnalysisResult', back_populates='user')
    audit_logs = sqlalchemy.orm.relationship('AuditLog', back_populates='user')
    data_sources = sqlalchemy.orm.relationship('DataSource', back_populates='created_by_user')
    reports = sqlalchemy.orm.relationship('Report', back_populates='user')
    
    def __init__(self, username: str, email: str, password: str, 
                 first_name: Optional[str] = None, 
                 last_name: Optional[str] = None,
                 role: Optional[UserRole] = None):
        """
        Initializes a new User instance
        
        Args:
            username: Unique username for the user
            email: Unique email address for the user
            password: Plain text password (will be hashed)
            first_name: Optional first name
            last_name: Optional last name
            role: UserRole for authorization (defaults to UserRole.VIEWER)
        """
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role or UserRole.VIEWER
        self.password_hash = get_password_hash(password)
        self.is_active = True
        self.is_locked = False
        self.failed_login_attempts = 0
        self.last_login = None
        
    def set_password(self, password: str) -> None:
        """
        Sets a new password for the user by hashing it
        
        Args:
            password: The new password in plain text
        """
        self.password_hash = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Verifies if the provided password matches the stored hash
        
        Args:
            password: The password to check
            
        Returns:
            True if password matches, False otherwise
        """
        return verify_password(password, self.password_hash)
    
    def update_last_login(self) -> None:
        """Updates the last login timestamp to current time"""
        self.last_login = datetime.utcnow()
    
    def increment_failed_login(self) -> None:
        """
        Increments the failed login attempts counter
        
        If failed_login_attempts >= 5, set is_locked to True
        """
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.is_locked = True
    
    def reset_failed_login_attempts(self) -> None:
        """Resets the failed login attempts counter to zero"""
        self.failed_login_attempts = 0
    
    def lock_account(self) -> None:
        """Locks the user account"""
        self.is_locked = True
    
    def unlock_account(self) -> None:
        """Unlocks the user account and resets failed login attempts"""
        self.is_locked = False
        self.reset_failed_login_attempts()
    
    def deactivate(self) -> None:
        """Deactivates the user account"""
        self.is_active = False
    
    def activate(self) -> None:
        """Activates the user account"""
        self.is_active = True
    
    def update_preferences(self, new_preferences: dict) -> None:
        """
        Updates user preferences
        
        Args:
            new_preferences: Dictionary of new preferences to merge with existing ones
        """
        if self.preferences is None:
            self.preferences = {}
        self.preferences.update(new_preferences)
    
    def get_full_name(self) -> str:
        """
        Returns the user's full name
        
        Returns:
            Full name or username if no name set
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.username
    
    def has_permission(self, permission: str) -> bool:
        """
        Checks if the user has a specific permission based on role
        
        Args:
            permission: The permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        # Admin role has all permissions
        if self.role == UserRole.ADMIN:
            return True
        
        # All roles can view
        if permission == 'view':
            return True
        
        # Manager and Analyst can edit and create
        if permission in ['edit', 'create']:
            return self.role in [UserRole.MANAGER, UserRole.ANALYST]
        
        # Only Manager can delete
        if permission == 'delete':
            return self.role == UserRole.MANAGER
        
        # Admin-specific permissions
        if permission == 'admin':
            return self.role == UserRole.ADMIN
        
        return False
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Converts user object to dictionary representation
        
        Args:
            include_sensitive: Whether to include sensitive information like password_hash
            
        Returns:
            Dictionary representation of user
        """
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.name if self.role else None,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'default_currency': self.default_currency,
            'date_format': self.date_format,
            'theme': self.theme,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'in_app_notifications': self.in_app_notifications
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
            user_dict['failed_login_attempts'] = self.failed_login_attempts
            user_dict['preferences'] = self.preferences
        
        return user_dict
    
    def __repr__(self) -> str:
        """
        Returns string representation of user
        
        Returns:
            String representation
        """
        return f"<User(id='{self.id}', username='{self.username}')>"