"""Game configuration and constants"""
import pygame

# =============================================================================
# Display Settings
# =============================================================================
WIDTH, HEIGHT = 800, 600  # Window resolution in pixels
FPS = 60  # Target frames per second for smooth animation

# =============================================================================
# Color Definitions (RGB format: 0-255)
# =============================================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# =============================================================================
# Animation Settings
# =============================================================================
ANIMATION_DURATION = 600  # Character animation length in milliseconds
BOUNCE_AMPLITUDE = 50  # Maximum vertical bounce height in pixels

# =============================================================================
# Firework Settings
# =============================================================================
# Color palette for random firework selection
FIREWORK_COLORS = [
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green
    (100, 100, 255),  # Blue
    (255, 255, 100),  # Yellow
    (255, 100, 255),  # Magenta
    (100, 255, 255),  # Cyan
    (255, 200, 100),  # Orange
    (200, 100, 255),  # Purple
]

# =============================================================================
# Character Text Content
# =============================================================================
TEXT_KWIMI = "Grogu is so cutie"  # Text displayed when 'K' key is pressed
TEXT_GROGU = "Kwomiiiii"  # Text displayed when 'G' key is pressed

# =============================================================================
# Asset File Paths
# =============================================================================
# Note: Update these paths to match your actual image file locations
HEART_IMAGE_PATH = 'v1/heart.png'  # Path to heart particle image
FACE_IMAGE_PATH = 'v1/derp.png'  # Path to character face image