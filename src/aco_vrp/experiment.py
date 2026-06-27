"""
Experiment orchestration for the ACO-CVRP scalability study.

Manages the full experiment matrix: 4 ACO configurations x 3 problem
sizes (25, 50, 100 customers) x 30 independent seeds, plus baseline
runs (Nearest Neighbor, Clarke-Wright Savings). Handles deterministic
seeding, parallel execution, progress logging, and result serialization.

Classes:
    ExperimentRunner    Configures and executes the full experiment matrix.

Usage:
    runner = ExperimentRunner(data_dir="data/solomon")
    results = runner.run_full_matrix(seeds=30)
    runner.save_results(results, "results/raw_runs.csv")
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any

from aco_vrp.core import ACO, ACOConfig
from aco_vrp.heuristics import clarke_wright_savings, nearest_neighbor
from aco_vrp.problem import CVRPInstance, load_solomon


class ExperimentRunner:
    """
    Orchestrates the execution of the ACO-CVRP scalability experiment.

    Constructs the experiment matrix from configuration presets, loads
    Solomon instances and subsets them to the target sizes, executes
    runs with controlled random seeds, and collects raw metrics.

    Attributes:
        data_dir: Path to directory containing Solomon instance files.
        configs: List of (config_id, ACOConfig) presets to evaluate.
        sizes: Problem sizes (customer counts) to test.
        baseline_results: Baseline heuristic results from the last run.
    """

    def __init__(self, data_dir: str = "data/solomon") -> None:
        """
        Initialize the experiment runner.

        Args:
            data_dir: Path to directory containing Solomon instance files.
        """
        self.data_dir = data_dir
        self.configs: list[tuple[str, ACOConfig]] = [
            (
                "C1",
                ACOConfig(
                    alpha=1.0,
                    beta=2.0,
                    rho=0.1,
                    ant_count=10,
                    max_iterations=100,
                    q0=0.0,
                    use_local_search=True,
                ),
            ),
            (
                "C2",
                ACOConfig(
                    alpha=1.0,
                    beta=5.0,
                    rho=0.1,
                    ant_count=10,
                    max_iterations=100,
                    q0=0.0,
                    use_local_search=True,
                ),
            ),
            (
                "C3",
                ACOConfig(
                    alpha=2.0,
                    beta=2.0,
                    rho=0.3,
                    ant_count=10,
                    max_iterations=100,
                    q0=0.0,
                    use_local_search=True,
                ),
            ),
            (
                "C4",
                ACOConfig(
                    alpha=2.0,
                    beta=5.0,
                    rho=0.3,
                    ant_count=10,
                    max_iterations=100,
                    q0=0.0,
                    use_local_search=True,
                ),
            ),
        ]
        self.sizes: list[int] = [25, 50, 100]
        self.baseline_results: dict[tuple[str, int], dict[str, Any]] = {}

    def run_full_matrix(self, seeds: int = 30) -> dict[tuple[str, int, int], dict[str, Any]]:
        """
        Execute the full experiment matrix across all configurations,
        problem sizes, and random seeds.

        Args:
            seeds: Number of independent runs per cell (default 30).

        Returns:
            Dictionary mapping (config_id, size, seed) to run metrics.
        """
        instance_path = Path(self.data_dir) / "RC101.txt"
        full_instance = load_solomon(str(instance_path))

        instances = {size: full_instance.subset(size) for size in self.sizes}

        # Run baseline heuristics
        self.baseline_results = {}
        for size in self.sizes:
            instance = instances[size]
            nn_solution = nearest_neighbor(instance)
            self.baseline_results[("NN", size)] = {
                "heuristic": "NN",
                "size": size,
                "total_distance": nn_solution.total_distance,
                "vehicle_count": nn_solution.vehicle_count,
            }
            cw_solution = clarke_wright_savings(instance)
            self.baseline_results[("CWS", size)] = {
                "heuristic": "CWS",
                "size": size,
                "total_distance": cw_solution.total_distance,
                "vehicle_count": cw_solution.vehicle_count,
            }

        total_tasks = 4 * len(self.sizes) * seeds
        completed = 0
        results: dict[tuple[str, int, int], dict[str, Any]] = {}

        for config_id, config in self.configs:
            for size in self.sizes:
                instance = instances[size]
                for seed in range(seeds):
                    try:
                        metrics = self._run_single_cell(config, instance, seed)
                        results[(config_id, size, seed)] = metrics
                    except Exception as exc:
                        print(
                            f"Error processing {config_id}"
                            f" size={size} seed={seed}: {exc}"
                        )

                    completed += 1
                    if completed % 30 == 0 or completed == total_tasks:
                        print(
                            f"[{completed}/{total_tasks}]"
                            f" Processing {config_id}"
                            f" size={size} seed={seed + 1}/{seeds}"
                        )

        return results

    @staticmethod
    def _run_single_cell(config: ACOConfig, instance: CVRPInstance, seed: int) -> dict[str, Any]:
        """
        Run a single experiment cell: one ACO configuration on one
        instance with one random seed.

        Args:
            config: ACO configuration preset.
            instance: CVRP problem instance (already subsetted).
            seed: Random seed for reproducibility.

        Returns:
            Dictionary of metrics for this run.
        """
        start_time = time.perf_counter()
        aco = ACO(config)
        solution = aco.solve(instance, seed=seed)
        wall_time = time.perf_counter() - start_time

        # Convergence iteration: first iteration within 5% of final best
        conv_history = aco.convergence_history
        convergence_iter = -1
        if conv_history:
            final_best = conv_history[-1]
            threshold = 1.05 * final_best
            for i, val in enumerate(conv_history):
                if val <= threshold:
                    convergence_iter = i
                    break

        return {
            "total_distance": solution.total_distance,
            "vehicle_count": solution.vehicle_count,
            "feasible": solution.feasible,
            "convergence_iter": convergence_iter,
            "wall_time_sec": wall_time,
        }

    @staticmethod
    def save_results(results: dict[tuple[str, int, int], dict[str, Any]], path: str) -> None:
        """
        Serialize raw experiment results to CSV.

        Args:
            results: Dictionary of run metrics keyed by (config_id, size, seed).
            path: Output file path.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "config_id",
                    "size",
                    "seed",
                    "total_distance",
                    "vehicle_count",
                    "feasible",
                    "convergence_iter",
                    "wall_time_sec",
                ]
            )
            for (config_id, size, seed), metrics in results.items():
                writer.writerow(
                    [
                        config_id,
                        size,
                        seed,
                        metrics.get("total_distance", ""),
                        metrics.get("vehicle_count", ""),
                        metrics.get("feasible", ""),
                        metrics.get("convergence_iter", ""),
                        metrics.get("wall_time_sec", ""),
                    ]
                )

    @staticmethod
    def save_baseline_results(
        baseline_results: dict[tuple[str, int], dict[str, Any]], path: str
    ) -> None:
        """
        Serialize baseline heuristic results to CSV.

        Args:
            baseline_results: Dictionary of baseline metrics keyed by (heuristic, size).
            path: Output file path.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["heuristic", "size", "total_distance", "vehicle_count"])
            for (heuristic, size), metrics in baseline_results.items():
                writer.writerow(
                    [
                        heuristic,
                        size,
                        metrics.get("total_distance", ""),
                        metrics.get("vehicle_count", ""),
                    ]
                )
