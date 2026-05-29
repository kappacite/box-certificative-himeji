import os
from flask import Flask, jsonify
from flask_cors import CORS

from config import config_by_name
from dao import db
from middleware import register_error_handlers
from routes import auth_bp, place_bp, tour_bp


def create_app(config_name: str = None) -> Flask:
    """Application factory for the Flask REST API.

    Loads configuration based on APP_ENV, initializes dependencies,
    registers blueprints, and configures error handling/CORS.

    Args:
        config_name: Optional configuration name overrides.

    Returns:
        The configured Flask application.
    """
    app = Flask(__name__)

    # Load configuration
    if not config_name:
        config_name = os.environ.get("APP_ENV", "development")

    config_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_class)

    # Fail-fast check for SECRET_KEY in production mode
    if config_name == "production":
        secret_key = app.config.get("SECRET_KEY")
        if not secret_key or secret_key == "change_me_in_production_default":
            raise ValueError(
                "SECRET_KEY environment variable is REQUIRED and must be secure in production!"
            )

    # Initialize CORS
    cors_origins = app.config.get("CORS_ORIGINS", "*")
    if cors_origins == "*":
        CORS(app)
    else:
        CORS(app, origins=cors_origins)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(place_bp)
    app.register_blueprint(tour_bp)

    # Register global error handlers
    register_error_handlers(app)

    # Health check endpoint for Docker and monitoring
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return (
            jsonify({"status": "success", "data": {"message": "Service is healthy"}}),
            200,
        )

    # Health check endpoint verifying database readiness
    @app.route("/api/health/ready", methods=["GET"])
    def health_ready():
        """Health check verifying database connection availability."""
        try:
            from sqlalchemy import text

            db.session.execute(text("SELECT 1"))
            return (
                jsonify(
                    {
                        "status": "success",
                        "data": {"message": "Database and service are ready"},
                    }
                ),
                200,
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Database is not ready: {str(e)}",
                        "code": "DATABASE_ERROR",
                    }
                ),
                500,
            )

    # Ensure database tables exist (SQLite dev automatic migration helper)
    if config_name != "production":
        with app.app_context():
            db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
