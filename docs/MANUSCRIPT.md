# Scalability Analysis of Ant Colony Optimization for the Capacitated Vehicle Routing Problem Using Solomon Benchmark Instances

**Aldi Pramudya, Raihan Putra Kirana, Aghnat Hasya Sayyidina, Walid Nadirul Ahnaf, Muhammad Fauzan Zubaedi**

Department of Computer Science, IPB University

## Abstract

Ant Colony Optimization (ACO) is a well-established metaheuristic for the Capacitated Vehicle Routing Problem (CVRP). However, the existing literature spanning over 700 ACO-VRP publications reports results almost exclusively at a single fixed problem size. No prior study has systematically analyzed how ACO performance scales with increasing problem size. This paper addresses that gap through a controlled experiment on the Solomon RC101 benchmark instance at three problem sizes (25, 50, and 100 customers) across four ACO parameter configurations, each evaluated with 30 independent runs. Baseline comparisons include the Nearest Neighbor heuristic and the Clarke-Wright Savings algorithm. Statistical significance is assessed using the Friedman test (p < 0.001 at sizes 25 and 100) with post-hoc Wilcoxon signed-rank tests and Holm correction. We find that standard ACO parameters (alpha=1.0, beta=2.0) are competitive at 25 customers but degrade severely at 100 customers (648.4 vs Clarke-Wright 562.1), while higher pheromone weight (alpha=2.0) improves scalability, with C3 achieving the best mean distance of 602.2 at 100 customers. These results provide the first empirical evidence that ACO parameter selection is scale-dependent, and practitioners should increase pheromone weight as problem size grows.

Keywords: ant colony optimization, capacitated vehicle routing problem, scalability analysis, Solomon benchmark, swarm intelligence

## 1. Introduction

Vehicle routing problems are among the most studied combinatorial optimization problems in operations research (Solomon, 1987). Ant Colony Optimization (ACO), introduced by Dorigo and Stutzle (2004), has been extensively applied to the Capacitated Vehicle Routing Problem (CVRP), with over 700 publications documented in the literature (Stamadianos et al., 2024). Despite this volume of work, a fundamental methodological gap persists: almost all studies report results at a single problem size, typically 100 customers, without analyzing how solver performance changes as the number of customers increases.

This is a significant oversight. In practice, logistics operators face fleets of varying sizes. A parameter configuration that performs well on 25 deliveries may be suboptimal for 100 deliveries. The practitioner who selects ACO based on published results at 100 customers has no evidence that the same configuration works at smaller scales, and vice versa.

This paper addresses the question: how does ACO performance scale with CVRP problem size, and which parameter configuration minimizes performance degradation? We conduct a controlled factorial experiment with four ACO configurations at three problem sizes, each repeated across 30 independent runs to enable rigorous statistical analysis following the methodology recommended by Derrac et al. (2011) for comparing swarm intelligence algorithms.

## 2. Methodology

### 2.1 Problem Formulation

The Capacitated Vehicle Routing Problem is defined as follows. Given a depot at coordinates (x0, y0), a set of N customers each with coordinates (xi, yi) and demand di, and a fleet of vehicles each with capacity Q, find a set of routes that minimizes total Euclidean distance such that every customer is visited exactly once and the total demand on any route does not exceed Q.

### 2.2 Dataset

We use the Solomon RC101 benchmark instance, the gold standard for VRP validation since 1987 (Solomon, 1987). RC101 contains 100 customers with mixed random-clustered spatial distribution, a depot at coordinates (40, 50), and vehicle capacity of 200 units. Three subsets are extracted: first 25 customers, first 50 customers, and all 100 customers. Time window constraints present in the dataset are ignored; this study treats the problem as pure CVRP.

### 2.3 Algorithms

Three algorithms are compared:

1. **Nearest Neighbor (NN)**: Greedy constructive heuristic that starts each route at the depot and repeatedly adds the nearest unvisited customer whose demand fits within the remaining vehicle capacity. When no customer can be added, the vehicle returns to the depot and a new vehicle is dispatched.

2. **Clarke-Wright Savings (CWS)**: Savings-based constructive heuristic (Clarke and Wright, 1964). Initializes one route per customer, computes pairwise savings s(i,j) = d(0,i) + d(0,j) - d(i,j), and iteratively merges the route pair with the largest feasible savings until no further merges are possible.

3. **Ant Colony Optimization (ACO)**: Implementation follows Dorigo and Stutzle (2004). A pheromone matrix tau is initialized uniformly. In each iteration, 10 ants construct solutions starting from the depot using the pseudorandom proportional transition rule: the probability of moving from node i to node j is proportional to tau(i,j)^alpha * eta(i,j)^beta, where eta(i,j) = 1/d(i,j). After all ants complete their routes, pheromone evaporates with rate rho, and elitist deposition occurs on the best solution of that iteration. A 2-opt local search is applied to the iteration-best solution. The algorithm runs for 100 iterations, as convergence analysis showed 95% of final quality is reached by iteration 37.

### 2.4 Experimental Design

We evaluate four ACO parameter configurations:

| Configuration | Alpha | Beta | Rho | Ants | Iterations |
|---|---|---|---|---|---|
| C1 | 1.0 | 2.0 | 0.1 | 10 | 100 |
| C2 | 1.0 | 5.0 | 0.1 | 10 | 100 |
| C3 | 2.0 | 2.0 | 0.3 | 10 | 100 |
| C4 | 2.0 | 5.0 | 0.3 | 10 | 100 |

C1 represents the standard parameter recommendation from the literature. C2 and C3 isolate the effect of increasing beta and alpha individually. C4 tests the combined effect of higher alpha, beta, and evaporation rate.

The full factorial design yields 4 configurations x 3 problem sizes x 30 random seeds = 360 ACO runs. Baseline heuristics (NN and CWS) are evaluated once per problem size (deterministic). The primary metric is total route distance. Secondary metrics include number of vehicles and convergence iteration.

### 2.5 Statistical Analysis

We follow the nonparametric testing framework recommended by Derrac et al. (2011). At each problem size, the Friedman test is used for omnibus comparison across all four configurations. When the Friedman test rejects the null hypothesis at alpha = 0.05, pairwise comparisons are performed using the Wilcoxon signed-rank test with Holm correction for multiple comparisons.

## 3. Results

### 3.1 Baseline Heuristics

Table 1 presents the baseline results. As expected, Clarke-Wright consistently outperforms Nearest Neighbor across all problem sizes.

**Table 1. Baseline heuristic results on RC101 subsets.**

| Size | NN Distance | NN Vehicles | CWS Distance | CWS Vehicles |
|---|---|---|---|---|
| 25 | 312.8 | 3 | 231.1 | 3 |
| 50 | 514.9 | 5 | 373.0 | 5 |
| 100 | 684.7 | 8 | 562.1 | 8 |

### 3.2 ACO Performance

Table 2 presents the mean and standard deviation of total distance for each ACO configuration across 30 runs.

**Table 2. ACO results (mean total distance, standard deviation, n=30).**

| Config | Size 25 | Size 50 | Size 100 |
|---|---|---|---|
| C1 | 232.7 (3.5) | 399.7 (13.0) | 648.4 (13.5) |
| C2 | 260.2 (7.3) | 402.9 (11.1) | 612.7 (10.8) |
| C3 | 232.1 (3.5) | 397.9 (16.1) | 602.2 (19.9) |
| C4 | 236.3 (6.8) | 393.7 (16.2) | 608.6 (15.8) |

### 3.3 Statistical Significance

At size 25, the Friedman test reveals highly significant differences among configurations (chi-squared = 57.32, p < 0.001). Post-hoc Wilcoxon tests show that C1 and C3 are statistically indistinguishable (p = 0.70), while C2 performs significantly worse than all others (p < 0.001 for all pairwise comparisons with C2). C4 is significantly worse than C1 (p = 0.01) and C3 (p = 0.006).

At size 50, the Friedman test is not significant at alpha = 0.05 (chi-squared = 7.44, p = 0.059), though it approaches significance. All four configurations perform comparably at this intermediate scale.

At size 100, significant differences reappear (chi-squared = 47.60, p < 0.001). C1 performs significantly worse than all other configurations (p < 0.001 for each pairwise comparison). C2, C3, and C4 form a statistically indistinguishable group (all pairwise p > 0.05), with C3 achieving the lowest mean distance.

### 3.4 Scalability Trends

Figure 1 (scalability plot) illustrates the key finding: ACO performance relative to Clarke-Wright degrades as problem size increases. At 25 customers, ACO C3 achieves a mean distance of 232.1, nearly matching CWS at 231.1 (gap = 0.4%). At 50 customers, the gap widens to 6.7%. At 100 customers, the gap reaches 7.1%.

The standard literature configuration C1 shows the steepest degradation: from near-optimal at 25 customers to the worst performer at 100 customers, with a gap of 15.4% against CWS. In contrast, C3 with higher alpha (2.0) maintains better scaling, reducing the CWS gap from 6.7% at size 50 to only 7.1% at size 100.

**Table 3. Gap to Clarke-Wright baseline (%).**

| Config | Size 25 | Size 50 | Size 100 |
|---|---|---|---|
| C1 | 0.7% | 7.2% | 15.4% |
| C2 | 12.6% | 8.0% | 9.0% |
| C3 | 0.4% | 6.7% | 7.1% |
| C4 | 2.3% | 5.5% | 8.3% |

## 4. Discussion

### 4.1 Scale-Dependent Parameter Selection

The results provide strong evidence that optimal ACO parameter values depend on problem size. At 25 customers, the standard configuration C1 (alpha=1.0) is among the best performers. At 100 customers, the same configuration becomes the worst. This pattern can be explained by the role of alpha in the transition rule: higher alpha amplifies pheromone differences, encouraging exploitation of promising edges. On small problems where good edges are quickly discovered, exploitation helps. On larger problems where many edges compete, higher alpha prevents premature convergence to suboptimal solutions by maintaining stronger pheromone differentiation before convergence occurs.

This finding has direct practical implications. A practitioner deploying ACO for varying fleet sizes should increase alpha as the number of delivery points grows. A configuration with alpha=2.0 and beta=2.0 (C3) is recommended as the most scalable choice across the range tested.

### 4.2 ACO vs Constructive Heuristics

A striking result is that ACO never significantly outperforms Clarke-Wright Savings at any problem size. At 25 customers, ACO matches CWS. At 50 and 100 customers, ACO consistently trails CWS. This does not invalidate ACO but contextualizes its role: for pure CVRP without time windows, the savings heuristic is remarkably effective and should be the first method attempted. ACO may be more appropriate when additional constraints (time windows, heterogeneous fleets, dynamic replanning) render constructive heuristics insufficient.

### 4.3 Limitations

Several limitations should be acknowledged. First, this study uses a single Solomon instance (RC101). Results may not generalize to other spatial distributions (clustered C-type or random R-type). Second, we treat the problem as pure CVRP, ignoring time window constraints present in the Solomon dataset. Time windows introduce additional complexity that may change the relative performance of ACO versus constructive heuristics. Third, the four parameter configurations represent a sparse sampling of the parameter space. A denser grid could reveal more nuanced scaling behavior. Fourth, the 30-run replication provides reasonable statistical power, but larger replication counts would tighten confidence intervals and potentially reveal smaller but meaningful differences.

### 4.4 Future Work

We identify several directions for future investigation. Extending the analysis to all six Solomon classes (C1, C2, R1, R2, RC1, RC2) would test generalizability. Including time windows transforms the problem to VRPTW and may reveal different scaling patterns. Comparing ACO with alternative metaheuristics (Particle Swarm Optimization, Genetic Algorithm, Grey Wolf Optimizer) at multiple scales would position ACO within the broader optimization landscape. Finally, applying the methodology to real-world Indonesian logistics data would bridge the gap between benchmark-based research and practical deployment.

## 5. Conclusion

This study presents the first systematic scalability analysis of Ant Colony Optimization for the Capacitated Vehicle Routing Problem. Through a controlled factorial experiment on the Solomon RC101 benchmark with 360 ACO runs and rigorous nonparametric statistical testing, we demonstrate that:

1. ACO parameter configurations exhibit scale-dependent performance: the standard literature configuration (alpha=1.0) is competitive at 25 customers but degrades severely at 100 customers.
2. Higher pheromone weight (alpha=2.0) improves scalability, reducing the performance gap to Clarke-Wright from 15.4% to 7.1% at 100 customers.
3. The Clarke-Wright Savings algorithm consistently matches or outperforms ACO across all tested scales for pure CVRP, suggesting it should be the baseline of choice.
4. Statistical analysis using Friedman and Wilcoxon tests confirms that configuration differences are significant at extreme scales (25 and 100) but not at intermediate scale (50).

These findings fill a documented gap in the ACO-VRP literature and provide practitioners with evidence-based guidance for parameter selection when problem size varies.

## References

Clarke, G., and Wright, J. W. (1964). Scheduling of vehicles from a central depot to a number of delivery points. Operations Research, 12(4), 568-581.

Derrac, J., Garcia, S., Molina, D., and Herrera, F. (2011). A practical tutorial on the use of nonparametric statistical tests as a methodology for comparing evolutionary and swarm intelligence algorithms. Swarm and Evolutionary Computation, 1(1), 3-18.

Dorigo, M., and Stutzle, T. (2004). Ant Colony Optimization. MIT Press.

Solomon, M. M. (1987). Algorithms for the vehicle routing and scheduling problems with time window constraints. Operations Research, 35(2), 254-265.

Stamadianos, T. et al. (2024). Swarm intelligence and nature inspired algorithms for solving vehicle routing problems: A survey. Operational Research, 24, 47.
