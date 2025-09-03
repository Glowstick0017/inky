"""
Simple Font Utility for E-ink Display
Uses PIL's built-in fonts and common system fonts with proper fallbacks
"""

from PIL import ImageFont
import os

def get_font(style='regular', size=16):
    """
    Get an appropriate font for the given style and size.
    
    Args:
        style: 'regular', 'bold', 'italic', 'title', 'quote', 'small'
        size: Font size in points
    
    Returns:
        PIL ImageFont object
    """
    
    # Common font paths to try (works on most systems)
    font_candidates = {
        'regular': [
            # Windows fonts
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/calibri.ttf',
            'C:/Windows/Fonts/segoeui.ttf',
            # Linux fonts (Raspberry Pi)
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf',
            # macOS fonts
            '/System/Library/Fonts/Helvetica.ttc',
            '/System/Library/Fonts/Arial.ttf',
        ],
        'bold': [
            # Windows fonts
            'C:/Windows/Fonts/arialbd.ttf',
            'C:/Windows/Fonts/calibrib.ttf',
            'C:/Windows/Fonts/segoeuib.ttf',
            # Linux fonts
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf',
            # macOS fonts
            '/System/Library/Fonts/Helvetica.ttc',
            '/System/Library/Fonts/Arial Bold.ttf',
        ],
        'italic': [
            # Windows fonts
            'C:/Windows/Fonts/ariali.ttf',
            'C:/Windows/Fonts/calibrii.ttf',
            'C:/Windows/Fonts/segoeuii.ttf',
            # Linux fonts
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf',
            # macOS fonts
            '/System/Library/Fonts/Helvetica.ttc',
            '/System/Library/Fonts/Arial Italic.ttf',
        ]
    }
    
    # Map styles to font types
    if style in ['title', 'bold']:
        font_type = 'bold'
    elif style in ['italic', 'quote']:
        font_type = 'italic'
    else:  # regular, small, etc.
        font_type = 'regular'
    
    # Try to load fonts in order of preference
    for font_path in font_candidates.get(font_type, font_candidates['regular']):
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    
    # If no system fonts work, use PIL's default font
    # For different styles with default font, we can adjust size
    if style == 'title':
        size = int(size * 1.2)  # Make titles slightly larger
    elif style == 'small':
        size = max(8, int(size * 0.8))  # Make small text smaller but readable
    
    try:
        return ImageFont.load_default()
    except Exception:
        # Ultimate fallback - create a basic font
        return ImageFont.load_default()

def get_display_fonts():
    """
    Get a set of fonts optimized for e-ink display readability.
    Returns a dictionary of common font styles.
    """
    return {
        'header': get_font('title', 32),
        'title': get_font('title', 24),
        'large': get_font('bold', 20),
        'medium': get_font('regular', 16),
        'small': get_font('regular', 13),
        'tiny': get_font('small', 11),
        'quote': get_font('italic', 14),
        'temp_large': get_font('bold', 56),
        'temp_medium': get_font('bold', 28),
    }

def get_weather_fonts():
    """Get fonts specifically sized for weather display."""
    return {
        'header': get_font('title', 32),
        'temp': get_font('bold', 56),
        'large': get_font('bold', 22),
        'medium': get_font('regular', 18),
        'small': get_font('small', 15),
    }

def get_starmap_fonts():
    """Get fonts specifically sized for starmap display."""
    return {
        'title': get_font('title', 22),
        'large': get_font('regular', 16),
        'medium': get_font('regular', 14),
        'small': get_font('small', 11),
        'tiny': get_font('small', 10),
    }

def get_system_fonts():
    """Get fonts specifically sized for system display."""
    return {
        'title': get_font('title', 24),
        'large': get_font('bold', 20),
        'medium': get_font('bold', 16),
        'small': get_font('regular', 13),
        'tiny': get_font('small', 11),
    }

def get_artwork_fonts():
    """Get fonts specifically sized for artwork display."""
    return {
        'quote': get_font('quote', 14),
        'author': get_font('italic', 12),
        'title': get_font('title', 24),
        'message': get_font('regular', 16),
    }
