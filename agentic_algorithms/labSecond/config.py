"""
Configuration parameters for the artificial life simulation.
"""

# World settings
WORLD_SIZE = 800  # NxN grid size
CELL_SIZE = 1  # Size of each cell in pixels for visualization

# Display settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
FPS = 60  # Target frames per second
ITERATIONS_PER_FRAME = 1  # Simulation steps per visual frame

# Population settings
INITIAL_PLANTS = 15000
INITIAL_HERBIVORES = 3000
INITIAL_CARNIVORES = 10

# Population limits (as fraction of initial)
MIN_POPULATION_RATIO = 0.25
MAX_POPULATION_RATIO = 0.50

# Energy settings
MAX_ENERGY = 100
PLANT_ENERGY = 35  # Energy gained from eating a plant (high to enable fast reproduction)
HERBIVORE_ENERGY = 100  # Energy gained from eating a herbivore (max to enable carnivore reproduction)

# Metabolism (energy loss per iteration)
HERBIVORE_METABOLISM = 1
CARNIVORE_METABOLISM = 1

# Reproduction settings
REPRODUCTION_THRESHOLD = 50  # Energy needed to reproduce (50% of max)
REPRODUCTION_ENERGY_SPLIT = 0.5  # Energy split between parent and child

# Mutation settings
WEIGHT_MUTATION_RANGE = 0.1  # +/- range for weight mutation
BIAS_MUTATION_RANGE = 0.05  # +/- range for bias mutation

# Neural network initialization
WEIGHT_INIT_RANGE = 1.0  # Initial weights in [-1, 1]
BIAS_INIT_RANGE = 0.5  # Initial biases in [-0.5, 0.5]

# Movement settings
MOVE_DISTANCE_MIN = 1
MOVE_DISTANCE_MAX = 2
CARNIVORE_MOVE_BONUS = 0  # Extra movement distance for carnivores (0 = same speed as herbivores)
VISION_RANGE = 15  # How far agents can see
EAT_RANGE = 3  # Range within which herbivores can eat plants
CARNIVORE_EAT_RANGE = 3  # Range within which carnivores can eat herbivores

# Simulation duration
MAX_ITERATIONS = 5000  # Total iterations to run
STATS_INTERVAL = 50  # How often to print stats

# Colors (RGB)
BACKGROUND_COLOR = (30, 30, 30)
PLANT_COLOR = (0, 200, 0)
HERBIVORE_COLOR = (0, 100, 255)
CARNIVORE_COLOR = (255, 50, 50)
TEXT_COLOR = (255, 255, 255)

# Agent display sizes
PLANT_SIZE = 2
HERBIVORE_SIZE = 3
CARNIVORE_SIZE = 4

# Directions (for agent orientation)
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

DIRECTION_VECTORS = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0)
}

# Action indices
ACTION_TURN_LEFT = 0
ACTION_TURN_RIGHT = 1
ACTION_MOVE = 2
ACTION_EAT = 3
