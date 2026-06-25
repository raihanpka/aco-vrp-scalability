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

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import stats


class StatisticalAnalyzer:
    """
    Analyzes raw experiment results with nonparametric statistical tests.

    Loads per-run metrics (total distance, vehicle count, convergence
    speed, feasibility rate), computes aggregate statistics (mean,
    median, standard deviation, standard error), and performs
    hypothesis tests at each problem size.

    The raw_data dictionary is expected to be keyed by tuples of
    (config_id, size, seed) mapping to metric dictionaries, e.g.:
        raw_data[("cfg_a", 25, 0)] = {"total_distance": 842.3, ...}

    Attributes:
        raw_data: Raw run metrics indexed by (config_id, size, seed).
        alpha: Significance level for hypothesis tests (default 0.05).
    """

    def __init__(self, raw_data: dict[Any, Any], alpha: float = 0.05) -> None:
        """
        Initialize the statistical analyzer.

        Args:
            raw_data: Raw run metrics from ExperimentRunner.
            alpha: Significance level for hypothesis tests.
        """
        self.raw_data = raw_data
        self.alpha = alpha

    def _extract_metric(
        self, config_ids: list[str], metric: str, size: int
    ) -> np.ndarray:
        """Extract metric values across runs for given configs and size.

        Args:
            config_ids: List of configuration identifiers.
            metric: Metric name to extract.
            size: Problem size.

        Returns:
            2-D array of shape (n_runs, n_configs).
        """
        seeds: set[int] = set()
        for key in self.raw_data:
            # keys may be tuples (config, size, seed) or strings
            if isinstance(key, tuple) and len(key) == 3:
                _, key_size, seed = key
                if key_size == size:
                    seeds.add(seed)

        sorted_seeds = sorted(seeds)
        values: list[list[float]] = []
        for config_id in config_ids:
            col: list[float] = []
            for seed in sorted_seeds:
                lookup = (config_id, size, seed)
                if lookup in self.raw_data:
                    col.append(float(self.raw_data[lookup][metric]))
            if col:
                values.append(col)

        if not values:
            return np.array([])
        return np.array(values).T

    def friedman_test(self, metric: str, size: int) -> tuple[float, float]:
        """
        Perform the Friedman test across all configurations at a given
        problem size for the specified metric.

        Args:
            metric: Metric name to compare (e.g., "total_distance").
            size: Problem size (25, 50, or 100).

        Returns:
            Tuple of (Friedman statistic, p-value).

        Raises:
            ValueError: If fewer than 2 configurations have data for the
                        given size and metric.
        """
        config_ids = self._discover_configs(size)
        if len(config_ids) < 2:
            msg = (
                f"Need at least 2 configurations with data for "
                f"size={size}, metric={metric!r}"
            )
            raise ValueError(msg)

        data = self._extract_metric(config_ids, metric, size)
        return friedman_test(data)

    def _discover_configs(self, size: int) -> list[str]:
        """Discover configuration IDs present in raw_data for a given size."""
        configs: set[str] = set()
        for key in self.raw_data:
            if isinstance(key, tuple) and len(key) == 3:
                config_id, key_size, _ = key
                if key_size == size:
                    configs.add(config_id)
        return sorted(configs)

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

        Raises:
            ValueError: If either configuration has no data for the given
                        size and metric.
        """
        data = self._extract_metric([config_a, config_b], metric, size)
        if data.shape[1] < 2:
            msg = (
                f"Insufficient data for configs {config_a!r} and "
                f"{config_b!r} at size={size}, metric={metric!r}"
            )
            raise ValueError(msg)

        return wilcoxon_signed_rank(data[:, 0], data[:, 1])


# END OF STATISTICAL ANALYZER CLASS


def friedman_test(data: np.ndarray) -> tuple[float, float]:
    """
    Perform the Friedman rank-sum test for repeated measures.

    The Friedman test is a nonparametric omnibus test for detecting
    differences across multiple treatments (configurations) when the
    same set of blocks (runs / instances) is measured under each
    treatment.

    Args:
        data: 2-D array of shape (n_blocks, n_treatments) where each
              row corresponds to a block and each column to a treatment.
              Blocks must be independent; treatments are compared within
              each block.

    Returns:
        Tuple of (Friedman chi-squared statistic, p-value).

    Raises:
        ValueError: If data has fewer than 3 treatments or fewer than 2
                    blocks.

    References:
        Derrac, J. et al. (2011). A practical tutorial on the use of
        nonparametric statistical tests as a methodology for comparing
        evolutionary and swarm intelligence algorithms.
        *Swarm and Evolutionary Computation*, 1(1), 3-18.
    """
    if data.ndim != 2:
        msg = f"data must be 2-D, got shape {data.shape}"
        raise ValueError(msg)

    n_blocks, n_treatments = data.shape
    if n_treatments < 3:
        msg = f"Need at least 3 treatments, got {n_treatments}"
        raise ValueError(msg)
    if n_blocks < 2:
        msg = f"Need at least 2 blocks, got {n_blocks}"
        raise ValueError(msg)

    columns = [data[:, j] for j in range(n_treatments)]
    result = stats.friedmanchisquare(*columns)
    return float(result.statistic), float(result.pvalue)


def wilcoxon_signed_rank(
    x: np.ndarray, y: np.ndarray, zero_method: str = "wilcox"
) -> tuple[float, float]:
    """
    Perform the Wilcoxon signed-rank test for paired samples.

    Tests the null hypothesis that two related paired samples come from
    the same distribution. In the context of algorithm comparison, this
    tests whether two configurations produce significantly different
    performance on the same set of problem instances.

    Args:
        x: 1-D array of observations from the first treatment.
        y: 1-D array of observations from the second treatment (must
           be the same length as x).
        zero_method: How to handle zero differences. "wilcox" discards
                     them (default, same as Derrac et al. 2011).
                     "zsplit" includes them with a split allocation.
                     "pratt" includes them per Pratt's adjustment.

    Returns:
        Tuple of (Wilcoxon T statistic, p-value).

    Raises:
        ValueError: If x and y have different lengths or contain fewer
                    than 2 non-tied pairs.

    References:
        Derrac, J. et al. (2011). A practical tutorial on the use of
        nonparametric statistical tests as a methodology for comparing
        evolutionary and swarm intelligence algorithms.
        *Swarm and Evolutionary Computation*, 1(1), 3-18.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.ndim != 1 or y.ndim != 1:
        msg = f"x and y must be 1-D, got shapes {x.shape} and {y.shape}"
        raise ValueError(msg)
    if len(x) != len(y):
        msg = f"x and y must have the same length, got {len(x)} and {len(y)}"
        raise ValueError(msg)
    if len(x) < 2:
        msg = f"Need at least 2 paired observations, got {len(x)}"
        raise ValueError(msg)

    result = stats.wilcoxon(x, y, zero_method=zero_method, alternative="two-sided")
    return float(result.statistic), float(result.pvalue)
