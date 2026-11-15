"""
src/decoder.py
Greedy capacity-splitting decoder and penalized fitness evaluation for CVRP.
"""

from typing import Sequence
import numpy as np


def decode_routes(
    chromosome: Sequence[int],
    demands: np.ndarray,
    capacity: int,
) -> list[list[int]]:
    """
    Greedy Capacity-Splitting Decoder:
    Iterates through the 1D customer permutation chromosome and assigns customers
    to the current vehicle route until adding the next customer exceeds vehicle capacity Q.
    When capacity would be exceeded, the vehicle returns to Depot 0 and a new vehicle route begins.

    Returns:
        List of routes, where each route is an ordered list starting and ending at 0:
        e.g., [[0, c1, c2, ..., 0], [0, ck, ..., 0], ...]
    """
    routes: list[list[int]] = []
    current_route: list[int] = [0]
    current_load: int = 0

    for customer in chromosome:
        cust_demand = int(demands[customer])
        if current_load + cust_demand <= capacity:
            current_route.append(int(customer))
            current_load += cust_demand
        else:
            # Seal current route back to depot
            current_route.append(0)
            routes.append(current_route)
            # Start fresh vehicle route
            current_route = [0, int(customer)]
            current_load = cust_demand

    if len(current_route) > 1:
        current_route.append(0)
        routes.append(current_route)

    return routes


def calculate_route_distance(route: Sequence[int], dist_matrix: np.ndarray) -> float:
    """Calculates total Euclidean travel distance for a single route [0, c1, ..., cm, 0]."""
    if len(route) < 2:
        return 0.0
    dist = 0.0
    for idx in range(len(route) - 1):
        dist += float(dist_matrix[route[idx], route[idx + 1]])
    return dist


def calculate_route_demand(route: Sequence[int], demands: np.ndarray) -> int:
    """Calculates cumulative customer demand on a route (excluding depot 0)."""
    return int(sum(demands[node] for node in route if node != 0))


def evaluate_fitness(
    chromosome: Sequence[int],
    dist_matrix: np.ndarray,
    demands: np.ndarray,
    capacity: int,
    max_vehicles: int = 8,
    lambda_penalty: float = 500.0,
) -> tuple[float, float, list[list[int]], float]:
    """
    Evaluates a candidate chromosome:
    1. Decodes chromosome into vehicle routes using greedy capacity splitting.
    2. Computes cumulative travel distance across all active vehicles.
    3. Calculates penalties for any capacity violation or exceeding fleet limit K.
    4. Computes scalar fitness score F(S) = 1.0 / (1.0 + C(S)).

    Returns:
        (total_distance, total_penalty, routes, fitness)
    """
    routes = decode_routes(chromosome, demands, capacity)

    total_distance = 0.0
    total_penalty = 0.0

    for route in routes:
        # Distance calculation
        for i in range(len(route) - 1):
            total_distance += float(dist_matrix[route[i], route[i + 1]])

        # Capacity violation check
        route_load = sum(int(demands[node]) for node in route if node != 0)
        if route_load > capacity:
            total_penalty += lambda_penalty * (route_load - capacity)

    # Fleet size constraint check
    num_vehicles = len(routes)
    if num_vehicles > max_vehicles:
        # Severe penalty for violating available fleet limit K = 8
        excess_vehicles = num_vehicles - max_vehicles
        total_penalty += lambda_penalty * (excess_vehicles * capacity)

    total_cost = total_distance + total_penalty
    fitness = 1.0 / (1.0 + total_cost)

    return total_distance, total_penalty, routes, fitness


if __name__ == "__main__":
    from dataset import get_default_instance

    inst = get_default_instance()
    # Test with identity permutation
    sample_chrom = list(range(1, inst.num_customers + 1))
    tdist, tpen, routes, fit = evaluate_fitness(
        sample_chrom, inst.dist_matrix, inst.demands, inst.vehicle_capacity, inst.max_vehicles
    )
    print(f"Sample Chromosome Evaluation:")
    print(f"  Vehicles Used: {len(routes)} / {inst.max_vehicles}")
    print(f"  Total Distance: {tdist:.2f} km")
    print(f"  Total Penalty: {tpen:.2f}")
    print(f"  Fitness F(S): {fit:.8f}")
    print(f"  First Route: {routes[0]} (demand={calculate_route_demand(routes[0], inst.demands)})")

