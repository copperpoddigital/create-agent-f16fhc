import pytest  # version ^7.0.0
from datetime import datetime, timedelta  # standard library
import uuid  # standard library

from ...models import User  # Import User model for testing
from ...models.enums import UserRole  # Import user role enumeration for testing role-based functionality
from .conftest import db_session  # Import database session fixture for testing


def test_user_creation(db_session):
    """Tests that a user can be created with the correct attributes"""
    # Create a new User instance with test data
    user = User(
        username="testuser",
        email="test@example.com",
        password="testpassword",
        first_name="Test",
        last_name="User",
        role=UserRole.ANALYST
    )

    # Add the user to the database session
    db_session.add(user)

    # Commit the session
    db_session.commit()

    # Query the user from the database
    retrieved_user = db_session.query(User).filter_by(username="testuser").first()

    # Assert that the user attributes match the expected values
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.first_name == "Test"
    assert retrieved_user.last_name == "User"
    assert retrieved_user.role == UserRole.ANALYST

    # Assert that the user has a UUID primary key
    assert isinstance(retrieved_user.id, str)
    assert uuid.UUID(retrieved_user.id)

    # Assert that created_at and updated_at timestamps are set
    assert retrieved_user.created_at is not None
    assert retrieved_user.updated_at is not None


def test_password_hashing():
    """Tests that passwords are properly hashed and can be verified"""
    # Create a new User instance
    user = User(username="testuser", email="test@example.com", password="testpassword")

    # Set a password using set_password method
    user.set_password("testpassword")

    # Assert that the password_hash attribute is not equal to the original password
    assert user.password_hash != "testpassword"

    # Assert that check_password returns True for the correct password
    assert user.check_password("testpassword") is True

    # Assert that check_password returns False for an incorrect password
    assert user.check_password("wrongpassword") is False


def test_user_roles():
    """Tests that user roles are correctly assigned and permissions work as expected"""
    # Create users with different roles (ADMIN, MANAGER, ANALYST, VIEWER)
    admin_user = User(username="admin", email="admin@example.com", password="password", role=UserRole.ADMIN)
    manager_user = User(username="manager", email="manager@example.com", password="password", role=UserRole.MANAGER)
    analyst_user = User(username="analyst", email="analyst@example.com", password="password", role=UserRole.ANALYST)
    viewer_user = User(username="viewer", email="viewer@example.com", password="password", role=UserRole.VIEWER)

    # Test that ADMIN has all permissions
    assert admin_user.has_permission("view") is True
    assert admin_user.has_permission("edit") is True
    assert admin_user.has_permission("create") is True
    assert admin_user.has_permission("delete") is True
    assert admin_user.has_permission("admin") is True

    # Test that MANAGER has appropriate permissions but not admin permissions
    assert manager_user.has_permission("view") is True
    assert manager_user.has_permission("edit") is True
    assert manager_user.has_permission("create") is True
    assert manager_user.has_permission("delete") is True
    assert manager_user.has_permission("admin") is False

    # Test that ANALYST has limited permissions
    assert analyst_user.has_permission("view") is True
    assert analyst_user.has_permission("edit") is True
    assert analyst_user.has_permission("create") is True
    assert analyst_user.has_permission("delete") is False
    assert analyst_user.has_permission("admin") is False

    # Test that VIEWER has only view permissions
    assert viewer_user.has_permission("view") is True
    assert viewer_user.has_permission("edit") is False
    assert viewer_user.has_permission("create") is False
    assert viewer_user.has_permission("delete") is False
    assert viewer_user.has_permission("admin") is False


def test_failed_login_attempts():
    """Tests that failed login attempts are tracked and account locking works"""
    # Create a new User instance
    user = User(username="testuser", email="test@example.com", password="testpassword")

    # Call increment_failed_login multiple times
    user.increment_failed_login()
    assert user.failed_login_attempts == 1
    user.increment_failed_login()
    user.increment_failed_login()
    user.increment_failed_login()
    user.increment_failed_login()

    # Assert that failed_login_attempts is incremented correctly
    assert user.failed_login_attempts == 5

    # Assert that the account is locked after 5 failed attempts
    assert user.is_locked is True

    # Call reset_failed_login_attempts
    user.reset_failed_login_attempts()

    # Assert that failed_login_attempts is reset to 0
    assert user.failed_login_attempts == 0
    assert user.is_locked is False


def test_account_locking():
    """Tests that accounts can be manually locked and unlocked"""
    # Create a new User instance
    user = User(username="testuser", email="test@example.com", password="testpassword")

    # Assert that is_locked is initially False
    assert user.is_locked is False

    # Call lock_account method
    user.lock_account()

    # Assert that is_locked is now True
    assert user.is_locked is True

    # Call unlock_account method
    user.unlock_account()

    # Assert that is_locked is False again
    assert user.is_locked is False

    # Assert that failed_login_attempts is reset to 0 after unlocking
    assert user.failed_login_attempts == 0


def test_account_activation():
    """Tests that accounts can be activated and deactivated"""
    # Create a new User instance
    user = User(username="testuser", email="test@example.com", password="testpassword")

    # Assert that is_active is initially True
    assert user.is_active is True

    # Call deactivate method
    user.deactivate()

    # Assert that is_active is now False
    assert user.is_active is False

    # Call activate method
    user.activate()

    # Assert that is_active is True again
    assert user.is_active is True


def test_last_login_update():
    """Tests that last login timestamp can be updated"""
    # Create a new User instance
    user = User(username="testuser", email="test@example.com", password="testpassword")

    # Assert that last_login is initially None
    assert user.last_login is None

    # Call update_last_login method
    user.update_last_login()

    # Assert that last_login is now set to a datetime value
    assert user.last_login is not None
    assert isinstance(user.last_login, datetime)

    # Store the current last_login value
    last_login_1 = user.last_login

    # Wait a short time
    import time
    time.sleep(0.1)

    # Call update_last_login again
    user.update_last_login()

    # Assert that last_login has been updated to a newer timestamp
    assert user.last_login > last_login_1


def test_user_preferences():
    """Tests that user preferences can be updated"""
    # Create a new User instance
    user = User(username="testuser", email="test@example.com", password="testpassword")

    # Assert that preferences is initially None
    assert user.preferences is None

    # Call update_preferences with a test preferences dictionary
    test_preferences = {"theme": "dark", "notifications": True}
    user.update_preferences(test_preferences)

    # Assert that preferences now contains the expected values
    assert user.preferences == test_preferences

    # Call update_preferences with additional preferences
    additional_preferences = {"language": "en", "date_format": "YYYY-MM-DD"}
    user.update_preferences(additional_preferences)

    # Assert that preferences contains both original and new values
    expected_preferences = {"theme": "dark", "notifications": True, "language": "en", "date_format": "YYYY-MM-DD"}
    assert user.preferences == expected_preferences

    # Call update_preferences with overlapping keys
    overlapping_preferences = {"theme": "light", "notifications": False}
    user.update_preferences(overlapping_preferences)

    # Assert that overlapping keys are updated with new values
    expected_preferences.update(overlapping_preferences)
    assert user.preferences == expected_preferences


def test_get_full_name():
    """Tests that get_full_name returns the correct value based on available name fields"""
    # Create a User with only username set
    user1 = User(username="testuser", email="test@example.com", password="testpassword")

    # Assert that get_full_name returns the username
    assert user1.get_full_name() == "testuser"

    # Set first_name only
    user1.first_name = "Test"

    # Assert that get_full_name returns the first_name
    assert user1.get_full_name() == "Test"

    # Set both first_name and last_name
    user1.last_name = "User"

    # Assert that get_full_name returns 'first_name last_name'
    assert user1.get_full_name() == "Test User"


def test_to_dict():
    """Tests that to_dict returns the correct dictionary representation of a user"""
    # Create a User with test data
    user = User(username="testuser", email="test@example.com", password="testpassword", first_name="Test", last_name="User")
    user.set_password("testpassword")

    # Call to_dict with include_sensitive=False
    user_dict = user.to_dict(include_sensitive=False)

    # Assert that the returned dictionary contains expected fields
    assert "id" in user_dict
    assert "username" in user_dict
    assert "email" in user_dict
    assert "first_name" in user_dict
    assert "last_name" in user_dict
    assert "role" in user_dict
    assert "is_active" in user_dict
    assert "is_locked" in user_dict
    assert "last_login" in user_dict
    assert "created_at" in user_dict
    assert "updated_at" in user_dict

    # Assert that sensitive fields like password_hash are not included
    assert "password_hash" not in user_dict
    assert "failed_login_attempts" not in user_dict
    assert "preferences" not in user_dict

    # Call to_dict with include_sensitive=True
    user_dict_sensitive = user.to_dict(include_sensitive=True)

    # Assert that sensitive fields are now included
    assert "password_hash" in user_dict_sensitive
    assert "failed_login_attempts" in user_dict_sensitive
    assert "preferences" in user_dict_sensitive