"""
Authentication-related Pydantic schemas for the Freight Price Movement Agent.

This module defines Pydantic schemas for validation, serialization, and
deserialization of authentication-related data. These schemas support the
OAuth 2.0 authentication flow with JWT tokens, session management, and
implement security features like password complexity validation.
"""

from datetime import datetime
import re
from typing import Optional, Dict

import pydantic

from ...core.schemas import BaseModel, ErrorResponse, SuccessResponse
from ...core.exceptions import ValidationException
from ..auth.models import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH, TOKEN_TYPE_RESET

# Password requirements
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
        ValidationException: If the password doesn't meet complexity requirements
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationException(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long",
            details={"password": "insufficient_length"}
        )
    
    if not re.search(r'[a-z]', password):
        raise ValidationException(
            "Password must contain at least one lowercase letter",
            details={"password": "missing_lowercase"}
        )
    
    if not re.search(r'[A-Z]', password):
        raise ValidationException(
            "Password must contain at least one uppercase letter",
            details={"password": "missing_uppercase"}
        )
    
    if not re.search(r'\d', password):
        raise ValidationException(
            "Password must contain at least one digit",
            details={"password": "missing_digit"}
        )
    
    if not re.search(r'[@$!%*?&]', password):
        raise ValidationException(
            "Password must contain at least one special character (@$!%*?&)",
            details={"password": "missing_special_character"}
        )
    
    return password


class LoginRequest(BaseModel):
    """
    Schema for user login request validation.
    
    Validates a user login request with username, password, and optional
    remember_me flag for extended session.
    """
    username: str
    password: str
    remember_me: Optional[bool] = False
    
    class Config:
        """Configuration for the LoginRequest schema."""
        extra = 'forbid'  # Prevent additional fields


class TokenResponse(BaseModel):
    """
    Schema for token response after successful authentication.
    
    Provides access and refresh tokens along with expiration information.
    """
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    session_id: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token request validation.
    
    Validates a request to refresh an access token using a refresh token.
    The refresh_token can be None if it's in cookies.
    """
    refresh_token: Optional[str] = None


class RevokeTokenRequest(BaseModel):
    """
    Schema for token revocation request validation.
    
    Validates a request to revoke a token, making it invalid.
    """
    token: str
    token_type: Optional[str] = TOKEN_TYPE_ACCESS
    
    @pydantic.validator('token_type')
    def validate_token_type(cls, token_type: str) -> str:
        """
        Validates that the token type is one of the allowed values.
        
        Args:
            token_type: The token type to validate
            
        Returns:
            Validated token type
            
        Raises:
            ValueError: If token_type is not valid
        """
        if token_type not in [TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH, TOKEN_TYPE_RESET]:
            raise ValueError(
                f"Invalid token type. Must be one of: {TOKEN_TYPE_ACCESS}, {TOKEN_TYPE_REFRESH}, {TOKEN_TYPE_RESET}"
            )
        return token_type


class SessionResponse(BaseModel):
    """
    Schema for session information response.
    
    Provides comprehensive information about a user session.
    """
    session_id: str
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    last_activity_at: datetime
    is_active: bool


class PasswordChangeRequest(BaseModel):
    """
    Schema for password change request validation.
    
    Validates a request to change a user's password.
    """
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
            ValueError: If passwords don't match or validation fails
        """
        new_password = values.get('new_password')
        confirm_password = values.get('confirm_password')
        
        if new_password != confirm_password:
            raise ValueError("New password and confirmation do not match")
        
        try:
            # Use the validate_password function to check complexity
            validate_password(new_password)
        except ValidationException as e:
            raise ValueError(str(e))
        
        return values


class PasswordResetRequest(BaseModel):
    """
    Schema for password reset request validation.
    
    Validates a request to initiate a password reset process.
    """
    email: str
    
    @pydantic.validator('email')
    def validate_email(cls, email: str) -> str:
        """
        Validates that the email is in a correct format.
        
        Args:
            email: The email to validate
            
        Returns:
            Validated email
            
        Raises:
            ValueError: If email format is invalid
        """
        # Simple regex for email validation
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError("Invalid email format")
        return email


class PasswordResetConfirm(BaseModel):
    """
    Schema for password reset confirmation validation.
    
    Validates a request to complete a password reset process.
    """
    token: str
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
            ValueError: If passwords don't match or validation fails
        """
        new_password = values.get('new_password')
        confirm_password = values.get('confirm_password')
        
        if new_password != confirm_password:
            raise ValueError("New password and confirmation do not match")
        
        try:
            # Use the validate_password function to check complexity
            validate_password(new_password)
        except ValidationException as e:
            raise ValueError(str(e))
        
        return values


class TokenData(BaseModel):
    """
    Schema for decoded token data.
    
    Represents the data contained in a JWT token after decoding.
    """
    sub: str  # Subject (user ID)
    jti: Optional[str] = None  # JWT ID (unique identifier for the token)
    exp: Optional[datetime] = None  # Expiration time
    iat: Optional[datetime] = None  # Issued at time
    type: Optional[str] = None  # Token type