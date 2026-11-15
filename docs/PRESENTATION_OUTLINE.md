# Presentation Outline & Live Demo Script: Evolutionary Optimization for CVRP

**Project Title**: Evolutionary Computing for the Capacitated Vehicle Routing Problem (CVRP)  
**Target Duration**: 10–15 Minutes Presentation + 3 Minutes Live Demonstration  
**Target Audience**: Academic Evaluators, Operations Research Specialists, Data Scientists  
**Assessment Target**: Task 2 PBL Assessment (30 Marks)

---

## Slide-by-Slide Presentation Structure (10–15 Minutes)

### Slide 1: Title & Executive Overview (1:00 min)
* **Title**: Evolutionary Optimization of Urban Parcel Delivery: A Capacitated Vehicle Routing Study
* **Subtitle**: High-Performance Permutation Genetic Algorithm with Adaptive Diversity Maintenance
* **Presenter Information**: Evolutionary Computing PBL Candidate
* **Key Visuals**: Split banner showing the e-commerce distribution problem statement alongside the 2D optimized route topology.
* **Speaker Script**:
  > "Good morning, evaluators. Today I present an end-to-end evolutionary computing framework developed to solve the Capacitated Vehicle Routing Problem (CVRP). Real-world logistics hubs face mounting cost and emissions pressures. In this project, we designed a robust, scalable Genetic Algorithm in Python that delivers a 29.85% distance reduction and saves over 309 kilometers compared to traditional greedy nearest-neighbor dispatching."

---

### Slide 2: Real-World Problem Scenario & NP-Hard Challenge (1:30 min)
* **Problem Description**: Regional e-commerce distribution hub in a $100 \times 100\text{ km}$ urban grid.
  - Central Depot (Node 0) at coordinates $(50.0, 50.0)\text{ km}$.
  - $N = 35$ customer locations with parcel demands $d_i \in [10, 25]\text{ units}$. Total demand = 580 units.
  - Homogeneous fleet limit: $K = 8$ delivery vans, each with payload capacity $Q = 100\text{ units}$.
* **Theoretical Complexity**:
  - Permutation search space: $35! \approx 1.03 \times 10^{40}$ possible visit sequences.
  - Multi-vehicle partitioning induces an NP-hard combinatorial explosion where exact mathematical solvers fail at scale.
* **Speaker Script**:
  > "Our problem models a real-world regional delivery depot. Thirty-five customer locations demand a total of 580 parcel units, requiring a theoretical minimum fleet of 6 vans given our 100-unit vehicle capacity. Because CVRP is NP-hard, testing every route sequence is impossible—the search space exceeds $10^{40}$ permutations. Greedy heuristics make quick, short-sighted choices that leave isolated customers and cause crossing routes. This motivates our evolutionary computing approach."

---

### Slide 3: Mathematical Formulation & Penalized Objective (1:30 min)
* **Mathematical Model**:
  $$\text{Minimize } C(S) = \sum_{k=1}^K \sum_{i=0}^N \sum_{j=0}^N c_{ij} x_{ijk} + \lambda \sum_{k=1}^K \max\left(0, \sum_{i \in R_k} d_i - Q\right)$$
  $$\text{Maximization Fitness: } F(S) = \frac{1}{1 + C(S)}$$
* **Constraints**:
  - Every customer visited exactly once: $\sum_{k=1}^K \sum_{j=0}^N x_{ijk} = 1, \quad \forall i \in \{1, \dots, N\}$
  - Flow conservation: Every route begins and ends at Depot 0.
  - Heavy violation penalty: $\lambda = 500$ enforces strict feasibility boundaries.
* **Speaker Script**:
  > "To formulate this for evolutionary computation, we define an objective function that sums total Euclidean travel distance across all active vehicles while incorporating a severe capacity penalty parameter $\lambda = 500$. We convert this minimization objective into a bounded scalar maximization fitness score $F(S) = 1 / (1 + C(S))$, allowing individuals with shorter, fully feasible routes to achieve higher reproductive fitness."

---

### Slide 4: Chromosome Representation & Greedy Split Decoder (1:30 min)
* **Representation**: 1D integer permutation vector of length $N = 35$: $[c_1, c_2, \dots, c_{35}]$.
* **Christian Prins' Greedy Capacity-Splitting Paradigm**:
  - Sequentially assigns customers to the current vehicle route until adding the next customer exceeds vehicle capacity $Q = 100$.
  - When capacity is reached, the vehicle returns to Depot 0, and a new vehicle route is initiated.
* **Key Advantages**:
  - Zero Repair Overhead: Every permutation maps directly to a valid set of multi-vehicle routes.
  - Guarantees $100\%$ customer visit completeness without illegal subtours.
* **Speaker Script**:
  > "Following the landmark work of Christian Prins, rather than using complex 2D binary adjacency matrices that generate disconnected subtours and require costly repair operators, we represent each candidate as a 1D permutation of customer IDs. Our greedy capacity-splitting decoder parses this giant tour, packing customers into vans up to capacity $Q=100$, and automatically inserting depot returns. This ensures every chromosome is structurally valid by construction."

---

### Slide 5: Evolutionary Operators & Diversity Control (2:00 min)
* **Pipeline Components**:
  1. **Hybrid Initialization**: 90% uniform random permutations + 10% randomized Nearest-Neighbor permutations.
  2. **Parent Selection**: Tournament Selection ($k=3$) providing balanced selection pressure without premature stagnation.
  3. **Recombination**: Order Crossover (OX1, $p_c = 0.85$) preserving contiguous sub-route sequences from Parent 1 and filling remaining positions from Parent 2.
  4. **Hybrid Mutation**: 50/50 balance of Swap Mutation (inter-route repositioning) and Inversion Mutation (2-opt style edge untangling, $p_m = 0.08$).
  5. **Survivor Selection & Elitism**: Generational replacement with top 4% elitism.
  6. **Adaptive Diversity Injection**: 5% random immigrant injection if population fitness standard deviation $\sigma < 10^{-6}$ for 20 generations.
* **Speaker Script**:
  > "Our evolutionary engine incorporates specialized genetic operators. We seed 10% of the initial population using randomized nearest-neighbor heuristics, giving the population a head start without compromising genetic variance. We employ Order Crossover (OX1) at an 85% rate to preserve spatial clusters, and a 50/50 hybrid mutation that combines swap mutation with 2-opt inversion to untangle intersecting road segments. Crucially, if fitness variance stagnates below $10^{-6}$, our engine injects 5% random immigrants to escape local optima."

---

### Slide 6: Experimental Design & Sensitivity Matrix (1:30 min)
* **One-Factor-At-A-Time (OFAT) Matrix**: 5 independent seeds per setting (70 runs total):
  - Population Size: $P \in \{40, 100, 200\}$
  - Mutation Rate: $p_m \in \{0.01, 0.08, 0.20\}$
  - Crossover Rate: $p_c \in \{0.60, 0.85, 0.95\}$
  - Max Generations: $\text{Gen} \in \{100, 250, 500\}$
  - Selection Strategy: Tournament Selection ($k=3$) vs. Roulette Wheel Selection
* **Logged Metrics**: Mean Best Distance, Standard Deviation, Best Distance, Convergence Generation, Runtime.
* **Speaker Script**:
  > "To validate our algorithm rigorously, we conducted an automated sensitivity suite across five key parameters with five independent random seeds per configuration—totaling 70 complete optimization runs. This allowed us to characterize how population size, genetic operators, and selection pressure interact to govern convergence speed and final solution quality."

---

### Slide 7: Experimental Results & Sensitivity Analysis (2:00 min)
* **Key Findings**:
  - **Population Size**: Increasing $P$ from 40 to 200 improved mean distance from $803.32\text{ km}$ to $780.68\text{ km}$, yielding our global best of $727.17\text{ km}$ at a modest runtime of $0.64\text{ s}$.
  - **Mutation Rate**: $p_m = 0.01$ trapped the algorithm prematurely at $821.94\text{ km}$ (mean convergence gen 4.6), while $p_m = 0.20$ caused disruptive churn ($793.27\text{ km}$). The $p_m = 0.08$ rate proved optimal ($781.49\text{ km}$).
  - **Selection Method**: Tournament Selection ($781.49\text{ km}$) decisively beat Roulette Wheel Selection ($822.12\text{ km}$) by over $40\text{ km}$ due to scale-invariant selection pressure.
* **Visual Aid**: Display `param_analysis.png`.
* **Speaker Script**:
  > "The sensitivity data revealed clear evolutionary dynamics. A very low mutation rate of 0.01 suffered severe premature convergence within just 5 generations, while 0.20 disrupted high-fitness building blocks. Tournament selection substantially outperformed Roulette Wheel selection by 40 kilometers because roulette wheel suffers from selection pressure degradation as fitness values homogenize. Population size 200 discovered our global best solution."

---

### Slide 8: Baseline Benchmark Comparison & Route Visualizations (2:00 min)
* **Head-to-Head Comparison Table**:
  | Metric | Greedy Nearest-Neighbor Baseline | Genetic Algorithm (Ours) | Improvement |
  | :--- | :---: | :---: | :---: |
  | **Total Route Distance** | $1036.59\text{ km}$ | **$727.17\text{ km}$** | **$-309.42\text{ km}$ ($-29.85\%$)** |
  | **Fleet Size Utilized** | 7 Vans | **6 Vans (Theoretical Min)** | **$-1$ Van ($-14.3\%$)** |
  | **Execution Time** | $0.42\text{ ms}$ | $0.796\text{ s}$ | Real-time dispatch feasible |
* **Visual Aid**: Display `route_comparison.png` and `convergence_curve.png`.
* **Speaker Script**:
  > "Here is our benchmark comparison. The deterministic nearest-neighbor baseline produces 1,036 kilometers across 7 vehicles, suffering from overlapping paths and stranding customer 27 on an inefficient solo route. In contrast, our GA achieved 727.17 kilometers across just 6 vehicles—matching the theoretical minimum fleet size. That is an absolute savings of 309.42 kilometers, or a 29.85% reduction, fully computed in under 0.8 seconds."

---

### Slide 9: Conclusion, Industrial Relevance & Future Work (1:00 min)
* **Summary of Achievements**:
  - Demonstrated full evolutionary pipeline matching all Task 2 PBL rubric criteria.
  - Achieved near-30% travel distance reduction and optimal fleet sizing.
  - Validated 70 experimental runs with statistical rigor and publication-grade visualizations.
* **Future Extensions**: Time windows (VRPTW), dynamic traffic matrices, multi-depot extensions.
* **Speaker Script**:
  > "In conclusion, our evolutionary algorithm successfully solves the CVRP with high computational efficiency, strong convergence stability, and substantial distance savings. This demonstrates the immense value of metaheuristic search for modern green logistics. Thank you, and I am now ready to demonstrate the live code execution."

---

## Live Demonstration Script (3 Minutes)

### Step 1: Terminal Setup & Execution
Open the command line in the project workspace and run:
```powershell
python cvrp_evolutionary_project/main.py --demo
```

### Step 2: Demonstration Narration
1. **Instance Summary Displayed (0:00 - 0:30)**:
   > "As we launch `main.py --demo`, the system first seeds the benchmark environment with Seed 42, generating 35 customer locations across a 100x100 kilometer grid with total demand of 580 parcel units."
2. **Baseline NN Execution (0:30 - 1:00)**:
   > "Next, it runs the deterministic Greedy Nearest-Neighbor baseline. In less than one millisecond, it outputs a solution totaling 1,036.59 kilometers across 7 delivery vans."
3. **Genetic Algorithm Optimization Loop (1:00 - 2:00)**:
   > "Now watch the GA engine execute. Starting at generation 0 with a population average distance of ~1,770 km, within 50 generations the best chromosome rapidly untangles to under 780 km. Our adaptive early stopping condition activates once improvements taper below $10^{-5}$ across 60 generations."
4. **Summary & Output Inspection (2:00 - 3:00)**:
   > "The terminal displays the benchmark summary table showing over 25% distance reduction. Simultaneously, the program outputs high-resolution 300 DPI figures to `outputs/plots/` and serializes the full coordinate and vehicle partition structure to `outputs/best_routes.json`."

---

## Question & Answer Preparation (Evaluator Defense)

1. **Q: Why did you choose permutation encoding over a binary adjacency matrix?**
   - *A*: A binary adjacency matrix has $N^2$ binary variables and frequently creates disjoint cycles, unvisited nodes, or subtours, requiring computationally expensive repair operators. Permutation encoding ensures every customer ID appears exactly once, guaranteeing 100% validity by construction.

2. **Q: How does your fitness function prevent capacity violations?**
   - *A*: Our greedy capacity-splitting decoder splits routes before $Q=100$ is exceeded. In addition, our fitness function incorporates an explicit penalty term $\lambda \sum \max(0, \text{demand} - Q)$ with $\lambda = 500$, heavily suppressing any infeasible candidates.

3. **Q: Why is Tournament selection superior to Roulette Wheel selection here?**
   - *A*: Roulette Wheel selection relies on absolute fitness values. As the population converges and fitness values become very close (e.g., $0.00127$ vs $0.00128$), selection probabilities become nearly uniform, causing loss of selection pressure. Tournament selection maintains invariant selection pressure based solely on rank.

