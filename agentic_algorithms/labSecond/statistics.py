"""
Statistics collection and analysis module for the artificial life simulation.
Generates reports and visualizations of simulation data.
"""

import os
from typing import Dict, List
from world import World
from config import STATS_INTERVAL

# Try to import matplotlib for plotting
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Graphs will not be generated.")


class Statistics:
    """Handles statistics collection, analysis, and reporting."""

    def __init__(self, world: World, output_dir: str = "output_data"):
        self.world = world
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def print_stats(self, force: bool = False):
        """Print current statistics to console."""
        if force or self.world.iteration % STATS_INTERVAL == 0:
            print(f"\n{'='*50}")
            print(self.world.get_stats_string())
            print(f"{'='*50}")

    def generate_population_plot(self):
        """Generate population over time plot."""
        if not MATPLOTLIB_AVAILABLE:
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        iterations = self.world.history['iterations']
        ax.plot(iterations, self.world.history['herbivores'],
                label='Herbivores', color='blue', linewidth=2)
        ax.plot(iterations, self.world.history['carnivores'],
                label='Carnivores', color='red', linewidth=2)

        # Scale plants for visibility (they're usually much more numerous)
        plants_scaled = [p / 10 for p in self.world.history['plants']]
        ax.plot(iterations, plants_scaled,
                label='Plants (÷10)', color='green', linewidth=1, alpha=0.7)

        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Population', fontsize=12)
        ax.set_title('Population Dynamics Over Time', fontsize=14)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'population_dynamics.png'), dpi=150)
        plt.close()

    def generate_generation_plot(self):
        """Generate average generation over time plot."""
        if not MATPLOTLIB_AVAILABLE:
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        iterations = self.world.history['iterations']
        ax.plot(iterations, self.world.history['herbivore_avg_gen'],
                label='Herbivores', color='blue', linewidth=2)
        ax.plot(iterations, self.world.history['carnivore_avg_gen'],
                label='Carnivores', color='red', linewidth=2)

        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Average Generation', fontsize=12)
        ax.set_title('Evolution: Average Generation Over Time', fontsize=14)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'generation_evolution.png'), dpi=150)
        plt.close()

    def generate_energy_plot(self):
        """Generate average energy over time plot."""
        if not MATPLOTLIB_AVAILABLE:
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        iterations = self.world.history['iterations']
        ax.plot(iterations, self.world.history['herbivore_avg_energy'],
                label='Herbivores', color='blue', linewidth=2)
        ax.plot(iterations, self.world.history['carnivore_avg_energy'],
                label='Carnivores', color='red', linewidth=2)

        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Average Energy', fontsize=12)
        ax.set_title('Average Energy Levels Over Time', fontsize=14)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'energy_levels.png'), dpi=150)
        plt.close()

    def generate_world_map(self):
        """Generate a map showing current agent positions."""
        if not MATPLOTLIB_AVAILABLE:
            return

        fig, ax = plt.subplots(figsize=(10, 10))

        # Plot plants
        plant_x = [p.x for p in self.world.plants if p.alive]
        plant_y = [p.y for p in self.world.plants if p.alive]
        ax.scatter(plant_x, plant_y, c='green', s=1, alpha=0.5, label='Plants')

        # Plot herbivores
        herb_x = [h.x for h in self.world.herbivores if h.alive]
        herb_y = [h.y for h in self.world.herbivores if h.alive]
        ax.scatter(herb_x, herb_y, c='blue', s=20, alpha=0.8, label='Herbivores')

        # Plot carnivores
        carn_x = [c.x for c in self.world.carnivores if c.alive]
        carn_y = [c.y for c in self.world.carnivores if c.alive]
        ax.scatter(carn_x, carn_y, c='red', s=30, alpha=0.8, label='Carnivores')

        ax.set_xlim(0, 800)  # WORLD_SIZE
        ax.set_ylim(0, 800)
        ax.set_aspect('equal')
        ax.set_xlabel('X Position', fontsize=12)
        ax.set_ylabel('Y Position', fontsize=12)
        ax.set_title(f'World Map at Iteration {self.world.iteration}', fontsize=14)
        ax.legend(loc='upper right')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'world_map.png'), dpi=150)
        plt.close()

    def generate_all_plots(self):
        """Generate all statistical plots."""
        print("\nGenerating plots...")
        self.generate_population_plot()
        self.generate_generation_plot()
        self.generate_energy_plot()
        self.generate_world_map()
        print(f"Plots saved to {self.output_dir}/")

    def generate_final_report(self):
        """Generate a final text report of the simulation."""
        report_path = os.path.join(self.output_dir, 'simulation_report.txt')

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ARTIFICIAL LIFE SIMULATION - FINAL REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Total Iterations: {self.world.iteration}\n\n")

            f.write("FINAL POPULATIONS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Plants: {sum(1 for p in self.world.plants if p.alive)}\n")
            f.write(f"Herbivores: {len(self.world.herbivores)}\n")
            f.write(f"Carnivores: {len(self.world.carnivores)}\n\n")

            if self.world.herbivores:
                f.write("HERBIVORE STATISTICS:\n")
                f.write("-" * 30 + "\n")
                ages = [h.age for h in self.world.herbivores]
                gens = [h.generation for h in self.world.herbivores]
                energies = [h.energy for h in self.world.herbivores]
                f.write(f"Average Age: {sum(ages)/len(ages):.1f}\n")
                f.write(f"Max Age: {max(ages)}\n")
                f.write(f"Average Generation: {sum(gens)/len(gens):.1f}\n")
                f.write(f"Max Generation: {max(gens)}\n")
                f.write(f"Average Energy: {sum(energies)/len(energies):.1f}\n\n")

            if self.world.carnivores:
                f.write("CARNIVORE STATISTICS:\n")
                f.write("-" * 30 + "\n")
                ages = [c.age for c in self.world.carnivores]
                gens = [c.generation for c in self.world.carnivores]
                energies = [c.energy for c in self.world.carnivores]
                f.write(f"Average Age: {sum(ages)/len(ages):.1f}\n")
                f.write(f"Max Age: {max(ages)}\n")
                f.write(f"Average Generation: {sum(gens)/len(gens):.1f}\n")
                f.write(f"Max Generation: {max(gens)}\n")
                f.write(f"Average Energy: {sum(energies)/len(energies):.1f}\n\n")

            f.write("POPULATION HISTORY SUMMARY:\n")
            f.write("-" * 30 + "\n")
            if self.world.history['herbivores']:
                f.write(f"Herbivores - Min: {min(self.world.history['herbivores'])}, "
                       f"Max: {max(self.world.history['herbivores'])}\n")
            if self.world.history['carnivores']:
                f.write(f"Carnivores - Min: {min(self.world.history['carnivores'])}, "
                       f"Max: {max(self.world.history['carnivores'])}\n")

            if self.world.history['herbivore_avg_gen']:
                max_herb_gen = max(self.world.history['herbivore_avg_gen'])
                f.write(f"\nPeak Herbivore Generation: {max_herb_gen:.1f}\n")
            if self.world.history['carnivore_avg_gen']:
                max_carn_gen = max(self.world.history['carnivore_avg_gen'])
                f.write(f"Peak Carnivore Generation: {max_carn_gen:.1f}\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("End of Report\n")

        print(f"Report saved to {report_path}")

    def save_history_csv(self):
        """Save simulation history to CSV file."""
        csv_path = os.path.join(self.output_dir, 'simulation_history.csv')

        with open(csv_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("iteration,plants,herbivores,carnivores,"
                   "herb_avg_age,herb_avg_gen,herb_avg_energy,"
                   "carn_avg_age,carn_avg_gen,carn_avg_energy\n")

            # Data
            for i in range(len(self.world.history['iterations'])):
                f.write(f"{self.world.history['iterations'][i]},"
                       f"{self.world.history['plants'][i]},"
                       f"{self.world.history['herbivores'][i]},"
                       f"{self.world.history['carnivores'][i]},"
                       f"{self.world.history['herbivore_avg_age'][i]:.2f},"
                       f"{self.world.history['herbivore_avg_gen'][i]:.2f},"
                       f"{self.world.history['herbivore_avg_energy'][i]:.2f},"
                       f"{self.world.history['carnivore_avg_age'][i]:.2f},"
                       f"{self.world.history['carnivore_avg_gen'][i]:.2f},"
                       f"{self.world.history['carnivore_avg_energy'][i]:.2f}\n")

        print(f"History saved to {csv_path}")
