from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")  # The DataObject type
ID = TypeVar("ID")


class BaseDAO(Generic[T, ID], ABC):
    """Abstract Base Data Access Object defining standard CRUD operations."""

    @abstractmethod
    def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Retrieve an entity by its unique ID.

        Args:
            entity_id: The ID of the entity.

        Returns:
            The entity DataObject, or None if not found.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieve all entities of this type.

        Returns:
            A list of all entity DataObjects.
        """
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """Persist a new entity.

        Args:
            entity: The DataObject to persist.

        Returns:
            The persisted DataObject (including its generated ID).
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity.

        Args:
            entity: The DataObject to update.

        Returns:
            The updated DataObject.
        """
        pass

    @abstractmethod
    def delete(self, entity_id: ID) -> bool:
        """Delete an entity by its unique ID.

        Args:
            entity_id: The ID of the entity to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        pass
