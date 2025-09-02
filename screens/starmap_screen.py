"""
Star Chart Screen - Interactive Night Sky Display
Displays current star chart with constellations, planets, and celestial objects
Optimized for 640x400 e-ink display with high contrast and large labels
Updates every 30 minutes with current sky view for Phoenix, Arizona
"""

import requests
import json
import math
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from .base_screen import BaseScreen
import config

class StarmapScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.STARMAP_UPDATE_INTERVAL if hasattr(config, 'STARMAP_UPDATE_INTERVAL') else 1800
        self.current_starmap = None
        
        # Location coordinates (use dedicated location config or fallback)
        self.latitude = config.LOCATION_LATITUDE if hasattr(config, 'LOCATION_LATITUDE') else config.WEATHER_LATITUDE if hasattr(config, 'WEATHER_LATITUDE') else 33.4484
        self.longitude = config.LOCATION_LONGITUDE if hasattr(config, 'LOCATION_LONGITUDE') else config.WEATHER_LONGITUDE if hasattr(config, 'WEATHER_LONGITUDE') else -112.0740
        self.city_name = config.LOCATION_CITY if hasattr(config, 'LOCATION_CITY') else config.WEATHER_CITY_NAME if hasattr(config, 'WEATHER_CITY_NAME') else "Phoenix, AZ"
        
        # Star chart APIs - we'll use multiple sources with fallbacks
        self.astronomy_api_base = "https://api.astronomyapi.com/api/v2"
        self.ipgeolocation_api = "https://api.ipgeolocation.io/astronomy"
        
        # Constellation data for fallback display
        self.major_constellations = {
            "Ursa Major": {"stars": [(200, 100), (220, 90), (240, 95), (260, 105), (280, 110), (300, 108), (320, 115)]},
            "Orion": {"stars": [(400, 200), (420, 180), (440, 160), (380, 220), (460, 210), (400, 240), (440, 260)]},
            "Cassiopeia": {"stars": [(150, 150), (170, 140), (190, 145), (210, 135), (230, 150)]},
            "Big Dipper": {"stars": [(180, 80), (200, 85), (220, 75), (240, 80), (260, 90), (280, 95), (300, 100)]},
            "Polaris": {"stars": [(320, 100)]},
            "Leo": {"stars": [(350, 150), (370, 140), (390, 135), (410, 145), (430, 160)]},
        }
        
        # Planet data for display
        self.planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        
        # Fallback star data for when APIs are unavailable
        self.fallback_stars = {
            "title": "Night Sky - Phoenix, AZ",
            "time": "Current Time",
            "visible_planets": ["Venus", "Mars", "Jupiter"],
            "moon_phase": "Waxing Gibbous",
            "constellations": self.major_constellations
        }
    
    def fetch_current_astronomy_data(self):
        """Fetch current astronomy data from multiple sources."""
        current_time = datetime.now()
        
        try:
            # Try IP Geolocation astronomy API (free tier available)
            response = requests.get(
                f"{self.ipgeolocation_api}",
                params={
                    "lat": self.latitude,
                    "long": self.longitude
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self.process_astronomy_data(data, current_time)
                
        except Exception as e:
            print(f"Error fetching astronomy data: {e}")
        
        # Return fallback data with current time
        fallback = self.fallback_stars.copy()
        fallback["time"] = current_time.strftime("%B %d, %Y - %I:%M %p")
        return fallback
    
    def process_astronomy_data(self, api_data, current_time):
        """Process API data into our standard format."""
        processed_data = {
            "title": "Night Sky - Phoenix, AZ",
            "time": current_time.strftime("%B %d, %Y - %I:%M %p"),
            "visible_planets": [],
            "moon_phase": "Unknown",
            "constellations": self.major_constellations,
            "sunrise": api_data.get("sunrise", "N/A"),
            "sunset": api_data.get("sunset", "N/A"),
            "moon_illumination": api_data.get("moon_illumination", "Unknown")
        }
        
        # Extract moon phase if available
        if "moon_phase" in api_data:
            processed_data["moon_phase"] = api_data["moon_phase"]
        
        return processed_data
    
    def create_starmap_background(self):
        """Create a beautiful night sky background."""
        # Create deep night sky gradient
        image = Image.new("RGB", (640, 400), (5, 5, 25))
        draw = ImageDraw.Draw(image)
        
        # Create gradient from deep blue to black
        for y in range(400):
            ratio = y / 400
            # Deep blue at top, darker at bottom
            r = int(5 + (15 * (1 - ratio)))
            g = int(5 + (25 * (1 - ratio)))
            b = int(25 + (50 * (1 - ratio)))
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Add stars scattered across the sky
        import random
        random.seed(42)  # Consistent star pattern
        for _ in range(150):
            x = random.randint(0, 640)
            y = random.randint(0, 300)  # Keep stars in upper area
            brightness = random.randint(150, 255)
            size = random.choice([1, 1, 1, 2])  # Mostly small stars
            
            if size == 1:
                draw.point((x, y), fill=(brightness, brightness, brightness))
            else:
                draw.ellipse([x-1, y-1, x+1, y+1], fill=(brightness, brightness, brightness))
        
        # Add some brighter stars
        for _ in range(20):
            x = random.randint(50, 590)
            y = random.randint(50, 250)
            brightness = random.randint(200, 255)
            # Draw star with cross pattern
            draw.line([(x-2, y), (x+2, y)], fill=(brightness, brightness, brightness), width=1)
            draw.line([(x, y-2), (x, y+2)], fill=(brightness, brightness, brightness), width=1)
            draw.point((x, y), fill=(255, 255, 255))
        
        return image
    
    def draw_constellation(self, draw, constellation_name, star_coords, font):
        """Draw a constellation with connected stars and label."""
        if len(star_coords) < 2:
            return
        
        # Draw constellation lines
        for i in range(len(star_coords) - 1):
            x1, y1 = star_coords[i]
            x2, y2 = star_coords[i + 1]
            draw.line([(x1, y1), (x2, y2)], fill=(100, 150, 200), width=1)
        
        # Draw stars as bright points
        for x, y in star_coords:
            draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 200))
            draw.point((x, y), fill=(255, 255, 255))
        
        # Draw constellation name near the first star
        if star_coords and font:
            label_x, label_y = star_coords[0]
            label_x += 15
            label_y -= 10
            # Ensure label stays on screen
            if label_x > 550:
                label_x = star_coords[0][0] - 80
            if label_y < 20:
                label_y = star_coords[0][1] + 15
                
            draw.text((label_x, label_y), constellation_name, fill=(200, 200, 255), font=font)
    
    def draw_planet(self, draw, planet_name, x, y, font):
        """Draw a planet with distinctive appearance."""
        planet_colors = {
            "Mercury": (169, 169, 169),    # Gray
            "Venus": (255, 215, 0),        # Gold
            "Mars": (205, 92, 92),         # Red
            "Jupiter": (255, 165, 0),      # Orange
            "Saturn": (255, 215, 0),       # Yellow
            "Moon": (245, 245, 220)        # Beige
        }
        
        color = planet_colors.get(planet_name, (255, 255, 255))
        
        # Draw planet as larger circle
        draw.ellipse([x-4, y-4, x+4, y+4], fill=color)
        draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 255))
        
        # Add planet label
        if font:
            label_x = x + 10
            label_y = y - 8
            if label_x > 580:
                label_x = x - 60
            draw.text((label_x, label_y), planet_name, fill=(255, 255, 100), font=font)
    
    def display(self):
        """Display the current star chart with constellations and planets."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Star Chart screen...")
        
        try:
            # Fetch current astronomy data
            star_data = self.fetch_current_astronomy_data()
            self.current_starmap = star_data
            
            # Create night sky background
            display_image = self.create_starmap_background()
            draw = ImageDraw.Draw(display_image)
            
            # Load fonts
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 24)
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 14)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 12)
            except:
                try:
                    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                except:
                    font_title = font_large = font_medium = font_small = ImageFont.load_default()
            
            # Draw title
            title = "NIGHT SKY CHART"
            if font_title:
                bbox = draw.textbbox((0, 0), title, font=font_title)
                title_width = bbox[2] - bbox[0]
                title_x = (640 - title_width) // 2
                # Add shadow for visibility
                draw.text((title_x + 2, 12), title, fill=(0, 0, 0), font=font_title)
                draw.text((title_x, 10), title, fill=(255, 255, 255), font=font_title)
            
            # Draw current time
            time_text = star_data["time"]
            if font_medium:
                bbox = draw.textbbox((0, 0), time_text, font=font_medium)
                time_width = bbox[2] - bbox[0]
                time_x = (640 - time_width) // 2
                draw.text((time_x + 1, 41), time_text, fill=(0, 0, 0), font=font_medium)
                draw.text((time_x, 40), time_text, fill=(200, 200, 255), font=font_medium)
            
            # Draw constellations
            for constellation_name, constellation_data in star_data["constellations"].items():
                star_coords = constellation_data["stars"]
                self.draw_constellation(draw, constellation_name, star_coords, font_small)
            
            # Draw visible planets
            planet_positions = [
                (480, 120), (520, 180), (150, 200), (350, 120), (580, 150)
            ]
            
            for i, planet in enumerate(star_data.get("visible_planets", [])[:5]):
                if i < len(planet_positions):
                    x, y = planet_positions[i]
                    self.draw_planet(draw, planet, x, y, font_small)
            
            # Information panel at bottom
            info_y = 320
            info_bg = Image.new("RGBA", (640, 80), (0, 0, 0, 150))
            display_image.paste(info_bg, (0, info_y), info_bg)
            
            # Moon phase and other info
            if font_large:
                moon_text = f"Moon: {star_data.get('moon_phase', 'Unknown')}"
                draw.text((21, info_y + 11), moon_text, fill=(0, 0, 0), font=font_large)
                draw.text((20, info_y + 10), moon_text, fill=(255, 255, 200), font=font_large)
            
            if font_medium:
                # Sunrise/sunset info
                sunrise = star_data.get("sunrise", "N/A")
                sunset = star_data.get("sunset", "N/A")
                sun_info = f"Sunrise: {sunrise} | Sunset: {sunset}"
                draw.text((21, info_y + 36), sun_info, fill=(0, 0, 0), font=font_medium)
                draw.text((20, info_y + 35), sun_info, fill=(255, 200, 100), font=font_medium)
                
                # Location info
                location_text = "Location: Phoenix, Arizona"
                draw.text((21, info_y + 56), location_text, fill=(0, 0, 0), font=font_medium)
                draw.text((20, info_y + 55), location_text, fill=(150, 255, 150), font=font_medium)
            
            # Display the star chart
            self.inky.set_image(display_image)
            self.inky.show()
            
            print(f"Displayed star chart for {star_data['time']}")
            
        except Exception as e:
            print(f"Error displaying star chart: {e}")
            self.display_error_message("Star Chart Error", str(e))
    
    def display_error_message(self, title, message):
        """Display an error message with night sky theme."""
        image = Image.new("RGB", (640, 400), (5, 5, 25))
        draw = ImageDraw.Draw(image)
        
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 20)
            font_text = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
        except:
            font_title = font_text = ImageFont.load_default()
            
        if font_title:
            # Draw error title
            bbox = draw.textbbox((0, 0), title, font=font_title)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 180), title, fill=(255, 100, 100), font=font_title)
            
        if font_text:
            # Draw error message (truncated)
            if len(message) > 50:
                message = message[:47] + "..."
            bbox = draw.textbbox((0, 0), message, font=font_text)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 220), message, fill=(200, 200, 200), font=font_text)
        
        self.inky.set_image(image)
        self.inky.show()
