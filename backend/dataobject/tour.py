from dataclasses import dataclass, field
from typing import Optional, List
from dataobject.place import Place


@dataclass
class Tour:
    """Tour data object representing an optimized route."""

    name: str
    owner_id: int
    places: List[Place] = field(default_factory=list)
    total_distance: float = 0.0
    visibility: str = "private"  # "private" or "public"
    share_token: Optional[str] = None
    max_distance: float = 100.0
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert the Tour dataclass instance to a dictionary.

        Returns:
            A dictionary representation of the Tour.
        """
        places_dict = [p.to_dict() for p in self.places]

        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "places": places_dict,
            "total_distance": self.total_distance,
            "visibility": self.visibility,
            "share_token": self.share_token,
            "max_distance": self.max_distance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tour":
        """Create a Tour instance from a dictionary.

        Args:
            data: The source dictionary.

        Returns:
            A Tour instance.
        """
        raw_places = data.get("places", [])
        places = [Place.from_dict(p) if isinstance(p, dict) else p for p in raw_places]

        return cls(
            name=data.get("name"),
            owner_id=data.get("owner_id"),
            places=places,
            total_distance=float(data.get("total_distance", 0.0)),
            visibility=data.get("visibility", "private"),
            share_token=data.get("share_token"),
            max_distance=float(data.get("max_distance", 100.0)),
            id=data.get("id"),
        )
