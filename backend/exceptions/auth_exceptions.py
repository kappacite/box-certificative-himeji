class UnauthorizedException(Exception):
    """Exception raised when a user is not authorized (401)."""

    status_code = 401
    code = "UNAUTHORIZED"

    def __init__(self, message: str = "Invalid credentials or missing token"):
        super().__init__(message)
        self.message = message


class ForbiddenException(Exception):
    """Exception raised when a user does not have permission (403)."""

    status_code = 403
    code = "FORBIDDEN"

    def __init__(
        self, message: str = "You do not have permission to access this resource"
    ):
        super().__init__(message)
        self.message = message


class TokenExpiredException(UnauthorizedException):
    """Exception raised when a JWT token has expired."""

    code = "TOKEN_EXPIRED"

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class InvalidTokenException(UnauthorizedException):
    """Exception raised when a JWT token is invalid."""

    code = "INVALID_TOKEN"

    def __init__(self, message: str = "Token is invalid"):
        super().__init__(message)
