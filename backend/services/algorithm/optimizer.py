from typing import List
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from dataobject.place import Place
from services.algorithm.distance import haversine


def optimize(
    places: List[Place], locked_positions: dict[int, int] = None
) -> List[Place]:
    """Returns an ordered list of Places representing the optimal tour.

    To satisfy position constraints efficiently and avoid solver timeouts or poor
    local minima on larger datasets (e.g. 200 places), a robust sub-tour
    optimization and insertion strategy is used:
    1. Filter out locked places.
    2. Optimize the remaining unlocked places using OR-Tools (solving a pure TSP).
    3. Reconstruct the final tour by inserting the locked places back into their
       designated indices.

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

    place_by_id = {p.id: p for p in places if p.id is not None}

    # Extract valid locks: target_position -> Place
    locked_places_dict = {}
    locked_ids = set()
    used_positions = set()
    start_place_id = None

    # 1. Prioritize start node lock (position 0)
    for pid, pos in locked_positions.items():
        if pid in place_by_id and pos == 0:
            start_place_id = pid
            locked_places_dict[0] = place_by_id[pid]
            locked_ids.add(pid)
            used_positions.add(0)
            break

    # 2. Extract other locked positions
    for pid, pos in locked_positions.items():
        if pid == start_place_id:
            continue
        if pid in place_by_id and 0 <= pos < num_places:
            if pos not in used_positions:
                locked_places_dict[pos] = place_by_id[pid]
                locked_ids.add(pid)
                used_positions.add(pos)

    # 3. Filter unlocked places
    unlocked_places = [p for p in places if p.id not in locked_ids]

    # 4. If all places are locked, or only 1 is unlocked, reconstruct directly
    if len(unlocked_places) <= 1:
        final_route = [None] * num_places
        for pos, place in locked_places_dict.items():
            final_route[pos] = place
        unlocked_idx = 0
        for i in range(num_places):
            if final_route[i] is None:
                if unlocked_idx < len(unlocked_places):
                    final_route[i] = unlocked_places[unlocked_idx]
                    unlocked_idx += 1
        return [p for p in final_route if p is not None]

    # 5. Optimize the unlocked places using OR-Tools (without locks)
    num_unlocked = len(unlocked_places)
    dist_matrix = [
        [
            int(haversine(unlocked_places[i], unlocked_places[j]) * 1000)
            for j in range(num_unlocked)
        ]
        for i in range(num_unlocked)
    ]

    try:
        # Create routing index manager: (num_nodes, num_vehicles, start_node)
        manager = pywrapcp.RoutingIndexManager(num_unlocked, 1, 0)
        routing = pywrapcp.RoutingModel(manager)
        transit_callback_index = routing.RegisterTransitMatrix(dist_matrix)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
        )
        search_parameters.time_limit.seconds = 3

        # Solve
        solution = routing.SolveWithParameters(search_parameters)

        optimized_unlocked = []
        if solution:
            index = routing.Start(0)
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                optimized_unlocked.append(unlocked_places[node])
                index = solution.Value(routing.NextVar(index))
        else:
            optimized_unlocked = list(unlocked_places)
    except Exception:
        optimized_unlocked = list(unlocked_places)

    # 6. Reconstruct final tour by inserting locked places at their positions
    final_route = [None] * num_places
    for pos, place in locked_places_dict.items():
        final_route[pos] = place

    unlocked_idx = 0
    for i in range(num_places):
        if final_route[i] is None:
            if unlocked_idx < len(optimized_unlocked):
                final_route[i] = optimized_unlocked[unlocked_idx]
                unlocked_idx += 1

    return [p for p in final_route if p is not None]
