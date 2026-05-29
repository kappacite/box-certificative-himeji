from flask import Blueprint, request, jsonify, g
from services.tour_service import TourService
from middleware.auth_middleware import require_auth, require_owner
from exceptions import ValidationException

tour_bp = Blueprint("tours", __name__, url_prefix="/api/tours")
tour_service = TourService()


@tour_bp.route("", methods=["GET"])
@require_auth
def get_tours():
    """Retrieve all tours owned by the authenticated user with optional search/pagination."""
    q = request.args.get("q")
    try:
        page = int(request.args.get("page", 1))
        limit_val = request.args.get("limit")
        limit = int(limit_val) if limit_val is not None else None
    except ValueError:
        raise ValidationException("Invalid page or limit parameter")

    tours = tour_service.get_tours(
        owner_id=g.current_user.id, q=q, page=page, limit=limit
    )
    return (
        jsonify({"status": "success", "data": {"tours": [t.to_dict() for t in tours]}}),
        200,
    )


@tour_bp.route("", methods=["POST"])
@require_auth
def create_tour():
    """Generate and save an optimized tour from list of place IDs."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    place_ids = data.get("place_ids", [])
    visibility = data.get("visibility", "private")
    locked_positions = data.get("locked_positions")
    locked_places = data.get("locked_places")

    max_distance_val = data.get("max_distance")
    max_distance = 100.0
    if max_distance_val is not None:
        try:
            max_distance = float(max_distance_val)
        except (ValueError, TypeError):
            raise ValidationException("max_distance must be a number")

    tour = tour_service.create_tour(
        name=name,
        place_ids=place_ids,
        owner_id=g.current_user.id,
        visibility=visibility,
        locked_positions=locked_positions,
        locked_places=locked_places,
        max_distance=max_distance,
    )
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 201


@tour_bp.route("/preview", methods=["POST"])
@require_auth
def preview_tour():
    """Preview an optimized tour from place IDs without saving."""
    data = request.get_json(silent=True) or {}
    place_ids = data.get("place_ids", [])
    locked_positions = data.get("locked_positions")
    locked_places = data.get("locked_places")

    max_distance_val = data.get("max_distance")
    max_distance = 100.0
    if max_distance_val is not None:
        try:
            max_distance = float(max_distance_val)
        except (ValueError, TypeError):
            raise ValidationException("max_distance must be a number")

    tour = tour_service.preview_tour(
        place_ids=place_ids,
        owner_id=g.current_user.id,
        locked_positions=locked_positions,
        locked_places=locked_places,
        max_distance=max_distance,
    )
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 200


@tour_bp.route("/<int:tour_id>", methods=["GET"])
@require_auth
@require_owner("tour")
def get_tour(tour_id):
    """Retrieve a specific tour."""
    tour = tour_service.get_tour_by_id(tour_id, g.current_user.id)
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 200


@tour_bp.route("/<int:tour_id>", methods=["DELETE"])
@require_auth
@require_owner("tour")
def delete_tour(tour_id):
    """Delete a specific tour."""
    tour_service.delete_tour(tour_id, g.current_user.id)
    return "", 204


@tour_bp.route("/<int:tour_id>", methods=["PATCH"])
@require_auth
@require_owner("tour")
def patch_tour(tour_id):
    """Change attribute(s) for a tour."""
    data = request.get_json(silent=True) or {}

    visibility = data.get("visibility")
    places_id = data.get("places_id") or data.get("place_ids") or data.get("places")
    name = data.get("name")
    locked_positions = data.get("locked_positions")
    locked_places = data.get("locked_places")
    optimize = data.get("optimize", True)  # False → save order as-is, skip algorithm

    max_distance_val = data.get("max_distance")
    max_distance = None
    if max_distance_val is not None:
        try:
            max_distance = float(max_distance_val)
        except (ValueError, TypeError):
            raise ValidationException("max_distance must be a number")

    tour = tour_service.patch_tour(
        tour_id=tour_id,
        visibility=visibility,
        places_id=places_id,
        name=name,
        owner_id=g.current_user.id,
        locked_positions=locked_positions,
        locked_places=locked_places,
        max_distance=max_distance,
        optimize=optimize,
    )
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 200


@tour_bp.route("/<int:tour_id>/share", methods=["PATCH"])
@require_auth
@require_owner("tour")
def share_tour(tour_id):
    """Change visibility of a tour, supporting toggling if not specified."""
    data = request.get_json(silent=True) or {}
    visibility = data.get("visibility")

    tour = tour_service.get_tour_by_id(tour_id, g.current_user.id)
    if visibility is None:
        visibility = "public" if tour.visibility == "private" else "private"

    tour = tour_service.patch_tour(
        tour_id=tour_id,
        visibility=visibility,
        places_id=None,
        name=None,
        owner_id=g.current_user.id,
    )
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 200


@tour_bp.route("/public", methods=["GET"])
def get_public_tours():
    """Retrieve all public tours with optional search and pagination."""
    q = request.args.get("q")
    try:
        page = int(request.args.get("page", 1))
        limit_val = request.args.get("limit")
        limit = int(limit_val) if limit_val is not None else None
    except ValueError:
        raise ValidationException("Invalid page or limit parameter")

    tours = tour_service.get_public_tours(q=q, page=page, limit=limit)
    return (
        jsonify({"status": "success", "data": {"tours": [t.to_dict() for t in tours]}}),
        200,
    )


def serialize_public_tour(tour) -> dict:
    """Serialize a Tour data object for public access, hiding internal database IDs."""
    places = []
    for p in tour.places:
        places.append(
            {
                "name": p.name,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "visibility": p.visibility,
                "is_hotel": getattr(p, "is_hotel", False),
                "locked": getattr(p, "locked", False),
            }
        )
    return {
        "name": tour.name,
        "places": places,
        "total_distance": tour.total_distance,
        "visibility": tour.visibility,
        "share_token": tour.share_token,
        "max_distance": tour.max_distance,
    }


@tour_bp.route("/shared/<string:share_token>", methods=["GET"])
def get_shared_tour(share_token):
    """Retrieve a public tour by share token. No authentication required."""
    tour = tour_service.get_shared_tour(share_token)
    return (
        jsonify(
            {
                "status": "success",
                "data": {"tour": serialize_public_tour(tour)},
            }
        ),
        200,
    )


@tour_bp.route("/<int:tour_id>/recalculate", methods=["POST"])
@require_auth
@require_owner("tour")
def recalculate_tour(tour_id):
    """Recalculate distance and place order of a tour after place modifications."""
    tour = tour_service.recalculate_tour(tour_id, g.current_user.id)
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 200


@tour_bp.route("/<int:tour_id>/duplicate", methods=["POST"])
@require_auth
def duplicate_tour(tour_id):
    """Duplicate a public or owned tour into the current user's space."""
    tour = tour_service.duplicate_tour(tour_id, g.current_user.id)
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 201


@tour_bp.route("/optimize", methods=["POST"])
@require_auth
def optimize_tour():
    """Optimize a list of place IDs and return the sorted sequence and distance."""
    data = request.get_json(silent=True) or {}
    place_ids = data.get("place_ids", [])
    locked_positions = data.get("locked_positions")
    locked_places = data.get("locked_places")

    max_distance_val = data.get("max_distance")
    max_distance = 100.0
    if max_distance_val is not None:
        try:
            max_distance = float(max_distance_val)
        except (ValueError, TypeError):
            raise ValidationException("max_distance must be a number")

    result = tour_service.optimize_places(
        place_ids=place_ids,
        owner_id=g.current_user.id,
        locked_positions=locked_positions,
        locked_places=locked_places,
        max_distance=max_distance,
    )
    return jsonify({"status": "success", "data": result}), 200
