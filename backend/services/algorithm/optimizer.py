from typing import List
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from dataobject.place import Place
from services.algorithm.distance import haversine


def optimize(places: List[Place]) -> List[Place]:
    """Returns an ordered list of Places representing the optimal tour.

    Uses Google OR-Tools Routing library to solve the Traveling Salesperson
    Problem (TSP) to near-optimality.

    Args:
        places: A list of Place data objects to optimize.

    Returns:
        An ordered list of Place data objects representing the optimal tour.
    """
    if len(places) <= 1:
        return list(places)

    num_places = len(places)

    # 1. Precompute the distance matrix in meters (integer values)
    # This avoids crossing the Python-C++ language boundary inside the solver loop.
    dist_matrix = [
        [int(haversine(places[i], places[j]) * 1000) for j in range(num_places)]
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

    # 6. Setting first solution heuristic.
    # Christofides strategy is highly efficient for metric TSP and is faster
    # and more precise than PATH_CHEAPEST_ARC on geometric instances.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
    )

    # 7. Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # 8. Extract the route.
    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(places[node])
            index = solution.Value(routing.NextVar(index))
        return route
    else:
        # Fallback to the original order if no solution is found
        return list(places)
