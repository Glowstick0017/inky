"""
Classical Artwork Screen
Displays rotating classical artwork from the Metropolitan Museum of Art API
Updates every 5 minutes with a new piece of art
"""

import requests
import json
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .base_screen import BaseScreen
import config

class ArtworkScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.ARTWORK_UPDATE_INTERVAL
        self.current_artwork = None
        self.met_base_url = "https://collectionapi.metmuseum.org/public/collection/v1"
        
        # Smaller cache for Pi Zero 2 W
        self.artwork_cache = []
        self.cache_populated = False
    
    def get_classical_artwork_ids(self):
        """Get a collection of classical artwork IDs from the Met Museum API."""
        try:
            # Search for paintings from classical periods
            search_url = f"{self.met_base_url}/search"
            
            # Search for classical European paintings
            params = {
                'q': 'painting',
                'hasImages': 'true',
                'departmentId': 11,  # European Paintings department
                'dateBegin': 1400,
                'dateEnd': 1900
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('objectIDs'):
                    # Get smaller sample for Pi Zero 2 W (less memory)
                    all_ids = data['objectIDs']
                    return random.sample(all_ids, min(20, len(all_ids)))
            
            # Fallback to some known classical artwork IDs
            return [436535, 436532, 437133, 435844, 436106, 437329, 437394, 45734, 459123]
            
        except Exception as e:
            print(f"Error fetching artwork IDs: {e}")
            # Fallback IDs
            return [436535, 436532, 437133, 435844, 436106]
    
    def get_artwork_details(self, object_id):
        """Get detailed information about a specific artwork."""
        try:
            url = f"{self.met_base_url}/objects/{object_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Ensure the artwork has an image and is public domain
                if (data.get('primaryImage') and 
                    data.get('isPublicDomain', False) and
                    data.get('objectName') in ['Painting', 'Print', 'Drawing']):
                    
                    return {
                        'title': data.get('title', 'Untitled'),
                        'artist': data.get('artistDisplayName', 'Unknown Artist'),
                        'date': data.get('objectDate', 'Unknown Date'),
                        'image_url': data.get('primaryImage'),
                        'culture': data.get('culture', ''),
                        'medium': data.get('medium', ''),
                        'department': data.get('department', '')
                    }
            return None
            
        except Exception as e:
            print(f"Error fetching artwork details for ID {object_id}: {e}")
            return None
    
    def download_and_resize_image(self, image_url, max_width=400, max_height=250):
        """Download and resize artwork image to fit the display (optimized for Pi Zero)."""
        try:
            response = requests.get(image_url, timeout=15)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Calculate resize maintaining aspect ratio
                aspect_ratio = image.width / image.height
                
                if aspect_ratio > max_width / max_height:
                    # Width is the limiting factor
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:
                    # Height is the limiting factor
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                return image
                
        except Exception as e:
            print(f"Error downloading/resizing image: {e}")
            
        return None
    
    def create_fallback_image(self):
        """Create a fallback image when artwork can't be loaded."""
        image = Image.new("RGB", (400, 300), (245, 245, 220))  # Beige background
        draw = ImageDraw.Draw(image)
        
        try:
            # Try to use a built-in font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = None
            font_small = None
        
        # Draw placeholder content
        text = "Classical Artwork"
        if font_large:
            bbox = draw.textbbox((0, 0), text, font=font_large)
            text_width = bbox[2] - bbox[0]
            x = (400 - text_width) // 2
            draw.text((x, 120), text, fill=(60, 60, 60), font=font_large)
        
        subtext = "Loading..."
        if font_small:
            bbox = draw.textbbox((0, 0), subtext, font=font_small)
            text_width = bbox[2] - bbox[0]
            x = (400 - text_width) // 2
            draw.text((x, 160), subtext, fill=(100, 100, 100), font=font_small)
        
        return image
    
    def display(self):
        """Display the current classical artwork."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Classical Artwork screen...")
        
        try:
            # Populate cache if needed
            if not self.cache_populated:
                print("Populating artwork cache...")
                self.artwork_cache = self.get_classical_artwork_ids()
                self.cache_populated = True
            
            # Try to get a new artwork
            attempts = 0
            artwork_data = None
            
            while attempts < 5 and not artwork_data:
                if self.artwork_cache:
                    object_id = random.choice(self.artwork_cache)
                    artwork_data = self.get_artwork_details(object_id)
                    attempts += 1
                else:
                    break
            
            if not artwork_data:
                print("Could not fetch artwork data, using fallback")
                artwork_image = self.create_fallback_image()
                title = "Classical Artwork"
                artist = "Unable to load"
                date = ""
            else:
                print(f"Displaying: {artwork_data['title']} by {artwork_data['artist']}")
                
                # Download and resize the artwork image
                artwork_image = self.download_and_resize_image(artwork_data['image_url'])
                
                if not artwork_image:
                    artwork_image = self.create_fallback_image()
                    
                title = artwork_data['title']
                artist = artwork_data['artist']
                date = artwork_data['date']
            
            # Create the full display image
            display_image = Image.new("RGB", (self.inky.width, self.inky.height), (255, 255, 255))
            
            # Paste the artwork image centered
            if artwork_image:
                x_offset = (self.inky.width - artwork_image.width) // 2
                y_offset = 20  # Leave space at top for title
                display_image.paste(artwork_image, (x_offset, y_offset))
            
            # Add text information
            draw = ImageDraw.Draw(display_image)
            
            try:
                font_title = ImageFont.load_default()
                font_info = ImageFont.load_default()
            except:
                font_title = None
                font_info = None
            
            # Draw title (truncated if too long)
            if title and font_title:
                if len(title) > 45:
                    title = title[:42] + "..."
                bbox = draw.textbbox((0, 0), title, font=font_title)
                text_width = bbox[2] - bbox[0]
                x = max(5, (self.inky.width - text_width) // 2)
                draw.text((x, 5), title, fill=(0, 0, 0), font=font_title)
            
            # Draw artist and date at bottom
            if artist and font_info:
                info_text = f"{artist}"
                if date:
                    info_text += f" ({date})"
                    
                if len(info_text) > 60:
                    info_text = info_text[:57] + "..."
                    
                bbox = draw.textbbox((0, 0), info_text, font=font_info)
                text_width = bbox[2] - bbox[0]
                x = max(5, (self.inky.width - text_width) // 2)
                y = self.inky.height - 25
                draw.text((x, y), info_text, fill=(50, 50, 50), font=font_info)
            
            # Display timestamp
            timestamp = datetime.now().strftime("%m/%d %H:%M")
            if font_info:
                draw.text((5, self.inky.height - 15), timestamp, fill=(100, 100, 100), font=font_info)
            
            # Convert to Inky's palette and display
            self.inky.set_image(display_image)
            self.inky.show()
            
            self.current_artwork = artwork_data
            
        except Exception as e:
            print(f"Error displaying artwork: {e}")
            # Show error message on screen
            self.display_error_message("Artwork Error", str(e))
    
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
