"""
src/ga_engine.py
Core Genetic Algorithm optimization engine for CVRP with elitism,
adaptive diversity injection, convergence tracking, and early stopping.
"""

from dataclasses import dataclass, field
import random
import time
from typing import Literal
import numpy as np

try:
    from src.dataset import CVRPInstance, get_default_instance
    from src.decoder import evaluate_fitness
    from src.operators import (
        initialize_hybrid_population,
        tournament_selection,
        roulette_wheel_selection,
        order_crossover_ox1,
        hybrid_mutation,
        inject_random_immigrants,
    )
except (ImportError, ModuleNotFoundError):
    from dataset import CVRPInstance, get_default_instance
    from decoder import evaluate_fitness
    from operators import (
        initialize_hybrid_population,
        tournament_selection,
        roulette_wheel_selection,
        order_crossover_ox1,
        hybrid_mutation,
        inject_random_immigrants,
    )


@dataclass
class GAConfig:
    """Hyperparameter and operational configuration for CVRP GA engine."""
    pop_size: int = 100
    crossover_rate: float = 0.85
    mutation_rate: float = 0.08
    max_generations: int = 400
    selection_method: Literal["tournament", "roulette"] = "tournament"
    tournament_k: int = 3
    elitism_rate: float = 0.04
    nn_seeding_ratio: float = 0.10
    diversity_threshold: float = 1e-6
    diversity_patience: int = 20
    immigrant_ratio: float = 0.05
    early_stopping_patience: int = 60
    early_stopping_delta: float = 1e-5
    seed: int | None = 42


@dataclass
class GAResult:
    """Encapsulates all results, execution metrics, and trajectories from a GA run."""
    best_chromosome: list[int]
    best_distance: float
    best_fitness: float
    best_routes: list[list[int]]
    num_vehicles: int
    generation_converged: int
    total_generations: int
    execution_time: float
    config: GAConfig
    history: dict[str, list] = field(default_factory=dict)


def run_genetic_algorithm(
    instance: CVRPInstance | None = None,
    config: GAConfig | None = None,
    verbose: bool = False,
) -> GAResult:
    """
    Executes the Genetic Algorithm for CVRP:
    1. Hybrid population initialization (90% random, 10% randomized NN).
    2. Generational loop with parent selection (Tournament / Roulette).
    3. Order Crossover (OX1) & Hybrid Mutation (Swap & Inversion).
    4. Elitism (top 4%) and generational replacement.
    5. Adaptive diversity monitoring with random immigrant injection.
    6. Early stopping if best fitness stalls for 60 consecutive generations.
    """
    if instance is None:
        instance = get_default_instance()
    if config is None:
        config = GAConfig()

    start_time = time.perf_counter()
    rng = random.Random(config.seed)

    # 1. Initialize Hybrid Population
    population = initialize_hybrid_population(
        pop_size=config.pop_size,
        num_customers=instance.num_customers,
        dist_matrix=instance.dist_matrix,
        nn_ratio=config.nn_seeding_ratio,
        rng=rng,
    )

    # Evaluation helper
    def _eval_individual(chrom: list[int]):
        return evaluate_fitness(
            chrom,
            instance.dist_matrix,
            instance.demands,
            instance.vehicle_capacity,
            instance.max_vehicles,
        )

    # Evaluate initial population
    evaluations = [_eval_individual(chrom) for chrom in population]
    # Each evaluation: (total_distance, total_penalty, routes, fitness)
    distances = [e[0] for e in evaluations]
    fitnesses = [e[3] for e in evaluations]

    # Global best tracking
    best_idx = int(np.argmax(fitnesses))
    global_best_fitness = fitnesses[best_idx]
    global_best_dist = distances[best_idx]
    global_best_routes = evaluations[best_idx][2]
    global_best_chrom = population[best_idx].copy()
    generation_converged = 0

    # History logging
    history: dict[str, list] = {
        "generation": [],
        "best_distance": [],
        "avg_distance": [],
        "best_fitness": [],
        "diversity_std": [],
        "injections": [],
    }

    # Tracking counters
    stagnation_counter = 0
    no_improve_counter = 0
    elitism_count = max(1, int(round(config.elitism_rate * config.pop_size)))

    for gen in range(config.max_generations + 1):
        # Current generation metrics
        curr_best_idx = int(np.argmax(fitnesses))
        curr_best_fit = fitnesses[curr_best_idx]
        curr_best_dist = distances[curr_best_idx]
        curr_avg_dist = float(np.mean(distances))
        diversity_std = float(np.std(fitnesses))

        # Check for new global best
        if curr_best_fit > global_best_fitness:
            global_best_fitness = curr_best_fit
            global_best_dist = curr_best_dist
            global_best_routes = evaluations[curr_best_idx][2]
            global_best_chrom = population[curr_best_idx].copy()
            generation_converged = gen

        history["generation"].append(gen)
        history["best_distance"].append(global_best_dist)
        history["avg_distance"].append(curr_avg_dist)
        history["best_fitness"].append(global_best_fitness)
        history["diversity_std"].append(diversity_std)

        if verbose and (gen % 50 == 0 or gen == config.max_generations):
            print(
                f"Gen {gen:3d} | Best Dist: {global_best_dist:7.2f} km | "
                f"Avg Dist: {curr_avg_dist:7.2f} km | Best Fit: {global_best_fitness:.8f} | "
                f"Std: {diversity_std:.2e} | Routes: {len(global_best_routes)}"
            )

        # Check early stopping termination condition:
        # Fails to improve by at least early_stopping_delta (1e-5) over 60 consecutive generations
        if gen >= config.early_stopping_patience:
            window_improvement = (
                history["best_fitness"][gen]
                - history["best_fitness"][gen - config.early_stopping_patience]
            )
            if window_improvement < config.early_stopping_delta:
                if verbose:
                    print(
                        f"Early stopping triggered at generation {gen} "
                        f"(improvement over {config.early_stopping_patience} gens was {window_improvement:.2e} < {config.early_stopping_delta:.2e})."
                    )
                break

        if gen == config.max_generations:
            break

        # Check Diversity Maintenance Condition
        if diversity_std < config.diversity_threshold:
            stagnation_counter += 1
            if stagnation_counter >= config.diversity_patience:
                # Inject 5% random immigrants
                population, fitnesses = inject_random_immigrants(
                    population, fitnesses, immigrant_ratio=config.immigrant_ratio, rng=rng
                )
                # Re-evaluate immigrants
                for i in range(len(population)):
                    if fitnesses[i] == 0.0:
                        td, tp, rt, fit = _eval_individual(population[i])
                        distances[i] = td
                        fitnesses[i] = fit
                        evaluations[i] = (td, tp, rt, fit)
                history["injections"].append(gen)
                stagnation_counter = 0
                if verbose:
                    print(f"  [Diversity Injection] Injected random immigrants at gen {gen}.")
        else:
            stagnation_counter = 0

        # Create Next Generation
        # 1. Elitism: sort and retain top elitism_count individuals
        sorted_indices = sorted(range(config.pop_size), key=lambda i: fitnesses[i], reverse=True)
        next_population: list[list[int]] = [population[i].copy() for i in sorted_indices[:elitism_count]]
        next_evals = [evaluations[i] for i in sorted_indices[:elitism_count]]

        # Selection function
        def _select_parent() -> list[int]:
            if config.selection_method == "tournament":
                return tournament_selection(population, fitnesses, k=config.tournament_k, rng=rng)
            else:
                return roulette_wheel_selection(population, fitnesses, rng=rng)

        # 2. Fill remaining slots with crossover and mutation
        while len(next_population) < config.pop_size:
            p1 = _select_parent()
            p2 = _select_parent()

            c1, c2 = order_crossover_ox1(p1, p2, pc=config.crossover_rate, rng=rng)

            c1 = hybrid_mutation(c1, pm=config.mutation_rate, rng=rng)
            c2 = hybrid_mutation(c2, pm=config.mutation_rate, rng=rng)

            next_population.append(c1)
            next_evals.append(_eval_individual(c1))

            if len(next_population) < config.pop_size:
                next_population.append(c2)
                next_evals.append(_eval_individual(c2))

        population = next_population
        evaluations = next_evals
        distances = [e[0] for e in evaluations]
        fitnesses = [e[3] for e in evaluations]

    exec_time = time.perf_counter() - start_time

    return GAResult(
        best_chromosome=global_best_chrom,
        best_distance=global_best_dist,
        best_fitness=global_best_fitness,
        best_routes=global_best_routes,
        num_vehicles=len(global_best_routes),
        generation_converged=generation_converged,
        total_generations=len(history["generation"]) - 1,
        execution_time=exec_time,
        config=config,
        history=history,
    )


if __name__ == "__main__":
    inst = get_default_instance()
    cfg = GAConfig(max_generations=100, seed=42)
    print("Running initial test run of GA Engine (100 gens)...")
    res = run_genetic_algorithm(inst, cfg, verbose=True)
    print(f"\nCompleted in {res.execution_time:.3f} seconds.")
    print(f"Best Distance: {res.best_distance:.2f} km across {res.num_vehicles} vehicles.")
    print(f"Converged at Generation: {res.generation_converged}")
