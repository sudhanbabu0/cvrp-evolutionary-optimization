"""
main.py
Master CLI entry point for CVRP Evolutionary Computing Project.
Supports:
  --demo        : Rapid live end-to-end execution, solver comparisons, and plot generation
  --experiments : Runs full Stage 5 sensitivity matrix (70 runs, 5 seeds per setting)
  --plots       : Renders high-resolution 300 DPI publication plots
  --all         : Executes full end-to-end pipeline (experiments -> plots -> report check)
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure project root is in python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.dataset import get_default_instance
from src.baseline_nn import solve_greedy_nearest_neighbor
from src.ga_engine import run_genetic_algorithm, GAConfig
from src.experiments import run_experiment_suite
from src.visualize import plot_convergence, plot_route_comparison, plot_parameter_analysis


def run_demo():
    """Runs a live end-to-end demo of CVRP optimization."""
    print("=" * 76)
    print("  CVRP EVOLUTIONARY OPTIMIZATION: LIVE DEMONSTRATION & BENCHMARK")
    print("=" * 76)

    instance = get_default_instance()
    print("\n[1/4] Problem Instance Initialized:")
    print(instance.summary())

    print("\n" + "-" * 76)
    print("[2/4] Executing Traditional Baseline: Deterministic Greedy Nearest-Neighbor...")
    base_start = time.perf_counter()
    base_res = solve_greedy_nearest_neighbor(instance)
    base_time = time.perf_counter() - base_start
    print(f"  -> Total Baseline Route Distance : {base_res.total_distance:7.2f} km")
    print(f"  -> Vehicles Utilized              : {base_res.num_vehicles} / {instance.max_vehicles}")
    print(f"  -> Baseline Computation Time      : {base_time * 1000:7.3f} ms")

    print("\n" + "-" * 76)
    print("[3/4] Executing Proposed Solution: Genetic Algorithm with Hybrid Seeding & OX1...")
    cfg = GAConfig(
        pop_size=100,
        crossover_rate=0.85,
        mutation_rate=0.08,
        max_generations=400,
        selection_method="tournament",
        tournament_k=3,
        elitism_rate=0.04,
        seed=42,
    )
    ga_res = run_genetic_algorithm(instance, config=cfg, verbose=True)

    dist_savings = base_res.total_distance - ga_res.best_distance
    savings_pct = (dist_savings / base_res.total_distance) * 100.0

    print("\n" + "=" * 76)
    print("  OPTIMIZATION BENCHMARK SUMMARY")
    print("=" * 76)
    print(f"  Metric                      | Baseline (Greedy NN) | Genetic Algorithm (Ours)")
    print(f"  ----------------------------+----------------------+-------------------------")
    print(f"  Total Travel Distance (km)  | {base_res.total_distance:18.2f}   | {ga_res.best_distance:21.2f}")
    print(f"  Fleet Vans Utilized         | {base_res.num_vehicles:18d}   | {ga_res.num_vehicles:21d}")
    print(f"  Execution Time              | {base_time * 1000:15.3f} ms   | {ga_res.execution_time:18.3f} s")
    print(f"  Generation Converged        |                N/A   | {ga_res.generation_converged:21d}")
    print(f"  Fitness Score F(S)          | {1.0 / (1.0 + base_res.total_distance):18.8f}   | {ga_res.best_fitness:21.8f}")
    print(f"  ----------------------------+----------------------+-------------------------")
    print(f"  Distance Reduction (km)     | {'-':18s}   | {dist_savings:18.2f} km")
    print(f"  Percentage Distance Savings | {'-':18s}   | {savings_pct:18.2f} %")
    print("=" * 76)

    print("\n[4/4] Generating Demonstration Visualizations...")
    plots_dir = project_root / "outputs" / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Check if global best routes exist from sensitivity sweeps
    best_json = project_root / "outputs" / "best_routes.json"
    if best_json.exists():
        import json
        with open(best_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        best_routes = data["genetic_algorithm_best"]["routes"]
        best_dist = data["genetic_algorithm_best"]["total_distance_km"]
        print(f"  (Plotting with global best routes: {best_dist:.2f} km across {len(best_routes)} vehicles)")
    else:
        best_routes = ga_res.best_routes
        best_dist = ga_res.best_distance

    plot_convergence(ga_res.history, plots_dir / "convergence_curve.png")
    plot_route_comparison(
        instance.coords,
        instance.demands,
        base_res.routes,
        base_res.total_distance,
        best_routes,
        best_dist,
        plots_dir / "route_comparison.png",
    )
    print(f"  Saved convergence plot : {plots_dir / 'convergence_curve.png'}")
    print(f"  Saved route map        : {plots_dir / 'route_comparison.png'}")
    print("\nDemo completed successfully with 0 errors!")


def main():
    parser = argparse.ArgumentParser(description="CVRP Evolutionary Optimization Master CLI")
    parser.add_argument("--demo", action="store_true", help="Run rapid end-to-end optimization demo and visualizer")
    parser.add_argument("--experiments", action="store_true", help="Run full Stage 5 parameter sensitivity suite (70 runs)")
    parser.add_argument("--plots", action="store_true", help="Generate all high-resolution 300 DPI charts")
    parser.add_argument("--all", action="store_true", help="Run full pipeline: experiments, plots, and demo check")

    args = parser.parse_args()

    # Default to --demo if no argument passed
    if not (args.demo or args.experiments or args.plots or args.all):
        args.demo = True

    if args.all or args.experiments:
        print("\n>>> EXECUTING COMPLETE PARAMETER SENSITIVITY SUITE (STAGE 5) <<<")
        raw_res, summary_data, base_res, best_ga = run_experiment_suite(verbose=True)

        print("\n>>> GENERATING ALL PUBLICATION CHARTS (STAGE 6) <<<")
        plots_dir = project_root / "outputs" / "plots"
        inst = get_default_instance()
        plot_convergence(best_ga.history, plots_dir / "convergence_curve.png")
        plot_route_comparison(
            inst.coords,
            inst.demands,
            base_res.routes,
            base_res.total_distance,
            best_ga.best_routes,
            best_ga.best_distance,
            plots_dir / "route_comparison.png",
        )
        plot_parameter_analysis(summary_data, plots_dir / "param_analysis.png")
        print("All high-resolution plots generated at 300 DPI.")

    elif args.plots:
        print("\n>>> GENERATING PUBLICATION CHARTS (300 DPI) <<<")
        inst = get_default_instance()
        plots_dir = project_root / "outputs" / "plots"
        plots_dir.mkdir(parents=True, exist_ok=True)
        base_res = solve_greedy_nearest_neighbor(inst)

        best_json = project_root / "outputs" / "best_routes.json"
        csv_file = project_root / "outputs" / "tables" / "experiment_results.csv"

        if best_json.exists():
            import json
            with open(best_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            ga_routes = data["genetic_algorithm_best"]["routes"]
            ga_dist = data["genetic_algorithm_best"]["total_distance_km"]
        else:
            ga_res = run_genetic_algorithm(inst, GAConfig(seed=42), verbose=False)
            ga_routes = ga_res.best_routes
            ga_dist = ga_res.best_distance

        # Run one full GA run for detailed convergence curve
        ga_run = run_genetic_algorithm(inst, GAConfig(seed=42, max_generations=400), verbose=False)
        plot_convergence(ga_run.history, plots_dir / "convergence_curve.png")

        plot_route_comparison(
            inst.coords,
            inst.demands,
            base_res.routes,
            base_res.total_distance,
            ga_routes,
            ga_dist,
            plots_dir / "route_comparison.png",
        )

        if csv_file.exists():
            import csv
            import numpy as np
            # Reconstruct summary_data
            rows = []
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            cats = ["Population Size", "Mutation Rate", "Crossover Rate", "Max Generations", "Selection Method"]
            summary_data = {}
            for cat in cats:
                cat_rows = [r for r in rows if r["experiment_category"] == cat]
                vals = sorted(list(set(r["parameter_value"] for r in cat_rows)), key=lambda x: (float(x) if x.replace('.', '', 1).isdigit() else x))
                summary_data[cat] = []
                for v in vals:
                    sub = [r for r in cat_rows if r["parameter_value"] == v]
                    dists = [float(r["best_distance"]) for r in sub]
                    summary_data[cat].append({
                        "parameter_value": v,
                        "mean_distance": float(np.mean(dists)),
                        "std_distance": float(np.std(dists)),
                        "best_distance": float(np.min(dists)),
                    })
            plot_parameter_analysis(summary_data, plots_dir / "param_analysis.png")
            print("  Re-rendered param_analysis.png from experiment_results.csv.")

        print("All high-resolution charts generated at 300 DPI.")

    if args.demo:
        run_demo()


if __name__ == "__main__":
    main()
