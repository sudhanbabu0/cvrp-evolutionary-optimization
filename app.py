"""
cvrp_evolutionary_project/app.py
Interactive Web Dashboard & Live Visualization Server for CVRP Evolutionary Computing.
Powered by Flask, Tailwind CSS, HTML5 Canvas, and Chart.js.
Supports Scenario Persistence (Save/Load/Export), Backend GA Solver, and Custom Fleet Routing.
"""

import os
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.dataset import get_default_instance, generate_cvrp_dataset, CVRPInstance
from src.decoder import calculate_route_demand, calculate_route_distance
from src.baseline_nn import solve_greedy_nearest_neighbor
from src.ga_engine import run_genetic_algorithm, GAConfig
import numpy as np

app = Flask(
    __name__,
    template_folder=str(project_root / "templates"),
    static_folder=str(project_root / "outputs" / "plots")
)

# Storage directories for backend persistence
SCENARIOS_DIR = project_root / "saved_scenarios"
SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)

SOLUTIONS_DIR = project_root / "saved_solutions"
SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)

# Cache default instance
instance = get_default_instance()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/instance", methods=["GET"])
def get_instance_data():
    """Returns dataset nodes, coordinates, and demands for the interactive canvas."""
    customers = []
    for c_id in range(1, instance.num_nodes):
        dx = instance.coords[c_id][0] - instance.coords[0][0]
        dy = instance.coords[c_id][1] - instance.coords[0][1]
        dist_depot = float(np.sqrt(dx * dx + dy * dy))
        angle = float((np.arctan2(dy, dx) * 180 / np.pi + 360) % 360)

        customers.append({
            "id": c_id,
            "x": round(float(instance.coords[c_id][0]), 2),
            "y": round(float(instance.coords[c_id][1]), 2),
            "demand": int(instance.demands[c_id]),
            "distToDepot": round(dist_depot, 1),
            "angle": round(angle, 1),
        })

    return jsonify({
        "depot": {"id": 0, "x": float(instance.coords[0][0]), "y": float(instance.coords[0][1])},
        "customers": customers,
        "num_customers": instance.num_customers,
        "vehicle_capacity": instance.vehicle_capacity,
        "max_fleet_limit": instance.max_vehicles,
        "total_demand": instance.total_demand,
        "seed": instance.seed,
    })


@app.route("/api/run-baseline", methods=["POST"])
def run_baseline():
    """Runs deterministic Greedy Nearest-Neighbor CVRP solver."""
    res = solve_greedy_nearest_neighbor(instance)
    return jsonify({
        "status": "success",
        "solver": "Greedy Nearest-Neighbor Heuristic",
        "total_distance": round(res.total_distance, 2),
        "num_vehicles": res.num_vehicles,
        "execution_time_ms": round(res.execution_time * 1000, 3),
        "routes": res.routes,
        "route_demands": res.route_demands,
        "route_distances": [round(d, 2) for d in res.route_distances],
    })


@app.route("/api/run-ga", methods=["POST"])
def run_ga():
    """Runs Genetic Algorithm with custom or default hyperparameters."""
    data = request.get_json(silent=True) or {}

    pop_size = int(data.get("pop_size", 100))
    mutation_rate = float(data.get("mutation_rate", 0.08))
    crossover_rate = float(data.get("crossover_rate", 0.85))
    max_generations = int(data.get("max_generations", 200))
    selection_method = str(data.get("selection_method", "tournament"))
    seed = int(data.get("seed", 42))

    cfg = GAConfig(
        pop_size=pop_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        max_generations=max_generations,
        selection_method=selection_method,
        seed=seed,
    )

    start_time = time.perf_counter()
    res = run_genetic_algorithm(instance, config=cfg, verbose=False)
    runtime = time.perf_counter() - start_time

    route_demands = [calculate_route_demand(r, instance.demands) for r in res.best_routes]
    route_distances = [round(calculate_route_distance(r, instance.dist_matrix), 2) for r in res.best_routes]

    return jsonify({
        "status": "success",
        "solver": "Genetic Algorithm",
        "total_distance": round(res.best_distance, 2),
        "best_fitness": round(res.best_fitness, 8),
        "num_vehicles": res.num_vehicles,
        "generation_converged": res.generation_converged,
        "total_generations": res.total_generations,
        "execution_time_sec": round(runtime, 3),
        "routes": res.best_routes,
        "route_demands": route_demands,
        "route_distances": route_distances,
        "history": {
            "generation": res.history["generation"],
            "best_distance": [round(d, 2) for d in res.history["best_distance"]],
            "avg_distance": [round(d, 2) for d in res.history["avg_distance"]],
            "best_fitness": res.history["best_fitness"],
        },
    })


@app.route("/api/best-solution", methods=["GET"])
def get_best_solution():
    """Returns the precomputed global best solution (727.17 km) from best_routes.json."""
    best_json_path = project_root / "outputs" / "best_routes.json"
    if best_json_path.exists():
        with open(best_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"status": "success", "data": data})
    else:
        return jsonify({"status": "error", "message": "best_routes.json not found"}), 404


# =========================================================================
# BACKEND PERSISTENCE: Save, Load, List, and Delete Scenarios & Solutions
# =========================================================================

def _sanitize_name(name: str) -> str:
    """Sanitizes user input filename to prevent directory traversal."""
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name.strip())
    return cleaned[:80] or "cvrp_scenario"


@app.route("/api/save", methods=["POST"])
def save_scenario():
    """
    Saves complete scenario, customer demands, warehouse distances,
    routes, and optimization metrics to backend storage.
    """
    try:
        data = request.get_json(silent=True) or {}
        raw_name = data.get("scenario_name", "").strip() or f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        clean_name = _sanitize_name(raw_name)
        if not clean_name.endswith(".json"):
            clean_name += ".json"

        filepath = SCENARIOS_DIR / clean_name
        data["saved_at"] = datetime.now().isoformat()
        data["filename"] = clean_name

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return jsonify({
            "status": "success",
            "message": f"Successfully saved scenario '{clean_name}' on server disk.",
            "filename": clean_name,
            "saved_at": data["saved_at"],
            "size_bytes": filepath.stat().st_size
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/saved-items", methods=["GET"])
def list_saved_items():
    """Lists all saved scenarios and plans stored on the server backend."""
    try:
        items = []
        for p in sorted(SCENARIOS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = json.load(f)
                num_sites = len(content.get("customers", []))
                routes = content.get("routes", [])
                metrics = content.get("metrics", {})
                items.append({
                    "filename": p.name,
                    "scenario_name": content.get("scenario_name", p.stem),
                    "saved_at": content.get("saved_at", datetime.fromtimestamp(p.stat().st_mtime).isoformat()),
                    "num_sites": num_sites,
                    "num_routes": len(routes),
                    "total_distance": metrics.get("ga_distance") or metrics.get("baseline_distance") or "N/A",
                    "fleet_limit": content.get("fleet_limit", 8),
                    "size_bytes": p.stat().st_size
                })
            except Exception:
                continue

        return jsonify({"status": "success", "items": items})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/load/<path:filename>", methods=["GET"])
def load_scenario(filename: str):
    """Loads a specific saved scenario JSON from the backend."""
    try:
        safe_name = _sanitize_name(filename)
        if not safe_name.endswith(".json"):
            safe_name += ".json"
        filepath = SCENARIOS_DIR / safe_name

        if not filepath.exists():
            return jsonify({"status": "error", "message": f"File '{safe_name}' not found"}), 404

        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)

        return jsonify({"status": "success", "data": content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/delete/<path:filename>", methods=["DELETE", "POST"])
def delete_scenario(filename: str):
    """Deletes a saved scenario from the backend."""
    try:
        safe_name = _sanitize_name(filename)
        if not safe_name.endswith(".json"):
            safe_name += ".json"
        filepath = SCENARIOS_DIR / safe_name

        if filepath.exists():
            filepath.unlink()
            return jsonify({"status": "success", "message": f"File '{safe_name}' deleted successfully."})
        else:
            return jsonify({"status": "error", "message": f"File '{safe_name}' not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 70)
    print("  CVRP EVOLUTIONARY OPTIMIZATION INTERACTIVE WEB SERVER")
    print(f"  Running on: http://0.0.0.0:{port}")
    print(f"  Scenario Storage Directory: {SCENARIOS_DIR}")
    print("=" * 70)
    app.run(host="0.0.0.0", port=port, debug=False)
