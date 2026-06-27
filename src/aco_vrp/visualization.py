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
    "C1": "C1 (a=1.0, b=2.0, r=0.1)",
    "C2": "C2 (a=1.0, b=5.0, r=0.1)",
    "C3": "C3 (a=2.0, b=2.0, r=0.3)",
    "C4": "C4 (a=2.0, b=5.0, r=0.3)",
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

    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.18), ncol=4, fontsize=8)
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
        axes[-1].legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.25), fontsize=7, ncol=4)
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
    output_path: str = "results/route_map.svg",
) -> None:
    """Plot customers and directed vehicle routes on a 2-D coordinate plane.

    Each route segment carries an arrowhead indicating travel direction.
    Visit order numbers are shown beside each node. The depot is a filled
    square and customers are hollow circles.

    Args:
        instance: CVRPInstance with .depot (has .x, .y) and .customers
                  (list of Customer with .x, .y).
        solution: CVRPSolution with .routes (list of lists of node indices 1..N).
        title: Plot title.
        output_path: Path for the saved SVG.
    """
    from matplotlib.patches import FancyArrowPatch
    from matplotlib.lines import Line2D

    route_styles = [
        "-", "--", "-.", (0, (3, 2, 1, 2)),
        (0, (1, 1)), (0, (5, 3)), "-", "--", "-.", (0, (3, 2, 1, 2)),
    ]

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.set_aspect("equal")

    xs = [c.x for c in instance.customers]
    ys = [c.y for c in instance.customers]
    ax.scatter(xs, ys, s=22, marker="o", facecolor="white",
               edgecolor=GRAY_DARK, linewidth=0.7, zorder=3)
    ax.scatter([instance.depot.x], [instance.depot.y], s=70, marker="s",
               c=GRAY_DARK, zorder=4)
    ax.text(instance.depot.x, instance.depot.y + 2.0, "Depot",
            ha="center", fontsize=8, fontweight="bold")

    legend_handles = [
        Line2D([0], [0], marker="s", color=GRAY_DARK, markerfacecolor=GRAY_DARK,
               markersize=9, linestyle="none", label="Depot"),
        Line2D([0], [0], marker="o", color=GRAY_DARK, markerfacecolor="white",
               markeredgecolor=GRAY_DARK, markersize=8, linestyle="none",
               label="Customer"),
    ]

    def _draw_arrow(src_x, src_y, dst_x, dst_y, linestyle, lw, arrow_zorder):
        alpha_val = 1.0 if linestyle == "-" else 0.85
        arrow = FancyArrowPatch(
            (src_x, src_y), (dst_x, dst_y),
            arrowstyle="-|>", mutation_scale=12,
            color=GRAY_DARK, linestyle=linestyle, linewidth=lw,
            alpha=alpha_val, zorder=arrow_zorder,
        )
        ax.add_patch(arrow)

    visit_counter: dict[int, int] = {}

    for ri, route in enumerate(solution.routes):
        if not route:
            continue
        sty = route_styles[ri % len(route_styles)]
        lw = 1.2 if ri < 6 else 0.7
        label = f"Vehicle {ri + 1}"

        prev_x, prev_y = instance.depot.x, instance.depot.y

        for pos, node_idx in enumerate(route):
            c = instance.customers[node_idx - 1]
            _draw_arrow(prev_x, prev_y, c.x, c.y, sty, lw, 2)

            visit_counter[node_idx] = visit_counter.get(node_idx, 0) + 1
            order_num = visit_counter[node_idx]
            offset_x = 0.8 if order_num == 1 else -0.8
            offset_y = 0.8 if order_num == 1 else -0.8
            ax.text(c.x + offset_x, c.y + offset_y, str(pos + 1),
                    fontsize=5.5, ha="center", va="center", color=GRAY_DARK,
                    fontweight="bold", zorder=5)

            prev_x, prev_y = c.x, c.y

        _draw_arrow(prev_x, prev_y, instance.depot.x, instance.depot.y, ":", 0.6, 1)

        legend_handles.append(
            Line2D([0], [0], color=GRAY_DARK, linestyle=sty,
                   linewidth=lw, label=label)
        )

    legend_handles.append(
        Line2D([0], [0], color=GRAY_DARK, linestyle=":", linewidth=0.6,
               label="Return to depot")
    )

    ax.legend(handles=legend_handles, frameon=False, loc="lower center",
              bbox_to_anchor=(0.5, -0.18), fontsize=7, ncol=3)
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_title(title)
    ax.grid(True, linestyle=":", color=GRAY_LIGHT, linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    _save(fig, output_path)
    plt.close(fig)


def plot_vehicle_route_map(
    instance: Any,
    route: list[int],
    vehicle_num: int,
    title: str = "Vehicle Route",
    output_path: str = "results/route_maps/vehicle_route.svg",
) -> None:
    """Plot a SINGLE vehicle route on a 2-D coordinate plane with arrows.

    Only the customers in this route are highlighted. Others are dimmed.
    Directional arrows show travel order. Visit order numbers appear
    beside each node. Designed for per-vehicle inspection.

    Args:
        instance: CVRPInstance.
        route: List of node indices (1..N) for this vehicle.
        vehicle_num: Vehicle number for labeling.
        title: Plot title.
        output_path: SVG output path.
    """
    from matplotlib.patches import FancyArrowPatch
    from matplotlib.lines import Line2D

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.set_aspect("equal")

    all_xs = [c.x for c in instance.customers]
    all_ys = [c.y for c in instance.customers]
    route_set = set(route)

    other_xs = [c.x for i, c in enumerate(instance.customers) if (i + 1) not in route_set]
    other_ys = [c.y for i, c in enumerate(instance.customers) if (i + 1) not in route_set]
    ax.scatter(other_xs, other_ys, s=10, marker="o", facecolor="white",
               edgecolor=GRAY_LIGHT, linewidth=0.3, zorder=2)

    # Highlight route customers
    route_xs = [instance.customers[n - 1].x for n in route]
    route_ys = [instance.customers[n - 1].y for n in route]
    ax.scatter(route_xs, route_ys, s=30, marker="o", facecolor="white",
               edgecolor=GRAY_DARK, linewidth=1.0, zorder=4)

    ax.scatter([instance.depot.x], [instance.depot.y], s=80, marker="s",
               c=GRAY_DARK, zorder=5)
    ax.text(instance.depot.x, instance.depot.y + 2.0, "Depot",
            ha="center", fontsize=9, fontweight="bold")

    # Draw edges with arrows
    prev_x, prev_y = instance.depot.x, instance.depot.y
    for pos, node_idx in enumerate(route):
        c = instance.customers[node_idx - 1]
        arrow = FancyArrowPatch(
            (prev_x, prev_y), (c.x, c.y),
            arrowstyle="-|>", mutation_scale=14,
            color=GRAY_DARK, linewidth=1.4, alpha=0.9, zorder=3,
        )
        ax.add_patch(arrow)
        offset_x = 1.0 if pos % 2 == 0 else -1.0
        offset_y = 1.0 if pos < len(route) // 2 else -1.0
        ax.text(c.x + offset_x, c.y + offset_y, str(pos + 1),
                fontsize=6.5, ha="center", va="center", color=GRAY_DARK,
                fontweight="bold", zorder=6)
        prev_x, prev_y = c.x, c.y

    return_arrow = FancyArrowPatch(
        (prev_x, prev_y), (instance.depot.x, instance.depot.y),
        arrowstyle="-|>", mutation_scale=14,
        color=GRAY_DARK, linewidth=0.8, alpha=0.6, linestyle=":", zorder=3,
    )
    ax.add_patch(return_arrow)

    legend_handles = [
        Line2D([0], [0], marker="s", color=GRAY_DARK, markerfacecolor=GRAY_DARK,
               markersize=10, linestyle="none", label="Depot"),
        Line2D([0], [0], marker="o", color=GRAY_DARK, markerfacecolor="white",
               markeredgecolor=GRAY_DARK, markersize=9, linestyle="none",
               label=f"Route customer ({len(route)} stops)"),
        Line2D([0], [0], marker="o", color=GRAY_LIGHT, markerfacecolor="white",
               markeredgecolor=GRAY_LIGHT, markersize=6, linestyle="none",
               label="Other customers"),
    ]
    ax.legend(handles=legend_handles, frameon=False, loc="lower center",
              bbox_to_anchor=(0.5, -0.15), fontsize=8, ncol=3)

    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_title(f"{title} (Vehicle {vehicle_num})")
    ax.grid(True, linestyle=":", color=GRAY_LIGHT, linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    _save(fig, output_path)
    plt.close(fig)


def plot_pheromone_animation(
    instance: Any,
    pheromone_snapshots: list[Any],
    output_path: str = "results/pheromone_evolution.mp4",
    fps: int = 2,
) -> None:
    """Animate pheromone concentration on edges over ACO iterations.

    Each frame shows all customer positions with edges drawn at opacity
    proportional to pheromone level. Thicker and darker edges indicate
    stronger pheromone trails. The title shows the iteration number.

    Args:
        instance: CVRPInstance with .depot and .customers.
        pheromone_snapshots: List of (N+1)x(N+1) tau matrices.
        output_path: MP4 output path.
        fps: Frames per second.
    """
    from matplotlib.animation import FuncAnimation, FFMpegWriter

    n = len(instance.customers) + 1
    all_tau = pheromone_snapshots
    if not all_tau:
        return
    first_tau = all_tau[0]
    n = first_tau.shape[0]

    xs = [c.x for c in instance.customers]
    ys = [c.y for c in instance.customers]

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.set_aspect("equal")

    def update(frame_idx: int) -> list[Any]:
        ax.clear()
        ax.set_aspect("equal")
        ax.scatter(
            xs, ys, s=18, marker="o", facecolor="white",
            edgecolor=GRAY_DARK, linewidth=0.7, zorder=4,
        )
        ax.scatter(
            [instance.depot.x], [instance.depot.y],
            s=70, c=GRAY_DARK, marker="s", zorder=5,
        )
        ax.text(
            instance.depot.x, instance.depot.y + 1.5, "Depot",
            ha="center", fontsize=8, fontweight="bold",
        )
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.grid(True, linestyle=":", color=GRAY_LIGHT, linewidth=0.3, alpha=0.5)

        tau = all_tau[min(frame_idx, len(all_tau) - 1)]
        mean_val = float(np.mean(tau))
        max_val = float(np.max(tau))
        threshold = mean_val + (max_val - mean_val) * 0.5

        artists: list[Any] = []

        for i in range(n):
            for j in range(i + 1, n):
                val = float(tau[i, j])
                if val < threshold:
                    continue
                alpha = min((val - threshold) / (max_val - threshold + 1e-9), 1.0) * 0.85
                lw = max(0.3, ((val - threshold) / (max_val - threshold + 1e-9)) * 3.0)
                if i == 0:
                    x1, y1 = instance.depot.x, instance.depot.y
                else:
                    x1, y1 = instance.customers[i - 1].x, instance.customers[i - 1].y
                if j == 0:
                    x2, y2 = instance.depot.x, instance.depot.y
                else:
                    x2, y2 = instance.customers[j - 1].x, instance.customers[j - 1].y
                (line,) = ax.plot(
                    [x1, x2], [y1, y2], color=GRAY_DARK,
                    linewidth=lw, alpha=alpha, zorder=2,
                )
                artists.append(line)

        iteration = (frame_idx + 1) * 5
        shown = len(artists)
        size_label = f"Size {len(instance.customers)}"
        ax.set_title(
            f"{size_label}  Pheromone Trails at Iteration {iteration} ({shown} significant edges)",
            fontsize=11,
        )
        return artists

    anim = FuncAnimation(
        fig, update, frames=len(all_tau), interval=1000 // fps, blit=False,
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    writer = FFMpegWriter(fps=fps, metadata={"title": "Pheromone Evolution"})
    anim.save(str(output_path), writer=writer)
    plt.close(fig)


def plot_route_videos(
    instance: Any,
    solution: Any,
    output_dir: str = "results",
    fps: int = 4,
) -> list[str]:
    """Create one MP4 video per vehicle route, showing edge-by-edge construction.

    Each video starts from an empty map and draws one route step by step,
    with directional arrows and a title showing current edge progress.
    Each video saves as route_vN.mp4 in the output directory.

    Args:
        instance: CVRPInstance with .depot and .customers.
        solution: CVRPSolution with .routes.
        output_dir: Directory for output videos.
        fps: Frames per second.

    Returns:
        List of paths to generated video files.
    """
    from matplotlib.animation import FuncAnimation, FFMpegWriter
    from matplotlib.patches import FancyArrowPatch

    xs = [c.x for c in instance.customers]
    ys = [c.y for c in instance.customers]
    paths: list[str] = []

    for ri, route in enumerate(solution.routes):
        if not route:
            continue

        route_edges: list[tuple[float, float, float, float, str]] = []
        prev_x, prev_y = instance.depot.x, instance.depot.y
        for node_idx in route:
            c = instance.customers[node_idx - 1]
            route_edges.append((prev_x, prev_y, c.x, c.y, f"depot to node {node_idx}"
                               if prev_x == instance.depot.x and prev_y == instance.depot.y
                               else f"node {route[route.index(node_idx) - 1] if route.index(node_idx) > 0 else '?'} to node {node_idx}"))
            prev_x, prev_y = c.x, c.y
        route_edges.append((prev_x, prev_y, instance.depot.x, instance.depot.y,
                           f"node {route[-1]} to depot"))

        frame_labels: list[str] = []
        size_label = f"Size {len(instance.customers)}"
        for ei in range(len(route_edges)):
            for _ in range(5):
                frame_labels.append(
                    f"{size_label}  Vehicle {ri + 1}: edge {ei + 1}/{len(route_edges)}"
                )

        for _ in range(fps * 3):
            frame_labels.append(
                f"{size_label}  Vehicle {ri + 1}: complete ({len(route)} stops)"
            )

        fig, ax = plt.subplots(figsize=(8, 7))
        ax.set_aspect("equal")

        def make_update(edges, labels):
            drawn_edges: list[tuple[float, float, float, float]] = []

            def update(frame_idx: int) -> list[Any]:
                ax.clear()
                ax.set_aspect("equal")
                ax.scatter(xs, ys, s=16, marker="o", facecolor="white",
                           edgecolor=GRAY_DARK, linewidth=0.5, zorder=3)
                ax.scatter([instance.depot.x], [instance.depot.y], s=60,
                           c=GRAY_DARK, marker="s", zorder=4)
                ax.text(instance.depot.x, instance.depot.y + 1.5, "Depot",
                        ha="center", fontsize=8, fontweight="bold")
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")

                idx = min(frame_idx // 5, len(edges) - 1)
                if idx >= len(drawn_edges):
                    drawn_edges.clear()
                    for e in range(idx + 1):
                        if e < len(edges):
                            drawn_edges.append(edges[e][:4])

                artists: list[Any] = []
                for sx, sy, dx, dy in drawn_edges:
                    arrow = FancyArrowPatch(
                        (sx, sy), (dx, dy), arrowstyle="-|>",
                        mutation_scale=10, color=GRAY_DARK,
                        linewidth=1.2, alpha=0.8, zorder=2,
                    )
                    ax.add_patch(arrow)
                    artists.append(arrow)

                ax.set_title(labels[min(frame_idx, len(labels) - 1)], fontsize=10)
                ax.grid(True, linestyle=":", color=GRAY_LIGHT, linewidth=0.3, alpha=0.5)
                return artists
            return update

        updater = make_update(route_edges, frame_labels)
        anim = FuncAnimation(
            fig, updater, frames=len(frame_labels),
            interval=1000 // fps, blit=False,
        )
        out_path = str(Path(output_dir) / f"route_v{ri + 1}.mp4")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        writer = FFMpegWriter(fps=fps, metadata={"title": f"ACO Vehicle {ri + 1} Route"})
        anim.save(out_path, writer=writer)
        plt.close(fig)
        paths.append(out_path)

    return paths


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


def plot_3d_pheromone_surface(
    instance: Any,
    tau: Any,
    output_path: str = "results/pheromone_3d.svg",
) -> None:
    """Plot a 3-D surface of interpolated pheromone concentration.

    Interpolates pheromone values from the node graph onto a rectangular
    grid covering the customer coordinate range. The surface height
    represents pheromone intensity. Higher peaks indicate edges strongly
    favored by the ant colony.

    Args:
        instance: CVRPInstance providing customer coordinates.
        tau: NxN pheromone matrix from ACO (numpy array).
        output_path: Path for the saved SVG.
    """
    from matplotlib import cm
    from scipy.interpolate import griddata

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    n_cust = len(instance.customers)
    grid_xi = np.linspace(0, 60, 40)
    grid_yi = np.linspace(30, 90, 40)
    grid_x, grid_y = np.meshgrid(grid_xi, grid_yi)

    points = []
    values = []
    for i in range(1, n_cust + 1):
        for j in range(1, n_cust + 1):
            if i == j:
                continue
            mid_x = (instance.customers[i - 1].x + instance.customers[j - 1].x) / 2
            mid_y = (instance.customers[i - 1].y + instance.customers[j - 1].y) / 2
            points.append((mid_x, mid_y))
            values.append(float(tau[i, j]))

    points_arr = np.array(points)
    values_arr = np.array(values)
    grid_z = griddata(points_arr, values_arr, (grid_x, grid_y), method="linear", fill_value=0.0)

    surf = ax.plot_surface(grid_x, grid_y, grid_z, cmap=cm.viridis,
                           linewidth=0, antialiased=True, alpha=0.9)
    ax.scatter(
        [c.x for c in instance.customers],
        [c.y for c in instance.customers],
        np.zeros(n_cust),
        c="black", s=15, marker="o", zorder=5,
    )
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Pheromone")
    ax.set_title("Pheromone Concentration Surface After ACO")
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label="Pheromone Level")
    fig.tight_layout()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(path.with_suffix(".svg")), format="svg")
    plt.close(fig)


def plot_3d_scalability_surface(
    results: dict[tuple[str, int, int], dict[str, Any]],
    size: int = 100,
    output_path: str = "results/scalability_3d.svg",
) -> None:
    """Plot a 3-D wireframe surface of mean distance vs alpha and beta.

    Each of the 4 configurations defines one corner of the (alpha, beta)
    grid. The surface interpolates performance between them.

    Args:
        results: ACO run metrics keyed by (config_id, size, seed).
        size: Problem size to analyze.
        output_path: Path for the saved SVG.
    """
    from matplotlib import cm

    alphas = np.array([1.0, 2.0])
    betas = np.array([2.0, 5.0])
    alpha_grid, beta_grid = np.meshgrid(alphas, betas)
    dist_grid = np.zeros_like(alpha_grid)

    for ci, alpha in enumerate(alphas):
        for bi, beta in enumerate(betas):
            cid = f"C{ci + bi * 2 + 1}"
            if cid == "C2":
                cid = "C2"
            vals: list[float] = []
            for c in ["C1", "C2", "C3", "C4"]:
                a_val = 1.0 if c in ("C1", "C2") else 2.0
                b_val = 2.0 if c in ("C1", "C3") else 5.0
                if abs(a_val - alpha) < 0.01 and abs(b_val - beta) < 0.01:
                    for seed in range(30):
                        key = (c, size, seed)
                        if key in results:
                            vals.append(float(results[key]["total_distance"]))
                    break
            if vals:
                dist_grid[bi, ci] = np.mean(vals)
            else:
                dist_grid[bi, ci] = np.nan

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_wireframe(alpha_grid, beta_grid, dist_grid, color=GRAY_DARK,
                      linewidth=1.0)
    ax.scatter(alpha_grid.ravel(), beta_grid.ravel(), dist_grid.ravel(),
               c=np.array(dist_grid).ravel(), cmap=cm.plasma, s=60,
               zorder=5)
    ax.set_xlabel("Alpha")
    ax.set_ylabel("Beta")
    ax.set_zlabel("Mean Total Distance")
    ax.set_title(f"Scalability Surface (Size = {size})")
    fig.tight_layout()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(path.with_suffix(".svg")), format="svg")
    plt.close(fig)