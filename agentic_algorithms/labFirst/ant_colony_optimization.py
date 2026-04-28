"""
Ant Colony Optimization (ACO) Algorithm for Traveling Salesman Problem
Based on the Ukrainian documentation provided
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import random
import os

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)


class AntColonyOptimization:
    """
    Implementation of Ant Colony Optimization algorithm for TSP
    """
    
    def __init__(
        self,
        distances: np.ndarray,
        n_ants: Optional[int] = None,
        n_iterations: int = 100,
        alpha: float = 1.0,
        beta: float = 2.0,
        rho: float = 0.5,
        Q: float = 100.0,
        elite_ants: int = 0,
        initial_pheromone: float = 0.1
    ):
        """
        Initialize ACO algorithm
        
        Parameters:
        -----------
        distances : np.ndarray
            Distance matrix between cities (symmetric)
        n_ants : int, optional
            Number of ants (default: number of cities)
        n_iterations : int
            Number of iterations to run
        alpha : float
            Pheromone importance parameter (α)
        beta : float
            Visibility (distance) importance parameter (β)
        rho : float
            Pheromone evaporation coefficient (ρ), range [0, 1]
        Q : float
            Constant related to pheromone deposit
        elite_ants : int
            Number of elite ants for elitist strategy
        initial_pheromone : float
            Initial pheromone level on all edges
        """
        self.distances = distances
        self.n_cities = len(distances)
        self.n_ants = n_ants if n_ants else self.n_cities
        self.n_iterations = n_iterations
        self.alpha = alpha  # α parameter
        self.beta = beta    # β parameter
        self.rho = rho      # ρ parameter (evaporation)
        self.Q = Q
        self.elite_ants = elite_ants
        
        # Initialize pheromone matrix
        self.pheromones = np.ones((self.n_cities, self.n_cities)) * initial_pheromone
        
        # Calculate visibility (η_ij = 1/d_ij)
        self.visibility = np.zeros((self.n_cities, self.n_cities))
        for i in range(self.n_cities):
            for j in range(self.n_cities):
                if i != j and distances[i][j] > 0:
                    self.visibility[i][j] = 1.0 / distances[i][j]
        
        # Best solution tracking
        self.best_path = None
        self.best_length = float('inf')
        self.history = []
        
    def _calculate_probabilities(self, current_city: int, unvisited: List[int]) -> np.ndarray:
        """
        Calculate probabilities for choosing next city
        Based on formula (1) from the document
        
        P_ij^k(t) = [τ_ij(t)]^α * [η_ij]^β / Σ[τ_il(t)]^α * [η_il]^β
        """
        pheromone = np.array([self.pheromones[current_city][j] for j in unvisited])
        visibility = np.array([self.visibility[current_city][j] for j in unvisited])
        
        # Calculate numerator for each unvisited city
        numerator = (pheromone ** self.alpha) * (visibility ** self.beta)
        denominator = numerator.sum()
        
        if denominator == 0:
            # If all values are zero, use uniform probability
            return np.ones(len(unvisited)) / len(unvisited)
        
        probabilities = numerator / denominator
        return probabilities
    
    def _select_next_city(self, current_city: int, unvisited: List[int]) -> int:
        """
        Select next city based on probabilistic rule
        Uses roulette wheel selection
        """
        probabilities = self._calculate_probabilities(current_city, unvisited)
        
        # Roulette wheel selection
        rand = random.random()
        cumulative_prob = 0
        
        for i, city in enumerate(unvisited):
            cumulative_prob += probabilities[i]
            if rand <= cumulative_prob:
                return city
        
        # Fallback (shouldn't happen)
        return unvisited[-1]
    
    def _construct_solution(self, start_city: int) -> Tuple[List[int], float]:
        """
        Construct a solution (tour) for one ant
        
        Returns:
        --------
        path : List[int]
            The path taken by the ant
        length : float
            Total length of the path
        """
        path = [start_city]
        unvisited = list(range(self.n_cities))
        unvisited.remove(start_city)
        
        current_city = start_city
        
        # Build the tour
        while unvisited:
            next_city = self._select_next_city(current_city, unvisited)
            path.append(next_city)
            unvisited.remove(next_city)
            current_city = next_city
        
        # Calculate total path length
        length = self._calculate_path_length(path)
        
        return path, length
    
    def _calculate_path_length(self, path: List[int]) -> float:
        """Calculate total length of a path"""
        length = 0
        for i in range(len(path)):
            from_city = path[i]
            to_city = path[(i + 1) % len(path)]  # Return to start
            length += self.distances[from_city][to_city]
        return length
    
    def _update_pheromones(self, all_paths: List[List[int]], all_lengths: List[float]):
        """
        Update pheromone levels on all edges
        Based on formulas (2) and the update rule from the document
        """
        # Evaporation (negative feedback)
        # τ_ij(t+1) = (1-ρ) * τ_ij(t) + Δτ_ij
        self.pheromones *= (1 - self.rho)
        
        # Deposit pheromones (positive feedback)
        for path, length in zip(all_paths, all_lengths):
            # Δτ_ij^k = Q / L_k if edge (i,j) in path, else 0
            deposit = self.Q / length
            
            for i in range(len(path)):
                from_city = path[i]
                to_city = path[(i + 1) % len(path)]
                self.pheromones[from_city][to_city] += deposit
                self.pheromones[to_city][from_city] += deposit  # Symmetric
        
        # Elite ant strategy (if enabled)
        if self.elite_ants > 0 and self.best_path:
            elite_deposit = self.elite_ants * self.Q / self.best_length
            for i in range(len(self.best_path)):
                from_city = self.best_path[i]
                to_city = self.best_path[(i + 1) % len(self.best_path)]
                self.pheromones[from_city][to_city] += elite_deposit
                self.pheromones[to_city][from_city] += elite_deposit
    
    def optimize(self, verbose: bool = True) -> Tuple[List[int], float]:
        """
        Run the ACO algorithm
        
        Returns:
        --------
        best_path : List[int]
            The best path found
        best_length : float
            Length of the best path
        """
        # Distribute ants uniformly across starting cities
        start_cities = [i % self.n_cities for i in range(self.n_ants)]
        
        for iteration in range(self.n_iterations):
            all_paths = []
            all_lengths = []
            
            # Each ant constructs a solution
            for ant in range(self.n_ants):
                path, length = self._construct_solution(start_cities[ant])
                all_paths.append(path)
                all_lengths.append(length)
                
                # Update best solution if found
                if length < self.best_length:
                    self.best_length = length
                    self.best_path = path.copy()
            
            # Update pheromones
            self._update_pheromones(all_paths, all_lengths)
            
            # Track history
            avg_length = np.mean(all_lengths)
            self.history.append({
                'iteration': iteration,
                'best_length': self.best_length,
                'avg_length': avg_length,
                'min_length': min(all_lengths),
                'max_length': max(all_lengths)
            })
            
            if verbose and (iteration + 1) % 10 == 0:
                print(f"Iteration {iteration + 1}/{self.n_iterations}: "
                      f"Best = {self.best_length:.2f}, "
                      f"Avg = {avg_length:.2f}")
        
        if verbose:
            print(f"\nOptimization complete!")
            print(f"Best path length: {self.best_length:.2f}")
            print(f"Best path: {self.best_path}")
        
        return self.best_path, self.best_length
    
    def plot_convergence(self):
        """Plot convergence graph"""
        iterations = [h['iteration'] for h in self.history]
        best_lengths = [h['best_length'] for h in self.history]
        avg_lengths = [h['avg_length'] for h in self.history]
        
        plt.figure(figsize=(10, 6))
        plt.plot(iterations, best_lengths, 'b-', label='Best Length', linewidth=2)
        plt.plot(iterations, avg_lengths, 'r--', label='Average Length', linewidth=1)
        plt.xlabel('Iteration')
        plt.ylabel('Path Length')
        plt.title('ACO Convergence')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return plt
    
    def plot_pheromone_matrix(self):
        """Visualize pheromone matrix"""
        plt.figure(figsize=(8, 6))
        plt.imshow(self.pheromones, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Pheromone Level')
        plt.title('Pheromone Matrix')
        plt.xlabel('City')
        plt.ylabel('City')
        plt.tight_layout()
        return plt


def create_random_tsp(n_cities: int, seed: Optional[int] = None) -> np.ndarray:
    """
    Create a random TSP instance with cities in 2D space
    
    Parameters:
    -----------
    n_cities : int
        Number of cities
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    distances : np.ndarray
        Distance matrix
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate random city coordinates
    cities = np.random.rand(n_cities, 2) * 100
    
    # Calculate Euclidean distances
    distances = np.zeros((n_cities, n_cities))
    for i in range(n_cities):
        for j in range(n_cities):
            if i != j:
                distances[i][j] = np.linalg.norm(cities[i] - cities[j])
    
    return distances, cities


def plot_tour(cities: np.ndarray, path: List[int], title: str = "Best Tour"):
    """
    Plot the tour on a 2D map
    
    Parameters:
    -----------
    cities : np.ndarray
        City coordinates (n_cities x 2)
    path : List[int]
        Order of cities to visit
    title : str
        Plot title
    """
    plt.figure(figsize=(10, 8))
    
    # Plot cities
    plt.scatter(cities[:, 0], cities[:, 1], c='red', s=100, zorder=5, label='Cities')
    
    # Plot tour
    for i in range(len(path)):
        from_city = path[i]
        to_city = path[(i + 1) % len(path)]
        plt.plot([cities[from_city, 0], cities[to_city, 0]],
                [cities[from_city, 1], cities[to_city, 1]],
                'b-', linewidth=1.5, alpha=0.7)
    
    # Annotate cities
    for i, (x, y) in enumerate(cities):
        plt.annotate(str(i), (x, y), fontsize=8, ha='center', va='center',
                    bbox=dict(boxstyle='circle', facecolor='white', alpha=0.7))
    
    # Mark start city
    start = path[0]
    plt.scatter(cities[start, 0], cities[start, 1], 
               c='green', s=200, marker='*', zorder=6, label='Start')
    
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.tight_layout()
    return plt


# Example usage and demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("Ant Colony Optimization for Traveling Salesman Problem")
    print("=" * 60)
    print()
    
    # Create a random TSP instance
    n_cities = 20
    print(f"Creating random TSP with {n_cities} cities...")
    distances, cities = create_random_tsp(n_cities, seed=42)
    
    # Initialize ACO
    print("\nInitializing ACO algorithm...")
    print(f"Parameters:")
    print(f"  - Number of ants: {n_cities}")
    print(f"  - Iterations: 100")
    print(f"  - Alpha (α): 1.0")
    print(f"  - Beta (β): 2.0")
    print(f"  - Rho (ρ): 0.5")
    print(f"  - Q: 100.0")
    print(f"  - Elite ants: 5")
    print()
    
    aco = AntColonyOptimization(
        distances=distances,
        n_ants=n_cities,
        n_iterations=100,
        alpha=1.0,
        beta=2.0,
        rho=0.5,
        Q=100.0,
        elite_ants=5,
        initial_pheromone=0.1
    )
    
    # Run optimization
    print("Running optimization...")
    print("-" * 60)
    best_path, best_length = aco.optimize(verbose=True)
    print("-" * 60)
    
    # Plot results
    print("\nGenerating visualizations...")
    
    # Plot convergence
    plt_conv = aco.plot_convergence()
    plt_conv.savefig(os.path.join(OUTPUT_DIR, 'aco_convergence.png'), dpi=150, bbox_inches='tight')
    print("✓ Convergence plot saved")

    # Plot pheromone matrix
    plt_pher = aco.plot_pheromone_matrix()
    plt_pher.savefig(os.path.join(OUTPUT_DIR, 'aco_pheromone_matrix.png'), dpi=150, bbox_inches='tight')
    print("✓ Pheromone matrix saved")

    # Plot best tour
    plt_tour = plot_tour(cities, best_path,
                        title=f"Best Tour (Length: {best_length:.2f})")
    plt_tour.savefig(os.path.join(OUTPUT_DIR, 'aco_best_tour.png'), dpi=150, bbox_inches='tight')
    print("✓ Best tour plot saved")

    print(f"\nAll visualizations saved to {OUTPUT_DIR}")
    print("\n" + "=" * 60)
    print("Optimization Complete!")
    print("=" * 60)
