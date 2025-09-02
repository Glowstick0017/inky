"""
Artwork with Quotes Screen
Displays full-screen high-quality artwork with inspiring quotes overlay
Updates every 5 minutes with new artwork and quotes
"""

import requests
import json
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
from .base_screen import BaseScreen
import config

class ArtworkScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.ARTWORK_UPDATE_INTERVAL
        self.current_artwork = None
        self.current_quote = None
        self.artwork_rotation_index = 0  # Track artwork rotation
        
        # Multiple art sources for better variety
        self.art_sources = [
            {
                'name': 'Wikimedia Commons',
                'type': 'wikimedia',
                'search_url': 'https://commons.wikimedia.org/w/api.php'
            },
            {
                'name': 'Unsplash',
                'type': 'unsplash', 
                'search_url': 'https://api.unsplash.com/photos/random'
            }
        ]
        
        # High-quality search terms for artwork
        self.artwork_keywords = [
            'classical painting', 'renaissance art', 'baroque painting', 'impressionist painting',
            'landscape painting', 'portrait painting', 'still life painting', 'abstract art',
            'modern art', 'contemporary art', 'sculpture', 'fine art photography',
            'architectural photography', 'nature photography', 'minimalist art', 'museum artwork'
        ]
        
        # Quote sources for overlay
        self.quote_sources = [
            {
                'name': 'Quotable',
                'url': 'https://api.quotable.io/random',
                'max_length': 150
            },
            {
                'name': 'ZenQuotes',
                'url': 'https://zenquotes.io/api/random',
                'max_length': 150
            }
        ]
        
        # Inspiring fallback quotes
        self.fallback_quotes = [
            {
                "text": "Art enables us to find ourselves and lose ourselves at the same time.",
                "author": "Thomas Merton"
            },
            {
                "text": "Every artist was first an amateur.",
                "author": "Ralph Waldo Emerson"
            },
            {
                "text": "Art is not what you see, but what you make others see.",
                "author": "Edgar Degas"
            },
            {
                "text": "The purpose of art is washing the dust of daily life off our souls.",
                "author": "Pablo Picasso"
            },
            {
                "text": "Art should comfort the disturbed and disturb the comfortable.",
                "author": "Cesar A. Cruz"
            },
            {
                "text": "Creativity takes courage.",
                "author": "Henri Matisse"
            }
        ]
        
        # Fallback high-quality images
        self.fallback_images = [
            'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/The_Great_Wave_off_Kanagawa.jpg/1280px-The_Great_Wave_off_Kanagawa.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/687px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg'
        ]
    
    def get_unsplash_artwork(self, keyword=None):
        """Get high-quality artwork from Unsplash (no API key needed for basic usage)."""
        try:
            if keyword is None:
                keyword = random.choice(self.artwork_keywords)
            url = "https://api.unsplash.com/photos/random"
            params = {
                'query': keyword,
                'orientation': 'landscape',
                'content_filter': 'high',
                'w': 640,
                'h': 400,
                'fit': 'crop'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('description', 'Untitled'),
                    'artist': data.get('user', {}).get('name', 'Unknown Artist'),
                    'source': 'Unsplash',
                    'image_url': data.get('urls', {}).get('regular', ''),
                    'color': data.get('color', '#FFFFFF')
                }
        except Exception as e:
            print(f"Error fetching from Unsplash: {e}")
        return None
    
    def get_wikimedia_artwork(self, keyword=None):
        """Get artwork from Wikimedia Commons."""
        try:
            if keyword is None:
                keyword = random.choice(self.artwork_keywords)
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': f'{keyword} filetype:bitmap',
                'srnamespace': '6',
                'srlimit': '20'
            }
            
            response = requests.get(self.art_sources[0]['search_url'], params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('query', {}).get('search'):
                    # Get a random result
                    result = random.choice(data['query']['search'])
                    title = result.get('title', 'Untitled').replace('File:', '')
                    
                    # Get image info
                    info_params = {
                        'action': 'query',
                        'format': 'json',
                        'titles': result['title'],
                        'prop': 'imageinfo',
                        'iiprop': 'url|size'
                    }
                    
                    info_response = requests.get(self.art_sources[0]['search_url'], params=info_params, timeout=10)
                    if info_response.status_code == 200:
                        info_data = info_response.json()
                        pages = info_data.get('query', {}).get('pages', {})
                        for page in pages.values():
                            imageinfo = page.get('imageinfo', [])
                            if imageinfo:
                                return {
                                    'title': title,
                                    'artist': 'Wikimedia Commons',
                                    'source': 'Wikimedia',
                                    'image_url': imageinfo[0].get('url', ''),
                                    'color': '#FFFFFF'
                                }
        except Exception as e:
            print(f"Error fetching from Wikimedia: {e}")
        return None
    
    def download_and_resize_artwork(self, image_url):
        """Download and resize artwork to fill the entire 640x400 screen."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=20)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Resize to fill the entire screen (640x400)
                image = image.resize((640, 400), Image.Resampling.LANCZOS)
                
                # Enhance the image for better display on e-ink
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.2)  # Increase contrast slightly
                
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.1)  # Slight sharpening
                
                return image
                
        except Exception as e:
            print(f"Error downloading/resizing artwork: {e}")
            
        return None
    
    def create_gradient_overlay(self, width, height, color):
        """Create a subtle gradient overlay for text readability."""
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # Create a gradient from transparent to semi-transparent
        for y in range(height):
            alpha = int(120 * (y / height))  # Gradient from 0 to 120 alpha
            for x in range(width):
                overlay.putpixel((x, y), (0, 0, 0, alpha))
        
        return overlay
    
    def get_artwork_from_fallback(self):
        """Get artwork from fallback URLs."""
        try:
            url = random.choice(self.fallback_images)
            return {
                'title': 'Classic Masterpiece',
                'artist': 'Master Artist',
                'source': 'Classic Collection',
                'image_url': url,
                'color': '#FFFFFF'
            }
        except:
            return None
    
    def fetch_quote(self):
        """Fetch an inspiring quote from multiple sources."""
        try:
            # Try to fetch from quote APIs
            for source in self.quote_sources:
                try:
                    response = requests.get(source['url'], timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if source['name'] == 'Quotable':
                            quote_text = data.get('content', '')
                            author = data.get('author', 'Unknown')
                            if len(quote_text) <= source['max_length']:
                                return {'text': quote_text, 'author': author}
                        
                        elif source['name'] == 'ZenQuotes':
                            if isinstance(data, list) and len(data) > 0:
                                quote_data = data[0]
                                quote_text = quote_data.get('q', '')
                                author = quote_data.get('a', 'Unknown')
                                if len(quote_text) <= source['max_length']:
                                    return {'text': quote_text, 'author': author}
                
                except Exception as e:
                    print(f"Error fetching from {source['name']}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error in fetch_quote: {e}")
        
        # Return fallback quote if all APIs fail
        return random.choice(self.fallback_quotes)
    
    def display(self):
        """Display full-screen artwork with an inspiring quote overlay."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Artwork + Quote screen...")
        
        try:
            # Get fresh artwork (cycles through keywords for variety)
            artwork_data = None
            sources_to_try = [
                self.get_unsplash_artwork,
                self.get_wikimedia_artwork,
                self.get_artwork_from_fallback
            ]
            
            # Cycle through keywords to ensure variety
            keyword = self.artwork_keywords[self.artwork_rotation_index % len(self.artwork_keywords)]
            self.artwork_rotation_index += 1
            print(f"Searching for artwork with keyword: {keyword}")
            
            for source_func in sources_to_try:
                try:
                    if source_func.__name__ == 'get_artwork_from_fallback':
                        artwork_data = source_func()
                    else:
                        artwork_data = source_func(keyword)
                    if artwork_data and artwork_data.get('image_url'):
                        break
                except Exception as e:
                    print(f"Error with source {source_func.__name__}: {e}")
                    continue
            
            if not artwork_data:
                print("Using fallback artwork")
                artwork_data = {
                    'title': 'Classic Masterpiece',
                    'artist': 'Master Artist', 
                    'source': 'Classic Collection',
                    'image_url': random.choice(self.fallback_images),
                    'color': '#6A5ACD'
                }
            
            # Get fresh quote
            quote_data = self.fetch_quote()
            self.current_quote = quote_data
            
            # Download and process the artwork
            if artwork_data.get('image_url'):
                print(f"Displaying artwork with quote by {quote_data['author']}")
                artwork_image = self.download_and_resize_artwork(artwork_data['image_url'])
            else:
                artwork_image = None
            
            # If we couldn't get an image, create a beautiful fallback
            if not artwork_image:
                artwork_image = self.create_fallback_artwork(artwork_data)
            
            # Create elegant quote overlay
            display_image = self.add_quote_overlay(artwork_image, quote_data)
            
            # Store current artwork
            self.current_artwork = artwork_data
            
            # Display the combined artwork + quote
            self.inky.set_image(display_image)
            self.inky.show()
            
        except Exception as e:
            print(f"Error displaying artwork: {e}")
            self.display_error_message("Artwork Error", str(e))
    
    def add_quote_overlay(self, artwork_image, quote_data):
        """Add elegant quote overlay to artwork."""
        # Create overlay for quote (bottom portion)
        overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Create elegant gradient overlay at bottom for quote
        for y in range(280, 400):  # Bottom 120 pixels for quote
            alpha = int(160 * ((y - 280) / 120))  # Gradient from 0 to 160 alpha
            overlay_draw.rectangle([(0, y), (640, y+1)], fill=(0, 0, 0, alpha))
        
        # Add subtle border at top of quote area
        overlay_draw.rectangle([(0, 280), (640, 282)], fill=(255, 255, 255, 100))
        
        # Composite the overlay onto the artwork
        display_image = Image.alpha_composite(artwork_image.convert('RGBA'), overlay)
        display_image = display_image.convert('RGB')
        
        # Add quote text with elegant typography
        draw = ImageDraw.Draw(display_image)
        
        try:
            # Try to load large, readable fonts
            font_quote = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 18)
            font_author = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", 16)
        except:
            try:
                font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
                font_author = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 16)
            except:
                font_quote = font_author = ImageFont.load_default()
        
        # Wrap and draw quote text
        quote_text = quote_data['text']
        max_width = 580  # Leave margins
        quote_lines = self.wrap_text_for_quote(quote_text, font_quote, max_width, 4)
        
        # Center the quote vertically in the overlay area
        line_height = 22
        total_text_height = len(quote_lines) * line_height + 30  # Include author space
        start_y = 290 + (110 - total_text_height) // 2
        
        # Draw quote text with elegant styling
        for i, line in enumerate(quote_lines):
            y = start_y + (i * line_height)
            bbox = draw.textbbox((0, 0), line, font=font_quote)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            
            # Add subtle text shadow for better readability
            draw.text((x + 1, y + 1), line, fill=(0, 0, 0, 200), font=font_quote)
            # Main quote text in white
            draw.text((x, y), line, fill=(255, 255, 255), font=font_quote)
        
        # Draw author with elegant styling
        author_text = f"- {quote_data['author']}"
        author_y = start_y + len(quote_lines) * line_height + 15
        bbox = draw.textbbox((0, 0), author_text, font=font_author)
        text_width = bbox[2] - bbox[0]
        x = (640 - text_width) // 2
        
        # Author shadow and text
        draw.text((x + 1, author_y + 1), author_text, fill=(0, 0, 0, 200), font=font_author)
        draw.text((x, author_y), author_text, fill=(255, 255, 255), font=font_author)
        
        return display_image
    
    def wrap_text_for_quote(self, text, font, max_width, max_lines=4):
        """Wrap text for quote display with proper line breaks."""
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
                    lines.append(word)
                    if len(lines) >= max_lines:
                        break
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        return lines[:max_lines]
    
    def create_fallback_artwork(self, artwork_data):
        """Create a beautiful fallback artwork when images can't be loaded."""
        # Create a gradient background
        image = Image.new("RGB", (640, 400), (50, 50, 70))
        draw = ImageDraw.Draw(image)
        
        # Create gradient background
        base_color = artwork_data.get('color', '#6A5ACD')
        try:
            # Convert hex to RGB
            base_color = base_color.lstrip('#')
            r, g, b = tuple(int(base_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            r, g, b = 106, 90, 205  # Default purple
        
        # Create gradient
        for y in range(400):
            factor = y / 400
            new_r = int(r * (1 - factor * 0.5))
            new_g = int(g * (1 - factor * 0.5))
            new_b = int(b * (1 - factor * 0.5))
            color = (new_r, new_g, new_b)
            draw.line([(0, y), (640, y)], fill=color)
        
        # Add artistic geometric shapes
        for i in range(5):
            x = random.randint(50, 590)
            y = random.randint(50, 350)
            size = random.randint(30, 80)
            alpha = random.randint(30, 80)
            
            # Create semi-transparent overlay
            overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Draw circle
            overlay_draw.ellipse([x-size, y-size, x+size, y+size], 
                               fill=(255, 255, 255, alpha))
            
            # Composite
            image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        return image
    
    
    def display_error_message(self, title, message):
        """Display an error message on the screen."""
        image = Image.new("RGB", (640, 400), (60, 60, 80))
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
            draw.text((x, 180), title, fill=(255, 100, 100), font=font)
            
            # Draw error message (truncated)
            if len(message) > 60:
                message = message[:57] + "..."
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 220), message, fill=(200, 200, 200), font=font)
        
        self.inky.set_image(image)
        self.inky.show()
