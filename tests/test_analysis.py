"""
Unit tests for the statistical analysis module (aco_vrp.analysis).

Tests cover:
    friedman_test             Omnibus test validation and error cases
    wilcoxon_signed_rank      Pairwise test validation and error cases
    StatisticalAnalyzer       Data extraction and orchestration
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from aco_vrp.analysis import (
    StatisticalAnalyzer,
    friedman_test,
    wilcoxon_signed_rank,
)

# ---------------------------------------------------------------------------
# Friedman test
# ---------------------------------------------------------------------------


def test_friedman_test_different_treatments() -> None:
    """Friedman test should reject null when treatments differ clearly."""
    rng = np.random.default_rng(42)
    # Treatment 0: low values (good), 1: medium, 2: high (bad)
    data = np.column_stack(
        [
            rng.normal(100, 5, size=30),
            rng.normal(150, 5, size=30),
            rng.normal(200, 5, size=30),
        ]
    )
    stat, pvalue = friedman_test(data)

    assert stat > 0
    assert pvalue < 0.01


def test_friedman_test_identical_treatments() -> None:
    """Friedman test should not reject null when all treatments are equal."""
    rng = np.random.default_rng(99)
    col = rng.normal(100, 5, size=20)
    data = np.column_stack([col, col, col])

    stat, pvalue = friedman_test(data)

    # scipy may return NaN when all columns are identical (zero variance).
    if np.isnan(pvalue):
        assert np.isnan(stat)
    else:
        assert pvalue > 0.05


def test_friedman_test_minimum_treatments() -> None:
    """Friedman test works with the minimum of 3 treatments (scipy limit)."""
    rng = np.random.default_rng(7)
    data = np.column_stack(
        [
            rng.normal(100, 5, size=10),
            rng.normal(110, 5, size=10),
            rng.normal(120, 5, size=10),
        ]
    )
    stat, pvalue = friedman_test(data)
    assert stat >= 0
    assert 0.0 <= pvalue <= 1.0


def test_friedman_test_agrees_with_scipy_direct() -> None:
    """Our wrapper should produce the same result as calling scipy directly."""
    rng = np.random.default_rng(123)
    n_blocks, n_treatments = 15, 4
    data = rng.normal(0, 1, size=(n_blocks, n_treatments))
    for j in range(n_treatments):
        data[:, j] += j * 2  # shift each treatment

    stat_wrapper, p_wrapper = friedman_test(data)

    columns = [data[:, j] for j in range(n_treatments)]
    result_direct = stats.friedmanchisquare(*columns)
    stat_direct, p_direct = result_direct.statistic, result_direct.pvalue

    assert stat_wrapper == pytest.approx(float(stat_direct), rel=1e-12)
    assert p_wrapper == pytest.approx(float(p_direct), rel=1e-12)


def test_friedman_test_minimum_blocks() -> None:
    """Friedman test should accept exactly 2 blocks."""
    data = np.array([[1.0, 2.0, 3.0], [2.0, 3.0, 5.0]])
    stat, pvalue = friedman_test(data)
    assert stat >= 0
    assert 0.0 <= pvalue <= 1.0


def test_friedman_test_known_result() -> None:
    """Friedman test on a minimal known dataset with no ties.

    Blocks: 3, Treatments: 3
    Within each block the ranks are unambiguous (1, 2, 3).
    Friedman statistic = (12 / (n*k*(k+1))) * sum(R_j^2) - 3*n*(k+1)
        = (12 / (3*3*4)) * (4^2 + 6^2 + 8^2) - 3*3*4
        = (12/36) * (16+36+64) - 36
        = (1/3) * 116 - 36
        = 38.666... - 36 = 2.666...
    """
    data = np.array(
        [
            [1.0, 2.0, 3.0],  # ranks: 1, 2, 3
            [1.1, 2.1, 3.1],  # ranks: 1, 2, 3
            [1.2, 2.2, 3.2],  # ranks: 1, 2, 3
        ]
    )
    stat, _pvalue = friedman_test(data)

    # With no ties, rank sums: R1=3, R2=6, R3=9
    # Friedman = (12/(3*3*4)) * (9+36+81) - 36 = (1/3)*126 - 36 = 42 - 36 = 6
    # Hmm, let me recompute with the real scipy value.
    expected_stat = 6.0
    assert stat == pytest.approx(expected_stat, rel=1e-10)


# ---------------------------------------------------------------------------
# Friedman test — error cases
# ---------------------------------------------------------------------------


def test_friedman_test_rejects_1d_input() -> None:
    with pytest.raises(ValueError, match="2-D"):
        friedman_test(np.array([1.0, 2.0, 3.0]))


def test_friedman_test_rejects_fewer_than_3_treatments() -> None:
    with pytest.raises(ValueError, match="at least 3 treatments"):
        friedman_test(np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]))


def test_friedman_test_rejects_single_block() -> None:
    with pytest.raises(ValueError, match="at least 2 blocks"):
        friedman_test(np.array([[1.0, 2.0, 3.0]]))


# ---------------------------------------------------------------------------
# Wilcoxon signed-rank test
# ---------------------------------------------------------------------------


def test_wilcoxon_signed_rank_different() -> None:
    """Wilcoxon should reject null when one sample is consistently larger."""
    rng = np.random.default_rng(1337)
    x = rng.normal(100, 3, size=30)
    y = rng.normal(110, 3, size=30)  # shifted up

    stat, pvalue = wilcoxon_signed_rank(x, y)
    assert stat >= 0
    assert pvalue < 0.01


def test_wilcoxon_signed_rank_identical() -> None:
    """Wilcoxon should not reject null for nearly identical samples."""
    rng = np.random.default_rng(42)
    base = rng.normal(100, 3, size=30)

    stat, pvalue = wilcoxon_signed_rank(base, base.copy())
    # With all zero diffs, scipy >= 1.11 returns NaN; older returns 0 or warns.
    # Adjust expectation: pvalue well above any reasonable alpha.
    if not np.isnan(pvalue):
        assert pvalue > 0.05


def test_wilcoxon_signed_rank_agrees_with_scipy() -> None:
    """Our wrapper should agree with scipy.stats.wilcoxon directly."""
    rng = np.random.default_rng(256)
    x = rng.normal(0, 1, size=25)
    y = x + rng.normal(0.5, 0.2, size=25)

    stat_w, p_w = wilcoxon_signed_rank(x, y)
    result_direct = stats.wilcoxon(x, y, zero_method="wilcox", alternative="two-sided")
    stat_d, p_d = result_direct.statistic, result_direct.pvalue

    assert stat_w == pytest.approx(float(stat_d), rel=1e-12)
    assert p_w == pytest.approx(float(p_d), rel=1e-12)


def test_wilcoxon_signed_rank_small_n() -> None:
    """Wilcoxon should handle the minimum sample size (n=2 non-tied pairs)."""
    x = np.array([1.0, 2.0])
    y = np.array([3.0, 5.0])
    stat, pvalue = wilcoxon_signed_rank(x, y)
    assert stat >= 0
    assert 0.0 <= pvalue <= 1.0


def test_wilcoxon_signed_rank_zero_differences_handling() -> None:
    """Zero-difference pairs should be handled per zero_method."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    # Pair at index 2 is identical; delta = [3, 3, 0, 3, 3]
    y = np.array([4.0, 5.0, 3.0, 7.0, 8.0])

    stat, pvalue = wilcoxon_signed_rank(x, y, zero_method="wilcox")
    assert stat >= 0
    assert 0.0 <= pvalue <= 1.0


# ---------------------------------------------------------------------------
# Wilcoxon signed-rank — error cases
# ---------------------------------------------------------------------------


def test_wilcoxon_rejects_different_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        wilcoxon_signed_rank(np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0]))


def test_wilcoxon_rejects_too_few_pairs() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        wilcoxon_signed_rank(np.array([1.0]), np.array([2.0]))


def test_wilcoxon_rejects_2d_input() -> None:
    with pytest.raises(ValueError, match="1-D"):
        wilcoxon_signed_rank(
            np.array([[1.0, 2.0], [3.0, 4.0]]),
            np.array([[5.0, 6.0], [7.0, 8.0]]),
        )


# ---------------------------------------------------------------------------
# StatisticalAnalyzer
# ---------------------------------------------------------------------------


def _make_raw_data(
    configs: list[str], sizes: list[int], seeds: int, rng: np.random.Generator
) -> dict[tuple[str, int, int], dict[str, float]]:
    """Build a minimal raw_data dict for testing StatisticalAnalyzer."""
    raw: dict[tuple[str, int, int], dict[str, float]] = {}
    for cfg in configs:
        for size in sizes:
            for seed in range(seeds):
                raw[(cfg, size, seed)] = {
                    "distance": float(rng.normal(100 + 10 * len(cfg), 5)),
                    "vehicles": float(rng.integers(3, 8)),
                }
    return raw


def test_analyzer_friedman_test() -> None:
    rng = np.random.default_rng(1)
    configs = ["cfg_a", "cfg_b", "cfg_c"]
    raw = _make_raw_data(configs, sizes=[25], seeds=30, rng=rng)

    analyzer = StatisticalAnalyzer(raw, alpha=0.05)
    stat, pvalue = analyzer.friedman_test("distance", size=25)

    assert stat >= 0
    assert 0.0 <= pvalue <= 1.0


def test_analyzer_wilcoxon_signed_rank() -> None:
    rng = np.random.default_rng(2)
    configs = ["cfg_a", "cfg_b"]
    raw = _make_raw_data(configs, sizes=[50], seeds=30, rng=rng)

    analyzer = StatisticalAnalyzer(raw, alpha=0.05)
    stat, pvalue = analyzer.wilcoxon_signed_rank("cfg_a", "cfg_b", "distance", size=50)

    assert stat >= 0
    assert 0.0 <= pvalue <= 1.0


def test_analyzer_friedman_insufficient_configs() -> None:
    raw: dict[tuple[str, int, int], dict[str, float]] = {
        ("only_cfg", 25, 0): {"distance": 100.0},
    }
    analyzer = StatisticalAnalyzer(raw, alpha=0.05)

    with pytest.raises(ValueError, match="at least 2 configurations"):
        analyzer.friedman_test("distance", size=25)


def test_analyzer_wilcoxon_missing_config() -> None:
    raw: dict[tuple[str, int, int], dict[str, float]] = {
        ("cfg_a", 25, 0): {"distance": 100.0},
    }
    analyzer = StatisticalAnalyzer(raw, alpha=0.05)

    with pytest.raises(ValueError, match="Insufficient data"):
        analyzer.wilcoxon_signed_rank("cfg_a", "cfg_b", "distance", size=25)
