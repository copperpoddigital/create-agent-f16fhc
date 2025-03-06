"""
Authentication routes for the Freight Price Movement Agent API.

This module defines RESTful endpoints for user authentication, token management,
session handling, and password operations following OAuth 2.0 standards.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Body, Security

from .controllers import (
    login, logout, refresh_token, revoke_token, get_current_user,
    change_password, request_password_reset, confirm_password_reset,
    get_session_info, terminate_current_session, terminate_other_sessions,
    get_user_info
)
from .schemas import (
    LoginRequest, RefreshTokenRequest, RevokeTokenRequest,
    PasswordChangeRequest, PasswordResetRequest, PasswordResetConfirm,
    TokenResponse, SessionResponse
)
from ...models.user import User
from ...core.schemas import ErrorResponse
from ...core.logging import logger

# Create API router for authentication endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post('/login', status_code=status.HTTP_200_OK, response_model=TokenResponse)
def login_route(
    request_data: LoginRequest, 
    request: Request,
    response: Response
):
    """
    Authenticate a user and issue JWT tokens.

    Args:
        request_data: Login request data
        request: FastAPI request object
        response: FastAPI response object to set cookies

    Returns:
        Authentication response with tokens
    """
    try:
        # Log login attempt with masked username for security
        username_masked = f"{request_data.username[:2]}***" if len(request_data.username) > 2 else "***"
        logger.info(f"Login attempt for user: {username_masked}")
        
        # Call login controller
        auth_response = login(request_data, request, response)
        return auth_response
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Authentication failed", "errors": str(e)}
        )


@router.post('/logout', status_code=status.HTTP_200_OK)
@router.get('/logout', status_code=status.HTTP_200_OK)
def logout_route(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """
    Logout a user and invalidate their tokens.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        current_user: Currently authenticated user

    Returns:
        Success message
    """
    try:
        logger.info(f"Logout for user: {current_user.username}")
        result = logout(request, response, current_user)
        return result
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Logout failed", "errors": str(e)}
        )


@router.post('/refresh', status_code=status.HTTP_200_OK, response_model=TokenResponse)
def refresh_token_route(
    request_data: RefreshTokenRequest,
    request: Request,
    response: Response
):
    """
    Refresh an access token using a refresh token.

    Args:
        request_data: Refresh token request data
        request: FastAPI request object
        response: FastAPI response object

    Returns:
        New token response
    """
    try:
        logger.info("Token refresh request")
        new_token = refresh_token(request_data, request, response)
        return new_token
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Token refresh failed", "errors": str(e)}
        )


@router.post('/revoke', status_code=status.HTTP_200_OK)
def revoke_token_route(
    request_data: RevokeTokenRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Revoke a specific token.

    Args:
        request_data: Token revocation request data
        current_user: Currently authenticated user

    Returns:
        Success message
    """
    try:
        logger.info(f"Token revocation request for user: {current_user.username}")
        result = revoke_token(request_data, current_user)
        return result
    except Exception as e:
        logger.error(f"Token revocation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Token revocation failed", "errors": str(e)}
        )


@router.get('/me', status_code=status.HTTP_200_OK)
def get_user_info_route(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user.

    Args:
        current_user: Currently authenticated user

    Returns:
        User information
    """
    try:
        logger.info(f"User info request for user: {current_user.username}")
        user_info = get_user_info(current_user)
        return user_info
    except Exception as e:
        logger.error(f"Get user info failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve user information", "errors": str(e)}
        )


@router.post('/password/change', status_code=status.HTTP_200_OK)
def change_password_route(
    request_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Change the password for the authenticated user.

    Args:
        request_data: Password change request data
        current_user: Currently authenticated user

    Returns:
        Success message
    """
    try:
        logger.info(f"Password change request for user: {current_user.username}")
        result = change_password(request_data, current_user)
        return result
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password change failed", "errors": str(e)}
        )


@router.post('/password/reset/request', status_code=status.HTTP_200_OK)
def request_password_reset_route(
    request_data: PasswordResetRequest
):
    """
    Request a password reset link.

    Args:
        request_data: Password reset request data

    Returns:
        Success message
    """
    try:
        # Log without email for privacy
        logger.info("Password reset request received")
        result = request_password_reset(request_data)
        return result
    except Exception as e:
        # Always return success to prevent user enumeration, but log the error
        logger.error(f"Password reset request failed: {str(e)}", exc_info=True)
        return {"message": "If your email is registered, you will receive password reset instructions"}


@router.post('/password/reset/confirm', status_code=status.HTTP_200_OK)
def confirm_password_reset_route(
    request_data: PasswordResetConfirm
):
    """
    Confirm a password reset with a token.

    Args:
        request_data: Password reset confirmation data

    Returns:
        Success message
    """
    try:
        logger.info("Password reset confirmation request")
        result = confirm_password_reset(request_data)
        return result
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password reset failed", "errors": str(e)}
        )


@router.get('/session', status_code=status.HTTP_200_OK, response_model=SessionResponse)
def get_session_info_route(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the current session.

    Args:
        request: FastAPI request object
        current_user: Currently authenticated user

    Returns:
        Session information
    """
    try:
        logger.info(f"Session info request for user: {current_user.username}")
        session_info = get_session_info(request, current_user)
        return session_info
    except Exception as e:
        logger.error(f"Get session info failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Failed to retrieve session information", "errors": str(e)}
        )


@router.post('/session/terminate', status_code=status.HTTP_200_OK)
def terminate_current_session_route(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """
    Terminate the current user session.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        current_user: Currently authenticated user

    Returns:
        Success message
    """
    try:
        logger.info(f"Session termination request for user: {current_user.username}")
        result = terminate_current_session(request, response, current_user)
        return result
    except Exception as e:
        logger.error(f"Session termination failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to terminate session", "errors": str(e)}
        )


@router.post('/session/terminate-others', status_code=status.HTTP_200_OK)
def terminate_other_sessions_route(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Terminate all other sessions for the authenticated user.

    Args:
        request: FastAPI request object
        current_user: Currently authenticated user

    Returns:
        Success message with count of terminated sessions
    """
    try:
        logger.info(f"Request to terminate other sessions for user: {current_user.username}")
        result = terminate_other_sessions(request, current_user)
        return result
    except Exception as e:
        logger.error(f"Other sessions termination failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to terminate other sessions", "errors": str(e)}
        )