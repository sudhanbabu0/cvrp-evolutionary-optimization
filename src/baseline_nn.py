"""
src/baseline_nn.py
Deterministic Greedy Nearest-Neighbor CVRP heuristic for benchmarking against GA.
"""

from dataclasses import dataclass
import time
import numpy as np

try:
    from src.dataset import CVRPInstance, get_default_instance
    from src.decoder import calculate_route_distance, calculate_route_demand
except (ImportError, ModuleNotFoundError):
    from dataset import CVRPInstance, get_default_instance
    from decoder import calculate_route_distance, calculate_route_demand


@dataclass
class BaselineResult:
    """Holds results from deterministic Greedy Nearest-Neighbor CVRP solver."""
    routes: list[list[int]]
    total_distance: float
    num_vehicles: int
    execution_time: float
    route_demands: list[int]
    route_distances: list[float]


def solve_greedy_nearest_neighbor(instance: CVRPInstance | None = None) -> BaselineResult:
    """
    Deterministic Greedy Nearest-Neighbor CVRP Heuristic:
    1. Dispatches vehicle from Depot 0 with capacity Q = 100.
    2. Greedily visits the closest unvisited customer whose demand fits in remaining capacity.
    3. When no feasible unvisited customer fits, the vehicle returns to depot 0.
    4. Dispatches subsequent vehicles until all N = 35 customers are served.
    5. Returns route sequence, distance, fleet count, and runtime.
    """
    if instance is None:
        instance = get_default_instance()

    start_time = time.perf_counter()

    unvisited = set(range(1, instance.num_customers + 1))
    routes: list[list[int]] = []
    route_demands: list[int] = []
    route_distances: list[float] = []

    while unvisited:
        current_route = [0]
        current_node = 0
        remaining_capacity = instance.vehicle_capacity

        while True:
            # Candidates that fit within remaining vehicle capacity
            feasible_candidates = [
                c for c in unvisited if instance.demands[c] <= remaining_capacity
            ]

            if not feasible_candidates:
                # No more customers can fit into current vehicle
                break

            # Choose customer with minimum Euclidean distance from current_node
            # Break distance ties deterministically with node ID
            best_customer = min(
                feasible_candidates,
                key=lambda c: (instance.dist_matrix[current_node, c], c),
            )

            current_route.append(best_customer)
            remaining_capacity -= int(instance.demands[best_customer])
            current_node = best_customer
            unvisited.remove(best_customer)

        # Vehicle returns to depot
        current_route.append(0)
        routes.append(current_route)
        route_demands.append(calculate_route_demand(current_route, instance.demands))
        route_distances.append(calculate_route_distance(current_route, instance.dist_matrix))

    exec_time = time.perf_counter() - start_time
    total_distance = sum(route_distances)

    return BaselineResult(
        routes=routes,
        total_distance=total_distance,
        num_vehicles=len(routes),
        execution_time=exec_time,
        route_demands=route_demands,
        route_distances=route_distances,
    )


if __name__ == "__main__":
    inst = get_default_instance()
    res = solve_greedy_nearest_neighbor(inst)

    print("=== Greedy Nearest-Neighbor CVRP Baseline Results ===")
    print(f"Total Fleet Distance : {res.total_distance:.2f} km")
    print(f"Vehicles Utilized    : {res.num_vehicles} (Fleet Limit K = {inst.max_vehicles})")
    print(f"Execution Time       : {res.execution_time * 1000:.3f} ms ({res.execution_time:.6f} s)")
    print(f"\nRoute Breakdown ({res.num_vehicles} routes):")
    for idx, (route, dem, dist) in enumerate(zip(res.routes, res.route_demands, res.route_distances), 1):
        cust_str = " -> ".join(str(n) for n in route)
        print(f"  Route {idx} (Demand: {dem:3d}/{inst.vehicle_capacity}, Dist: {dist:6.2f} km): {cust_str}")
