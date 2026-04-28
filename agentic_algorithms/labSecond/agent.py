"""
Agent classes for the artificial life simulation.
Contains Plant, Herbivore, and Carnivore classes with neural network logic.
"""

import numpy as np
import random
from config import (
    WORLD_SIZE, MAX_ENERGY, WEIGHT_INIT_RANGE, BIAS_INIT_RANGE,
    WEIGHT_MUTATION_RANGE, BIAS_MUTATION_RANGE, REPRODUCTION_THRESHOLD,
    REPRODUCTION_ENERGY_SPLIT, HERBIVORE_METABOLISM, CARNIVORE_METABOLISM,
    MOVE_DISTANCE_MIN, MOVE_DISTANCE_MAX, CARNIVORE_MOVE_BONUS, DIRECTION_VECTORS,
    NORTH, EAST, SOUTH, WEST, ACTION_TURN_LEFT, ACTION_TURN_RIGHT,
    ACTION_MOVE, ACTION_EAT, PLANT_ENERGY, HERBIVORE_ENERGY
)


class Plant:
    """Static plant object that provides energy to herbivores."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.alive = True

    def get_position(self):
        return (self.x, self.y)


class Agent:
    """
    Base class for mobile agents (herbivores and carnivores).
    Contains neural network for decision making.
    """

    # Neural network dimensions
    NUM_INPUTS = 12  # 3 types × 4 directions
    NUM_OUTPUTS = 4  # turn left, turn right, move, eat

    def __init__(self, x: float, y: float, agent_type: str,
                 generation: int = 1, weights=None, biases=None):
        self.x = x
        self.y = y
        self.agent_type = agent_type  # 'herbivore' or 'carnivore'
        self.energy = int(MAX_ENERGY * 0.7)  # Start with 70% energy
        self.age = 0
        self.generation = generation
        self.direction = random.choice([NORTH, EAST, SOUTH, WEST])
        self.alive = True

        # Neural network components
        self.inputs = np.zeros(self.NUM_INPUTS)
        self.outputs = np.zeros(self.NUM_OUTPUTS)

        # Initialize or inherit weights and biases
        if weights is not None:
            self.weights = weights.copy()
        else:
            self.weights = self._initialize_weights()

        if biases is not None:
            self.biases = biases.copy()
        else:
            self.biases = np.random.uniform(
                -BIAS_INIT_RANGE, BIAS_INIT_RANGE,
                self.NUM_OUTPUTS
            )

    def _initialize_weights(self):
        """
        Initialize neural network weights with bias toward food-seeking behavior.
        Inputs: 0-2 front (herb/carn/plant), 3-5 left, 6-8 right, 9-11 near
        Outputs: 0 turn-left, 1 turn-right, 2 move, 3 eat
        """
        weights = np.random.uniform(
            -WEIGHT_INIT_RANGE * 0.5, WEIGHT_INIT_RANGE * 0.5,
            (self.NUM_INPUTS, self.NUM_OUTPUTS)
        )

        # Food index: plants (2) for herbivores, herbivores (0) for carnivores
        food_idx = 2 if self.agent_type == 'herbivore' else 0
        # Predator index for avoidance
        predator_idx = 1 if self.agent_type == 'herbivore' else None

        # Both herbivores and carnivores get strong food-seeking behavior
        weights[food_idx, 2] = 0.8  # front food -> move
        weights[food_idx + 3, 0] = 0.6  # left food -> turn left
        weights[food_idx + 6, 1] = 0.6  # right food -> turn right
        weights[food_idx + 9, 3] = 1.0  # near food -> eat

        # Herbivores should avoid carnivores
        if predator_idx is not None:
            weights[predator_idx, 2] = -0.5  # predator in front -> don't move forward
            weights[predator_idx + 9, 2] = 0.8  # predator near -> run (move)

        # Add some noise for diversity
        weights += np.random.uniform(-0.2, 0.2, weights.shape)

        return weights

    def get_position(self):
        return (self.x, self.y)

    def get_metabolism(self) -> int:
        """Return energy cost per iteration."""
        if self.agent_type == 'herbivore':
            return HERBIVORE_METABOLISM
        return CARNIVORE_METABOLISM

    def sense_environment(self, herbivores_front, carnivores_front, plants_front,
                         herbivores_left, carnivores_left, plants_left,
                         herbivores_right, carnivores_right, plants_right,
                         herbivores_near, carnivores_near, plants_near):
        """
        Update sensor inputs based on nearby entities.

        Inputs 0-2: Front (herbivores, carnivores, plants)
        Inputs 3-5: Left
        Inputs 6-8: Right
        Inputs 9-11: Near (within radius 2)
        """
        self.inputs[0] = herbivores_front
        self.inputs[1] = carnivores_front
        self.inputs[2] = plants_front
        self.inputs[3] = herbivores_left
        self.inputs[4] = carnivores_left
        self.inputs[5] = plants_left
        self.inputs[6] = herbivores_right
        self.inputs[7] = carnivores_right
        self.inputs[8] = plants_right
        self.inputs[9] = herbivores_near
        self.inputs[10] = carnivores_near
        self.inputs[11] = plants_near

    def compute_outputs(self):
        """
        Compute neural network outputs using formula:
        o_j = b_j + Σ(u_i × w_ij)
        """
        self.outputs = self.biases + np.dot(self.inputs, self.weights)

    def choose_action(self) -> int:
        """Choose action with highest output value (winner-takes-all)."""
        return int(np.argmax(self.outputs))

    def turn_left(self):
        """Rotate 90 degrees counter-clockwise."""
        self.direction = (self.direction - 1) % 4

    def turn_right(self):
        """Rotate 90 degrees clockwise."""
        self.direction = (self.direction + 1) % 4

    def move(self):
        """Move 1-2 units in current direction (carnivores get a speed bonus)."""
        max_dist = MOVE_DISTANCE_MAX
        if self.agent_type == 'carnivore':
            max_dist += CARNIVORE_MOVE_BONUS
        distance = random.randint(MOVE_DISTANCE_MIN, max_dist)
        dx, dy = DIRECTION_VECTORS[self.direction]
        self.x += dx * distance
        self.y += dy * distance

    def execute_action(self, action: int):
        """Execute the chosen action."""
        if action == ACTION_TURN_LEFT:
            self.turn_left()
        elif action == ACTION_TURN_RIGHT:
            self.turn_right()
        elif action == ACTION_MOVE:
            self.move()
        # ACTION_EAT is handled by the world simulation

    def apply_metabolism(self):
        """Reduce energy based on metabolism rate."""
        self.energy -= self.get_metabolism()
        self.age += 1

        if self.energy <= 0:
            self.alive = False

    def is_outside_world(self) -> bool:
        """Check if agent is outside the world boundaries."""
        return (self.x < 0 or self.x >= WORLD_SIZE or
                self.y < 0 or self.y >= WORLD_SIZE)

    def can_reproduce(self) -> bool:
        """Check if agent has enough energy to reproduce."""
        return self.energy >= REPRODUCTION_THRESHOLD

    def eat(self, energy_gained: int):
        """Gain energy from eating (capped at MAX_ENERGY)."""
        self.energy = min(MAX_ENERGY, self.energy + energy_gained)

    def reproduce(self):
        """
        Create offspring with mutated neural network.
        Returns a new agent or None if reproduction fails.
        """
        if not self.can_reproduce():
            return None

        # Split energy
        child_energy = int(self.energy * REPRODUCTION_ENERGY_SPLIT)
        self.energy -= child_energy

        # Mutate weights
        mutated_weights = self.weights + np.random.uniform(
            -WEIGHT_MUTATION_RANGE, WEIGHT_MUTATION_RANGE,
            self.weights.shape
        )

        # Mutate biases
        mutated_biases = self.biases + np.random.uniform(
            -BIAS_MUTATION_RANGE, BIAS_MUTATION_RANGE,
            self.biases.shape
        )

        # Random position near parent
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        child_x = self.x + offset_x
        child_y = self.y + offset_y

        # Create child
        child = Agent(
            x=child_x,
            y=child_y,
            agent_type=self.agent_type,
            generation=self.generation + 1,
            weights=mutated_weights,
            biases=mutated_biases
        )
        child.energy = child_energy

        return child


class Herbivore(Agent):
    """Herbivore agent that eats plants."""

    def __init__(self, x: float, y: float, generation: int = 1,
                 weights=None, biases=None):
        super().__init__(x, y, 'herbivore', generation, weights, biases)


class Carnivore(Agent):
    """Carnivore agent that eats herbivores."""

    def __init__(self, x: float, y: float, generation: int = 1,
                 weights=None, biases=None):
        super().__init__(x, y, 'carnivore', generation, weights, biases)
