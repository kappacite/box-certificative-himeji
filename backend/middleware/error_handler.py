from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register global error handlers for the Flask application.

    Ensures all exceptions return the standardized JSON envelope:
    {
        "status": "error",
        "message": "...",
        "code": "..."
    }

    Args:
        app: The Flask application instance.
    """

    @app.errorhandler(Exception)
    def handle_exception(e):
        # 1. Custom domain exceptions (e.g. NotFoundException, UnauthorizedException)
        if hasattr(e, "status_code") and hasattr(e, "code"):
            response = jsonify(
                {"status": "error", "message": str(e), "code": getattr(e, "code")}
            )
            response.status_code = e.status_code
            return response

        # 2. Flask/Werkzeug built-in HTTP Exceptions (e.g. 405 Method Not Allowed)
        if isinstance(e, HTTPException):
            response = jsonify(
                {
                    "status": "error",
                    "message": e.description,
                    "code": e.name.upper().replace(" ", "_"),
                }
            )
            response.status_code = e.code
            return response

        # 3. Catch-all for unhandled server errors (500)
        app.logger.error(f"Unhandled exception occurred: {str(e)}", exc_info=True)
        response = jsonify(
            {
                "status": "error",
                "message": "An unexpected internal server error occurred",
                "code": "INTERNAL_SERVER_ERROR",
            }
        )
        response.status_code = 500
        return response
