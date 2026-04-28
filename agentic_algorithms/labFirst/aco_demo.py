"""
Interactive Demo for Ant Colony Optimization
Simple interface for experimenting with ACO parameters
"""

from ant_colony_optimization import AntColonyOptimization, create_random_tsp, plot_tour
import numpy as np
import matplotlib.pyplot as plt
import os

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_demo(
    n_cities=15,
    n_ants=None,
    n_iterations=50,
    alpha=1.0,
    beta=2.0,
    rho=0.5,
    elite_ants=3,
    seed=None,
    show_plots=True
):
    """
    Run a complete ACO demonstration with given parameters
    
    Parameters:
    -----------
    n_cities : int
        Number of cities in TSP
    n_ants : int
        Number of ants (default: same as n_cities)
    n_iterations : int
        Number of iterations
    alpha : float
        Pheromone importance (α)
    beta : float
        Distance importance (β)
    rho : float
        Evaporation rate (ρ)
    elite_ants : int
        Number of elite ants
    seed : int
        Random seed for reproducibility
    show_plots : bool
        Whether to display plots
    """
    
    print("\n" + "="*70)
    print("ANT COLONY OPTIMIZATION - INTERACTIVE DEMO")
    print("="*70)
    
    # Create TSP instance
    print(f"\n📍 Creating TSP with {n_cities} cities...")
    distances, cities = create_random_tsp(n_cities, seed=seed)
    
    # Calculate greedy solution for comparison
    greedy_length = greedy_tsp(distances)
    print(f"   Greedy solution: {greedy_length:.2f}")
    
    # Setup ACO
    if n_ants is None:
        n_ants = n_cities
    
    print(f"\n🐜 Setting up ACO with:")
    print(f"   - Ants: {n_ants}")
    print(f"   - Iterations: {n_iterations}")
    print(f"   - Alpha (α): {alpha}")
    print(f"   - Beta (β): {beta}")
    print(f"   - Rho (ρ): {rho}")
    print(f"   - Elite ants: {elite_ants}")
    
    aco = AntColonyOptimization(
        distances=distances,
        n_ants=n_ants,
        n_iterations=n_iterations,
        alpha=alpha,
        beta=beta,
        rho=rho,
        Q=100.0,
        elite_ants=elite_ants
    )
    
    # Run optimization
    print(f"\n⚙️  Running optimization...")
    best_path, best_length = aco.optimize(verbose=False)
    
    # Results
    print(f"\n✅ Optimization complete!")
    print(f"   Best solution: {best_length:.2f}")
    print(f"   Improvement over greedy: {((greedy_length - best_length) / greedy_length * 100):.1f}%")
    print(f"   Path: {best_path[:10]}{'...' if len(best_path) > 10 else ''}")
    
    # Statistics
    first_best = aco.history[0]['best_length']
    last_avg = aco.history[-1]['avg_length']
    
    print(f"\n📊 Statistics:")
    print(f"   Initial best: {first_best:.2f}")
    print(f"   Final best: {best_length:.2f}")
    print(f"   Total improvement: {first_best - best_length:.2f} ({((first_best - best_length) / first_best * 100):.1f}%)")
    print(f"   Final average: {last_avg:.2f}")
    print(f"   Convergence rate: {(best_length / last_avg * 100):.1f}%")
    
    # Find iteration of best solution
    for i, h in enumerate(aco.history):
        if h['best_length'] == best_length:
            best_iteration = i
            break
    print(f"   Best found at iteration: {best_iteration + 1}")
    
    # Plots
    if show_plots:
        print(f"\n📈 Generating visualizations...")
        
        # Create comprehensive figure
        fig = plt.figure(figsize=(16, 10))
        
        # 1. Convergence plot
        ax1 = plt.subplot(2, 3, 1)
        iterations = [h['iteration'] for h in aco.history]
        best_lengths = [h['best_length'] for h in aco.history]
        avg_lengths = [h['avg_length'] for h in aco.history]
        
        ax1.plot(iterations, best_lengths, 'b-', label='Best', linewidth=2)
        ax1.plot(iterations, avg_lengths, 'r--', label='Average', linewidth=1.5, alpha=0.7)
        ax1.axhline(y=greedy_length, color='g', linestyle=':', label='Greedy', linewidth=1.5)
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Path Length')
        ax1.set_title('Convergence', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Best tour visualization
        ax2 = plt.subplot(2, 3, 2)
        ax2.scatter(cities[:, 0], cities[:, 1], c='red', s=100, zorder=5)
        for i in range(len(best_path)):
            from_city = best_path[i]
            to_city = best_path[(i + 1) % len(best_path)]
            ax2.plot([cities[from_city, 0], cities[to_city, 0]],
                    [cities[from_city, 1], cities[to_city, 1]],
                    'b-', linewidth=1.5, alpha=0.7)
        
        # Annotate cities
        for i, (x, y) in enumerate(cities):
            ax2.annotate(str(i), (x, y), fontsize=7, ha='center', va='center',
                        bbox=dict(boxstyle='circle', facecolor='white', alpha=0.7, pad=0.2))
        
        start = best_path[0]
        ax2.scatter(cities[start, 0], cities[start, 1], 
                   c='green', s=250, marker='*', zorder=6)
        
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_title(f'Best Tour (Length: {best_length:.2f})', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.axis('equal')
        
        # 3. Pheromone matrix
        ax3 = plt.subplot(2, 3, 3)
        im = ax3.imshow(aco.pheromones, cmap='hot', interpolation='nearest')
        plt.colorbar(im, ax=ax3, label='Pheromone')
        ax3.set_xlabel('City')
        ax3.set_ylabel('City')
        ax3.set_title('Pheromone Matrix', fontweight='bold')
        
        # 4. Improvement per iteration
        ax4 = plt.subplot(2, 3, 4)
        improvements = []
        for i in range(1, len(aco.history)):
            prev_best = aco.history[i-1]['best_length']
            curr_best = aco.history[i]['best_length']
            improvement = prev_best - curr_best
            improvements.append(improvement)
        
        ax4.bar(range(1, len(improvements)+1), improvements, color='blue', alpha=0.7)
        ax4.set_xlabel('Iteration')
        ax4.set_ylabel('Improvement')
        ax4.set_title('Improvement per Iteration', fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. Solution diversity
        ax5 = plt.subplot(2, 3, 5)
        min_lengths = [h['min_length'] for h in aco.history]
        max_lengths = [h['max_length'] for h in aco.history]
        
        ax5.fill_between(iterations, min_lengths, max_lengths, 
                         alpha=0.3, color='gray', label='Range')
        ax5.plot(iterations, avg_lengths, 'r-', label='Average', linewidth=2)
        ax5.plot(iterations, best_lengths, 'b-', label='Best', linewidth=2)
        ax5.set_xlabel('Iteration')
        ax5.set_ylabel('Path Length')
        ax5.set_title('Solution Diversity', fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Parameter summary
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        summary_text = f"""
        PARAMETERS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Cities:           {n_cities}
        Ants:             {n_ants}
        Iterations:       {n_iterations}
        Alpha (α):        {alpha}
        Beta (β):         {beta}
        Rho (ρ):          {rho}
        Elite Ants:       {elite_ants}
        
        RESULTS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Greedy:           {greedy_length:.2f}
        ACO Best:         {best_length:.2f}
        Improvement:      {((greedy_length - best_length) / greedy_length * 100):.1f}%
        
        Best at iter:     {best_iteration + 1}
        Total improv:     {first_best - best_length:.2f}
        Convergence:      {(best_length / last_avg * 100):.1f}%
        """
        
        ax6.text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
                verticalalignment='center')
        
        plt.suptitle('ACO Analysis Dashboard', fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        # Save
        output_path = os.path.join(OUTPUT_DIR, 'aco_demo_analysis.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"   Saved to: {output_path}")
    
    print("\n" + "="*70)
    
    return {
        'best_path': best_path,
        'best_length': best_length,
        'greedy_length': greedy_length,
        'improvement': (greedy_length - best_length) / greedy_length * 100,
        'history': aco.history,
        'aco': aco
    }


def greedy_tsp(distances):
    """Simple greedy algorithm for comparison"""
    n = len(distances)
    unvisited = set(range(1, n))
    current = 0
    path_length = 0
    
    while unvisited:
        nearest = min(unvisited, key=lambda x: distances[current][x])
        path_length += distances[current][nearest]
        current = nearest
        unvisited.remove(nearest)
    
    # Return to start
    path_length += distances[current][0]
    
    return path_length


def compare_configurations():
    """Compare different ACO configurations"""
    
    print("\n" + "="*70)
    print("COMPARING DIFFERENT CONFIGURATIONS")
    print("="*70)
    
    configs = [
        {'name': 'Default', 'alpha': 1.0, 'beta': 2.0, 'rho': 0.5, 'elite_ants': 3},
        {'name': 'Exploitation', 'alpha': 2.0, 'beta': 1.0, 'rho': 0.3, 'elite_ants': 10},
        {'name': 'Exploration', 'alpha': 0.5, 'beta': 5.0, 'rho': 0.7, 'elite_ants': 0},
        {'name': 'Fast Convergence', 'alpha': 3.0, 'beta': 1.0, 'rho': 0.2, 'elite_ants': 15},
    ]
    
    n_cities = 15
    distances, cities = create_random_tsp(n_cities, seed=42)
    
    results = []
    
    for config in configs:
        print(f"\nTesting: {config['name']}")
        
        aco = AntColonyOptimization(
            distances=distances,
            n_ants=n_cities,
            n_iterations=50,
            alpha=config['alpha'],
            beta=config['beta'],
            rho=config['rho'],
            elite_ants=config['elite_ants']
        )
        
        best_path, best_length = aco.optimize(verbose=False)
        
        results.append({
            'name': config['name'],
            'length': best_length,
            'history': aco.history
        })
        
        print(f"  Best: {best_length:.2f}")
    
    # Plot comparison
    plt.figure(figsize=(12, 6))
    
    for result in results:
        iterations = [h['iteration'] for h in result['history']]
        lengths = [h['best_length'] for h in result['history']]
        plt.plot(iterations, lengths, label=result['name'], linewidth=2)
    
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Best Path Length', fontsize=12)
    plt.title('Configuration Comparison', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'aco_config_comparison.png'), dpi=150)

    print("\n" + "="*70)
    print("RESULTS SUMMARY:")
    print("="*70)
    for result in results:
        print(f"  {result['name']:20s}: {result['length']:8.2f}")

    print(f"\nPlot saved to: {os.path.join(OUTPUT_DIR, 'aco_config_comparison.png')}")


if __name__ == "__main__":
    # Example 1: Basic demo
    print("\n🔷 Example 1: Basic Demo")
    run_demo(
        n_cities=15,
        n_iterations=50,
        alpha=1.0,
        beta=2.0,
        rho=0.5,
        elite_ants=3,
        seed=123
    )
    
    # Example 2: Larger problem
    print("\n\n🔷 Example 2: Larger Problem")
    run_demo(
        n_cities=25,
        n_iterations=75,
        alpha=1.0,
        beta=3.0,
        rho=0.5,
        elite_ants=5,
        seed=456
    )
    
    # Example 3: Compare configurations
    print("\n\n🔷 Example 3: Configuration Comparison")
    compare_configurations()
    
    print("\n\n✨ All demos completed successfully!")
    print(f"Check {OUTPUT_DIR} for visualizations")
