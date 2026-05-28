from typing import List
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from dataobject.place import Place
from services.algorithm.distance import haversine


def run_subtour_insertion(
    places: List[Place], locked_positions: dict[int, int]
) -> List[Place]:
    """Helper to calculate a feasible starting tour using subtour insertion."""
    num_places = len(places)
    place_by_id = {p.id: p for p in places if p.id is not None}

    locked_places_dict = {}
    locked_ids = set()
    used_positions = set()
    start_place_id = None

    # 1. Lock at position 0
    for pid, pos in locked_positions.items():
        if pid in place_by_id and pos == 0:
            start_place_id = pid
            locked_places_dict[0] = place_by_id[pid]
            locked_ids.add(pid)
            used_positions.add(0)
            break

    # 2. Lock at other positions
    for pid, pos in locked_positions.items():
        if pid == start_place_id:
            continue
        if pid in place_by_id and 0 <= pos < num_places:
            if pos not in used_positions:
                locked_places_dict[pos] = place_by_id[pid]
                locked_ids.add(pid)
                used_positions.add(pos)

    unlocked_places = [p for p in places if p.id not in locked_ids]

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

    num_unlocked = len(unlocked_places)
    dist_matrix = [
        [
            int(haversine(unlocked_places[i], unlocked_places[j]) * 1000)
            for j in range(num_unlocked)
        ]
        for i in range(num_unlocked)
    ]

    try:
        manager = pywrapcp.RoutingIndexManager(num_unlocked, 1, 0)
        routing = pywrapcp.RoutingModel(manager)
        transit_callback_index = routing.RegisterTransitMatrix(dist_matrix)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
        )
        search_parameters.time_limit.seconds = 3

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


def optimize(
    places: List[Place], locked_positions: dict[int, int] = None
) -> List[Place]:
    """Returns an ordered list of Places representing the optimal tour.

    Uses Google OR-Tools Routing library to solve the Traveling Salesperson
    Problem (TSP) to near-optimality, respecting optional locked positions.
    To avoid solver failures or timeouts under hard cumulative constraints,
    the solver is 'warm-started' with a feasible starting solution constructed
    via a fast sub-tour insertion algorithm.

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

    # 1. Generate feasible starting route using Subtour Insertion
    initial_route = run_subtour_insertion(places, valid_locks)

    if len(places) <= 2:
        return initial_route

    # 2. Build global distance matrix
    dist_matrix = [
        [
            int(haversine(places[i], places[j]) * 1000)
            for j in range(num_places)
        ]
        for i in range(num_places)
    ]

    # Map place ID to its index in input places
    place_to_idx = {p.id: idx for idx, p in enumerate(places) if p.id is not None}

    # Start node for OR-Tools routing model (taken from initial route start)
    start_place_id = initial_route[0].id
    start_node = place_to_idx.get(start_place_id, 0)

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
                continue
            node_idx = place_to_idx.get(pid)
            if node_idx is not None:
                index = manager.NodeToIndex(node_idx)
                steps_dimension.CumulVar(index).SetValue(pos)

        # Convert initial_route to node indices list (excluding start node)
        initial_route_nodes = [place_to_idx[p.id] for p in initial_route if p.id in place_to_idx]
        initial_route_nodes = initial_route_nodes[1:]

        # Read assignment from initial route
        assignment = routing.ReadAssignmentFromRoutes([initial_route_nodes], True)

        if assignment:
            # Set search parameters with Local Search Metaheuristic
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.time_limit.seconds = 3
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )

            # Solve from assignment
            solution = routing.SolveFromAssignmentWithParameters(assignment, search_parameters)

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

    # Fallback to subtour insertion if warmstart fails
    return initial_route
