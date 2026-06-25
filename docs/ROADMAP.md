# Development Roadmap: ACO-CVRP Scalability Analysis

**Status:** Foundation phase  
**Last updated:** June 2026

## Overview

This roadmap organizes development into sequential milestones. Each
milestone depends on the completion of the previous one. Milestones are
designed to produce a verifiable increment of research capability.

## Milestone 0: Foundation (current)

Establish project structure, dependency management, documentation,
and skeleton code. No algorithm implementation yet.

Tasks:

- [x] Create project directory structure
- [x] Configure `pyproject.toml` with `uv` dependency management
- [x] Add MIT license
- [x] Write README with abstract, reproducibility notes, and citation
- [x] Create package skeleton with module docstrings
- [x] Create test skeleton with placeholder files
- [x] Write METHODOLOGY.md with full experimental protocol
- [x] Write ROADMAP.md (this file)
- [ ] Verify `uv sync` installs all dependencies cleanly
- [ ] Verify `uv run pytest` executes without import errors

## Milestone 1: Data and Problem Representation

Implement the CVRP problem representation and Solomon instance loader.

Tasks:

- [ ] Implement `Customer`, `Depot`, `CVRPInstance`, `CVRPSolution`
  dataclasses in `src/aco_vrp/problem.py`
- [ ] Implement Solomon RC101 text parser
- [ ] Implement distance matrix computation
- [ ] Implement solution feasibility checking (capacity constraint)
- [ ] Implement subset extraction (first N customers)
- [ ] Write `scripts/download_solomon.py` to fetch the dataset
- [ ] Write unit tests for all problem module functions
- [ ] Verify RC101 loads correctly: 100 customers, correct depot
  coordinates, valid distance matrix

## Milestone 2: Baseline Heuristics

Implement constructive heuristics for comparison.

Tasks:

- [ ] Implement Nearest Neighbor in `src/aco_vrp/heuristics.py`
- [ ] Implement Clarke-Wright Savings algorithm
- [ ] Validate outputs against literature values for RC101
- [ ] Write unit tests covering edge cases
- [ ] Generate baseline results for sizes 25, 50, 100
- [ ] Save baseline summary to `results/baseline_summary.csv`

## Milestone 3: ACO Core Algorithm

Implement the full Ant Colony Optimization algorithm.

Tasks:

- [ ] Implement pheromone matrix initialization
- [ ] Implement ant solution construction with capacity constraints
- [ ] Implement pheromone evaporation and deposition
- [ ] Implement elitist update on global best
- [ ] Implement 2-opt local search (optional, toggleable)
- [ ] Implement convergence tracking and termination
- [ ] Write unit tests on small handcrafted instances
- [ ] Benchmark on RC101 against literature best-known solutions

## Milestone 4: Experiment Orchestration

Implement the experiment runner and parallel execution.

Tasks:

- [ ] Implement `ExperimentRunner` with configuration matrix
- [ ] Implement deterministic seeding across configurations
- [ ] Implement parallel execution with `concurrent.futures`
- [ ] Implement progress logging and checkpoint saving
- [ ] Implement result serialization to CSV
- [ ] Write integration tests for a minimal experiment run
- [ ] Execute a trial run (1 seed, all configurations, all sizes)
  and validate output

## Milestone 5: Statistical Analysis

Implement nonparametric statistical tests.

Tasks:

- [ ] Implement Friedman test via `scipy.stats`
- [ ] Implement Wilcoxon signed-rank test
- [ ] Implement Holm correction for multiple comparisons
- [ ] Implement Nemenyi post-hoc critical difference computation
- [ ] Implement descriptive statistics aggregation
- [ ] Implement scalability regression analysis
- [ ] Write unit tests against known statistical outputs
- [ ] Generate `results/statistical_report.txt`

## Milestone 6: Visualization

Generate publication-quality figures and animations.

Tasks:

- [ ] Implement scalability plot with confidence bands
- [ ] Implement parameter interaction heatmap
- [ ] Implement convergence curve overlay
- [ ] Implement Nemenyi critical difference diagram
- [ ] Implement pheromone concentration animation (Plotly HTML)
- [ ] Ensure all plots are colorblind-friendly and publication-ready
- [ ] Write scripts to generate all figures in one command

## Milestone 7: Full Experiment Execution

Run the complete experiment and produce the final results.

Tasks:

- [ ] Execute 4 configs x 3 sizes x 30 seeds = 360 ACO runs
- [ ] Execute baseline runs for all sizes
- [ ] Generate all statistical test outputs
- [ ] Generate all visualizations
- [ ] Validate all results are internally consistent
- [ ] Document any anomalies or unexpected results

## Milestone 8: Manuscript Preparation

Prepare the final research paper.

Tasks:

- [ ] Write abstract (200-300 words)
- [ ] Write introduction with literature review
- [ ] Write methodology section (reference METHODOLOGY.md)
- [ ] Write results section with figures and tables
- [ ] Write discussion section interpreting scalability findings
- [ ] Write conclusion and future work
- [ ] Format references in APA or IEEE style
- [ ] Peer review by team members

## Timeline Estimate

| Milestone | Estimated effort | Cumulative |
| --------- | ---------------- | ---------- |
| M0: Foundation | Done | Done |
| M1: Data and Problem | 1 day | Day 1 |
| M2: Baseline Heuristics | 0.5 day | Day 1.5 |
| M3: ACO Core | 1.5 days | Day 3 |
| M4: Experiment Runner | 0.5 day | Day 3.5 |
| M5: Statistics | 0.5 day | Day 4 |
| M6: Visualization | 0.5 day | Day 4.5 |
| M7: Full Execution | 6 hours (compute) | Day 5 |
| M8: Manuscript | 1 day | Day 6 |

Total human effort: approximately 5-6 days.
Compute time for full experiment: approximately 6 hours (can run overnight).
