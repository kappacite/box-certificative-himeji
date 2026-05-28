import uuid
from typing import List, Optional
from dao.tour_dao import TourDAO
from dao.place_dao import PlaceDAO
from dataobject.tour import Tour
from dataobject.place import Place
from services.algorithm import optimize, haversine
from exceptions import NotFoundException, ForbiddenException, ValidationException


class TourService:
    """Business logic service for managing Tours, computing distances, and sharing."""

    def __init__(self, tour_dao: TourDAO = None, place_dao: PlaceDAO = None):
        self.tour_dao = tour_dao or TourDAO()
        self.place_dao = place_dao or PlaceDAO()

    def get_tours_by_owner(self, owner_id: int) -> List[Tour]:
        """Retrieve all tours belonging to an owner.

        Args:
            owner_id: The ID of the owner.

        Returns:
            A list of Tour data objects.
        """
        return self.tour_dao.get_by_owner(owner_id)

    def get_tour_by_id(self, tour_id: int, owner_id: int) -> Tour:
        """Retrieve a specific tour by ID, verifying ownership.

        Args:
            tour_id: The ID of the tour.
            owner_id: The ID of the current user.

        Returns:
            The Tour data object.

        Raises:
            NotFoundException: If the tour does not exist.
            ForbiddenException: If the tour does not belong to the user.
        """
        tour = self.tour_dao.get_by_id(tour_id)
        if not tour:
            raise NotFoundException("Tour not found")
        if tour.owner_id != owner_id:
            raise ForbiddenException("You do not own this tour")
        return tour

    def create_tour(
        self,
        name: str,
        place_ids: List[int],
        owner_id: int,
        visibility: str = "private",
        locked_positions: dict = None,
        locked_places: list = None,
    ) -> Tour:
        """Generate an optimized tour from a list of place IDs, optionally locking some steps.

        Args:
            name: The name of the tour.
            place_ids: A list of place IDs (or dicts containing 'id' and
              optionally 'locked'/'position') to include.
            owner_id: The ID of the owner user.
            visibility: The sharing visibility ('private' or 'public').
            locked_positions: Dict mapping place_id (as str) to target position.
            locked_places: List of place_ids to lock at their input positions.

        Returns:
            The created and persisted Tour.

        Raises:
            ValidationException: If there are fewer than 2 places or validation fails.
            ForbiddenException: If the user doesn't own all specified places.
        """
        if not name or not name.strip():
            raise ValidationException("Tour name is required")
        if not place_ids or len(place_ids) < 2:
            raise ValidationException(
                "At least 2 places are required to generate a tour"
            )
        if visibility not in ["private", "public"]:
            raise ValidationException("Visibility must be either 'private' or 'public'")

        # Parse place_ids and locks
        parsed_place_ids = []
        locked_map = {}  # place_id -> position

        for index, item in enumerate(place_ids):
            if isinstance(item, dict):
                pid = item.get("id")
                if pid is not None:
                    parsed_place_ids.append(pid)
                    if item.get("locked") or item.get("position") is not None:
                        locked_map[pid] = item.get("position", index)
            else:
                try:
                    parsed_place_ids.append(int(item))
                except (ValueError, TypeError):
                    raise ValidationException("Invalid place ID format")

        # Merge separately passed locked_positions
        if locked_positions:
            for pid_str, pos in locked_positions.items():
                try:
                    pid = int(pid_str)
                    locked_map[pid] = int(pos)
                except (ValueError, TypeError):
                    raise ValidationException("Invalid locked_positions format")

        # Merge separately passed locked_places
        if locked_places:
            for pid in locked_places:
                try:
                    pid = int(pid)
                    if pid in parsed_place_ids:
                        locked_map[pid] = parsed_place_ids.index(pid)
                except (ValueError, TypeError):
                    raise ValidationException("Invalid locked_places format")

        # Retrieve and validate all places belong to the owner or are public
        places_by_id = {p.id: p for p in self.place_dao.get_by_ids(parsed_place_ids)}
        places = []
        for pid in parsed_place_ids:
            place = places_by_id.get(pid)
            if not place:
                raise ValidationException(f"Place with ID {pid} does not exist")
            if place.owner_id != owner_id and place.visibility != "public":
                raise ForbiddenException(
                    f"You do not own the place with ID {pid} and it is not public"
                )
            places.append(place)

        # Optimize the place ordering respecting locks
        optimized_places = optimize(places, locked_map)

        # Apply locked property on returned place objects
        for place in optimized_places:
            place.locked = (place.id in locked_map)

        # Calculate total distance (closed loop)
        total_dist = self.calculate_tour_distance(optimized_places)

        # Generate a share token
        share_token = str(uuid.uuid4())

        new_tour = Tour(
            name=name.strip(),
            owner_id=owner_id,
            places=optimized_places,
            total_distance=total_dist,
            visibility=visibility,
            share_token=share_token,
        )

        return self.tour_dao.create(new_tour)

    def preview_tour(
        self,
        place_ids: List[int],
        owner_id: int,
        locked_positions: dict = None,
        locked_places: list = None,
    ) -> Tour:
        """Generate an optimized tour preview without persisting it.

        Args:
            place_ids: A list of place IDs (or dicts) to include.
            owner_id: The ID of the owner user.
            locked_positions: Dict mapping place_id (as str) to target position.
            locked_places: List of place_ids to lock at their input positions.

        Returns:
            A transient (unsaved) Tour data object.

        Raises:
            ValidationException: If validation fails or too few places are provided.
            ForbiddenException: If the user doesn't own all specified places.
        """
        if not place_ids or len(place_ids) < 2:
            raise ValidationException(
                "At least 2 places are required to generate a tour"
            )

        # Parse place_ids and locks
        parsed_place_ids = []
        locked_map = {}  # place_id -> position

        for index, item in enumerate(place_ids):
            if isinstance(item, dict):
                pid = item.get("id")
                if pid is not None:
                    parsed_place_ids.append(pid)
                    if item.get("locked") or item.get("position") is not None:
                        locked_map[pid] = item.get("position", index)
            else:
                try:
                    parsed_place_ids.append(int(item))
                except (ValueError, TypeError):
                    raise ValidationException("Invalid place ID format")

        # Merge separately passed locked_positions
        if locked_positions:
            for pid_str, pos in locked_positions.items():
                try:
                    pid = int(pid_str)
                    locked_map[pid] = int(pos)
                except (ValueError, TypeError):
                    raise ValidationException("Invalid locked_positions format")

        # Merge separately passed locked_places
        if locked_places:
            for pid in locked_places:
                try:
                    pid = int(pid)
                    if pid in parsed_place_ids:
                        locked_map[pid] = parsed_place_ids.index(pid)
                except (ValueError, TypeError):
                    raise ValidationException("Invalid locked_places format")

        # Retrieve and validate all places belong to the owner or are public
        places_by_id = {p.id: p for p in self.place_dao.get_by_ids(parsed_place_ids)}
        places = []
        for pid in parsed_place_ids:
            place = places_by_id.get(pid)
            if not place:
                raise ValidationException(f"Place with ID {pid} does not exist")
            if place.owner_id != owner_id and place.visibility != "public":
                raise ForbiddenException(
                    f"You do not own the place with ID {pid} and it is not public"
                )
            places.append(place)

        # Optimize the place ordering respecting locks
        optimized_places = optimize(places, locked_map)

        # Apply locked property on returned place objects
        for place in optimized_places:
            place.locked = (place.id in locked_map)

        # Calculate total distance (closed loop)
        total_dist = self.calculate_tour_distance(optimized_places)

        # Return transient Tour data object (not persisted, id is None)
        return Tour(
            name="Preview",
            owner_id=owner_id,
            places=optimized_places,
            total_distance=total_dist,
            visibility="private",
            share_token="",
            id=None,
        )

    def optimize_places(
        self,
        place_ids: List[int],
        owner_id: int,
        locked_positions: dict = None,
        locked_places: list = None,
    ) -> dict:
        """Optimize place sequence according to coordinates and locked constraints.

        Args:
            place_ids: A list of place IDs (or dicts) to include.
            owner_id: The ID of the owner user.
            locked_positions: Dict mapping place_id (as str) to target position.
            locked_places: List of place_ids to lock at their input positions.

        Returns:
            A dictionary containing:
                - places: A list of dict representations of optimized Places.
                - total_distance: The total distance of the closed loop.

        Raises:
            ValidationException: If validation fails or too few places are provided.
            ForbiddenException: If the user doesn't own all specified places.
        """
        if not place_ids or len(place_ids) < 2:
            raise ValidationException(
                "At least 2 places are required to generate a tour"
            )

        # Parse place_ids and locks
        parsed_place_ids = []
        locked_map = {}  # place_id -> position

        for index, item in enumerate(place_ids):
            if isinstance(item, dict):
                pid = item.get("id")
                if pid is not None:
                    parsed_place_ids.append(pid)
                    if item.get("locked") or item.get("position") is not None:
                        locked_map[pid] = item.get("position", index)
            else:
                try:
                    parsed_place_ids.append(int(item))
                except (ValueError, TypeError):
                    raise ValidationException("Invalid place ID format")

        # Merge separately passed locked_positions
        if locked_positions:
            for pid_str, pos in locked_positions.items():
                try:
                    pid = int(pid_str)
                    locked_map[pid] = int(pos)
                except (ValueError, TypeError):
                    raise ValidationException("Invalid locked_positions format")

        # Merge separately passed locked_places
        if locked_places:
            for pid in locked_places:
                try:
                    pid = int(pid)
                    if pid in parsed_place_ids:
                        locked_map[pid] = parsed_place_ids.index(pid)
                except (ValueError, TypeError):
                    raise ValidationException("Invalid locked_places format")

        # Retrieve and validate all places belong to the owner or are public
        places_by_id = {p.id: p for p in self.place_dao.get_by_ids(parsed_place_ids)}
        places = []
        for pid in parsed_place_ids:
            place = places_by_id.get(pid)
            if not place:
                raise ValidationException(f"Place with ID {pid} does not exist")
            if place.owner_id != owner_id and place.visibility != "public":
                raise ForbiddenException(
                    f"You do not own the place with ID {pid} and it is not public"
                )
            places.append(place)

        # Optimize the place ordering respecting locks
        optimized_places = optimize(places, locked_map)

        # Apply locked property on returned place objects
        for place in optimized_places:
            place.locked = (place.id in locked_map)

        # Calculate total distance (closed loop)
        total_dist = self.calculate_tour_distance(optimized_places)

        return {
            "places": [p.to_dict() for p in optimized_places],
            "total_distance": total_dist,
        }

    def get_public_tours(
        self,
        q: Optional[str] = None,
        page: int = 1,
        limit: Optional[int] = None,
    ) -> List[Tour]:
        """Retrieve all public tours with optional search and pagination.

        Args:
            q: Optional search query.
            page: Page number.
            limit: Maximum number of tours to retrieve.

        Returns:
            A list of Tour data objects.
        """
        return self.tour_dao.query_tours(visibility="public", q=q, page=page, limit=limit)

    def get_tours(
        self,
        owner_id: int,
        q: Optional[str] = None,
        page: int = 1,
        limit: Optional[int] = None,
    ) -> List[Tour]:
        """Retrieve user tours with optional search and pagination.

        Args:
            owner_id: Owner user ID.
            q: Optional search query.
            page: Page number.
            limit: Maximum number of tours to retrieve.

        Returns:
            A list of Tour data objects.
        """
        return self.tour_dao.query_tours(owner_id=owner_id, q=q, page=page, limit=limit)

    def duplicate_tour(self, tour_id: int, owner_id: int) -> Tour:
        """Duplicate a tour (if public or owned) into the user's personal space.

        Args:
            tour_id: The ID of the tour to copy.
            owner_id: The user ID duplicating the tour.

        Returns:
            The newly created Tour data object.

        Raises:
            NotFoundException: If the tour doesn't exist.
            ForbiddenException: If the user cannot access the tour.
        """
        tour = self.tour_dao.get_by_id(tour_id)
        if not tour:
            raise NotFoundException("Tour not found")
        if tour.owner_id != owner_id and tour.visibility != "public":
            raise ForbiddenException("You do not have access to duplicate this tour")

        duplicated_places = []
        for place in tour.places:
            if place.owner_id == owner_id or place.visibility == "public":
                duplicated_places.append(place)
            else:
                cloned_place = Place(
                    name=place.name,
                    latitude=place.latitude,
                    longitude=place.longitude,
                    owner_id=owner_id,
                    visibility="private",
                )
                saved_place = self.place_dao.create(cloned_place)
                saved_place.locked = place.locked
                duplicated_places.append(saved_place)

        share_token = str(uuid.uuid4())
        new_tour = Tour(
            name=f"{tour.name} (Copy)",
            owner_id=owner_id,
            places=duplicated_places,
            total_distance=tour.total_distance,
            visibility="private",
            share_token=share_token,
        )
        return self.tour_dao.create(new_tour)

    def recalculate_tour(self, tour_id: int, owner_id: int) -> Tour:
        """Recalculate the optimized routing and distance of a tour.

        Args:
            tour_id: The ID of the tour to recalculate.
            owner_id: The user ID of the owner.

        Returns:
            The updated Tour.
        """
        tour = self.get_tour_by_id(tour_id, owner_id)

        locked_map = {}
        for index, place in enumerate(tour.places):
            if place.locked:
                locked_map[place.id] = index

        optimized_places = optimize(tour.places, locked_map)

        for place in optimized_places:
            place.locked = (place.id in locked_map)

        tour.places = optimized_places
        tour.total_distance = self.calculate_tour_distance(optimized_places)

        return self.tour_dao.update(tour)

    def delete_tour(self, tour_id: int, owner_id: int) -> bool:
        """Delete a tour, verifying ownership.

        Args:
            tour_id: The ID of the tour.
            owner_id: The ID of the current user.

        Returns:
            True if deletion was successful.
        """
        # Triggers ownership verification
        self.get_tour_by_id(tour_id, owner_id)
        return self.tour_dao.delete(tour_id)

    def patch_tour(
        self,
        tour_id: int,
        visibility: Optional[str],
        places_id: Optional[List[int]],
        name: Optional[str],
        owner_id: int,
        locked_positions: Optional[dict] = None,
        locked_places: Optional[list] = None,
    ) -> Tour:
        """Update tour.

        Args:
            tour_id: The ID of the tour.
            visibility: Either 'private' or 'public', or None to toggle/keep.
            places_id: New list of place IDs, or None to keep.
            name: New tour name, or None to keep.
            owner_id: The ID of the current user.
            locked_positions: Optional new locked positions mapping.
            locked_places: Optional new locked places list.

        Returns:
            The updated Tour.
        """
        tour = self.get_tour_by_id(tour_id, owner_id)

        if name is not None:
            if not name.strip():
                raise ValidationException("Name cannot be empty.")
            tour.name = name.strip()

        if visibility is not None:
            if visibility not in ["private", "public"]:
                raise ValidationException("Invalid visibility value.")
            tour.visibility = visibility

        # Re-calculate routing if place list or locks are updated
        if (
            places_id is not None
            or locked_positions is not None
            or locked_places is not None
        ):
            if places_id is not None:
                raw_pids = places_id
            else:
                raw_pids = [p.id for p in tour.places]

            parsed_place_ids = []
            locked_map = {}

            for index, item in enumerate(raw_pids):
                if isinstance(item, dict):
                    pid = item.get("id")
                    if pid is not None:
                        parsed_place_ids.append(pid)
                        if item.get("locked") or item.get("position") is not None:
                            locked_map[pid] = item.get("position", index)
                else:
                    try:
                        parsed_place_ids.append(int(item))
                    except (ValueError, TypeError):
                        raise ValidationException("Invalid place ID format")

            # Merge separately passed locked_positions
            if locked_positions is not None:
                for pid_str, pos in locked_positions.items():
                    try:
                        pid = int(pid_str)
                        locked_map[pid] = int(pos)
                    except (ValueError, TypeError):
                        raise ValidationException("Invalid locked_positions format")

            # Merge separately passed locked_places
            if locked_places is not None:
                for pid in locked_places:
                    try:
                        pid = int(pid)
                        if pid in parsed_place_ids:
                            locked_map[pid] = parsed_place_ids.index(pid)
                    except (ValueError, TypeError):
                        raise ValidationException("Invalid locked_places format")

            # If we did not pass new locks, preserve existing locks that are still in the list
            if (
                locked_positions is None
                and locked_places is None
                and places_id is None
            ):
                for p in tour.places:
                    if p.locked and p.id in parsed_place_ids:
                        locked_map[p.id] = parsed_place_ids.index(p.id)

            if len(parsed_place_ids) < 2:
                raise ValidationException(
                    "At least 2 places are required to generate a tour"
                )

            places_by_id = {p.id: p for p in self.place_dao.get_by_ids(parsed_place_ids)}
            places = []
            for pid in parsed_place_ids:
                place = places_by_id.get(pid)
                if not place:
                    raise ValidationException(f"Place with ID {pid} does not exist")
                if place.owner_id != owner_id and place.visibility != "public":
                    raise ForbiddenException(
                        f"You do not own the place with ID {pid} and it is not public"
                    )
                places.append(place)

            optimized_places = optimize(places, locked_map)

            # Apply locked property on returned place objects
            for place in optimized_places:
                place.locked = (place.id in locked_map)

            tour.places = optimized_places
            tour.total_distance = self.calculate_tour_distance(optimized_places)

        return self.tour_dao.update(tour)

    def get_shared_tour(self, share_token: str) -> Tour:
        """Retrieve a public tour by its share token. No authentication required.

        Args:
            share_token: The unique public UUID share token.

        Returns:
            The Tour.

        Raises:
            NotFoundException: If the tour is not found or is set to private.
        """
        tour = self.tour_dao.get_by_share_token(share_token)
        if not tour or tour.visibility != "public":
            raise NotFoundException("Shared tour not found or is private")
        return tour

    def calculate_tour_distance(self, places: List[Place]) -> float:
        """Calculate the total great-circle distance of a closed loop path.

        Args:
            places: Ordered list of places.

        Returns:
            The total distance in km.
        """
        if len(places) <= 1:
            return 0.0
        total = 0.0
        for i in range(len(places) - 1):
            total += haversine(places[i], places[i + 1])
        # Return to start
        total += haversine(places[-1], places[0])
        return total
