"""
Daily Quotes Screen
Displays inspiring daily quotes with beautiful styling and artistic backgrounds
Updates every hour with a new quote
"""

import requests
import json
import random
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
        
        # Beautiful background themes for quotes
        self.background_themes = [
            {
                'name': 'sunset',
                'colors': [(255, 94, 77), (255, 154, 0), (255, 206, 84)],
                'style': 'gradient'
            },
            {
                'name': 'ocean',
                'colors': [(64, 224, 208), (70, 130, 180), (25, 25, 112)],
                'style': 'gradient'
            },
            {
                'name': 'forest',
                'colors': [(34, 139, 34), (107, 142, 35), (85, 107, 47)],
                'style': 'gradient'
            },
            {
                'name': 'lavender',
                'colors': [(147, 112, 219), (186, 85, 211), (138, 43, 226)],
                'style': 'gradient'
            },
            {
                'name': 'autumn',
                'colors': [(255, 140, 0), (255, 69, 0), (139, 69, 19)],
                'style': 'gradient'
            },
            {
                'name': 'midnight',
                'colors': [(25, 25, 112), (72, 61, 139), (123, 104, 238)],
                'style': 'gradient'
            }
        ]
        
        # Extended collection of inspirational quotes
        self.fallback_quotes = [
            {
                "text": "The only way to do great work is to love what you do.",
                "author": "Steve Jobs"
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
                "text": "The future belongs to those who believe in the beauty of their dreams.",
                "author": "Eleanor Roosevelt"
            },
            {
                "text": "It is during our darkest moments that we must focus to see the light.",
                "author": "Aristotle"
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
                "text": "You learn more from failure than from success. Don't let it stop you.",
                "author": "Unknown"
            },
            {
                "text": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
                "author": "Winston Churchill"
            },
            {
                "text": "The only impossible journey is the one you never begin.",
                "author": "Tony Robbins"
            },
            {
                "text": "In the middle of difficulty lies opportunity.",
                "author": "Albert Einstein"
            },
            {
                "text": "Believe you can and you're halfway there.",
                "author": "Theodore Roosevelt"
            },
            {
                "text": "The greatest glory in living lies not in never falling, but in rising every time we fall.",
                "author": "Nelson Mandela"
            },
            {
                "text": "Your time is limited, don't waste it living someone else's life.",
                "author": "Steve Jobs"
            },
            {
                "text": "If you want to live a happy life, tie it to a goal, not to people or things.",
                "author": "Albert Einstein"
            }
        ]
    
    
    def get_quote_from_api(self):
        """Fetch a quote from various quote APIs."""
        apis_to_try = [
            {
                'url': 'https://zenquotes.io/api/random',
                'parser': lambda r: {
                    'text': r[0]['q'] if r and len(r) > 0 else None,
                    'author': r[0]['a'] if r and len(r) > 0 else None
                }
            },
            {
                'url': 'https://quotable.io/random?minLength=50&maxLength=200',
                'parser': lambda r: {
                    'text': r.get('content'),
                    'author': r.get('author')
                }
            },
            {
                'url': 'https://api.quotegarden.io/api/v3/quotes/random',
                'parser': lambda r: {
                    'text': r.get('data', {}).get('quoteText'),
                    'author': r.get('data', {}).get('quoteAuthor')
                }
            }
        ]
        
        for api in apis_to_try:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(api['url'], headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    quote = api['parser'](data)
                    
                    if quote['text'] and quote['author'] and len(quote['text']) > 20:
                        return quote
                        
            except Exception as e:
                print(f"Error fetching from {api['url']}: {e}")
                continue
        
        # Return fallback quote if all APIs fail
        return random.choice(self.fallback_quotes)
    
    def create_gradient_background(self, width, height, theme):
        """Create a beautiful gradient background."""
        image = Image.new('RGB', (width, height), theme['colors'][0])
        
        if theme['style'] == 'gradient':
            colors = theme['colors']
            
            # Create smooth gradient
            for y in range(height):
                # Determine which color pair to interpolate between
                progress = y / height
                
                if progress < 0.5:
                    # First half: interpolate between first and second color
                    t = progress * 2
                    color1, color2 = colors[0], colors[1]
                else:
                    # Second half: interpolate between second and third color
                    t = (progress - 0.5) * 2
                    color1, color2 = colors[1], colors[2] if len(colors) > 2 else colors[1]
                
                # Linear interpolation
                r = int(color1[0] * (1 - t) + color2[0] * t)
                g = int(color1[1] * (1 - t) + color2[1] * t)
                b = int(color1[2] * (1 - t) + color2[2] * t)
                
                # Draw the line
                draw = ImageDraw.Draw(image)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image
    
    def add_decorative_elements(self, draw, width, height, theme):
        """Add decorative geometric elements to the background."""
        # Add subtle decorative circles
        for i in range(8):
            x = random.randint(-50, width + 50)
            y = random.randint(-50, height + 50)
            radius = random.randint(20, 100)
            
            # Semi-transparent overlay
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Use theme colors with low opacity
            color = random.choice(theme['colors'])
            alpha = random.randint(10, 30)
            
            overlay_draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                               fill=(*color, alpha))
            
            return overlay
        
        return None
    
    def wrap_text_enhanced(self, text, font, max_width, max_lines=6):
        """Enhanced text wrapping with better word distribution."""
        words = text.split()
        lines = []
        current_line = []
        
        # Create a temporary image to measure text
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
                    # Word is too long, split it
                    lines.append(word)
                    if len(lines) >= max_lines:
                        break
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        return lines[:max_lines]
    
    def display(self):
        """Display an inspiring quote with beautiful artistic background."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Daily Quotes screen...")
        
        try:
            # Get a new quote
            quote_data = self.get_quote_from_api()
            
            if quote_data:
                print(f"Displaying quote: {quote_data['text'][:50]}...")
                self.current_quote = quote_data
            else:
                # Use fallback
                quote_data = random.choice(self.fallback_quotes)
                print("Using fallback quote")
            
            # Choose a random theme
            theme = random.choice(self.background_themes)
            print(f"Using {theme['name']} theme")
            
            # Create beautiful gradient background
            display_image = self.create_gradient_background(640, 400, theme)
            
            # Add decorative elements
            decorative_overlay = self.add_decorative_elements(None, 640, 400, theme)
            if decorative_overlay:
                display_image = Image.alpha_composite(display_image.convert('RGBA'), decorative_overlay).convert('RGB')
            
            # Create semi-transparent overlay for text readability
            text_overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(text_overlay)
            
            # Central area for text with subtle background
            overlay_draw.rounded_rectangle(
                [(50, 80), (590, 320)], 
                radius=20, 
                fill=(255, 255, 255, 80)
            )
            
            # Composite the text overlay
            display_image = Image.alpha_composite(display_image.convert('RGBA'), text_overlay).convert('RGB')
            draw = ImageDraw.Draw(display_image)
            
            # Load fonts - simulate larger fonts by repeating characters if needed
            try:
                font_quote = ImageFont.load_default()
                font_author = ImageFont.load_default()
                font_header = ImageFont.load_default()
            except:
                font_quote = font_author = font_header = None
            
            # Draw inspirational header
            header_text = "DAILY INSPIRATION"
            if font_header:
                bbox = draw.textbbox((0, 0), header_text, font=font_header)
                text_width = bbox[2] - bbox[0]
                x = (640 - text_width) // 2
                y = 30
                # Shadow effect
                draw.text((x+2, y+2), header_text, fill=(0, 0, 0), font=font_header)
                draw.text((x, y), header_text, fill=(255, 255, 255), font=font_header)
            
            # Prepare and wrap quote text
            quote_text = f'"{quote_data["text"]}"'
            
            # Wrap quote text with larger constraints
            max_quote_width = 480  # Wider text area
            if font_quote:
                quote_lines = self.wrap_text_enhanced(quote_text, font_quote, max_quote_width)
            else:
                # Simple word wrapping fallback
                words_per_line = 10
                words = quote_text.split()
                quote_lines = [' '.join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)]
            
            # Calculate quote positioning (center vertically)
            line_height = 25  # Increased line height for better readability
            total_quote_height = len(quote_lines) * line_height
            quote_start_y = (400 - total_quote_height) // 2
            
            # Draw quote text with larger, more readable font
            for i, line in enumerate(quote_lines):
                if font_quote:
                    bbox = draw.textbbox((0, 0), line, font=font_quote)
                    text_width = bbox[2] - bbox[0]
                    x = (640 - text_width) // 2
                    y = quote_start_y + (i * line_height)
                    
                    # Shadow for readability
                    draw.text((x+1, y+1), line, fill=(0, 0, 0), font=font_quote)
                    draw.text((x, y), line, fill=(50, 50, 50), font=font_quote)
            
            # Draw author with emphasis
            author_text = f"— {quote_data['author']}"
            if font_author:
                bbox = draw.textbbox((0, 0), author_text, font=font_author)
                text_width = bbox[2] - bbox[0]
                x = (640 - text_width) // 2
                y = quote_start_y + total_quote_height + 30
                
                # Shadow effect
                draw.text((x+1, y+1), author_text, fill=(0, 0, 0), font=font_author)
                draw.text((x, y), author_text, fill=(70, 70, 70), font=font_author)
            
            # Add decorative quote marks
            quote_mark_size = 30
            draw.text((70, quote_start_y - 20), '"', fill=(255, 255, 255), font=font_header)
            draw.text((560, quote_start_y + total_quote_height + 10), '"', fill=(255, 255, 255), font=font_header)
            
            # Display date and time with better styling
            now = datetime.now()
            date_text = now.strftime("%A, %B %d")
            time_text = now.strftime("%H:%M")
            
            if font_author:
                # Date in bottom left
                draw.text((21, 361), date_text, fill=(0, 0, 0), font=font_author)
                draw.text((20, 360), date_text, fill=(200, 200, 200), font=font_author)
                
                # Time in bottom right
                bbox = draw.textbbox((0, 0), time_text, font=font_author)
                text_width = bbox[2] - bbox[0]
                x = 640 - text_width - 20
                draw.text((x+1, 361), time_text, fill=(0, 0, 0), font=font_author)
                draw.text((x, 360), time_text, fill=(200, 200, 200), font=font_author)
            
            # Display the beautiful quote
            self.inky.set_image(display_image)
            self.inky.show()
            
        except Exception as e:
            print(f"Error displaying quote: {e}")
            self.display_error_message("Quote Error", str(e))
        except Exception as e:
            print(f"Error displaying quote: {e}")
            self.display_error_message("Quote Error", str(e))
    
    def display_error_message(self, title, message):
        """Display an error message on the screen."""
        # Create a beautiful error display with a sunset theme
        theme = self.background_themes[0]  # Use sunset theme
        image = self.create_gradient_background(640, 400, theme)
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        if font:
            # Draw error title
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            y = 180
            # Shadow effect
            draw.text((x+2, y+2), title, fill=(0, 0, 0), font=font)
            draw.text((x, y), title, fill=(255, 255, 255), font=font)
            
            # Draw error message (truncated)
            if len(message) > 60:
                message = message[:57] + "..."
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            y = 220
            draw.text((x+1, y+1), message, fill=(0, 0, 0), font=font)
            draw.text((x, y), message, fill=(200, 200, 200), font=font)
        
        self.inky.set_image(image)
        self.inky.show()
