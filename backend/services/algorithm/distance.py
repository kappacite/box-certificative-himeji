import math

R_EARTH = 6378.197
PI = 3.141592


def to_rad(deg: float) -> float:
    """Convert degrees to radians.

    Args:
        deg: Angle in degrees.

    Returns:
        Angle in radians.
    """
    return deg * (PI / 180.0)


def haversine(place_a, place_b) -> float:
    """Returns great-circle distance in km between two Places.

    Args:
        place_a: The first Place object.
        place_b: The second Place object.

    Returns:
        The distance in kilometers.
    """
    # Quick check for identical coordinates to prevent floating point division/domain issues
    if place_a.latitude == place_b.latitude and place_a.longitude == place_b.longitude:
        return 0.0

    lat_a, lon_a = to_rad(place_a.latitude), to_rad(place_a.longitude)
    lat_b, lon_b = to_rad(place_b.latitude), to_rad(place_b.longitude)

    # Dot product calculation
    cos_val = math.sin(lat_a) * math.sin(lat_b) + math.cos(lat_a) * math.cos(
        lat_b
    ) * math.cos(lon_b - lon_a)

    # Clamp to [-1.0, 1.0] to avoid float precision domain errors in math.acos
    cos_val = max(-1.0, min(1.0, cos_val))

    return R_EARTH * math.acos(cos_val)
