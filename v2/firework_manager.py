"""
Firework Manager Module
=======================

Manages the creation, updating, and lifecycle of fireworks.

Classes:
    FireworkManager: Handles a list of fireworks and their operations
"""
from particles import Firework
import random
from config import WIDTH, HEIGHT, FIREWORK_COLORS


class FireworkManager:
    """
    Manages active fireworks, including adding new ones and updating them.
    """
    def __init__(self, particle_cache):
        self.fireworks = []
        self.particle_cache = particle_cache
    
    def add_firework(self, particle_type="heart"):
        """
        Create and add a new firework to the list.
        
        Args:
            particle_type (str): "heart" or "pixel"
        """
        
        start_x = random.randint(50, WIDTH - 50)
        start_y = HEIGHT
        target_x = random.randint(100, WIDTH - 100)
        target_y = random.randint(50, HEIGHT // 2)
        color = random.choice(FIREWORK_COLORS)
        
        firework = Firework(start_x, start_y, target_x, target_y, color, particle_type, self.particle_cache)
        self.fireworks.append(firework)
    
    def update_fireworks(self):
        """
        Update all fireworks and remove completed ones.
        
        Returns:
            List of active fireworks
        """
        self.fireworks = [fw for fw in self.fireworks if fw.update()]
        return self.fireworks
    
    def get_fireworks(self):
        """Return the current list of fireworks."""
        return self.fireworks