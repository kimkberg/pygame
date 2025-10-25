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
import random
import sys
from config import *
from particles import Firework, ParticleCache
from character import Character


class Game:
    """Main game controller"""
    def __init__(self):
        """
        Initialize the game and all its subsystems.
        
        Sets up pygame, creates the display window, initializes the particle
        cache system, creates character instances, and prepares game state.
        """
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
        
        # Game state tracking
        self.fireworks = []  # List of active firework instances
        self.timers = {'space': 0, 'p': 0, 'kg': 0}  # Tracks continuous key presses
        self.running = True  # Controls main game loop
    
    def create_firework(self, particle_type="heart"):
        """
        Create a new firework at a random position with specified particle type.
        
        Args:
            particle_type (str): Type of particles to spawn on explosion.
                Options: "heart" for heart-shaped particles, "pixel" for rectangles.
        
        Returns:
            Firework: A new firework instance ready to be added to the game.
        """
        start_x = random.randint(50, WIDTH - 50)
        start_y = HEIGHT
        target_x = random.randint(100, WIDTH - 100)
        target_y = random.randint(50, HEIGHT // 2)
        color = random.choice(FIREWORK_COLORS)
        
        return Firework(start_x, start_y, target_x, target_y, color, particle_type, self.particle_cache)
    
    def handle_events(self):
        """
        Process pygame events like window close.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def handle_input(self, current_time):
        """
        Process continuous keyboard input and trigger appropriate actions.
        
        This method checks for held keys and triggers animations or spawns
        fireworks based on which keys are pressed. Uses timers to control
        the rate of continuous actions.
        
        Args:
            current_time (int): Current game time in milliseconds from pygame.time.get_ticks()
        
        Key Mappings:
            SPACE: Spawn heart fireworks continuously
            P: Spawn pixel fireworks continuously (disabled during K+G combo)
            LEFT: Trigger Kwimi's flip animation
            RIGHT: Trigger Grogu's flip animation
            K: Kwimi says something about Grogu
            G: Grogu says something about Kwimi
            K+G: Romance combo - rapid heart fireworks
        """
        keys = pygame.key.get_pressed()
        
        # Firework controls
        if keys[pygame.K_SPACE]:
            self.timers['space'] += 1
            if self.timers['space'] % 8 == 0:
                self.fireworks.append(self.create_firework("heart"))
        else:
            self.timers['space'] = 0
        
        if keys[pygame.K_p] and not (keys[pygame.K_k] and keys[pygame.K_g]):
            self.timers['p'] += 1
            if self.timers['p'] % 8 == 0:
                self.fireworks.append(self.create_firework("pixel"))
        else:
            self.timers['p'] = 0
        
        # Character animations
        if keys[pygame.K_LEFT] and not self.kwimi.animation['is_animating']:
            self.kwimi.start_animation(current_time)
        
        if keys[pygame.K_RIGHT] and not self.grogu.animation['is_animating']:
            self.grogu.start_animation(current_time)
        
        if keys[pygame.K_k] and not self.kwimi.animation['is_animating']:
            font = pygame.font.Font(None, 24)
            text = font.render(TEXT_KWIMI, True, WHITE)
            self.kwimi.start_animation(current_time, text)
        
        if keys[pygame.K_g] and not self.grogu.animation['is_animating']:
            font = pygame.font.Font(None, 24)
            text = font.render(TEXT_GROGU, True, WHITE)
            self.grogu.start_animation(current_time, text)
        
        # Romance combo
        if keys[pygame.K_k] and keys[pygame.K_g]:
            self.timers['kg'] += 1
            if self.timers['kg'] % 4 == 0:
                self.fireworks.append(self.create_firework("heart"))
        else:
            self.timers['kg'] = 0
    
    def update(self, current_time):
        """
        Update all game objects and clean up expired effects.
        
        Updates firework physics and animations, removes completed fireworks,
        and updates both character animations.
        
        Args:
            current_time (int): Current game time in milliseconds
        """
        # Update fireworks and filter out completed ones
        self.fireworks = [fw for fw in self.fireworks if fw.update()]
        self.kwimi.update(current_time)
        self.grogu.update(current_time)
    
    def draw(self):
        """
        Render all visual elements to the screen.
        
        Draws the background, ground line, characters, fireworks, and UI
        elements in the correct layering order. Completes with a display flip
        to show the rendered frame.
        """
        self.screen.fill((30, 30, 30))
        
        # Draw ground line
        pygame.draw.line(self.screen, WHITE, [0, HEIGHT // 2 + 32], [WIDTH, HEIGHT // 2 + 32], 10)
        
        # Draw characters
        self.kwimi.draw(self.screen)
        self.grogu.draw(self.screen)
        
        # Draw fireworks
        for firework in self.fireworks:
            firework.draw(self.screen)
        
        # Draw instructions
        self.draw_instructions()
        
        pygame.display.flip()
    
    def draw_instructions(self):
        """Draw control instructions"""
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "SPACE: Heart fireworks",
            "P: Pixel fireworks", 
            "K+G: Romance combo (hearts!)",
        ]
        
        for i, instruction in enumerate(instructions):
            surface = instruction_font.render(instruction, True, WHITE)
            self.screen.blit(surface, (10, 10 + i * 25))
    
    def run(self):
        """
        Execute the main game loop.
        
        Runs the core game loop at the configured FPS, processing events,
        handling input, updating game state, and rendering each frame until
        the user quits. Properly shuts down pygame on exit.
        
        The loop follows the standard game pattern:
            1. Get current time
            2. Handle events (window close, etc.)
            3. Process input (keyboard)
            4. Update game state (physics, animations)
            5. Render frame
            6. Cap framerate
        """
        while self.running:
            current_time = pygame.time.get_ticks()
            
            self.handle_events()
            self.handle_input(current_time)
            self.update(current_time)
            self.draw()
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()