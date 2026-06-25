"""
aco_vrp: Ant Colony Optimization for Capacitated Vehicle Routing Problem.

A research toolkit for systematic scalability analysis of ACO on Solomon
benchmark instances. Provides core algorithm implementation, problem
representation, baseline heuristics, experiment orchestration, statistical
analysis, and visualization.

Modules:
    core         ACO algorithm (ant-based constructive heuristic with
                 pheromone update, evaporation, and local search)
    problem      CVRP representation, Solomon instance parser, solution
                 evaluation (distance, feasibility, fleet count)
    heuristics   Baseline methods: Nearest Neighbor constructive and
                 Clarke-Wright Savings algorithm
    experiment   Experiment matrix execution, parallel run management,
                 result serialization
    analysis     Nonparametric statistical testing (Friedman, Wilcoxon,
                 Nemenyi post-hoc) and result aggregation
    visualization Pheromone heatmaps, convergence curves, parameter
                 interaction plots, critical difference diagrams
"""

__all__ = [
    "core",
    "problem",
    "heuristics",
    "experiment",
    "analysis",
    "visualization",
]
