"""
Screen module initialization
"""

from .base_screen import BaseScreen
from .artwork_screen import ArtworkScreen
from .weather_screen import WeatherScreen
from .starmap_screen import StarmapScreen
from .system_screen import SystemScreen

__all__ = [
    'BaseScreen',
    'ArtworkScreen', 
    'WeatherScreen',
    'StarmapScreen',
    'SystemScreen'
]
