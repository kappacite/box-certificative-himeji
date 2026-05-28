class NotFoundException(Exception):
    """Exception raised when a resource is not found (404)."""

    status_code = 404
    code = "NOT_FOUND"

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
        self.message = message


class ValidationException(Exception):
    """Exception raised when input validation fails (400)."""

    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)
        self.message = message


class ConflictException(Exception):
    """Exception raised when there is a resource conflict, like duplicate user (409)."""

    status_code = 409
    code = "CONFLICT"

    def __init__(self, message: str = "Resource conflict occurred"):
        super().__init__(message)
        self.message = message
