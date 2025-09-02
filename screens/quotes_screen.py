"""
Daily Quotes Screen - Large Text with Stunning Visuals
Displays inspiring daily quotes with beautiful styling and artistic backgrounds
Updates every hour with a new quote
"""

import requests
import json
import random
import math
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from .base_screen import BaseScreen
import config

class QuotesScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.QUOTES_UPDATE_INTERVAL
        self.current_quote = None
        
        # Stunning visual themes for quotes with rich colors
        self.background_themes = [
            {
                'name': 'golden_hour',
                'colors': [(255, 215, 0), (255, 140, 0), (255, 69, 0)],
                'accent': (255, 255, 255),
                'pattern': 'sunburst'
            },
            {
                'name': 'deep_ocean',
                'colors': [(0, 119, 190), (0, 180, 216), (144, 224, 239)],
                'accent': (255, 255, 255),
                'pattern': 'waves'
            },
            {
                'name': 'mystical_forest',
                'colors': [(34, 139, 34), (0, 100, 0), (85, 107, 47)],
                'accent': (255, 255, 255),
                'pattern': 'leaves'
            },
            {
                'name': 'royal_purple',
                'colors': [(75, 0, 130), (138, 43, 226), (186, 85, 211)],
                'accent': (255, 255, 255),
                'pattern': 'stars'
            },
            {
                'name': 'warm_sunset',
                'colors': [(255, 94, 77), (255, 154, 0), (255, 206, 84)],
                'accent': (255, 255, 255),
                'pattern': 'clouds'
            },
            {
                'name': 'arctic_blue',
                'colors': [(176, 196, 222), (135, 206, 235), (70, 130, 180)],
                'accent': (25, 25, 112),
                'pattern': 'frost'
            }
        ]
        
        # Quote sources with fallback quotes
        self.quote_sources = [
            {
                'name': 'Quotable',
                'url': 'https://api.quotable.io/random',
                'max_length': 200
            },
            {
                'name': 'ZenQuotes',
                'url': 'https://zenquotes.io/api/random',
                'max_length': 200
            }
        ]
        
        # Inspiring fallback quotes
        self.fallback_quotes = [
            {
                "text": "The future belongs to those who believe in the beauty of their dreams.",
                "author": "Eleanor Roosevelt"
            },
            {
                "text": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
                "author": "Winston Churchill"
            },
            {
                "text": "Innovation distinguishes between a leader and a follower.",
                "author": "Steve Jobs"
            },
            {
                "text": "Life is what happens to you while you're busy making other plans.",
                "author": "John Lennon"
            },
            {
                "text": "The way to get started is to quit talking and begin doing.",
                "author": "Walt Disney"
            },
            {
                "text": "Don't let yesterday take up too much of today.",
                "author": "Will Rogers"
            },
            {
                "text": "You learn more from failure than from success.",
                "author": "Unknown"
            },
            {
                "text": "If you are working on something exciting that you really care about, you don't have to be pushed.",
                "author": "Steve Jobs"
            }
        ]
    
    def fetch_quote(self):
        """Fetch an inspiring quote from various APIs."""
        for source in self.quote_sources:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(source['url'], headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if source['name'] == 'Quotable':
                        quote_text = data.get('content', '')
                        quote_author = data.get('author', 'Unknown')
                    elif source['name'] == 'ZenQuotes':
                        if isinstance(data, list) and len(data) > 0:
                            quote_text = data[0].get('q', '')
                            quote_author = data[0].get('a', 'Unknown')
                        else:
                            continue
                    
                    # Filter quotes that are too long
                    if quote_text and len(quote_text) <= source['max_length']:
                        return {
                            "text": quote_text.strip(),
                            "author": quote_author.strip()
                        }
                        
            except Exception as e:
                print(f"Error fetching from {source['name']}: {e}")
                continue
        
        # Return random fallback quote
        return random.choice(self.fallback_quotes)
    
    def create_stunning_background(self, theme):
        """Create a visually stunning background with patterns."""
        image = Image.new("RGB", (640, 400), theme['colors'][0])
        draw = ImageDraw.Draw(image)
        
        # Create smooth gradient background
        for y in range(400):
            ratio = y / 400
            if ratio < 0.5:
                # Top half
                blend_ratio = ratio * 2
                r = int(theme['colors'][0][0] * (1 - blend_ratio) + theme['colors'][1][0] * blend_ratio)
                g = int(theme['colors'][0][1] * (1 - blend_ratio) + theme['colors'][1][1] * blend_ratio)
                b = int(theme['colors'][0][2] * (1 - blend_ratio) + theme['colors'][1][2] * blend_ratio)
            else:
                # Bottom half
                blend_ratio = (ratio - 0.5) * 2
                r = int(theme['colors'][1][0] * (1 - blend_ratio) + theme['colors'][2][0] * blend_ratio)
                g = int(theme['colors'][1][1] * (1 - blend_ratio) + theme['colors'][2][1] * blend_ratio)
                b = int(theme['colors'][1][2] * (1 - blend_ratio) + theme['colors'][2][2] * blend_ratio)
            
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Add themed patterns
        self.add_visual_pattern(draw, theme['pattern'], theme['colors'])
        
        return image
    
    def add_visual_pattern(self, draw, pattern, colors):
        """Add beautiful visual patterns to the background."""
        if pattern == 'sunburst':
            # Radiating sun rays from corner
            center_x, center_y = 550, 50
            for angle in range(0, 360, 12):
                rad = math.radians(angle)
                x1 = center_x + 30 * math.cos(rad)
                y1 = center_y + 30 * math.sin(rad)
                x2 = center_x + 120 * math.cos(rad)
                y2 = center_y + 120 * math.sin(rad)
                draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 200, 80), width=2)
        
        elif pattern == 'waves':
            # Flowing wave patterns
            for offset in range(0, 640, 40):
                wave_points = []
                for x in range(offset, min(offset + 200, 640), 5):
                    y = 100 + 30 * math.sin((x - offset) * 0.02)
                    wave_points.append((x, y))
                if len(wave_points) > 1:
                    for i in range(len(wave_points) - 1):
                        draw.line([wave_points[i], wave_points[i + 1]], fill=(255, 255, 255, 60), width=3)
        
        elif pattern == 'stars':
            # Twinkling stars
            import random
            random.seed(42)  # Consistent pattern
            for _ in range(25):
                x = random.randint(50, 590)
                y = random.randint(50, 350)
                size = random.randint(2, 6)
                # Draw 4-pointed star
                draw.line([(x - size, y), (x + size, y)], fill=(255, 255, 255), width=2)
                draw.line([(x, y - size), (x, y + size)], fill=(255, 255, 255), width=2)
        
        elif pattern == 'leaves':
            # Floating leaves
            leaf_positions = [(100, 80), (300, 120), (500, 90), (150, 300), (400, 280)]
            for x, y in leaf_positions:
                # Simple leaf shape
                draw.ellipse([x, y, x + 15, y + 25], fill=(144, 238, 144))
                draw.line([(x + 7, y), (x + 7, y + 25)], fill=(34, 139, 34), width=2)
        
        elif pattern == 'clouds':
            # Soft cloud shapes
            cloud_positions = [(80, 60), (280, 90), (480, 70)]
            for x, y in cloud_positions:
                # Multiple circles for cloud effect
                for offset_x, offset_y, radius in [(0, 0, 20), (15, -5, 18), (30, 0, 16), (-10, -3, 14)]:
                    draw.ellipse([x + offset_x - radius, y + offset_y - radius,
                                x + offset_x + radius, y + offset_y + radius],
                               fill=(255, 255, 255, 100))
    
    def wrap_text_large(self, text, font, max_width, max_lines=6):
        """Wrap text for large display with generous spacing."""
        words = text.split()
        lines = []
        current_line = []
        
        # Create temporary image for text measurement
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    if len(lines) >= max_lines:
                        break
                    current_line = [word]
                else:
                    # Word too long, split it
                    lines.append(word)
                    if len(lines) >= max_lines:
                        break
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        return lines[:max_lines]
    
    def display(self):
        """Display an inspiring quote with stunning visuals and large text."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Quotes screen...")
        
        try:
            # Get fresh quote
            quote_data = self.fetch_quote()
            self.current_quote = quote_data
            
            # Select random theme
            theme = random.choice(self.background_themes)
            print(f"Using theme: {theme['name']}")
            
            # Create stunning background
            display_image = self.create_stunning_background(theme)
            draw = ImageDraw.Draw(display_image)
            
            # Load much larger fonts for better readability
            try:
                # Try to load large TrueType fonts
                font_quote = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 32)
                font_author = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", 24)
                font_header = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 28)
            except:
                try:
                    # Try DejaVu fonts as backup
                    font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
                    font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 24)
                    font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
                except:
                    # Fallback to default fonts (less ideal but functional)
                    font_quote = ImageFont.load_default()
                    font_author = ImageFont.load_default()
                    font_header = ImageFont.load_default()
            
            # Create semi-transparent overlay for better text readability
            overlay = Image.new("RGBA", (640, 400), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Draw elegant text background panel
            panel_margin = 60
            overlay_draw.rounded_rectangle(
                [(panel_margin, 80), (640 - panel_margin, 320)],
                radius=20,
                fill=(0, 0, 0, 120)
            )
            
            # Blend overlay with background
            display_image = Image.alpha_composite(display_image.convert("RGBA"), overlay).convert("RGB")
            draw = ImageDraw.Draw(display_image)
            
            # Draw header
            header_text = "✨ DAILY INSPIRATION ✨"
            if font_header:
                bbox = draw.textbbox((0, 0), header_text, font=font_header)
                text_width = bbox[2] - bbox[0]
                x = (640 - text_width) // 2
                # Draw with shadow effect
                draw.text((x + 2, 42), header_text, fill=(0, 0, 0, 100), font=font_header)
                draw.text((x, 40), header_text, fill=theme['accent'], font=font_header)
            
            # Draw quote with much larger text
            quote_text = quote_data['text']
            max_text_width = 640 - (panel_margin * 2) - 40  # Account for panel margins
            
            if font_quote:
                quote_lines = self.wrap_text_large(quote_text, font_quote, max_text_width, 5)
                line_height = 45  # Much larger line spacing
                total_text_height = len(quote_lines) * line_height
                start_y = 150  # Start lower to accommodate header
                
                for i, line in enumerate(quote_lines):
                    y = start_y + (i * line_height)
                    bbox = draw.textbbox((0, 0), line, font=font_quote)
                    text_width = bbox[2] - bbox[0]
                    x = (640 - text_width) // 2
                    
                    # Text shadow for depth
                    draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 150), font=font_quote)
                    # Main text
                    draw.text((x, y), line, fill=theme['accent'], font=font_quote)
            
            # Draw author with elegant styling
            author_text = f"— {quote_data['author']}"
            if font_author:
                bbox = draw.textbbox((0, 0), author_text, font=font_author)
                text_width = bbox[2] - bbox[0]
                x = (640 - text_width) // 2
                y = 280  # Position below quote
                
                # Author shadow
                draw.text((x + 1, y + 1), author_text, fill=(0, 0, 0, 120), font=font_author)
                # Author text
                draw.text((x, y), author_text, fill=theme['accent'], font=font_author)
            
            # Add decorative corner elements
            self.add_corner_decorations(draw, theme['accent'])
            
            # Display timestamp
            current_time = datetime.now().strftime("%I:%M %p")
            if font_author:
                draw.text((520, 370), current_time, fill=(255, 255, 255, 200), font=font_author)
            
            # Display the quote
            self.inky.set_image(display_image)
            self.inky.show()
            
            print(f"Displayed quote by {quote_data['author']}")
            
        except Exception as e:
            print(f"Error displaying quote: {e}")
            self.display_error_message("Quote Error", str(e))
    
    def add_corner_decorations(self, draw, color):
        """Add elegant corner decorations."""
        # Top left corner
        draw.arc([20, 20, 60, 60], 180, 270, fill=color, width=3)
        draw.arc([25, 25, 55, 55], 180, 270, fill=color, width=2)
        
        # Top right corner  
        draw.arc([580, 20, 620, 60], 270, 360, fill=color, width=3)
        draw.arc([585, 25, 615, 55], 270, 360, fill=color, width=2)
        
        # Bottom left corner
        draw.arc([20, 340, 60, 380], 90, 180, fill=color, width=3)
        draw.arc([25, 345, 55, 375], 90, 180, fill=color, width=2)
        
        # Bottom right corner
        draw.arc([580, 340, 620, 380], 0, 90, fill=color, width=3)
        draw.arc([585, 345, 615, 375], 0, 90, fill=color, width=2)
    
    def display_error_message(self, title, message):
        """Display an error message with quote theme."""
        image = Image.new("RGB", (640, 400), (139, 69, 19))
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        if font:
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 180), title, fill=(255, 255, 255), font=font)
            
            if len(message) > 60:
                message = message[:57] + "..."
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 210), message, fill=(200, 200, 200), font=font)
        
        self.inky.set_image(image)
        self.inky.show()
