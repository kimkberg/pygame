"""
Main Game Module
================
Features:
    - Dual character animation system with bounce effects
    - Particle-based firework system (hearts and pixels)
    - Keyboard-driven interactions and special combo moves
    - Modular architecture with separated concerns

Usage:
    Run this file directly to start the game:
        python main.py
    
    Or import the Game class:
        from main import Game
        game = Game()
        game.run()
"""
import pygame
import sys
from config import WIDTH, HEIGHT, FPS, FACE_IMAGE_PATH, HEART_IMAGE_PATH
from particles import ParticleCache
from character import Character
from input_handler import InputHandler
from renderer import Renderer
from firework_manager import FireworkManager


class Game:
    """Main game controller"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pygame Organized Game")
        self.clock = pygame.time.Clock()
        
        # Initialize particle system with cached images for performance
        self.particle_cache = ParticleCache()
        self.particle_cache.preload_heart_images(HEART_IMAGE_PATH)
        
        # Create two characters at different positions
        self.kwimi = Character(FACE_IMAGE_PATH, [100, HEIGHT // 2 - 32], "Kwimi", flipped=True)
        self.grogu = Character(FACE_IMAGE_PATH, [WIDTH - 164, HEIGHT // 2 - 32], "Grogu")
        
        # Initialize subsystems
        self.input_handler = InputHandler()
        self.renderer = Renderer(self.screen)
        self.firework_manager = FireworkManager(self.particle_cache)

        # Running state
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()

            self.handle_events()
            keys = pygame.key.get_pressed()
            self.input_handler.process_input(keys, self.kwimi, self.grogu, self.firework_manager, current_time)
            
            self.firework_manager.update_fireworks()
            self.kwimi.update(current_time)
            self.grogu.update(current_time)

            self.renderer.draw_frame(self.kwimi, self.grogu, self.firework_manager.get_fireworks())
            
            pygame.display.update()

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()