from typing import List
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from dataobject.place import Place
from services.algorithm.distance import haversine


def fallback_reconstruction(
    places: List[Place], locked_positions: dict[int, int]
) -> List[Place]:
    """Helper fallback to reconstruct the tour if the solver cannot find a solution.

    Places locked positions are respected, and the remaining slots are filled
    with the unlocked places in their input order.
    """
    num_places = len(places)
    place_by_id = {p.id: p for p in places if p.id is not None}

    final_route = [None] * num_places
    used_ids = set()

    # Place locked nodes
    for pid, pos in locked_positions.items():
        if pid in place_by_id and 0 <= pos < num_places:
            final_route[pos] = place_by_id[pid]
            used_ids.add(pid)

    # Unlocked nodes
    unlocked_places = [p for p in places if p.id not in used_ids]

    unlocked_idx = 0
    for i in range(num_places):
        if final_route[i] is None:
            if unlocked_idx < len(unlocked_places):
                final_route[i] = unlocked_places[unlocked_idx]
                unlocked_idx += 1

    return [p for p in final_route if p is not None]


def optimize(
    places: List[Place], locked_positions: dict[int, int] = None
) -> List[Place]:
    """Returns an ordered list of Places representing the optimal tour.

    Uses Google OR-Tools Routing library to solve the Traveling Salesperson
    Problem (TSP) to near-optimality, respecting optional locked positions.
    To satisfy position constraints, a global cumulative Steps dimension is used,
    forcing locked places to be visited at their designated step/rank.

    Args:
        places: A list of Place data objects to optimize.
        locked_positions: A dictionary mapping place ID to its locked index in
          the tour.

    Returns:
        An ordered list of Place data objects representing the optimal tour.
    """
    if len(places) <= 1:
        return list(places)

    num_places = len(places)

    if not locked_positions:
        locked_positions = {}

    # Map place ID to Place object and index in input list
    place_by_id = {p.id: p for p in places if p.id is not None}

    # Sanitize locked positions
    valid_locks = {}
    used_positions = set()
    start_place_id = None

    # First find if there is a lock at position 0
    for pid, pos in locked_positions.items():
        if pid in place_by_id and pos == 0:
            start_place_id = pid
            valid_locks[pid] = 0
            used_positions.add(0)
            break

    # Extract all other valid locked positions
    for pid, pos in locked_positions.items():
        if pid == start_place_id:
            continue
        if pid in place_by_id and 0 <= pos < num_places:
            if pos not in used_positions:
                valid_locks[pid] = pos
                used_positions.add(pos)

    # Determine start place for the vehicle (must end up at position 0)
    if start_place_id is None:
        # Find the first place that does not have a lock at pos > 0
        for p in places:
            if p.id not in valid_locks:
                start_place_id = p.id
                break
        if start_place_id is None:
            start_place_id = places[0].id

    # Get index of start place in input list
    start_node = 0
    for idx, p in enumerate(places):
        if p.id == start_place_id:
            start_node = idx
            break

    # Build global distance matrix
    dist_matrix = [
        [
            int(haversine(places[i], places[j]) * 1000)
            for j in range(num_places)
        ]
        for i in range(num_places)
    ]

    try:
        manager = pywrapcp.RoutingIndexManager(num_places, 1, start_node)
        routing = pywrapcp.RoutingModel(manager)
        transit_callback_index = routing.RegisterTransitMatrix(dist_matrix)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Steps dimension tracking cumulative sequence position of visited nodes
        routing.AddConstantDimension(
            1,              # increment per step
            num_places + 1,  # capacity (max step count)
            True,           # fix_start_cumul_to_zero
            "Steps"
        )
        steps_dimension = routing.GetDimensionOrDie("Steps")

        # Constrain locked places to their specified index
        for pid, pos in valid_locks.items():
            if pid == start_place_id:
                # Already guaranteed by setting start_node as vehicle start
                continue
            # Find node index in `places`
            node_idx = None
            for idx, p in enumerate(places):
                if p.id == pid:
                    node_idx = idx
                    break
            if node_idx is not None:
                index = manager.NodeToIndex(node_idx)
                steps_dimension.CumulVar(index).SetValue(pos)

        # Set first solution heuristic and search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
        )
        # Set a safety time limit on the solver
        search_parameters.time_limit.seconds = 3

        # Solve
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            optimized_places = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                optimized_places.append(places[node])
                index = solution.Value(routing.NextVar(index))
            return optimized_places
    except Exception:
        pass

    # Fallback if solver fails or raises exception
    return fallback_reconstruction(places, valid_locks)
