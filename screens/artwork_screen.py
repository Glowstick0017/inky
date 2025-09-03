"""
Artwork with Quotes Screen
Displays full-screen high-quality artwork with inspiring quotes overlay
Updates every 5 minutes with new artwork and quotes from reliable art APIs
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
        
        # Art APIs that provide reliable, high-quality artwork
        self.art_apis = [
            {
                'name': 'Met Museum',
                'type': 'met',
                'search_url': 'https://collectionapi.metmuseum.org/public/collection/v1/search',
                'object_url': 'https://collectionapi.metmuseum.org/public/collection/v1/objects/'
            },
            {
                'name': 'Art Institute Chicago',
                'type': 'aic',
                'search_url': 'https://api.artic.edu/api/v1/artworks/search',
                'detail_url': 'https://api.artic.edu/api/v1/artworks/'
            },
            {
                'name': 'Harvard Art Museums',
                'type': 'harvard',
                'search_url': 'https://api.harvardartmuseums.org/object',
                'api_key': None  # Free tier available
            },
            {
                'name': 'Unsplash',
                'type': 'unsplash',
                'search_url': 'https://api.unsplash.com/photos/random'
            }
        ]
        
        # Refined search terms for high-quality artwork
        self.artwork_keywords = [
            # Art movements and styles
            'impressionism', 'post-impressionism', 'renaissance', 'baroque', 'romanticism',
            'abstract expressionism', 'cubism', 'surrealism', 'art nouveau', 'modernism',
            
            # Subject matter
            'landscape', 'portrait', 'still life', 'nature', 'cityscape', 'seascape',
            'floral', 'architectural', 'botanical', 'geometric', 'minimalist',
            
            # Mediums and techniques
            'oil painting', 'watercolor', 'photography', 'sculpture', 'drawing',
            'printmaking', 'contemporary art', 'fine art', 'classical art'
        ]
        
        # Quote sources for overlay
        self.quote_sources = [
            {
                'name': 'Quotable',
                'url': 'https://api.quotable.io/random',
                'max_length': 140
            },
            {
                'name': 'ZenQuotes',
                'url': 'https://zenquotes.io/api/random',
                'max_length': 140
            }
        ]
        
        # Curated fallback quotes for when APIs fail
        self.fallback_quotes = [
            {"text": "Art enables us to find ourselves and lose ourselves at the same time.", "author": "Thomas Merton"},
            {"text": "Every artist was first an amateur.", "author": "Ralph Waldo Emerson"},
            {"text": "Art is not what you see, but what you make others see.", "author": "Edgar Degas"},
            {"text": "The purpose of art is washing the dust of daily life off our souls.", "author": "Pablo Picasso"},
            {"text": "Creativity takes courage.", "author": "Henri Matisse"},
            {"text": "Art should comfort the disturbed and disturb the comfortable.", "author": "Cesar A. Cruz"}
        ]
    
    def get_met_museum_artwork(self, keyword=None):
        """Get artwork from Metropolitan Museum of Art API."""
        try:
            if keyword is None:
                keyword = random.choice(self.artwork_keywords)
            
            print(f"Searching Met Museum for: {keyword}")
            
            # Search for artwork
            search_params = {
                'hasImages': 'true',
                'isPublicDomain': 'true',
                'q': keyword
            }
            
            response = requests.get(self.art_apis[0]['search_url'], params=search_params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                object_ids = data.get('objectIDs', [])
                
                if object_ids:
                    # Try up to 5 random objects to find one with a good image
                    for _ in range(min(5, len(object_ids))):
                        object_id = random.choice(object_ids)
                        
                        # Get artwork details
                        object_response = requests.get(f"{self.art_apis[0]['object_url']}{object_id}", timeout=10)
                        if object_response.status_code == 200:
                            artwork_data = object_response.json()
                            
                            # Check if artwork has a primary image
                            primary_image = artwork_data.get('primaryImage', '')
                            if primary_image and self.validate_image_url(primary_image):
                                title = artwork_data.get('title', 'Untitled')
                                artist = artwork_data.get('artistDisplayName', 'Unknown Artist')
                                date = artwork_data.get('objectDate', '')
                                
                                print(f"Found Met artwork: {title} by {artist}")
                                return {
                                    'title': title,
                                    'artist': artist,
                                    'date': date,
                                    'source': 'Metropolitan Museum of Art',
                                    'image_url': primary_image,
                                    'color': '#8B4513'
                                }
            
        except Exception as e:
            print(f"Error fetching from Met Museum: {e}")
        return None
    
    def get_art_institute_artwork(self, keyword=None):
        """Get artwork from Art Institute of Chicago API."""
        try:
            if keyword is None:
                keyword = random.choice(self.artwork_keywords)
            
            print(f"Searching Art Institute Chicago for: {keyword}")
            
            # Use the simpler GET endpoint with query parameters
            search_params = {
                'q': keyword,
                'limit': 20,
                'fields': 'id,title,artist_display,image_id,is_public_domain,date_display'
            }
            
            response = requests.get('https://api.artic.edu/api/v1/artworks', params=search_params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                artworks = data.get('data', [])
                
                if artworks:
                    # Try to find artworks with valid images
                    for artwork in artworks:
                        image_id = artwork.get('image_id')
                        if image_id and artwork.get('is_public_domain'):
                            # Construct image URL
                            image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
                            
                            if self.validate_image_url(image_url):
                                title = artwork.get('title', 'Untitled')
                                artist = artwork.get('artist_display', 'Unknown Artist')
                                date = artwork.get('date_display', '')
                                
                                print(f"Found AIC artwork: {title}")
                                return {
                                    'title': title,
                                    'artist': artist,
                                    'date': date,
                                    'source': 'Art Institute of Chicago',
                                    'image_url': image_url,
                                    'color': '#B8860B'
                                }
            
        except Exception as e:
            print(f"Error fetching from Art Institute of Chicago: {e}")
        return None
    
    def get_unsplash_artwork(self, keyword=None):
        """Get curated artwork from Unsplash (requires API key)."""
        try:
            if keyword is None:
                keyword = random.choice(self.artwork_keywords)
            
            print(f"Searching Unsplash for: {keyword} (may require API key)")
            
            # Try without API key first (limited access)
            params = {
                'query': f"{keyword} art museum gallery",
                'orientation': 'landscape',
                'content_filter': 'high'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.art_apis[3]['search_url'], params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                image_url = data.get('urls', {}).get('regular', '')
                if image_url and self.validate_image_url(image_url):
                    description = data.get('description', '') or data.get('alt_description', 'Contemporary Art')
                    artist = data.get('user', {}).get('name', 'Contemporary Artist')
                    color = data.get('color', '#FFFFFF')
                    
                    title = description[:50] + '...' if len(description) > 50 else description
                    
                    print(f"Found Unsplash artwork: {title}")
                    return {
                        'title': title,
                        'artist': artist,
                        'date': 'Contemporary',
                        'source': 'Unsplash',
                        'image_url': image_url,
                        'color': color
                    }
            elif response.status_code == 401:
                print("Unsplash requires API key - skipping")
                    
        except Exception as e:
            print(f"Error fetching from Unsplash: {e}")
        return None
    
    def validate_image_url(self, url):
        """Validate that an image URL is accessible and returns an actual image."""
        try:
            # Quick HEAD request to check if URL is valid
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                return any(img_type in content_type for img_type in ['image/jpeg', 'image/jpg', 'image/png'])
        except:
            pass
        return False
    
    def download_and_resize_artwork(self, image_url):
        """Download and resize artwork to fill the entire 640x400 screen with proper fit."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Download the image
            response = requests.get(image_url, headers=headers, timeout=20)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Get original dimensions
                orig_width, orig_height = image.size
                target_width, target_height = 640, 400
                
                # Calculate scaling to fill the screen while maintaining aspect ratio
                scale_x = target_width / orig_width
                scale_y = target_height / orig_height
                scale = max(scale_x, scale_y)  # Use max to fill the screen
                
                # Calculate new dimensions
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
                
                # Resize the image
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center crop to exact screen size
                left = (new_width - target_width) // 2
                top = (new_height - target_height) // 2
                right = left + target_width
                bottom = top + target_height
                
                image = image.crop((left, top, right, bottom))
                
                # Enhance the image for better e-ink display
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.1)  # Slight contrast boost
                
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.05)  # Very slight sharpening
                
                print(f"Successfully processed image: {target_width}x{target_height}")
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching new artwork...")
        
        try:
            # Try to get artwork from our reliable art APIs
            artwork_data = None
            keyword = random.choice(self.artwork_keywords)
            
            # Try art APIs in order of preference - only free APIs
            art_sources = [
                self.get_met_museum_artwork,
                self.get_art_institute_artwork
            ]
            
            print(f"Searching for: {keyword}")
            
            for source_func in art_sources:
                try:
                    print(f"Trying {source_func.__name__}...")
                    artwork_data = source_func(keyword)
                    if artwork_data and artwork_data.get('image_url'):
                        print(f"✓ Got artwork from {source_func.__name__}")
                        break
                except Exception as e:
                    print(f"✗ Error with {source_func.__name__}: {e}")
                    continue
            
            if not artwork_data:
                print("❌ Could not fetch artwork from any source")
                self.display_error_message("No Artwork Available", "Unable to fetch artwork from any source")
                return
            
            # Get a quote
            quote_data = self.fetch_quote()
            
            # Download and process the artwork
            print(f"Downloading image: {artwork_data['image_url']}")
            artwork_image = self.download_and_resize_artwork(artwork_data['image_url'])
            
            if not artwork_image:
                print("❌ Failed to download/process artwork image")
                self.display_error_message("Image Error", "Could not process artwork image")
                return
            
            # Add quote overlay
            display_image = self.add_quote_overlay(artwork_image, quote_data, artwork_data)
            
            # Store current data
            self.current_artwork = artwork_data
            self.current_quote = quote_data
            
            # Display the final image
            print(f"✓ Displaying: {artwork_data['title']} by {artwork_data['artist']}")
            self.inky.set_image(display_image)
            self.inky.show()
            
        except Exception as e:
            print(f"❌ Error in display: {e}")
            self.display_error_message("Display Error", str(e))
    
    def add_quote_overlay(self, artwork_image, quote_data, artwork_data):
        """Add an elegant quote overlay that doesn't obscure the artwork."""
        # Create overlay
        overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Calculate quote area dimensions - bottom portion of screen
        quote_width = 500  # 78% of screen width for better readability
        quote_height = 120  # Increased height for longer quotes
        quote_x = (640 - quote_width) // 2  # Center horizontally
        quote_y = 280  # Start lower on screen
        
        # Create subtle background with gradient
        for y in range(quote_y, min(quote_y + quote_height, 400)):
            progress = (y - quote_y) / quote_height
            alpha = int(100 + (progress * 50))  # Gradient from 100 to 150 alpha
            overlay_draw.rectangle([(quote_x - 10, y), (quote_x + quote_width + 10, y+1)], 
                                 fill=(0, 0, 0, alpha))
        
        # Add border for definition
        overlay_draw.rectangle([quote_x - 10, quote_y, quote_x + quote_width + 10, quote_y + quote_height], 
                             outline=(255, 255, 255, 120), width=1)
        
        # Composite overlay onto artwork
        display_image = Image.alpha_composite(artwork_image.convert('RGBA'), overlay)
        display_image = display_image.convert('RGB')
        
        # Add text
        draw = ImageDraw.Draw(display_image)
        
        # Font sizes - adjusted for better readability
        try:
            font_quote = font_manager.get_font('quote', 15)
            font_author = font_manager.get_font('italic', 13)
            font_artwork = font_manager.get_font('regular', 11)
        except:
            # Fallback to default fonts if font_manager fails
            font_quote = ImageFont.load_default()
            font_author = ImageFont.load_default()
            font_artwork = ImageFont.load_default()
        
        # Wrap quote text properly
        quote_text = quote_data['text']
        max_text_width = quote_width - 20  # Padding
        quote_lines = self.wrap_text_smart(quote_text, font_quote, max_text_width, max_lines=4)
        
        # Position and draw quote text
        line_height = 18
        text_start_y = quote_y + 15
        
        for i, line in enumerate(quote_lines):
            y = text_start_y + (i * line_height)
            x = quote_x + 10
            
            # Ensure we don't go beyond screen bounds
            if y + line_height > 400:
                break
                
            # Text shadow for readability
            draw.text((x + 1, y + 1), line, fill=(0, 0, 0), font=font_quote)
            # Main text
            draw.text((x, y), line, fill=(255, 255, 255), font=font_quote)
        
        # Draw author
        author_text = f"— {quote_data['author']}"
        author_y = text_start_y + len(quote_lines) * line_height + 8
        
        # Ensure author fits on screen
        if author_y + 15 <= 400:  # Check if author text fits
            # Truncate author if too long
            max_author_width = max_text_width - 20
            if self.get_text_width(author_text, font_author) > max_author_width:
                author_name = quote_data['author']
                if len(author_name) > 25:
                    author_name = author_name[:22] + "..."
                author_text = f"— {author_name}"
            
            author_x = quote_x + 10
            draw.text((author_x + 1, author_y + 1), author_text, fill=(0, 0, 0), font=font_author)
            draw.text((author_x, author_y), author_text, fill=(220, 220, 220), font=font_author)
        
        # Add artwork attribution in top-right corner
        attribution = f"{artwork_data.get('title', 'Untitled')}"
        artist = artwork_data.get('artist', 'Unknown Artist')
        if len(attribution) > 30:
            attribution = attribution[:27] + "..."
        if len(artist) > 25:
            artist = artist[:22] + "..."
            
        # Small attribution area in top-right
        attr_bg_width = 200
        attr_bg_height = 45
        attr_x = 640 - attr_bg_width - 10
        attr_y = 10
        
        # Subtle background for attribution
        attr_overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
        attr_draw = ImageDraw.Draw(attr_overlay)
        attr_draw.rectangle([attr_x, attr_y, attr_x + attr_bg_width, attr_y + attr_bg_height], 
                           fill=(0, 0, 0, 120))
        
        display_image = Image.alpha_composite(display_image.convert('RGBA'), attr_overlay)
        display_image = display_image.convert('RGB')
        
        # Draw attribution text
        draw = ImageDraw.Draw(display_image)
        draw.text((attr_x + 6, attr_y + 5), attribution, fill=(255, 255, 255), font=font_artwork)
        draw.text((attr_x + 6, attr_y + 20), artist, fill=(200, 200, 200), font=font_artwork)
        draw.text((attr_x + 6, attr_y + 32), artwork_data.get('source', ''), fill=(160, 160, 160), font=font_artwork)
        
        return display_image
    
    def wrap_text_smart(self, text, font, max_width, max_lines=4):
        """Smart text wrapping that handles punctuation and doesn't cut words awkwardly."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.get_text_width(test_line, font) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    if len(lines) >= max_lines:
                        break
                    current_line = [word]
                else:
                    # Word too long, try to break it
                    lines.append(word)
                    if len(lines) >= max_lines:
                        break
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        # If we have more text than fits, add ellipsis to last line
        if len(lines) == max_lines and len(words) > sum(len(line.split()) for line in lines):
            last_line = lines[-1]
            while self.get_text_width(last_line + "...", font) > max_width and len(last_line) > 0:
                words_in_line = last_line.split()
                if len(words_in_line) > 1:
                    words_in_line = words_in_line[:-1]
                    last_line = ' '.join(words_in_line)
                else:
                    last_line = last_line[:-1]
            lines[-1] = last_line + "..."
        
        return lines[:max_lines]
    
    def get_text_width(self, text, font):
        """Get the width of text in pixels."""
        try:
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0]
        except:
            return len(text) * 8  # Rough fallback
    
    
    def display_error_message(self, title, message):
        """Display an error message on the screen."""
        image = Image.new("RGB", (640, 400), (40, 40, 60))
        draw = ImageDraw.Draw(image)
        
        try:
            font_title = font_manager.get_font('title', 24)
            font_message = font_manager.get_font('regular', 16)
        except:
            font_title = ImageFont.load_default()
            font_message = ImageFont.load_default()
        
        # Draw error title
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (640 - title_width) // 2
        draw.text((title_x, 160), title, fill=(255, 120, 120), font=font_title)
        
        # Draw error message (with wrapping)
        message_lines = self.wrap_text_smart(message, font_message, 580, max_lines=3)
        line_height = 20
        start_y = 200
        
        for i, line in enumerate(message_lines):
            line_bbox = draw.textbbox((0, 0), line, font=font_message)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (640 - line_width) // 2
            draw.text((line_x, start_y + i * line_height), line, fill=(200, 200, 200), font=font_message)
        
        # Display the error
        self.inky.set_image(image)
        self.inky.show()
