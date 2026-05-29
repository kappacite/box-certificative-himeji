from flask import Blueprint, request, jsonify, g
from services.place_service import PlaceService
from middleware.auth_middleware import require_auth, require_owner, optional_auth
from exceptions import ValidationException, UnauthorizedException

place_bp = Blueprint("places", __name__, url_prefix="/api/places")
place_service = PlaceService()


@place_bp.route("", methods=["GET"])
@optional_auth
def get_places():
    """Retrieve places with filters and pagination."""
    visibility = request.args.get("visibility")
    q = request.args.get("q")
    try:
        page = int(request.args.get("page", 1))
        limit_val = request.args.get("limit")
        limit = int(limit_val) if limit_val is not None else None
    except ValueError:
        raise ValidationException("Invalid page or limit parameter")

    # If requesting private (or default) places, require auth
    if visibility != "public":
        if not g.current_user:
            raise UnauthorizedException("Authentication required")
        owner_id = g.current_user.id
    else:
        owner_id = None

    places = place_service.get_places(
        owner_id=owner_id, visibility=visibility, q=q, page=page, limit=limit
    )
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
    lat = place_service.parse_coordinate(latitude, "latitude")
    lon = place_service.parse_coordinate(longitude, "longitude")

    place = place_service.create_place(name, g.current_user.id, lat, lon, visibility)
    return jsonify({"status": "success", "data": {"place": place.to_dict()}}), 201


@place_bp.route("/search", methods=["GET"])
def search_place():
    """Geocode a place name without persisting it."""
    q = request.args.get("q")
    if not q or not q.strip():
        raise ValidationException("Query parameter 'q' is required")
    lat, lon = place_service.geocode_place_name(q)
    return (
        jsonify({"status": "success", "data": {"latitude": lat, "longitude": lon}}),
        200,
    )


@place_bp.route("/geocode", methods=["POST"])
def geocode_place():
    """Geocode a place name without persisting it."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name or not name.strip():
        raise ValidationException("Place name is required")
    lat, lon = place_service.geocode_place_name(name)
    return (
        jsonify({"status": "success", "data": {"latitude": lat, "longitude": lon}}),
        200,
    )


@place_bp.route("/public", methods=["GET"])
def get_public_places():
    """Retrieve all public places with optional search and pagination."""
    q = request.args.get("q")
    try:
        page = int(request.args.get("page", 1))
        limit_val = request.args.get("limit")
        limit = int(limit_val) if limit_val is not None else None
    except ValueError:
        raise ValidationException("Invalid page or limit parameter")

    places = place_service.get_places(
        owner_id=None, visibility="public", q=q, page=page, limit=limit
    )
    return (
        jsonify(
            {"status": "success", "data": {"places": [p.to_dict() for p in places]}}
        ),
        200,
    )


@place_bp.route("/public/<int:place_id>", methods=["GET"])
def get_public_place(place_id):

    place = place_service.get_public_place_by_id(place_id)
    return jsonify({"status": "success", "data": {"place": place.to_dict()}}), 200


@place_bp.route("/<int:place_id>", methods=["GET"])
@optional_auth
def get_place(place_id):
    """Retrieve a specific place."""
    owner_id = g.current_user.id if g.current_user else None
    place = place_service.get_place_by_id(place_id, owner_id)
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

    lat = place_service.parse_coordinate(latitude, "latitude")
    lon = place_service.parse_coordinate(longitude, "longitude")

    place = place_service.update_place(
        place_id, name, g.current_user.id, lat, lon, visibility
    )
    return jsonify({"status": "success", "data": {"place": place.to_dict()}}), 200


@place_bp.route("/<int:place_id>", methods=["PATCH"])
@require_auth
@require_owner("place")
def patch_place(place_id):
    """Partially update a specific place."""
    data = request.get_json(silent=True) or {}

    update_name = "name" in data
    update_coords = "latitude" in data or "longitude" in data
    update_visibility = "visibility" in data

    name = data.get("name")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    visibility = data.get("visibility")

    lat = None
    lon = None
    if update_coords:
        lat = place_service.parse_coordinate(latitude, "latitude")
        lon = place_service.parse_coordinate(longitude, "longitude")

    place = place_service.patch_place(
        place_id=place_id,
        owner_id=g.current_user.id,
        name=name,
        latitude=lat,
        longitude=lon,
        visibility=visibility,
        update_name=update_name,
        update_coords=update_coords,
        update_visibility=update_visibility,
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
