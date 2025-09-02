"""
Base Screen Class
All screen implementations should inherit from this base class.
Optimized for Raspberry Pi Zero 2 W performance.
"""

from abc import ABC, abstractmethod
from inky.auto import auto
import config

class BaseScreen(ABC):
    # Class variable to hold the shared display instance
    _shared_inky = None
    
    def __init__(self):
        # Initialize display only once and share across all screens
        if BaseScreen._shared_inky is None:
            BaseScreen._shared_inky = auto(ask_user=False, verbose=False)
        self.inky = BaseScreen._shared_inky
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
    
    @classmethod
    def cleanup_display(cls):
        """Clean up the shared display instance when shutting down."""
        if cls._shared_inky is not None:
            # Reset the display to a clean state
            try:
                cls._shared_inky.set_border(cls._shared_inky.WHITE)
                from PIL import Image
                clean_image = Image.new("P", (cls._shared_inky.width, cls._shared_inky.height), cls._shared_inky.WHITE)
                cls._shared_inky.set_image(clean_image)
                cls._shared_inky.show()
            except Exception as e:
                print(f"Error cleaning up display: {e}")
            cls._shared_inky = None
