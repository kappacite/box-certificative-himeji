from flask import Blueprint, request, jsonify, g
from services.auth_service import AuthService
from middleware.auth_middleware import require_auth

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
auth_service = AuthService()


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user.

    Expects:
        JSON body with username, email, and password.

    Returns:
        Standard envelope with registered User.
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    user = auth_service.register(username, email, password)
    return jsonify({"status": "success", "data": {"user": user.to_dict()}}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Log in a user.

    Expects:
        JSON body with email and password.

    Returns:
        Standard envelope with JWT token and User.
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    token, user = auth_service.login(email, password)
    return (
        jsonify(
            {"status": "success", "data": {"token": token, "user": user.to_dict()}}
        ),
        200,
    )


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    """Log out the current user and blacklist their JWT."""
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            from dao.models import RevokedTokenModel
            from dao.database import db
            exists = RevokedTokenModel.query.filter_by(token=token).first()
            if not exists:
                revoked = RevokedTokenModel(token=token)
                db.session.add(revoked)
                db.session.commit()

    return (
        jsonify({"status": "success", "data": {"message": "Logged out successfully"}}),
        200,
    )


@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_current_user():
    """Retrieve the profile of the currently authenticated user."""
    return jsonify({"status": "success", "data": {"user": g.current_user.to_dict()}}), 200
