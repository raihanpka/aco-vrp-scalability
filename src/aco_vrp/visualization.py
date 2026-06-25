"""
Visualization module for the ACO-CVRP scalability experiment.

Generates publication-quality figures: scalability plots with confidence
bands, parameter interaction heatmaps, convergence curve overlays,
pheromone concentration animations, and critical difference diagrams
following the Nemenyi post-hoc procedure.

Functions:
    plot_scalability        Performance degradation curve across problem
                            sizes with confidence bands.
    plot_parameter_heatmap  Alpha vs. Beta interaction heatmap at each
                            problem size.
    plot_convergence        Overlay of convergence curves for all
                            configurations.
    plot_critical_difference  Nemenyi CD diagram for post-hoc comparisons.
    plot_pheromone_animation  Animated heatmap of pheromone concentration
                            evolution across iterations.
"""

from typing import Any


def plot_scalability(
    results: dict[str, Any],
    metric: str = "total_distance",
    output_path: str = "results/scalability_plot.pdf",
) -> None:
    """
    Plot performance degradation as problem size increases.

    X-axis: problem size (25, 50, 100). Y-axis: metric value.
    One line per ACO configuration, each with a confidence band
    derived from 30 independent runs.

    Args:
        results: Dictionary of run metrics.
        metric: Metric to plot on the Y-axis.
        output_path: File path for saving the figure.
    """
    raise NotImplementedError("Scalability plot not yet implemented.")


def plot_parameter_heatmap(
    results: dict[str, Any],
    size: int = 100,
    output_path: str = "results/parameter_heatmap.pdf",
) -> None:
    """
    Plot a heatmap of metric values across alpha and beta parameter
    combinations for a given problem size.

    Args:
        results: Dictionary of run metrics.
        size: Problem size to analyze.
        output_path: File path for saving the figure.
    """
    raise NotImplementedError("Parameter heatmap not yet implemented.")
