from typing import List, Optional
from dao.database import db
from dao.base_dao import BaseDAO
from dao.models import PlaceModel
from dataobject.place import Place


class PlaceDAO(BaseDAO[Place, int]):
    """Data Access Object for Place persistence."""

    def get_by_id(self, entity_id: int) -> Optional[Place]:
        """Retrieve a place by ID."""
        place_model = PlaceModel.query.get(entity_id)
        if not place_model:
            return None
        return self._to_dataobject(place_model)

    def get_all(self) -> List[Place]:
        """Retrieve all places."""
        place_models = PlaceModel.query.all()
        return [self._to_dataobject(pm) for pm in place_models]

    def create(self, entity: Place) -> Place:
        """Create and persist a new place."""
        place_model = PlaceModel(
            name=entity.name,
            latitude=entity.latitude,
            longitude=entity.longitude,
            owner_id=entity.owner_id,
            visibility=entity.visibility,
        )
        db.session.add(place_model)
        db.session.commit()
        entity.id = place_model.id
        return entity

    def update(self, entity: Place) -> Place:
        """Update an existing place."""
        place_model = PlaceModel.query.get(entity.id)
        if place_model:
            place_model.name = entity.name
            place_model.latitude = entity.latitude
            place_model.longitude = entity.longitude
            place_model.owner_id = entity.owner_id
            place_model.visibility = entity.visibility
            db.session.commit()
        return entity

    def delete(self, entity_id: int) -> bool:
        """Delete a place by ID."""
        place_model = PlaceModel.query.get(entity_id)
        if place_model:
            db.session.delete(place_model)
            db.session.commit()
            return True
        return False

    def get_by_owner(self, owner_id: int) -> List[Place]:
        """Retrieve all places belonging to a specific owner.

        Args:
            owner_id: The ID of the owner user.

        Returns:
            A list of Place data objects.
        """
        place_models = PlaceModel.query.filter_by(owner_id=owner_id).all()
        return [self._to_dataobject(pm) for pm in place_models]

    def get_public(self) -> List[Place]:
        """Retrieve all public places.

        Returns:
            A list of Place data objects.
        """
        place_models = PlaceModel.query.filter_by(visibility="public").all()
        return [self._to_dataobject(pm) for pm in place_models]

    def query_places(
        self,
        owner_id: Optional[int] = None,
        visibility: Optional[str] = None,
        q: Optional[str] = None,
        page: int = 1,
        limit: Optional[int] = None,
    ) -> List[Place]:
        """Query places with filters and pagination.

        Args:
            owner_id: Optional owner user ID filter.
            visibility: Optional visibility ('public' or 'private') filter.
            q: Optional search query for place name (case-insensitive).
            page: Page number for pagination (starts at 1).
            limit: Maximum number of places to retrieve.

        Returns:
            A list of Place data objects.
        """
        query = PlaceModel.query

        if visibility is not None:
            query = query.filter(PlaceModel.visibility == visibility)
        if owner_id is not None:
            query = query.filter(PlaceModel.owner_id == owner_id)
        if q:
            query = query.filter(PlaceModel.name.ilike(f"%{q}%"))

        # Pagination
        if limit is not None and limit > 0:
            offset = (page - 1) * limit
            query = query.limit(limit).offset(offset)

        place_models = query.all()
        return [self._to_dataobject(pm) for pm in place_models]

    def _to_dataobject(self, model: PlaceModel) -> Place:
        """Helper to convert PlaceModel (ORM) to Place (DataObject)."""
        return Place(
            id=model.id,
            name=model.name,
            latitude=model.latitude,
            longitude=model.longitude,
            owner_id=model.owner_id,
            visibility=model.visibility,
        )
