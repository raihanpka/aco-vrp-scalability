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
    CVRPSolution   A feasible or infeasible solution: list of routes,
                   total distance, vehicle count.

Node index convention (used by distance() and routes):
    0       = depot
    1..N    = customers (customer with 0-based index i has node index i+1)
"""

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


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
        customers: List of customer nodes (0-based indexing).
        vehicle_capacity: Maximum load per vehicle.
        max_vehicles: Upper bound on number of vehicles (optional).
    """

    name: str
    depot: Depot
    customers: list[Customer]
    vehicle_capacity: float
    max_vehicles: int | None = None

    def distance(self, node1: int, node2: int) -> float:
        """
        Euclidean distance between two nodes.

        Node 0 is the depot; nodes 1..N are customers, where customer
        with 0-based index i has node index i+1.

        Args:
            node1: First node index (0 = depot, 1..N = customer).
            node2: Second node index (0 = depot, 1..N = customer).

        Returns:
            Euclidean distance as a float.
        """
        if node1 == node2:
            return 0.0
        x1, y1 = (self.depot.x, self.depot.y) if node1 == 0 else (self.customers[node1 - 1].x, self.customers[node1 - 1].y)
        x2, y2 = (self.depot.x, self.depot.y) if node2 == 0 else (self.customers[node2 - 1].x, self.customers[node2 - 1].y)
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def distance_matrix(self) -> np.ndarray:
        """
        Compute the full (N+1) x (N+1) distance matrix for all nodes.

        Row and column 0 correspond to the depot; rows/columns 1..N
        correspond to customers. The matrix is symmetric.

        Returns:
            2-D numpy array of shape (N+1, N+1).
        """
        n = len(self.customers) + 1
        mat = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                mat[i, j] = self.distance(i, j)
        return mat

    def subset(self, n: int) -> "CVRPInstance":
        """
        Return a new instance containing only the first n customers.

        Args:
            n: Number of customers to keep (must be <= len(customers)).

        Returns:
            A new CVRPInstance with customers[:n] and name suffixed by _n.
        """
        if n > len(self.customers):
            raise ValueError(f"Requested subset size {n} exceeds instance size {len(self.customers)}")
        return CVRPInstance(
            name=f"{self.name}_{n}",
            depot=self.depot,
            customers=self.customers[:n],
            vehicle_capacity=self.vehicle_capacity,
            max_vehicles=self.max_vehicles,
        )


@dataclass
class CVRPSolution:
    """
    A complete solution to a CVRP instance.

    Routes contain 1-based node indices matching the distance() convention:
    node 0 is the depot (implicit start/end), nodes 1..N are customers.

    Attributes:
        routes: List of routes; each route is a sequence of node indices
                (1..N), not including the depot at start or end.
        total_distance: Sum of Euclidean distances across all routes.
        vehicle_count: Number of vehicles used.
        feasible: Whether all capacity constraints are satisfied and all
                  customers are visited exactly once.
    """

    routes: list[list[int]] = field(default_factory=list)
    total_distance: float = 0.0
    vehicle_count: int = 0
    feasible: bool = False

    def is_feasible(self, instance: CVRPInstance) -> bool:
        """
        Check that the solution satisfies capacity constraints and visits
        every customer exactly once.

        Args:
            instance: The CVRP problem instance this solution belongs to.

        Returns:
            True if all routes are capacity-feasible and all customers
            are visited exactly once; False otherwise.
        """
        visited: set[int] = set()

        for route in self.routes:
            load = 0.0
            for node_idx in route:
                # node_idx must be a valid customer node (1..N)
                if node_idx < 1 or node_idx > len(instance.customers):
                    return False
                if node_idx in visited:
                    return False
                visited.add(node_idx)
                load += instance.customers[node_idx - 1].demand
                if load > instance.vehicle_capacity:
                    return False

        # Every customer node must be visited exactly once
        return visited == set(range(1, len(instance.customers) + 1))

    def compute_distance(self, instance: CVRPInstance) -> float:
        """
        Calculate the total route distance including depot-to-first and
        last-to-depot legs for every route.

        Args:
            instance: The CVRP problem instance this solution belongs to.

        Returns:
            Total Euclidean distance as a float.
        """
        total = 0.0
        for route in self.routes:
            if not route:
                continue
            # depot → first customer
            total += instance.distance(0, route[0])
            # customer → next customer
            for i in range(len(route) - 1):
                total += instance.distance(route[i], route[i + 1])
            # last customer → depot
            total += instance.distance(route[-1], 0)
        return total


def load_solomon(path: str) -> CVRPInstance:
    """
    Parse a Solomon VRPTW benchmark text file into a CVRPInstance.

    The Solomon format is a fixed-width columnar text file:

        <instance name>
        VEHICLE
        NUMBER     CAPACITY
        <max_vehicles>  <vehicle_capacity>

        CUSTOMER
        CUST NO.  XCOORD.  YCOORD.  DEMAND  READY TIME  DUE DATE  SERVICE TIME

        0   <depot data>
        1   <customer 1 data>
        ...

    Customer 0 is the depot. All other rows are customers stored with
    0-based indexing (index = CUST NO. - 1).

    Args:
        path: Path to the Solomon instance file (e.g., "data/solomon/RC101.txt").

    Returns:
        A CVRPInstance populated from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the depot row (CUST NO. 0) is missing.
    """
    lines = Path(path).read_text().splitlines()

    name = lines[0].strip()
    max_vehicles: int | None = None
    vehicle_capacity = 0.0
    depot: Depot | None = None
    customers: list[Customer] = []

    i = 0
    while i < len(lines):
        token = lines[i].strip()

        if token == "VEHICLE":
            # Next non-blank line is "NUMBER  CAPACITY" header; skip it
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            i += 1  # skip header row
            # Next non-blank line contains the values
            while i < len(lines) and not lines[i].strip():
                i += 1
            parts = lines[i].split()
            max_vehicles = int(parts[0])
            vehicle_capacity = float(parts[1])

        elif token == "CUSTOMER":
            # Skip the column-header line and any blank lines, then read data
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            i += 1  # skip "CUST NO.  XCOORD. ..." header
            while i < len(lines) and not lines[i].strip():
                i += 1
            # Read all remaining data rows
            while i < len(lines):
                row = lines[i].strip()
                i += 1
                if not row:
                    continue
                parts = row.split()
                if len(parts) < 7:
                    continue
                cust_no = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                demand = float(parts[3])
                ready_time = float(parts[4])
                due_date = float(parts[5])
                service_time = float(parts[6])

                if cust_no == 0:
                    depot = Depot(x=x, y=y)
                else:
                    customers.append(Customer(
                        index=cust_no - 1,  # 0-based
                        x=x,
                        y=y,
                        demand=demand,
                        ready_time=ready_time,
                        due_date=due_date,
                        service_time=service_time,
                    ))
            break  # CUSTOMER section is always the last section

        i += 1

    if depot is None:
        raise ValueError(f"No depot row (CUST NO. 0) found in {path}")
    if vehicle_capacity <= 0.0:
        raise ValueError(f"VEHICLE section missing or capacity is zero in {path}")

    return CVRPInstance(
        name=name,
        depot=depot,
        customers=customers,
        vehicle_capacity=vehicle_capacity,
        max_vehicles=max_vehicles,
    )
