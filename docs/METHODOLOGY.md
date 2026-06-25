# Research Methodology: ACO-CVRP Scalability Analysis

**Document purpose:** Step-by-step experimental protocol for reproducibility.
Follow the phases below in order. Each phase produces verifiable outputs
before the next phase begins.

## Phase 1: Environment and Data Preparation

### 1.1 Environment Setup

Install Python 3.12 or later and `uv`. Clone the repository and install
dependencies:

```bash
git clone <repository-url>
cd pkk-swarm-intelligence
uv sync
uv sync --group dev
```

Verify the installation:

```bash
uv run python -c "import aco_vrp; print('Package loaded successfully.')"
uv run pytest -v
```

Expected outcome: All placeholder tests pass (or are skipped). No import errors.

### 1.2 Dataset Acquisition

Download the Solomon VRPTW Benchmark. Write the download script at
`scripts/download_solomon.py` to:

1. Fetch the RC101 instance from SINTEF.
2. Save the raw text file to `data/solomon/RC101.txt`.
3. Verify file integrity (check line count and format).

Expected output: `data/solomon/RC101.txt` with 100 customer records
plus depot and header lines.

### 1.3 Instance Validation

Load RC101 and verify:

- All 100 customers have valid coordinates (x, y), demand > 0, time windows.
- The depot is at the coordinates specified in the file.
- Vehicle capacity matches the header value.
- Euclidean distance matrix is symmetric and correctly computed.

Expected output: Console log confirming instance dimensions and no
parsing errors.

## Phase 2: Baseline Heuristics

### 2.1 Nearest Neighbor Implementation

Implement the Nearest Neighbor constructive heuristic in
`src/aco_vrp/heuristics.py`. The algorithm:

1. Starts at the depot.
2. At each step, finds the nearest unvisited customer that fits within
   remaining vehicle capacity.
3. If no customer can be added, returns to depot and starts a new route.
4. Repeats until all customers are visited.

Verification:

- Run on the full RC101 instance (100 customers).
- Assert total distance > 0 and all customers are visited.
- Assert capacity constraint is not violated.
- Compare against known literature values for RC101.

### 2.2 Clarke-Wright Savings Implementation

Implement the Clarke-Wright Savings algorithm in the same file. The algorithm:

1. Computes savings(i, j) = d(depot, i) + d(depot, j) - d(i, j) for each pair.
2. Initializes one route per customer (depot -> customer -> depot).
3. Sorts savings in descending order.
4. Iteratively merges the pair with the highest feasible savings.

Verification:

- Run on RC101 (100 customers).
- Assert total distance is less than or equal to Nearest Neighbor result
  (Clarke-Wright typically produces better solutions).
- Assert capacity constraints are satisfied.

### 2.3 Baseline Metrics Collection

Run both heuristics on subsets of 25, 50, and 100 customers. Record:

- Total distance
- Number of vehicles used
- Feasibility rate

Save results to `results/baseline_summary.csv`.

## Phase 3: ACO Core Implementation

### 3.1 Pheromone Matrix and Solution Construction

Implement in `src/aco_vrp/core.py`:

1. Initialize pheromone matrix tau[i][j] = initial_pheromone for all edges.
2. Construct solutions: each ant starts at depot and selects the next
   customer j from unvisited set using transition probability:
   P(i, j) = (tau[i][j]^alpha * eta[i][j]^beta) / sum(...)
   where eta[i][j] = 1 / distance(i, j).
3. Track vehicle capacity: skip customers whose demand exceeds remaining
   capacity.
4. Return to depot when no feasible customer remains.

### 3.2 Pheromone Update

Implement evaporation and deposition:

1. Evaporation: tau[i][j] = (1 - rho) * tau[i][j] for all edges.
2. Deposition: add delta_tau = Q / L_best for edges on the best solution
   of the iteration, where L_best is total distance of that solution.
3. Optionally apply elitist deposition (deposit additional pheromone on
   the global best solution).

### 3.3 Optional Local Search

Implement 2-opt improvement: for each route, try reversing a subsequence
and accept if it reduces total distance. Apply after each ant completes
its solution.

### 3.4 Convergence and Termination

- Track the global best solution across iterations.
- Stop after max_iterations or when no improvement observed for
  stagnation_limit iterations (optional early stopping).

### 3.5 Unit Testing for ACO Core

- Test on a small handcrafted instance (3 customers, known optimal).
- Assert ACO finds the optimal solution within 50 iterations.
- Assert pheromone values are non-negative and properly bounded.
- Assert no constraint violations in generated solutions.

## Phase 4: Experiment Design

### 4.1 Parameter Configurations

Define four ACO configurations to evaluate:

| Config | Alpha | Beta | Rho | Ants | Iterations |
| ------ | ----- | ---- | --- | ---- | ---------- |
| C1     | 1.0   | 2.0  | 0.1 | 10   | 200        |
| C2     | 1.0   | 5.0  | 0.1 | 10   | 200        |
| C3     | 2.0   | 2.0  | 0.3 | 10   | 200        |
| C4     | 2.0   | 5.0  | 0.3 | 10   | 200        |

Justification: C1 is the standard recommendation (Dorigo and Stutzle,
2004). C2 and C3 explore the impact of increasing beta and alpha
individually. C4 tests the combined effect of higher alpha, beta, and rho.

### 4.2 Problem Sizes

Extract three subsets from RC101:

- Size 25: First 25 customers from the instance.
- Size 50: First 50 customers.
- Size 100: All 100 customers (full instance).

### 4.3 Random Seeds

Execute 30 independent runs per cell (4 configs x 3 sizes = 12 cells).
Total: 360 ACO runs. Each run uses a different random seed (0-29) to
control the stochastic nature of the algorithm (initial ant placement,
tie-breaking in transition rule).

### 4.4 Experiment Runner

Implement `ExperimentRunner` in `src/aco_vrp/experiment.py`:

1. Accept configuration list and size list.
2. For each (config, size) cell, run ACO for each seed.
3. Collect metrics per run: total distance, vehicle count, convergence
   iteration (when 95% of best fitness reached), wall-clock time,
   feasibility.
4. Save raw results to `results/raw_runs.csv`.

Expected: `results/raw_runs.csv` with columns:
config_id, size, seed, total_distance, vehicle_count, convergence_iter,
wall_time_sec, feasible.

### 4.5 Parallel Execution

Optimize the experiment runner to execute independent runs in parallel
using Python's `multiprocessing` or `concurrent.futures`. Target: full
experiment completes within 2 hours on a 4-core machine (vs. 6 hours
sequential).

## Phase 5: Statistical Analysis

### 5.1 Descriptive Statistics

For each (config, size) cell, compute:

- Mean and median of total distance
- Standard deviation and standard error
- Minimum and maximum
- Interquartile range (IQR)

Output: `results/summary.csv`.

### 5.2 Hypothesis Testing

Follow the methodology of Derrac et al. (2011):

1. **Friedman test** (omnibus): Are there significant differences among
   the four configurations within each problem size?
   Null hypothesis: all configurations have equal performance.
   Test separately for each problem size and each metric.

2. **Wilcoxon signed-rank test** (pairwise): Which specific pairs of
   configurations differ significantly?
   Apply Holm correction for multiple comparisons.

3. **Significance level:** alpha = 0.05 for all tests.

### 5.3 Scalability Analysis

The primary research question: how does the performance gap between ACO
and baseline heuristics change as problem size increases?

For each configuration, compute:

- Gap to best-known solution (%) at each problem size.
- Regression of total distance against problem size (slope indicates
  degradation rate).
- Statistical test: does the gap at size 100 differ significantly from
  the gap at size 25?

### 5.4 Parameter Sensitivity

Analyze which parameter (alpha, beta, rho) has the strongest effect on
performance at each problem size:

- Compute main effects from the 2x2x2 factorial design.
- Identify interactions (e.g., alpha x beta interaction at size 100).

Output: `results/statistical_report.txt` with full test output.

## Phase 6: Visualization

### 6.1 Scalability Plot

`results/scalability_plot.pdf`:

- X-axis: problem size (25, 50, 100)
- Y-axis: mean total distance
- One line per ACO configuration, with 95% confidence band
- Horizontal reference lines: Nearest Neighbor and Savings baselines

### 6.2 Parameter Interaction Heatmap

`results/parameter_heatmap.pdf`:

- 2D heatmap: alpha on X-axis, beta on Y-axis
- Color intensity: mean total distance at size 100
- Three panels: one for each problem size

### 6.3 Convergence Curves

Plot mean convergence curves (best distance vs. iteration) for each
configuration at each problem size, with confidence bands.

### 6.4 Critical Difference Diagram

`results/critical_difference.pdf`:

- Nemenyi post-hoc CD diagram for size 100.
- Horizontal axis: mean rank of each configuration.
- Critical difference bar indicating which configurations are
  statistically indistinguishable.

### 6.5 Pheromone Animation

`results/physics_animation.html` (interactive Plotly):

- Animated heatmap of pheromone concentration on the customer graph.
- Each frame represents one iteration.
- Color intensity represents pheromone level (fading = evaporation,
  intensifying = deposition).
- Route of the best ant overlaid on the heatmap.

## Phase 7: Interpretation and Reporting

### 7.1 Key Findings to Document

1. At what problem size does ACO begin to show statistically significant
   improvement over Nearest Neighbor?
2. Which parameter configuration scales best (minimum degradation slope)?
3. What is the interaction between alpha and beta at different problem
   sizes? Does the optimal alpha/beta ratio change?
4. What is the reliability of ACO (feasibility rate) as problem size grows?
5. What are the practical implications for practitioners choosing between
   ACO and simpler heuristics based on problem size?

### 7.2 Limitations

Acknowledge:

- Single instance (RC101): results may not generalize to other Solomon
  classes (C, R, RC with different spatial distributions).
- Fixed parameter configurations: a more extensive grid could reveal
  finer-grained scaling behavior.
- No time window analysis: this study treats the problem as CVRP,
  ignoring time window constraints present in the Solomon format.
- Compute budget: 30 runs per cell provides reasonable statistical
  power but larger replication counts would tighten confidence intervals.

### 7.3 Future Work

- Extend to all 6 Solomon classes (C1, C2, R1, R2, RC1, RC2).
- Include time windows in the analysis (VRPTW scalability).
- Compare with alternative metaheuristics (PSO, GA, GWO) at scale.
- Apply to real-world logistics data from Indonesian contexts.
