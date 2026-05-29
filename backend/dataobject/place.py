from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Place:
    """Place data object representing a location with coordinates."""

    name: str
    latitude: float
    longitude: float
    owner_id: int
    visibility: str = "private"  # "private" or "public"
    id: Optional[int] = None
    locked: bool = False
    is_hotel: bool = False

    def to_dict(self) -> dict:
        """Convert the Place dataclass instance to a dictionary.

        Returns:
            A dictionary representation of the Place.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Place":
        """Create a Place instance from a dictionary.

        Args:
            data: The source dictionary.

        Returns:
            A Place instance.
        """
        return cls(
            name=data.get("name"),
            latitude=float(data.get("latitude")),
            longitude=float(data.get("longitude")),
            owner_id=data.get("owner_id"),
            visibility=data.get("visibility", "private"),
            id=data.get("id"),
            locked=data.get("locked", False),
            is_hotel=data.get("is_hotel", False),
        )
