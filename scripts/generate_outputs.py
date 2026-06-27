"""Comprehensive output generation script.

Generates all research outputs organized by type:
  route_maps/    Per-vehicle route maps (SVG)
  route_videos/  Per-vehicle route construction videos (MP4)
  aggregated/    Aggregate plots: scalability, heatmap, CD diagram, convergence
  3d/            3D visualizations: pheromone surface, scalability surface
  anime/         Animations: pheromone evolution
  data/          CSV data files
  report/        Statistical report

Usage:
    python scripts/generate_outputs.py
"""

import csv
import sys
import time
from pathlib import Path

import numpy as np

from aco_vrp.core import ACO, ACOConfig
from aco_vrp.experiment import ExperimentRunner
from aco_vrp.problem import load_solomon
from aco_vrp.visualization import (
    plot_3d_pheromone_surface,
    plot_3d_scalability_surface,
    plot_cd_from_results,
    plot_convergence,
    plot_parameter_heatmap,
    plot_pheromone_animation,
    plot_route_map,
    plot_route_videos,
    plot_scalability,
    plot_vehicle_route_map,
)

BASE = Path("results")
DIRS = {
    "route_maps": BASE / "route_maps",
    "route_videos": BASE / "route_videos",
    "aggregated": BASE / "aggregated",
    "3d": BASE / "3d",
    "anime": BASE / "anime",
    "data": BASE / "data",
    "report": BASE / "report",
}
for d in DIRS.values():
    d.mkdir(parents=True, exist_ok=True)


def main() -> None:
    start = time.perf_counter()

    results = {}
    baseline = {}
    try:
        with open(BASE / "raw_runs.csv", "r") as f:
            for row in csv.DictReader(f):
                key = (row["config_id"], int(row["size"]), int(row["seed"]))
                results[key] = {"total_distance": float(row["total_distance"]),
                                "vehicle_count": int(row["vehicle_count"])}
        with open(BASE / "baseline_runs.csv", "r") as f:
            for row in csv.DictReader(f):
                baseline[(row["heuristic"], int(row["size"]))] = {
                    "total_distance": float(row["total_distance"]),
                    "vehicle_count": int(row["vehicle_count"]),
                }
        print("Loaded existing experiment data.")
    except FileNotFoundError:
        print("No existing CSV data. Run experiments first.")
        sys.exit(1)

    inst = load_solomon("data/solomon/RC101.txt")
    config = ACOConfig(alpha=2.0, beta=2.0, rho=0.3, ant_count=10,
                       max_iterations=100, use_local_search=True)

    conv_exp = ExperimentRunner(data_dir="data/solomon")
    conv_results = conv_exp.run_full_matrix(seeds=3)
    conv_data: dict[tuple[str, int], list[float]] = {}
    counts: dict[tuple[str, int], int] = {}
    for (config_id, size, _seed), metrics in conv_results.items():
        history = metrics.get("convergence_history", [])
        if not history:
            continue
        key = (config_id, size)
        if key not in conv_data:
            conv_data[key] = [0.0] * len(history)
            counts[key] = 0
        for i, val in enumerate(history):
            if i < len(conv_data[key]):
                conv_data[key][i] += val
        counts[key] += 1
    for key in conv_data:
        conv_data[key] = [v / counts[key] for v in conv_data[key]]
    print(f"Collected convergence data for {len(conv_data)} cells.\n")

    # Per-vehicle route maps + per-vehicle videos
    for size in [25, 50, 100]:
        sub = inst.subset(size)
        aco = ACO(config)
        sol = aco.solve(sub, seed=0)
        print(f"\nSize {size}: dist={sol.total_distance:.1f}, {sol.vehicle_count} vehicles")

        plot_route_map(sub, sol, f"ACO Route Map ({size} Customers)",
                       str(DIRS["route_maps"] / f"route_map_{size}.svg"))
        print(f"  route_map_{size}.svg")

        for ri, route in enumerate(sol.routes):
            if not route:
                continue
            plot_vehicle_route_map(
                sub, route, ri + 1,
                title=f"Size {size}",
                output_path=str(DIRS["route_maps"] / f"route_map_{size}_v{ri + 1}.svg"),
            )
            print(f"  route_map_{size}_v{ri + 1}.svg")

        plot_route_videos(sub, sol, str(DIRS["route_videos"] / f"size_{size}"), fps=5)
        print(f"  {sol.vehicle_count} videos in route_videos/size_{size}/")

    # Pheromone evolution animation
    sub25 = inst.subset(25)
    aco25 = ACO(config)
    sol25 = aco25.solve(sub25, seed=0)
    plot_pheromone_animation(sub25, aco25.pheromone_snapshots,
                             str(DIRS["anime"] / "pheromone_evolution.mp4"), fps=4)
    print(f"\nPheromone evolution: {len(aco25.pheromone_snapshots)} frames")

    # 3D plots
    plot_3d_scalability_surface(results, size=100,
                                output_path=str(DIRS["3d"] / "scalability_3d.svg"))
    print("3d/scalability_3d.svg")

    sol100_ac = ACO(config)
    sol100 = sol100_ac.solve(inst.subset(100), seed=0)
    tau = np.zeros((101, 101))
    for sn in sol100_ac.pheromone_snapshots:
        tau += sn
    tau /= len(sol100_ac.pheromone_snapshots) if sol100_ac.pheromone_snapshots else 1
    plot_3d_pheromone_surface(inst.subset(100), tau,
                              str(DIRS["3d"] / "pheromone_3d.svg"))
    print("3d/pheromone_3d.svg")

    # Aggregated plots
    plot_scalability(results, baseline_results=baseline,
                     output_path=str(DIRS["aggregated"] / "scalability_plot.svg"))
    print("aggregated/scalability_plot.svg")

    plot_parameter_heatmap(results, size=100,
                           output_path=str(DIRS["aggregated"] / "parameter_heatmap.svg"))
    print("aggregated/parameter_heatmap.svg")

    plot_cd_from_results(results, size=100,
                         output_path=str(DIRS["aggregated"] / "critical_difference.svg"))
    print("aggregated/critical_difference.svg")

    plot_convergence(conv_data,
                     output_path=str(DIRS["aggregated"] / "convergence_curves.svg"))
    print("aggregated/convergence_curves.svg")

    # Copy CSV data
    import shutil
    import statistics

    for csv_file in ["raw_runs.csv", "baseline_runs.csv"]:
        src = BASE / csv_file
        if src.exists():
            shutil.copy2(src, DIRS["data"] / csv_file)
            print(f"data/{csv_file}")

    from aco_vrp.analysis import StatisticalAnalyzer
    analyzer = StatisticalAnalyzer(results, alpha=0.05)
    report_path = DIRS["report"] / "statistical_report.txt"
    with open(report_path, "w") as r:
        for size in [25, 50, 100]:
            r.write(f"Size = {size}\n")
            try:
                stat, pval = analyzer.friedman_test("total_distance", size)
                sig = "SIGNIFICANT" if pval < 0.05 else "not significant"
                r.write(f"Friedman: stat={stat:.4f}, p={pval:.6f} ({sig})\n")
            except ValueError:
                pass
            configs = analyzer._discover_configs(size)
            for i, ca in enumerate(configs):
                for cb in configs[i + 1 :]:
                    try:
                        _, pval = analyzer.wilcoxon_signed_rank(ca, cb, "total_distance", size)
                        r.write(f"  Wilcoxon {ca} vs {cb}: p={pval:.6f}")
                        r.write(" *\n" if pval < 0.05 else "\n")
                    except ValueError:
                        pass
            r.write("\n")
        for cid in ["C1", "C2", "C3", "C4"]:
            for sz in [25, 50, 100]:
                vals = [
                    v["total_distance"]
                    for (c, s, _), v in results.items()
                    if c == cid and s == sz
                ]
                if vals:
                    r.write(
                        f"{cid} size={sz}: "
                        f"mean={statistics.mean(vals):.1f}, "
                        f"std={statistics.stdev(vals):.1f}, "
                        f"n={len(vals)}\n"
                    )
    print("report/statistical_report.txt")

    elapsed = time.perf_counter() - start
    print(f"\nAll outputs generated in {elapsed:.0f}s ({elapsed/60:.1f}min)")


if __name__ == "__main__":
    main()
