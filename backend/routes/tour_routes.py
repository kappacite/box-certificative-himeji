from flask import Blueprint, request, jsonify, g
from services.tour_service import TourService
from middleware.auth_middleware import require_auth, require_owner


tour_bp = Blueprint("tours", __name__, url_prefix="/api/tours")
tour_service = TourService()


@tour_bp.route("", methods=["GET"])
@require_auth
def get_tours():
    """Retrieve all tours owned by the authenticated user."""
    tours = tour_service.get_tours_by_owner(g.current_user.id)
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

    tour = tour_service.create_tour(
        name=name,
        place_ids=place_ids,
        owner_id=g.current_user.id,
        visibility=visibility,
        locked_positions=locked_positions,
        locked_places=locked_places,
    )
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 201


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

    tour = tour_service.patch_tour(
        tour_id=tour_id,
        visibility=visibility,
        places_id=places_id,
        name=name,
        owner_id=g.current_user.id,
        locked_positions=locked_positions,
        locked_places=locked_places,
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
        owner_id=g.current_user.id
    )
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 200


@tour_bp.route("/public", methods=["GET"])
def get_public_tours():
    """Retrieve all public tours. No authentication required."""
    tours = tour_service.get_public_tours()
    return (
        jsonify({"status": "success", "data": {"tours": [t.to_dict() for t in tours]}}),
        200,
    )


@tour_bp.route("/shared/<string:share_token>", methods=["GET"])
def get_shared_tour(share_token):
    """Retrieve a public tour by share token. No authentication required."""
    tour = tour_service.get_shared_tour(share_token)
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 200
