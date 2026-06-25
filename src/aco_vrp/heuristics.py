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
    raise NotImplementedError("Nearest Neighbor heuristic not yet implemented.")


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
    raise NotImplementedError("Clarke-Wright Savings heuristic not yet implemented.")
