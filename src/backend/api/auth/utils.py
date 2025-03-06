"""
Utility functions for authentication and security in the Freight Price Movement Agent.

This module provides helper functions for token management, session handling,
password operations, and security monitoring.
"""

from datetime import datetime, timedelta
import uuid
from typing import Optional, Dict, Any

import sqlalchemy

from ...core.db import session
from ...models.user import User
from .models import (
    Token, Session, FailedLoginAttempt, PasswordResetToken,
    TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH, TOKEN_TYPE_RESET,
    MAX_FAILED_ATTEMPTS, LOCKOUT_DURATION_MINUTES
)
from .schemas import TokenData
from ...core.config import settings
from ...models.audit_log import AuditLog
from ...core.security import (
    verify_password as core_verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_token
)
from ...core.exceptions import AuthenticationException

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1

def verify_password(plain_password: str, user: User) -> bool:
    """
    Verifies a plain password against a user's stored password hash.
    
    Args:
        plain_password: Plain password to verify
        user: User object with password_hash
        
    Returns:
        True if password matches, False otherwise
    """
    return core_verify_password(plain_password, user.password_hash)

def store_token(token_string: str, token_type: str, user_id: str, expires_at: datetime) -> Token:
    """
    Stores a token in the database.
    
    Args:
        token_string: Token string to store
        token_type: Type of token (access, refresh, reset)
        user_id: ID of the user associated with the token
        expires_at: Expiration datetime for the token
        
    Returns:
        Created Token object
    """
    token = Token(
        token=token_string,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires_at
    )
    session.add(token)
    session.commit()
    return token

def revoke_token(token_string: str, reason: Optional[str] = None) -> bool:
    """
    Revokes a token in the database.
    
    Args:
        token_string: Token string to revoke
        reason: Optional reason for revocation
        
    Returns:
        True if token was found and revoked, False otherwise
    """
    token = session.query(Token).filter(Token.token == token_string).first()
    if token:
        token.revoke(reason)
        session.commit()
        return True
    return False

def is_token_valid(token_string: str, token_type: Optional[str] = None) -> bool:
    """
    Checks if a token is valid in the database.
    
    Args:
        token_string: Token string to check
        token_type: Optional token type to filter by
        
    Returns:
        True if token is valid, False otherwise
    """
    query = session.query(Token).filter(Token.token == token_string)
    if token_type:
        query = query.filter(Token.token_type == token_type)
    
    token = query.first()
    if token:
        return token.is_valid
    return False

def create_user_session(user_id: str, ip_address: Optional[str] = None, 
                       user_agent: Optional[str] = None) -> Session:
    """
    Creates a new user session.
    
    Args:
        user_id: ID of the user for the session
        ip_address: Optional IP address of the client
        user_agent: Optional user agent string of the client
        
    Returns:
        Created Session object
    """
    session_id = str(uuid.uuid4())
    user_session = Session(
        session_id=session_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    session.add(user_session)
    session.commit()
    return user_session

def validate_session(session_id: str) -> Optional[Session]:
    """
    Validates a user session.
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        Session object if valid, None otherwise
    """
    user_session = session.query(Session).filter(Session.session_id == session_id).first()
    if user_session and user_session.is_valid():
        return user_session
    return None

def update_session_activity(session_id: str) -> bool:
    """
    Updates the last activity timestamp of a session.
    
    Args:
        session_id: Session ID to update
        
    Returns:
        True if session was found and updated, False otherwise
    """
    user_session = session.query(Session).filter(Session.session_id == session_id).first()
    if user_session:
        user_session.update_activity()
        session.commit()
        return True
    return False

def terminate_session(session_id: str) -> bool:
    """
    Terminates a user session.
    
    Args:
        session_id: Session ID to terminate
        
    Returns:
        True if session was found and terminated, False otherwise
    """
    user_session = session.query(Session).filter(Session.session_id == session_id).first()
    if user_session:
        user_session.terminate()
        session.commit()
        return True
    return False

def terminate_all_user_sessions(user_id: str, current_session_id: Optional[str] = None) -> int:
    """
    Terminates all sessions for a user except the current one.
    
    Args:
        user_id: User ID whose sessions to terminate
        current_session_id: Optional current session ID to exclude from termination
        
    Returns:
        Number of terminated sessions
    """
    query = session.query(Session).filter(
        Session.user_id == user_id,
        Session.is_active == True
    )
    
    if current_session_id:
        query = query.filter(Session.session_id != current_session_id)
    
    sessions_to_terminate = query.all()
    terminated_count = 0
    
    for user_session in sessions_to_terminate:
        user_session.terminate()
        terminated_count += 1
    
    if terminated_count > 0:
        session.commit()
    
    return terminated_count

def record_failed_login(username: str, ip_address: Optional[str] = None) -> FailedLoginAttempt:
    """
    Records a failed login attempt.
    
    Args:
        username: Username that failed login
        ip_address: Optional IP address of the client
        
    Returns:
        Created FailedLoginAttempt object
    """
    attempt = FailedLoginAttempt(
        username=username,
        ip_address=ip_address
    )
    session.add(attempt)
    
    # Update user failed_login_attempts count if user exists
    user = session.query(User).filter(User.username == username).first()
    if user:
        user.increment_failed_login()
    
    session.commit()
    return attempt

def check_account_lockout(username: str) -> bool:
    """
    Checks if an account is locked due to too many failed login attempts.
    
    Args:
        username: Username to check
        
    Returns:
        True if account is locked, False otherwise
    """
    user = session.query(User).filter(User.username == username).first()
    
    # If user exists, check if account is locked
    if user:
        if user.is_locked:
            # Check if lockout duration has passed
            lockout_time = datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            latest_attempt = session.query(FailedLoginAttempt)\
                .filter(FailedLoginAttempt.username == username)\
                .order_by(FailedLoginAttempt.attempt_time.desc())\
                .first()
            
            if latest_attempt and latest_attempt.attempt_time < lockout_time:
                # Lockout duration has passed, unlock the account
                user.unlock_account()
                session.commit()
                return False
            
            return True  # Account is still locked
    
    # If user not found, check recent failed login attempts
    lockout_time = datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    recent_attempts = session.query(FailedLoginAttempt)\
        .filter(
            FailedLoginAttempt.username == username,
            FailedLoginAttempt.attempt_time >= lockout_time,
            FailedLoginAttempt.resolved == False
        )\
        .count()
    
    return recent_attempts >= MAX_FAILED_ATTEMPTS

def resolve_failed_attempts(username: str) -> int:
    """
    Resolves failed login attempts for a username.
    
    Args:
        username: Username to resolve attempts for
        
    Returns:
        Number of resolved attempts
    """
    attempts = session.query(FailedLoginAttempt)\
        .filter(
            FailedLoginAttempt.username == username,
            FailedLoginAttempt.resolved == False
        )\
        .all()
    
    resolved_count = 0
    for attempt in attempts:
        attempt.resolve()
        resolved_count += 1
    
    if resolved_count > 0:
        session.commit()
    
    # Reset user failed_login_attempts if user exists
    user = session.query(User).filter(User.username == username).first()
    if user:
        user.reset_failed_login_attempts()
        if user.is_locked:
            user.unlock_account()
        session.commit()
    
    return resolved_count

def generate_password_reset_token(user_id: str) -> PasswordResetToken:
    """
    Generates a password reset token for a user.
    
    Args:
        user_id: User ID to generate token for
        
    Returns:
        Created password reset token object
    """
    # Generate a secure random token
    token = generate_secure_token()
    
    # Create token in database with expiry in 1 hour
    reset_token = PasswordResetToken(
        token=token,
        user_id=user_id,
        expiry_hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS
    )
    
    session.add(reset_token)
    session.commit()
    return reset_token

def verify_password_reset_token(token_string: str) -> Optional[PasswordResetToken]:
    """
    Verifies a password reset token.
    
    Args:
        token_string: Token string to verify
        
    Returns:
        Token object if valid, None otherwise
    """
    reset_token = session.query(PasswordResetToken)\
        .filter(PasswordResetToken.token == token_string)\
        .first()
    
    if reset_token and reset_token.is_valid():
        return reset_token
    return None

def create_audit_log(user_id: str, action: str, details: Dict, 
                    ip_address: Optional[str] = None) -> AuditLog:
    """
    Creates an audit log entry.
    
    Args:
        user_id: User ID performing the action
        action: Action being performed
        details: Dictionary containing additional details
        ip_address: Optional IP address of the client
        
    Returns:
        Created audit log object
    """
    from ...models.audit_log import ActionType
    
    # Convert string action to ActionType enum
    try:
        action_type = ActionType[action.upper()]
    except KeyError:
        action_type = ActionType.CONFIGURATION  # Default if not matching
    
    audit_log = AuditLog(
        action=action_type,
        resource_type="auth",
        resource_id=None,  # No specific resource ID for general auth actions
        user_id=user_id,
        ip_address=ip_address,
        details=details
    )
    
    session.add(audit_log)
    session.commit()
    return audit_log

def get_user_by_username(username: str) -> Optional[User]:
    """
    Retrieves a user by username.
    
    Args:
        username: Username to search for
        
    Returns:
        User object if found, None otherwise
    """
    return session.query(User).filter(User.username == username).first()

def get_user_by_email(email: str) -> Optional[User]:
    """
    Retrieves a user by email.
    
    Args:
        email: Email to search for
        
    Returns:
        User object if found, None otherwise
    """
    return session.query(User).filter(User.email == email).first()

def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Retrieves a user by ID.
    
    Args:
        user_id: User ID to search for
        
    Returns:
        User object if found, None otherwise
    """
    return session.query(User).filter(User.id == user_id).first()