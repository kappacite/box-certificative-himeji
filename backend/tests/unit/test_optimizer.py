from services.algorithm.optimizer import optimize, optimize_with_hotels
from services.algorithm.distance import haversine
from dataobject.place import Place


def _calculate_total_distance(tour: list[Place]) -> float:
    if len(tour) <= 1:
        return 0.0
    total = 0.0
    for i in range(len(tour) - 1):
        total += haversine(tour[i], tour[i + 1])
    total += haversine(tour[-1], tour[0])
    return total


def test_optimize_empty_or_single_place():
    """Test optimizer behaviour on edge cases (0 or 1 place)."""
    assert optimize([]) == []

    place = Place(name="Paris", latitude=48.8566, longitude=2.3522, owner_id=1)
    assert optimize([place]) == [place]


def test_optimize_multiple_places():
    """Test optimizer on a set of coordinates, ensuring it visits all and minimizes distance."""
    # A simple triangle path where they might be out of order
    p1 = Place(name="A", latitude=0.0, longitude=0.0, owner_id=1, id=1)
    p2 = Place(name="B", latitude=0.0, longitude=10.0, owner_id=1, id=2)
    p3 = Place(name="C", latitude=10.0, longitude=10.0, owner_id=1, id=3)
    p4 = Place(name="D", latitude=10.0, longitude=0.0, owner_id=1, id=4)

    # Input out of order
    places = [p1, p3, p2, p4]

    tour = optimize(places)

    # Must contain the same elements
    assert len(tour) == 4
    assert set(p.id for p in tour) == set(p.id for p in places)

    # Distance of optimized tour should be less than or equal to sub-optimal ordering
    opt_dist = _calculate_total_distance(tour)
    sub_opt_dist = _calculate_total_distance(places)
    assert opt_dist <= sub_opt_dist


def test_optimize_with_locked_positions():
    """Test optimizer respecting locked positions."""
    p1 = Place(name="A", latitude=0.0, longitude=0.0, owner_id=1, id=1)
    p2 = Place(name="B", latitude=0.0, longitude=10.0, owner_id=1, id=2)
    p3 = Place(name="C", latitude=10.0, longitude=10.0, owner_id=1, id=3)
    p4 = Place(name="D", latitude=10.0, longitude=0.0, owner_id=1, id=4)

    # Let's say input is [p1, p2, p3, p4]
    # We want to force C (id=3) to be at position 1, and A (id=1) to be at position 0
    locked_positions = {3: 1, 1: 0}
    tour = optimize([p1, p2, p3, p4], locked_positions=locked_positions)

    assert len(tour) == 4
    # Check that A (id=1) is at index 0
    assert tour[0].id == 1
    # Check that C (id=3) is at index 1
    assert tour[1].id == 3


def test_optimize_with_hotels():
    """Test optimize_with_hotels algorithm."""
    # Paris
    p1 = Place(name="Paris 1", latitude=48.8566, longitude=2.3522, owner_id=1, id=1)
    # Versailles (16 km from Paris)
    p2 = Place(name="Versailles", latitude=48.8014, longitude=2.1301, owner_id=1, id=2)
    # Lyon (391 km from Paris)
    p3 = Place(name="Lyon", latitude=45.7640, longitude=4.8357, owner_id=1, id=3)

    # 1. With max_distance = 100.0 km
    # Versailles is covered by Paris 1. Lyon is a separate hotel.
    # Hotels = [Paris 1, Lyon].
    # Round trips = Paris 1 -> Versailles -> Paris 1.
    # The returned sequence should be [Paris 1, Versailles, Paris 1, Lyon]
    # (loop closure returns to Paris 1)
    sequence = optimize_with_hotels([p1, p2, p3], max_distance=100.0)
    assert len(sequence) == 5
    assert [p.id for p in sequence] == [1, 2, 1, 3, 1]
    assert sequence[0].is_hotel is True
    assert sequence[1].is_hotel is False
    assert sequence[2].is_hotel is True
    assert sequence[3].is_hotel is True
    assert sequence[4].is_hotel is True

    # 2. With max_distance = 5.0 km
    # Versailles is too far from Paris 1 (16 km > 5.0 km).
    # All places become their own hotels.
    # Hotels = [Paris 1, Versailles, Lyon].
    # The returned sequence has length 4: [Paris 1, Versailles, Lyon, Paris 1]
    sequence_no_grouping = optimize_with_hotels([p1, p2, p3], max_distance=5.0)
    assert len(sequence_no_grouping) == 4
    assert [p.id for p in sequence_no_grouping] in [[1, 2, 3, 1], [1, 3, 2, 1]]
    for p in sequence_no_grouping:
        assert p.is_hotel is True


def test_optimize_with_hotels_locked_non_hotel_place():
    """Test that locking a non-hotel place maps and moves its covering hotel."""
    # Paris 1 (start, H1)
    p1 = Place(name="Paris 1", latitude=48.8566, longitude=2.3522, owner_id=1, id=1)
    # Versailles (16 km from Paris, covered by H1)
    p2 = Place(name="Versailles", latitude=48.8014, longitude=2.1301, owner_id=1, id=2)
    # Lyon (391 km from Paris, H2)
    p3 = Place(name="Lyon", latitude=45.7640, longitude=4.8357, owner_id=1, id=3)
    # Marseille (H3)
    p4 = Place(name="Marseille", latitude=43.2965, longitude=5.3698, owner_id=1, id=4)

    # Marseille (id=4) is locked at final position 3.
    # Group sizes: H1 (size 3), H2 (size 1), H3 (size 1).
    # Reference cumulative sizes: [0, 3, 4, 5].
    # target_pos = 3 is in range [3, 4) which corresponds to Lyon (index 1).
    # H3 (Marseille) gets locked at index 1.
    # So optimized hotels will be [H1, H3, H2].
    # Expected sequence: H1 -> Versailles -> H1 -> H3 -> H2
    locked = {4: 3}
    sequence = optimize_with_hotels(
        [p1, p2, p3, p4], locked_positions=locked, max_distance=100.0
    )

    assert len(sequence) == 6
    assert [p.id for p in sequence] == [1, 2, 1, 4, 3, 1]
