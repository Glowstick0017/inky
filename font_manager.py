"""
Font Manager for Raspberry Pi E-ink Display
Handles font loading with fallbacks optimized for Raspberry Pi Zero 2W
"""

from PIL import ImageFont
import os

class FontManager:
    def __init__(self):
        self.font_cache = {}
        self.loaded_fonts = {}  # Pre-loaded fonts
        
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
        
        # Pre-load base fonts at initialization
        self._preload_base_fonts()
    
    def _preload_base_fonts(self):
        """Pre-load the most common fonts to avoid loading during display operations."""
        try:
            # Find the best available fonts once
            self.loaded_fonts['regular_path'] = self._find_best_font_path(['regular'])
            self.loaded_fonts['bold_path'] = self._find_best_font_path(['bold'])
            self.loaded_fonts['italic_path'] = self._find_best_font_path(['italic'])
            
            print("Font paths identified for fast loading")
        except Exception as e:
            print(f"Error pre-loading fonts: {e}")
            self.loaded_fonts['regular_path'] = None
            self.loaded_fonts['bold_path'] = None
            self.loaded_fonts['italic_path'] = None
    
    def _find_best_font_path(self, style_list):
        """Find the best available font path for a given style."""
        if 'bold' in style_list:
            paths_to_try = [
                '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf',
                '/usr/share/fonts/truetype/roboto/Roboto-Medium.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'
            ]
        elif 'italic' in style_list:
            paths_to_try = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf',
                '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf'  # Fallback to regular
            ]
        else:  # regular
            paths_to_try = []
            # Try Roboto first (best for e-ink)
            paths_to_try.extend(self.font_paths['roboto'])
            paths_to_try.extend(self.font_paths['dejavu'])
            paths_to_try.extend(self.font_paths['liberation'])
            paths_to_try.extend(self.font_paths['noto'])
        
        for path in paths_to_try:
            if os.path.exists(path):
                return path
        return None
    
    def get_font(self, style='regular', size=16):
        """
        Get the best available font for the given style and size.
        Uses pre-loaded font paths for maximum speed.
        
        Args:
            style: 'regular', 'bold', 'italic', 'quote', 'title', 'small'
            size: Font size in points
        """
        cache_key = f"{style}_{size}"
        
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Map styles to font paths (fast lookup)
        font_path = None
        if style in ['regular', 'quote', 'small']:
            font_path = self.loaded_fonts.get('regular_path')
        elif style in ['bold', 'title']:
            font_path = self.loaded_fonts.get('bold_path') or self.loaded_fonts.get('regular_path')
        elif style == 'italic':
            font_path = self.loaded_fonts.get('italic_path') or self.loaded_fonts.get('regular_path')
        
        # Load font with pre-identified path
        if font_path and os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, size)
                self.font_cache[cache_key] = font
                return font
            except Exception as e:
                print(f"Failed to load pre-identified font {font_path}: {e}")
        
        # Ultimate fallback
        print(f"Using default font at size {size}")
        font = ImageFont.load_default()
        self.font_cache[cache_key] = font
        return font
    
    def clear_cache(self):
        """Clear the font cache to free memory."""
        self.font_cache.clear()

# Global font manager instance
font_manager = FontManager()
