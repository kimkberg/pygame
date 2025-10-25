"""
Particle System Module
======================

Implements a flexible particle system for visual effects including fireworks
and explosions. Features multiple particle types (hearts, pixels) with physics
simulation, sprite caching for performance, and lifecycle management.

Classes:
    ParticleCache: Manages pre-loaded and scaled heart images
    BaseParticle: Abstract base with common particle physics
    PixelParticle: Simple rectangular particles for pixel-art style effects
    HeartParticle: Heart-shaped particles using cached sprites
    Firework: Complete firework with launch and explosion phases

Physics Features:
    - Gravity simulation
    - Air resistance/friction
    - Velocity-based movement
    - Alpha fading over lifetime
"""
import pygame
import math
import random
from config import FIREWORK_COLORS


class ParticleCache:
    """
    Manages a cache of pre-loaded and scaled heart images for performance.
    
    Pre-loading multiple sizes of the heart image prevents expensive scaling
    operations during particle creation and improves runtime performance.
    
    Attributes:
        cache (dict): Maps sizes (int) to pre-scaled pygame.Surface objects
    """
    
    def __init__(self):
        self.cache = {}
    
    def preload_heart_images(self, heart_path):
        """
        Load and cache heart images at multiple common sizes.
        
        Attempts to load a heart image from the specified path and creates
        scaled versions at predefined sizes. Falls back to pink rectangles
        if the image cannot be loaded.
        
        Args:
            heart_path (str): File path to the heart image (PNG recommended)
        
        Cached Sizes:
            20, 25, 30, 35, 40, 45 pixels (square dimensions)
        """
        try:
            heart = pygame.image.load(heart_path).convert_alpha()
            sizes = [20, 25, 30, 35, 40, 45]
            for size in sizes:
                self.cache[size] = pygame.transform.scale(heart, (size, size))
        except (pygame.error, FileNotFoundError):
            print("Could not load heart image, using rectangles instead")
            for size in [20, 25, 30, 35, 40, 45]:
                heart_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                heart_surface.fill((255, 182, 203, 255))
                self.cache[size] = heart_surface
    
    def get_cached_heart(self, size):
        """
        Retrieve a cached heart image of the specified size.
        
        Returns the exact size if cached, or the closest available size if
        the difference is small (<= 5 pixels). For larger differences,
        scales the closest cached image and caches the new size.
        
        Args:
            size (int): Desired heart image size in pixels
        
        Returns:
            pygame.Surface: Heart image at the requested size, or None if cache is empty
        """
        available_sizes = list(self.cache.keys())
        if not available_sizes:
            return None
        
        closest_size = min(available_sizes, key=lambda x: abs(x - size))
        
        if closest_size == size:
            return self.cache[closest_size]
        
        if abs(closest_size - size) <= 5:
            return self.cache[closest_size]
        
        if size not in self.cache:
            self.cache[size] = pygame.transform.scale(self.cache[closest_size], (size, size))
        
        return self.cache[size]


class BaseParticle:
    """
    Base class for all particle types with shared physics simulation.
    
    Implements common particle behavior including gravity, air resistance,
    lifetime tracking, and alpha-based color fading. Subclasses should
    override the draw() method for custom rendering.
    
    Attributes:
        x, y (float): Current particle position in screen coordinates
        v_x, v_y (float): Velocity components in pixels per frame
        color (tuple): Original RGB color (0-255 for each channel)
        current_color (tuple): Faded color based on remaining lifetime
        size (int): Particle size in pixels
        life_time (int): Remaining lifetime in frames
        max_life (int): Initial lifetime for fade calculations
        gravity (float): Downward acceleration per frame
    """
    
    def __init__(self, x, y, v_x, v_y, color, size, life_time):
        """
        Initialize a new particle with physics properties.
        
        Args:
            x (float): Starting x-coordinate
            y (float): Starting y-coordinate
            v_x (float): Initial horizontal velocity (pixels/frame)
            v_y (float): Initial vertical velocity (pixels/frame)
            color (tuple): RGB color tuple (r, g, b) with values 0-255
            size (int): Particle size in pixels
            life_time (int): How many frames the particle should exist
        """
        self.x = x
        self.y = y
        self.v_x = v_x
        self.v_y = v_y
        self.color = color
        self.current_color = color
        self.size = size
        self.life_time = life_time
        self.max_life = life_time
        self.gravity = 0.1

    def update(self):
        """
        Update particle physics and lifetime for one frame.
        
        Applies velocity to position, adds gravity, applies air resistance,
        decrements lifetime, and calculates faded color based on remaining life.
        
        Returns:
            bool: True if particle is still alive, False if lifetime expired
        """
        # Apply velocity to position
        self.x += self.v_x
        self.y += self.v_y
        
        # Apply physics forces
        self.v_y += self.gravity  # Gravity pulls down
        self.v_x *= 0.99  # Air resistance slows horizontal movement

        # Age the particle
        self.life_time -= 1

        # Fade color proportionally to remaining life (alpha blending)
        alpha = self.life_time / self.max_life
        self.current_color = (
            int(self.color[0] * alpha),
            int(self.color[1] * alpha),
            int(self.color[2] * alpha)
        )

        return self.life_time > 0
    
    def draw(self, screen):
        """
        Render the particle to the screen. Override in subclasses.
        
        Args:
            screen (pygame.Surface): Surface to draw on
        """
        pass


class PixelParticle(BaseParticle):
    """
    Simple rectangular particles for retro pixel-art style effects.
    
    Draws as small colored squares, useful for traditional firework effects
    or when heart images are not desired.
    """
    
    def draw(self, screen):
        """
        Draw particle as a colored rectangle.
        
        Args:
            screen (pygame.Surface): Surface to draw on
        """
        if self.life_time > 0:
            particle_rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
            pygame.draw.rect(screen, self.current_color, particle_rect)


class HeartParticle(BaseParticle):
    """
    Heart-shaped particles using pre-cached sprite images.
    
    Uses the ParticleCache to retrieve appropriately sized heart images,
    applying alpha transparency for smooth fading effects.
    
    Attributes:
        heart_image (pygame.Surface): Cached heart sprite for this size
    """
    
    def __init__(self, x, y, v_x, v_y, color, size, life_time, particle_cache):
        """
        Create a heart particle with cached sprite.
        
        Args:
            x, y (float): Starting position
            v_x, v_y (float): Initial velocity
            color (tuple): RGB color (not used directly, sprite has own color)
            size (int): Desired heart size in pixels
            life_time (int): Lifetime in frames
            particle_cache (ParticleCache): Cache to retrieve heart sprite from
        """
        super().__init__(x, y, v_x, v_y, color, size, life_time)
        self.heart_image = particle_cache.get_cached_heart(size)
    
    def draw(self, screen):
        """
        Draw heart sprite with alpha fading.
        
        Args:
            screen (pygame.Surface): Surface to draw on
        """
        if self.life_time > 0 and self.heart_image:
            # Calculate fade alpha (0-255)
            alpha = int(255 * (self.life_time / self.max_life))
            
            if alpha < 255:
                # Create faded copy for this frame
                faded_heart = self.heart_image.copy()
                faded_heart.set_alpha(alpha)
                screen.blit(faded_heart, (int(self.x), int(self.y)))
            else:
                # Full opacity, draw directly
                screen.blit(self.heart_image, (int(self.x), int(self.y)))


class Firework:
    """
    Complete firework effect with launch and explosion phases.
    
    Simulates a firework that launches from a starting point toward a target,
    then explodes into multiple particles when it reaches the destination.
    
    Lifecycle:
        1. Launch phase: Projectile moves toward target with trailing effect
        2. Explosion trigger: When near target, spawns particle burst
        3. Particle phase: Individual particles follow physics until they fade
    
    Attributes:
        x, y (float): Current projectile position
        target_x, target_y (float): Destination coordinates
        color (tuple): RGB color for projectile and particles
        particle_type (str): "heart" or "pixel" for explosion particles
        particle_cache (ParticleCache): Cache for heart sprites (if needed)
        v_x, v_y (float): Projectile velocity components
        exploded (bool): Whether explosion has occurred
        particles (list): Active particles from explosion
    """
    
    def __init__(self, x, y, target_x, target_y, color, particle_type="heart", particle_cache=None):
        """
        Create a new firework.
        
        Args:
            x, y (float): Launch position
            target_x, target_y (float): Explosion point
            color (tuple): RGB color tuple
            particle_type (str): "heart" or "pixel" for particle style
            particle_cache (ParticleCache): Required if using heart particles
        """
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.color = color
        self.particle_type = particle_type
        self.particle_cache = particle_cache
        # Calculate velocity to reach target (2% of distance per frame)
        self.v_x = (target_x - x) * 0.02
        self.v_y = (target_y - y) * 0.02
        self.exploded = False
        self.particles = []

    def update(self):
        """
        Update firework state for one frame.
        
        In launch phase: moves toward target, checks for arrival.
        In explosion phase: updates all particles and removes dead ones.
        
        Returns:
            bool: True if firework still active (launching or has particles),
                  False if completely finished
        """
        if not self.exploded:
            # Launch phase: move toward target
            self.x += self.v_x
            self.y += self.v_y

            # Check if close enough to target (within 10 pixels)
            if abs(self.x - self.target_x) < 10 and abs(self.y - self.target_y) < 10:
                self.explode()
        else:
            # Explosion phase: update particles and remove dead ones
            self.particles = [p for p in self.particles if p.update()]

        return len(self.particles) > 0 or not self.exploded
    
    def explode(self):
        """
        Trigger the explosion, creating a burst of particles.
        
        Spawns 5-15 particles radiating in random directions with varying
        speeds, sizes, and lifetimes. Particle properties depend on the
        particle_type setting.
        """
        self.exploded = True
        particle_count = random.randint(5, 15)  # Random number of particles

        for _ in range(particle_count):
            # Random direction (angle in radians)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            # Convert polar to Cartesian coordinates
            v_x = math.cos(angle) * speed
            v_y = math.sin(angle) * speed

            # Particle properties vary by type
            if self.particle_type == "heart":
                size = random.randint(25, 40)  # Larger hearts
                life_time = random.randint(30, 60)  # Longer life
            else:  # pixel particles
                size = random.randint(2, 6)  # Smaller pixels
                life_time = random.randint(20, 40)  # Shorter life
            
            # Add color variation (±30 to each RGB channel)
            color_variant = (
                min(255, max(0, self.color[0] + random.randint(-30, 30))),
                min(255, max(0, self.color[1] + random.randint(-30, 30))),
                min(255, max(0, self.color[2] + random.randint(-30, 30)))
            )

            # Create appropriate particle type
            if self.particle_type == "heart":
                particle = HeartParticle(self.x, self.y, v_x, v_y, color_variant, 
                                        size, life_time, self.particle_cache)
            else:
                particle = PixelParticle(self.x, self.y, v_x, v_y, color_variant, 
                                        size, life_time)
            
            self.particles.append(particle)

    def draw(self, screen):
        """
        Render the firework in its current state.
        
        Launch phase: Draws projectile with fading trail.
        Explosion phase: Draws all active particles.
        
        Args:
            screen (pygame.Surface): Surface to draw on
        """
        if not self.exploded:
            # Draw the ascending projectile
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
            
            # Draw motion trail behind projectile
            for i in range(5):
                trail_x = int(self.x - self.v_x * i * 2)
                trail_y = int(self.y - self.v_y * i * 2)
                # Fade trail progressively
                alpha = 1 - (i * 0.2)
                trail_color = (
                    int(self.color[0] * alpha),
                    int(self.color[1] * alpha),
                    int(self.color[2] * alpha)
                )
                # Shrink trail circles progressively
                pygame.draw.circle(screen, trail_color, (trail_x, trail_y), max(1, 3 - i))
        else:
            # Draw all explosion particles
            for particle in self.particles:
                particle.draw(screen)