"""
Visualization module for the artificial life simulation.
Uses Pygame for real-time rendering.
"""

import pygame
import math
from typing import Optional
from world import World
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WORLD_SIZE, FPS,
    BACKGROUND_COLOR, PLANT_COLOR, HERBIVORE_COLOR, CARNIVORE_COLOR,
    TEXT_COLOR, PLANT_SIZE, HERBIVORE_SIZE, CARNIVORE_SIZE,
    DIRECTION_VECTORS
)


class Visualizer:
    """Handles all visualization using Pygame."""

    def __init__(self, world: World):
        self.world = world
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self.running = False
        self.paused = False

        # Scaling factors
        self.scale_x = WINDOW_WIDTH / WORLD_SIZE
        self.scale_y = WINDOW_HEIGHT / WORLD_SIZE

    def initialize(self):
        """Initialize Pygame and create window."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Artificial Life Simulation - Food Chain")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.running = True

    def world_to_screen(self, x: float, y: float) -> tuple:
        """Convert world coordinates to screen coordinates."""
        # Clamp to visible area for display purposes
        screen_x = int(max(0, min(x, WORLD_SIZE)) * self.scale_x)
        screen_y = int(max(0, min(y, WORLD_SIZE)) * self.scale_y)
        return (screen_x, screen_y)

    def handle_events(self) -> bool:
        """Process Pygame events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    # Reset simulation
                    self.world.__init__()
                    self.world.initialize()
        return True

    def draw_plants(self):
        """Draw all alive plants."""
        for plant in self.world.plants:
            if plant.alive:
                pos = self.world_to_screen(plant.x, plant.y)
                pygame.draw.circle(self.screen, PLANT_COLOR, pos, PLANT_SIZE)

    def draw_agents(self):
        """Draw all herbivores and carnivores."""
        # Draw herbivores
        for herbivore in self.world.herbivores:
            if herbivore.alive:
                pos = self.world_to_screen(herbivore.x, herbivore.y)
                pygame.draw.circle(self.screen, HERBIVORE_COLOR, pos, HERBIVORE_SIZE)

                # Draw direction indicator
                dx, dy = DIRECTION_VECTORS[herbivore.direction]
                end_x = pos[0] + dx * 6
                end_y = pos[1] + dy * 6
                pygame.draw.line(self.screen, HERBIVORE_COLOR, pos, (end_x, end_y), 1)

        # Draw carnivores
        for carnivore in self.world.carnivores:
            if carnivore.alive:
                pos = self.world_to_screen(carnivore.x, carnivore.y)
                pygame.draw.circle(self.screen, CARNIVORE_COLOR, pos, CARNIVORE_SIZE)

                # Draw direction indicator
                dx, dy = DIRECTION_VECTORS[carnivore.direction]
                end_x = pos[0] + dx * 8
                end_y = pos[1] + dy * 8
                pygame.draw.line(self.screen, CARNIVORE_COLOR, pos, (end_x, end_y), 1)

    def draw_stats(self):
        """Draw statistics overlay."""
        stats_lines = [
            f"Iteration: {self.world.iteration}",
            f"Plants: {sum(1 for p in self.world.plants if p.alive)}",
            f"Herbivores: {len(self.world.herbivores)}",
            f"Carnivores: {len(self.world.carnivores)}",
        ]

        if self.world.herbivores:
            avg_gen = sum(h.generation for h in self.world.herbivores) / len(self.world.herbivores)
            stats_lines.append(f"Herb. Avg Gen: {avg_gen:.1f}")

        if self.world.carnivores:
            avg_gen = sum(c.generation for c in self.world.carnivores) / len(self.world.carnivores)
            stats_lines.append(f"Carn. Avg Gen: {avg_gen:.1f}")

        # Add control hints
        stats_lines.append("")
        stats_lines.append("SPACE: Pause | ESC: Quit | R: Reset")

        if self.paused:
            stats_lines.insert(0, "** PAUSED **")

        # Draw semi-transparent background for stats
        stats_height = len(stats_lines) * 20 + 10
        stats_surface = pygame.Surface((200, stats_height))
        stats_surface.fill((0, 0, 0))
        stats_surface.set_alpha(180)
        self.screen.blit(stats_surface, (5, 5))

        # Draw text
        y_offset = 10
        for line in stats_lines:
            if line.startswith("**"):
                text_color = (255, 255, 0)  # Yellow for paused
            else:
                text_color = TEXT_COLOR
            text = self.font.render(line, True, text_color)
            self.screen.blit(text, (10, y_offset))
            y_offset += 20

    def draw_legend(self):
        """Draw color legend."""
        legend_x = WINDOW_WIDTH - 120
        legend_y = 10

        # Background
        legend_surface = pygame.Surface((110, 80))
        legend_surface.fill((0, 0, 0))
        legend_surface.set_alpha(180)
        self.screen.blit(legend_surface, (legend_x - 5, legend_y - 5))

        # Legend items
        items = [
            (PLANT_COLOR, "Plants"),
            (HERBIVORE_COLOR, "Herbivores"),
            (CARNIVORE_COLOR, "Carnivores")
        ]

        for i, (color, label) in enumerate(items):
            pygame.draw.circle(self.screen, color, (legend_x + 10, legend_y + i * 25 + 10), 6)
            text = self.small_font.render(label, True, TEXT_COLOR)
            self.screen.blit(text, (legend_x + 25, legend_y + i * 25 + 3))

    def render(self):
        """Render the current frame."""
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)

        # Draw world boundary
        pygame.draw.rect(self.screen, (60, 60, 60),
                        (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 2)

        # Draw entities
        self.draw_plants()
        self.draw_agents()

        # Draw UI
        self.draw_stats()
        self.draw_legend()

        # Update display
        pygame.display.flip()

    def tick(self):
        """Maintain target frame rate."""
        self.clock.tick(FPS)

    def cleanup(self):
        """Clean up Pygame resources."""
        pygame.quit()

    def is_running(self) -> bool:
        """Check if visualization should continue."""
        return self.running

    def set_running(self, value: bool):
        """Set running state."""
        self.running = value
