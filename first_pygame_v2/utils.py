"""
Utility Functions Module
========================

Provides reusable utility functions for image loading and animation easing.
These helper functions are used across multiple modules for common tasks.

Functions:
    load_image: Load and transform images with error handling
    ease_out_bounce: Bounce easing function for natural motion
    ease_out_elastic: Elastic easing for springy effects

Easing Functions:
    Mathematical functions that map linear time progression (0.0 to 1.0)
    to non-linear motion curves, creating more natural-looking animations.
    
    Reference: https://easings.net/
"""
import pygame
import math
from config import RED, GREEN


def load_image(filename, size=None, flip=None):
    """
    Load an image file with optional transformations and error handling.
    
    Attempts to load a pygame image, scale it if size is specified, and flip
    it if requested. Falls back to a colored placeholder rectangle if the
    file cannot be loaded.
    
    Args:
        filename (str): Path to image file (PNG, JPG, etc.)
        size (tuple, optional): Desired (width, height) to scale to
        flip (bool, optional): If True, flip image horizontally
    
    Returns:
        pygame.Surface: Loaded and transformed image, or placeholder
    
    Examples:
        >>> img = load_image('sprite.png')  # Load as-is
        >>> img = load_image('sprite.png', (64, 64))  # Load and scale
        >>> img = load_image('sprite.png', (64, 64), True)  # Load, scale, and flip
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
        # Create fallback colored rectangle
        placeholder = pygame.Surface((64, 64))
        placeholder.fill(RED if "face1" in filename else GREEN)
        return placeholder


def ease_out_bounce(t):
    """
    Bounce easing function for smooth, natural bounce motion.
    
    Maps linear time progression to a bouncing curve that decelerates and
    bounces multiple times before settling. Creates realistic physics-like
    motion without actual physics simulation.
    
    The function has 4 distinct bounce phases with decreasing amplitude,
    similar to a ball bouncing and coming to rest.
    
    Args:
        t (float): Time progression from 0.0 (start) to 1.0 (end)
    
    Returns:
        float: Eased value (typically 0.0 to 1.0 range with bounces)
    
    Math:
        Uses quadratic curves (7.5625 * t²) in each bounce phase for
        smooth acceleration/deceleration.
    
    Example:
        >>> ease_out_bounce(0.0)  # Returns 0.0 (start)
        >>> ease_out_bounce(0.5)  # Returns ~0.76 (mid-bounce)
        >>> ease_out_bounce(1.0)  # Returns 1.0 (settled)
    """
    if t < 1/2.75:
        return 7.5625 * t * t
    elif t < 2/2.75:
        t -= 1.5/2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5/2.75:
        t -= 2.25/2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625/2.75
        return 7.5625 * t * t + 0.984375

def ease_out_elastic(t):
    """Elastic easing function for a more playful bounce"""
    # Handle edge cases
    if t == 0:
        return 0
    if t == 1:
        return 1
    
    # Elastic parameters
    p = 0.3  # Period - controls bounciness
    s = p / 4  # Phase shift
    
    # Exponentially decaying sinusoid
    return (2 ** (-10 * t)) * math.sin((t - s) * (2 * math.pi) / p) + 1