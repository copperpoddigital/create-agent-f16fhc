"""
Controller functions for authentication operations in the Freight Price Movement Agent.

This module implements the business logic for user authentication, token management,
session handling, and password operations, providing a secure OAuth 2.0 based
authentication framework with JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import Depends, HTTPException, status, Request, Response
from jose.exceptions import JWTError

from ...core.db import session
from ...models.user import User
from .schemas import (
    LoginRequest, TokenResponse, RefreshTokenRequest, RevokeTokenRequest,
    SessionResponse, PasswordChangeRequest, PasswordResetRequest,
    PasswordResetConfirm, TokenData
)
from .utils import (
    verify_password, store_token, revoke_token as revoke_db_token, is_token_valid,
    create_user_session, validate_session, update_session_activity,
    terminate_session, terminate_all_user_sessions, record_failed_login,
    check_account_lockout, resolve_failed_attempts, generate_password_reset_token,
    verify_password_reset_token, create_audit_log, get_user_by_username,
    get_user_by_email, get_user_by_id
)
from .models import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH
from ...core.security import create_access_token, create_refresh_token, decode_token
from ...core.exceptions import AuthenticationException, ValidationException, NotFoundException

# Constants for cookie names
ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
SESSION_COOKIE_NAME = "session_id"


def login(
    request_data: LoginRequest,
    request: Request,
    response: Response
) -> TokenResponse:
    """
    Authenticates a user and issues access and refresh tokens.
    
    Args:
        request_data: Login request data containing username and password
        request: FastAPI request object to access client information
        response: FastAPI response object to set cookies
        
    Returns:
        Token response with access and refresh tokens
    """
    # Check if account is locked
    if check_account_lockout(request_data.username):
        raise AuthenticationException(
            "Account is locked due to too many failed login attempts. Please try again later.",
            details={"reason": "account_locked"}
        )
    
    # Get user by username
    user = get_user_by_username(request_data.username)
    
    # If user not found, record failed login and raise exception
    if not user:
        record_failed_login(
            request_data.username, 
            ip_address=request.client.host if request.client else None
        )
        raise AuthenticationException(
            "Invalid username or password",
            details={"reason": "invalid_credentials"}
        )
    
    # Verify password
    if not verify_password(request_data.password, user):
        record_failed_login(
            request_data.username, 
            ip_address=request.client.host if request.client else None
        )
        raise AuthenticationException(
            "Invalid username or password",
            details={"reason": "invalid_credentials"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise AuthenticationException(
            "User account is inactive",
            details={"reason": "inactive_account"}
        )
    
    # Reset failed login attempts and update last login
    resolve_failed_attempts(user.username)
    user.update_last_login()
    session.commit()
    
    # Create access token
    access_token_data = {"sub": user.id}
    access_token = create_access_token(access_token_data)
    
    # Create refresh token
    refresh_token_data = {"sub": user.id}
    refresh_token = create_refresh_token(refresh_token_data)
    
    # Store tokens in database
    access_token_expires = datetime.utcnow() + timedelta(minutes=15)  # From settings
    refresh_token_expires = datetime.utcnow() + timedelta(days=7)     # From settings
    
    store_token(access_token, TOKEN_TYPE_ACCESS, user.id, access_token_expires)
    store_token(refresh_token, TOKEN_TYPE_REFRESH, user.id, refresh_token_expires)
    
    # Create user session
    user_session = create_user_session(
        user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    # Set cookies if remember_me is True
    if request_data.remember_me:
        response.set_cookie(
            key=ACCESS_TOKEN_COOKIE_NAME,
            value=access_token,
            httponly=True,
            secure=True,  # Set to False in development environment
            samesite="lax",
            max_age=15 * 60  # 15 minutes in seconds
        )
        
        response.set_cookie(
            key=REFRESH_TOKEN_COOKIE_NAME,
            value=refresh_token,
            httponly=True,
            secure=True,  # Set to False in development environment
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 days in seconds
        )
        
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=user_session.session_id,
            httponly=True,
            secure=True,  # Set to False in development environment
            samesite="lax",
            max_age=24 * 60 * 60  # 24 hours in seconds
        )
    
    # Create audit log
    create_audit_log(
        user.id,
        "LOGIN",
        details={
            "username": user.username,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        },
        ip_address=request.client.host if request.client else None
    )
    
    # Return token response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=15 * 60,  # 15 minutes in seconds
        session_id=user_session.session_id
    )


def logout(
    request: Request,
    response: Response,
    current_user: User
) -> Dict:
    """
    Logs out a user by revoking tokens and terminating the session.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object to clear cookies
        current_user: Currently authenticated user
        
    Returns:
        Success message
    """
    # Extract tokens and session ID
    auth_header = request.headers.get("Authorization", "")
    access_token = None
    if auth_header.startswith("Bearer "):
        access_token = auth_header.replace("Bearer ", "")
    else:
        access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    
    # Revoke access token if present
    if access_token:
        revoke_db_token(access_token, reason="Logout")
    
    # Revoke refresh token if present
    if refresh_token:
        revoke_db_token(refresh_token, reason="Logout")
    
    # Terminate session if present
    if session_id:
        terminate_session(session_id)
    
    # Clear cookies
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME)
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME)
    response.delete_cookie(SESSION_COOKIE_NAME)
    
    # Create audit log
    create_audit_log(
        current_user.id,
        "LOGOUT",
        details={
            "username": current_user.username,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        },
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "Successfully logged out"}


def refresh_token(
    request_data: RefreshTokenRequest,
    request: Request,
    response: Response
) -> TokenResponse:
    """
    Issues a new access token using a valid refresh token.
    
    Args:
        request_data: Refresh token request data
        request: FastAPI request object
        response: FastAPI response object to set cookies
        
    Returns:
        Token response with new access token
    """
    # Extract refresh token from request data or cookies
    refresh_token = request_data.refresh_token
    if not refresh_token:
        refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    # Check if refresh token is provided
    if not refresh_token:
        raise AuthenticationException(
            "Refresh token is required",
            details={"reason": "missing_token"}
        )
    
    # Verify token is valid in database
    if not is_token_valid(refresh_token, TOKEN_TYPE_REFRESH):
        raise AuthenticationException(
            "Invalid or expired refresh token",
            details={"reason": "invalid_token"}
        )
    
    # Decode token to get user ID
    try:
        token_data = decode_token(refresh_token)
        user_id = token_data.get("sub")
        
        if not user_id:
            raise AuthenticationException(
                "Invalid token payload",
                details={"reason": "invalid_payload"}
            )
        
        # Get user by ID
        user = get_user_by_id(user_id)
        
        if not user or not user.is_active:
            raise AuthenticationException(
                "User not found or inactive",
                details={"reason": "user_not_found"}
            )
        
        # Revoke old refresh token
        revoke_db_token(refresh_token, reason="Refresh")
        
        # Create new access token
        access_token_data = {"sub": user.id}
        access_token = create_access_token(access_token_data)
        
        # Create new refresh token
        refresh_token_data = {"sub": user.id}
        new_refresh_token = create_refresh_token(refresh_token_data)
        
        # Store new tokens in database
        access_token_expires = datetime.utcnow() + timedelta(minutes=15)  # From settings
        refresh_token_expires = datetime.utcnow() + timedelta(days=7)     # From settings
        
        store_token(access_token, TOKEN_TYPE_ACCESS, user.id, access_token_expires)
        store_token(new_refresh_token, TOKEN_TYPE_REFRESH, user.id, refresh_token_expires)
        
        # Update session activity if session ID is in cookies
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        if session_id:
            update_session_activity(session_id)
        
        # Set cookies if old cookies were present
        if request.cookies.get(ACCESS_TOKEN_COOKIE_NAME) or request.cookies.get(REFRESH_TOKEN_COOKIE_NAME):
            response.set_cookie(
                key=ACCESS_TOKEN_COOKIE_NAME,
                value=access_token,
                httponly=True,
                secure=True,  # Set to False in development environment
                samesite="lax",
                max_age=15 * 60  # 15 minutes in seconds
            )
            
            response.set_cookie(
                key=REFRESH_TOKEN_COOKIE_NAME,
                value=new_refresh_token,
                httponly=True,
                secure=True,  # Set to False in development environment
                samesite="lax",
                max_age=7 * 24 * 60 * 60  # 7 days in seconds
            )
        
        # Create audit log
        create_audit_log(
            user.id,
            "TOKEN_REFRESH",
            details={
                "username": user.username,
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            },
            ip_address=request.client.host if request.client else None
        )
        
        # Return token response
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=15 * 60,  # 15 minutes in seconds
            session_id=session_id
        )
        
    except JWTError:
        raise AuthenticationException(
            "Invalid refresh token",
            details={"reason": "token_invalid"}
        )
    except Exception as e:
        raise AuthenticationException(
            "Failed to refresh token",
            details={"reason": "token_processing_error", "error": str(e)}
        )


def revoke_token(
    request_data: RevokeTokenRequest,
    current_user: User
) -> Dict:
    """
    Revokes a specific token to invalidate it.
    
    Args:
        request_data: Token revocation request data
        current_user: Currently authenticated user
        
    Returns:
        Success message
    """
    # Extract token and token_type
    token = request_data.token
    token_type = request_data.token_type
    
    # Revoke token in database
    success = revoke_db_token(token, reason="Manual revocation")
    
    # Create audit log
    if success:
        create_audit_log(
            current_user.id,
            "TOKEN_REVOKE",
            details={
                "username": current_user.username,
                "token_type": token_type
            }
        )
    
    return {"message": "Token successfully revoked"}


def get_current_user(request: Request) -> User:
    """
    Extracts and validates the current user from the request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Current authenticated user
    """
    # Extract access token from authorization header or cookies
    auth_header = request.headers.get("Authorization", "")
    access_token = None
    
    if auth_header.startswith("Bearer "):
        access_token = auth_header.replace("Bearer ", "")
    else:
        access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    
    # Check if token is provided
    if not access_token:
        raise AuthenticationException(
            "Authentication required",
            details={"reason": "missing_token"}
        )
    
    # Verify token is valid in database
    if not is_token_valid(access_token, TOKEN_TYPE_ACCESS):
        raise AuthenticationException(
            "Invalid or expired token",
            details={"reason": "invalid_token"}
        )
    
    # Decode token
    try:
        token_data = decode_token(access_token)
        user_id = token_data.get("sub")
        
        if not user_id:
            raise AuthenticationException(
                "Invalid token payload",
                details={"reason": "invalid_payload"}
            )
        
        # Get user by ID
        user = get_user_by_id(user_id)
        
        if not user:
            raise AuthenticationException(
                "User not found",
                details={"reason": "user_not_found"}
            )
        
        if not user.is_active:
            raise AuthenticationException(
                "User account is inactive",
                details={"reason": "inactive_account"}
            )
        
        # Update session activity if session ID is in cookies
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        if session_id:
            update_session_activity(session_id)
        
        return user
        
    except JWTError:
        raise AuthenticationException(
            "Invalid authentication token",
            details={"reason": "token_invalid"}
        )
    except Exception as e:
        raise AuthenticationException(
            "Authentication failed",
            details={"reason": "token_processing_error", "error": str(e)}
        )


def change_password(
    request_data: PasswordChangeRequest,
    current_user: User
) -> Dict:
    """
    Changes a user's password after validating the current password.
    
    Args:
        request_data: Password change request data
        current_user: Currently authenticated user
        
    Returns:
        Success message
    """
    # Verify current password
    if not verify_password(request_data.current_password, current_user):
        raise AuthenticationException(
            "Current password is incorrect",
            details={"reason": "invalid_password"}
        )
    
    # Set new password
    current_user.set_password(request_data.new_password)
    
    # Terminate all user sessions except current one for security
    session_id = None
    try:
        # Get the current session ID from request context
        from fastapi import request as fastapi_request
        session_id = fastapi_request.cookies.get(SESSION_COOKIE_NAME)
    except:
        # No session to preserve
        pass
    
    terminate_all_user_sessions(current_user.id, current_session_id=session_id)
    
    # Commit changes
    session.commit()
    
    # Create audit log
    create_audit_log(
        current_user.id,
        "PASSWORD_CHANGE",
        details={"username": current_user.username}
    )
    
    return {"message": "Password successfully changed"}


def request_password_reset(
    request_data: PasswordResetRequest
) -> Dict:
    """
    Initiates a password reset process by generating a reset token.
    
    Args:
        request_data: Password reset request data
        
    Returns:
        Success message
    """
    # Get user by email
    user = get_user_by_email(request_data.email)
    
    # If user not found, still return success to prevent user enumeration
    if not user:
        return {"message": "If your email is registered, you will receive password reset instructions"}
    
    # Generate password reset token
    reset_token = generate_password_reset_token(user.id)
    
    # In a real implementation, you would send an email with the reset token
    # For example:
    # reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
    # send_password_reset_email(user.email, user.username, reset_url)
    
    # Create audit log
    create_audit_log(
        user.id,
        "PASSWORD_RESET_REQUEST",
        details={"username": user.username, "email": user.email}
    )
    
    return {"message": "If your email is registered, you will receive password reset instructions"}


def confirm_password_reset(
    request_data: PasswordResetConfirm
) -> Dict:
    """
    Completes the password reset process by validating the token and setting a new password.
    
    Args:
        request_data: Password reset confirmation data
        
    Returns:
        Success message
    """
    # Verify token
    reset_token = verify_password_reset_token(request_data.token)
    
    if not reset_token:
        raise AuthenticationException(
            "Invalid or expired password reset token",
            details={"reason": "invalid_token"}
        )
    
    # Get user
    user = get_user_by_id(reset_token.user_id)
    
    if not user:
        raise NotFoundException(
            "User not found",
            details={"reason": "user_not_found"}
        )
    
    # Set new password
    user.set_password(request_data.new_password)
    
    # Mark token as used
    reset_token.mark_used()
    
    # Terminate all user sessions for security
    terminate_all_user_sessions(user.id)
    
    # Commit changes
    session.commit()
    
    # Create audit log
    create_audit_log(
        user.id,
        "PASSWORD_RESET_COMPLETE",
        details={"username": user.username}
    )
    
    return {"message": "Password successfully reset"}


def get_session_info(
    request: Request,
    current_user: User
) -> SessionResponse:
    """
    Retrieves information about the current user session.
    
    Args:
        request: FastAPI request object
        current_user: Currently authenticated user
        
    Returns:
        Session information
    """
    # Extract session ID from cookies
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not session_id:
        raise AuthenticationException(
            "No active session found",
            details={"reason": "missing_session"}
        )
    
    # Validate session
    user_session = validate_session(session_id)
    
    if not user_session:
        raise AuthenticationException(
            "Invalid or expired session",
            details={"reason": "invalid_session"}
        )
    
    # Return session information
    return SessionResponse(
        session_id=user_session.session_id,
        user_id=user_session.user_id,
        ip_address=user_session.ip_address,
        user_agent=user_session.user_agent,
        created_at=user_session.created_at,
        expires_at=user_session.expires_at,
        last_activity_at=user_session.last_activity_at,
        is_active=user_session.is_active
    )


def terminate_current_session(
    request: Request,
    response: Response,
    current_user: User
) -> Dict:
    """
    Terminates the current user session.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object to clear cookies
        current_user: Currently authenticated user
        
    Returns:
        Success message
    """
    # Extract session ID from cookies
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not session_id:
        raise AuthenticationException(
            "No active session found",
            details={"reason": "missing_session"}
        )
    
    # Terminate session
    success = terminate_session(session_id)
    
    if not success:
        raise AuthenticationException(
            "Failed to terminate session",
            details={"reason": "termination_failed"}
        )
    
    # Clear session cookie
    response.delete_cookie(SESSION_COOKIE_NAME)
    
    # Create audit log
    create_audit_log(
        current_user.id,
        "SESSION_TERMINATE",
        details={"username": current_user.username, "session_id": session_id},
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "Session successfully terminated"}


def terminate_other_sessions(
    request: Request,
    current_user: User
) -> Dict:
    """
    Terminates all user sessions except the current one.
    
    Args:
        request: FastAPI request object
        current_user: Currently authenticated user
        
    Returns:
        Success message with count of terminated sessions
    """
    # Extract session ID from cookies
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not session_id:
        raise AuthenticationException(
            "No active session found",
            details={"reason": "missing_session"}
        )
    
    # Terminate all other sessions
    terminated_count = terminate_all_user_sessions(current_user.id, current_session_id=session_id)
    
    # Create audit log
    create_audit_log(
        current_user.id,
        "SESSIONS_TERMINATE_OTHERS",
        details={"username": current_user.username, "terminated_count": terminated_count},
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": f"Successfully terminated {terminated_count} session(s)", "count": terminated_count}


def get_user_info(current_user: User) -> Dict:
    """
    Retrieves information about the current authenticated user.
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        User information
    """
    # Convert user object to dictionary with necessary information
    user_info = current_user.to_dict(include_sensitive=False)
    
    return user_info