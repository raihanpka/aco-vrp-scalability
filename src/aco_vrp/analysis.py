"""
Statistical analysis module for the ACO-CVRP scalability experiment.

Implements nonparametric statistical tests as recommended by Derrac et al.
(2011) for comparing evolutionary and swarm intelligence algorithms:
Friedman test for omnibus comparison, Wilcoxon signed-rank test for
pairwise comparisons with Holm correction, and Nemenyi post-hoc test
for critical difference diagrams.

Classes:
    StatisticalAnalyzer    Processes raw experiment results and produces
                           summary statistics, test outputs, and effect
                           size measures.

Functions:
    friedman_test          Omnibus test across multiple configurations.
    wilcoxon_signed_rank   Pairwise comparison between two configurations.
    nemenyi_post_hoc       Critical difference computation for CD diagrams.
    holm_correction        Adjust p-values for multiple comparisons.
"""

from typing import Any


class StatisticalAnalyzer:
    """
    Analyzes raw experiment results with nonparametric statistical tests.

    Loads per-run metrics (total distance, vehicle count, convergence
    speed, feasibility rate), computes aggregate statistics (mean,
    median, standard deviation, standard error), and performs
    hypothesis tests at each problem size.

    Attributes:
        raw_data: Raw run metrics indexed by (config_id, size, seed).
        alpha: Significance level for hypothesis tests (default 0.05).
    """

    def __init__(self, raw_data: dict[str, Any], alpha: float = 0.05) -> None:
        """
        Initialize the statistical analyzer.

        Args:
            raw_data: Raw run metrics from ExperimentRunner.
            alpha: Significance level for hypothesis tests.
        """
        self.raw_data = raw_data
        self.alpha = alpha

    def friedman_test(self, metric: str, size: int) -> tuple[float, float]:
        """
        Perform the Friedman test across all configurations at a given
        problem size for the specified metric.

        Args:
            metric: Metric name to compare (e.g., "total_distance").
            size: Problem size (25, 50, or 100).

        Returns:
            Tuple of (Friedman statistic, p-value).
        """
        raise NotImplementedError("Friedman test not yet implemented.")

    def wilcoxon_signed_rank(
        self, config_a: str, config_b: str, metric: str, size: int
    ) -> tuple[float, float]:
        """
        Perform the Wilcoxon signed-rank test between two configurations.

        Args:
            config_a: Identifier for the first configuration.
            config_b: Identifier for the second configuration.
            metric: Metric name to compare.
            size: Problem size.

        Returns:
            Tuple of (Wilcoxon statistic, p-value).
        """
        raise NotImplementedError("Wilcoxon test not yet implemented.")
