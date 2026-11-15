"""
src/experiments.py
Stage 5: Automated Parameter Sensitivity Suite (One-Factor-At-A-Time across 5 parameters,
5 independent random seeds per setting).
Generates experiment_results.csv, experiment_summary.md, and best_routes.json.
"""

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any
import numpy as np

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.dataset import get_default_instance, CVRPInstance
from src.decoder import calculate_route_demand, calculate_route_distance
from src.ga_engine import run_genetic_algorithm, GAConfig, GAResult
from src.baseline_nn import solve_greedy_nearest_neighbor, BaselineResult


SEEDS = [42, 101, 202, 303, 404]


def run_experiment_suite(
    instance: CVRPInstance | None = None,
    output_dir: str | Path | None = None,
    verbose: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any], BaselineResult, GAResult]:
    """
    Executes the 5 OFAT parameter sweeps with 5 independent seeds per configuration:
    1. Population Size: P in {40, 100, 200}
    2. Mutation Rate: pm in {0.01, 0.08, 0.20}
    3. Crossover Rate: pc in {0.60, 0.85, 0.95}
    4. Generations: Gen in {100, 250, 500}
    5. Selection Method: {Tournament (k=3), Roulette Wheel}
    """
    if instance is None:
        instance = get_default_instance()
    if output_dir is None:
        output_dir = project_root / "outputs"
    else:
        output_dir = Path(output_dir)

    tables_dir = output_dir / "tables"
    plots_dir = output_dir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run deterministic baseline solver
    if verbose:
        print("\n" + "=" * 70)
        print("STAGE 4: Executing Deterministic Greedy Nearest-Neighbor Baseline...")
        print("=" * 70)
    baseline_res = solve_greedy_nearest_neighbor(instance)
    if verbose:
        print(f"  NN Distance: {baseline_res.total_distance:.2f} km | Vehicles: {baseline_res.num_vehicles} | Runtime: {baseline_res.execution_time * 1000:.3f} ms")

    # Parameter sweeps definition
    sweeps = [
        # (category_name, param_name, list of (param_val, config_dict))
        (
            "Population Size",
            "pop_size",
            [
                (40, {"pop_size": 40, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "tournament"}),
                (100, {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "tournament"}),
                (200, {"pop_size": 200, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "tournament"}),
            ],
        ),
        (
            "Mutation Rate",
            "mutation_rate",
            [
                (0.01, {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.01, "max_generations": 400, "selection_method": "tournament"}),
                (0.08, {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "tournament"}),
                (0.20, {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.20, "max_generations": 400, "selection_method": "tournament"}),
            ],
        ),
        (
            "Crossover Rate",
            "crossover_rate",
            [
                (0.60, {"pop_size": 100, "crossover_rate": 0.60, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "tournament"}),
                (0.85, {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "tournament"}),
                (0.95, {"pop_size": 100, "crossover_rate": 0.95, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "tournament"}),
            ],
        ),
        (
            "Max Generations",
            "max_generations",
            [
                (100, {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 100, "selection_method": "tournament"}),
                (250, {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 250, "selection_method": "tournament"}),
                (500, {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 500, "selection_method": "tournament"}),
            ],
        ),
        (
            "Selection Method",
            "selection_method",
            [
                ("Tournament (k=3)", {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "tournament", "tournament_k": 3}),
                ("Roulette Wheel", {"pop_size": 100, "crossover_rate": 0.85, "mutation_rate": 0.08, "max_generations": 400, "selection_method": "roulette"}),
            ],
        ),
    ]

    all_raw_results: list[dict[str, Any]] = []
    overall_best_ga_result: GAResult | None = None

    if verbose:
        print("\n" + "=" * 70)
        print("STAGE 5: Executing Parameter Sensitivity Suite (70 Runs Total)...")
        print("=" * 70)

    run_counter = 0
    total_runs = sum(len(configs) * len(SEEDS) for _, _, configs in sweeps)

    for cat_name, param_name, config_list in sweeps:
        if verbose:
            print(f"\n--- Sweeping {cat_name} ---")
        for param_val, cfg_kwargs in config_list:
            for seed in SEEDS:
                run_counter += 1
                cfg = GAConfig(**cfg_kwargs, seed=seed)
                res = run_genetic_algorithm(instance, cfg, verbose=False)

                record = {
                    "experiment_category": cat_name,
                    "parameter_name": param_name,
                    "parameter_value": str(param_val),
                    "seed": seed,
                    "best_distance": round(res.best_distance, 2),
                    "best_fitness": round(res.best_fitness, 8),
                    "num_vehicles": res.num_vehicles,
                    "convergence_gen": res.generation_converged,
                    "total_generations": res.total_generations,
                    "runtime_sec": round(res.execution_time, 4),
                }
                all_raw_results.append(record)

                if overall_best_ga_result is None or res.best_distance < overall_best_ga_result.best_distance:
                    overall_best_ga_result = res

            if verbose:
                matching = [r for r in all_raw_results if r["experiment_category"] == cat_name and r["parameter_value"] == str(param_val)]
                dists = [m["best_distance"] for m in matching]
                times = [m["runtime_sec"] for m in matching]
                print(
                    f"  [{run_counter:2d}/{total_runs}] {param_name}={param_val:<16} | "
                    f"Mean Dist: {np.mean(dists):7.2f} ± {np.std(dists):5.2f} km | "
                    f"Best: {np.min(dists):7.2f} km | Mean Time: {np.mean(times):.3f}s"
                )

    # 2. Write outputs/tables/experiment_results.csv
    csv_path = tables_dir / "experiment_results.csv"
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "experiment_category",
            "parameter_name",
            "parameter_value",
            "seed",
            "best_distance",
            "best_fitness",
            "num_vehicles",
            "convergence_gen",
            "total_generations",
            "runtime_sec",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_raw_results)

    # 3. Aggregate results for experiment_summary.md
    summary_data: dict[str, list[dict[str, Any]]] = {}
    for cat_name, param_name, config_list in sweeps:
        cat_summaries = []
        for param_val, _ in config_list:
            subset = [
                r for r in all_raw_results
                if r["experiment_category"] == cat_name and r["parameter_value"] == str(param_val)
            ]
            dists = [s["best_distance"] for s in subset]
            gens = [s["convergence_gen"] for s in subset]
            times = [s["runtime_sec"] for s in subset]
            vehs = [s["num_vehicles"] for s in subset]

            cat_summaries.append({
                "parameter_value": str(param_val),
                "mean_distance": float(np.mean(dists)),
                "std_distance": float(np.std(dists)),
                "best_distance": float(np.min(dists)),
                "worst_distance": float(np.max(dists)),
                "mean_conv_gen": float(np.mean(gens)),
                "mean_runtime": float(np.mean(times)),
                "mean_vehicles": float(np.mean(vehs)),
            })
        summary_data[cat_name] = cat_summaries

    # 4. Generate Markdown Summary Table
    md_path = tables_dir / "experiment_summary.md"
    savings_pct = (
        (baseline_res.total_distance - overall_best_ga_result.best_distance)
        / baseline_res.total_distance
    ) * 100.0

    md_lines = [
        "# CVRP Evolutionary Algorithm: Experimental Sensitivity Analysis & Benchmark Summary",
        "",
        "## Executive Summary & Baseline Comparison",
        "",
        f"- **Benchmark Instance**: 35 Customers + 1 Central Depot, Seed=42, Fleet Limit K = {instance.max_vehicles}, Capacity Q = {instance.vehicle_capacity}",
        f"- **Total Customer Demand**: {instance.total_demand} units (Theoretical minimum fleet = {int(np.ceil(instance.total_demand / instance.vehicle_capacity))} vans)",
        f"- **Deterministic Greedy Nearest-Neighbor Baseline Distance**: **{baseline_res.total_distance:.2f} km** ({baseline_res.num_vehicles} vehicles, runtime: {baseline_res.execution_time * 1000:.2f} ms)",
        f"- **Genetic Algorithm Global Best Distance**: **{overall_best_ga_result.best_distance:.2f} km** ({overall_best_ga_result.num_vehicles} vehicles, runtime: {overall_best_ga_result.execution_time:.3f} s)",
        f"- **Net Distance Savings Achieved by GA**: **{baseline_res.total_distance - overall_best_ga_result.best_distance:.2f} km ({savings_pct:.2f}% reduction)**",
        "",
        "---",
        "",
        "## One-Factor-At-A-Time (OFAT) Sensitivity Sweeps (5 Runs Per Setting)",
        "",
    ]

    for cat_name, rows in summary_data.items():
        md_lines.append(f"### {cat_name} Sensitivity Analysis")
        md_lines.append("")
        md_lines.append("| Tested Value | Mean Best Distance (km) | Std Dev (km) | Best Overall (km) | Mean Conv. Gen | Mean Runtime (s) |")
        md_lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
        for r in rows:
            md_lines.append(
                f"| **{r['parameter_value']}** | {r['mean_distance']:.2f} | {r['std_distance']:.2f} | {r['best_distance']:.2f} | {r['mean_conv_gen']:.1f} | {r['mean_runtime']:.3f} |"
            )
        md_lines.append("")

    with open(md_path, mode="w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # 5. Serialize best routes and metrics to outputs/best_routes.json
    best_routes_path = output_dir / "best_routes.json"
    ga_route_demands = [
        calculate_route_demand(r, instance.demands) for r in overall_best_ga_result.best_routes
    ]
    ga_route_dists = [
        calculate_route_distance(r, instance.dist_matrix) for r in overall_best_ga_result.best_routes
    ]

    best_routes_payload = {
        "problem_metadata": {
            "num_customers": instance.num_customers,
            "total_nodes": instance.num_nodes,
            "depot_coordinate": list(instance.depot_coord),
            "vehicle_capacity": instance.vehicle_capacity,
            "max_fleet_limit": instance.max_vehicles,
            "total_customer_demand": instance.total_demand,
            "theoretical_min_fleet": int(np.ceil(instance.total_demand / instance.vehicle_capacity)),
            "instance_seed": instance.seed,
        },
        "baseline_nearest_neighbor": {
            "solver_type": "Deterministic Greedy Nearest-Neighbor with Capacity Splitting",
            "total_distance_km": round(baseline_res.total_distance, 2),
            "vehicles_utilized": baseline_res.num_vehicles,
            "runtime_seconds": round(baseline_res.execution_time, 6),
            "routes": baseline_res.routes,
            "route_demands": baseline_res.route_demands,
            "route_distances_km": [round(d, 2) for d in baseline_res.route_distances],
        },
        "genetic_algorithm_best": {
            "total_distance_km": round(overall_best_ga_result.best_distance, 2),
            "best_fitness": round(overall_best_ga_result.best_fitness, 8),
            "vehicles_utilized": overall_best_ga_result.num_vehicles,
            "generation_converged": overall_best_ga_result.generation_converged,
            "total_generations": overall_best_ga_result.total_generations,
            "runtime_seconds": round(overall_best_ga_result.execution_time, 4),
            "distance_savings_km": round(baseline_res.total_distance - overall_best_ga_result.best_distance, 2),
            "distance_savings_percent": round(savings_pct, 2),
            "routes": overall_best_ga_result.best_routes,
            "route_demands": ga_route_demands,
            "route_distances_km": [round(d, 2) for d in ga_route_dists],
            "best_chromosome": overall_best_ga_result.best_chromosome,
        },
    }

    with open(best_routes_path, mode="w", encoding="utf-8") as f:
        json.dump(best_routes_payload, f, indent=2)

    if verbose:
        print(f"\nArtifacts generated successfully:")
        print(f"  - Detailed Raw CSV : {csv_path}")
        print(f"  - Summary Markdown : {md_path}")
        print(f"  - Serialized JSON  : {best_routes_path}")

    return all_raw_results, summary_data, baseline_res, overall_best_ga_result


if __name__ == "__main__":
    run_experiment_suite(verbose=True)

