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

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from aco_vrp.problem import CVRPInstance, CVRPSolution


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


class ACO:
    """
    Ant Colony Optimization solver for CVRP.

    Manages pheromone matrix, ant solution construction, evaporation,
    elitist deposition, optional 2-opt local search, and convergence
    tracking.
    """

    def __init__(self, config: ACOConfig) -> None:
        self.config = config
        self.rng: random.Random | None = None
        self.convergence_history: list[float] = []
        self.route_history: list[list[list[int]]] = []
        self.pheromone_snapshots: list[np.ndarray] = []

    def solve(self, instance: CVRPInstance, seed: int = 0) -> CVRPSolution:
        """
        Run the ACO algorithm on the given CVRP instance.

        Args:
            instance: The CVRP problem instance.
            seed: Random seed for reproducibility.

        Returns:
            The best CVRPSolution found across all iterations.
        """
        self.rng = random.Random(seed)
        n = len(instance.customers) + 1  # +1 for depot (node 0)

        # Precompute distance matrix and heuristic information
        dist = instance.distance_matrix()
        with np.errstate(divide="ignore", invalid="ignore"):
            eta = 1.0 / dist
        np.fill_diagonal(eta, 0.0)

        # Initialize pheromone matrix
        tau = np.full((n, n), self.config.initial_pheromone, dtype=np.float64)

        # Extract demands into a numpy array for fast indexing
        # demands[k] corresponds to customer node index k+1
        demands = np.array([c.demand for c in instance.customers], dtype=np.float64)

        global_best_sol = CVRPSolution()
        global_best_dist = float("inf")
        self.convergence_history = []
        self.route_history = []
        self.pheromone_snapshots = []

        for iteration_counter in range(self.config.max_iterations):
            iteration_solutions: list[CVRPSolution] = []
            iteration_distances: list[float] = []

            # Each ant constructs a solution
            for _ in range(self.config.ant_count):
                sol = self._construct_solution(instance, tau, eta, demands)
                dist_val = sol.compute_distance(instance)
                sol.total_distance = dist_val
                sol.feasible = sol.is_feasible(instance)
                sol.vehicle_count = len(sol.routes)
                iteration_solutions.append(sol)
                iteration_distances.append(dist_val)

            # Identify best solution of this iteration
            best_idx = int(np.argmin(iteration_distances))
            best_iter_sol = iteration_solutions[best_idx]
            best_iter_dist = iteration_distances[best_idx]

            # Optional 2-opt local search on the iteration best
            if self.config.use_local_search:
                improved_routes: list[list[int]] = []
                total_after_2opt = 0.0
                for route in best_iter_sol.routes:
                    improved = (
                        self._apply_two_opt(route, instance)
                        if len(route) > 2
                        else route[:]
                    )
                    improved_routes.append(improved)
                    if improved:
                        rd = instance.distance(0, improved[0])
                        for k in range(len(improved) - 1):
                            rd += instance.distance(improved[k], improved[k + 1])
                        rd += instance.distance(improved[-1], 0)
                        total_after_2opt += rd

                if improved_routes:
                    best_iter_sol = CVRPSolution(
                        routes=improved_routes,
                        total_distance=total_after_2opt,
                        vehicle_count=len(improved_routes),
                        feasible=False,
                    )
                    best_iter_sol.feasible = best_iter_sol.is_feasible(instance)
                    best_iter_dist = best_iter_sol.total_distance

            # Update global best
            if best_iter_dist < global_best_dist:
                global_best_dist = best_iter_dist
                global_best_sol = CVRPSolution(
                    routes=[r[:] for r in best_iter_sol.routes],
                    total_distance=best_iter_dist,
                    vehicle_count=best_iter_sol.vehicle_count,
                    feasible=best_iter_sol.feasible,
                )

            self.convergence_history.append(global_best_dist)
            self.route_history.append([r[:] for r in global_best_sol.routes])

            # Pheromone evaporation
            tau *= 1.0 - self.config.rho

            # Elitist pheromone deposition on best iteration solution
            deposit = (
                1.0 / best_iter_sol.total_distance
                if best_iter_sol.total_distance > 0
                else 1.0
            )
            for route in best_iter_sol.routes:
                if not route:
                    continue
                prev = 0
                for node in route:
                    tau[prev, node] += deposit
                    tau[node, prev] += deposit
                    prev = node
                tau[prev, 0] += deposit
                tau[0, prev] += deposit

            if (iteration_counter + 1) % 5 == 0:
                self.pheromone_snapshots.append(tau.copy())

        # Finalize global best solution fields
        global_best_sol.total_distance = global_best_dist
        global_best_sol.vehicle_count = len(global_best_sol.routes)
        global_best_sol.feasible = global_best_sol.is_feasible(instance)

        return global_best_sol

    def _construct_solution(
        self,
        instance: CVRPInstance,
        tau: np.ndarray,
        eta: np.ndarray,
        demands: np.ndarray,
    ) -> CVRPSolution:
        """
        Build a single ant's solution using the pseudorandom proportional rule.

        Args:
            instance: The CVRP instance.
            tau: Pheromone matrix.
            eta: Heuristic information matrix.
            demands: Precomputed customer demands array.

        Returns:
            A newly constructed CVRPSolution.
        """
        n_customers = len(instance.customers)
        unvisited = set(range(1, n_customers + 1))
        routes: list[list[int]] = []

        while unvisited:
            current_route: list[int] = []
            current_load = 0.0
            current_node = 0

            while True:
                # Build list of feasible (unvisited and capacity-compliant) customers
                feasible = [
                    j
                    for j in unvisited
                    if current_load + demands[j - 1] <= instance.vehicle_capacity
                ]
                if not feasible:
                    break

                feasible_arr = np.array(feasible, dtype=np.int64)
                tau_vals = tau[current_node, feasible_arr]
                eta_vals = eta[current_node, feasible_arr]

                # Compute scores: tau^alpha * eta^beta
                scores = np.power(tau_vals, self.config.alpha) * np.power(
                    eta_vals, self.config.beta
                )
                scores = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)

                total_score = float(np.sum(scores))
                if total_score <= 0.0:
                    # Fallback to uniform random selection among feasible
                    chosen = self.rng.choice(feasible)  # type: ignore[union-attr]
                else:
                    q = self.rng.random()  # type: ignore[union-attr]
                    if q < self.config.q0:
                        # Exploitation: select highest score
                        chosen = int(feasible_arr[int(np.argmax(scores))])
                    else:
                        # Exploration: roulette-wheel selection
                        probs = scores / total_score
                        chosen = self.rng.choices(  # type: ignore[union-attr]
                            feasible, weights=probs.tolist(), k=1
                        )[0]

                current_route.append(chosen)
                current_load += demands[chosen - 1]
                unvisited.remove(chosen)
                current_node = chosen

            if current_route:
                routes.append(current_route)

        return CVRPSolution(routes=routes)

    def _apply_two_opt(
        self, route: list[int], instance: CVRPInstance
    ) -> list[int]:
        """
        Apply the 2-opt local search to a single route.

        Tries reversing every segment i..j and accepts the move if it
        reduces the total route distance (including depot connections).

        Args:
            route: List of customer node indices (1..N).
            instance: The CVRP instance for distance lookups.

        Returns:
            An improved route (or the original if no improvement found).
        """
        if len(route) < 3:
            return route[:]

        best = route[:]
        dist = instance.distance_matrix()
        improved = True

        while improved:
            improved = False
            route_len = len(best)
            for i in range(route_len - 1):
                for j in range(i + 2, route_len):
                    prev_node = 0 if i == 0 else best[i - 1]
                    next_node = 0 if j == route_len - 1 else best[j + 1]

                    old_dist = dist[prev_node, best[i]] + dist[best[j], next_node]
                    new_dist = dist[prev_node, best[j]] + dist[best[i], next_node]

                    if new_dist < old_dist - 1e-9:
                        best[i : j + 1] = best[i : j + 1][::-1]
                        improved = True
                        break
                if improved:
                    break

        return best
