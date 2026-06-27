"""
Baseline heuristics for the Capacitated Vehicle Routing Problem.

Provides constructive and improvement heuristics used as comparison
baselines against ACO in the scalability experiment. All heuristics
operate on CVRPInstance and return CVRPSolution.

Functions:
    nearest_neighbor    Greedy constructive heuristic: at each step, visit
                        the nearest unvisited customer that does not violate
                        capacity constraints.
    clarke_wright_savings   Savings-based constructive heuristic: merge
                            routes based on distance savings until no
                            feasible merges remain.
"""

from aco_vrp.problem import CVRPInstance, CVRPSolution


def nearest_neighbor(instance: CVRPInstance) -> CVRPSolution:
    """
    Construct a CVRP solution using the Nearest Neighbor heuristic.

    Starting from the depot, repeatedly visits the closest unvisited
    customer whose demand fits within the remaining vehicle capacity.
    When no customer can be served, returns to the depot and dispatches
    a new vehicle.

    Args:
        instance: The CVRP problem instance.

    Returns:
        A CVRPSolution with the constructed routes and total distance.
    """
    routes: list[list[int]] = []
    unvisited = set(range(1, len(instance.customers) + 1))

    while unvisited:
        route: list[int] = []
        current_load = 0.0
        current_pos = 0

        while True:
            nearest = None
            nearest_dist = float("inf")

            for node in unvisited:
                demand = instance.customers[node - 1].demand
                if current_load + demand > instance.vehicle_capacity:
                    continue
                dist = instance.distance(current_pos, node)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = node

            if nearest is None:
                break

            route.append(nearest)
            current_load += instance.customers[nearest - 1].demand
            current_pos = nearest
            unvisited.remove(nearest)

        if route:
            routes.append(route)

    solution = CVRPSolution(routes=routes)
    solution.vehicle_count = len(routes)
    solution.total_distance = solution.compute_distance(instance)
    solution.feasible = solution.is_feasible(instance)
    return solution


def clarke_wright_savings(instance: CVRPInstance) -> CVRPSolution:
    """
    Construct a CVRP solution using the Clarke-Wright Savings algorithm.

    Initializes one route per customer (depot to customer to depot), then
    iteratively merges the pair of routes yielding the largest distance
    savings, subject to capacity constraints.

    Args:
        instance: The CVRP problem instance.

    Returns:
        A CVRPSolution with the merged routes and total distance.
    """
    n = len(instance.customers)
    if n == 0:
        solution = CVRPSolution(routes=[])
        solution.vehicle_count = 0
        solution.total_distance = 0.0
        solution.feasible = True
        return solution

    customer_route: dict[int, list[int]] = {i: [i] for i in range(1, n + 1)}

    savings: list[tuple[float, int, int]] = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            saving = instance.distance(0, i) + instance.distance(0, j) - instance.distance(i, j)
            savings.append((saving, i, j))

    savings.sort(key=lambda x: x[0], reverse=True)

    def route_demand(route: list[int]) -> float:
        return sum(instance.customers[node - 1].demand for node in route)

    for _saving, i, j in savings:
        route_i = customer_route[i]
        route_j = customer_route[j]

        if route_i is route_j:
            continue

        i_is_endpoint = route_i[0] == i or route_i[-1] == i
        j_is_endpoint = route_j[0] == j or route_j[-1] == j
        if not (i_is_endpoint and j_is_endpoint):
            continue

        if route_demand(route_i) + route_demand(route_j) > instance.vehicle_capacity:
            continue

        if route_i[-1] == i and route_j[0] == j:
            merged = route_i + route_j
        elif route_j[-1] == j and route_i[0] == i:
            merged = route_j + route_i
        else:
            continue

        for node in merged:
            customer_route[node] = merged

    seen_routes: set[int] = set()
    routes: list[list[int]] = []
    for node in range(1, n + 1):
        route = customer_route[node]
        route_id = id(route)
        if route_id not in seen_routes:
            seen_routes.add(route_id)
            routes.append(route)

    solution = CVRPSolution(routes=routes)
    solution.vehicle_count = len(routes)
    solution.total_distance = solution.compute_distance(instance)
    solution.feasible = solution.is_feasible(instance)
    return solution
