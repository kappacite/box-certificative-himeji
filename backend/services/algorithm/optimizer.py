from typing import List
from dataobject.place import Place
from services.algorithm.distance import haversine


def _calculate_total_distance(tour: List[Place]) -> float:
    """Calculate the total closed loop distance of a tour.

    Args:
        tour: The ordered list of places.

    Returns:
        The total distance in km.
    """
    if len(tour) <= 1:
        return 0.0
    total = 0.0
    for i in range(len(tour) - 1):
        total += haversine(tour[i], tour[i + 1])
    # Closed loop: return to the start
    total += haversine(tour[-1], tour[0])
    return total


def _nearest_neighbour(places: List[Place]) -> List[Place]:
    """Nearest Neighbour heuristic to build an initial tour.

    Args:
        places: Unordered list of places.

    Returns:
        A list of places ordered by nearest neighbor.
    """
    if len(places) <= 1:
        return list(places)

    unvisited = list(places)
    current = unvisited.pop(0)  # Start at the first place
    tour = [current]

    while unvisited:
        closest = min(unvisited, key=lambda p: haversine(current, p))
        unvisited.remove(closest)
        tour.append(closest)
        current = closest

    return tour


def _two_opt(tour: List[Place]) -> List[Place]:
    """2-opt local search to improve the tour.

    Args:
        tour: The initial tour.

    Returns:
        An optimized tour.
    """
    n = len(tour)
    if n <= 3:
        return tour

    improved = True
    best_tour = list(tour)

    # To prevent infinite loop, set a limit on iterations
    max_iterations = 200
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # We reverse the segment between i and j
                # new_tour = best_tour[0:i] + reversed(best_tour[i:j+1]) + best_tour[j+1:]

                # Check change in distance:
                # Old edges: tour[i-1]->tour[i] and tour[j]->tour[(j+1)%n]
                # New edges: tour[i-1]->tour[j] and tour[i]->tour[(j+1)%n]
                p_prev = best_tour[i - 1]
                p_i = best_tour[i]
                p_j = best_tour[j]
                p_next = best_tour[(j + 1) % n]

                old_dist = haversine(p_prev, p_i) + haversine(p_j, p_next)
                new_dist = haversine(p_prev, p_j) + haversine(p_i, p_next)

                if new_dist < old_dist - 1e-6:  # Floating point safety margin
                    # Reconstruct the tour with the reversed segment
                    best_tour[i : j + 1] = reversed(best_tour[i : j + 1])
                    improved = True
                    break  # Start over with the new best tour
            if improved:
                break

    return best_tour


def optimize(places: List[Place]) -> List[Place]:
    """Returns an ordered list of Places representing the optimal tour.

    Exposes the main entry point for the TSP optimization.
    First uses the Nearest Neighbour heuristic to build an initial tour,
    then applies 2-opt local search for further refinement.

    Args:
        places: A list of Place data objects to optimize.

    Returns:
        An ordered list of Place data objects representing the optimal tour.
    """
    if len(places) <= 1:
        return list(places)

    # 1. Generate initial tour using Nearest Neighbour
    initial_tour = _nearest_neighbour(places)

    # 2. Refine tour using 2-opt
    optimized_tour = _two_opt(initial_tour)

    return optimized_tour
