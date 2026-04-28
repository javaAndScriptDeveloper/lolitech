"""
Example demonstrations of ACO algorithm with different configurations
"""

import numpy as np
from ant_colony_optimization import AntColonyOptimization, create_random_tsp, plot_tour
import matplotlib.pyplot as plt
import os

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def compare_parameters():
    """
    Compare ACO performance with different parameter settings
    """
    print("=" * 70)
    print("Comparing ACO with Different Parameter Settings")
    print("=" * 70)
    
    # Create a fixed TSP instance
    n_cities = 15
    distances, cities = create_random_tsp(n_cities, seed=123)
    
    # Different configurations to test
    configs = [
        {
            'name': 'Balanced',
            'alpha': 1.0,
            'beta': 2.0,
            'rho': 0.5,
            'elite_ants': 3
        },
        {
            'name': 'High Pheromone Importance',
            'alpha': 2.0,
            'beta': 1.0,
            'rho': 0.5,
            'elite_ants': 3
        },
        {
            'name': 'High Distance Importance',
            'alpha': 1.0,
            'beta': 5.0,
            'rho': 0.5,
            'elite_ants': 3
        },
        {
            'name': 'Fast Evaporation',
            'alpha': 1.0,
            'beta': 2.0,
            'rho': 0.8,
            'elite_ants': 3
        },
        {
            'name': 'Slow Evaporation',
            'alpha': 1.0,
            'beta': 2.0,
            'rho': 0.2,
            'elite_ants': 3
        },
        {
            'name': 'More Elite Ants',
            'alpha': 1.0,
            'beta': 2.0,
            'rho': 0.5,
            'elite_ants': 10
        }
    ]
    
    results = []
    
    for config in configs:
        print(f"\nTesting configuration: {config['name']}")
        print(f"  α={config['alpha']}, β={config['beta']}, "
              f"ρ={config['rho']}, elite={config['elite_ants']}")
        
        aco = AntColonyOptimization(
            distances=distances,
            n_ants=n_cities,
            n_iterations=50,
            alpha=config['alpha'],
            beta=config['beta'],
            rho=config['rho'],
            Q=100.0,
            elite_ants=config['elite_ants']
        )
        
        best_path, best_length = aco.optimize(verbose=False)
        
        results.append({
            'name': config['name'],
            'best_length': best_length,
            'history': aco.history
        })
        
        print(f"  Result: Best length = {best_length:.2f}")
    
    # Plot comparison
    plt.figure(figsize=(14, 8))
    
    for result in results:
        iterations = [h['iteration'] for h in result['history']]
        best_lengths = [h['best_length'] for h in result['history']]
        plt.plot(iterations, best_lengths, label=result['name'], linewidth=2)
    
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Best Path Length', fontsize=12)
    plt.title('ACO Performance with Different Parameters', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'parameter_comparison.png'), dpi=150, bbox_inches='tight')

    print("\n" + "=" * 70)
    print("Results Summary:")
    print("=" * 70)
    for result in results:
        print(f"{result['name']:30s}: {result['best_length']:8.2f}")
    print(f"\nComparison plot saved to {os.path.join(OUTPUT_DIR, 'parameter_comparison.png')}")


def test_scalability():
    """
    Test ACO performance with different problem sizes
    """
    print("\n" + "=" * 70)
    print("Testing ACO Scalability")
    print("=" * 70)
    
    city_sizes = [10, 15, 20, 25, 30]
    results = []
    
    for n_cities in city_sizes:
        print(f"\nSolving TSP with {n_cities} cities...")
        
        distances, cities = create_random_tsp(n_cities, seed=42)
        
        aco = AntColonyOptimization(
            distances=distances,
            n_ants=n_cities,
            n_iterations=50,
            alpha=1.0,
            beta=2.0,
            rho=0.5,
            Q=100.0,
            elite_ants=5
        )
        
        best_path, best_length = aco.optimize(verbose=False)
        
        results.append({
            'n_cities': n_cities,
            'best_length': best_length,
            'final_avg': aco.history[-1]['avg_length']
        })
        
        print(f"  Best length: {best_length:.2f}")
        print(f"  Final avg: {aco.history[-1]['avg_length']:.2f}")
    
    # Plot scalability
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    n_cities_list = [r['n_cities'] for r in results]
    best_lengths = [r['best_length'] for r in results]
    
    ax1.plot(n_cities_list, best_lengths, 'o-', linewidth=2, markersize=8, color='blue')
    ax1.set_xlabel('Number of Cities', fontsize=12)
    ax1.set_ylabel('Best Path Length', fontsize=12)
    ax1.set_title('Scalability: Solution Quality', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Compute relative complexity
    complexity = [length / n for length, n in zip(best_lengths, n_cities_list)]
    ax2.plot(n_cities_list, complexity, 's-', linewidth=2, markersize=8, color='green')
    ax2.set_xlabel('Number of Cities', fontsize=12)
    ax2.set_ylabel('Avg Distance per City', fontsize=12)
    ax2.set_title('Scalability: Normalized Complexity', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'scalability_analysis.png'), dpi=150, bbox_inches='tight')

    print(f"\nScalability plot saved to {os.path.join(OUTPUT_DIR, 'scalability_analysis.png')}")


def demonstrate_convergence_behavior():
    """
    Demonstrate different convergence behaviors
    """
    print("\n" + "=" * 70)
    print("Demonstrating Convergence Behaviors")
    print("=" * 70)
    
    n_cities = 20
    distances, cities = create_random_tsp(n_cities, seed=999)
    
    scenarios = [
        {
            'name': 'Quick Convergence (High α, Low ρ)',
            'alpha': 3.0,
            'beta': 1.0,
            'rho': 0.2
        },
        {
            'name': 'Exploration Focus (Low α, High β)',
            'alpha': 0.5,
            'beta': 5.0,
            'rho': 0.5
        },
        {
            'name': 'Balanced Approach',
            'alpha': 1.0,
            'beta': 2.0,
            'rho': 0.5
        }
    ]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, scenario in enumerate(scenarios):
        print(f"\n{scenario['name']}")
        
        aco = AntColonyOptimization(
            distances=distances,
            n_ants=n_cities,
            n_iterations=100,
            alpha=scenario['alpha'],
            beta=scenario['beta'],
            rho=scenario['rho'],
            Q=100.0,
            elite_ants=3
        )
        
        best_path, best_length = aco.optimize(verbose=False)
        
        iterations = [h['iteration'] for h in aco.history]
        best_lengths = [h['best_length'] for h in aco.history]
        avg_lengths = [h['avg_length'] for h in aco.history]
        
        axes[idx].plot(iterations, best_lengths, 'b-', label='Best', linewidth=2)
        axes[idx].plot(iterations, avg_lengths, 'r--', label='Average', linewidth=1.5, alpha=0.7)
        axes[idx].set_xlabel('Iteration')
        axes[idx].set_ylabel('Path Length')
        axes[idx].set_title(scenario['name'], fontweight='bold')
        axes[idx].legend()
        axes[idx].grid(True, alpha=0.3)
        
        print(f"  Final best: {best_length:.2f}")
        print(f"  Improvement: {aco.history[0]['best_length'] - best_length:.2f}")
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'convergence_behaviors.png'), dpi=150, bbox_inches='tight')

    print(f"\nConvergence behavior plot saved to {os.path.join(OUTPUT_DIR, 'convergence_behaviors.png')}")


def analyze_pheromone_dynamics():
    """
    Analyze how pheromone levels change over time
    """
    print("\n" + "=" * 70)
    print("Analyzing Pheromone Dynamics")
    print("=" * 70)
    
    n_cities = 10
    distances, cities = create_random_tsp(n_cities, seed=555)
    
    aco = AntColonyOptimization(
        distances=distances,
        n_ants=n_cities,
        n_iterations=50,
        alpha=1.0,
        beta=2.0,
        rho=0.5,
        Q=100.0,
        elite_ants=3
    )
    
    # Store pheromone snapshots
    snapshots = []
    iterations_to_capture = [0, 10, 25, 49]
    
    for iteration in range(50):
        # Construct solutions
        all_paths = []
        all_lengths = []
        
        for ant in range(aco.n_ants):
            start_city = ant % aco.n_cities
            path, length = aco._construct_solution(start_city)
            all_paths.append(path)
            all_lengths.append(length)
            
            if length < aco.best_length:
                aco.best_length = length
                aco.best_path = path.copy()
        
        # Capture snapshot
        if iteration in iterations_to_capture:
            snapshots.append(aco.pheromones.copy())
        
        # Update pheromones
        aco._update_pheromones(all_paths, all_lengths)
    
    # Plot pheromone evolution
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for idx, (snapshot, iter_num) in enumerate(zip(snapshots, iterations_to_capture)):
        im = axes[idx].imshow(snapshot, cmap='hot', interpolation='nearest')
        axes[idx].set_title(f'Iteration {iter_num}', fontweight='bold')
        axes[idx].set_xlabel('City')
        axes[idx].set_ylabel('City')
        plt.colorbar(im, ax=axes[idx], label='Pheromone')
    
    plt.suptitle('Pheromone Matrix Evolution', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'pheromone_dynamics.png'), dpi=150, bbox_inches='tight')

    print(f"\nBest solution found: {aco.best_length:.2f}")
    print(f"Pheromone dynamics plot saved to {os.path.join(OUTPUT_DIR, 'pheromone_dynamics.png')}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ACO ADVANCED EXAMPLES AND ANALYSIS")
    print("=" * 70)
    
    # Run all demonstrations
    compare_parameters()
    test_scalability()
    demonstrate_convergence_behavior()
    analyze_pheromone_dynamics()
    
    print("\n" + "=" * 70)
    print("All analyses complete!")
    print(f"All plots saved to {OUTPUT_DIR}")
    print("=" * 70)
