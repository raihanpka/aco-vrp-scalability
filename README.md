# Ant Colony Optimization for Capacitated Vehicle Routing Problem: A Scalability Analysis on Solomon Benchmark Instances

## Team

| Name | NIM |
| ---- | --- |
| Aldi Pramudya | G6401231003 |
| Raihan Putra Kirana | G6401231027 |
| Aghnat Hasya Sayyidina | G6401213074 |
| Walid Nadirul Ahnaf | G6401231109 |
| Muhammad Fauzan Zubaedi | G6401231129 |

## Abstract

This project investigates how the performance of Ant Colony Optimization (ACO) scales with problem size when applied to the Capacitated Vehicle Routing Problem (CVRP). The existing ACO-CVRP literature, spanning over 700 publications, reports results almost exclusively at a fixed problem size (typically 100 customers). No prior study has conducted a systematic scalability analysis that documents how convergence speed, solution quality, and reliability degrade as the number of customers increases. This study addresses that methodological gap by evaluating ACO on Solomon instance RC101 at three problem sizes (25, 50, and 100 customers) under four parameter configurations, each repeated across 30 independent runs. Baseline comparisons include the Nearest Neighbor heuristic and the Clarke-Wright Savings algorithm. Statistical significance is assessed using the Friedman test with post-hoc Wilcoxon signed-rank tests and Holm correction. The primary contribution is the first empirical characterization of ACO scaling behavior on a standard benchmark, providing practitioners with evidence-based guidance on configuration selection when problem size varies.

**Keywords:** ant colony optimization, capacitated vehicle routing problem, scalability analysis, Solomon benchmark, swarm intelligence

## Project Structure

```
pkk-swarm-intelligence/
|-- src/
|   `-- aco_vrp/
|       |-- __init__.py          Package initialization
|       |-- core.py              ACO algorithm implementation
|       |-- problem.py           CVRP problem representation and Solomon instance loader
|       |-- heuristics.py        Baseline heuristics (Nearest Neighbor, Savings)
|       |-- experiment.py        Experiment orchestration and parallel execution
|       |-- analysis.py          Statistical analysis module
|       `-- visualization.py     Visualization and plotting utilities
|-- tests/
|   |-- __init__.py
|   |-- conftest.py              Shared test fixtures
|   |-- test_core.py             Unit tests for ACO algorithm
|   |-- test_problem.py          Unit tests for CVRP and data loading
|   `-- test_heuristics.py       Unit tests for baseline heuristics
|-- data/
|   `-- solomon/                 Solomon VRPTW benchmark instances
|-- results/                     Experiment output (figures, tables, logs)
|-- scripts/                     Utility scripts for data download and batch runs
|-- docs/
|   |-- METHODOLOGY.md           Step-by-step research methodology
|   `-- ROADMAP.md               Development roadmap
|-- pyproject.toml               Project metadata and dependencies
|-- LICENSE                      MIT License
|-- .gitignore
`-- README.md                    This file
```

## Rationale and Novelty

The literature gap motivating this study is documented in Stamadianos et al. (2024), who surveyed 703 ACO-VRP publications and noted that "scalability remains underexplored." Papers applying ACO to Solomon instances (Muhammad et al., 2023; Dong et al., 2024) report results at a single problem size without analyzing scaling trends. This study contributes:

1. The first systematic documentation of ACO performance degradation curves as CVRP problem size increases.
2. Identification of the parameter configuration that minimizes degradation under scaling.
3. Statistical evidence on whether ACO provides diminishing returns relative to simpler heuristics as problem size grows.

## Reproducibility

### Prerequisites

Python 3.12 or later and `uv` for dependency management. Install `uv` if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

```bash
git clone <repository-url>
cd pkk-swarm-intelligence
uv sync
uv sync --group dev       # For development tools (pytest, mypy, ruff)
```

### Running the Full Experiment Pipeline

```bash
# Step 1: Download Solomon benchmark instances
uv run python scripts/download_solomon.py

# Step 2: Run the full experiment matrix
uv run python scripts/run_experiments.py

# Step 3: Generate statistical analysis and figures
uv run python scripts/generate_analysis.py
```

Alternatively, import and use programmatically:

```python
from aco_vrp.experiment import ExperimentRunner
from aco_vrp.analysis import StatisticalAnalyzer

runner = ExperimentRunner()
results = runner.run_full_matrix(seeds=30)

analyzer = StatisticalAnalyzer(results)
analyzer.friedman_test()
analyzer.nemenyi_post_hoc()
```

### Expected Output

After a full run, the `results/` directory contains:

| File | Description |
| ---- | ----------- |
| `results/summary.csv` | Aggregated metrics per configuration and problem size |
| `results/raw_runs.csv` | Per-run metrics for all 30 seeds |
| `results/scalability_plot.pdf` | Performance degradation curve with confidence bands |
| `results/parameter_heatmap.pdf` | Alpha vs. Beta interaction at each problem size |
| `results/critical_difference.pdf` | Nemenyi critical difference diagram |
| `results/physics_animation.html` | Interactive pheromone concentration evolution |
| `results/statistical_report.txt` | Full Friedman and Wilcoxon test output |

### Compute Requirements

A full run (4 configurations x 3 problem sizes x 30 seeds = 360 ACO runs plus baseline evaluations) requires approximately 6 hours on a modern CPU. Memory usage is below 2 GB. No GPU is required.

## Development

```bash
# Type checking
uv run mypy src

# Linting
uv run ruff check src tests

# Running tests
uv run pytest -v

# Test coverage
uv run pytest --cov=aco_vrp --cov-report=html
```

## Data Source

The Solomon VRPTW Benchmark instances are obtained from SINTEF:

```
https://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/
```

Instance RC101 (100 customers, 1 depot, time windows) serves as the primary benchmark. The download script (`scripts/download_solomon.py`) fetches and extracts the dataset automatically.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full terms.

## Citation

If you use this code or the experimental results in academic work, please cite:

```bibtex
@misc{aco-vrp-scalability-2026,
  author       = {Pramudya, Aldi and Kirana, Raihan Putra and Sayyidina, Aghnat Hasya and Ahnaf, Walid Nadirul and Zubaedi, Muhammad Fauzan},
  title        = {Ant Colony Optimization for Capacitated Vehicle Routing Problem:
                  A Scalability Analysis on Solomon Benchmark Instances},
  year         = {2026},
  howpublished = {\\url{https://github.com/raihanpka/aco-vrp-scalability}},
  note         = {Computational Intelligence & Optimization Course Project}
}
```

## References

1. Derrac, J., Garcia, S., Molina, D., and Herrera, F. (2011). A practical tutorial on the use of nonparametric statistical tests as a methodology for comparing evolutionary and swarm intelligence algorithms. *Swarm and Evolutionary Computation*, 1(1), 3-18.

2. Solomon, M. M. (1987). Algorithms for the vehicle routing and scheduling problems with time window constraints. *Operations Research*, 35(2), 254-265.

3. Stamadianos, T. et al. (2024). Swarm intelligence and nature inspired algorithms for solving vehicle routing problems: A survey. *Operational Research*, 24, 47.

4. Dorigo, M., and Stutzle, T. (2004). *Ant Colony Optimization*. MIT Press.
