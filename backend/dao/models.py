from dao.database import db


class UserModel(db.Model):
    """SQLAlchemy model for users table."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationships
    places = db.relationship(
        "PlaceModel", backref="owner", cascade="all, delete-orphan", lazy=True
    )
    tours = db.relationship(
        "TourModel", backref="owner", cascade="all, delete-orphan", lazy=True
    )


class PlaceModel(db.Model):
    """SQLAlchemy model for places table."""

    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    visibility = db.Column(db.String(20), nullable=False, default="private")


class TourPlaceModel(db.Model):
    """Association model linking tours and places with ordering."""

    __tablename__ = "tour_places"

    tour_id = db.Column(
        db.Integer, db.ForeignKey("tours.id", ondelete="CASCADE"), primary_key=True
    )
    place_id = db.Column(
        db.Integer, db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False
    )
    position = db.Column(db.Integer, primary_key=True)
    locked = db.Column(db.Boolean, nullable=False, default=False)
    is_hotel = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship to access the Place entity directly
    place = db.relationship("PlaceModel", lazy="joined")


class TourModel(db.Model):
    """SQLAlchemy model for tours table."""

    __tablename__ = "tours"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    total_distance = db.Column(db.Float, nullable=False, default=0.0)
    visibility = db.Column(db.String(20), nullable=False, default="private")
    share_token = db.Column(db.String(36), unique=True, nullable=True)
    max_distance = db.Column(db.Float, nullable=False, default=100.0)

    # Ordered list of places via TourPlaceModel association
    tour_places = db.relationship(
        "TourPlaceModel",
        backref="tour",
        cascade="all, delete-orphan",
        order_by="TourPlaceModel.position",
        lazy="select",
    )


class RevokedTokenModel(db.Model):
    """SQLAlchemy model for blacklisted JWTs (revoked on logout)."""

    __tablename__ = "revoked_tokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False, index=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
