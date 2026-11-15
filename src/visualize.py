"""
src/visualize.py
Generates 300 DPI publication-grade figures for CVRP evolutionary optimization:
1. convergence_curve.png: Generation vs. Best Distance & Fitness / Diversity
2. route_comparison.png: Side-by-side 2D maps comparing Nearest-Neighbor vs. GA routes
3. param_analysis.png: Multi-panel parameter sensitivity charts
"""

from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Apply clean scientific styling
plt.rcParams.update({
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.family": "sans-serif",
    "figure.titlesize": 16,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.autolayout": False,
})

COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]


def plot_convergence(history: dict[str, list], output_path: str | Path, dpi: int = 300):
    """
    Renders convergence_curve.png:
    - Top/Left: Generation vs. Best Distance and Average Distance (km).
    - Bottom/Right: Generation vs. Best Fitness and Population Diversity (Fitness Std Dev).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    gens = history["generation"]
    best_dist = history["best_distance"]
    avg_dist = history["avg_distance"]
    best_fit = history["best_fitness"]
    diversity = history["diversity_std"]
    injections = history.get("injections", [])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, dpi=dpi)
    fig.suptitle("CVRP Genetic Algorithm Evolutionary Convergence Trajectory", fontsize=15, fontweight="bold", y=0.98)

    # Subplot 1: Distance Convergence
    ax1.plot(gens, avg_dist, color="#999999", linestyle="--", linewidth=1.5, label="Population Mean Distance", alpha=0.8)
    ax1.plot(gens, best_dist, color="#1f77b4", linewidth=2.5, label="Best Chromosome Distance")
    ax1.set_ylabel("Total Travel Distance (km)", fontweight="bold")
    ax1.set_title("Travel Distance Optimization over Generations", fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right", frameon=True, framealpha=0.9)

    # Highlight min distance
    min_dist = min(best_dist)
    min_gen = gens[best_dist.index(min_dist)]
    ax1.scatter([min_gen], [min_dist], color="#d62728", s=60, zorder=5)
    ax1.annotate(
        f"Global Best: {min_dist:.2f} km (Gen {min_gen})",
        xy=(min_gen, min_dist),
        xytext=(min_gen + 15, min_dist + (max(best_dist) - min_dist) * 0.1),
        arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5),
        fontweight="bold",
        color="#d62728",
        bbox=dict(boxstyle="round,pad=0.3", fc="#ffeedd", ec="#d62728", lw=1),
    )

    # Subplot 2: Fitness & Diversity
    ax2.plot(gens, best_fit, color="#2ca02c", linewidth=2.2, label="Best Fitness F(S)")
    ax2.set_xlabel("Generation", fontweight="bold")
    ax2.set_ylabel("Fitness Score F(S) = 1 / (1 + C(S))", color="#2ca02c", fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#2ca02c")
    ax2.grid(True, linestyle=":", alpha=0.6)

    # Secondary axis for diversity std
    ax2_twin = ax2.twinx()
    ax2_twin.plot(gens, diversity, color="#9467bd", linestyle="-.", linewidth=1.5, label="Fitness Std Dev (Diversity)")
    ax2_twin.set_ylabel("Population Diversity (Fitness Std)", color="#9467bd", fontweight="bold")
    ax2_twin.tick_params(axis="y", labelcolor="#9467bd")

    # Mark diversity injections if any
    for inj_gen in injections:
        ax2.axvline(x=inj_gen, color="#e377c2", linestyle=":", linewidth=1.5)
        ax2.annotate("Diversity Injection", xy=(inj_gen, best_fit[inj_gen]), fontsize=8, color="#e377c2")

    # Combine legends for ax2 and ax2_twin
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="lower right", frameon=True, framealpha=0.9)
    ax2.set_title("Fitness Maximization & Genetic Diversity Maintenance", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()


def _draw_route_map(
    ax: plt.Axes,
    coords: np.ndarray,
    demands: np.ndarray,
    routes: list[list[int]],
    title: str,
    total_dist: float,
    num_vehicles: int,
):
    """Draws a 2D multi-vehicle delivery route map on the specified Axes."""
    depot_coord = coords[0]

    # Draw routes with distinct colors and arrows
    for r_idx, route in enumerate(routes):
        col = COLORS[r_idx % len(COLORS)]
        route_coords = [coords[node] for node in route]
        xs = [pt[0] for pt in route_coords]
        ys = [pt[1] for pt in route_coords]

        # Route path
        ax.plot(xs, ys, color=col, linewidth=2.0, alpha=0.85, label=f"Van {r_idx + 1} ({len(route)-2} stops)")

        # Directional arrows along route
        for i in range(len(route) - 1):
            n1, n2 = route[i], route[i + 1]
            p1, p2 = coords[n1], coords[n2]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            dist = np.hypot(dx, dy)
            if dist > 5.0:
                mid_x = p1[0] + dx * 0.55
                mid_y = p1[1] + dy * 0.55
                ax.annotate(
                    "",
                    xy=(mid_x + dx * 0.05, mid_y + dy * 0.05),
                    xytext=(mid_x - dx * 0.05, mid_y - dy * 0.05),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.8, mutation_scale=12),
                )

    # Plot customer nodes
    for c_id in range(1, len(coords)):
        cx, cy = coords[c_id]
        ax.scatter(cx, cy, color="#333333", s=70, zorder=4, edgecolors="white", linewidth=1.2)
        ax.annotate(
            f"{c_id}",
            (cx, cy),
            fontsize=8,
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            zorder=5,
        )

    # Plot Depot 0
    ax.scatter(
        depot_coord[0],
        depot_coord[1],
        color="#d62728",
        s=200,
        marker="s",
        zorder=6,
        edgecolors="black",
        linewidth=2.0,
        label="Depot 0 (50, 50)",
    )

    ax.set_title(f"{title}\nTotal Distance: {total_dist:.2f} km | Fleet: {num_vehicles} vans", fontweight="bold", pad=10)
    ax.set_xlabel("X Coordinate (km)", fontweight="bold")
    ax.set_ylabel("Y Coordinate (km)", fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, frameon=True)


def plot_route_comparison(
    coords: np.ndarray,
    demands: np.ndarray,
    baseline_routes: list[list[int]],
    baseline_dist: float,
    ga_routes: list[list[int]],
    ga_dist: float,
    output_path: str | Path,
    dpi: int = 300,
):
    """
    Renders route_comparison.png:
    Side-by-side 2D maps comparing Nearest-Neighbor baseline routes against GA-optimized routes.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9), dpi=dpi)
    fig.suptitle(
        "Capacitated Vehicle Routing Problem: Baseline vs. Evolutionary Route Comparison",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    _draw_route_map(
        ax=ax1,
        coords=coords,
        demands=demands,
        routes=baseline_routes,
        title="Baseline: Greedy Nearest-Neighbor Heuristic",
        total_dist=baseline_dist,
        num_vehicles=len(baseline_routes),
    )

    savings = baseline_dist - ga_dist
    savings_pct = (savings / baseline_dist) * 100.0
    _draw_route_map(
        ax=ax2,
        coords=coords,
        demands=demands,
        routes=ga_routes,
        title=f"Evolutionary Algorithm (GA) Optimization\n(Savings: {savings:.2f} km / -{savings_pct:.1f}%)",
        total_dist=ga_dist,
        num_vehicles=len(ga_routes),
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()


def plot_parameter_analysis(
    summary_data: dict[str, list[dict]],
    output_path: str | Path,
    dpi: int = 300,
):
    """
    Renders param_analysis.png:
    Multi-panel chart illustrating the impact of Population Size, Mutation Rate,
    Crossover Rate, and Selection Method / Generations.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axs = plt.subplots(2, 2, figsize=(13, 10), dpi=dpi)
    fig.suptitle("CVRP Genetic Algorithm Hyperparameter Sensitivity Analysis", fontsize=16, fontweight="bold", y=0.98)

    # 1. Population Size
    ax = axs[0, 0]
    pop_rows = summary_data.get("Population Size", [])
    x_vals = [r["parameter_value"] for r in pop_rows]
    means = [r["mean_distance"] for r in pop_rows]
    stds = [r["std_distance"] for r in pop_rows]
    bests = [r["best_distance"] for r in pop_rows]
    bars = ax.bar(x_vals, means, yerr=stds, capsize=6, color="#1f77b4", alpha=0.75, edgecolor="black", label="Mean Best Distance")
    ax.scatter(x_vals, bests, color="#d62728", s=50, zorder=5, label="Best Run Distance")
    ax.set_title("(a) Population Size (P ∈ {40, 100, 200})", fontweight="bold")
    ax.set_xlabel("Population Size P", fontweight="bold")
    ax.set_ylabel("Mean Travel Distance (km)", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.9)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h / 2), ha="center", va="center", color="white", fontweight="bold")

    # 2. Mutation Rate
    ax = axs[0, 1]
    mut_rows = summary_data.get("Mutation Rate", [])
    x_vals = [r["parameter_value"] for r in mut_rows]
    means = [r["mean_distance"] for r in mut_rows]
    stds = [r["std_distance"] for r in mut_rows]
    bests = [r["best_distance"] for r in mut_rows]
    bars = ax.bar(x_vals, means, yerr=stds, capsize=6, color="#ff7f0e", alpha=0.75, edgecolor="black", label="Mean Best Distance")
    ax.scatter(x_vals, bests, color="#d62728", s=50, zorder=5, label="Best Run Distance")
    ax.set_title("(b) Mutation Rate (pm ∈ {0.01, 0.08, 0.20})", fontweight="bold")
    ax.set_xlabel("Mutation Probability (pm)", fontweight="bold")
    ax.set_ylabel("Mean Travel Distance (km)", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.9)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h / 2), ha="center", va="center", color="white", fontweight="bold")

    # 3. Crossover Rate
    ax = axs[1, 0]
    cross_rows = summary_data.get("Crossover Rate", [])
    x_vals = [r["parameter_value"] for r in cross_rows]
    means = [r["mean_distance"] for r in cross_rows]
    stds = [r["std_distance"] for r in cross_rows]
    bests = [r["best_distance"] for r in cross_rows]
    bars = ax.bar(x_vals, means, yerr=stds, capsize=6, color="#2ca02c", alpha=0.75, edgecolor="black", label="Mean Best Distance")
    ax.scatter(x_vals, bests, color="#d62728", s=50, zorder=5, label="Best Run Distance")
    ax.set_title("(c) Crossover Rate (pc ∈ {0.60, 0.85, 0.95})", fontweight="bold")
    ax.set_xlabel("Crossover Probability (pc)", fontweight="bold")
    ax.set_ylabel("Mean Travel Distance (km)", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.9)
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}", xy=(bar.get_x() + bar.get_width() / 2, h / 2), ha="center", va="center", color="white", fontweight="bold")

    # 4. Selection Method & Generations
    ax = axs[1, 1]
    sel_rows = summary_data.get("Selection Method", [])
    gen_rows = summary_data.get("Max Generations", [])

    labels = [r["parameter_value"] for r in sel_rows] + [f"Gen={r['parameter_value']}" for r in gen_rows]
    all_means = [r["mean_distance"] for r in sel_rows] + [r["mean_distance"] for r in gen_rows]
    all_stds = [r["std_distance"] for r in sel_rows] + [r["std_distance"] for r in gen_rows]
    colors = ["#9467bd", "#9467bd", "#17becf", "#17becf", "#17becf"]

    bars = ax.bar(range(len(labels)), all_means, yerr=all_stds, capsize=6, color=colors, alpha=0.75, edgecolor="black")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_title("(d) Selection Strategy & Max Generation Limits", fontweight="bold")
    ax.set_ylabel("Mean Travel Distance (km)", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)

    # Custom legend for category colors
    p1 = mpatches.Patch(color="#9467bd", label="Selection Method")
    p2 = mpatches.Patch(color="#17becf", label="Max Generations")
    ax.legend(handles=[p1, p2], loc="upper right", framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    from dataset import get_default_instance
    from baseline_nn import solve_greedy_nearest_neighbor
    from ga_engine import run_genetic_algorithm, GAConfig

    inst = get_default_instance()
    print("Testing visualizer...")
    base_res = solve_greedy_nearest_neighbor(inst)
    ga_res = run_genetic_algorithm(inst, GAConfig(max_generations=120, seed=42), verbose=False)

    out = Path("outputs/plots")
    out.mkdir(parents=True, exist_ok=True)
    plot_convergence(ga_res.history, out / "convergence_curve.png")
    plot_route_comparison(
        inst.coords,
        inst.demands,
        base_res.routes,
        base_res.total_distance,
        ga_res.best_routes,
        ga_res.best_distance,
        out / "route_comparison.png",
    )
    print("Plots generated successfully!")

