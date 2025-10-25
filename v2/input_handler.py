"""
Input Handler Module
====================

Handles keyboard input processing, including timers for continuous actions
and triggering character animations or fireworks.

Classes:
    InputHandler: Processes pygame key states and manages input timers
"""
import pygame
from config import TEXT_KWIMI, TEXT_GROGU, WHITE

class InputHandler:
    """
    Manages keyboard input and triggers game actions.
    
    Tracks timers for continuous key presses and provides methods to
    process input for characters and fireworks.
    """
    def __init__(self):
        self.timers = {'space': 0, 'p': 0, 'kg': 0}

    def process_input(self, keys, kwimi, grogu, firework_manager, current_time):
        """
        Process keyboard input and trigger actions.
        
        Args:
            keys: Pygame key state from pygame.key.get_pressed()
            kwimi: Character instance for Kwimi
            grogu: Character instance for Grogu
            firework_manager: FireworkManager instance
            current_time: Current time in milliseconds
        """
        # Firework controls
        if keys[pygame.K_SPACE]:
            self.timers['space'] += 1
            if self.timers['space'] % 8 == 0:
                firework_manager.add_firework("heart")
        else:
            self.timers['space'] = 0

        if keys[pygame.K_p] and not (keys[pygame.K_k] and keys[pygame.K_g]):
            self.timers['p'] += 1
            if self.timers['p'] % 8 == 0:
                firework_manager.add_firework("pixel")
        else:
            self.timers['p'] = 0

        # Character animations
        if keys[pygame.K_LEFT] and not kwimi.animation['is_animating']:
            kwimi.start_animation(current_time)
        
        if keys[pygame.K_RIGHT] and not grogu.animation['is_animating']:
            grogu.start_animation(current_time)
        
        if keys[pygame.K_k] and not kwimi.animation['is_animating']:
            font = pygame.font.Font(None, 24)
            text = font.render(TEXT_KWIMI, True, WHITE)
            kwimi.start_animation(current_time, text)
        
        if keys[pygame.K_g] and not grogu.animation['is_animating']:
            font = pygame.font.Font(None, 24)
            text = font.render(TEXT_GROGU, True, WHITE)
            grogu.start_animation(current_time, text)

        # Romance combo
        if keys[pygame.K_k] and keys[pygame.K_g]:
            self.timers['kg'] += 1
            if self.timers['kg'] % 4 == 0:
                firework_manager.add_firework("heart")
        else:
            self.timers['kg'] = 0