from typing import List
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from dataobject.place import Place
from services.algorithm.distance import haversine


def optimize(
    places: List[Place], locked_positions: dict[int, int] = None
) -> List[Place]:
    """Returns an ordered list of Places representing the optimal tour.

    Uses Google OR-Tools Routing library to solve the Traveling Salesperson
    Problem (TSP) to near-optimality, respecting optional locked positions.

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

    # Map place ID to Place object
    place_by_id = {p.id: p for p in places if p.id is not None}

    # Identify if a start place is locked at position 0
    start_place_id = None
    for pid, pos in locked_positions.items():
        if pid in place_by_id and pos == 0:
            start_place_id = pid
            break

    # Reorder places to put the locked start place at index 0
    ordered_places = list(places)
    if start_place_id is not None:
        start_place = place_by_id[start_place_id]
        ordered_places.remove(start_place)
        ordered_places.insert(0, start_place)

    # Re-map positions to indices in the ordered list
    place_to_idx = {
        p.id: idx for idx, p in enumerate(ordered_places) if p.id is not None
    }

    # Filter and validate other locked positions
    valid_locks = {}  # node_index -> target_position
    used_positions = set()

    if start_place_id is not None:
        valid_locks[0] = 0
        used_positions.add(0)

    for pid, pos in locked_positions.items():
        if pid == start_place_id:
            continue
        if pid in place_to_idx and 0 <= pos < num_places:
            idx = place_to_idx[pid]
            if pos not in used_positions:
                valid_locks[idx] = pos
                used_positions.add(pos)

    # 1. Precompute the distance matrix in meters (integer values)
    # This avoids crossing the Python-C++ language boundary inside the solver loop.
    dist_matrix = [
        [
            int(haversine(ordered_places[i], ordered_places[j]) * 1000)
            for j in range(num_places)
        ]
        for i in range(num_places)
    ]

    # 2. Create the routing index manager:
    # (num_nodes, num_vehicles, start_node, end_node)
    manager = pywrapcp.RoutingIndexManager(num_places, 1, 0)

    # 3. Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # 4. Register transit matrix directly.
    transit_callback_index = routing.RegisterTransitMatrix(dist_matrix)

    # 5. Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 6. Apply locks constraints if present
    if valid_locks:
        # Define a dimension to track step counts
        routing.AddConstantDimension(
            1,  # increment of 1 per step
            num_places + 1,  # capacity
            True,  # fix_start_cumul_to_zero
            "Step",
        )
        step_dimension = routing.GetDimensionOrDie("Step")
        for node_idx, pos in valid_locks.items():
            index = manager.NodeToIndex(node_idx)
            step_dimension.CumulVar(index).SetValue(pos)

    # 7. Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    if valid_locks:
        # Automatic works best when dimensions are constrained
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
        )
    else:
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
        )

    # 8. Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # 9. Extract the route.
    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(ordered_places[node])
            index = solution.Value(routing.NextVar(index))
        return route
    else:
        # Fallback to the ordered_places list if no solution is found
        return list(ordered_places)
