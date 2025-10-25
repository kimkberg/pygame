"""
Renderer Module
===============

Handles all rendering and drawing operations for the game.

Classes:
    Renderer: Manages screen drawing for characters, fireworks, and UI
"""
import pygame
from config import WIDTH, HEIGHT, WHITE

class Renderer:
    """
    Handles rendering of all game elements to the screen.
    """
    def __init__(self, screen):
        self.screen = screen

    def draw_frame(self, kwimi, grogu, fireworks):
        """
        Draw a complete frame including background, characters, and effects.
        
        Args:
            kwimi: Character instance for Kwimi
            grogu: Character instance for Grogu
            fireworks: List of active Firework instances
        """
        self.screen.fill((30, 30, 30))

        # Draw ground line
        pygame.draw.line(self.screen, WHITE, [0, HEIGHT // 2 + 32], [WIDTH, HEIGHT // 2 + 32], 10)

        # Draw characters
        kwimi.draw(self.screen)
        grogu.draw(self.screen)

        # Draw fireworks
        for firework in fireworks:
            firework.draw(self.screen)

        # Draw instructions
        self._draw_instructions()

    def _draw_instructions(self):
        """Draw control instructions at the top-left."""
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "SPACE: Heart fireworks",
            "P: Pixel fireworks", 
            "K+G: Romance combo (hearts!)",
        ]
        
        for i, instruction in enumerate(instructions):
            surface = instruction_font.render(instruction, True, WHITE)
            self.screen.blit(surface, (10, 10 + i * 25))