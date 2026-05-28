from typing import List, Optional
from dao.database import db
from dao.base_dao import BaseDAO
from dao.models import UserModel
from dataobject.user import User


class UserDAO(BaseDAO[User, int]):
    """Data Access Object for User persistence."""

    def get_by_id(self, entity_id: int) -> Optional[User]:
        """Retrieve a user by ID."""
        user_model = UserModel.query.get(entity_id)
        if not user_model:
            return None
        return self._to_dataobject(user_model)

    def get_all(self) -> List[User]:
        """Retrieve all users."""
        user_models = UserModel.query.all()
        return [self._to_dataobject(um) for um in user_models]

    def create(self, entity: User) -> User:
        """Create and persist a new user."""
        user_model = UserModel(
            username=entity.username,
            email=entity.email,
            password_hash=entity.password_hash,
        )
        db.session.add(user_model)
        db.session.commit()
        entity.id = user_model.id
        return entity

    def update(self, entity: User) -> User:
        """Update an existing user."""
        user_model = UserModel.query.get(entity.id)
        if user_model:
            user_model.username = entity.username
            user_model.email = entity.email
            user_model.password_hash = entity.password_hash
            db.session.commit()
        return entity

    def delete(self, entity_id: int) -> bool:
        """Delete a user by ID."""
        user_model = UserModel.query.get(entity_id)
        if user_model:
            db.session.delete(user_model)
            db.session.commit()
            return True
        return False

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address.

        Args:
            email: The email address to look up.

        Returns:
            The User data object or None.
        """
        user_model = UserModel.query.filter_by(email=email).first()
        if not user_model:
            return None
        return self._to_dataobject(user_model)

    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by their username.

        Args:
            username: The username to look up.

        Returns:
            The User data object or None.
        """
        user_model = UserModel.query.filter_by(username=username).first()
        if not user_model:
            return None
        return self._to_dataobject(user_model)

    def _to_dataobject(self, model: UserModel) -> User:
        """Helper to convert UserModel (ORM) to User (DataObject)."""
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
        )
