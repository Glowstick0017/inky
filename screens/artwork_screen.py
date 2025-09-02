"""
Artwork with Quotes Screen
Displays full-screen high-quality artwork with inspiring quotes overlay
Updates every 5 minutes with new artwork and quotes
"""

import requests
import json
import random
import ssl
import urllib3
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
from .base_screen import BaseScreen
import config
from font_manager import font_manager

# Disable SSL warnings for older systems
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
                'name': 'Direct Images',
                'type': 'direct',
                'search_url': None
            },
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
        
        # Fallback high-quality images - expanded collection with more variety
        self.fallback_images = [
            'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/The_Great_Wave_off_Kanagawa.jpg/1280px-The_Great_Wave_off_Kanagawa.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/687px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Leonardo_da_Vinci_-_Mona_Lisa_%28Louvre%2C_Paris%29.jpg/800px-Leonardo_da_Vinci_-_Mona_Lisa_%28Louvre%2C_Paris%29.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_WGA24666.jpg/800px-Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_WGA24666.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Monet_Water_Lilies_1919_Metropolitan_Museum.jpg/1280px-Monet_Water_Lilies_1919_Metropolitan_Museum.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Tsunami_by_hokusai_19th_century.jpg/1280px-Tsunami_by_hokusai_19th_century.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Vincent_van_Gogh_-_The_Potato_Eaters_-_Google_Art_Project_%282%29.jpg/1280px-Vincent_van_Gogh_-_The_Potato_Eaters_-_Google_Art_Project_%282%29.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Self-Portrait_with_a_Straw_Hat_%28obverse-_The_Potato_Peeler%29_%28F_61v_JH_1302%29_by_Vincent_van_Gogh.jpg/800px-Self-Portrait_with_a_Straw_Hat_%28obverse-_The_Potato_Peeler%29_%28F_61v_JH_1302%29_by_Vincent_van_Gogh.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg/1280px-A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg/800px-Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/David_-_The_Death_of_Socrates.jpg/1280px-David_-_The_Death_of_Socrates.jpg'
        ]
        
        # Matching artwork info for fallback images
        self.fallback_artwork_info = [
            {'title': 'The Starry Night', 'artist': 'Vincent van Gogh', 'color': '#1E3A8A'},
            {'title': 'The Great Wave off Kanagawa', 'artist': 'Katsushika Hokusai', 'color': '#0F4C75'},
            {'title': 'The Scream', 'artist': 'Edvard Munch', 'color': '#DC2626'},
            {'title': 'Mona Lisa', 'artist': 'Leonardo da Vinci', 'color': '#8B5A2B'},
            {'title': 'Girl with a Pearl Earring', 'artist': 'Johannes Vermeer', 'color': '#1F2937'},
            {'title': 'Water Lilies', 'artist': 'Claude Monet', 'color': '#059669'},
            {'title': 'The Great Wave (Alt)', 'artist': 'Katsushika Hokusai', 'color': '#1E40AF'},
            {'title': 'The Potato Eaters', 'artist': 'Vincent van Gogh', 'color': '#92400E'},
            {'title': 'Self-Portrait with Straw Hat', 'artist': 'Vincent van Gogh', 'color': '#B45309'},
            {'title': 'A Sunday on La Grande Jatte', 'artist': 'Georges Seurat', 'color': '#047857'},
            {'title': 'Wanderer above the Sea of Fog', 'artist': 'Caspar David Friedrich', 'color': '#374151'},
            {'title': 'The Death of Socrates', 'artist': 'Jacques-Louis David', 'color': '#7C2D12'}
        ]
    
    def get_direct_artwork(self, keyword=None):
        """Get artwork directly from our curated collection."""
        try:
            # Use rotation to ensure we cycle through all images
            # Note: rotation_index is incremented in display() method
            index = self.artwork_rotation_index % len(self.fallback_images)
            url = self.fallback_images[index]
            artwork_info = self.fallback_artwork_info[index]
            
            print(f"Using direct artwork: {artwork_info['title']} by {artwork_info['artist']}")
            
            return {
                'title': artwork_info['title'],
                'artist': artwork_info['artist'],
                'source': 'Curated Collection',
                'image_url': url,
                'color': artwork_info['color']
            }
        except Exception as e:
            print(f"Error getting direct artwork: {e}")
            return None

    def get_unsplash_artwork(self, keyword=None):
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
            
            # Try with SSL verification first, then without if needed
            try:
                response = requests.get(url, params=params, headers=headers, timeout=15, verify=True)
            except (requests.exceptions.SSLError, ssl.SSLError):
                print(f"SSL verification failed for Unsplash, trying without verification...")
                response = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Successfully fetched Unsplash artwork: {data.get('description', 'Untitled')}")
                return {
                    'title': data.get('description', 'Untitled'),
                    'artist': data.get('user', {}).get('name', 'Unknown Artist'),
                    'source': 'Unsplash',
                    'image_url': data.get('urls', {}).get('regular', ''),
                    'color': data.get('color', '#FFFFFF')
                }
            else:
                print(f"Unsplash API returned status code: {response.status_code}")
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
            
            # Try with SSL verification first, then without if needed
            try:
                response = requests.get(image_url, headers=headers, timeout=20, verify=True)
            except (requests.exceptions.SSLError, ssl.SSLError):
                print(f"SSL verification failed for image, trying without verification...")
                response = requests.get(image_url, headers=headers, timeout=20, verify=False)
            
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
        """Get artwork from fallback URLs with proper variety tracking."""
        try:
            # Use rotation index to ensure variety in fallback images too
            index = self.artwork_rotation_index % len(self.fallback_images)
            url = self.fallback_images[index]
            artwork_info = self.fallback_artwork_info[index]
            
            print(f"Using fallback artwork: {artwork_info['title']} by {artwork_info['artist']}")
            
            return {
                'title': artwork_info['title'],
                'artist': artwork_info['artist'],
                'source': 'Classic Collection',
                'image_url': url,
                'color': artwork_info['color']
            }
        except Exception as e:
            print(f"Error getting fallback artwork: {e}")
            # Ultimate fallback with generated artwork
            return {
                'title': 'Generated Artwork',
                'artist': 'AI Assistant',
                'source': 'Generated',
                'image_url': None,  # Will trigger generated artwork
                'color': '#6A5ACD'
            }
    
    def fetch_quote(self):
        """Fetch an inspiring quote from multiple sources with SSL error handling."""
        try:
            # Try to fetch from quote APIs with SSL verification disabled for older systems
            for source in self.quote_sources:
                try:
                    # Try with SSL verification first
                    try:
                        response = requests.get(source['url'], timeout=10, verify=True)
                    except (requests.exceptions.SSLError, ssl.SSLError):
                        # If SSL fails, try without verification (for older Pi systems)
                        print(f"SSL verification failed for {source['name']}, trying without verification...")
                        response = requests.get(source['url'], timeout=10, verify=False)
                    
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
        print("Using fallback quote due to API failures")
        return random.choice(self.fallback_quotes)
    
    def display(self):
        """Display full-screen artwork with an inspiring quote overlay."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Artwork + Quote screen...")
        
        try:
            # Get fresh artwork (cycles through keywords for variety)
            artwork_data = None
            sources_to_try = [
                self.get_direct_artwork,      # Try our curated collection first
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
                    if source_func.__name__ in ['get_artwork_from_fallback', 'get_direct_artwork']:
                        artwork_data = source_func()
                    else:
                        artwork_data = source_func(keyword)
                    if artwork_data and artwork_data.get('image_url'):
                        print(f"Successfully got artwork from {source_func.__name__}")
                        break
                    elif artwork_data and not artwork_data.get('image_url'):
                        print(f"Got artwork metadata but no URL from {source_func.__name__}")
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
        """Add highly visible quote overlay with enhanced readability."""
        # Create overlay for quote (bottom portion) with stronger background
        overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Create stronger gradient overlay for maximum text readability
        for y in range(260, 400):  # Bottom 140 pixels for quote (more space)
            progress = (y - 260) / 140
            # Much stronger gradient for better text visibility
            alpha = int(180 + (progress * 75))  # Range from 180 to 255 alpha
            overlay_draw.rectangle([(0, y), (640, y+1)], fill=(0, 0, 0, alpha))
        
        # Add strong border at top of quote area with glow effect
        for i in range(3):
            alpha = 120 - (i * 30)
            overlay_draw.rectangle([(0, 260 + i), (640, 262 + i)], fill=(255, 255, 255, alpha))
        
        # Composite the overlay onto the artwork
        display_image = Image.alpha_composite(artwork_image.convert('RGBA'), overlay)
        display_image = display_image.convert('RGB')
        
        # Add quote text with maximum visibility
        draw = ImageDraw.Draw(display_image)
        
        # Use the font manager for better fonts
        font_quote = font_manager.get_font('quote', 20)  # Larger quote text
        font_author = font_manager.get_font('italic', 18)  # Larger author text
        
        # Wrap and draw quote text
        quote_text = quote_data['text']
        max_width = 560  # Slightly narrower for better readability
        quote_lines = self.wrap_text_for_quote(quote_text, font_quote, max_width, 4)
        
        # Center the quote vertically in the overlay area
        line_height = 26  # More line spacing
        total_text_height = len(quote_lines) * line_height + 35  # Include author space
        start_y = 270 + (130 - total_text_height) // 2
        
        # Draw quote text with maximum visibility techniques
        for i, line in enumerate(quote_lines):
            y = start_y + (i * line_height)
            bbox = draw.textbbox((0, 0), line, font=font_quote)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            
            # Multiple shadow layers for extreme visibility
            shadow_offsets = [(3, 3), (2, 2), (1, 1), (-1, -1), (-2, -2)]
            for offset in shadow_offsets:
                shadow_alpha = 150 if abs(offset[0]) <= 1 else 100
                draw.text((x + offset[0], y + offset[1]), line, fill=(0, 0, 0), font=font_quote)
            
            # Outline effect for even better visibility
            outline_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for offset in outline_offsets:
                draw.text((x + offset[0], y + offset[1]), line, fill=(0, 0, 0), font=font_quote)
            
            # Main quote text in bright white
            draw.text((x, y), line, fill=(255, 255, 255), font=font_quote)
        
        # Draw author with enhanced visibility
        author_text = f"— {quote_data['author']}"
        author_y = start_y + len(quote_lines) * line_height + 20
        bbox = draw.textbbox((0, 0), author_text, font=font_author)
        text_width = bbox[2] - bbox[0]
        x = (640 - text_width) // 2
        
        # Author shadow and outline
        for offset in shadow_offsets:
            shadow_alpha = 150 if abs(offset[0]) <= 1 else 100
            draw.text((x + offset[0], author_y + offset[1]), author_text, fill=(0, 0, 0), font=font_author)
        
        for offset in outline_offsets:
            draw.text((x + offset[0], author_y + offset[1]), author_text, fill=(0, 0, 0), font=font_author)
        
        # Main author text in slightly dimmed white for elegance
        draw.text((x, author_y), author_text, fill=(240, 240, 240), font=font_author)
        
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
        
        # Create gradient background based on artwork theme
        base_color = artwork_data.get('color', '#6A5ACD')
        try:
            # Convert hex to RGB
            base_color = base_color.lstrip('#')
            r, g, b = tuple(int(base_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            r, g, b = 106, 90, 205  # Default purple
        
        # Create multi-layer gradient for depth
        for y in range(400):
            factor = y / 400
            # Layer 1: Base gradient
            new_r = int(r * (1 - factor * 0.6))
            new_g = int(g * (1 - factor * 0.6))
            new_b = int(b * (1 - factor * 0.6))
            
            # Layer 2: Add some warm tones at the bottom
            if y > 200:
                warm_factor = (y - 200) / 200
                new_r = min(255, int(new_r + warm_factor * 30))
                new_g = min(255, int(new_g + warm_factor * 15))
            
            color = (new_r, new_g, new_b)
            draw.line([(0, y), (640, y)], fill=color)
        
        # Add artistic geometric patterns based on artwork style
        title = artwork_data.get('title', '').lower()
        
        if 'abstract' in title or 'modern' in title:
            # Abstract geometric shapes
            for i in range(8):
                x = random.randint(50, 590)
                y = random.randint(50, 350)
                size = random.randint(20, 100)
                alpha = random.randint(20, 60)
                
                overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # Mix of circles and rectangles
                if i % 2 == 0:
                    overlay_draw.ellipse([x-size, y-size, x+size, y+size], 
                                       fill=(255, 255, 255, alpha))
                else:
                    overlay_draw.rectangle([x-size, y-size, x+size, y+size], 
                                         fill=(255, 255, 255, alpha))
                
                image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        elif 'landscape' in title or 'nature' in title:
            # Nature-inspired flowing lines
            for i in range(3):
                y_base = random.randint(100, 300)
                overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # Draw flowing wave-like lines
                points = []
                for x in range(0, 640, 20):
                    y_offset = int(30 * random.uniform(-1, 1))
                    points.append((x, y_base + y_offset))
                
                for j in range(len(points) - 1):
                    overlay_draw.line([points[j], points[j+1]], fill=(255, 255, 255, 40), width=3)
                
                image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        else:
            # Classic artistic elements - gentle circles and lines
            for i in range(5):
                x = random.randint(100, 540)
                y = random.randint(100, 300)
                size = random.randint(40, 120)
                alpha = random.randint(15, 45)
                
                overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # Gentle circles with soft edges
                overlay_draw.ellipse([x-size, y-size, x+size, y+size], 
                                   fill=(255, 255, 255, alpha))
                
                image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        # Add title text if available
        title = artwork_data.get('title', 'Generated Art')
        artist = artwork_data.get('artist', 'AI Assistant')
        
        # Use font manager for better fonts
        font_title = font_manager.get_font('title', 32)
        font_artist = font_manager.get_font('regular', 20)
        
        # Add semi-transparent overlay for text
        text_overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_overlay)
        
        # Background for text
        text_draw.rectangle([(50, 150), (590, 250)], fill=(0, 0, 0, 100))
        
        # Title text
        bbox = text_draw.textbbox((0, 0), title, font=font_title)
        text_width = bbox[2] - bbox[0]
        x = (640 - text_width) // 2
        text_draw.text((x, 170), title, fill=(255, 255, 255, 255), font=font_title)
        
        # Artist text
        bbox = text_draw.textbbox((0, 0), artist, font=font_artist)
        text_width = bbox[2] - bbox[0]
        x = (640 - text_width) // 2
        text_draw.text((x, 210), artist, fill=(200, 200, 200, 255), font=font_artist)
        
        # Composite text overlay
        image = Image.alpha_composite(image.convert('RGBA'), text_overlay).convert('RGB')
        
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
