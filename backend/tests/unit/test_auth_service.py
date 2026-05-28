import pytest
from services.auth_service import AuthService
from exceptions.app_exceptions import ConflictException
from exceptions.auth_exceptions import UnauthorizedException


def test_auth_register_success(app):
    """Test successful user registration."""
    with app.app_context():
        service = AuthService()
        user = service.register("testuser", "test@example.com", "securepassword123")

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash != "securepassword123"  # Must be hashed!


def test_auth_register_duplicate(app):
    """Test duplicate registration error."""
    with app.app_context():
        service = AuthService()
        service.register("testuser", "test@example.com", "securepassword123")

        # Duplicate username
        with pytest.raises(ConflictException):
            service.register("testuser", "different@example.com", "password")

        # Duplicate email
        with pytest.raises(ConflictException):
            service.register("different", "test@example.com", "password")


def test_auth_login_success(app):
    """Test successful login and token validation."""
    with app.app_context():
        service = AuthService()
        service.register("testuser", "test@example.com", "securepassword")

        token, user = service.login("test@example.com", "securepassword")
        assert token is not None
        assert user.username == "testuser"

        # Verify generated token resolves back to user
        verified_user = service.verify_token(token)
        assert verified_user.id == user.id
        assert verified_user.username == "testuser"


def test_auth_login_invalid_password(app):
    """Test login failure with invalid password."""
    with app.app_context():
        service = AuthService()
        service.register("testuser", "test@example.com", "securepassword")

        with pytest.raises(UnauthorizedException):
            service.login("test@example.com", "wrongpassword")
