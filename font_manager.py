"""
Font Manager for Raspberry Pi E-ink Display
Handles font loading with fallbacks optimized for Raspberry Pi Zero 2W
"""

from PIL import ImageFont
import os

class FontManager:
    def __init__(self):
        self.font_cache = {}
        
        # Font paths in order of preference for Raspberry Pi
        self.font_paths = {
            'roboto': [
                '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf',
                '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf',
                '/usr/share/fonts/truetype/roboto/Roboto-Medium.ttf'
            ],
            'dejavu': [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'
            ],
            'liberation': [
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf'
            ],
            'noto': [
                '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
                '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'
            ]
        }
    
    def get_font(self, style='regular', size=16):
        """
        Get the best available font for the given style and size.
        
        Args:
            style: 'regular', 'bold', 'italic', 'quote', 'title', 'small'
            size: Font size in points
        """
        cache_key = f"{style}_{size}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Map styles to specific font searches
        style_mapping = {
            'regular': self._get_regular_font,
            'bold': self._get_bold_font,
            'italic': self._get_italic_font,
            'quote': self._get_quote_font,
            'title': self._get_title_font,
            'small': self._get_small_font
        }
        
        font_func = style_mapping.get(style, self._get_regular_font)
        font = font_func(size)
        
        self.font_cache[cache_key] = font
        return font
    
    def _get_regular_font(self, size):
        """Get the best regular font."""
        paths_to_try = []
        
        # Try Roboto first (best for e-ink)
        paths_to_try.extend(self.font_paths['roboto'])
        paths_to_try.extend(self.font_paths['dejavu'])
        paths_to_try.extend(self.font_paths['liberation'])
        paths_to_try.extend(self.font_paths['noto'])
        
        return self._load_first_available_font(paths_to_try, size)
    
    def _get_bold_font(self, size):
        """Get the best bold font."""
        paths_to_try = [
            '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf',
            '/usr/share/fonts/truetype/roboto/Roboto-Medium.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'
        ]
        
        return self._load_first_available_font(paths_to_try, size)
    
    def _get_italic_font(self, size):
        """Get the best italic font."""
        paths_to_try = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf',
            '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf'  # Fallback to regular
        ]
        
        return self._load_first_available_font(paths_to_try, size)
    
    def _get_quote_font(self, size):
        """Get the best font for quotes (optimized for readability)."""
        # For quotes, prioritize readability and elegance
        paths_to_try = [
            '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ]
        
        return self._load_first_available_font(paths_to_try, size)
    
    def _get_title_font(self, size):
        """Get the best font for titles."""
        paths_to_try = [
            '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf',
            '/usr/share/fonts/truetype/roboto/Roboto-Medium.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
        ]
        
        return self._load_first_available_font(paths_to_try, size)
    
    def _get_small_font(self, size):
        """Get the best font for small text."""
        # For small text, prioritize clarity
        paths_to_try = [
            '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ]
        
        return self._load_first_available_font(paths_to_try, size)
    
    def _load_first_available_font(self, paths, size):
        """Try to load the first available font from the paths list."""
        for path in paths:
            try:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, size)
                    print(f"Loaded font: {path} at size {size}")
                    return font
            except Exception as e:
                print(f"Failed to load font {path}: {e}")
                continue
        
        # Ultimate fallback
        print(f"Using default font at size {size}")
        return ImageFont.load_default()
    
    def clear_cache(self):
        """Clear the font cache to free memory."""
        self.font_cache.clear()

# Global font manager instance
font_manager = FontManager()
