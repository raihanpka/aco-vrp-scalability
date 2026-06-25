"""
Core Ant Colony Optimization algorithm for the Capacitated Vehicle Routing
Problem.

Implements the standard ACO metaheuristic: ant-based constructive solution
building guided by pheromone trails (tau) and heuristic information (eta),
followed by pheromone evaporation and deposition. Parameterized by alpha
(pheromone weight), beta (heuristic weight), and rho (evaporation rate).

Classes:
    ACOConfig      Parameter container for alpha, beta, rho, ant_count,
                   and max_iterations.
    Ant            Single ant agent that builds a complete CVRP solution.
    ACO            Top-level orchestrator that manages the pheromone
                   matrix, dispatches ants per iteration, and applies
                   evaporation and elitist deposition.

The implementation follows Dorigo and Stutzle (2004) with standard
extensions for CVRP constraints: capacity feasibility check during
solution construction, route-level vehicle count tracking, and optional
2-opt local search.
"""

from dataclasses import dataclass


@dataclass
class ACOConfig:
    """
    Configuration parameters for the ACO algorithm.

    Attributes:
        alpha: Pheromone trail weight (default 1.0).
        beta: Heuristic information weight (default 2.0).
        rho: Pheromone evaporation rate in (0, 1] (default 0.1).
        ant_count: Number of ants per iteration (default 10).
        max_iterations: Maximum number of iterations (default 200).
        initial_pheromone: Initial pheromone value on all edges.
        q0: Exploitation probability for pseudorandom proportional rule.
        use_local_search: Whether to apply 2-opt after construction.
    """

    alpha: float = 1.0
    beta: float = 2.0
    rho: float = 0.1
    ant_count: int = 10
    max_iterations: int = 200
    initial_pheromone: float = 1.0
    q0: float = 0.0
    use_local_search: bool = True
