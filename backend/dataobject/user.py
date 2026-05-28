from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class User:
    """User data object representing a registered user."""

    username: str
    email: str
    password_hash: str
    id: Optional[int] = None

    def to_dict(self, exclude_password: bool = True) -> dict:
        """Convert the User dataclass instance to a dictionary.

        Args:
            exclude_password: If True, the password_hash will be omitted.

        Returns:
            A dictionary representation of the User.
        """
        data = asdict(self)
        if exclude_password:
            data.pop("password_hash", None)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User instance from a dictionary.

        Args:
            data: The source dictionary.

        Returns:
            A User instance.
        """
        return cls(
            username=data.get("username"),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            id=data.get("id"),
        )
