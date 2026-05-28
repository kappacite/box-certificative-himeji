import datetime
import os
from typing import Tuple
import bcrypt
import jwt

from dao.user_dao import UserDAO
from dataobject.user import User
from exceptions.app_exceptions import ConflictException, ValidationException
from exceptions.auth_exceptions import (
    UnauthorizedException,
    TokenExpiredException,
    InvalidTokenException,
)


class AuthService:
    """Business logic service for user authentication and session management."""

    def __init__(self, user_dao: UserDAO = None):
        self.user_dao = user_dao or UserDAO()
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

        return self.user_dao.create(new_user)

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
