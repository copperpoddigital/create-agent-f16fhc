"""
Core security module for the Freight Price Movement Agent application.

This module implements security features including authentication, password
management, token handling, and cryptographic utilities. It provides a comprehensive 
security framework for protecting sensitive freight pricing data and ensuring proper 
access control throughout the application.

Key components:
- Password hashing and verification using bcrypt
- JWT token generation and validation for authentication
- Secure session management
- Cryptographically secure random string generation

The security implementations follow industry best practices and standards
to protect against common vulnerabilities and attacks.
"""

from datetime import datetime, timedelta
import uuid
from typing import Dict, Optional

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from passlib.context import CryptContext
import secrets  # secrets module for cryptographically strong random values

from .config import settings
from .exceptions import AuthenticationException

# Configure the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT algorithm
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    
    Args:
        plain_password: The plain-text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates a secure hash for a password.
    
    Args:
        password: The plain-text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token for a user.
    
    Args:
        data: The payload data to include in the token
        expires_delta: Optional expiration time override, defaults to settings
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "token_type": "access",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT refresh token for a user.
    
    Args:
        data: The payload data to include in the token
        expires_delta: Optional expiration time override, defaults to settings
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """
    Decodes and validates a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        AuthenticationException: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise AuthenticationException("Token has expired")
    except JWTError:
        raise AuthenticationException("Invalid authentication token")
    except Exception as e:
        raise AuthenticationException("Token validation failed", {"error": str(e)})


def validate_access_token(token: str) -> Dict:
    """
    Validates an access token and ensures it's the correct type.
    
    Args:
        token: The JWT token to validate
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        AuthenticationException: If the token is invalid or not an access token
    """
    payload = decode_token(token)
    
    if payload.get("token_type") != "access":
        raise AuthenticationException("Invalid token type, access token required")
    
    return payload


def validate_refresh_token(token: str) -> Dict:
    """
    Validates a refresh token and ensures it's the correct type.
    
    Args:
        token: The JWT token to validate
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        AuthenticationException: If the token is invalid or not a refresh token
    """
    payload = decode_token(token)
    
    if payload.get("token_type") != "refresh":
        raise AuthenticationException("Invalid token type, refresh token required")
    
    return payload


def generate_password_reset_token(user_id: str) -> str:
    """
    Generates a secure token for password reset.
    
    Args:
        user_id: The ID of the user requesting password reset
        
    Returns:
        str: The password reset token
    """
    # Generate a random token component for additional security
    random_token = secrets.token_urlsafe(32)
    
    # Create token data with user ID, random component, and token type
    token_data = {
        "sub": user_id,
        "token_type": "reset",
        "random": random_token
    }
    
    # Set shorter expiration for security (30 minutes)
    expires = timedelta(minutes=30)
    
    # Use the JWT infrastructure to create a secure token
    return create_access_token(token_data, expires_delta=expires)


def validate_password_reset_token(token: str) -> str:
    """
    Validates a password reset token.
    
    Args:
        token: The password reset token to validate
        
    Returns:
        str: The user ID from the token
        
    Raises:
        AuthenticationException: If the token is invalid or not a reset token
    """
    payload = decode_token(token)
    
    if payload.get("token_type") != "reset":
        raise AuthenticationException("Invalid token type, reset token required")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Invalid reset token, missing user identifier")
    
    return user_id


def generate_session_id() -> str:
    """
    Generates a unique session identifier.
    
    Returns:
        str: A unique session ID (UUID4)
    """
    return str(uuid.uuid4())


def generate_secure_random_string(length: int) -> str:
    """
    Generates a cryptographically secure random string.
    
    Args:
        length: The desired length of the random string
        
    Returns:
        str: A secure random string
    """
    if length < 1:
        raise ValueError("Length must be a positive integer")
    
    # Use secrets module for cryptographically strong random string generation
    return secrets.token_urlsafe(length)