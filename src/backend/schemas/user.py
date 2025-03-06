"""
User-related schema models for the Freight Price Movement Agent.

This module provides Pydantic schema models for user data validation, 
serialization, and deserialization. These schemas support user management, 
authentication, and authorization operations.
"""

import re
import uuid
import datetime
from typing import Optional, List, Dict

import pydantic

from ..core.schemas import BaseModel
from .common import IDModel, TimestampModel
from ..models.enums import UserRole

# Password complexity requirements
PASSWORD_MIN_LENGTH = 12
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$'


def validate_password(password: str) -> str:
    """
    Validates a password against complexity requirements.
    
    Args:
        password: The password to validate
        
    Returns:
        The validated password if it meets requirements
        
    Raises:
        ValueError: If the password does not meet complexity requirements
    """
    # Check minimum length
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")
    
    # Check for at least one special character
    if not any(c in '@$!%*?&' for c in password):
        raise ValueError("Password must contain at least one special character (@$!%*?&)")
    
    return password


class UserBase(BaseModel):
    """Base schema for user data with common fields."""
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    is_active: bool = True
    
    class Config:
        orm_mode = True
    
    @pydantic.validator('email')
    def validate_email(cls, email: str) -> str:
        """
        Validates that the email is in a correct format.
        
        Args:
            email: The email to validate
            
        Returns:
            The validated email
            
        Raises:
            ValueError: If the email format is invalid
        """
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValueError("Invalid email format")
        return email.lower()


class UserCreate(UserBase):
    """Schema for user creation with password validation."""
    password: str
    confirm_password: Optional[str] = None
    
    @pydantic.root_validator
    def validate_passwords(cls, values: Dict) -> Dict:
        """
        Validates that the password meets requirements and matches confirmation.
        
        Args:
            values: Dictionary of field values
            
        Returns:
            Validated values dictionary
            
        Raises:
            ValueError: If passwords don't match or don't meet requirements
        """
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        
        if confirm_password is not None and password != confirm_password:
            raise ValueError("Passwords do not match")
        
        # Validate password complexity
        if password:
            validate_password(password)
        
        return values


class UserUpdate(BaseModel):
    """Schema for user update with optional fields."""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    default_currency: Optional[str] = None
    date_format: Optional[str] = None
    theme: Optional[str] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    in_app_notifications: Optional[bool] = None
    preferences: Optional[dict] = None
    
    @pydantic.validator('email')
    def validate_email(cls, email: Optional[str]) -> Optional[str]:
        """
        Validates that the email is in a correct format if provided.
        
        Args:
            email: The email to validate
            
        Returns:
            The validated email
            
        Raises:
            ValueError: If the email format is invalid
        """
        if email is None:
            return None
            
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValueError("Invalid email format")
            
        return email.lower()


class UserInDB(UserBase, IDModel, TimestampModel):
    """Schema for user data from database with ID and timestamps."""
    last_login: Optional[datetime.datetime] = None
    is_locked: bool = False
    failed_login_attempts: int = 0
    default_currency: Optional[str] = "USD"
    date_format: Optional[str] = "MM/DD/YYYY"
    theme: Optional[str] = "light"
    email_notifications: bool = True
    sms_notifications: bool = False
    in_app_notifications: bool = True
    preferences: Optional[dict] = None
    
    class Config:
        orm_mode = True


class UserWithPassword(UserInDB):
    """Schema for user data with password hash (for internal use only)."""
    password_hash: str
    
    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """Schema for user data in API responses (without sensitive information)."""
    id: uuid.UUID
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    is_active: bool
    last_login: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    default_currency: Optional[str] = None
    date_format: Optional[str] = None
    theme: Optional[str] = None
    email_notifications: bool = True
    sms_notifications: bool = False
    in_app_notifications: bool = True
    
    class Config:
        orm_mode = True
    
    def get_full_name(self) -> str:
        """
        Returns the user's full name or username if no name is set.
        
        Returns:
            User's full name or username
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username


class UserListResponse(BaseModel):
    """Schema for paginated list of users in API responses."""
    data: List[UserResponse]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """Schema for password change request validation."""
    current_password: str
    new_password: str
    confirm_password: str
    
    @pydantic.root_validator
    def validate_passwords(cls, values: Dict) -> Dict:
        """
        Validates that the new password meets requirements and matches confirmation.
        
        Args:
            values: Dictionary of field values
            
        Returns:
            Validated values dictionary
            
        Raises:
            ValueError: If passwords don't match or don't meet requirements
        """
        new_password = values.get('new_password')
        confirm_password = values.get('confirm_password')
        
        if new_password != confirm_password:
            raise ValueError("New password and confirmation do not match")
        
        # Validate password complexity
        if new_password:
            validate_password(new_password)
        
        return values


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    default_currency: Optional[str] = None
    date_format: Optional[str] = None
    theme: Optional[str] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    in_app_notifications: Optional[bool] = None
    preferences: Optional[dict] = None
    
    @pydantic.validator('default_currency')
    def validate_currency(cls, currency: Optional[str]) -> Optional[str]:
        """
        Validates that the currency code is in a valid format if provided.
        
        Args:
            currency: The currency code to validate
            
        Returns:
            The validated currency code
            
        Raises:
            ValueError: If the currency code format is invalid
        """
        if currency is None:
            return None
            
        if not re.match(r'^[A-Z]{3}$', currency, re.IGNORECASE):
            raise ValueError("Currency code must be a 3-letter ISO code (e.g., USD, EUR, GBP)")
            
        return currency.upper()