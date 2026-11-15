"""
src/dataset.py
Reproducible 35-customer + 1-depot Capacitated Vehicle Routing Problem (CVRP) generator
and vectorized Euclidean distance matrix precomputation.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class CVRPInstance:
    """Represents a Capacitated Vehicle Routing Problem instance."""
    num_customers: int
    num_nodes: int
    depot_idx: int
    depot_coord: tuple[float, float]
    coords: np.ndarray          # shape (num_nodes, 2)
    demands: np.ndarray         # shape (num_nodes,)
    dist_matrix: np.ndarray     # shape (num_nodes, num_nodes)
    vehicle_capacity: int       # Q
    max_vehicles: int           # K
    seed: int

    @property
    def total_demand(self) -> int:
        return int(np.sum(self.demands))

    def summary(self) -> str:
        return (
            f"CVRP Instance Summary:\n"
            f"  Depot: Node {self.depot_idx} at {self.depot_coord}\n"
            f"  Customers: {self.num_customers} (Nodes 1 to {self.num_customers})\n"
            f"  Total Customer Demand: {self.total_demand} units\n"
            f"  Vehicle Capacity (Q): {self.vehicle_capacity} units\n"
            f"  Max Fleet Limit (K): {self.max_vehicles} vehicles\n"
            f"  Theoretical Minimum Vehicles: {int(np.ceil(self.total_demand / self.vehicle_capacity))}\n"
            f"  Grid Range: [5, 95] x [5, 95] km\n"
            f"  Distance Matrix Shape: {self.dist_matrix.shape}\n"
            f"  Seed: {self.seed}"
        )


def generate_cvrp_dataset(
    seed: int = 42,
    num_customers: int = 35,
    capacity: int = 100,
    max_vehicles: int = 8,
    grid_min: float = 5.0,
    grid_max: float = 95.0,
    demand_min: int = 10,
    demand_max: int = 25,
    depot_coord: tuple[float, float] = (50.0, 50.0),
) -> CVRPInstance:
    """
    Generates a reproducible CVRP dataset:
    - Node 0: Depot at depot_coord (50.0, 50.0) with demand 0
    - Nodes 1..N: Customer locations uniformly distributed in [grid_min, grid_max]^2
      with integer parcel demands in [demand_min, demand_max].
    - Precomputes symmetric (N+1) x (N+1) Euclidean distance matrix.
    """
    num_nodes = num_customers + 1
    rng = np.random.RandomState(seed)

    coords = np.zeros((num_nodes, 2), dtype=float)
    coords[0] = depot_coord
    coords[1:] = rng.uniform(grid_min, grid_max, size=(num_customers, 2))

    demands = np.zeros(num_nodes, dtype=int)
    demands[0] = 0
    # demand_max + 1 for inclusive upper bound [demand_min, demand_max]
    demands[1:] = rng.randint(demand_min, demand_max + 1, size=num_customers)

    # Compute Euclidean distance matrix vectorized
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]  # (36, 36, 2)
    dist_matrix = np.sqrt(np.sum(diff ** 2, axis=-1))

    return CVRPInstance(
        num_customers=num_customers,
        num_nodes=num_nodes,
        depot_idx=0,
        depot_coord=depot_coord,
        coords=coords,
        demands=demands,
        dist_matrix=dist_matrix,
        vehicle_capacity=capacity,
        max_vehicles=max_vehicles,
        seed=seed,
    )


_DEFAULT_INSTANCE: CVRPInstance | None = None


def get_default_instance() -> CVRPInstance:
    """Returns the singleton default CVRP benchmark instance (seed=42)."""
    global _DEFAULT_INSTANCE
    if _DEFAULT_INSTANCE is None:
        _DEFAULT_INSTANCE = generate_cvrp_dataset(seed=42)
    return _DEFAULT_INSTANCE


if __name__ == "__main__":
    instance = get_default_instance()
    print(instance.summary())
    print("\nFirst 5 customer coordinates and demands:")
    for cid in range(1, 6):
        print(f"Customer {cid:2d}: Coord=({instance.coords[cid][0]:.2f}, {instance.coords[cid][1]:.2f}), Demand={instance.demands[cid]}")

