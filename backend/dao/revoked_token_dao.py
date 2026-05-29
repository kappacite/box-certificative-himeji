from typing import List, Optional
from dao.database import db
from dao.base_dao import BaseDAO
from dao.models import RevokedTokenModel
from dataobject.revoked_token import RevokedToken


class RevokedTokenDAO(BaseDAO[RevokedToken, int]):
    """Data Access Object for RevokedToken persistence."""

    def get_by_id(self, entity_id: int) -> Optional[RevokedToken]:
        """Retrieve a revoked token by ID."""
        model = db.session.get(RevokedTokenModel, entity_id)
        if not model:
            return None
        return self._to_dataobject(model)

    def get_all(self) -> List[RevokedToken]:
        """Retrieve all revoked tokens."""
        models = RevokedTokenModel.query.all()
        return [self._to_dataobject(m) for m in models]

    def create(self, entity: RevokedToken) -> RevokedToken:
        """Create and persist a new revoked token."""
        model = RevokedTokenModel(token=entity.token)
        db.session.add(model)
        db.session.commit()
        entity.id = model.id
        entity.revoked_at = model.revoked_at
        return entity

    def update(self, entity: RevokedToken) -> RevokedToken:
        """Update an existing revoked token."""
        model = db.session.get(RevokedTokenModel, entity.id)
        if model:
            model.token = entity.token
            db.session.commit()
        return entity

    def delete(self, entity_id: int) -> bool:
        """Delete a revoked token by ID."""
        model = db.session.get(RevokedTokenModel, entity_id)
        if model:
            db.session.delete(model)
            db.session.commit()
            return True
        return False

    def get_by_token(self, token: str) -> Optional[RevokedToken]:
        """Retrieve a revoked token by the token string."""
        model = RevokedTokenModel.query.filter_by(token=token).first()
        if not model:
            return None
        return self._to_dataobject(model)

    def _to_dataobject(self, model: RevokedTokenModel) -> RevokedToken:
        """Helper to convert RevokedTokenModel (ORM) to RevokedToken (DataObject)."""
        return RevokedToken(
            id=model.id,
            token=model.token,
            revoked_at=model.revoked_at,
        )
