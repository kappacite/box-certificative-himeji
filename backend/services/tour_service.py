import uuid
from typing import List, Optional, Tuple
from dao.tour_dao import TourDAO
from dao.place_dao import PlaceDAO
from dataobject.tour import Tour
from dataobject.place import Place
from services.algorithm import optimize_with_hotels, haversine
from exceptions import NotFoundException, ForbiddenException, ValidationException


class TourService:
    """Business logic service for managing Tours, computing distances, and sharing."""

    def __init__(self, tour_dao: TourDAO = None, place_dao: PlaceDAO = None):
        self.tour_dao = tour_dao or TourDAO()
        self.place_dao = place_dao or PlaceDAO()

    def _parse_place_inputs_and_locks(
        self,
        place_ids: List,
        locked_positions: dict = None,
        locked_places: list = None,
    ) -> Tuple[List[int], dict]:
        """Parse raw place input list and merge locked constraints into a map
        of place_id -> position.

        Args:
            place_ids: A list of place IDs or dicts containing 'id', 'locked', 'position'.
            locked_positions: Dict mapping place_id (as str) to target position.
            locked_places: List of place_ids to lock at their input positions.

        Returns:
            A tuple containing:
                - A list of integer place IDs.
                - A dictionary mapping place ID (int) to its locked position (int).
        """
        parsed_place_ids = []
        locked_map = {}

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

        return parsed_place_ids, locked_map

    def _retrieve_and_validate_places(
        self,
        place_ids: List[int],
        owner_id: int,
    ) -> List[Place]:
        """Retrieve places from DAO and validate ownership/visibility.

        Args:
            place_ids: List of place IDs.
            owner_id: The ID of the current user.

        Returns:
            A list of Place data objects in the requested order.
        """
        places_by_id = {p.id: p for p in self.place_dao.get_by_ids(place_ids)}
        places = []
        for pid in place_ids:
            place = places_by_id.get(pid)
            if not place:
                raise ValidationException(f"Place with ID {pid} does not exist")
            if place.owner_id != owner_id and place.visibility != "public":
                raise ForbiddenException(
                    f"You do not own the place with ID {pid} and it is not public"
                )
            places.append(place)
        return places

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
        max_distance: float = 100.0,
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
            max_distance: Maximum distance in km for round trips.

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

        parsed_place_ids, locked_map = self._parse_place_inputs_and_locks(
            place_ids, locked_positions, locked_places
        )

        places = self._retrieve_and_validate_places(parsed_place_ids, owner_id)

        # Optimize the place ordering respecting locks
        optimized_places = optimize_with_hotels(
            places, locked_map, max_distance=max_distance
        )

        # Apply locked property on returned place objects
        for place in optimized_places:
            place.locked = place.id in locked_map

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
            max_distance=max_distance,
        )

        from dao.database import db

        tour = self.tour_dao.create(new_tour)
        db.session.commit()
        return tour

    def preview_tour(
        self,
        place_ids: List[int],
        owner_id: int,
        locked_positions: dict = None,
        locked_places: list = None,
        max_distance: float = 100.0,
    ) -> Tour:
        """Generate an optimized tour preview without persisting it.

        Args:
            place_ids: A list of place IDs (or dicts) to include.
            owner_id: The ID of the owner user.
            locked_positions: Dict mapping place_id (as str) to target position.
            locked_places: List of place_ids to lock at their input positions.
            max_distance: Maximum distance in km for round trips.

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

        parsed_place_ids, locked_map = self._parse_place_inputs_and_locks(
            place_ids, locked_positions, locked_places
        )

        places = self._retrieve_and_validate_places(parsed_place_ids, owner_id)

        # Optimize the place ordering respecting locks
        optimized_places = optimize_with_hotels(
            places, locked_map, max_distance=max_distance
        )

        # Apply locked property on returned place objects
        for place in optimized_places:
            place.locked = place.id in locked_map

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
            max_distance=max_distance,
            id=None,
        )

    def optimize_places(
        self,
        place_ids: List[int],
        owner_id: int,
        locked_positions: dict = None,
        locked_places: list = None,
        max_distance: float = 100.0,
    ) -> dict:
        """Optimize place sequence according to coordinates and locked constraints.

        Args:
            place_ids: A list of place IDs (or dicts) to include.
            owner_id: The ID of the owner user.
            locked_positions: Dict mapping place_id (as str) to target position.
            locked_places: List of place_ids to lock at their input positions.
            max_distance: Maximum distance in km for round trips.

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

        parsed_place_ids, locked_map = self._parse_place_inputs_and_locks(
            place_ids, locked_positions, locked_places
        )

        places = self._retrieve_and_validate_places(parsed_place_ids, owner_id)

        # Optimize the place ordering respecting locks
        optimized_places = optimize_with_hotels(
            places, locked_map, max_distance=max_distance
        )

        # Apply locked property on returned place objects
        for place in optimized_places:
            place.locked = place.id in locked_map

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
        return self.tour_dao.query_tours(
            visibility="public", q=q, page=page, limit=limit
        )

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
        from dao.database import db

        duplicated_tour = self.tour_dao.create(new_tour)
        db.session.commit()
        return duplicated_tour

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
        unique_places = []
        seen = set()
        for p in tour.places:
            if p.id not in seen:
                seen.add(p.id)
                unique_places.append(p)

        for index, place in enumerate(unique_places):
            if place.locked:
                locked_map[place.id] = index

        optimized_places = optimize_with_hotels(
            unique_places, locked_map, max_distance=tour.max_distance
        )

        for place in optimized_places:
            place.locked = place.id in locked_map

        tour.places = optimized_places
        tour.total_distance = self.calculate_tour_distance(optimized_places)

        from dao.database import db

        updated_tour = self.tour_dao.update(tour)
        db.session.commit()
        return updated_tour

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
        from dao.database import db

        deleted = self.tour_dao.delete(tour_id)
        db.session.commit()
        return deleted

    def patch_tour(
        self,
        tour_id: int,
        visibility: Optional[str],
        places_id: Optional[List[int]],
        name: Optional[str],
        owner_id: int,
        locked_positions: Optional[dict] = None,
        locked_places: Optional[list] = None,
        max_distance: Optional[float] = None,
        optimize: bool = True,
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
            max_distance: Optional updated max_distance for clustering.
            optimize: When False, save places in the provided order without
                      running the optimization algorithm (default True).

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

        if max_distance is not None:
            tour.max_distance = max_distance

        # Re-calculate routing if place list, max_distance, or locks are updated
        if (
            places_id is not None
            or locked_positions is not None
            or locked_places is not None
            or max_distance is not None
        ):
            if places_id is not None:
                raw_pids = places_id
            else:
                # Deduplicate while preserving order
                raw_pids = []
                seen_pid = set()
                for p in tour.places:
                    if p.id not in seen_pid:
                        seen_pid.add(p.id)
                        raw_pids.append(p.id)

            parsed_place_ids, locked_map = self._parse_place_inputs_and_locks(
                raw_pids, locked_positions, locked_places
            )

            # If we did not pass new locks, preserve existing locks that are still in the list
            if locked_positions is None and locked_places is None and places_id is None:
                for p in tour.places:
                    if p.locked and p.id in parsed_place_ids:
                        locked_map[p.id] = parsed_place_ids.index(p.id)

            if len(parsed_place_ids) < 2:
                raise ValidationException(
                    "At least 2 places are required to generate a tour"
                )

            places = self._retrieve_and_validate_places(parsed_place_ids, owner_id)

            if optimize:
                optimized_places = optimize_with_hotels(
                    places, locked_map, max_distance=tour.max_distance
                )
                # Apply locked property on returned place objects
                for place in optimized_places:
                    place.locked = place.id in locked_map
            else:
                # Save in the exact order provided — no algorithm.
                # Restore is_hotel from the existing tour so hotel markers are preserved.
                existing_hotel_map = {p.id: p.is_hotel for p in tour.places}
                optimized_places = places
                for place in optimized_places:
                    place.locked = place.id in locked_map
                    place.is_hotel = existing_hotel_map.get(place.id, False)

            tour.places = optimized_places
            tour.total_distance = self.calculate_tour_distance(optimized_places)

        from dao.database import db

        updated_tour = self.tour_dao.update(tour)
        db.session.commit()
        return updated_tour

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
        """Calculate the total great-circle distance of a closed loop.

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
        # Loop closure: add distance from the last place back to the first
        total += haversine(places[-1], places[0])
        return total
