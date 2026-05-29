from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class RevokedToken:
    """Pure data object representing a revoked JWT token."""

    token: str
    id: Optional[int] = None
    revoked_at: Optional[datetime.datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "token": self.token,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }
