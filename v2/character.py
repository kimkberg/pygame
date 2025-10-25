"""
Character Animation Module
==========================

Provides an animated character system with smooth bounce effects, scaling,
flipping, and text bubble support. Uses easing functions for natural-looking
motion.

Classes:
    Character: Fully animated character with image loading, transformations,
               and text overlay capabilities

Features:
    - Automatic flip animation with bounce physics
    - Scale transformation during animation
    - Text bubble overlay during animations
    - Graceful fallback to colored rectangles if images fail to load
"""
import pygame
import math
from config import ANIMATION_DURATION, BOUNCE_AMPLITUDE, WHITE
from utils import ease_out_bounce


class Character:
    """
    An animated character face with bounce effects and text overlays.
    
    Manages character image loading, flip animations, bounce physics, and
    optional text rendering. Animations use easing functions for smooth,
    natural-looking motion.
    
    Attributes:
        name (str): Character display name
        position (list): Base [x, y] screen coordinates
        src_image (pygame.Surface): Original character image (never modified)
        current_image (pygame.Surface): Currently displayed image (may be transformed)
        current_bounce (float): Current vertical offset from bounce animation
        animation (dict): Animation state including timing, scale, flip, and text
    
    Animation State Keys:
        is_animating (bool): Whether animation is active
        start_time (int): Animation start time in milliseconds
        duration (int): Total animation duration in milliseconds
        start_scale, target_scale (float): Scale transformation bounds
        bounce_height (float): Current vertical bounce offset
        bounce_amp (int): Maximum bounce height in pixels
        flipped (bool): Whether image is currently flipped
        text (pygame.Surface): Optional text to display during animation
    """
    
    def __init__(self, image_path, position, name, size=(64, 64), flipped=False):
        """
        Create a new character with specified image and properties.
        
        Args:
            image_path (str): Path to character image file
            position (list): Initial [x, y] screen position
            name (str): Display name for this character
            size (tuple): Desired (width, height) in pixels, default (64, 64)
            flipped (bool): Whether to initially flip the image horizontally
        """
        self.name = name
        self.position = position
        self.src_image = self.load_image(image_path, size, flipped)
        self.current_image = self.src_image.copy()
        self.current_bounce = 0
        
        # Animation state dictionary
        self.animation = {
            'is_animating': False,
            'start_time': 0,
            'duration': ANIMATION_DURATION,
            'start_scale': 1.0,
            'target_scale': 1.2,  # 20% larger at peak
            'bounce_height': 0,
            'bounce_amp': BOUNCE_AMPLITUDE,
            'flipped': False,
            'text': None  # Optional text surface to display
        }
    
    def load_image(self, filename, size, flip):
        """
        Load and transform character image with error handling.
        
        Attempts to load the image file, scale it to the desired size, and
        optionally flip it. If loading fails, creates a red placeholder square.
        
        Args:
            filename (str): Path to image file
            size (tuple): Desired (width, height)
            flip (bool): Whether to flip horizontally
        
        Returns:
            pygame.Surface: Loaded and transformed image, or placeholder
        """
        try:
            image = pygame.image.load(filename).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            if flip:
                image = pygame.transform.flip(image, True, False)
            return image
        except (pygame.error, FileNotFoundError):
            print(f"Could not load image: {filename}")
            # Create red placeholder rectangle
            placeholder = pygame.Surface(size)
            placeholder.fill((255, 0, 0))
            return placeholder
    
    def start_animation(self, current_time, text=None):
        """
        Initiate a new bounce animation with optional text overlay.
        
        Only starts if no animation is currently active. Flips the character
        and can display a text bubble during the animation.
        
        Args:
            current_time (int): Current game time in milliseconds
            text (pygame.Surface, optional): Rendered text to display during animation
        """
        if not self.animation['is_animating']:
            self.animation['is_animating'] = True
            self.animation['start_time'] = current_time
            self.animation['flipped'] = not self.animation['flipped']
            self.animation['text'] = text
    
    def update(self, current_time):
        """
        Update animation state for the current frame.
        
        Calculates animation progress, applies easing function for smooth motion,
        updates scale and bounce transformations, and modifies the current_image
        accordingly. Automatically ends animation when duration is complete.
        
        Args:
            current_time (int): Current game time in milliseconds
        """
        if not self.animation['is_animating']:
            return
        
        # Calculate animation progress (0.0 to 1.0)
        elapsed = current_time - self.animation['start_time']
        progress = min(elapsed / self.animation['duration'], 1.0)
        
        # End animation when complete
        if progress >= 1.0:
            self.animation['is_animating'] = False
            return
        
        # Apply bounce easing for natural motion
        bounce_progress = ease_out_bounce(progress)
        # Scale from 1.0 to target_scale and back
        scale = 1.0 + (self.animation['target_scale'] - 1.0) * (1.0 - bounce_progress)
        # Vertical bounce using sine wave (peaks at 0.5 progress)
        bounce_height = math.sin(progress * math.pi) * self.animation['bounce_amp']
        
        # Apply transformations to image
        img = self.src_image
        
        # Flip if needed
        if self.animation['flipped']:
            img = pygame.transform.flip(img, True, False)
        
        # Scale if changed
        if scale != 1.0:
            new_width = int(img.get_width() * scale)
            new_height = int(img.get_height() * scale)
            img = pygame.transform.scale(img, (new_width, new_height))
        
        # Update display state
        self.current_image = img
        self.current_bounce = -bounce_height  # Negative = upward
    
    def draw(self, screen):
        """
        Render the character, name label, and optional text to the screen.
        
        Draws the (possibly transformed) character image at the calculated
        position including bounce offset, displays the character name above,
        and shows any active text bubble.
        
        Args:
            screen (pygame.Surface): Surface to draw on
        """
        # Calculate position accounting for scaling and bounce
        # Center scaled image on original position
        draw_pos = [
            self.position[0] - (self.current_image.get_width() - 64) // 2,
            self.position[1] + self.current_bounce - (self.current_image.get_height() - 64) // 2
        ]
        
        # Draw character image
        screen.blit(self.current_image, draw_pos)
        
        # Draw name label above character
        font = pygame.font.Font(None, 36)
        label = font.render(self.name, True, WHITE)
        screen.blit(label, (self.position[0], draw_pos[1] - 40))
        
        # Draw text bubble during animation if present
        if self.animation.get('text') and self.animation['is_animating']:
            # Position text to the side based on character name
            text_offset = 80 if self.name == "Kwimi" else -80
            text_pos = (draw_pos[0] + text_offset, draw_pos[1])
            screen.blit(self.animation['text'], text_pos)