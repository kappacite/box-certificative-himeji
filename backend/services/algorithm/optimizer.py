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

    # 1. Create the routing index manager:
    # (num_nodes, num_vehicles, start_node, end_node)
    manager = pywrapcp.RoutingIndexManager(num_places, 1, 0)

    # 2. Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # 3. Create and register a transit callback.
    # Distances in OR-Tools must be integers. We scale to meters (dist * 1000) to keep precision.
    def distance_callback(from_index: int, to_index: int) -> int:
        """Returns the scaled distance between two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        dist_km = haversine(places[from_node], places[to_node])
        return int(dist_km * 1000)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # 4. Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 5. Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # 6. Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # 7. Extract the route.
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
