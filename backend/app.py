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
    with app.app_context():
        if config_name != "production":
            db.create_all()
        run_auto_migrations(app)

    return app


def run_auto_migrations(app) -> None:
    """Checks the database schema and applies missing columns or constraints automatically."""
    from sqlalchemy import text
    from dao import db

    with app.app_context():
        # Check if the database has tables at all (specifically tours)
        try:
            db.session.execute(text("SELECT 1 FROM tours LIMIT 1"))
        except Exception:
            db.session.rollback()
            # If the tables don't exist, they will be created by db.create_all()
            return

        # 1. Check tours.max_distance
        try:
            db.session.execute(text("SELECT max_distance FROM tours LIMIT 1"))
        except Exception:
            db.session.rollback()
            print("[*] Auto-migration: Adding max_distance column to tours table...")
            db.session.execute(
                text("ALTER TABLE tours ADD COLUMN max_distance FLOAT NOT NULL DEFAULT 100.0")
            )
            db.session.commit()

        # 2. Check places.city
        try:
            db.session.execute(text("SELECT city FROM places LIMIT 1"))
        except Exception:
            db.session.rollback()
            print("[*] Auto-migration: Adding city column to places table...")
            db.session.execute(text("ALTER TABLE places ADD COLUMN city VARCHAR(100)"))
            db.session.commit()

        # 3. Check tour_places primary key (SQLite specific migration)
        is_sqlite = "sqlite" in str(db.engine.url)
        if is_sqlite:
            try:
                # Query sqlite_master to inspect DDL
                sql_row = db.session.execute(
                    text("SELECT sql FROM sqlite_master WHERE type='table' AND name='tour_places'")
                ).fetchone()
                if sql_row:
                    create_sql = sql_row[0]
                    if (
                        "PRIMARY KEY (tour_id, place_id)" in create_sql
                        or "PRIMARY KEY(tour_id, place_id)" in create_sql
                    ):
                        print(
                            "[*] Auto-migration: Recreating tour_places table to use (tour_id, position) as PRIMARY KEY..."
                        )

                        # Check if is_hotel exists
                        try:
                            db.session.execute(
                                text("SELECT is_hotel FROM tour_places LIMIT 1")
                            )
                            has_is_hotel = True
                        except Exception:
                            db.session.rollback()
                            has_is_hotel = False

                        # Rename old table
                        db.session.execute(
                            text("ALTER TABLE tour_places RENAME TO tour_places_old")
                        )

                        # Create new table with correct schema
                        db.session.execute(
                            text("""
                            CREATE TABLE tour_places (
                                tour_id INTEGER NOT NULL,
                                place_id INTEGER NOT NULL,
                                position INTEGER NOT NULL,
                                locked BOOLEAN NOT NULL DEFAULT 0,
                                is_hotel BOOLEAN NOT NULL DEFAULT 0,
                                PRIMARY KEY (tour_id, position),
                                FOREIGN KEY(tour_id) REFERENCES tours (id) ON DELETE CASCADE,
                                FOREIGN KEY(place_id) REFERENCES places (id) ON DELETE CASCADE
                            )
                        """)
                        )

                        # Copy data
                        if has_is_hotel:
                            db.session.execute(
                                text("""
                                INSERT INTO tour_places (tour_id, place_id, position, locked, is_hotel)
                                SELECT tour_id, place_id, position, locked, is_hotel FROM tour_places_old
                            """)
                            )
                        else:
                            db.session.execute(
                                text("""
                                INSERT INTO tour_places (tour_id, place_id, position, locked, is_hotel)
                                SELECT tour_id, place_id, position, locked, 0 FROM tour_places_old
                            """)
                            )

                        # Drop old table
                        db.session.execute(text("DROP TABLE tour_places_old"))
                        db.session.commit()
                        print("[+] Auto-migration: tour_places table successfully migrated!")
            except Exception as e:
                db.session.rollback()
                print(f"[-] Auto-migration: Failed to migrate tour_places table: {e}")


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
