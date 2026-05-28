from flask import Blueprint, request, jsonify, g
from services.place_service import PlaceService
from middleware.auth_middleware import require_auth, require_owner
from exceptions.app_exceptions import ValidationException

place_bp = Blueprint("places", __name__, url_prefix="/api/places")
place_service = PlaceService()


def parse_coordinate(value, coord_name):
    """Safely parse a coordinate to float and validate its valid geographical range.

    Args:
        value: The raw coordinate input (from JSON).
        coord_name: Either 'latitude' or 'longitude'.

    Returns:
        The float value, or None if empty.

    Raises:
        ValidationException: If parsing fails or coordinate is out of bounds.
    """
    if value is None or value == "":
        return None
    try:
        val = float(value)
    except (ValueError, TypeError):
        raise ValidationException(f"Invalid {coord_name} format. Must be a number.")

    if coord_name == "latitude" and not (-90.0 <= val <= 90.0):
        raise ValidationException("Latitude must be between -90 and 90 degrees.")
    if coord_name == "longitude" and not (-180.0 <= val <= 180.0):
        raise ValidationException("Longitude must be between -180 and 180 degrees.")

    return val


@place_bp.route("", methods=["GET"])
@require_auth
def get_places():
    """Retrieve all places owned by the authenticated user."""
    places = place_service.get_places_by_owner(g.current_user.id)
    return (
        jsonify(
            {"status": "success", "data": {"places": [p.to_dict() for p in places]}}
        ),
        200,
    )


@place_bp.route("", methods=["POST"])
@require_auth
def create_place():
    """Create a new place. Resolves coordinates via Nominatim if not provided."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    visibility = data.get("visibility", "private")

    # If coordinates are passed as empty strings, convert to None
    lat = parse_coordinate(latitude, "latitude")
    lon = parse_coordinate(longitude, "longitude")

    place = place_service.create_place(name, g.current_user.id, lat, lon, visibility)
    return jsonify({"status": "success", "data": {"place": place.to_dict()}}), 201


@place_bp.route("/public", methods=["GET"])
def get_public_places():
    """Retrieve all public places."""
    places = place_service.get_public_places()
    return jsonify(
            {"status": "success", "data": {"places": [p.to_dict() for p in places]}}
        ), 200


@place_bp.route("/public/<int:place_id>", methods=["GET"])
def get_public_place(place_id):

    place = place_service.get_public_place_by_id(place_id)
    return jsonify({"status": "success", "data": {"place": place.to_dict()}}), 200


@place_bp.route("/<int:place_id>", methods=["GET"])
@require_auth
@require_owner("place")
def get_place(place_id):
    """Retrieve a specific place."""
    place = place_service.get_place_by_id(place_id, g.current_user.id)
    return jsonify({"status": "success", "data": {"place": place.to_dict()}}), 200


@place_bp.route("/<int:place_id>", methods=["PUT"])
@require_auth
@require_owner("place")
def update_place(place_id):
    """Update a specific place."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    visibility = data.get("visibility")

    lat = parse_coordinate(latitude, "latitude")
    lon = parse_coordinate(longitude, "longitude")

    place = place_service.update_place(
        place_id, name, g.current_user.id, lat, lon, visibility
    )
    return jsonify({"status": "success", "data": {"place": place.to_dict()}}), 200


@place_bp.route("/<int:place_id>", methods=["DELETE"])
@require_auth
@require_owner("place")
def delete_place(place_id):
    """Delete a specific place."""
    place_service.delete_place(place_id, g.current_user.id)
    # According to rules, successful update/delete with no body is 204
    return "", 204
