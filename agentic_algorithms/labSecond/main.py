#!/usr/bin/env python3
"""
Artificial Life Simulation - Food Chain
Main entry point for the simulation.

This simulation models a food chain ecosystem with:
- Plants (static food source)
- Herbivores (eat plants, neural network controlled)
- Carnivores (eat herbivores, neural network controlled)

Agents evolve through natural selection and mutation of their neural networks.
"""

import sys
import argparse
from world import World
from statistics import Statistics
from config import MAX_ITERATIONS, ITERATIONS_PER_FRAME, STATS_INTERVAL

# Try to import Visualizer (requires pygame)
PYGAME_AVAILABLE = False
try:
    from visualizer import Visualizer
    PYGAME_AVAILABLE = True
except ImportError:
    pass


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Artificial Life Simulation - Food Chain Ecosystem'
    )
    parser.add_argument(
        '--iterations', '-i', type=int, default=MAX_ITERATIONS,
        help=f'Number of iterations to run (default: {MAX_ITERATIONS})'
    )
    parser.add_argument(
        '--no-visual', '-n', action='store_true',
        help='Run without visualization (faster, for data collection)'
    )
    parser.add_argument(
        '--speed', '-s', type=int, default=ITERATIONS_PER_FRAME,
        help=f'Iterations per frame (default: {ITERATIONS_PER_FRAME})'
    )
    parser.add_argument(
        '--output', '-o', type=str, default='output_data',
        help='Output directory for statistics and plots (default: output_data)'
    )
    return parser.parse_args()


def run_with_visualization(world: World, stats: Statistics,
                           max_iterations: int, speed: int):
    """Run simulation with Pygame visualization."""
    visualizer = Visualizer(world)
    visualizer.initialize()

    print("\nSimulation started with visualization.")
    print("Controls:")
    print("  SPACE - Pause/Resume")
    print("  R     - Reset simulation")
    print("  ESC   - Quit")
    print()

    try:
        while visualizer.is_running() and world.iteration < max_iterations:
            # Handle events
            if not visualizer.handle_events():
                visualizer.set_running(False)
                break

            # Run simulation steps (unless paused)
            if not visualizer.paused:
                for _ in range(speed):
                    world.step()

                    # Print stats periodically
                    if world.iteration % STATS_INTERVAL == 0:
                        stats.print_stats()

                    # Check if simulation should end
                    if world.is_simulation_over():
                        print("\n*** All agents have died! Simulation over. ***")
                        visualizer.paused = True
                        break

            # Render
            visualizer.render()
            visualizer.tick()

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")

    finally:
        visualizer.cleanup()


def run_headless(world: World, stats: Statistics, max_iterations: int):
    """Run simulation without visualization (faster)."""
    print("\nRunning headless simulation...")
    print(f"Target iterations: {max_iterations}")
    print()

    try:
        while world.iteration < max_iterations:
            world.step()

            # Print stats periodically
            if world.iteration % STATS_INTERVAL == 0:
                stats.print_stats()

            # Check if simulation should end
            if world.is_simulation_over():
                print("\n*** All agents have died! Simulation over. ***")
                break

            # Progress indicator
            if world.iteration % 500 == 0:
                progress = (world.iteration / max_iterations) * 100
                print(f"Progress: {progress:.1f}%")

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")


def main():
    """Main entry point."""
    args = parse_arguments()

    print("=" * 60)
    print("ARTIFICIAL LIFE SIMULATION - FOOD CHAIN")
    print("=" * 60)
    print()
    print("Initializing world...")

    # Create and initialize world
    world = World()
    world.initialize()

    # Create statistics handler
    stats = Statistics(world, args.output)

    print(f"World initialized with:")
    print(f"  - {len([p for p in world.plants if p.alive])} plants")
    print(f"  - {len(world.herbivores)} herbivores")
    print(f"  - {len(world.carnivores)} carnivores")
    print()

    # Run simulation
    if args.no_visual:
        run_headless(world, stats, args.iterations)
    elif not PYGAME_AVAILABLE:
        print("Pygame not available. Running in headless mode...")
        run_headless(world, stats, args.iterations)
    else:
        run_with_visualization(world, stats, args.iterations, args.speed)

    # Generate final statistics
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)

    stats.print_stats(force=True)
    stats.generate_all_plots()
    stats.generate_final_report()
    stats.save_history_csv()

    print("\nThank you for running the simulation!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
