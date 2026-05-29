from typing import List, Optional
from dao.database import db
from dao.base_dao import BaseDAO
from dao.models import TourModel, TourPlaceModel
from dataobject.tour import Tour
from dataobject.place import Place


class TourDAO(BaseDAO[Tour, int]):
    """Data Access Object for Tour persistence, handling ordered relations to Places."""

    def get_by_id(self, entity_id: int) -> Optional[Tour]:
        """Retrieve a tour by ID, populating its ordered list of places."""
        tour_model = db.session.get(TourModel, entity_id)
        if not tour_model:
            return None
        return self._to_dataobject(tour_model)

    def get_all(self) -> List[Tour]:
        """Retrieve all tours."""
        tour_models = TourModel.query.all()
        return [self._to_dataobject(tm) for tm in tour_models]

    def create(self, entity: Tour) -> Tour:
        """Create and persist a new tour with its ordered places."""
        tour_model = TourModel(
            name=entity.name,
            owner_id=entity.owner_id,
            total_distance=entity.total_distance,
            visibility=entity.visibility,
            share_token=entity.share_token,
            max_distance=entity.max_distance,
        )
        db.session.add(tour_model)
        # Flush to get the tour_model.id
        db.session.flush()

        # Add the ordered places relationship
        for index, place in enumerate(entity.places):
            if place.id is None:
                # If place isn't saved, we might have an issue.
                # Assuming places are already saved before creating a tour.
                raise ValueError(
                    f"Place '{place.name}' must have an ID to be linked in a tour."
                )

            assoc = TourPlaceModel(
                tour_id=tour_model.id,
                place_id=place.id,
                position=index,
                locked=place.locked,
                is_hotel=place.is_hotel,
            )
            db.session.add(assoc)

        db.session.flush()
        entity.id = tour_model.id
        return entity

    def update(self, entity: Tour) -> Tour:
        """Update an existing tour, replacing its ordered place list."""
        tour_model = db.session.get(TourModel, entity.id)
        if not tour_model:
            return entity

        # Update basic attributes
        tour_model.name = entity.name
        tour_model.total_distance = entity.total_distance
        tour_model.visibility = entity.visibility
        tour_model.share_token = entity.share_token
        tour_model.max_distance = entity.max_distance

        # Replace ordered list of places: delete existing, add new ones
        TourPlaceModel.query.filter_by(tour_id=entity.id).delete()

        for index, place in enumerate(entity.places):
            if place.id is None:
                raise ValueError(
                    f"Place '{place.name}' must have an ID to be linked in a tour."
                )

            assoc = TourPlaceModel(
                tour_id=tour_model.id,
                place_id=place.id,
                position=index,
                locked=place.locked,
                is_hotel=place.is_hotel,
            )
            db.session.add(assoc)

        db.session.flush()
        return entity

    def delete(self, entity_id: int) -> bool:
        """Delete a tour by ID. Foreign keys take care of cascade deletes."""
        tour_model = db.session.get(TourModel, entity_id)
        if tour_model:
            db.session.delete(tour_model)
            db.session.flush()
            return True
        return False

    def get_by_owner(self, owner_id: int) -> List[Tour]:
        """Retrieve all tours belonging to a specific owner.

        Args:
            owner_id: The ID of the owner user.

        Returns:
            A list of Tour data objects.
        """
        tour_models = TourModel.query.filter_by(owner_id=owner_id).all()
        return [self._to_dataobject(tm) for tm in tour_models]

    def get_by_share_token(self, share_token: str) -> Optional[Tour]:
        """Retrieve a public tour by its share token.

        Args:
            share_token: The UUID share token.

        Returns:
            The Tour data object, or None if not found or private.
        """
        tour_model = TourModel.query.filter_by(share_token=share_token).first()
        if not tour_model:
            return None
        return self._to_dataobject(tour_model)

    def get_public(self) -> List[Tour]:
        """Retrieve all public tours.

        Returns:
            A list of Tour data objects.
        """
        tour_models = TourModel.query.filter_by(visibility="public").all()
        return [self._to_dataobject(tm) for tm in tour_models]

    def query_tours(
        self,
        owner_id: Optional[int] = None,
        visibility: Optional[str] = None,
        q: Optional[str] = None,
        page: int = 1,
        limit: Optional[int] = None,
    ) -> List[Tour]:
        """Query tours with filters and pagination.

        Args:
            owner_id: Optional owner user ID filter.
            visibility: Optional visibility ('public' or 'private') filter.
            q: Optional search query for tour name (case-insensitive).
            page: Page number for pagination (starts at 1).
            limit: Maximum number of tours to retrieve.

        Returns:
            A list of Tour data objects.
        """
        query = TourModel.query

        if visibility is not None:
            query = query.filter(TourModel.visibility == visibility)
        if owner_id is not None:
            query = query.filter(TourModel.owner_id == owner_id)
        if q:
            query = query.filter(TourModel.name.ilike(f"%{q}%"))

        # Pagination
        if limit is not None and limit > 0:
            offset = (page - 1) * limit
            query = query.limit(limit).offset(offset)

        tour_models = query.all()
        return [self._to_dataobject(tm) for tm in tour_models]

    def _to_dataobject(self, model: TourModel) -> Tour:
        """Helper to convert TourModel (ORM) to Tour (DataObject) with resolved Places."""
        places = []
        for tp in model.tour_places:
            # tp.place is a PlaceModel
            place_do = Place(
                id=tp.place.id,
                name=tp.place.name,
                latitude=tp.place.latitude,
                longitude=tp.place.longitude,
                owner_id=tp.place.owner_id,
                visibility=tp.place.visibility,
                locked=getattr(tp, "locked", False),
                is_hotel=getattr(tp, "is_hotel", False),
            )
            places.append(place_do)

        return Tour(
            id=model.id,
            name=model.name,
            owner_id=model.owner_id,
            places=places,
            total_distance=model.total_distance,
            visibility=model.visibility,
            share_token=model.share_token,
            max_distance=model.max_distance,
        )
