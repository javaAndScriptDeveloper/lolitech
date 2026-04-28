"""
World simulation for the artificial life system.
Manages all agents, interactions, and the simulation loop.
Uses spatial hashing for efficient neighbor queries.
"""

import random
import math
from typing import List, Tuple, Optional, Dict, Set
from collections import defaultdict
from agent import Plant, Agent, Herbivore, Carnivore
from config import (
    WORLD_SIZE, INITIAL_PLANTS, INITIAL_HERBIVORES, INITIAL_CARNIVORES,
    VISION_RANGE, EAT_RANGE, CARNIVORE_EAT_RANGE, PLANT_ENERGY, HERBIVORE_ENERGY,
    ACTION_EAT, MIN_POPULATION_RATIO, MAX_POPULATION_RATIO,
    DIRECTION_VECTORS, NORTH, EAST, SOUTH, WEST
)


class SpatialHash:
    """Spatial hash grid for fast neighbor queries."""

    def __init__(self, cell_size: float = 10.0):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Set] = defaultdict(set)

    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Get grid cell for a position."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def clear(self):
        """Clear all entries."""
        self.grid.clear()

    def insert(self, obj, x: float, y: float):
        """Insert an object at position."""
        cell = self._get_cell(x, y)
        self.grid[cell].add(obj)

    def query_radius(self, x: float, y: float, radius: float) -> List:
        """Get all objects within radius of a position."""
        results = []
        cell_radius = int(radius / self.cell_size) + 1
        center_cell = self._get_cell(x, y)

        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    results.extend(self.grid[cell])

        return results


class World:
    """
    Manages the simulation world including all agents and their interactions.
    """

    def __init__(self):
        self.plants: List[Plant] = []
        self.herbivores: List[Herbivore] = []
        self.carnivores: List[Carnivore] = []
        self.iteration = 0

        # Spatial hashing for efficient queries
        self.plant_grid = SpatialHash(cell_size=5.0)
        self.herbivore_grid = SpatialHash(cell_size=10.0)
        self.carnivore_grid = SpatialHash(cell_size=10.0)

        # Statistics tracking
        self.history = {
            'iterations': [],
            'plants': [],
            'herbivores': [],
            'carnivores': [],
            'herbivore_avg_age': [],
            'herbivore_avg_gen': [],
            'carnivore_avg_age': [],
            'carnivore_avg_gen': [],
            'herbivore_avg_energy': [],
            'carnivore_avg_energy': []
        }

        # Population limits
        self.max_herbivores = int(INITIAL_HERBIVORES * MAX_POPULATION_RATIO / MIN_POPULATION_RATIO)
        self.max_carnivores = int(INITIAL_CARNIVORES * MAX_POPULATION_RATIO / MIN_POPULATION_RATIO)

        # Precompute facing angles
        self.facing_angles = {
            NORTH: -math.pi / 2,
            EAST: 0,
            SOUTH: math.pi / 2,
            WEST: math.pi
        }

    def initialize(self):
        """Initialize the world with starting populations."""
        # Create plants
        for _ in range(INITIAL_PLANTS):
            x = random.uniform(0, WORLD_SIZE)
            y = random.uniform(0, WORLD_SIZE)
            self.plants.append(Plant(x, y))

        # Create herbivores
        for _ in range(INITIAL_HERBIVORES):
            x = random.uniform(0, WORLD_SIZE)
            y = random.uniform(0, WORLD_SIZE)
            self.herbivores.append(Herbivore(x, y))

        # Create carnivores
        for _ in range(INITIAL_CARNIVORES):
            x = random.uniform(0, WORLD_SIZE)
            y = random.uniform(0, WORLD_SIZE)
            self.carnivores.append(Carnivore(x, y))

        # Build spatial grids
        self._rebuild_grids()

    def _rebuild_grids(self):
        """Rebuild all spatial hash grids."""
        self.plant_grid.clear()
        self.herbivore_grid.clear()
        self.carnivore_grid.clear()

        for p in self.plants:
            if p.alive:
                self.plant_grid.insert(p, p.x, p.y)

        for h in self.herbivores:
            if h.alive:
                self.herbivore_grid.insert(h, h.x, h.y)

        for c in self.carnivores:
            if c.alive:
                self.carnivore_grid.insert(c, c.x, c.y)

    def get_direction_zone(self, agent: Agent, target_x: float, target_y: float) -> Optional[str]:
        """
        Determine which zone a target is in relative to agent's direction.
        Returns 'front', 'left', 'right', or 'near'.
        """
        dx = target_x - agent.x
        dy = target_y - agent.y
        dist_sq = dx * dx + dy * dy

        if dist_sq <= 4:  # Near zone (radius 2)
            return 'near'

        if dist_sq > VISION_RANGE * VISION_RANGE:
            return None  # Out of range

        # Calculate angle to target
        angle = math.atan2(dy, dx)
        facing = self.facing_angles[agent.direction]

        # Relative angle (normalized to [-pi, pi])
        relative = angle - facing
        if relative > math.pi:
            relative -= 2 * math.pi
        elif relative < -math.pi:
            relative += 2 * math.pi

        # Determine zone based on relative angle
        if -0.7854 <= relative <= 0.7854:  # pi/4
            return 'front'
        elif 0.7854 < relative <= 2.3562:  # 3*pi/4
            return 'right'
        elif -2.3562 <= relative < -0.7854:
            return 'left'

        return None  # Behind

    def sense_for_agent(self, agent: Agent) -> Tuple:
        """
        Calculate sensor inputs for an agent using spatial hashing.
        Returns counts of entities in each direction zone.
        """
        counts = {
            'front': [0, 0, 0],  # herbivores, carnivores, plants
            'left': [0, 0, 0],
            'right': [0, 0, 0],
            'near': [0, 0, 0]
        }

        query_radius = max(VISION_RANGE, 2) + 1

        # Check nearby herbivores
        nearby_herbivores = self.herbivore_grid.query_radius(agent.x, agent.y, query_radius)
        for h in nearby_herbivores:
            if h is agent or not h.alive:
                continue
            zone = self.get_direction_zone(agent, h.x, h.y)
            if zone:
                counts[zone][0] += 1

        # Check nearby carnivores
        nearby_carnivores = self.carnivore_grid.query_radius(agent.x, agent.y, query_radius)
        for c in nearby_carnivores:
            if c is agent or not c.alive:
                continue
            zone = self.get_direction_zone(agent, c.x, c.y)
            if zone:
                counts[zone][1] += 1

        # Check nearby plants
        nearby_plants = self.plant_grid.query_radius(agent.x, agent.y, query_radius)
        for p in nearby_plants:
            if not p.alive:
                continue
            zone = self.get_direction_zone(agent, p.x, p.y)
            if zone:
                counts[zone][2] += 1

        return (
            counts['front'][0], counts['front'][1], counts['front'][2],
            counts['left'][0], counts['left'][1], counts['left'][2],
            counts['right'][0], counts['right'][1], counts['right'][2],
            counts['near'][0], counts['near'][1], counts['near'][2]
        )

    def try_eat_herbivore(self, herbivore: Herbivore) -> bool:
        """Herbivore attempts to eat a plant."""
        nearby_plants = self.plant_grid.query_radius(herbivore.x, herbivore.y, EAT_RANGE + 1)
        for plant in nearby_plants:
            if not plant.alive:
                continue
            dx = plant.x - herbivore.x
            dy = plant.y - herbivore.y
            if dx * dx + dy * dy <= EAT_RANGE * EAT_RANGE:
                plant.alive = False
                herbivore.eat(PLANT_ENERGY)
                return True
        return False

    def try_eat_carnivore(self, carnivore: Carnivore) -> bool:
        """Carnivore attempts to eat a herbivore (uses larger eat range)."""
        nearby_herbivores = self.herbivore_grid.query_radius(
            carnivore.x, carnivore.y, CARNIVORE_EAT_RANGE + 1
        )
        for herbivore in nearby_herbivores:
            if not herbivore.alive:
                continue
            dx = herbivore.x - carnivore.x
            dy = herbivore.y - carnivore.y
            if dx * dx + dy * dy <= CARNIVORE_EAT_RANGE * CARNIVORE_EAT_RANGE:
                herbivore.alive = False
                carnivore.eat(HERBIVORE_ENERGY)
                return True
        return False

    def regenerate_plants(self):
        """Regenerate eaten plants at random locations."""
        for plant in self.plants:
            if not plant.alive:
                plant.x = random.uniform(0, WORLD_SIZE)
                plant.y = random.uniform(0, WORLD_SIZE)
                plant.alive = True

    def process_agent(self, agent: Agent, is_herbivore: bool):
        """Process a single agent's turn."""
        if not agent.alive:
            return None

        # 1. Read sensors
        sensor_data = self.sense_for_agent(agent)
        agent.sense_environment(*sensor_data)

        # 2. Compute neural network outputs
        agent.compute_outputs()

        # 3. Choose action
        action = agent.choose_action()

        # 4. Execute action
        if action == ACTION_EAT:
            if is_herbivore:
                self.try_eat_herbivore(agent)
            else:
                self.try_eat_carnivore(agent)
        else:
            agent.execute_action(action)

        # 5. Apply metabolism
        agent.apply_metabolism()

        # 6. Check if outside world (desert death)
        if agent.is_outside_world():
            agent.energy -= 5  # Extra penalty for being outside
            if agent.energy <= 0:
                agent.alive = False

        # 7. Check reproduction
        child = None
        if agent.alive and agent.can_reproduce():
            # Check population limits
            if is_herbivore and len(self.herbivores) < self.max_herbivores:
                child = agent.reproduce()
            elif not is_herbivore and len(self.carnivores) < self.max_carnivores:
                child = agent.reproduce()

        return child

    def step(self):
        """Execute one simulation step."""
        self.iteration += 1

        # Rebuild spatial grids at start of each step
        self._rebuild_grids()

        # Process agents in random order
        all_agents = [(h, True) for h in self.herbivores if h.alive] + \
                     [(c, False) for c in self.carnivores if c.alive]
        random.shuffle(all_agents)

        new_herbivores = []
        new_carnivores = []

        for agent, is_herbivore in all_agents:
            child = self.process_agent(agent, is_herbivore)
            if child:
                if is_herbivore:
                    new_herbivores.append(Herbivore(
                        child.x, child.y, child.generation,
                        child.weights, child.biases
                    ))
                    new_herbivores[-1].energy = child.energy
                else:
                    new_carnivores.append(Carnivore(
                        child.x, child.y, child.generation,
                        child.weights, child.biases
                    ))
                    new_carnivores[-1].energy = child.energy

        # Add new agents
        self.herbivores.extend(new_herbivores)
        self.carnivores.extend(new_carnivores)

        # Remove dead agents
        self.herbivores = [h for h in self.herbivores if h.alive]
        self.carnivores = [c for c in self.carnivores if c.alive]

        # Regenerate plants
        self.regenerate_plants()

        # Record statistics
        self.record_stats()

    def record_stats(self):
        """Record current statistics."""
        self.history['iterations'].append(self.iteration)
        self.history['plants'].append(sum(1 for p in self.plants if p.alive))
        self.history['herbivores'].append(len(self.herbivores))
        self.history['carnivores'].append(len(self.carnivores))

        # Herbivore stats
        if self.herbivores:
            self.history['herbivore_avg_age'].append(
                sum(h.age for h in self.herbivores) / len(self.herbivores)
            )
            self.history['herbivore_avg_gen'].append(
                sum(h.generation for h in self.herbivores) / len(self.herbivores)
            )
            self.history['herbivore_avg_energy'].append(
                sum(h.energy for h in self.herbivores) / len(self.herbivores)
            )
        else:
            self.history['herbivore_avg_age'].append(0)
            self.history['herbivore_avg_gen'].append(0)
            self.history['herbivore_avg_energy'].append(0)

        # Carnivore stats
        if self.carnivores:
            self.history['carnivore_avg_age'].append(
                sum(c.age for c in self.carnivores) / len(self.carnivores)
            )
            self.history['carnivore_avg_gen'].append(
                sum(c.generation for c in self.carnivores) / len(self.carnivores)
            )
            self.history['carnivore_avg_energy'].append(
                sum(c.energy for c in self.carnivores) / len(self.carnivores)
            )
        else:
            self.history['carnivore_avg_age'].append(0)
            self.history['carnivore_avg_gen'].append(0)
            self.history['carnivore_avg_energy'].append(0)

    def get_stats_string(self) -> str:
        """Get formatted statistics string."""
        h_avg_age = self.history['herbivore_avg_age'][-1] if self.history['herbivore_avg_age'] else 0
        h_avg_gen = self.history['herbivore_avg_gen'][-1] if self.history['herbivore_avg_gen'] else 0
        c_avg_age = self.history['carnivore_avg_age'][-1] if self.history['carnivore_avg_age'] else 0
        c_avg_gen = self.history['carnivore_avg_gen'][-1] if self.history['carnivore_avg_gen'] else 0

        return (
            f"Iteration: {self.iteration}\n"
            f"Plants: {len([p for p in self.plants if p.alive])}\n"
            f"Herbivores: {len(self.herbivores)} (avg age: {h_avg_age:.1f}, gen: {h_avg_gen:.1f})\n"
            f"Carnivores: {len(self.carnivores)} (avg age: {c_avg_age:.1f}, gen: {c_avg_gen:.1f})"
        )

    def is_simulation_over(self) -> bool:
        """Check if simulation should end (all agents dead)."""
        return len(self.herbivores) == 0 and len(self.carnivores) == 0
