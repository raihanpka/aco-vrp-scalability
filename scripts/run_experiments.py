"""Full experiment execution script.

Runs the complete ACO-CVRP scalability experiment:
4 configurations x 3 problem sizes x 30 seeds = 360 ACO runs,
plus baseline heuristics. Saves raw results, generates statistical
analysis, and produces publication-quality visualizations.

Usage:
    python scripts/run_experiments.py
"""

import sys
import time
from pathlib import Path

from aco_vrp.analysis import StatisticalAnalyzer
from aco_vrp.experiment import ExperimentRunner
from aco_vrp.visualization import (
    plot_convergence,
    plot_critical_difference,
    plot_parameter_heatmap,
    plot_scalability,
)

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    total_start = time.perf_counter()

    print("Phase 1: Running full experiment matrix (seeds=30)")
    print("This will execute 360 ACO runs across 12 cells.")
    runner = ExperimentRunner(data_dir="data/solomon")
    results = runner.run_full_matrix(seeds=30)

    phase1_elapsed = time.perf_counter() - total_start
    print(f"Phase 1 completed in {phase1_elapsed:.1f}s")

    runner.save_results(results, str(RESULTS_DIR / "raw_runs.csv"))
    runner.save_baseline_results(
        runner.baseline_results, str(RESULTS_DIR / "baseline_runs.csv")
    )
    print("Raw results saved to results/raw_runs.csv")
    print("Baseline results saved to results/baseline_runs.csv")

    print()
    print("Phase 2: Statistical analysis")
    analyzer = StatisticalAnalyzer(results, alpha=0.05)

    with open(RESULTS_DIR / "statistical_report.txt", "w") as report:
        for size in [25, 50, 100]:
            report.write(f"Size = {size}\n")
            report.write("=" * 20 + "\n")
            try:
                stat, pval = analyzer.friedman_test("total_distance", size)
                report.write(f"Friedman test: statistic={stat:.4f}, p={pval:.6f}\n")
                if pval < 0.05:
                    report.write("  Significant differences found among configurations.\n")
                else:
                    report.write("  No significant differences.\n")
            except ValueError as exc:
                report.write(f"  Friedman test failed: {exc}\n")

            configs = analyzer._discover_configs(size)
            for i, ca in enumerate(configs):
                for cb in configs[i + 1 :]:
                    try:
                        stat, pval = analyzer.wilcoxon_signed_rank(
                            ca, cb, "total_distance", size
                        )
                        report.write(
                            f"  Wilcoxon {ca} vs {cb}: stat={stat:.4f}, p={pval:.6f}"
                        )
                        if pval < 0.05:
                            report.write(" (significant)")
                        report.write("\n")
                    except ValueError as exc:
                        report.write(f"  Wilcoxon {ca} vs {cb} failed: {exc}\n")
            report.write("\n")

        report.write("Summary Statistics\n")
        report.write("=" * 20 + "\n")
        for config_id in ["C1", "C2", "C3", "C4"]:
            for size in [25, 50, 100]:
                values = [
                    v["total_distance"]
                    for (cid, sz, _sd), v in results.items()
                    if cid == config_id and sz == size
                ]
                if values:
                    import statistics
                    report.write(
                        f"{config_id} size={size}: "
                        f"mean={statistics.mean(values):.1f}, "
                        f"std={statistics.stdev(values):.1f}, "
                        f"n={len(values)}\n"
                    )

    print("Statistical report saved to results/statistical_report.txt")

    print()
    print("Phase 3: Generating visualizations")
    plot_scalability(
        results,
        baseline_results=runner.baseline_results,
        output_path=str(RESULTS_DIR / "scalability_plot.pdf"),
    )
    print("  scalability_plot.pdf created")

    plot_parameter_heatmap(
        results, size=100, output_path=str(RESULTS_DIR / "parameter_heatmap.pdf")
    )
    print("  parameter_heatmap.pdf created")

    plot_critical_difference(
        output_path=str(RESULTS_DIR / "critical_difference.pdf")
    )
    print("  critical_difference.pdf created")

    total_elapsed = time.perf_counter() - total_start
    print()
    print(f"All phases completed in {total_elapsed:.1f}s")


if __name__ == "__main__":
    main()
