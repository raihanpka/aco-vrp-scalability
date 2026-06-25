"""
CVRP problem representation and Solomon benchmark instance loader.

Defines the data structures for customer locations, demands, time windows,
depot coordinates, vehicle capacity, and route-level solution representation.
Includes a parser for the standard Solomon VRPTW file format.

Classes:
    Customer       A single customer node with coordinates, demand, and
                   time window.
    Depot          The central depot with coordinates.
    CVRPInstance   Complete problem instance: customers, depot, vehicle
                   capacity, and metadata.
    CVPRSolution   A feasible or infeasible solution: list of routes,
                   total distance, vehicle count.
"""

from dataclasses import dataclass, field


@dataclass
class Customer:
    """
    A customer node in the CVRP.

    Attributes:
        index: 0-based index in the instance.
        x: X-coordinate.
        y: Y-coordinate.
        demand: Quantity of goods required.
        ready_time: Earliest service start time.
        due_date: Latest service finish time.
        service_time: Time required for service at this customer.
    """

    index: int
    x: float
    y: float
    demand: float
    ready_time: float = 0.0
    due_date: float = float("inf")
    service_time: float = 0.0


@dataclass
class Depot:
    """
    The central depot from which all vehicles start and end.

    Attributes:
        x: X-coordinate.
        y: Y-coordinate.
    """

    x: float
    y: float


@dataclass
class CVRPInstance:
    """
    A complete CVRP problem instance.

    Attributes:
        name: Instance identifier (e.g., "RC101").
        depot: Central depot coordinates.
        customers: List of customer nodes.
        vehicle_capacity: Maximum load per vehicle.
        max_vehicles: Upper bound on number of vehicles (optional).
    """

    name: str
    depot: Depot
    customers: list[Customer]
    vehicle_capacity: float
    max_vehicles: int | None = None


@dataclass
class CVRPSolution:
    """
    A complete solution to a CVRP instance.

    Attributes:
        routes: List of routes, each route is a sequence of customer indices.
        total_distance: Sum of Euclidean distances across all routes.
        vehicle_count: Number of vehicles used.
        feasible: Whether all capacity and time window constraints are satisfied.
    """

    routes: list[list[int]] = field(default_factory=list)
    total_distance: float = 0.0
    vehicle_count: int = 0
    feasible: bool = False
