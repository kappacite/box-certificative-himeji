from services.algorithm.optimizer import optimize
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
