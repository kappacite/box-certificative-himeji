import requests
from typing import List, Optional, Tuple
from dao.place_dao import PlaceDAO
from dataobject.place import Place
from exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException,
    UnauthorizedException,
)


class PlaceService:
    """Business logic service for managing Places and calling external Geocoding API."""

    def validate_coordinate_pair(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
        allow_both_missing: bool = True,
    ) -> None:
        """Ensure latitude and longitude are provided together when explicit."""
        both_missing = latitude is None and longitude is None
        if both_missing and allow_both_missing:
            return
        if latitude is None or longitude is None:
            raise ValidationException(
                "Latitude and longitude must be provided together."
            )

    def parse_coordinate(self, value, coord_name: str) -> Optional[float]:
        """Safely parse a coordinate to float and validate its valid geographical range.

        Args:
            value: The raw coordinate input.
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

    def __init__(self, place_dao: PlaceDAO = None):
        self.place_dao = place_dao or PlaceDAO()
        self.geocoding_url = "https://nominatim.openstreetmap.org/search"

    def get_places_by_owner(self, owner_id: int) -> List[Place]:
        """Retrieve all places belonging to an owner.

        Args:
            owner_id: The ID of the owner user.

        Returns:
            A list of Place data objects.
        """
        return self.place_dao.get_by_owner(owner_id)

    def get_places(
        self,
        owner_id: Optional[int] = None,
        visibility: Optional[str] = None,
        q: Optional[str] = None,
        page: int = 1,
        limit: Optional[int] = None,
    ) -> List[Place]:
        """Retrieve places with optional visibility filter, search query, and pagination.

        Args:
            owner_id: Optional owner user ID filter.
            visibility: Optional visibility filter.
            q: Optional search query.
            page: Page number for pagination.
            limit: Maximum number of places to retrieve.

        Returns:
            A list of Place data objects.
        """
        if visibility == "public":
            return self.place_dao.query_places(
                visibility="public", q=q, page=page, limit=limit
            )
        else:
            return self.place_dao.query_places(
                owner_id=owner_id, visibility=visibility, q=q, page=page, limit=limit
            )

    def get_place_by_id(self, place_id: int, owner_id: int) -> Place:
        """Retrieve a specific place by ID, verifying ownership.

        Args:
            place_id: The ID of the place.
            owner_id: The ID of the current user.

        Returns:
            The Place data object.

        Raises:
            NotFoundException: If the place does not exist.
            UnauthorizedException: If the user is unauthenticated and resource is private.
            ForbiddenException: If the place does not belong to the user.
        """
        place = self.place_dao.get_by_id(place_id)
        if not place:
            raise NotFoundException("Place not found")
        if place.owner_id != owner_id and place.visibility != "public":
            if owner_id is None:
                raise UnauthorizedException("Authentication required")
            raise ForbiddenException("You do not have access to this place")
        return place

    def create_place(
        self,
        name: str,
        owner_id: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        visibility: str = "private",
    ) -> Place:
        """Create a new place, optionally geocoding its name if coordinates are omitted.

        Args:
            name: The name of the place.
            owner_id: The ID of the owner.
            latitude: Optional latitude.
            longitude: Optional longitude.
            visibility: The sharing visibility ('private' or 'public').

        Returns:
            The created Place.

        Raises:
            ValidationException: If coordinates cannot be resolved or input is invalid.
        """
        if not name or not name.strip():
            raise ValidationException("Place name is required")
        if visibility not in ["private", "public"]:
            raise ValidationException("Visibility must be either 'private' or 'public'")

        self.validate_coordinate_pair(latitude, longitude)

        # Resolve coordinates via Nominatim if not provided
        if latitude is None and longitude is None:
            latitude, longitude = self.geocode_place_name(name)

        new_place = Place(
            name=name.strip(),
            latitude=latitude,
            longitude=longitude,
            owner_id=owner_id,
            visibility=visibility,
        )
        from dao.database import db
        place = self.place_dao.create(new_place)
        db.session.commit()
        return place

    def update_place(
        self,
        place_id: int,
        name: str,
        owner_id: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        visibility: Optional[str] = None,
    ) -> Place:
        """Update a place. Re-geocodes the name if it changes and coordinates are not provided.

        Args:
            place_id: The ID of the place.
            name: The updated name.
            owner_id: The ID of the current user.
            latitude: Optional updated latitude.
            longitude: Optional updated longitude.
            visibility: Optional updated visibility.

        Returns:
            The updated Place data object.

        Raises:
            NotFoundException: If the place does not exist.
            ForbiddenException: If the place does not belong to the user.
            ValidationException: If validation or geocoding fails.
        """
        # Ensure user owns the place before modifying it
        place = self.place_dao.get_by_id(place_id)
        if not place:
            raise NotFoundException("Place not found")
        if place.owner_id != owner_id:
            raise ForbiddenException("You do not own this place")

        if not name or not name.strip():
            raise ValidationException("Place name is required")
        if visibility is not None and visibility not in ["private", "public"]:
            raise ValidationException("Visibility must be either 'private' or 'public'")

        old_name = place.name
        place.name = name.strip()

        if visibility is not None:
            place.visibility = visibility

        self.validate_coordinate_pair(latitude, longitude)

        # If coordinates are explicitly given, use them
        if latitude is not None and longitude is not None:
            place.latitude = latitude
            place.longitude = longitude
        # If the name changed and coordinates were not provided, re-geocode
        elif place.name != old_name:
            lat, lon = self.geocode_place_name(place.name)
            place.latitude = lat
            place.longitude = lon

        from dao.database import db
        updated = self.place_dao.update(place)
        db.session.commit()
        return updated

    def patch_place(
        self,
        place_id: int,
        owner_id: int,
        name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        visibility: Optional[str] = None,
        update_name: bool = False,
        update_coords: bool = False,
        update_visibility: bool = False,
    ) -> Place:
        """Partially update a place.

        Args:
            place_id: The ID of the place.
            owner_id: The ID of the current user.
            name: Optional updated name.
            latitude: Optional updated latitude.
            longitude: Optional updated longitude.
            visibility: Optional updated visibility.
            update_name: True if name should be updated.
            update_coords: True if coordinates should be updated.
            update_visibility: True if visibility should be updated.

        Returns:
            The updated Place data object.

        Raises:
            NotFoundException: If the place does not exist.
            ForbiddenException: If the place does not belong to the user.
            ValidationException: If validation or geocoding fails.
        """
        place = self.place_dao.get_by_id(place_id)
        if not place:
            raise NotFoundException("Place not found")
        if place.owner_id != owner_id:
            raise ForbiddenException("You do not own this place")

        if update_name:
            if not name or not name.strip():
                raise ValidationException("Place name is required")
            old_name = place.name
            place.name = name.strip()
        else:
            old_name = place.name

        if update_visibility:
            if visibility not in ["private", "public"]:
                raise ValidationException(
                    "Visibility must be either 'private' or 'public'"
                )
            place.visibility = visibility

        if update_coords:
            self.validate_coordinate_pair(latitude, longitude, allow_both_missing=False)
            if latitude is not None and longitude is not None:
                place.latitude = latitude
                place.longitude = longitude
        elif update_name and place.name != old_name:
            # If name changed but coordinates were not explicitly updated, re-geocode
            lat, lon = self.geocode_place_name(place.name)
            place.latitude = lat
            place.longitude = lon

        from dao.database import db
        updated = self.place_dao.update(place)
        db.session.commit()
        return updated

    def delete_place(self, place_id: int, owner_id: int) -> bool:
        """Delete a place by ID, verifying ownership.

        Args:
            place_id: The ID of the place.
            owner_id: The ID of the current user.

        Returns:
            True if deletion was successful.
        """
        # Triggers ownership checks (only the owner can delete)
        place = self.place_dao.get_by_id(place_id)
        if not place:
            raise NotFoundException("Place not found")
        if place.owner_id != owner_id:
            raise ForbiddenException("You do not own this place")
        from dao.database import db
        deleted = self.place_dao.delete(place_id)
        db.session.commit()
        return deleted

    def get_public_places(self) -> List[Place]:
        """Retrieve all public places.

        Returns:
            A list of Place data objects.
        """
        return self.place_dao.get_public()

    def get_public_place_by_id(self, place_id: int) -> Place:
        """Retrieve a specific place by ID, verifying ownership.

        Args:
            place_id: The ID of the place.
            owner_id: The ID of the current user.

        Returns:
            The Place data object.

        Raises:
            NotFoundException: If the place does not exist.
            ForbiddenException: If the place does not belong to the user.
        """
        place = self.place_dao.get_by_id(place_id)
        if not place:
            raise NotFoundException("Place not found")
        if place.visibility != "public":
            raise ForbiddenException("You do not have access to this place")
        return place

    def geocode_place_name(self, name: str) -> Tuple[float, float]:
        """Call OpenStreetMap Nominatim API to resolve a name to coordinates.

        Args:
            name: The search query (place name).

        Returns:
            A tuple of (latitude, longitude) as floats.

        Raises:
            ValidationException: If Nominatim cannot resolve the place.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        params = {"q": name, "format": "json", "limit": 1}
        try:
            session = requests.Session()
            session.trust_env = False
            response = session.get(
                self.geocoding_url, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise ValidationException(f"Failed to contact geocoding service: {str(e)}")

        if not data or not isinstance(data, list):
            raise ValidationException(
                f"Could not resolve coordinates for place name: '{name}'"
            )

        try:
            result = data[0]
            lat = float(result["lat"])
            lon = float(result["lon"])
            return lat, lon
        except (KeyError, ValueError, IndexError):
            raise ValidationException(
                f"Invalid geocoding response format for place: '{name}'"
            )
