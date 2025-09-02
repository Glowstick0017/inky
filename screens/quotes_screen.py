"""
Daily Quotes Screen
Displays inspiring daily quotes with beautiful styling and occasional decorative art
Updates every hour with a new quote
"""

import requests
import json
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .base_screen import BaseScreen
import config

class QuotesScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.QUOTES_UPDATE_INTERVAL
        self.current_quote = None
        
        # Backup quotes in case API is unavailable
        self.fallback_quotes = [
            {
                "text": "The only way to do great work is to love what you do.",
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
                "text": "If you are working on something that you really care about, you don't have to be pushed.",
                "author": "Steve Jobs"
            }
        ]
    
    def get_quote_from_api(self):
        """Fetch a quote from a quotes API."""
        apis_to_try = [
            {
                'url': 'https://zenquotes.io/api/random',
                'parser': lambda r: {
                    'text': r[0]['q'] if r and len(r) > 0 else None,
                    'author': r[0]['a'] if r and len(r) > 0 else None
                }
            },
            {
                'url': 'https://quotable.io/random',
                'parser': lambda r: {
                    'text': r.get('content'),
                    'author': r.get('author')
                }
            }
        ]
        
        for api in apis_to_try:
            try:
                response = requests.get(api['url'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    quote = api['parser'](data)
                    
                    if quote['text'] and quote['author']:
                        return quote
                        
            except Exception as e:
                print(f"Error fetching from {api['url']}: {e}")
                continue
        
        # Return fallback quote if all APIs fail
        return random.choice(self.fallback_quotes)
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed max width
            test_line = ' '.join(current_line + [word])
            
            # Create a temporary image to measure text
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, split it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_decorative_border(self, draw, width, height):
        """Create a decorative border around the quote."""
        # Corner decorations
        corner_size = 20
        
        # Top-left corner
        draw.arc([5, 5, 5 + corner_size, 5 + corner_size], 180, 270, fill=(100, 100, 100), width=2)
        
        # Top-right corner  
        draw.arc([width - corner_size - 5, 5, width - 5, 5 + corner_size], 270, 360, fill=(100, 100, 100), width=2)
        
        # Bottom-left corner
        draw.arc([5, height - corner_size - 5, 5 + corner_size, height - 5], 90, 180, fill=(100, 100, 100), width=2)
        
        # Bottom-right corner
        draw.arc([width - corner_size - 5, height - corner_size - 5, width - 5, height - 5], 0, 90, fill=(100, 100, 100), width=2)
        
        # Decorative lines
        # Top
        draw.line([25, 10, width - 25, 10], fill=(150, 150, 150), width=1)
        
        # Bottom
        draw.line([25, height - 10, width - 25, height - 10], fill=(150, 150, 150), width=1)
        
        # Left
        draw.line([10, 25, 10, height - 25], fill=(150, 150, 150), width=1)
        
        # Right
        draw.line([width - 10, 25, width - 10, height - 25], fill=(150, 150, 150), width=1)
    
    def create_gradient_background(self, width, height):
        """Create a subtle gradient background."""
        image = Image.new('RGB', (width, height), (255, 255, 255))
        
        # Create a very subtle gradient from light blue to white
        for y in range(height):
            # Calculate gradient value (very subtle)
            gradient_value = int(245 + (10 * y / height))
            gradient_value = min(255, gradient_value)
            
            color = (gradient_value, gradient_value + 2, 255)
            
            # Draw gradient line
            for x in range(width):
                if x % 3 == 0:  # Sparse pattern for subtlety
                    image.putpixel((x, y), color)
        
        return image
    
    def display(self):
        """Display the current daily quote."""
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
            
            # Create background with subtle styling
            display_image = self.create_gradient_background(self.inky.width, self.inky.height)
            draw = ImageDraw.Draw(display_image)
            
            # Create decorative border
            self.create_decorative_border(draw, self.inky.width, self.inky.height)
            
            # Load fonts
            try:
                font_quote = ImageFont.load_default()
                font_author = ImageFont.load_default()
                font_header = ImageFont.load_default()
            except:
                font_quote = None
                font_author = None
                font_header = None
            
            # Draw header
            header_text = "Daily Inspiration"
            if font_header:
                bbox = draw.textbbox((0, 0), header_text, font=font_header)
                text_width = bbox[2] - bbox[0]
                x = (self.inky.width - text_width) // 2
                draw.text((x, 25), header_text, fill=(50, 50, 100), font=font_header)
            
            # Prepare quote text
            quote_text = f'"{quote_data["text"]}"'
            
            # Wrap quote text
            max_quote_width = self.inky.width - 80  # Leave margins
            if font_quote:
                quote_lines = self.wrap_text(quote_text, font_quote, max_quote_width)
            else:
                # Simple word wrapping fallback
                words_per_line = 8
                words = quote_text.split()
                quote_lines = [' '.join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)]
            
            # Calculate quote positioning
            line_height = 20
            total_quote_height = len(quote_lines) * line_height
            quote_start_y = (self.inky.height - total_quote_height - 60) // 2 + 40
            
            # Draw quote text
            for i, line in enumerate(quote_lines):
                if font_quote:
                    bbox = draw.textbbox((0, 0), line, font=font_quote)
                    text_width = bbox[2] - bbox[0]
                    x = (self.inky.width - text_width) // 2
                    y = quote_start_y + (i * line_height)
                    draw.text((x, y), line, fill=(30, 30, 30), font=font_quote)
            
            # Draw author
            author_text = f"— {quote_data['author']}"
            if font_author:
                bbox = draw.textbbox((0, 0), author_text, font=font_author)
                text_width = bbox[2] - bbox[0]
                x = (self.inky.width - text_width) // 2
                y = quote_start_y + total_quote_height + 20
                draw.text((x, y), author_text, fill=(70, 70, 70), font=font_author)
            
            # Add decorative elements
            # Small decorative dots
            dot_size = 3
            for i in range(3):
                x = (self.inky.width // 2) - 20 + (i * 20)
                y = quote_start_y + total_quote_height + 50
                draw.ellipse([x-dot_size, y-dot_size, x+dot_size, y+dot_size], fill=(100, 100, 150))
            
            # Display date and time
            now = datetime.now()
            date_text = now.strftime("%A, %B %d")
            time_text = now.strftime("%H:%M")
            
            if font_author:
                # Date in bottom left
                draw.text((10, self.inky.height - 25), date_text, fill=(100, 100, 100), font=font_author)
                
                # Time in bottom right
                bbox = draw.textbbox((0, 0), time_text, font=font_author)
                text_width = bbox[2] - bbox[0]
                x = self.inky.width - text_width - 10
                draw.text((x, self.inky.height - 25), time_text, fill=(100, 100, 100), font=font_author)
            
            # Convert to Inky's palette and display
            self.inky.set_image(display_image)
            self.inky.show()
            
        except Exception as e:
            print(f"Error displaying quote: {e}")
            self.display_error_message("Quote Error", str(e))
    
    def display_error_message(self, title, message):
        """Display an error message on the screen."""
        image = Image.new("RGB", (self.inky.width, self.inky.height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        if font:
            # Draw error title
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.inky.width - text_width) // 2
            draw.text((x, 150), title, fill=(200, 0, 0), font=font)
            
            # Draw error message (truncated)
            if len(message) > 50:
                message = message[:47] + "..."
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.inky.width - text_width) // 2
            draw.text((x, 180), message, fill=(100, 100, 100), font=font)
        
        self.inky.set_image(image)
        self.inky.show()
