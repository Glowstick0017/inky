"""
Classical Artwork Screen
Displays full-screen high-quality artwork from multiple sources
Updates every 5 minutes with a new piece of art
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
            },
            {
                'name': 'Met Museum',
                'type': 'met',
                'base_url': 'https://collectionapi.metmuseum.org/public/collection/v1'
            }
        ]
        
        # High-quality search terms for artwork
        self.artwork_keywords = [
            'classical painting', 'renaissance art', 'baroque painting', 'impressionist painting',
            'landscape painting', 'portrait painting', 'still life painting', 'abstract art',
            'modern art', 'contemporary art', 'sculpture', 'fine art photography',
            'architectural photography', 'nature photography', 'minimalist art'
        ]
        
        # Fallback high-quality images
        self.fallback_images = [
            'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/The_Great_Wave_off_Kanagawa.jpg/1280px-The_Great_Wave_off_Kanagawa.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/687px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg'
        ]
    
    def get_unsplash_artwork(self):
        """Get high-quality artwork from Unsplash (no API key needed for basic usage)."""
        try:
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
    
    def get_wikimedia_artwork(self):
        """Get artwork from Wikimedia Commons."""
        try:
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
    
    def display(self):
        """Display full-screen high-quality artwork."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Artwork screen...")
        
        try:
            # Try different sources for artwork
            artwork_data = None
            sources_to_try = [
                self.get_unsplash_artwork,
                self.get_wikimedia_artwork,
                self.get_artwork_from_fallback
            ]
            
            for source_func in sources_to_try:
                try:
                    artwork_data = source_func()
                    if artwork_data and artwork_data.get('image_url'):
                        break
                except Exception as e:
                    print(f"Error with source {source_func.__name__}: {e}")
                    continue
            
            if not artwork_data:
                print("Could not fetch any artwork, creating fallback")
                artwork_data = {
                    'title': 'Art Gallery',
                    'artist': 'Dashboard',
                    'source': 'Internal',
                    'image_url': None,
                    'color': '#6A5ACD'
                }
            
            # Download and process the artwork
            if artwork_data.get('image_url'):
                print(f"Displaying: {artwork_data['title']} by {artwork_data['artist']}")
                artwork_image = self.download_and_resize_artwork(artwork_data['image_url'])
            else:
                artwork_image = None
            
            # If we couldn't get an image, create a beautiful fallback
            if not artwork_image:
                artwork_image = self.create_fallback_artwork(artwork_data)
            
            # Create overlay for text (bottom portion)
            overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Create gradient overlay at bottom for text
            for y in range(320, 400):  # Bottom 80 pixels
                alpha = int(180 * ((y - 320) / 80))  # Gradient from 0 to 180 alpha
                overlay_draw.rectangle([(0, y), (640, y+1)], fill=(0, 0, 0, alpha))
            
            # Composite the overlay onto the artwork
            display_image = Image.alpha_composite(artwork_image.convert('RGBA'), overlay)
            display_image = display_image.convert('RGB')
            
            # Add text information with better typography
            draw = ImageDraw.Draw(display_image)
            
            try:
                # Try to load better fonts if available, otherwise use default
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default() 
                font_small = ImageFont.load_default()
            except:
                font_large = font_medium = font_small = None
            
            # Draw title (large, white text at bottom)
            title = artwork_data.get('title', 'Untitled')
            if len(title) > 35:
                title = title[:32] + "..."
                
            if font_large:
                bbox = draw.textbbox((0, 0), title, font=font_large)
                text_width = bbox[2] - bbox[0]
                x = 20
                y = 340
                # Add shadow effect
                draw.text((x+2, y+2), title, fill=(0, 0, 0), font=font_large)
                draw.text((x, y), title, fill=(255, 255, 255), font=font_large)
            
            # Draw artist and source
            artist_text = artwork_data.get('artist', 'Unknown Artist')
            source_text = artwork_data.get('source', '')
            info_text = f"{artist_text}"
            if source_text:
                info_text += f" • {source_text}"
                
            if len(info_text) > 50:
                info_text = info_text[:47] + "..."
                
            if font_medium:
                x = 20
                y = 365
                # Add shadow effect
                draw.text((x+1, y+1), info_text, fill=(0, 0, 0), font=font_medium)
                draw.text((x, y), info_text, fill=(200, 200, 200), font=font_medium)
            
            # Display timestamp in corner
            timestamp = datetime.now().strftime("%H:%M")
            if font_small:
                bbox = draw.textbbox((0, 0), timestamp, font=font_small)
                text_width = bbox[2] - bbox[0]
                x = 640 - text_width - 20
                y = 370
                draw.text((x+1, y+1), timestamp, fill=(0, 0, 0), font=font_small)
                draw.text((x, y), timestamp, fill=(150, 150, 150), font=font_small)
            
            # Display the final image
            self.inky.set_image(display_image)
            self.inky.show()
            
            self.current_artwork = artwork_data
            
        except Exception as e:
            print(f"Error displaying artwork: {e}")
            self.display_error_message("Artwork Error", str(e))
    
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
