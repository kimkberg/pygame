"""
First Pygame V2 - Interactive Animation and Particle System
===========================================================

A well-documented pygame application demonstrating modular architecture,
particle effects, character animations, and clean code practices.

Main Components:
    Game: Main game controller
    Character: Animated character system
    Firework: Particle-based firework effects
    ParticleCache: Performance-optimized sprite caching

Quick Start:
    >>> from first_pygame_v2.main import Game
    >>> game = Game()
    >>> game.run()

Version: 2.0.0
"""

__version__ = '2.0.0'
__all__ = [
    'Game',
    'Character', 
    'Firework',
    'ParticleCache',
    'BaseParticle',
    'PixelParticle',
    'HeartParticle',
    'InputHandler',
    'Renderer',
    'FireworkManager'
]

# Make key classes available at package level
from .main import Game
from .character import Character
from .particles import (
    Firework, 
    ParticleCache,
    BaseParticle,
    PixelParticle,
    HeartParticle
)
from .input_handler import InputHandler
from .renderer import Renderer
from .firework_manager import FireworkManager