import os


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change_me_in_production_default")
    GEOCODING_API_URL = os.environ.get(
        "GEOCODING_API_URL", "https://nominatim.openstreetmap.org/search"
    )
    TOKEN_EXPIRY_HOURS = int(os.environ.get("TOKEN_EXPIRY_HOURS", 24))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")


class DevelopmentConfig(Config):
    """Development configuration."""

    # Read DATABASE_PATH from env, default to local dev file if not inside docker
    db_path = os.environ.get("DATABASE_PATH", "travel.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Production configuration."""

    # In production, we require SECRET_KEY to be set
    SECRET_KEY = os.environ.get("SECRET_KEY")
    db_path = os.environ.get("DATABASE_PATH", "/app/data/travel.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"


# Configuration registry
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
