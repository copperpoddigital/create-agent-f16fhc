"""
Authentication-related database models for the Freight Price Movement Agent.

This module defines the SQLAlchemy ORM models for authentication, session management,
and security monitoring. These models support the OAuth 2.0 authentication flow with
JWT tokens and implement security features like session tracking and failed login
attempt monitoring.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid
import sqlalchemy
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ...core.db import Base
from ...models.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin

# Token type constants
TOKEN_TYPE_ACCESS = 'access'
TOKEN_TYPE_REFRESH = 'refresh'
TOKEN_TYPE_RESET = 'reset'

# Session and security settings
SESSION_EXPIRY_HOURS = 24
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


class Token(Base, UUIDMixin, TimestampMixin):
    """
    SQLAlchemy model representing an authentication token in the system.
    
    Stores access and refresh tokens with their associated metadata
    including expiration time, validity status, and revocation information.
    """
    __tablename__ = 'auth_tokens'
    
    token = Column(String(255), unique=True, index=True, nullable=False)
    token_type = Column(String(50), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    is_valid = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    revocation_reason = Column(String(255), nullable=True)
    
    # Relationship with User model
    user = relationship('User')
    
    def __init__(self, token: str, token_type: str, expires_at: datetime, user_id: str):
        """
        Initializes a new Token instance.
        
        Args:
            token: The token string value
            token_type: Type of token (access, refresh, reset)
            expires_at: Expiration datetime
            user_id: ID of the associated user
        """
        self.id = str(uuid.uuid4())
        self.token = token
        self.token_type = token_type
        self.expires_at = expires_at
        self.user_id = user_id
        self.is_valid = True
        self.revoked_at = None
        self.revocation_reason = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """
        Checks if the token has expired.
        
        Returns:
            True if token has expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """
        Checks if the token is valid (not expired and not revoked).
        
        Returns:
            True if token is valid, False otherwise
        """
        return self.is_valid and not self.is_expired()
    
    def revoke(self, reason: Optional[str] = None) -> None:
        """
        Revokes the token, making it invalid.
        
        Args:
            reason: Optional reason for revocation
        """
        self.is_valid = False
        self.revoked_at = datetime.utcnow()
        self.revocation_reason = reason
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts token object to dictionary representation.
        
        Returns:
            Dictionary representation of token
        """
        return {
            'id': self.id,
            'token': self.token,
            'token_type': self.token_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'user_id': self.user_id,
            'is_valid': self.is_valid,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
            'revocation_reason': self.revocation_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Session(Base, TimestampMixin):
    """
    SQLAlchemy model representing a user session in the system.
    
    Tracks active user sessions with metadata including IP address,
    user agent, and activity timestamps for security and monitoring.
    """
    __tablename__ = 'user_sessions'
    
    session_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 addresses can be up to 45 chars
    user_agent = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    terminated_at = Column(DateTime, nullable=True)
    
    # Relationship with User model
    user = relationship('User')
    
    def __init__(self, session_id: str, user_id: str, ip_address: Optional[str] = None, 
                 user_agent: Optional[str] = None):
        """
        Initializes a new Session instance.
        
        Args:
            session_id: Unique session identifier
            user_id: ID of the associated user
            ip_address: Optional client IP address
            user_agent: Optional client user agent string
        """
        self.session_id = session_id
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = datetime.utcnow()
        self.last_activity_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(hours=SESSION_EXPIRY_HOURS)
        self.is_active = True
        self.terminated_at = None
        self.updated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """
        Checks if the session has expired.
        
        Returns:
            True if session has expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """
        Checks if the session is valid (active and not expired).
        
        Returns:
            True if session is valid, False otherwise
        """
        return self.is_active and not self.is_expired()
    
    def update_activity(self) -> None:
        """
        Updates the last activity timestamp.
        """
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def extend(self, hours: Optional[int] = None) -> None:
        """
        Extends the session expiration time.
        
        Args:
            hours: Number of hours to extend the session, defaults to SESSION_EXPIRY_HOURS
        """
        extension_hours = hours if hours is not None else SESSION_EXPIRY_HOURS
        self.expires_at = datetime.utcnow() + timedelta(hours=extension_hours)
        self.updated_at = datetime.utcnow()
    
    def terminate(self) -> None:
        """
        Terminates the session, making it inactive.
        """
        self.is_active = False
        self.terminated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts session object to dictionary representation.
        
        Returns:
            Dictionary representation of session
        """
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'is_active': self.is_active,
            'terminated_at': self.terminated_at.isoformat() if self.terminated_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class FailedLoginAttempt(Base, UUIDMixin, TimestampMixin):
    """
    SQLAlchemy model representing a failed login attempt for security monitoring.
    
    Tracks failed authentication attempts to identify potential brute force attacks
    and implement account lockout policies for security protection.
    """
    __tablename__ = 'failed_login_attempts'
    
    username = Column(String(255), index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 addresses can be up to 45 chars
    attempt_time = Column(DateTime, nullable=False)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    def __init__(self, username: str, ip_address: Optional[str] = None):
        """
        Initializes a new FailedLoginAttempt instance.
        
        Args:
            username: The username that failed authentication
            ip_address: Optional client IP address
        """
        self.id = str(uuid.uuid4())
        self.username = username
        self.ip_address = ip_address
        self.attempt_time = datetime.utcnow()
        self.resolved = False
        self.resolved_at = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def resolve(self) -> None:
        """
        Marks the failed login attempt as resolved.
        """
        self.resolved = True
        self.resolved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts failed login attempt object to dictionary representation.
        
        Returns:
            Dictionary representation of failed login attempt
        """
        return {
            'id': self.id,
            'username': self.username,
            'ip_address': self.ip_address,
            'attempt_time': self.attempt_time.isoformat() if self.attempt_time else None,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PasswordResetToken(Base, UUIDMixin, TimestampMixin):
    """
    SQLAlchemy model representing a password reset token.
    
    Manages password reset tokens with expiration and usage tracking
    to implement secure password recovery functionality.
    """
    __tablename__ = 'password_reset_tokens'
    
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)
    used_at = Column(DateTime, nullable=True)
    
    # Relationship with User model
    user = relationship('User')
    
    def __init__(self, token: str, user_id: str, expiry_hours: Optional[int] = 1):
        """
        Initializes a new PasswordResetToken instance.
        
        Args:
            token: The reset token string
            user_id: ID of the associated user
            expiry_hours: Number of hours until token expiration (default: 1)
        """
        self.id = str(uuid.uuid4())
        self.token = token
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(hours=expiry_hours)
        self.is_valid = True
        self.used_at = None
        self.updated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """
        Checks if the token has expired.
        
        Returns:
            True if token has expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """
        Checks if the token is valid (not expired, not used, and marked as valid).
        
        Returns:
            True if token is valid, False otherwise
        """
        return self.is_valid and not self.is_expired() and self.used_at is None
    
    def mark_used(self) -> None:
        """
        Marks the token as used.
        """
        self.is_valid = False
        self.used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def invalidate(self) -> None:
        """
        Invalidates the token without marking it as used.
        """
        self.is_valid = False
        self.updated_at = datetime.utcnow()