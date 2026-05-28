from functools import wraps
from flask import request, g
from services.auth_service import AuthService
from exceptions.auth_exceptions import UnauthorizedException


def require_auth(f):
    """Decorator to require valid JWT authentication.

    Decodes the token from the Authorization header and stores the
    authenticated User in flask.g.current_user.

    Args:
        f: The function to decorate.

    Returns:
        The decorated function.

    Raises:
        UnauthorizedException: If the authorization header is missing or invalid.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise UnauthorizedException("Authorization header is missing")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise UnauthorizedException("Authorization header must be Bearer token")

        token = parts[1]
        auth_service = AuthService()
        # verify_token will raise TokenExpiredException or InvalidTokenException if invalid
        g.current_user = auth_service.verify_token(token)

        return f(*args, **kwargs)

    return decorated


def require_owner(resource_type: str):
    """Decorator to check that the current authenticated user owns the requested resource.

    Args:
        resource_type: The type of resource to check ('place' or 'tour').

    Returns:
        The decorator function.

    Raises:
        UnauthorizedException: If user is not authenticated.
        NotFoundException: If the resource does not exist.
        ForbiddenException: If the user is not the owner of the resource.
    """

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = getattr(g, "current_user", None)
            if not current_user:
                raise UnauthorizedException("Authentication required")

            if resource_type == "place":
                place_id = kwargs.get("place_id")
                if place_id is not None:
                    from services.place_service import PlaceService

                    place_service = PlaceService()
                    # get_place_by_id raises NotFoundException/ForbiddenException if check fails
                    place_service.get_place_by_id(place_id, current_user.id)

            elif resource_type == "tour":
                tour_id = kwargs.get("tour_id")
                if tour_id is not None:
                    from services.tour_service import TourService

                    tour_service = TourService()
                    # get_tour_by_id raises NotFoundException/ForbiddenException if check fails
                    tour_service.get_tour_by_id(tour_id, current_user.id)

            return f(*args, **kwargs)

        return decorated

    return decorator
