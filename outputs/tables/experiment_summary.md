# CVRP Evolutionary Algorithm: Experimental Sensitivity Analysis & Benchmark Summary

## Executive Summary & Baseline Comparison

- **Benchmark Instance**: 35 Customers + 1 Central Depot, Seed=42, Fleet Limit K = 8, Capacity Q = 100
- **Total Customer Demand**: 580 units (Theoretical minimum fleet = 6 vans)
- **Deterministic Greedy Nearest-Neighbor Baseline Distance**: **1036.59 km** (7 vehicles, runtime: 0.42 ms)
- **Genetic Algorithm Global Best Distance**: **727.17 km** (6 vehicles, runtime: 0.796 s)
- **Net Distance Savings Achieved by GA**: **309.42 km (29.85% reduction)**

---

## One-Factor-At-A-Time (OFAT) Sensitivity Sweeps (5 Runs Per Setting)

### Population Size Sensitivity Analysis

| Tested Value | Mean Best Distance (km) | Std Dev (km) | Best Overall (km) | Mean Conv. Gen | Mean Runtime (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **40** | 803.32 | 10.80 | 785.36 | 61.6 | 0.161 |
| **100** | 781.49 | 14.45 | 768.81 | 80.2 | 0.430 |
| **200** | 780.68 | 28.62 | 727.17 | 62.0 | 0.640 |

### Mutation Rate Sensitivity Analysis

| Tested Value | Mean Best Distance (km) | Std Dev (km) | Best Overall (km) | Mean Conv. Gen | Mean Runtime (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **0.01** | 821.94 | 13.13 | 802.70 | 4.6 | 0.233 |
| **0.08** | 781.49 | 14.45 | 768.81 | 80.2 | 0.416 |
| **0.2** | 793.27 | 11.64 | 773.90 | 75.4 | 0.382 |

### Crossover Rate Sensitivity Analysis

| Tested Value | Mean Best Distance (km) | Std Dev (km) | Best Overall (km) | Mean Conv. Gen | Mean Runtime (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **0.6** | 808.08 | 9.39 | 796.43 | 50.4 | 0.271 |
| **0.85** | 781.49 | 14.45 | 768.81 | 80.2 | 0.411 |
| **0.95** | 795.69 | 17.00 | 763.50 | 57.8 | 0.319 |

### Max Generations Sensitivity Analysis

| Tested Value | Mean Best Distance (km) | Std Dev (km) | Best Overall (km) | Mean Conv. Gen | Mean Runtime (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **100** | 783.59 | 13.82 | 768.81 | 60.4 | 0.341 |
| **250** | 781.49 | 14.45 | 768.81 | 80.2 | 0.409 |
| **500** | 781.49 | 14.45 | 768.81 | 80.2 | 0.409 |

### Selection Method Sensitivity Analysis

| Tested Value | Mean Best Distance (km) | Std Dev (km) | Best Overall (km) | Mean Conv. Gen | Mean Runtime (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tournament (k=3)** | 781.49 | 14.45 | 768.81 | 80.2 | 0.412 |
| **Roulette Wheel** | 822.12 | 13.33 | 802.70 | 29.2 | 0.266 |
