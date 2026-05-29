from typing import List
from dataclasses import replace
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
        return [replace(p) for p in places]

    places = [replace(p) for p in places]
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
        [int(haversine(places[i], places[j]) * 1000) for j in range(num_places)]
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
            1,  # increment per step
            num_places + 1,  # capacity (max step count)
            True,  # fix_start_cumul_to_zero
            "Steps",
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
        initial_route_nodes = [
            place_to_idx[p.id] for p in initial_route if p.id in place_to_idx
        ]
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
            solution = routing.SolveFromAssignmentWithParameters(
                assignment, search_parameters
            )

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


def resolve_hotel_locks(
    hotels: List[Place],
    hotel_round_trips: dict[int, List[Place]],
    locked_positions: dict[int, int],
) -> dict[int, int]:
    """Translates locked positions of places to hotel locked positions.

    Allows locking non-hotel places (round-trip destinations) at a given index
    in the final sequence by mapping that index back to the index of its
    covering hotel in the hotel sequence.
    """
    if not locked_positions or len(hotels) <= 1:
        return {}

    num_hotels = len(hotels)
    start_hotel = hotels[0]

    # Calculate cumulative group sizes in reference order
    cum_sizes = [0]
    for h in hotels:
        group_size = 1 + 2 * len(hotel_round_trips.get(h.id, []))
        cum_sizes.append(cum_sizes[-1] + group_size)

    def map_final_to_hotel_pos(final_pos: int) -> int:
        for idx in range(num_hotels):
            if cum_sizes[idx] <= final_pos < cum_sizes[idx + 1]:
                return idx
        if final_pos >= cum_sizes[-1]:
            return num_hotels - 1
        return 0

    # Group locked places by their covering hotel
    place_to_hotel = {}
    for h in hotels:
        place_to_hotel[h.id] = h
        for rt in hotel_round_trips.get(h.id, []):
            place_to_hotel[rt.id] = h

    # Map requested locked positions
    hotel_requests = {}  # hotel_id -> list of requested hotel positions
    used_positions = set()

    # The starting hotel is always locked at position 0.
    assigned_locks = {start_hotel.id: 0}
    used_positions.add(0)

    # Let's map target position 0 explicitly to starting hotel
    for pid, final_pos in locked_positions.items():
        covering_hotel = place_to_hotel.get(pid)
        if covering_hotel is None:
            continue
        if final_pos == 0 or covering_hotel.id == start_hotel.id:
            continue

        hotel_pos = map_final_to_hotel_pos(final_pos)
        # Ensure it doesn't map to 0 (which is reserved for start_hotel)
        hotel_pos = max(1, min(num_hotels - 1, hotel_pos))
        hotel_requests.setdefault(covering_hotel.id, []).append(hotel_pos)

    if not hotel_requests:
        return assigned_locks

    # For each hotel, take the average of its requested positions
    locked_hotels_list = []
    for hid, reqs in hotel_requests.items():
        avg_req = sum(reqs) / len(reqs)
        locked_hotels_list.append({"id": hid, "req": avg_req})

    # Sort locked hotels by their requested position
    locked_hotels_list.sort(key=lambda x: x["req"])

    # Assign unique positions in range [1, num_hotels - 1]
    for item in locked_hotels_list:
        # Find nearest available position in [1, num_hotels - 1]
        best_pos = None
        best_dist = float("inf")
        for pos in range(1, num_hotels):
            if pos not in used_positions:
                dist = abs(pos - item["req"])
                if dist < best_dist:
                    best_dist = dist
                    best_pos = pos
        if best_pos is not None:
            assigned_locks[item["id"]] = best_pos
            used_positions.add(best_pos)

    return assigned_locks


def optimize_with_hotels(
    places: List[Place],
    locked_positions: dict[int, int] = None,
    max_distance: float = 100.0,
) -> List[Place]:
    """Optimizes a tour by grouping nearby places into clusters with one hotel each.

    Returns the complete sequence of movements including round trips from hotels.
    The tour is optimized among hotels, and round trips to other places are counted.

    Args:
        places: List of Place data objects. The first place is the start/end point (first hotel).
        locked_positions: Optional dictionary mapping place ID to target position index.
        max_distance: Maximum distance in km for a place to be covered by a hotel.

    Returns:
        The sequence of places representing the full itinerary of movements.
    """
    if not places:
        return []
    places = [replace(p) for p in places]

    if len(places) <= 1:
        res = list(places)
        for p in res:
            p.is_hotel = True
        return res

    if max_distance <= 0.0:
        res = optimize(places, locked_positions)
        for p in res:
            p.is_hotel = True
        if res and res[-1].id != res[0].id:
            res.append(res[0])
        return res

    # 1. Greedy Set Cover to select hotels.
    # The first place (start point) MUST be a hotel.
    hotels = [places[0]]
    covered_ids = {places[0].id}

    # Calculate initially covered places by the start hotel
    for p in places:
        if haversine(places[0], p) <= max_distance:
            covered_ids.add(p.id)

    # Find hotels for the remaining uncovered places
    all_place_ids = {p.id for p in places}

    while not all_place_ids.issubset(covered_ids):
        best_candidate = None
        best_covered = set()

        # We can select any place as a hotel (including currently covered ones,
        # to maximize the coverage of remaining uncovered places).
        for candidate in places:
            if candidate.id in [h.id for h in hotels]:
                continue

            # Find which UNCOVERED places this candidate covers
            covers = {
                p.id
                for p in places
                if p.id not in covered_ids and haversine(candidate, p) <= max_distance
            }

            if len(covers) > len(best_covered):
                best_covered = covers
                best_candidate = candidate
            elif len(covers) == len(best_covered) and len(covers) > 0:
                # Tie-breaker: prefer the one that appears earlier in the input list
                if best_candidate is None or places.index(candidate) < places.index(
                    best_candidate
                ):
                    best_candidate = candidate
                    best_covered = covers

        if best_candidate is None:
            # If no candidate covers anything new, pick first uncovered place.
            uncovered_list = [p for p in places if p.id not in covered_ids]
            if uncovered_list:
                best_candidate = uncovered_list[0]
                best_covered = {best_candidate.id}
            else:
                break

        hotels.append(best_candidate)
        covered_ids.update(best_covered)

    # 2. Assign each non-hotel place to its closest hotel.
    hotel_ids = {h.id for h in hotels}
    hotel_round_trips = {h.id: [] for h in hotels}

    for p in places:
        p.is_hotel = p.id in hotel_ids
        if p.id in hotel_ids:
            continue
        # Find closest hotel
        closest_hotel = min(hotels, key=lambda h: haversine(h, p))
        hotel_round_trips[closest_hotel.id].append(p)

    # 3. Optimize the order of the hotels.
    # Translate original locked_positions to hotel locked positions
    resolved_locks = resolve_hotel_locks(hotels, hotel_round_trips, locked_positions)
    # We pass the subset of hotels to the original optimize function.
    optimized_hotels = optimize(hotels, resolved_locks)

    # 4. Construct the full sequence of movements.
    sequence = []
    if not optimized_hotels:
        return []

    for hotel in optimized_hotels:
        sequence.append(hotel)
        # Add round trips for this hotel
        rts = hotel_round_trips.get(hotel.id, [])
        for rt_place in rts:
            sequence.append(rt_place)
            sequence.append(hotel)

    # Reconnect back to start hotel for closed loop
    if sequence and sequence[-1].id != optimized_hotels[0].id:
        sequence.append(optimized_hotels[0])

    return sequence
