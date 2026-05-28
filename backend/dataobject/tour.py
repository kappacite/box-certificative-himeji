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
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert the Tour dataclass instance to a dictionary.

        Returns:
            A dictionary representation of the Tour.
        """
        places_dict = [p.to_dict() for p in self.places]
        if self.places:
            places_dict.append(self.places[0].to_dict())

        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "places": places_dict,
            "total_distance": self.total_distance,
            "visibility": self.visibility,
            "share_token": self.share_token,
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
        if len(places) > 1 and (
            (places[0].id is not None and places[0].id == places[-1].id)
            or (places[0] == places[-1])
        ):
            places = places[:-1]

        return cls(
            name=data.get("name"),
            owner_id=data.get("owner_id"),
            places=places,
            total_distance=float(data.get("total_distance", 0.0)),
            visibility=data.get("visibility", "private"),
            share_token=data.get("share_token"),
            id=data.get("id"),
        )
