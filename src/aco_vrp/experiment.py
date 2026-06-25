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

from typing import Any


class ExperimentRunner:
    """
    Orchestrates the execution of the ACO-CVRP scalability experiment.

    Constructs the experiment matrix from configuration presets, loads
    Solomon instances and subsets them to the target sizes, executes
    runs with controlled random seeds, and collects raw metrics.

    Attributes:
        data_dir: Path to directory containing Solomon instance files.
        configs: List of ACOConfig presets to evaluate.
        sizes: Problem sizes (customer counts) to test.
    """

    def __init__(self, data_dir: str = "data/solomon") -> None:
        """
        Initialize the experiment runner.

        Args:
            data_dir: Path to directory containing Solomon instance files.
        """
        self.data_dir = data_dir
        self.configs: list[object] = []
        self.sizes: list[int] = [25, 50, 100]

    def run_full_matrix(self, seeds: int = 30) -> dict[str, Any]:
        """
        Execute the full experiment matrix across all configurations,
        problem sizes, and random seeds.

        Args:
            seeds: Number of independent runs per cell (default 30).

        Returns:
            Dictionary mapping (config_id, size, seed) to run metrics.
        """
        raise NotImplementedError("Experiment runner not yet implemented.")

    def save_results(self, results: dict[str, Any], path: str) -> None:
        """
        Serialize raw experiment results to CSV.

        Args:
            results: Dictionary of run metrics.
            path: Output file path.
        """
        raise NotImplementedError("Result serialization not yet implemented.")
