from flask import Blueprint, request, jsonify, g
from services.tour_service import TourService
from middleware.auth_middleware import require_auth, require_owner

from exceptions.app_exceptions import ValidationException

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

    tour = tour_service.create_tour(name, place_ids, g.current_user.id, visibility)
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
    places = data.get("places")
    name = data.get("name")

    if 'name' in data:
        if not (name and name.strip()):
            raise ValidationException("Name cannot be empty.")

    if 'visibility' in data:
        if visibility not in ["private", "public"]:
            raise ValidationException("Invalid visibility value.")

    tour = tour_service.patch_tour(
        tour_id=tour_id,
        visibility=visibility,
        places=places,
        name=name,
        owner_id=g.current_user.id
    )
    return jsonify({"status": "success", "data": {"tour": tour.to_dict()}}), 200


@tour_bp.route("/<int:tour_id>/share", methods=["PATCH"])
@require_auth
@require_owner("tour")
def share_tour(tour_id):
    """Toggle visibility (public/private) for a tour."""
    data = request.get_json(silent=True) or {}
    visibility = data.get("visibility")

    tour = tour_service.get_tour_by_id(tour_id, g.current_user.id)

    if visibility is None:
        new_visibility = "private" if tour.visibility == "public" else "public"
    else:
        if visibility not in ["private", "public"]:
            raise ValidationException("Visibility must be either 'private' or 'public'")
        new_visibility = visibility

    tour = tour_service.patch_tour(
        tour_id=tour_id,
        visibility=new_visibility,
        places=None,
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
