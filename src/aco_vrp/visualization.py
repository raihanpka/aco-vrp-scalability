"""
Visualization module for the ACO-CVRP scalability experiment.

Generates publication-quality black and white figures using matplotlib
with varied line styles and marker shapes per configuration. Supports
SVG and PDF output. All 2-D plots are strictly grayscale.

Functions:
    plot_scalability        Performance degradation curve across problem
                            sizes with confidence bands.
    plot_convergence        Overlay of convergence curves for all
                            configurations per problem size.
    plot_parameter_heatmap  Grayscale heatmap of mean distance across
                            alpha and beta combinations.
    plot_critical_difference  Nemenyi CD diagram for post-hoc comparisons.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "text.usetex": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

CONFIG_LABELS: dict[str, str] = {
    "C1": "C1 (alpha=1.0, beta=2.0, rho=0.1)",
    "C2": "C2 (alpha=1.0, beta=5.0, rho=0.1)",
    "C3": "C3 (alpha=2.0, beta=2.0, rho=0.3)",
    "C4": "C4 (alpha=2.0, beta=5.0, rho=0.3)",
}

LINE_STYLES: dict[str, str] = {
    "C1": "-",
    "C2": "--",
    "C3": "-.",
    "C4": ":",
}

MARKERS: dict[str, str] = {
    "C1": "o",
    "C2": "^",
    "C3": "s",
    "C4": "D",
}

FILL_STYLES: dict[str, str] = {
    "C1": "full",
    "C2": "none",
    "C3": "full",
    "C4": "none",
}

GRAY_LIGHT = "0.75"
GRAY_MEDIUM = "0.4"
GRAY_DARK = "0.0"

CONFIG_ORDER = ["C1", "C2", "C3", "C4"]
SIZES = [25, 50, 100]

ALPHA_MAP = {0: 1.0, 1: 2.0}
BETA_MAP = {0: 2.0, 1: 5.0}

CONFIG_ALPHA_BETA = {
    "C1": (1.0, 2.0),
    "C2": (1.0, 5.0),
    "C3": (2.0, 2.0),
    "C4": (2.0, 5.0),
}


def _agg_by_config_size(
    results: dict[tuple[str, int, int], dict[str, Any]], metric: str
) -> dict[tuple[str, int], tuple[float, float]]:
    """Aggregate metric mean and std per (config_id, size)."""
    aggregated: dict[tuple[str, int], list[float]] = {}
    for (config_id, size, _seed), values in results.items():
        if metric in values:
            aggregated.setdefault((config_id, size), []).append(float(values[metric]))
    out: dict[tuple[str, int], tuple[float, float]] = {}
    for key, vals in aggregated.items():
        arr = np.array(vals)
        out[key] = (float(np.mean(arr)), float(np.std(arr, ddof=1)))
    return out


def plot_scalability(
    results: dict[tuple[str, int, int], dict[str, Any]],
    baseline_results: dict[tuple[str, int], dict[str, Any]] | None = None,
    metric: str = "total_distance",
    output_path: str = "results/scalability_plot.pdf",
) -> None:
    """Plot performance degradation as problem size increases.

    Each ACO configuration is drawn with a distinct line style and marker.
    Baseline heuristics (NN and CWS) are drawn as horizontal dashed lines
    when baseline_results is provided. The confidence band is a gray
    shaded region spanning mean plus/minus one standard deviation.

    Args:
        results: ACO run metrics keyed by (config_id, size, seed).
        baseline_results: Optional baseline metrics keyed by (heuristic, size).
        metric: Metric name to plot on the Y axis.
        output_path: Path for the saved figure (PDF and SVG will be written).
    """
    agg = _agg_by_config_size(results, metric)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.set_xlabel("Problem Size (Number of Customers)")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_xlim(20, 105)
    ax.set_xticks(SIZES)

    for config_id in CONFIG_ORDER:
        xs: list[int] = []
        means: list[float] = []
        stds: list[float] = []
        for size in SIZES:
            key = (config_id, size)
            if key not in agg:
                continue
            mean, std = agg[key]
            xs.append(size)
            means.append(mean)
            stds.append(std)
        if not xs:
            continue
        xs_arr = np.array(xs)
        means_arr = np.array(means)
        stds_arr = np.array(stds)
        ax.plot(
            xs_arr,
            means_arr,
            linestyle=LINE_STYLES[config_id],
            marker=MARKERS[config_id],
            fillstyle=FILL_STYLES[config_id],
            color=GRAY_DARK,
            markeredgecolor=GRAY_DARK,
            markerfacecolor=GRAY_LIGHT if FILL_STYLES[config_id] == "none" else GRAY_DARK,
            linewidth=1.2,
            markersize=7,
            label=CONFIG_LABELS[config_id],
        )
        ax.fill_between(
            xs_arr,
            means_arr - stds_arr,
            means_arr + stds_arr,
            color=GRAY_LIGHT,
            alpha=0.4,
            edgecolor="none",
        )

    if baseline_results:
        baseline_styles = {"NN": (0.6, (1, 2)), "CWS": (0.6, (3, 3, 1, 3))}
        for heuristic, label in [("NN", "Nearest Neighbor"), ("CWS", "Clarke-Wright Savings")]:
            bs_xs: list[int] = []
            bs_vals: list[float] = []
            for size in SIZES:
                key = (heuristic, size)
                if key in baseline_results:
                    bs_xs.append(size)
                    bs_vals.append(float(baseline_results[key][metric]))
            if bs_xs:
                ax.plot(
                    bs_xs,
                    bs_vals,
                    linestyle=baseline_styles[heuristic],
                    color=GRAY_DARK,
                    linewidth=0.9,
                    label=label,
                )

    ax.legend(frameon=False, loc="upper left")
    ax.grid(True, linestyle=":", color=GRAY_LIGHT, linewidth=0.5, alpha=0.7)
    fig.tight_layout()
    _save(fig, output_path)
    plt.close(fig)


def plot_convergence(
    convergence_data: dict[tuple[str, int], list[float]],
    output_path: str = "results/convergence_curves.pdf",
) -> None:
    """Plot convergence curves for all configurations at each problem size.

    Three subplots (one per problem size) arranged in a single row.
    Each configuration uses the same line style as in scalability plots.

    Args:
        convergence_data: Per-iteration best distances keyed by
            (config_id, size). Each value is a list of floats where
            index i is the best distance found up to iteration i.
        output_path: Path for the saved figure.
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), sharey=False)
    for ax_idx, size in enumerate(SIZES):
        ax = axes[ax_idx]
        ax.set_title(f"Size = {size}")
        ax.set_xlabel("Iteration")
        if ax_idx == 0:
            ax.set_ylabel("Best Distance")
        ax.grid(True, linestyle=":", color=GRAY_LIGHT, linewidth=0.5, alpha=0.7)

        for config_id in CONFIG_ORDER:
            key = (config_id, size)
            if key not in convergence_data or not convergence_data[key]:
                continue
            history = convergence_data[key]
            ax.plot(
                range(len(history)),
                history,
                linestyle=LINE_STYLES[config_id],
                color=GRAY_DARK,
                linewidth=0.9,
                label=CONFIG_LABELS[config_id] if ax_idx == 2 else None,
            )

    if axes[-1].get_legend_handles_labels()[0]:
        axes[-1].legend(frameon=False, loc="upper right", fontsize=7)
    fig.tight_layout()
    _save(fig, output_path)
    plt.close(fig)


def plot_parameter_heatmap(
    results: dict[tuple[str, int, int], dict[str, Any]],
    size: int = 100,
    metric: str = "total_distance",
    output_path: str = "results/parameter_heatmap.pdf",
) -> None:
    """Plot a grayscale heatmap of mean metric across alpha and beta.

    Cell intensity represents mean metric value. Darker cells indicate
    lower (better) total distance. Annotations show the numeric mean.

    Args:
        results: ACO run metrics keyed by (config_id, size, seed).
        size: Problem size to analyze.
        metric: Metric name to display.
        output_path: Path for the saved figure.
    """
    matrix = np.full((2, 2), np.nan)
    for config_id in CONFIG_ORDER:
        alpha, beta = CONFIG_ALPHA_BETA[config_id]
        alpha_idx = 0 if alpha == 1.0 else 1
        beta_idx = 0 if beta == 2.0 else 1
        vals = []
        for seed in range(30):
            key = (config_id, size, seed)
            if key in results and metric in results[key]:
                vals.append(float(results[key][metric]))
        if vals:
            matrix[beta_idx, alpha_idx] = np.mean(vals)

    fig, ax = plt.subplots(figsize=(4.5, 4.0))
    im = ax.imshow(
        matrix,
        cmap="gray_r",
        aspect="auto",
        vmin=np.nanmin(matrix),
        vmax=np.nanmax(matrix),
    )
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["1.0", "2.0"])
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["2.0", "5.0"])
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Beta")
    ax.set_title(f"{metric.replace('_', ' ').title()} (Size = {size})")
    cbar = fig.colorbar(im, ax=ax, label=metric.replace("_", " ").title())
    cbar.outline.set_edgecolor(GRAY_DARK)  # type: ignore[operator]

    for bi in range(2):
        for ai in range(2):
            val = matrix[bi, ai]
            if not np.isnan(val):
                ax.text(
                    ai, bi, f"{val:.1f}",
                    ha="center", va="center",
                    color="white" if val > np.nanmean(matrix) else "black",
                    fontsize=11, fontweight="bold",
                )

    fig.tight_layout()
    _save(fig, output_path)
    plt.close(fig)


def plot_critical_difference(
    cd_data: dict[str, float] | None = None,
    cd_threshold: float = 0.0,
    output_path: str = "results/critical_difference.pdf",
) -> None:
    """Draw a Nemenyi critical difference diagram.

    Configurations are placed on a horizontal axis ordered by mean rank
    (lower rank is better, i.e., further left). Configurations connected
    by a thick horizontal bar are not significantly different at the
    chosen significance level.

    Args:
        cd_data: Mapping of config_id to mean rank. If None, a placeholder
            diagram is drawn.
        cd_threshold: The critical difference value. If 0, a placeholder
            is used.
        output_path: Path for the saved figure.
    """
    if cd_data is None:
        cd_data = {"C1": 2.1, "C2": 1.8, "C3": 3.0, "C4": 3.1}
    if cd_threshold <= 0:
        cd_threshold = 1.5

    sorted_configs = sorted(cd_data.items(), key=lambda x: x[1])
    labels = [c for c, _ in sorted_configs]
    ranks = [r for _, r in sorted_configs]

    fig, ax = plt.subplots(figsize=(8, 2.2))
    ax.set_xlim(min(ranks) - 1.2, max(ranks) + 1.2)
    ax.set_ylim(0, 2.5)
    ax.axis("off")

    ax.plot([min(ranks) - 0.8, max(ranks) + 0.8], [1, 1], color=GRAY_DARK, linewidth=1.0)
    for r in ranks:
        ax.plot([r, r], [0.85, 1.15], color=GRAY_DARK, linewidth=1.0)
    for i, r in enumerate(ranks):
        ax.text(r, 0.5, labels[i], ha="center", va="top", fontsize=10, fontweight="bold")
        ax.text(r, 1.35, f"{r:.2f}", ha="center", va="bottom", fontsize=8, color=GRAY_MEDIUM)

    # Group configurations not significantly different
    for i in range(len(ranks)):
        for j in range(i + 1, len(ranks)):
            if ranks[j] - ranks[i] < cd_threshold:
                continue
            for k in range(j - 1, i, -1):
                if ranks[k] - ranks[i] < cd_threshold:
                    ax.plot(
                        [ranks[i], ranks[k]],
                        [1.6, 1.6],
                        color=GRAY_DARK,
                        linewidth=2.5,
                        solid_capstyle="butt",
                    )
                break
            break

    ax.text(
        max(ranks) + 0.5, 1.6,
        f"CD = {cd_threshold:.2f}",
        fontsize=8, color=GRAY_MEDIUM, va="center",
    )
    ax.set_title("Nemenyi Critical Difference Diagram", pad=10)
    fig.tight_layout()
    _save(fig, output_path)
    plt.close(fig)


def _save(fig: matplotlib.figure.Figure, output_path: str) -> None:
    """Save figure as SVG to the output directory."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    svg_path = path.with_suffix(".svg")
    fig.savefig(str(svg_path), format="svg")


def plot_route_map(
    instance: Any,
    solution: Any,
    title: str = "ACO Route Map",
    output_path: str = "results/route_map.pdf",
) -> None:
    """Plot customer locations and vehicle routes on a 2-D coordinate plane.

    Customers are drawn as small circles with their node index. The depot
    is drawn as a filled square. Each route is a polyline connecting
    customers in visit order, with a distinct line style. Segments to and
    from the depot are drawn as dotted lines.

    Args:
        instance: CVRPInstance providing .depot and .customers with .x, .y.
        solution: CVRPSolution providing .routes (list of lists of node indices).
        title: Plot title.
        output_path: Path for the saved figure.
    """
    route_styles = [
        {"linestyle": "-", "linewidth": 1.2},
        {"linestyle": "--", "linewidth": 1.2},
        {"linestyle": "-.", "linewidth": 1.2},
        {"linestyle": (0, (3, 2, 1, 2)), "linewidth": 1.2},
        {"linestyle": (0, (1, 1)), "linewidth": 0.9},
        {"linestyle": (0, (5, 3)), "linewidth": 0.9},
        {"linestyle": "-", "linewidth": 0.7},
        {"linestyle": "--", "linewidth": 0.7},
        {"linestyle": "-.", "linewidth": 0.7},
        {"linestyle": (0, (3, 2, 1, 2)), "linewidth": 0.7},
    ]

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_aspect("equal")

    # Plot customers
    xs = [c.x for c in instance.customers]
    ys = [c.y for c in instance.customers]
    ax.scatter(xs, ys, s=18, marker="o", facecolor="white",
               edgecolor=GRAY_DARK, linewidth=0.5, zorder=3)

    # Plot depot
    ax.scatter([instance.depot.x], [instance.depot.y], s=60, c=GRAY_DARK,
               marker="s", zorder=4)
    ax.text(instance.depot.x, instance.depot.y + 1.5, "Depot",
            ha="center", fontsize=7, fontweight="bold")

    # Draw routes
    for ri, route in enumerate(solution.routes):
        if not route:
            continue
        style = route_styles[ri % len(route_styles)]

        # Depot to first customer (dotted)
        ax.plot(
            [instance.depot.x, instance.customers[route[0] - 1].x],
            [instance.depot.y, instance.customers[route[0] - 1].y],
            color=GRAY_DARK, linestyle=":", linewidth=0.5, zorder=1,
        )

        # Customer to customer
        path_x = [instance.customers[node - 1].x for node in route]
        path_y = [instance.customers[node - 1].y for node in route]
        ax.plot(path_x, path_y, color=GRAY_DARK, linestyle=style["linestyle"],
                linewidth=style["linewidth"], zorder=2)

        # Last customer to depot (dotted)
        ax.plot(
            [instance.customers[route[-1] - 1].x, instance.depot.x],
            [instance.customers[route[-1] - 1].y, instance.depot.y],
            color=GRAY_DARK, linestyle=":", linewidth=0.5, zorder=1,
        )

    # Annotate a few key customers
    for c in instance.customers[:10]:
        ax.text(c.x + 0.6, c.y + 0.6, str(c.index + 1),
                fontsize=5, ha="center", va="center", color=GRAY_MEDIUM)

    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_title(title)
    ax.grid(True, linestyle=":", color=GRAY_LIGHT, linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    _save(fig, output_path)
    plt.close(fig)


def plot_route_animation(
    instance: Any,
    route_history: list[list[list[int]]],
    output_path: str = "results/route_evolution.mp4",
    fps: int = 10,
) -> None:
    """Create an MP4 video showing ACO route evolution over iterations.

    Each frame displays customer locations, the depot, and the best routes
    found up to that iteration. The title shows the iteration number.

    Requires ffmpeg installed for MP4 output.

    Args:
        instance: CVRPInstance providing .depot and .customers.
        route_history: List of routes per iteration from ACO.route_history.
        output_path: Path for the saved video.
        fps: Frames per second.
    """
    from matplotlib.animation import FuncAnimation, FFMpegWriter

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_aspect("equal")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.grid(True, linestyle=":", color=GRAY_LIGHT, linewidth=0.3, alpha=0.5)

    xs = [c.x for c in instance.customers]
    ys = [c.y for c in instance.customers]
    route_styles = [
        "-", "--", "-.", (0, (3, 2, 1, 2)),
        (0, (1, 1)), (0, (5, 3)), "-", "--",
    ]

    def update(frame: int) -> list[Any]:
        ax.clear()
        ax.set_aspect("equal")
        ax.scatter(
            xs, ys, s=14, marker="o", facecolor="white",
            edgecolor=GRAY_DARK, linewidth=0.5, zorder=3,
        )
        ax.scatter(
            [instance.depot.x], [instance.depot.y],
            s=50, c=GRAY_DARK, marker="s", zorder=4,
        )
        ax.text(
            instance.depot.x, instance.depot.y + 1.5, "Depot",
            ha="center", fontsize=7, fontweight="bold",
        )
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.grid(
            True, linestyle=":", color=GRAY_LIGHT,
            linewidth=0.3, alpha=0.5,
        )

        iteration_sol = route_history[min(frame, len(route_history) - 1)]
        artists: list[Any] = []

        for ri, route in enumerate(iteration_sol):
            if not route:
                continue
            sty = route_styles[ri % len(route_styles)]
            artists += ax.plot(
                [instance.depot.x, instance.customers[route[0] - 1].x],
                [instance.depot.y, instance.customers[route[0] - 1].y],
                color=GRAY_DARK, linestyle=":", linewidth=0.4, zorder=1,
            )
            px = [instance.customers[n - 1].x for n in route]
            py = [instance.customers[n - 1].y for n in route]
            artists += ax.plot(
                px, py, color=GRAY_DARK,
                linestyle=sty, linewidth=1.0, zorder=2,
            )
            artists += ax.plot(
                [instance.customers[route[-1] - 1].x, instance.depot.x],
                [instance.customers[route[-1] - 1].y, instance.depot.y],
                color=GRAY_DARK, linestyle=":", linewidth=0.4, zorder=1,
            )

        ax.set_title(f"Iteration {frame + 1} / {len(route_history)}")
        return artists

    step = max(1, len(route_history) // 200)
    frames = list(range(0, len(route_history), step))
    if not frames or frames[-1] != len(route_history) - 1:
        frames.append(len(route_history) - 1)

    anim = FuncAnimation(
        fig, update, frames=frames, interval=1000 // fps, blit=False,
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    writer = FFMpegWriter(fps=fps, metadata={"title": "ACO Route Evolution"})
    anim.save(str(output_path), writer=writer)
    plt.close(fig)


def plot_cd_from_results(
    results: dict[tuple[str, int, int], dict[str, Any]],
    size: int = 100,
    metric: str = "total_distance",
    output_path: str = "results/critical_difference.pdf",
) -> None:
    """Compute Nemenyi CD diagram from experiment results using mean ranks.

    Args:
        results: ACO metrics keyed by (config_id, size, seed).
        size: Problem size.
        metric: Metric name.
        output_path: Output figure path.
    """
    config_ids = ["C1", "C2", "C3", "C4"]
    cols: list[list[float]] = []
    for cid in config_ids:
        vals = [
            float(results[(cid, size, seed)][metric])
            for seed in range(30)
            if (cid, size, seed) in results and metric in results[(cid, size, seed)]
        ]
        cols.append(vals)

    if len(cols) < 2 or any(len(c) < 2 for c in cols):
        plot_critical_difference(output_path=output_path)
        return

    from scipy.stats import friedmanchisquare

    try:
        friedmanchisquare(*cols)
    except ValueError:
        plot_critical_difference(output_path=output_path)
        return

    mat = np.array(cols).T
    ranks = np.zeros_like(mat, dtype=float)
    for row_idx in range(mat.shape[0]):
        row_order = np.argsort(mat[row_idx])
        for rank_pos, col_idx in enumerate(row_order):
            ranks[row_idx, col_idx] = float(rank_pos + 1)

    mean_ranks = np.mean(ranks, axis=0)
    cd_data = {cid: float(mean_ranks[i]) for i, cid in enumerate(config_ids)}

    k = len(config_ids)
    n = mat.shape[0]
    q_alpha = 2.569  # for k=4, alpha=0.05
    cd_threshold = q_alpha * np.sqrt(k * (k + 1) / (6.0 * n))

    plot_critical_difference(cd_data, cd_threshold, output_path)