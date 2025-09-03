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
from font_utils import get_artwork_fonts, get_font

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
        
        # Refined search terms specifically for landscape-oriented classical artwork
        self.artwork_keywords = [
            # Landscape-focused art movements
            'landscape impressionism', 'landscape post-impressionism', 'landscape romanticism',
            'landscape realism', 'landscape naturalism', 'landscape baroque',
            
            # Specific landscape subjects - high priority
            'landscape oil painting', 'seascape painting', 'pastoral landscape', 
            'mountain landscape painting', 'river landscape painting', 'forest painting',
            'countryside painting', 'garden painting', 'coastal landscape',
            'valley landscape', 'meadow painting', 'field painting',
            'harbor scene', 'lake landscape', 'woodland scene',
            
            # Classical landscape schools and styles
            'hudson river school', 'barbizon school painting', 'classical landscape',
            'plein air landscape', 'romantic landscape', 'pastoral scene',
            'english landscape', 'dutch landscape', 'italian landscape',
            
            # Still life and botanical (usually horizontal)
            'still life oil painting', 'floral arrangement painting', 'botanical painting',
            'fruit still life', 'flower painting horizontal',
            
            # Architectural and city views (often landscape format)
            'architectural painting', 'city view painting', 'town square painting',
            'bridge painting', 'castle landscape', 'villa landscape',
            
            # Marine and coastal themes
            'marine painting', 'ship painting landscape', 'coastal scene',
            'harbor painting', 'beach scene painting', 'ocean view'
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
        """Get classical paintings from Metropolitan Museum of Art API."""
        try:
            if keyword is None:
                keyword = random.choice(self.artwork_keywords)
            
            print(f"Searching Met Museum for: {keyword}")
            
            # Enhanced search for paintings only
            search_params = {
                'hasImages': 'true',
                'isPublicDomain': 'true',
                'q': f'{keyword} painting',
                'departmentId': '11'  # European Paintings department
            }
            
            response = requests.get(self.art_apis[0]['search_url'], params=search_params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                object_ids = data.get('objectIDs', [])
                
                if object_ids:
                    # Try up to 15 random objects to find a landscape painting
                    attempts = min(15, len(object_ids))
                    for attempt in range(attempts):
                        object_id = random.choice(object_ids)
                        
                        print(f"  Checking Met object {attempt + 1}/{attempts}: {object_id}")
                        
                        # Get artwork details
                        object_response = requests.get(f"{self.art_apis[0]['object_url']}{object_id}", timeout=10)
                        if object_response.status_code == 200:
                            artwork_data = object_response.json()
                            
                            # Filter for paintings only
                            object_name = artwork_data.get('objectName', '').lower()
                            classification = artwork_data.get('classification', '').lower()
                            medium = artwork_data.get('medium', '').lower()
                            title = artwork_data.get('title', '').lower()
                            
                            # Check if it's a painting (not sculpture, decorative arts, etc.)
                            is_painting = any(word in object_name or word in classification or word in medium 
                                            for word in ['painting', 'canvas', 'oil', 'tempera', 'fresco', 'watercolor'])
                            
                            # Avoid decorative objects, sculptures, photographs
                            is_object = any(word in object_name or word in classification or word in title
                                          for word in ['vase', 'bowl', 'cup', 'jar', 'sculpture', 'statue', 
                                                     'photograph', 'print', 'textile', 'furniture', 'jewelry',
                                                     'armor', 'weapon', 'coin', 'medal', 'fragment', 'bust',
                                                     'relief', 'plaque', 'vessel', 'ewer', 'dish'])
                            
                            # Prefer landscape subjects
                            has_landscape_terms = any(word in title 
                                                    for word in ['landscape', 'view', 'countryside', 'valley', 
                                                               'river', 'mountain', 'field', 'meadow', 'coast',
                                                               'seascape', 'harbor', 'garden', 'park'])
                            
                            # Avoid likely portrait subjects
                            has_portrait_terms = any(word in title
                                                   for word in ['portrait', 'lady', 'gentleman', 'woman', 'man',
                                                              'child', 'boy', 'girl', 'duke', 'duchess', 'saint',
                                                              'madonna', 'virgin', 'christ', 'head of'])
                            
                            if is_painting and not is_object:
                                primary_image = artwork_data.get('primaryImage', '')
                                if primary_image and self.validate_image_url(primary_image):
                                    # Check if image is landscape orientation
                                    is_landscape = self.is_landscape_image(primary_image)
                                    
                                    # Preference scoring
                                    score = 0
                                    if is_landscape:
                                        score += 10
                                    if has_landscape_terms:
                                        score += 5
                                    if has_portrait_terms:
                                        score -= 8
                                    
                                    print(f"    Artwork score: {score} ({'landscape' if is_landscape else 'portrait'}) - {artwork_data.get('title', 'Untitled')}")
                                    
                                    # Accept if landscape or if we've tried many attempts
                                    if is_landscape or (attempt > 10 and score >= 0):
                                        title = artwork_data.get('title', 'Untitled')
                                        artist = artwork_data.get('artistDisplayName', 'Unknown Artist')
                                        date = artwork_data.get('objectDate', '')
                                        
                                        print(f"✓ Selected Met painting: {title} by {artist}")
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
        """Get paintings from Art Institute of Chicago API."""
        try:
            if keyword is None:
                keyword = random.choice(self.artwork_keywords)
            
            print(f"Searching Art Institute Chicago for: {keyword}")
            
            # Focus on paintings department with enhanced search
            search_params = {
                'q': f'{keyword} painting',
                'limit': 30,
                'fields': 'id,title,artist_display,image_id,is_public_domain,date_display,artwork_type_title,medium_display,classification_titles'
            }
            
            response = requests.get('https://api.artic.edu/api/v1/artworks', params=search_params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                artworks = data.get('data', [])
                
                if artworks:
                    # Filter for paintings and try to find landscape oriented ones
                    checked_count = 0
                    for artwork in artworks:
                        if checked_count >= 15:  # Limit checks for performance
                            break
                            
                        image_id = artwork.get('image_id')
                        if image_id and artwork.get('is_public_domain'):
                            checked_count += 1
                            
                            print(f"  Checking AIC artwork {checked_count}: {artwork.get('title', 'Untitled')}")
                            
                            # Check if it's a painting
                            artwork_type = artwork.get('artwork_type_title', '').lower()
                            medium = artwork.get('medium_display', '').lower()
                            classifications = artwork.get('classification_titles', [])
                            classification_text = ' '.join(classifications).lower() if classifications else ''
                            title = artwork.get('title', '').lower()
                            
                            # Must be a painting
                            is_painting = any(word in artwork_type or word in medium or word in classification_text
                                            for word in ['painting', 'oil', 'canvas', 'tempera', 'fresco', 'watercolor'])
                            
                            # Avoid non-painting objects
                            is_object = any(word in artwork_type or word in medium or word in classification_text
                                          for word in ['sculpture', 'textile', 'photograph', 'print', 'drawing',
                                                     'vessel', 'furniture', 'jewelry', 'armor', 'coin'])
                            
                            # Prefer landscape subjects
                            has_landscape_terms = any(word in title 
                                                    for word in ['landscape', 'view', 'countryside', 'valley', 
                                                               'river', 'mountain', 'field', 'meadow', 'coast',
                                                               'seascape', 'harbor', 'garden', 'park'])
                            
                            # Avoid likely portrait subjects
                            has_portrait_terms = any(word in title
                                                   for word in ['portrait', 'lady', 'gentleman', 'woman', 'man',
                                                              'child', 'boy', 'girl', 'self-portrait', 'head'])
                            
                            if is_painting and not is_object:
                                # Construct image URL
                                image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
                                
                                if self.validate_image_url(image_url):
                                    is_landscape = self.is_landscape_image(image_url)
                                    
                                    # Preference scoring
                                    score = 0
                                    if is_landscape:
                                        score += 10
                                    if has_landscape_terms:
                                        score += 5
                                    if has_portrait_terms:
                                        score -= 8
                                    
                                    print(f"    Artwork score: {score} ({'landscape' if is_landscape else 'portrait'})")
                                    
                                    # Accept if landscape or if we've checked many
                                    if is_landscape or (checked_count > 10 and score >= 0):
                                        title = artwork.get('title', 'Untitled')
                                        artist = artwork.get('artist_display', 'Unknown Artist')
                                        date = artwork.get('date_display', '')
                                        
                                        print(f"✓ Selected AIC painting: {title}")
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
        """Get curated classical artwork from Unsplash (requires API key)."""
        try:
            if keyword is None:
                keyword = random.choice(self.artwork_keywords)
            
            print(f"Searching Unsplash for: {keyword} (may require API key)")
            
            # Focus on classical paintings and artwork
            params = {
                'query': f"{keyword} classical painting museum fine art",
                'orientation': 'landscape',  # Force landscape orientation
                'content_filter': 'high',
                'order_by': 'relevant'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.art_apis[3]['search_url'], params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                image_url = data.get('urls', {}).get('regular', '')
                if image_url and self.validate_image_url(image_url):
                    description = data.get('description', '') or data.get('alt_description', 'Classical Art')
                    artist = data.get('user', {}).get('name', 'Contemporary Artist')
                    color = data.get('color', '#FFFFFF')
                    
                    # Clean up description to focus on artwork
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
    
    def is_landscape_image(self, url):
        """Check if an image is in landscape orientation (width > height)."""
        try:
            # Download first few KB to get image header with dimensions
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Range': 'bytes=0-32768'  # Get first 32KB which should contain header
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code in [200, 206]:  # 206 is partial content
                try:
                    image_data = BytesIO(response.content)
                    with Image.open(image_data) as img:
                        width, height = img.size
                        print(f"Image dimensions: {width}x{height} ({'landscape' if width > height else 'portrait'})")
                        return width > height
                except Exception as e:
                    print(f"Could not parse image dimensions from partial data: {e}")
                    # If partial fails, try a small full download
                    try:
                        full_response = requests.get(url, timeout=15, stream=True)
                        full_response.raw.decode_content = True
                        
                        # Read in chunks until we can get dimensions or hit limit
                        chunk_data = BytesIO()
                        max_size = 100 * 1024  # 100KB limit for dimension check
                        current_size = 0
                        
                        for chunk in full_response.iter_content(chunk_size=8192):
                            if chunk:
                                chunk_data.write(chunk)
                                current_size += len(chunk)
                                
                                # Try to open image after each chunk
                                try:
                                    chunk_data.seek(0)
                                    with Image.open(chunk_data) as img:
                                        width, height = img.size
                                        print(f"Image dimensions: {width}x{height} ({'landscape' if width > height else 'portrait'})")
                                        return width > height
                                except:
                                    chunk_data.seek(0, 2)  # Seek to end for next write
                                    
                                # Stop if we've read enough
                                if current_size > max_size:
                                    break
                    except Exception as e2:
                        print(f"Could not determine image orientation: {e2}")
        except Exception as e:
            print(f"Error checking image orientation: {e}")
        
        # Default to False (reject) if we can't determine orientation
        # This is more conservative - we'd rather skip an image than show a portrait one
        print("Could not determine image orientation - assuming portrait (rejecting)")
        return False
    
    def download_and_resize_artwork(self, image_url):
        """Download and resize artwork to fit the 640x400 landscape screen optimally."""
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
                
                print(f"Original image: {orig_width}x{orig_height}")
                
                # Check if image is portrait oriented
                is_portrait = orig_height > orig_width
                
                if is_portrait:
                    print("⚠️  Portrait image detected - applying special handling")
                    
                    # For portrait images, we have a few options:
                    # 1. Scale to fit width and center vertically (may show black bars)
                    # 2. Scale to fit height and crop sides (may lose content)
                    # 3. Try to find the best crop area
                    
                    # Option 1: Scale to fit width (preserve full width, center vertically)
                    scale = target_width / orig_width
                    new_width = target_width
                    new_height = int(orig_height * scale)
                    
                    # Resize image
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Create final canvas and center the image
                    final_image = Image.new('RGB', (target_width, target_height), (20, 20, 20))  # Dark background
                    
                    # Center the image vertically
                    y_offset = (target_height - new_height) // 2
                    final_image.paste(image, (0, y_offset))
                    
                    image = final_image
                    print(f"Portrait image fitted: {target_width}x{target_height} with vertical centering")
                
                else:
                    # Standard landscape processing
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
                    print(f"Landscape image cropped: {target_width}x{target_height}")
                
                # Enhance the image for better e-ink display
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.1)  # Slight contrast boost
                
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.05)  # Very slight sharpening
                
                print(f"✓ Successfully processed image: {target_width}x{target_height}")
                return image
                
        except Exception as e:
            print(f"❌ Error downloading/resizing artwork: {e}")
            
        return None
    
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
        """Add an elegant quote overlay in the bottom left corner."""
        # Create overlay
        overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Calculate quote area dimensions - bottom left corner
        quote_width = 300  # Smaller width for corner placement
        quote_height = 110  # Height for quote area
        quote_x = 20  # 20px from left edge
        quote_y = 270  # Start lower on screen (bottom area)
        
        # Create subtle background with gradient
        for y in range(quote_y, min(quote_y + quote_height, 400)):
            progress = (y - quote_y) / quote_height
            alpha = int(110 + (progress * 40))  # Gradient from 110 to 150 alpha
            overlay_draw.rectangle([(quote_x - 5, y), (quote_x + quote_width + 5, y+1)], 
                                 fill=(0, 0, 0, alpha))
        
        # Add border for definition
        overlay_draw.rectangle([quote_x - 5, quote_y, quote_x + quote_width + 5, quote_y + quote_height], 
                             outline=(255, 255, 255, 100), width=1)
        
        # Composite overlay onto artwork
        display_image = Image.alpha_composite(artwork_image.convert('RGBA'), overlay)
        display_image = display_image.convert('RGB')
        
        # Add text
        draw = ImageDraw.Draw(display_image)
        
        # Font sizes - adjusted for corner placement
        try:
            fonts = get_artwork_fonts()
            font_quote = fonts['quote']     # 14pt quote font
            font_author = fonts['author']   # 12pt italic font
        except:
            # Fallback to default fonts if font utilities fail
            font_quote = get_font('quote', 14)
            font_author = get_font('italic', 12)
        
        # Wrap quote text properly for smaller area
        quote_text = quote_data['text']
        max_text_width = quote_width - 20  # Padding
        quote_lines = self.wrap_text_smart(quote_text, font_quote, max_text_width, max_lines=4)
        
        # Position and draw quote text
        line_height = 16
        text_start_y = quote_y + 10
        
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
        author_y = text_start_y + len(quote_lines) * line_height + 6
        
        # Ensure author fits on screen
        if author_y + 15 <= 400:  # Check if author text fits
            # Truncate author if too long
            max_author_width = max_text_width - 20
            if self.get_text_width(author_text, font_author) > max_author_width:
                author_name = quote_data['author']
                if len(author_name) > 20:
                    author_name = author_name[:17] + "..."
                author_text = f"— {author_name}"
            
            author_x = quote_x + 10
            draw.text((author_x + 1, author_y + 1), author_text, fill=(0, 0, 0), font=font_author)
            draw.text((author_x, author_y), author_text, fill=(200, 200, 200), font=font_author)
        
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
            fonts = get_artwork_fonts()
            font_title = fonts['title']     # 24pt title font
            font_message = fonts['message'] # 16pt regular font
        except:
            font_title = get_font('title', 24)
            font_message = get_font('regular', 16)
        
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
