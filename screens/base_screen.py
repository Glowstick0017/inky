"""
Base Screen Class
All screen implementations should inherit from this base class.
Optimized for Raspberry Pi Zero 2 W performance.
"""

from abc import ABC, abstractmethod
from inky.auto import auto
import config

class BaseScreen(ABC):
    def __init__(self):
        # Initialize display once and reuse
        self.inky = auto(ask_user=False, verbose=False)
        self.update_interval = 300  # Default 5 minutes (from config)
        
    @abstractmethod
    def display(self):
        """Display the screen content. Must be implemented by subclasses."""
        pass
        
    def clear_screen(self):
        """Clear the screen to white."""
        from PIL import Image
        image = Image.new("P", (self.inky.width, self.inky.height), self.inky.WHITE)
        self.inky.set_image(image)
        self.inky.show()
