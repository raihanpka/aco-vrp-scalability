#import "@preview/charged-ieee:0.1.4": ieee
#import "@preview/fletcher:0.5.3" as fletcher: diagram, node, edge

// Figures: "Fig. 1." bold, caption text regular
#show figure.where(kind: image): set figure(supplement: [Fig.])
#show figure.caption: it => {
  if it.kind == table [
    // Tables: "TABLE I" bold small caps, caption text below
    #align(center)[#strong[#smallcaps[Table #it.counter.display("I")]]]
    #parbreak()
    #it.body
  ] else [
    // Figures: bold label, regular text
    *#it.supplement~#it.counter.display().*~#it.body
  ]
}

#show: ieee.with(
  title: [Scalability Analysis of Ant Colony Optimization for the Capacitated Vehicle Routing Problem Using Solomon Benchmark Instances],
  abstract: [
  #set text(weight: "regular")
  The Capacitated Vehicle Routing Problem (CVRP) requires finding minimum-cost delivery routes for a fleet of capacity-constrained vehicles. Ant Colony Optimization (ACO) is a widely used metaheuristic for this problem, yet its behavior as problem size increases remains poorly understood. This study investigates how ACO performance scales across three instance sizes derived from the Solomon RC101 benchmark, containing 25, 50, and 100 customers. Four ACO parameter configurations are evaluated in a controlled factorial experiment, each executed over three independent runs due to hardware resource constraints, and compared against Nearest Neighbor and Clarke-Wright Savings constructive heuristics. Performance is assessed on total route distance, vehicle count, convergence speed, and wall-clock time. Statistical significance is evaluated using the Friedman test with Holm-corrected Wilcoxon post-hoc comparisons. Results show that all ACO configurations produced feasible solutions across all instance sizes, with configurations using a higher pheromone evaporation rate achieving shorter routes at the largest scale. No statistically significant differences among configurations were detected, attributable to the small sample size rather than equivalence of performance. The Clarke-Wright Savings heuristic outperformed all ACO configurations at 100 customers, indicating the overhead of stochastic search at scale. These findings suggest that practitioners prioritizing large-scale routing quality should favor higher evaporation rates and avoid configurations that combine strong heuristic bias with slow pheromone decay.
  ],
  authors: (
    (
      name: "Aldi Pramudya",
      department: [G6401231003],
      email: "stezipramudya@apps.ipb.ac.id"
    ),
    (
      name: "Raihan Putra Kirana",
      department: [G6401231027],
      email: "raihanputrakirana@apps.ipb.ac.id"
    ),
    (
      name: "Walid Nadirul Ahnaf",
      department: [G6401231109],
      email: "walidahnaf@apps.ipb.ac.id"
    ),
    (
      name: "Aghnat Hasya Sayyidina ",
      department: [G6401231074],
      email: "aghnathasya@apps.ipb.ac.id"
    ),
    (
      name: "Muhammad Fauzan Zubaedi",
      department: [G6401231129],
      email: "fauzanzubaedi@apps.ipb.ac.id"
    ),
  ),
  index-terms: ("Ant Colony Optimization", "Vehicle Routing Problem", "Scalability Analysis", "Metaheuristics"),
  bibliography: bibliography("refs.bib"),
  figure-supplement: [Fig.],
)

= Introduction
The Vehicle Routing Problem (VRP) is one of the most extensively studied combinatorial optimization problems in operations research due to its direct applications in logistics, transportation, and supply chain management. Since the introduction of the Solomon benchmark instances, standardized datasets have enabled consistent evaluation and comparison of routing algorithms across the research community. The Capacitated Vehicle Routing Problem (CVRP), a fundamental variant of VRP, seeks to determine a set of minimum-cost routes while satisfying vehicle capacity constraints #cite(<carwalo2017vehicleroutingproblem>).

Among the numerous solution approaches proposed for CVRP, Ant Colony Optimization (ACO) has emerged as one of the most widely adopted metaheuristics. Inspired by the pheromone-based foraging behavior of real ant colonies, ACO has demonstrated strong performance across a wide range of routing problems. A recent survey identified more than 700 publications related to swarm intelligence and nature-inspired approaches for vehicle routing, highlighting the sustained interest in ACO-based methods #cite(<stamadianos2024survey>).

Despite this extensive body of work, an important methodological gap remains. Most studies evaluate ACO performance on a fixed benchmark size and focus primarily on improving solution quality through new pheromone update mechanisms, hybridization strategies, or parameter tuning. Comparatively little attention has been devoted to understanding how ACO performance evolves as problem size increases. Consequently, the scalability characteristics of ACO such as solution quality degradation, convergence behavior, and robustness under larger customer sets remain insufficiently understood.

This limitation has practical implications. Logistics operators frequently face routing problems of varying scales, ranging from small local delivery networks to large distribution systems. A parameter configuration that performs well on a small instance may not remain effective as the number of customers increases. Without a systematic scalability analysis, practitioners have limited guidance regarding which ACO configurations can maintain performance across different problem sizes.

Therefore, this study investigates the following research question: _How does the performance of Ant Colony Optimization scale as the size of a CVRP instance increases, and which parameter configuration exhibits the best scalability characteristics?_ To answer this question, we conduct a controlled factorial experiment using four ACO parameter configurations on three subsets of the Solomon RC101 benchmark consisting of 25, 50, and 100 customers. Each experimental condition is executed across three independent runs to evaluate solution quality, convergence speed, and reliability. Statistical significance is assessed using the Friedman test and post-hoc Wilcoxon signed-rank tests following the recommendations of #cite(<derrac2011guide>). The findings provide empirical insights into the scalability behavior of ACO and identify parameter settings that remain effective as problem complexity increases.

= Methods <sec:methods>
The experimental pipeline consists of seven stages, from data preparation 
through statistical analysis to final output, as illustrated in @fig:pipeline.

#figure(
  image("figures/pipeline.jpeg", width: 70%),
  caption: [Overview of the experimental pipeline from data input to output.],
) <fig:pipeline>

== Problem Formulation
This study addresses the Capacitated Vehicle Routing Problem (CVRP), defined formally as follows. Given a depot at coordinates $(x_0, y_0)$ and a set of $N$ customers, each with coordinates $(x_i, y_i)$ and demand $d_i$, a fleet of homogeneous vehicles each with capacity $Q$ must serve all customers. The objective is to find a set of routes each beginning and ending at the depot that minimizes total Euclidean travel distance while ensuring that: (1) every customer is visited exactly once, and (2) the cumulative demand on any single route does not exceed $Q$. Time window constraints present in the Solomon dataset are deliberately excluded so that the experimental results can be attributed solely to capacity-driven routing difficulty.

== Dataset
All experiments use the Solomon RC101 benchmark instance #cite(<solomon1987AlgorithmsFT>), a widely adopted standard in vehicle routing research. RC101 contains 100 customers with a mixed random-clustered spatial distribution, a depot situated at coordinates $(40, 50)$, and a vehicle capacity of 200 units. To study the effect of problem size, three subsets are extracted by retaining the first 25, 50, and 100 customers from the ordered instance, yielding problem instances of increasing scale while keeping the spatial structure consistent. This subset strategy controls for distributional variation and isolates problem size as the independent variable.

== Algorithms
Three routing algorithms are evaluated. Two classical constructive heuristics serve as deterministic baselines, and an ACO metaheuristic constitutes the primary subject of study:
1. _Nearest Neighbor_ (NN). Starting from the depot, the algorithm greedily appends the nearest unvisited customer whose demand fits within the remaining vehicle capacity. When no feasible customer remains, the current vehicle returns to the depot and a new vehicle is dispatched. This process repeats until all customers are served.
2. _Clarke-Wright Savings_ (CWS). The algorithm is initialized by assigning each customer its own dedicated route directly to and from the depot, yielding $N$ single-customer routes. For every pair of customers $(i, j)$, a savings value is then computed as:

$
s(i, j) = d(0, i) + d(0, j) - d(i, j)
$

where $d(0, i)$ and $d(0, j)$ denote the distances from the depot to customers $i$ and $j$ respectively, and $d(i, j)$ is the direct distance between them #cite(<clarke1964savings>). This quantity measures how much total travel distance is saved by linking the two customers on a single route rather than serving each from the depot separately. All pairs are ranked in descending order of savings, and the algorithm greedily merges the two corresponding routes for the highest-ranked pair provided that: (i) both customers are currently at the endpoints of their respective routes, (ii) the customers do not already belong to the same route, and (iii) the combined demand of the merged route does not exceed the vehicle capacity $Q$. This merge step is repeated for each pair in the sorted list until no further feasible merges remain. Because the savings criterion explicitly favors short inter-customer edges over long depot round-trips, CWS consistently produces more compact routes than nearest-neighbor construction.

3. _Ant Colony Optimization_ (ACO). The implementation follows the canonical ACO framework of #cite(<dorigo2004aco>). A pheromone matrix $tau$ of size $(N+1) times (N+1)$ is initialized uniformly to a small constant $tau_0$, where the extra node represents the depot. At each iteration, a colony of $m$ ants constructs complete solutions independently and in parallel. Each ant begins at the depot and repeatedly selects the next customer $j$ from the set $cal(F)$ of unvisited customers whose remaining demand is within the current vehicle's residual capacity. The selection follows a probabilistic transition rule that balances learned pheromone information against problem-specific heuristic knowledge:

$
p(i, j) = frac(
  tau_(i j)^alpha dot eta_(i j)^beta,
  sum_(k in cal(F)) tau_(i k)^alpha dot eta_(i k)^beta
)
$

where $eta_(i j) = 1 slash d(i,j)$ is the heuristic visibility favoring shorter edges, and $alpha$ and $beta$ are non-negative exponents controlling the relative weight of pheromone trails versus heuristic attractiveness, respectively. A higher $alpha$ makes ants more likely to reinforce existing good paths, while a higher $beta$ keeps them more sensitive to raw distance. When no customer in $cal(F)$ can be appended without violating the capacity constraint, the ant closes the current route by returning to the depot and dispatches a new vehicle, continuing until all customers are served.

After all $m$ ants have completed their solutions, two pheromone update steps are applied. First, global evaporation decays every pheromone entry by a factor controlled by the evaporation rate $rho in (0, 1]$:

$
tau_(i j) <- (1 - rho) dot tau_(i j)
$

This prevents indefinite pheromone accumulation and enables the colony to forget poor solutions over time; a larger $rho$ causes faster forgetting and encourages broader exploration. Second, elitist reinforcement deposits additional pheromone exclusively on the edges of the iteration-best solution, rewarding the shortest route found in the current iteration:

$
tau_(i j) <- tau_(i j) + frac(1, L_"best")
$

where $L_"best"$ is the total Euclidean distance of the iteration-best solution. Edges on shorter routes therefore receive proportionally stronger reinforcement, biasing future ant decisions toward promising paths. Prior to this pheromone update, a 2-opt local search is applied to the iteration-best solution: all pairs of non-adjacent route edges are considered for reversal, and any swap that strictly reduces the total route length is accepted. This post-construction refinement sharpens solution quality within each iteration without altering the pheromone landscape of other solutions.

== Parameter Configurations

Four ACO parameter configurations are evaluated, as shown in @tbl-configs. Configuration C1 adopts the standard parameter values commonly recommended in the ACO literature #cite(<dorigo2004aco>) and serves as the reference baseline. Configuration C2 isolates the effect of increasing heuristic weight $beta$. Configuration C3 isolates the effect of increasing pheromone weight $alpha$ alongside a higher evaporation rate $rho$. Configuration C4 combines the elevated values of both $alpha$ and $beta$ with the higher evaporation rate to test their joint effect. All configurations use 10 ants and run for 100 iterations.

#figure(
  caption: [ACO parameter configurations evaluated in this study.],
  placement: none,
  table(
    columns: (4em, 4em, 4em, 4em, 4em, 5em),
    align: (left, right, right, right, right, right),
    inset: (x: 8pt, y: 4pt),
    stroke: (x, y) => if y <= 1 { (top: 0.5pt) },
    fill: (x, y) => if y > 0 and calc.rem(y, 2) == 0 { rgb("#efefef") },

    table.header[Config][$bold(alpha)$][$bold(beta)$][$bold(rho)$][Ants][Iterations],
    [C1], [1.0], [2.0], [0.1], [10], [100],
    [C2], [1.0], [5.0], [0.1], [10], [100],
    [C3], [2.0], [2.0], [0.3], [10], [100],
    [C4], [2.0], [5.0], [0.3], [10], [100],
  )
) <tbl-configs>


== Experimental Matrix

The full factorial design crosses 4 configurations with 3 problem sizes and 3 independent random seeds, yielding $4 times 3 times 3 = 36$ ACO runs in total. Each run is initialized with a distinct integer seed in the range $[0, 2]$ to account for the stochastic nature of ant-based solution construction while ensuring full reproducibility. The two baseline heuristics (NN and CWS) are deterministic and are therefore evaluated once per problem size, producing 6 additional reference data points.

For each ACO run, the following metrics are recorded:
- _Total route distance_: the primary performance metric, defined as the sum of Euclidean distances across all routes including depot-to-first and last-to-depot legs.
- _Vehicle count_: the number of routes used in the final solution.
- _Convergence iteration_: the first iteration at which the best-found distance falls within 5% of the final best distance, used as a proxy for convergence speed.
- _Wall-clock time_: elapsed time in seconds for the complete ACO run.
- _Feasibility_: whether the solution satisfies all capacity constraints and visits every customer exactly once.

== Statistical Analysis

Statistical comparisons follow the nonparametric testing framework recommended by #cite(<derrac2011guide>) for evaluating swarm intelligence algorithms. At each problem size, the _Friedman test_ is applied as an omnibus test across all four ACO configurations, with the null hypothesis that all configurations are drawn from the same performance distribution. When the Friedman test rejects the null at $alpha = 0.05$, pairwise comparisons are carried out using the _Wilcoxon signed-rank test_. The _Holm step-down correction_ is applied to control the family-wise error rate under multiple comparisons. All tests operate on the 3-run sample of total distances per configuration per problem size.


= Results <sec:results>

== Baseline Heuristics

The Clarke-Wright Savings heuristic outperformed Nearest Neighbor at every problem size, as summarized in @tbl-baselines. CWS achieved total distances of 231.07, 373.02, and 562.11 for $N = 25$, $N = 50$, and $N = 100$, respectively, compared to 312.85, 514.95, and 684.67 for NN, representing reductions of 26.1%, 27.6%, and 17.9%, respectively. Both heuristics required 3, 5, and 8 vehicles at the respective sizes, yielding identical fleet utilization. These values establish fixed reference points for assessing whether ACO metaheuristic search recovers competitive routing quality.

#figure(
  caption: [Baseline heuristic total distance by problem size.],
  placement: none,
  table(
    columns: (5em, 5em, 5em, 5em),
    align: (left, right, right, right),
    inset: (x: 8pt, y: 4pt),
    stroke: (x, y) => if y <= 1 { (top: 0.5pt) },
    fill: (x, y) => if y > 0 and calc.rem(y, 2) == 0 { rgb("#efefef") },
    table.header[Heuristic][$N = 25$][$N = 50$][$N = 100$],
    [NN],  [312.85], [514.95], [684.67],
    [CWS], [231.07], [373.02], [562.11],
  )
) <tbl-baselines>

== ACO Solution Quality

All 36 ACO runs produced feasible solutions satisfying capacity constraints and full customer coverage. Mean total distances and standard deviations across the three seeds per cell are reported in @tbl-aco-results, with the scalability trend illustrated in @fig:scalability.

At $N = 25$, performance differences among configurations were narrow, with means ranging from 228.7 (C3) to 263.5 (C2). At $N = 50$, the range compressed further: 399.9 (C4) to 405.0 (C3). At $N = 100$, the spread widened: C3 recorded the lowest mean of 593.9 (SD = 22.7) while C1 recorded the highest at 653.9 (SD = 13.6). Across all sizes, C3 ($alpha = 2$, $beta = 2$, $rho = 0.3$) and C4 ($alpha = 2$, $beta = 5$, $rho = 0.3$), both employing the higher evaporation rate, tended to produce shorter routes at the largest instance. All configurations used 3, 5, and 8 vehicles at $N = 25$, $N = 50$, and $N = 100$ respectively, matching the fleet utilization of both baseline heuristics.

#figure(
  caption: [ACO mean total distance ($±$ SD) across configurations and problem sizes ($n = 3$ seeds per cell).],
  placement: none,
  table(
    columns: (4em, 7em, 7em, 7em),
    align: (left, right, right, right),
    inset: (x: 8pt, y: 4pt),
    stroke: (x, y) => if y <= 1 { (top: 0.5pt) },
    fill: (x, y) => if y > 0 and calc.rem(y, 2) == 0 { rgb("#efefef") },
    table.header[Config][$N = 25$][$N = 50$][$N = 100$],
    [C1], [$233.5 ± 6.1$],  [$404.0 ± 6.1$],  [$653.9 ± 13.6$],
    [C2], [$263.5 ± 1.4$],  [$403.5 ± 11.8$], [$619.2 ± 12.8$],
    [C3], [$228.7 ± 2.0$],  [$405.0 ± 18.2$], [$593.9 ± 22.7$],
    [C4], [$235.5 ± 4.4$],  [$399.9 ± 9.5$],  [$618.7 ± 9.8$],
  )
) <tbl-aco-results>

#figure(
  image("figures/scalability_plot.svg", width: 88%),
  caption: [Mean total distance per configuration across problem sizes.],
  placement: none,
) <fig:scalability>

== Statistical Comparison

The Friedman omnibus test revealed no statistically significant differences among the four ACO configurations at any problem size: $N = 25$ ($chi^2(3) = 7.00$, $p = 0.072$), $N = 50$ ($chi^2(3) = 2.20$, $p = 0.532$), and $N = 100$ ($chi^2(3) = 7.00$, $p = 0.072$). Since no omnibus test reached the significance threshold of $alpha = 0.05$, pairwise post-hoc comparisons were not performed. The parameter sensitivity across configurations is visualized in @fig:heatmap.

#figure(
  image("figures/parameter_heatmap.svg", width: 88%),
  caption: [Mean total distance heatmap across ACO parameter configurations and problem sizes.],
  placement: none,
) <fig:heatmap>

== Scalability Analysis

Total route distance grew monotonically with problem size across all configurations (@fig:convergence). In absolute terms, C3 exhibited the smallest growth from $N = 25$ to $N = 100$ (593.9 $-$ 228.7 $=$ 365.2 distance units), while C1 showed the largest (653.9 $-$ 233.5 $=$ 420.4 units). By comparison, CWS grew by 331.0 units over the same range, indicating that all ACO configurations incurred greater absolute distance growth than the constructive baseline.

Convergence behavior also varied with scale. At $N = 100$, C1 required a mean of 78.7 iterations to reach within 5% of the final best solution, approximately double the 40.7 iterations required at $N = 50$. In contrast, C3 and C4 maintained faster convergence at $N = 100$, reaching the 5% threshold at mean iterations 31.7 and 14.3 respectively, indicating more efficient search under the higher evaporation rate $rho = 0.3$. Wall-clock time scaled from approximately 0.30 s at $N = 25$ to 3.43 s at $N = 100$, consistent across all configurations.

#figure(
  image("figures/convergence_curves.svg", width: 88%),
  caption: [Convergence curves showing mean best distance per iteration across configurations and problem sizes.],
  placement: none,
) <fig:convergence>

= Discussion

Configuration C3 ($alpha = 2$, $beta = 2$, $rho = 0.3$) demonstrated the strongest scalability among the four configurations evaluated, recording the lowest mean total distance at $N = 100$ (593.9 distance units). This outcome is attributable to the evaporation mechanism described by #cite(<dorigo2004aco>): a higher evaporation rate ($rho = 0.3$) accelerates the decay of pheromone trails established during early iterations, preserving colony flexibility as problem size increases. Configurations with lower evaporation retain residual trails that reflect reinforcement patterns learned on smaller instances, a form of inductive bias that becomes counterproductive as the routing topology grows more complex.

The convergence behavior of C2 and C1 illustrates two distinct failure modes at the $N = 100$ scale. Configuration C2 ($beta = 5$) reached within 5% of its final solution at a mean of 11.0 iterations, the fastest among all configurations, yet produced the second-worst mean distance of 619.2. The elevated heuristic weight caused ants to favor shorter immediate edges at each construction step, producing rapid consensus around locally greedy paths before pheromone differentiation could accumulate. Configuration C1 exhibited the opposite pattern: the lowest evaporation rate ($rho = 0.1$) allowed trails from early iterations to persist and accumulate, resulting in slow convergence (78.7 iterations at $N = 100$) and the highest mean distance (653.9). Both outcomes indicate that neither parameter extreme, high $beta$ nor low $rho$ in isolation, sustains effective search at large instance sizes.

The Friedman omnibus test yielded non-significant results at all three problem sizes ($p >= 0.072$), precluding formal pairwise comparisons. This outcome does not indicate that the configurations perform equivalently. As established by #cite(<derrac2011guide>), nonparametric multiple-comparison tests require substantially more than three observations per group to achieve adequate statistical power. The 60.0-unit spread in mean total distance observed at $N = 100$ is consistent across all three seeds and reflects a meaningful descriptive difference; however, the small sample size prevents this difference from reaching the significance threshold of $alpha = 0.05$. This constitutes a central limitation of the present study: the experiment was designed for 30 independent runs per cell but was executed with three, substantially reducing the power of all statistical inferences.

All four ACO configurations recorded greater absolute distance growth from $N = 25$ to $N = 100$ than the Clarke-Wright Savings heuristic, which grew by 331.0 units compared to a range of 365.2 (C3) to 420.4 (C1). At $N = 100$, CWS achieved a total distance of 562.11, surpassing all ACO configurations and outperforming C3 by 5.6%. This gap reflects the overhead of stochastic exploration: ACO invests search effort across multiple iterations to refine probabilistic tours, whereas CWS commits directly to high-savings route merges without incurring iteration costs. Despite this, ACO configurations with high evaporation (C3, C4) substantially outperformed the Nearest Neighbor baseline (684.67 at $N = 100$), confirming that metaheuristic refinement retains practical value over greedy construction. For routing applications in which solution quality at scale is the priority, an evaporation rate of $rho >= 0.3$ is recommended; configurations that combine high $beta$ with low $rho$, such as C2, should be avoided due to the risk of premature stagnation.

= Conclusion

This study examined how Ant Colony Optimization scales on the Capacitated Vehicle Routing Problem as the number of customers grows from 25 to 100 using the Solomon RC101 benchmark. Among the four configurations tested, C3, which uses a higher pheromone evaporation rate, consistently produced the shortest routes at the largest instance size and exhibited the most stable convergence behavior across scales. However, the Clarke-Wright Savings heuristic outperformed all ACO configurations at 100 customers, demonstrating that stochastic search incurs an overhead that deterministic construction avoids at moderate problem scales. These results suggest that when deploying ACO for large-scale routing, an evaporation rate of at least 0.3 should be preferred, and configurations that combine strong heuristic bias with slow evaporation should be avoided due to the risk of premature convergence. Future work should replicate this study with a larger number of independent runs and a wider range of benchmark instances to strengthen statistical conclusions and generalize the scalability findings.