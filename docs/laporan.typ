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
  An IEEE abstract should be between 150 and 250 words long, formatted as a single paragraph. It must not contain math equations, citations, or footnotes. #lorem(150)
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
  index-terms: ("Scientific writing", "Typesetting", "Document creation", "Syntax"),
  bibliography: bibliography("refs.bib"),
  figure-supplement: [Fig.],
)

= Introduction
The Vehicle Routing Problem (VRP) is one of the most extensively studied combinatorial optimization problems in operations research due to its direct applications in logistics, transportation, and supply chain management. Since the introduction of the Solomon benchmark instances, standardized datasets have enabled consistent evaluation and comparison of routing algorithms across the research community. The Capacitated Vehicle Routing Problem (CVRP), a fundamental variant of VRP, seeks to determine a set of minimum-cost routes while satisfying vehicle capacity constraints #cite(<carwalo2017vehicleroutingproblem>).

Among the numerous solution approaches proposed for CVRP, Ant Colony Optimization (ACO) has emerged as one of the most widely adopted metaheuristics. Inspired by the pheromone-based foraging behavior of real ant colonies, ACO has demonstrated strong performance across a wide range of routing problems. A recent survey identified more than 700 publications related to swarm intelligence and nature-inspired approaches for vehicle routing, highlighting the sustained interest in ACO-based methods #cite(<stamadianos2024survey>).

Despite this extensive body of work, an important methodological gap remains. Most studies evaluate ACO performance on a fixed benchmark size and focus primarily on improving solution quality through new pheromone update mechanisms, hybridization strategies, or parameter tuning. Comparatively little attention has been devoted to understanding how ACO performance evolves as problem size increases. Consequently, the scalability characteristics of ACO such as solution quality degradation, convergence behavior, and robustness under larger customer sets remain insufficiently understood.

This limitation has practical implications. Logistics operators frequently face routing problems of varying scales, ranging from small local delivery networks to large distribution systems. A parameter configuration that performs well on a small instance may not remain effective as the number of customers increases. Without a systematic scalability analysis, practitioners have limited guidance regarding which ACO configurations can maintain performance across different problem sizes.

Therefore, this study investigates the following research question: _How does the performance of Ant Colony Optimization scale as the size of a CVRP instance increases, and which parameter configuration exhibits the best scalability characteristics?_ To answer this question, we conduct a controlled factorial experiment using four ACO parameter configurations on three subsets of the Solomon RC101 benchmark consisting of 25, 50, and 100 customers. Each experimental condition is executed across thirty independent runs to evaluate solution quality, convergence speed, and reliability. Statistical significance is assessed using the Friedman test and post-hoc Wilcoxon signed-rank tests following the recommendations of #cite(<derrac2011guide>). The findings provide empirical insights into the scalability behavior of ACO and identify parameter settings that remain effective as problem complexity increases.

= Methods <sec:methods>
The experimental pipeline consists of seven stages, from data preparation 
through statistical analysis to final output, as illustrated in @fig:pipeline.

#figure(
  image("figures/pipeline.png", width: 70%),
  caption: [Overview of the experimental pipeline from data input to output.],
  placement: top,
) <fig:pipeline>

== Problem Formulation
This study addresses the Capacitated Vehicle Routing Problem (CVRP), defined formally as follows. Given a depot at coordinates $(x_0, y_0)$ and a set of $N$ customers, each with coordinates $(x_i, y_i)$ and demand $d_i$, a fleet of homogeneous vehicles each with capacity $Q$ must serve all customers. The objective is to find a set of routes each beginning and ending at the depot that minimizes total Euclidean travel distance while ensuring that: (1) every customer is visited exactly once, and (2) the cumulative demand on any single route does not exceed $Q$. Time window constraints present in the Solomon dataset are deliberately excluded so that the experimental results can be attributed solely to capacity-driven routing difficulty.

== Dataset
All experiments use the Solomon RC101 benchmark instance #cite(<solomon1987AlgorithmsFT>), a widely adopted standard in vehicle routing research. RC101 contains 100 customers with a mixed random-clustered spatial distribution, a depot situated at coordinates $(40, 50)$, and a vehicle capacity of 200 units. To study the effect of problem size, three subsets are extracted by retaining the first 25, 50, and 100 customers from the ordered instance, yielding problem instances of increasing scale while keeping the spatial structure consistent. This subset strategy controls for distributional variation and isolates problem size as the independent variable.

== Algorithms
Three routing algorithms are evaluated. Two classical constructive heuristics serve as deterministic baselines, and an ACO metaheuristic constitutes the primary subject of study:
1. _Nearest Neighbor_ (NN). Starting from the depot, the algorithm greedily appends the nearest unvisited customer whose demand fits within the remaining vehicle capacity. When no feasible customer remains, the current vehicle returns to the depot and a new vehicle is dispatched. This process repeats until all customers are served.
2. _Clarke-Wright Savings_ (CWS). The algorithm initializes one route per customer and computes a savings value $s(i,j) = d(0,i) + d(0,j) - d(i,j)$ for each customer pair #cite(<clarke1964savings>), reflecting the distance saved by combining two routes into one. Pairs are sorted in descending order of savings, and routes are merged iteratively, subject to capacity feasibility, until no further merges are possible.
3. _Ant Colony Optimization_ (ACO). The implementation follows the canonical ACO framework of #cite(<dorigo2004aco>). A pheromone matrix $tau$ of size $(N+1) times (N+1)$ is initialized uniformly. At each iteration, a colony of $m$ ants constructs solutions independently. Each ant starts at the depot and selects the next customer $j$ from the set of unvisited, capacity-feasible customers according to the proportional transition rule:

$
p(i, j) = frac(
  tau_(i j)^alpha dot eta_(i j)^beta,
  sum_(k in cal(F)) tau_(i k)^alpha dot eta_(i k)^beta
)
$

where $eta_(i j) = 1 slash d(i,j)$ is the heuristic visibility, $cal(F)$ is the set of feasible candidate nodes, and $alpha$ and $beta$ are parameters that control the relative influence of pheromone and heuristic information, respectively. When no feasible customer can be added, the ant returns to the depot and begins a new route. After all ants complete their solutions, pheromone evaporates globally:

$
tau_(i j) <- (1 - rho) dot tau_(i j)
$

and elitist deposition is applied on the edges of the iteration-best solution:

$
tau_(i j) <- tau_(i j) + frac(1, L_"best")
$

where $L_"best"$ is the total distance of the best solution found in the current iteration and $rho in (0, 1]$ is the evaporation rate. A 2-opt local search is applied to the iteration-best solution prior to pheromone update to improve route quality within each iteration.

== Experimental Design

=== Parameter Configurations

Four ACO parameter configurations are evaluated, as shown in @tbl-configs. Configuration C1 adopts the standard parameter values commonly recommended in the ACO literature #cite(<dorigo2004aco>) and serves as the reference baseline. Configuration C2 isolates the effect of increasing heuristic weight $beta$. Configuration C3 isolates the effect of increasing pheromone weight $alpha$ alongside a higher evaporation rate $rho$. Configuration C4 combines the elevated values of both $alpha$ and $beta$ with the higher evaporation rate to test their joint effect. All configurations use 10 ants and run for 100 iterations.

#figure(
  caption: [ACO parameter configurations evaluated in this study.],
  placement: top,
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


=== Experimental Matrix

The full factorial design crosses 4 configurations with 3 problem sizes and 30 independent random seeds, yielding $4 times 3 times 30 = 360$ ACO runs in total. Each run is initialized with a distinct integer seed in the range $[0, 29]$ to account for the stochastic nature of ant-based solution construction while ensuring full reproducibility. The two baseline heuristics (NN and CWS) are deterministic and are therefore evaluated once per problem size, producing 6 additional reference data points.

For each ACO run, the following metrics are recorded:
- _Total route distance_: the primary performance metric, defined as the sum of Euclidean distances across all routes including depot-to-first and last-to-depot legs.
- _Vehicle count_: the number of routes used in the final solution.
- _Convergence iteration_: the first iteration at which the best-found distance falls within 5% of the final best distance, used as a proxy for convergence speed.
- _Wall-clock time_: elapsed time in seconds for the complete ACO run.
- _Feasibility_: whether the solution satisfies all capacity constraints and visits every customer exactly once.

=== Statistical Analysis

Statistical comparisons follow the nonparametric testing framework recommended by #cite(<derrac2011guide>) for evaluating swarm intelligence algorithms. At each problem size, the _Friedman test_ is applied as an omnibus test across all four ACO configurations, with the null hypothesis that all configurations are drawn from the same performance distribution. When the Friedman test rejects the null at $alpha = 0.05$, pairwise comparisons are carried out using the _Wilcoxon signed-rank test_. The _Holm step-down correction_ is applied to control the family-wise error rate under multiple comparisons. All tests operate on the 30-run sample of total distances per configuration per problem size.

= Result <sec:result>

== Baseline Heuristics
@tbl-baseline presents the deterministic results of the Nearest Neighbor (NN) and Clarke-Wright Savings (CWS) heuristics across the three problem sizes. CWS consistently outperforms NN, reducing total distance by 26.1% at 25 customers, 27.6% at 50 customers, and 17.9% at 100 customers. The CWS solution uses the same number of vehicles as NN at every problem size, indicating that the savings-based merging does not inflate the fleet requirement despite producing shorter routes.

#figure(
  caption: [Baseline heuristic results on RC101 subsets.],
  placement: top,
  table(
    columns: (5em, 8em, 6em, 8em, 6em),
    align: (left, right, right, right, right),
    inset: (x: 8pt, y: 4pt),
    stroke: (x, y) => if y <= 1 { (top: 0.5pt) },
    fill: (x, y) => if y > 0 and calc.rem(y, 2) == 0 { rgb("#efefef") },

    table.header[Size][NN Dist.][NN Veh.][CWS Dist.][CWS Veh.],
    [25], [312.85], [3], [231.07], [3],
    [50], [514.95], [5], [373.02], [5],
    [100], [684.67], [8], [562.11], [8],
  )
) <tbl-baseline>

== ACO Performance
#figure(
  caption: [ACO results by configuration and problem size. Mean total distance with standard deviation in parentheses ($n = 3$). All solutions are feasible and use the optimal number of vehicles (3 at size 25, 5 at size 50, 8 at size 100).],
  placement: top,
  table(
    columns: (5em, 10em, 10em, 10em),
    align: (left, center, center, center),
    inset: (x: 8pt, y: 4pt),
    stroke: (x, y) => if y <= 1 { (top: 0.5pt) },
    fill: (x, y) => if y > 0 and calc.rem(y, 2) == 0 { rgb("#efefef") },

    table.header[Config][Size 25][Size 50][Size 100],
    [C1], [$233.5 space plus.minus 6.1$], [$404.0 space plus.minus 6.1$], [$653.9 space plus.minus 13.6$],
    [C2], [$263.5 space plus.minus 1.4$], [$403.5 space plus.minus 11.8$], [$619.2 space plus.minus 12.8$],
    [C3], [$228.7 space plus.minus 2.0$], [$405.0 space plus.minus 18.2$], [$593.9 space plus.minus 22.7$],
    [C4], [$235.5 space plus.minus 4.4$], [$399.9 space plus.minus 9.5$], [$618.7 space plus.minus 9.8$],
  ),
) <tbl-aco-results>

@tbl-aco-results summarizes the mean total distance and standard deviation for each ACO configuration across $n = 3$ independent runs. All solutions satisfied capacity constraints and visited every customer exactly once. The number of vehicles produced by ACO matched the CWS baseline at every problem size, confirming that all configurations discovered solutions with the minimum feasible fleet count.

At 25 customers, configuration C3 ($alpha = 2.0$, $beta = 2.0$, $rho = 0.3$) achieves the lowest mean distance of 228.71, surpassing the CWS baseline (231.07) by 1.0%. Configuration C2 ($alpha = 1.0$, $beta = 5.0$) performs substantially worse with a mean distance of 263.50, trailing CWS by 14.0%. Configuration C1 ($alpha = 1.0$, $beta = 2.0$, $rho = 0.1$) yields a mean of 233.47, and C4 ($alpha = 2.0$, $beta = 5.0$, $rho = 0.3$) reaches 235.54.

At 50 customers, the performance differences narrow. Configuration C4 achieves the lowest mean distance (399.94), followed closely by C1 (403.98), C2 (403.49), and C3 (404.97). The difference between the best ACO configuration and CWS is 7.2%.

At 100 customers, C3 emerges as the strongest performer with a mean distance of 593.90, representing a 5.7% gap relative to CWS. C1 performs worst at 653.94 (16.3% gap), indicating substantial degradation of the standard parameter configuration at larger problem sizes. C2 (619.23) and C4 (618.73) occupy intermediate positions.

== Statistical Analysis
Statistical comparisons follow the nonparametric testing framework recommended by #cite(<derrac2011guide>). At each problem size, the Friedman test is applied as an test across all four configurations, followed by pairwise Wilcoxon signed-rank tests when the test rejects the null hypothesis at $alpha = 0.05$.

At size 25, the Friedman test yields $chi^2 = 7.00$ with $p = 0.072$, approaching but not reaching statistical significance. The near-significance reflects the consistent rank ordering across seeds, where C3 consistently ranks best and C2 consistently ranks worst. With only $n = 3$ blocks, the minimum attainable p-value for a four-group Friedman test is $p = 0.072$, indicating that the test is inherently underpowered at this sample size.

At size 50, the Friedman test is clearly non-significant ($chi^2 = 2.20$, $p = 0.532$). The four configurations produce overlapping performance distributions, and no configuration dominates across seeds.

At size 100, the Friedman test again approaches significance but still not reaching the statistical significance ($chi^2 = 7.00$, $p = 0.072$), reflecting a consistent rank ordering where C3 ranks best and C1 ranks worst in all three seeds. While statistical significance cannot be claimed at the $alpha = 0.05$ threshold, the directional trend is unambiguous: configurations with higher pheromone weight ($alpha = 2.0$) consistently outperform the standard configuration ($alpha = 1.0$) at the largest problem size.

== Scalability Trends

== Convergence Behavior

=== Wall-Clock Time

= Discussion

= Conclusion

/*

$ a + b = gamma $ <eq:gamma>

#lorem(80)

#figure(
  placement: none,
  circle(radius: 15pt),
  caption: [A circle representing the Sun.]
) <fig:sun>

In @fig:sun you can see a common representation of the Sun, which is a star that is located at the center of the solar system.

#lorem(120)

#figure(
  caption: [The Planets of the Solar System and Their Average Distance from the Sun],
  placement: top,
  table(
    // Table styling is not mandated by the IEEE. Feel free to adjust these
    // settings and potentially move them into a set rule.
    columns: (6em, auto),
    align: (left, right),
    inset: (x: 8pt, y: 4pt),
    stroke: (x, y) => if y <= 1 { (top: 0.5pt) },
    fill: (x, y) => if y > 0 and calc.rem(y, 2) == 0  { rgb("#efefef") },

    table.header[Planet][Distance (million km)],
    [Mercury], [57.9],
    [Venus], [108.2],
    [Earth], [149.6],
    [Mars], [227.9],
    [Jupiter], [778.6],
    [Saturn], [1,433.5],
    [Uranus], [2,872.5],
    [Neptune], [4,495.1],
  )
) <tab:planets>

In @tab:planets, you see the planets of the solar system and their average distance from the Sun.
The distances were calculated with @eq:gamma that we presented in @sec:methods.

#lorem(240)

#lorem(240)
*/