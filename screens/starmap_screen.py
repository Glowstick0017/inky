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
from font_manager import font_manager

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
        """Create a beautiful night sky background with enhanced depth."""
        # Create deep night sky gradient with more layers
        image = Image.new("RGB", (640, 400), (2, 2, 15))
        draw = ImageDraw.Draw(image)
        
        # Create multi-layer gradient for atmospheric depth
        for y in range(400):
            ratio = y / 400
            if ratio < 0.3:
                # Upper atmosphere - deep space blue
                blend = ratio / 0.3
                r = int(2 + (8 * blend))
                g = int(2 + (15 * blend))
                b = int(15 + (35 * blend))
            elif ratio < 0.7:
                # Mid atmosphere - richer blue
                blend = (ratio - 0.3) / 0.4
                r = int(10 + (5 * blend))
                g = int(17 + (18 * blend))
                b = int(50 + (25 * blend))
            else:
                # Lower atmosphere - horizon glow
                blend = (ratio - 0.7) / 0.3
                r = int(15 + (10 * blend))
                g = int(35 + (15 * blend))
                b = int(75 + (15 * blend))
            
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Add subtle nebula clouds for depth
        self.add_nebula_clouds(draw)
        
        # Add layered stars with different brightnesses
        self.add_stellar_field(draw)
        
        # Add Milky Way band for dramatic effect
        self.add_milky_way(draw)
        
        return image
    
    def add_nebula_clouds(self, draw):
        """Add subtle nebula-like clouds for atmospheric depth."""
        import random
        random.seed(42)  # Consistent pattern
        
        # Add faint nebula regions
        for _ in range(8):
            center_x = random.randint(100, 540)
            center_y = random.randint(50, 250)
            size = random.randint(60, 120)
            
            # Create circular nebula with gradient
            for radius in range(size, 0, -5):
                alpha = int(15 * (1 - radius/size))  # Fade out
                if alpha > 0:
                    # Subtle purple/blue nebula colors
                    r = random.randint(20, 40)
                    g = random.randint(15, 35)
                    b = random.randint(50, 80)
                    
                    # Draw nebula circle
                    bbox = [center_x - radius//2, center_y - radius//2, 
                           center_x + radius//2, center_y + radius//2]
                    try:
                        draw.ellipse(bbox, fill=(r, g, b, alpha))
                    except:
                        draw.ellipse(bbox, fill=(r, g, b))
    
    def add_stellar_field(self, draw):
        """Add layered star field with varying brightnesses and sizes."""
        import random
        random.seed(42)  # Consistent pattern
        
        # Background dim stars
        for _ in range(200):
            x = random.randint(0, 640)
            y = random.randint(0, 300)  # Keep in upper sky
            brightness = random.randint(80, 150)
            draw.point((x, y), fill=(brightness, brightness, brightness))
        
        # Medium brightness stars
        for _ in range(80):
            x = random.randint(0, 640)
            y = random.randint(0, 280)
            brightness = random.randint(150, 220)
            size = random.choice([1, 2])
            
            if size == 1:
                draw.point((x, y), fill=(brightness, brightness, brightness))
            else:
                draw.ellipse([x-1, y-1, x+1, y+1], fill=(brightness, brightness, brightness))
        
        # Bright prominent stars with cross pattern
        for _ in range(25):
            x = random.randint(50, 590)
            y = random.randint(50, 250)
            brightness = random.randint(200, 255)
            # Draw star with cross pattern and glow
            draw.line([(x-3, y), (x+3, y)], fill=(brightness, brightness, brightness), width=2)
            draw.line([(x, y-3), (x, y+3)], fill=(brightness, brightness, brightness), width=2)
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(255, 255, 255))
            
        # Add some colored stars for variety
        for _ in range(15):
            x = random.randint(100, 540)
            y = random.randint(80, 220)
            color_choice = random.choice([
                (255, 200, 200),  # Red giant
                (200, 200, 255),  # Blue giant
                (255, 255, 200),  # Yellow star
            ])
            draw.ellipse([x-2, y-2, x+2, y+2], fill=color_choice)
            draw.point((x, y), fill=(255, 255, 255))
    
    def add_milky_way(self, draw):
        """Add a subtle Milky Way band across the sky."""
        import random
        random.seed(24)  # Different seed for Milky Way
        
        # Create a diagonal band across the sky
        center_y = 150
        band_width = 80
        
        for x in range(0, 640, 3):
            # Curved path for the Milky Way
            y_offset = int(20 * math.sin(x / 100))
            band_center = center_y + y_offset
            
            for y in range(max(0, band_center - band_width//2), 
                          min(300, band_center + band_width//2), 2):
                distance_from_center = abs(y - band_center)
                alpha = max(0, int(30 * (1 - distance_from_center / (band_width//2))))
                
                if alpha > 5:
                    # Add star dust effect
                    if random.random() < 0.7:
                        brightness = random.randint(40, 80)
                        draw.point((x, y), fill=(brightness + alpha, brightness + alpha, brightness + alpha//2))
    
    def draw_constellation(self, draw, constellation_name, star_coords, font):
        """Draw a constellation with connected stars, enhanced depth, and label."""
        if len(star_coords) < 2:
            return
        
        # Draw constellation connection lines with subtle glow
        for i in range(len(star_coords) - 1):
            x1, y1 = star_coords[i]
            x2, y2 = star_coords[i + 1]
            # Draw thicker background line for glow effect
            draw.line([(x1, y1), (x2, y2)], fill=(50, 80, 120), width=3)
            # Draw main constellation line
            draw.line([(x1, y1), (x2, y2)], fill=(120, 180, 240), width=1)
        
        # Draw stars with varying brightness and size
        for i, (x, y) in enumerate(star_coords):
            # Vary star brightness - make some stars more prominent
            if i == 0 or i == len(star_coords) - 1:
                # Brighter end stars
                draw.ellipse([x-3, y-3, x+3, y+3], fill=(255, 255, 180))
                draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 220))
                draw.point((x, y), fill=(255, 255, 255))
            else:
                # Regular stars
                draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 200))
                draw.point((x, y), fill=(255, 255, 255))
        
        # Draw constellation name with enhanced visibility
        if star_coords and font:
            label_x, label_y = star_coords[0]
            label_x += 15
            label_y -= 12
            # Ensure label stays on screen
            if label_x > 520:
                label_x = star_coords[0][0] - 100
            if label_y < 20:
                label_y = star_coords[0][1] + 20
                
            # Add background box for better readability
            bbox = draw.textbbox((label_x, label_y), constellation_name, font=font)
            box_padding = 2
            draw.rectangle([bbox[0]-box_padding, bbox[1]-box_padding, 
                           bbox[2]+box_padding, bbox[3]+box_padding], 
                          fill=(0, 0, 0, 150))
            
            # Shadow text
            draw.text((label_x + 1, label_y + 1), constellation_name, fill=(0, 0, 0), font=font)
            # Main text
            draw.text((label_x, label_y), constellation_name, fill=(200, 220, 255), font=font)
    
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
        
        # Draw planet as larger circle with glow effect
        # Outer glow
        draw.ellipse([x-6, y-6, x+6, y+6], fill=(color[0]//3, color[1]//3, color[2]//3))
        # Main planet body
        draw.ellipse([x-4, y-4, x+4, y+4], fill=color)
        # Highlight
        draw.ellipse([x-2, y-2, x+2, y+2], fill=(min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)))
        
        # Add planet label with shadow
        if font:
            label_x = x + 10
            label_y = y - 8
            if label_x > 580:
                label_x = x - 60
            # Shadow
            draw.text((label_x + 1, label_y + 1), planet_name, fill=(0, 0, 0), font=font)
            # Main text
            draw.text((label_x, label_y), planet_name, fill=(255, 255, 100), font=font)
    
    def draw_moon_phase(self, draw, moon_phase, x, y, size=40):
        """Draw a detailed moon phase visualization."""
        # Moon phases and their illumination percentages
        moon_phases = {
            "New Moon": 0.0,
            "Waxing Crescent": 0.25,
            "First Quarter": 0.5,
            "Waxing Gibbous": 0.75,
            "Full Moon": 1.0,
            "Waning Gibbous": 0.75,
            "Last Quarter": 0.5,
            "Waning Crescent": 0.25,
            "Unknown": 0.5  # Default to half moon
        }
        
        illumination = moon_phases.get(moon_phase, 0.5)
        is_waning = "Waning" in moon_phase or "Last" in moon_phase
        
        # Draw moon shadow/background
        draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=(40, 40, 60))
        
        # Draw the illuminated portion
        if illumination == 0.0:  # New Moon
            # Very dark moon, barely visible
            draw.ellipse([x-size//2+2, y-size//2+2, x+size//2-2, y+size//2-2], fill=(60, 60, 80))
        elif illumination == 1.0:  # Full Moon
            # Bright full moon with surface detail
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=(240, 240, 220))
            # Add surface craters
            draw.ellipse([x-8, y-6, x-4, y-2], fill=(220, 220, 200))
            draw.ellipse([x+2, y+4, x+6, y+8], fill=(220, 220, 200))
            draw.ellipse([x-3, y+8, x+1, y+12], fill=(220, 220, 200))
        else:  # Crescent or Gibbous phases
            # Draw terminator line (shadow boundary)
            if is_waning:
                # Light on the left, shadow on right
                if illumination <= 0.5:
                    # Crescent - draw illuminated slice
                    width = int(size * illumination * 2)
                    draw.ellipse([x-width//2, y-size//2, x+width//2, y+size//2], fill=(240, 240, 220))
                else:
                    # Gibbous - draw full circle minus shadow
                    draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=(240, 240, 220))
                    shadow_width = int(size * (1 - illumination) * 2)
                    draw.ellipse([x+size//2-shadow_width, y-size//2, x+size//2, y+size//2], fill=(40, 40, 60))
            else:
                # Waxing - light on the right, shadow on left
                if illumination <= 0.5:
                    # Crescent - draw illuminated slice
                    width = int(size * illumination * 2)
                    draw.ellipse([x-width//2, y-size//2, x+width//2, y+size//2], fill=(240, 240, 220))
                else:
                    # Gibbous - draw full circle minus shadow
                    draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], fill=(240, 240, 220))
                    shadow_width = int(size * (1 - illumination) * 2)
                    draw.ellipse([x-size//2, y-size//2, x-size//2+shadow_width, y+size//2], fill=(40, 40, 60))
        
        # Add moon glow
        glow_size = size + 8
        for i in range(4):
            alpha = 30 - i * 7
            if alpha > 0:
                glow_radius = size//2 + i * 2
                # Subtle glow effect
                pass  # Simplified for e-ink display
        
        # Draw outer ring
        draw.ellipse([x-size//2-1, y-size//2-1, x+size//2+1, y+size//2+1], outline=(200, 200, 180), width=1)
    
    def display(self):
        """Display the current star chart with constellations and planets."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Star Chart screen...")
        
        try:
            # Fetch current astronomy data
            star_data = self.fetch_current_astronomy_data()
            self.current_starmap = star_data
            
            # Load fonts using font manager first (before image operations)
            font_title = font_manager.get_font('title', 24)
            font_large = font_manager.get_font('regular', 16)
            font_medium = font_manager.get_font('regular', 14)
            font_small = font_manager.get_font('small', 12)
            
            # Create night sky background
            display_image = self.create_starmap_background()
            draw = ImageDraw.Draw(display_image)
            
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
            
            # Draw visible planets with enhanced appearance
            planet_positions = [
                (480, 120), (520, 180), (150, 200), (350, 120), (580, 150)
            ]
            
            for i, planet in enumerate(star_data.get("visible_planets", [])[:5]):
                if i < len(planet_positions):
                    x, y = planet_positions[i]
                    self.draw_planet(draw, planet, x, y, font_small)
            
            # Draw moon phase in lower right corner
            moon_phase = star_data.get("moon_phase", "Unknown")
            moon_x, moon_y = 580, 320
            self.draw_moon_phase(draw, moon_phase, moon_x, moon_y, 45)
            
            # Add moon phase label
            if font_small:
                phase_label = moon_phase.replace(" ", "\n") if len(moon_phase) > 8 else moon_phase
                lines = phase_label.split('\n')
                for i, line in enumerate(lines):
                    label_y = moon_y + 35 + (i * 12)
                    bbox = draw.textbbox((0, 0), line, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    label_x = moon_x - text_width // 2
                    # Shadow
                    draw.text((label_x + 1, label_y + 1), line, fill=(0, 0, 0), font=font_small)
                    # Main text
                    draw.text((label_x, label_y), line, fill=(200, 200, 255), font=font_small)
            
            # Enhanced information panel at bottom
            info_y = 340
            info_bg = Image.new("RGBA", (520, 60), (0, 0, 0, 180))  # Shorter to make room for moon
            display_image.paste(info_bg, (0, info_y), info_bg)
            
            # Moon info (reduced since visual moon is shown)
            if font_medium:
                moon_text = f"Moon Phase: {star_data.get('moon_phase', 'Unknown')}"
                draw.text((16, info_y + 6), moon_text, fill=(0, 0, 0), font=font_medium)
                draw.text((15, info_y + 5), moon_text, fill=(255, 255, 200), font=font_medium)
            
            if font_small:
                # Sunrise/sunset info
                sunrise = star_data.get("sunrise", "N/A")
                sunset = star_data.get("sunset", "N/A")
                sun_info = f"Sunrise: {sunrise} | Sunset: {sunset}"
                draw.text((16, info_y + 26), sun_info, fill=(0, 0, 0), font=font_small)
                draw.text((15, info_y + 25), sun_info, fill=(255, 200, 100), font=font_small)
                
                # Location info
                location_text = f"Location: {self.city_name}"
                draw.text((16, info_y + 41), location_text, fill=(0, 0, 0), font=font_small)
                draw.text((15, info_y + 40), location_text, fill=(150, 255, 150), font=font_small)
            
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
            font_title = font_manager.get_font('title', 20)
            font_text = font_manager.get_font('regular', 16)
        except:
            font_title = font_text = font_manager.get_font('regular', 16)
            
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
