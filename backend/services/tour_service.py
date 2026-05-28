import uuid
from typing import List
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
    ) -> Tour:
        """Generate an optimized tour from a list of place IDs.

        Args:
            name: The name of the tour.
            place_ids: A list of place IDs to include.
            owner_id: The ID of the owner user.
            visibility: The sharing visibility ('private' or 'public').

        Returns:
            The created and persisted Tour.

        Raises:
            ValidationException: If there are fewer than 2 places or validation fails.
            ForbiddenException: If the user doesn't own all specified places
                (unless they are public).
        """
        if not name or not name.strip():
            raise ValidationException("Tour name is required")
        if not place_ids or len(place_ids) < 2:
            raise ValidationException(
                "At least 2 places are required to generate a tour"
            )
        if visibility not in ["private", "public"]:
            raise ValidationException("Visibility must be either 'private' or 'public'")

        # Retrieve and validate all places belong to the owner or are public
        places = []
        for pid in place_ids:
            place = self.place_dao.get_by_id(pid)
            if not place:
                raise ValidationException(f"Place with ID {pid} does not exist")
            if place.owner_id != owner_id and place.visibility != "public":
                raise ForbiddenException(
                    f"You do not own the place with ID {pid} and it is not public"
                )
            places.append(place)

        # Optimize the place ordering using nearest neighbour + 2-opt
        optimized_places = optimize(places)

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

    def get_public_tours(self) -> List[Tour]:
        """Retrieve all public tours.

        Returns:
            A list of Tour data objects.
        """
        return self.tour_dao.get_public()

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

    def update_share_visibility(
        self, tour_id: int, visibility: str, owner_id: int
    ) -> Tour:
        """Update tour sharing visibility (private vs public).

        Args:
            tour_id: The ID of the tour.
            visibility: Either 'private' or 'public'.
            owner_id: The ID of the current user.

        Returns:
            The updated Tour.

        Raises:
            ValidationException: If visibility value is invalid.
        """
        if visibility not in ["private", "public"]:
            raise ValidationException("Visibility must be either 'private' or 'public'")

        tour = self.get_tour_by_id(tour_id, owner_id)
        tour.visibility = visibility
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
