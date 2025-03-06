import pytest  # version ^7.0.0
import json  # version: stdlib

from fastapi.testclient import TestClient  # version ^0.95.0
from sqlalchemy.orm import Session  # version ^1.4.40

from ..conftest import db_session, client, test_user, auth_headers  # Internal fixtures
from ...models.user import User  # User model
from ...api.auth.models import Token, Session, TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH  # Auth models


def test_login_success(client: TestClient, test_user: User, db_session: Session) -> None:
    """Tests successful user login with valid credentials"""
    # Create login data with valid username and password
    login_data = {"username": test_user.username, "password": "testpassword"}

    # Send POST request to /auth/login endpoint
    response = client.post("/auth/login", json=login_data)

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains access_token, refresh_token, and token_type
    assert "access_token" in response_json
    assert "refresh_token" in response_json
    assert "token_type" in response_json

    # Assert token_type is 'bearer'
    assert response_json["token_type"] == "bearer"

    # Verify tokens are stored in the database
    access_token = db_session.query(Token).filter(Token.token == response_json["access_token"]).first()
    refresh_token = db_session.query(Token).filter(Token.token == response_json["refresh_token"]).first()
    assert access_token is not None
    assert refresh_token is not None


def test_login_invalid_credentials(client: TestClient) -> None:
    """Tests login failure with invalid credentials"""
    # Create login data with invalid username and password
    login_data = {"username": "invaliduser", "password": "invalidpassword"}

    # Send POST request to /auth/login endpoint
    response = client.post("/auth/login", json=login_data)

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about invalid credentials
    assert "message" in response_json
    assert "Invalid username or password" in response_json["message"]


def test_login_inactive_user(client: TestClient, test_user: User, db_session: Session) -> None:
    """Tests login failure with inactive user account"""
    # Set test_user.is_active to False
    test_user.is_active = False
    db_session.commit()

    # Create login data with valid username and password
    login_data = {"username": test_user.username, "password": "testpassword"}

    # Send POST request to /auth/login endpoint
    response = client.post("/auth/login", json=login_data)

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about inactive account
    assert "message" in response_json
    assert "User account is inactive" in response_json["message"]

    # Reset test_user.is_active to True for other tests
    test_user.is_active = True
    db_session.commit()


def test_login_locked_account(client: TestClient, test_user: User, db_session: Session) -> None:
    """Tests login failure with locked user account"""
    # Set test_user.is_locked to True
    test_user.is_locked = True
    db_session.commit()

    # Create login data with valid username and password
    login_data = {"username": test_user.username, "password": "testpassword"}

    # Send POST request to /auth/login endpoint
    response = client.post("/auth/login", json=login_data)

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about locked account
    assert "message" in response_json
    assert "Account is locked" in response_json["message"]

    # Reset test_user.is_locked to False for other tests
    test_user.is_locked = False
    db_session.commit()


def test_logout(client: TestClient, auth_headers: dict, db_session: Session) -> None:
    """Tests user logout functionality"""
    # Send POST request to /auth/logout endpoint with auth_headers
    response = client.post("/auth/logout", headers=auth_headers)

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains success message
    assert "message" in response_json
    assert "Successfully logged out" in response_json["message"]

    # Verify tokens are revoked in the database
    # Extract access token from auth_headers
    access_token = auth_headers["Authorization"].replace("Bearer ", "")
    token = db_session.query(Token).filter(Token.token == access_token).first()
    assert token is not None
    assert token.is_valid is False


def test_refresh_token(client: TestClient, test_user: User, db_session: Session) -> None:
    """Tests token refresh functionality"""
    # Login to get initial tokens
    login_data = {"username": test_user.username, "password": "testpassword"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    login_json = login_response.json()
    refresh_token = login_json["refresh_token"]

    # Create refresh token request data
    refresh_data = {"refresh_token": refresh_token}

    # Send POST request to /auth/refresh endpoint
    response = client.post("/auth/refresh", json=refresh_data)

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains new access_token and refresh_token
    assert "access_token" in response_json
    assert "refresh_token" in response_json

    # Verify old refresh token is revoked in database
    old_token = db_session.query(Token).filter(Token.token == refresh_token).first()
    assert old_token is not None
    assert old_token.is_valid is False

    # Verify new tokens are stored in database
    new_access_token = db_session.query(Token).filter(Token.token == response_json["access_token"]).first()
    new_refresh_token = db_session.query(Token).filter(Token.token == response_json["refresh_token"]).first()
    assert new_access_token is not None
    assert new_refresh_token is not None


def test_refresh_token_invalid(client: TestClient) -> None:
    """Tests token refresh failure with invalid refresh token"""
    # Create refresh token request with invalid token
    refresh_data = {"refresh_token": "invalid_refresh_token"}

    # Send POST request to /auth/refresh endpoint
    response = client.post("/auth/refresh", json=refresh_data)

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about invalid token
    assert "message" in response_json
    assert "Invalid or expired refresh token" in response_json["message"]


def test_revoke_token(client: TestClient, auth_headers: dict, db_session: Session) -> None:
    """Tests token revocation functionality"""
    # Login to get tokens
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    login_json = login_response.json()
    access_token = login_json["access_token"]

    # Create token revocation request data
    revoke_data = {"token": access_token, "token_type": TOKEN_TYPE_ACCESS}

    # Send POST request to /auth/revoke endpoint with auth_headers
    response = client.post("/auth/revoke", headers=auth_headers, json=revoke_data)

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains success message
    assert "message" in response_json
    assert "Token successfully revoked" in response_json["message"]

    # Verify token is revoked in database
    token = db_session.query(Token).filter(Token.token == access_token).first()
    assert token is not None
    assert token.is_valid is False


def test_get_user_info(client: TestClient, auth_headers: dict, test_user: User) -> None:
    """Tests retrieving current user information"""
    # Send GET request to /auth/me endpoint with auth_headers
    response = client.get("/auth/me", headers=auth_headers)

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains user information matching test_user
    assert "username" in response_json
    assert response_json["username"] == test_user.username
    assert "email" in response_json
    assert response_json["email"] == test_user.email

    # Verify sensitive information like password_hash is not included
    assert "password_hash" not in response_json


def test_change_password(client: TestClient, auth_headers: dict, test_user: User, db_session: Session) -> None:
    """Tests password change functionality"""
    # Create password change request data with current and new password
    change_data = {"current_password": "testpassword", "new_password": "newpassword123!", "confirm_password": "newpassword123!"}

    # Send POST request to /auth/password/change endpoint with auth_headers
    response = client.post("/auth/password/change", headers=auth_headers, json=change_data)

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains success message
    assert "message" in response_json
    assert "Password successfully changed" in response_json["message"]

    # Verify password is updated in database
    db_user = db_session.query(User).filter(User.id == test_user.id).first()
    assert db_user is not None
    assert db_user.check_password("newpassword123!") is True

    # Try to login with new password to confirm it works
    login_data = {"username": test_user.username, "password": "newpassword123!"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    # Reset password to original for other tests
    db_user.set_password("testpassword")
    db_session.commit()


def test_change_password_invalid_current(client: TestClient, auth_headers: dict) -> None:
    """Tests password change failure with invalid current password"""
    # Create password change request data with invalid current password
    change_data = {"current_password": "wrongpassword", "new_password": "newpassword123!", "confirm_password": "newpassword123!"}

    # Send POST request to /auth/password/change endpoint with auth_headers
    response = client.post("/auth/password/change", headers=auth_headers, json=change_data)

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about invalid current password
    assert "message" in response_json
    assert "Current password is incorrect" in response_json["message"]


def test_request_password_reset(client: TestClient, test_user: User, db_session: Session) -> None:
    """Tests password reset request functionality"""
    # Create password reset request data with valid email
    reset_data = {"email": test_user.email}

    # Send POST request to /auth/password/reset/request endpoint
    response = client.post("/auth/password/reset/request", json=reset_data)

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains success message
    assert "message" in response_json
    assert "If your email is registered, you will receive password reset instructions" in response_json["message"]

    # Verify reset token is created in database
    # TODO: Implement token verification


def test_confirm_password_reset(client: TestClient, test_user: User, db_session: Session) -> None:
    """Tests password reset confirmation functionality"""
    from ...api.auth.utils import generate_password_reset_token

    # Generate password reset token for test_user
    reset_token = generate_password_reset_token(test_user.id)

    # Create password reset confirmation data with token and new password
    confirm_data = {"token": reset_token, "new_password": "newpassword123!", "confirm_password": "newpassword123!"}

    # Send POST request to /auth/password/reset/confirm endpoint
    response = client.post("/auth/password/reset/confirm", json=confirm_data)

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains success message
    assert "message" in response_json
    assert "Password successfully reset" in response_json["message"]

    # Verify password is updated in database
    db_user = db_session.query(User).filter(User.id == test_user.id).first()
    assert db_user is not None
    assert db_user.check_password("newpassword123!") is True

    # Verify reset token is marked as used
    # TODO: Implement token verification

    # Try to login with new password to confirm it works
    login_data = {"username": test_user.username, "password": "newpassword123!"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    # Reset password to original for other tests
    db_user.set_password("testpassword")
    db_session.commit()


def test_confirm_password_reset_invalid_token(client: TestClient) -> None:
    """Tests password reset confirmation failure with invalid token"""
    # Create password reset confirmation data with invalid token
    confirm_data = {"token": "invalid_reset_token", "new_password": "newpassword123!", "confirm_password": "newpassword123!"}

    # Send POST request to /auth/password/reset/confirm endpoint
    response = client.post("/auth/password/reset/confirm", json=confirm_data)

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about invalid token
    assert "message" in response_json
    assert "Invalid or expired password reset token" in response_json["message"]


def test_get_session_info(client: TestClient, auth_headers: dict, db_session: Session) -> None:
    """Tests retrieving current session information"""
    # Login to create a session
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    login_json = login_response.json()
    session_id = login_json["session_id"]

    # Send GET request to /auth/session endpoint with auth_headers and session cookie
    response = client.get("/auth/session", headers=auth_headers, cookies={"session_id": session_id})

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains session information
    assert "data" in response_json
    assert "session_id" in response_json["data"]
    assert "user_id" in response_json["data"]

    # Verify session ID matches the one in the cookie
    assert response_json["data"]["session_id"] == session_id


def test_terminate_current_session(client: TestClient, auth_headers: dict, db_session: Session) -> None:
    """Tests terminating the current user session"""
    # Login to create a session
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    login_json = login_response.json()
    session_id = login_json["session_id"]

    # Send POST request to /auth/session/terminate endpoint with auth_headers and session cookie
    response = client.post("/auth/session/terminate", headers=auth_headers, cookies={"session_id": session_id})

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains success message
    assert "message" in response_json
    assert "Session successfully terminated" in response_json["message"]

    # Verify session is terminated in database
    session = db_session.query(Session).filter(Session.session_id == session_id).first()
    assert session is not None
    assert session.is_active is False


def test_terminate_other_sessions(client: TestClient, auth_headers: dict, test_user: User, db_session: Session) -> None:
    """Tests terminating all other user sessions"""
    from ...api.auth.utils import create_user_session

    # Create multiple sessions for test_user
    session1 = create_user_session(test_user.id, ip_address="127.0.0.1", user_agent="TestAgent1")
    session2 = create_user_session(test_user.id, ip_address="127.0.0.2", user_agent="TestAgent2")

    # Login to create a current session
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    login_json = login_response.json()
    session_id = login_json["session_id"]

    # Send POST request to /auth/session/terminate-others endpoint with auth_headers and session cookie
    response = client.post("/auth/session/terminate-others", headers=auth_headers, cookies={"session_id": session_id})

    # Assert response status code is 200
    assert response.status_code == 200

    # Parse response JSON
    response_json = response.json()

    # Assert response contains success message with count of terminated sessions
    assert "message" in response_json
    assert "Successfully terminated" in response_json["message"]
    assert "count" in response_json
    assert response_json["count"] == 2

    # Verify other sessions are terminated in database
    db_session1 = db_session.query(Session).filter(Session.session_id == session1.session_id).first()
    db_session2 = db_session.query(Session).filter(Session.session_id == session2.session_id).first()
    assert db_session1 is not None
    assert db_session1.is_active is False
    assert db_session2 is not None
    assert db_session2.is_active is False

    # Verify current session is still active
    current_session = db_session.query(Session).filter(Session.session_id == session_id).first()
    assert current_session is not None
    assert current_session.is_active is True


def test_unauthorized_access(client: TestClient) -> None:
    """Tests API endpoints requiring authentication reject unauthorized requests"""
    # Send GET request to /auth/me endpoint without auth headers
    response = client.get("/auth/me")

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about missing or invalid token
    assert "message" in response_json
    assert "Authentication required" in response_json["message"]

    # Test other protected endpoints to verify they also require authentication
    # TODO: Add tests for other protected endpoints


def test_invalid_token_access(client: TestClient) -> None:
    """Tests API endpoints reject requests with invalid tokens"""
    # Create headers with invalid token
    headers = {"Authorization": "Bearer invalid_token"}

    # Send GET request to /auth/me endpoint with invalid token headers
    response = client.get("/auth/me", headers=headers)

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about invalid token
    assert "message" in response_json
    assert "Invalid authentication token" in response_json["message"]


def test_account_lockout(client: TestClient, test_user: User, db_session: Session) -> None:
    """Tests account lockout after multiple failed login attempts"""
    # Create login data with valid username but wrong password
    login_data = {"username": test_user.username, "password": "wrongpassword"}

    # Send POST request to /auth/login endpoint multiple times (5+)
    for _ in range(6):
        response = client.post("/auth/login", json=login_data)

    # Verify account becomes locked after maximum attempts
    db_user = db_session.query(User).filter(User.id == test_user.id).first()
    assert db_user is not None
    assert db_user.is_locked is True

    # Try to login with correct credentials
    login_data = {"username": test_user.username, "password": "testpassword"}
    response = client.post("/auth/login", json=login_data)

    # Assert response status code is 401
    assert response.status_code == 401

    # Parse response JSON
    response_json = response.json()

    # Assert response contains error message about locked account
    assert "message" in response_json
    assert "Account is locked" in response_json["message"]

    # Reset account lock status for other tests
    db_user.unlock_account()
    db_session.commit()