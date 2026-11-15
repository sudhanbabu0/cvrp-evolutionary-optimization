"""
src/operators.py
Genetic operators for CVRP: Hybrid Initialization, Selection (Tournament & Roulette),
Order Crossover (OX1), Hybrid Mutation (Swap & Inversion), and Diversity Injection.
"""

import random
from typing import Sequence
import numpy as np


def generate_nearest_neighbor_tour(
    start_customer: int,
    num_customers: int,
    dist_matrix: np.ndarray,
    rng: random.Random,
) -> list[int]:
    """
    Generates a full permutation of customer IDs [1..N] using randomized nearest-neighbor
    heuristics starting at start_customer.
    """
    unvisited = set(range(1, num_customers + 1))
    unvisited.remove(start_customer)
    tour = [start_customer]
    current = start_customer

    while unvisited:
        # Find closest unvisited customer; add minor random perturbation if tied
        next_customer = min(unvisited, key=lambda c: dist_matrix[current, c])
        tour.append(next_customer)
        unvisited.remove(next_customer)
        current = next_customer

    return tour


def initialize_hybrid_population(
    pop_size: int,
    num_customers: int,
    dist_matrix: np.ndarray,
    nn_ratio: float = 0.10,
    rng: random.Random | None = None,
) -> list[list[int]]:
    """
    Hybrid Population Initialization:
    - (1 - nn_ratio) * 100% uniform random permutations
    - (nn_ratio) * 100% randomized Nearest-Neighbor permutations seeded with random start nodes.
    Ensures both high initial solution quality and broad structural diversity.
    """
    if rng is None:
        rng = random.Random()

    population: list[list[int]] = []
    num_nn = max(1, int(round(pop_size * nn_ratio)))
    num_random = pop_size - num_nn

    # 1. Randomized Nearest-Neighbor chromosomes
    customer_pool = list(range(1, num_customers + 1))
    for _ in range(num_nn):
        start_node = rng.choice(customer_pool)
        nn_tour = generate_nearest_neighbor_tour(start_node, num_customers, dist_matrix, rng)
        population.append(nn_tour)

    # 2. Uniform random permutation chromosomes
    base = list(range(1, num_customers + 1))
    for _ in range(num_random):
        chrom = base.copy()
        rng.shuffle(chrom)
        population.append(chrom)

    return population


def tournament_selection(
    population: Sequence[list[int]],
    fitnesses: Sequence[float],
    k: int = 3,
    rng: random.Random | None = None,
) -> list[int]:
    """
    Tournament Selection (k = 3 default):
    Picks k random candidates from the population and returns the one with the highest fitness.
    """
    if rng is None:
        rng = random.Random()
    selected_indices = rng.sample(range(len(population)), k)
    best_idx = max(selected_indices, key=lambda idx: fitnesses[idx])
    return population[best_idx].copy()


def roulette_wheel_selection(
    population: Sequence[list[int]],
    fitnesses: Sequence[float],
    rng: random.Random | None = None,
) -> list[int]:
    """
    Fitness-Proportionate Roulette Wheel Selection:
    Selects an individual with probability proportional to its fitness score.
    """
    if rng is None:
        rng = random.Random()
    total_fit = sum(fitnesses)
    if total_fit <= 0:
        return rng.choice(population).copy()

    pick = rng.uniform(0.0, total_fit)
    current = 0.0
    for chrom, fit in zip(population, fitnesses):
        current += fit
        if current >= pick:
            return chrom.copy()
    return population[-1].copy()


def order_crossover_ox1(
    parent1: Sequence[int],
    parent2: Sequence[int],
    pc: float = 0.85,
    rng: random.Random | None = None,
) -> tuple[list[int], list[int]]:
    """
    Order Crossover (OX1):
    Constructs offspring by preserving a contiguous slice of relative customer orders
    from parent 1 and filling remaining positions from parent 2 in circular order.
    Returns two offspring chromosomes.
    """
    if rng is None:
        rng = random.Random()

    if rng.random() > pc:
        return list(parent1), list(parent2)

    n = len(parent1)
    if n < 3:
        return list(parent1), list(parent2)

    # Pick two cut points i < j
    idx1, idx2 = sorted(rng.sample(range(n), 2))

    def _ox1_single(p1: Sequence[int], p2: Sequence[int]) -> list[int]:
        child = [0] * n
        # Copy slice from p1
        child[idx1 : idx2 + 1] = p1[idx1 : idx2 + 1]
        copied_set = set(child[idx1 : idx2 + 1])

        # Fill remaining positions circularly from p2 starting at idx2 + 1
        p2_ptr = (idx2 + 1) % n
        child_ptr = (idx2 + 1) % n

        while child_ptr != idx1:
            candidate = p2[p2_ptr]
            p2_ptr = (p2_ptr + 1) % n
            if candidate not in copied_set:
                child[child_ptr] = candidate
                child_ptr = (child_ptr + 1) % n

        return child

    child1 = _ox1_single(parent1, parent2)
    child2 = _ox1_single(parent2, parent1)
    return child1, child2


def swap_mutation(chromosome: list[int], rng: random.Random | None = None) -> list[int]:
    """Exchanges two customer locations at random indices (inter-route/position exchange)."""
    if rng is None:
        rng = random.Random()
    n = len(chromosome)
    if n < 2:
        return chromosome
    i, j = rng.sample(range(n), 2)
    chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
    return chromosome


def inversion_mutation(chromosome: list[int], rng: random.Random | None = None) -> list[int]:
    """Reverses a contiguous sub-segment of customers (2-opt path untangling)."""
    if rng is None:
        rng = random.Random()
    n = len(chromosome)
    if n < 2:
        return chromosome
    i, j = sorted(rng.sample(range(n), 2))
    chromosome[i : j + 1] = chromosome[i : j + 1][::-1]
    return chromosome


def hybrid_mutation(
    chromosome: list[int],
    pm: float = 0.08,
    rng: random.Random | None = None,
) -> list[int]:
    """
    Hybrid Mutation:
    Applies mutation with probability pm.
    Uses 50/50 balance between Swap Mutation and Inversion Mutation.
    """
    if rng is None:
        rng = random.Random()

    mutated = chromosome.copy()
    if rng.random() < pm:
        if rng.random() < 0.5:
            mutated = swap_mutation(mutated, rng)
        else:
            mutated = inversion_mutation(mutated, rng)

    return mutated


def inject_random_immigrants(
    population: list[list[int]],
    fitnesses: list[float],
    immigrant_ratio: float = 0.05,
    rng: random.Random | None = None,
) -> tuple[list[list[int]], list[float]]:
    """
    Replaces the worst immigrant_ratio * 100% individuals in the population
    with completely fresh uniform random permutations to recover genetic diversity.
    """
    if rng is None:
        rng = random.Random()

    n_pop = len(population)
    num_immigrants = max(1, int(round(n_pop * immigrant_ratio)))
    n_customers = len(population[0])

    # Find indices of worst individuals
    sorted_indices = sorted(range(n_pop), key=lambda i: fitnesses[i])
    worst_indices = sorted_indices[:num_immigrants]

    base = list(range(1, n_customers + 1))
    for idx in worst_indices:
        immigrant = base.copy()
        rng.shuffle(immigrant)
        population[idx] = immigrant
        # Fitness will be re-evaluated externally or set to 0 placeholder
        fitnesses[idx] = 0.0

    return population, fitnesses
