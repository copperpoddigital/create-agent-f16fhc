"""
Authentication module for the Freight Price Movement Agent API.

This module provides a comprehensive OAuth 2.0 based authentication framework
with JWT token support, secure session management, and user authentication.
It implements features for token issuance, validation, refresh, and revocation,
as well as password management and session control.

The module is designed to meet enterprise security standards with proper
token handling, secure password policies, and comprehensive session tracking
to protect sensitive freight pricing data.
"""

# Import authentication router
from .routes import router

# Import authentication controllers
from .controllers import (
    login, 
    logout, 
    refresh_token, 
    revoke_token, 
    get_current_user,
    change_password, 
    request_password_reset, 
    confirm_password_reset,
    get_session_info, 
    terminate_current_session, 
    terminate_other_sessions,
    get_user_info
)

# Import token type constants
from .models import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    TOKEN_TYPE_RESET
)

# Export all components
__all__ = [
    'router',
    'login',
    'logout',
    'refresh_token',
    'revoke_token',
    'get_current_user',
    'change_password',
    'request_password_reset',
    'confirm_password_reset',
    'get_session_info',
    'terminate_current_session',
    'terminate_other_sessions',
    'get_user_info',
    'TOKEN_TYPE_ACCESS',
    'TOKEN_TYPE_REFRESH',
    'TOKEN_TYPE_RESET'
]