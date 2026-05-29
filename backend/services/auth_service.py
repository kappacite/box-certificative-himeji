import datetime
import os
from typing import Tuple
import bcrypt
import jwt

from dao.user_dao import UserDAO
from dao.revoked_token_dao import RevokedTokenDAO
from dataobject.user import User
from dataobject.revoked_token import RevokedToken
from exceptions.app_exceptions import ConflictException, ValidationException
from exceptions.auth_exceptions import (
    UnauthorizedException,
    TokenExpiredException,
    InvalidTokenException,
)


class AuthService:
    """Business logic service for user authentication and session management."""

    def __init__(
        self, user_dao: UserDAO = None, revoked_token_dao: RevokedTokenDAO = None
    ):
        self.user_dao = user_dao or UserDAO()
        self.revoked_token_dao = revoked_token_dao or RevokedTokenDAO()
        from flask import current_app

        try:
            self.secret_key = current_app.config.get("SECRET_KEY") or os.environ.get(
                "SECRET_KEY", "change_me_in_production_default"
            )
            self.token_expiry_hours = int(
                current_app.config.get("TOKEN_EXPIRY_HOURS")
                or os.environ.get("TOKEN_EXPIRY_HOURS", 24)
            )
        except (RuntimeError, ValueError, TypeError):
            self.secret_key = os.environ.get(
                "SECRET_KEY", "change_me_in_production_default"
            )
            self.token_expiry_hours = int(os.environ.get("TOKEN_EXPIRY_HOURS", 24))

    def register(self, username: str, email: str, password: str) -> User:
        """Register a new user.

        Args:
            username: The requested username.
            email: The requested email.
            password: The plaintext password.

        Returns:
            The registered User data object.

        Raises:
            ValidationException: If input validation fails.
            ConflictException: If the email or username is already taken.
        """
        if not username or not email or not password:
            raise ValidationException("Username, email, and password are required")

        if len(password) < 6:
            raise ValidationException("Password must be at least 6 characters long")

        if self.user_dao.get_by_email(email):
            raise ConflictException("Email is already registered")

        if self.user_dao.get_by_username(username):
            raise ConflictException("Username is already taken")

        # Hash password with bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        new_user = User(username=username, email=email, password_hash=password_hash)

        from dao.database import db

        user = self.user_dao.create(new_user)
        db.session.commit()
        return user

    def login(self, email: str, password: str) -> Tuple[str, User]:
        """Authenticate user credentials and generate a JWT.

        Args:
            email: The user's email.
            password: The user's password.

        Returns:
            A tuple of (jwt_token, User).

        Raises:
            UnauthorizedException: If email or password is incorrect.
        """
        if not email or not password:
            raise UnauthorizedException("Email and password are required")

        user = self.user_dao.get_by_email(email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        # Verify password
        try:
            is_correct = bcrypt.checkpw(
                password.encode("utf-8"), user.password_hash.encode("utf-8")
            )
        except ValueError:
            is_correct = False

        if not is_correct:
            raise UnauthorizedException("Invalid email or password")

        token = self.generate_token(user.id)
        return token, user

    def generate_token(self, user_id: int) -> str:
        """Generate a new JWT for the user ID.

        Args:
            user_id: The user ID to include in the payload.

        Returns:
            The encoded JWT string.
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=self.token_expiry_hours),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> User:
        """Verify the JWT token and return the corresponding User.

        Args:
            token: The bearer JWT token.

        Returns:
            The authenticated User data object.

        Raises:
            TokenExpiredException: If the token has expired.
            InvalidTokenException: If the token is invalid or user is not found.
        """
        if self.revoked_token_dao.get_by_token(token) is not None:
            raise UnauthorizedException("Token has been revoked")

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                raise InvalidTokenException("Invalid token payload")
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.InvalidTokenError:
            raise InvalidTokenException()

        user = self.user_dao.get_by_id(user_id)
        if not user:
            raise InvalidTokenException("Authenticated user not found")

        return user

    def logout(self, token: str) -> None:
        """Revoke a JWT token to log the user out.

        Args:
            token: The JWT token string.
        """
        if not token:
            return
        exists = self.revoked_token_dao.get_by_token(token)
        if not exists:
            revoked = RevokedToken(token=token)
            self.revoked_token_dao.create(revoked)
            from dao.database import db

            db.session.commit()
