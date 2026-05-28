from dataobject.place import Place
from services.algorithm.distance import haversine


def test_haversine_same_coordinates():
    """Test that distance between a place and itself is exactly 0."""
    place = Place(name="Paris", latitude=48.8566, longitude=2.3522, owner_id=1)
    assert haversine(place, place) == 0.0


def test_haversine_different_places():
    """Test distance calculation between Paris and Lyon."""
    paris = Place(name="Paris", latitude=48.8566, longitude=2.3522, owner_id=1)
    lyon = Place(name="Lyon", latitude=45.7640, longitude=4.8357, owner_id=1)

    # Let's verify it returns a float and is approximately 391.2 km
    dist = haversine(paris, lyon)
    assert isinstance(dist, float)
    assert 390.0 < dist < 393.0


def test_haversine_antipodes():
    """Test distance calculation on opposite ends of the globe."""
    place_a = Place(name="Quito", latitude=0.0, longitude=-78.5, owner_id=1)
    place_b = Place(
        name="Singapore", latitude=0.0, longitude=101.5, owner_id=1
    )  # 180 degrees apart

    # 180 degrees difference along equator -> R_EARTH * PI
    expected_dist = 6378.197 * 3.141592
    assert abs(haversine(place_a, place_b) - expected_dist) < 1.0
