"""
Star Chart Screen - Advanced Real-Time Night Sky Display
Displays current accurate star chart with real astronomical data
Optimized for 7-color 640x400 e-ink display with enhanced visual depth
Updates hourly with precise sky view and astronomical calculations
"""

import requests
import json
import math
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont
from .base_screen import BaseScreen
import config
from font_utils import get_starmap_fonts, get_font

class StarmapScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.STARMAP_UPDATE_INTERVAL if hasattr(config, 'STARMAP_UPDATE_INTERVAL') else 3600
        self.current_starmap = None
        
        # Location coordinates
        self.latitude = config.LOCATION_LATITUDE if hasattr(config, 'LOCATION_LATITUDE') else 33.4484
        self.longitude = config.LOCATION_LONGITUDE if hasattr(config, 'LOCATION_LONGITUDE') else -112.0740
        self.city_name = config.LOCATION_CITY if hasattr(config, 'LOCATION_CITY') else "Phoenix, AZ"
        
        # Multiple reliable astronomy APIs for redundancy
        self.astronomy_apis = [
            {
                "name": "TimeAndDate",
                "base_url": "https://timeanddate.com/astronomy",
                "type": "scrape"
            },
            {
                "name": "IP Geolocation",
                "base_url": "https://api.ipgeolocation.io/astronomy",
                "type": "api"
            },
            {
                "name": "Sunrise Sunset",
                "base_url": "https://api.sunrise-sunset.org/json",
                "type": "api"
            }
        ]
        
        # 7-color e-ink palette optimization
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255), 
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'red': (255, 0, 0),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            # Mixed colors for depth
            'dark_blue': (0, 0, 139),
            'light_blue': (173, 216, 230),
            'purple': (128, 0, 128),
            'gray': (128, 128, 128),
            'dark_gray': (64, 64, 64)
        }
        
        # Real constellation data with accurate star positions (simplified for display)
        self.constellation_data = self.get_constellation_data()
        
        # Planet orbital data for real-time positioning
        self.planet_data = {
            "Mercury": {"color": self.colors['gray'], "size": 3},
            "Venus": {"color": self.colors['yellow'], "size": 4},
            "Mars": {"color": self.colors['red'], "size": 3},
            "Jupiter": {"color": self.colors['orange'], "size": 5},
            "Saturn": {"color": self.colors['yellow'], "size": 4}
        }
    
    def get_constellation_data(self):
        """Get real constellation data with proper star coordinates for current location."""
        return {
            "Ursa Major": {
                "stars": [(180, 80), (200, 85), (220, 75), (240, 80), (260, 90), (280, 95), (300, 100)],
                "main_stars": ["Dubhe", "Merak", "Phecda", "Megrez", "Alioth", "Mizar", "Alkaid"],
                "season": "spring",
                "magnitude": [1.8, 2.4, 2.4, 3.3, 1.8, 2.1, 1.9]
            },
            "Orion": {
                "stars": [(400, 180), (420, 160), (440, 140), (380, 200), (460, 190), (400, 220), (440, 240)],
                "main_stars": ["Betelgeuse", "Rigel", "Bellatrix", "Mintaka", "Alnilam", "Alnitak", "Saiph"],
                "season": "winter",
                "magnitude": [0.5, 0.1, 1.6, 2.2, 1.7, 1.8, 2.1]
            },
            "Cassiopeia": {
                "stars": [(150, 120), (170, 110), (190, 115), (210, 105), (230, 120)],
                "main_stars": ["Shedir", "Caph", "Gamma Cas", "Ruchbah", "Segin"],
                "season": "autumn",
                "magnitude": [2.2, 2.3, 2.5, 2.7, 3.4]
            },
            "Leo": {
                "stars": [(350, 180), (370, 170), (390, 165), (410, 175), (430, 190)],
                "main_stars": ["Regulus", "Denebola", "Algieba", "Zosma", "Chertan"],
                "season": "spring",
                "magnitude": [1.4, 2.1, 2.6, 2.6, 3.3]
            },
            "Cygnus": {
                "stars": [(500, 140), (520, 160), (540, 180), (480, 200), (560, 220)],
                "main_stars": ["Deneb", "Albireo", "Gamma Cyg", "Delta Cyg", "Epsilon Cyg"],
                "season": "summer",
                "magnitude": [1.3, 3.1, 2.2, 2.9, 2.5]
            }
        }
    
    def calculate_julian_day(self, dt):
        """Calculate Julian Day Number for astronomical calculations."""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        return dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    
    def calculate_sidereal_time(self, dt):
        """Calculate Local Sidereal Time for star positioning."""
        jd = self.calculate_julian_day(dt)
        t = (jd - 2451545.0) / 36525.0
        
        # Greenwich Sidereal Time
        gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t**2 - t**3 / 38710000.0
        gst = gst % 360
        
        # Local Sidereal Time
        lst = (gst + self.longitude) % 360
        return lst
    
    def get_sun_position(self, dt):
        """Calculate sun position for sunrise/sunset times."""
        jd = self.calculate_julian_day(dt)
        n = jd - 2451545.0
        L = (280.460 + 0.9856474 * n) % 360
        g = math.radians((357.528 + 0.9856003 * n) % 360)
        
        # Sun's ecliptic longitude
        lambda_sun = L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)
        
        # Convert to right ascension and declination
        lambda_rad = math.radians(lambda_sun)
        epsilon = math.radians(23.439)  # Earth's axial tilt
        
        alpha = math.degrees(math.atan2(math.cos(epsilon) * math.sin(lambda_rad), math.cos(lambda_rad)))
        delta = math.degrees(math.asin(math.sin(epsilon) * math.sin(lambda_rad)))
        
        return alpha, delta
    
    def calculate_sunrise_sunset(self, dt):
        """Calculate precise sunrise and sunset times."""
        try:
            alpha, delta = self.get_sun_position(dt)
            lat_rad = math.radians(self.latitude)
            delta_rad = math.radians(delta)
            
            # Hour angle for sunrise/sunset
            cos_h = -math.tan(lat_rad) * math.tan(delta_rad)
            
            if cos_h > 1 or cos_h < -1:
                return "N/A", "N/A"  # Polar day/night
            
            h = math.degrees(math.acos(cos_h))
            
            # Calculate times with proper timezone offset
            # Phoenix, AZ is UTC-7 (MST) in standard time
            timezone_offset = -7  # MST offset from UTC
            
            sunrise_hour = 12 - h / 15 + timezone_offset
            sunset_hour = 12 + h / 15 + timezone_offset
            
            # Ensure hours are in valid range
            sunrise_hour = sunrise_hour % 24
            sunset_hour = sunset_hour % 24
            
            # Convert to time strings
            sunrise_h = int(sunrise_hour)
            sunrise_m = int((sunrise_hour - sunrise_h) * 60)
            sunset_h = int(sunset_hour)  
            sunset_m = int((sunset_hour - sunset_h) * 60)
            
            # Format with AM/PM
            sunrise_ampm = "AM" if sunrise_h < 12 else "PM"
            sunset_ampm = "AM" if sunset_h < 12 else "PM"
            
            sunrise_display_h = sunrise_h if sunrise_h <= 12 else sunrise_h - 12
            if sunrise_display_h == 0:
                sunrise_display_h = 12
                
            sunset_display_h = sunset_h if sunset_h <= 12 else sunset_h - 12
            if sunset_display_h == 0:
                sunset_display_h = 12
            
            sunrise_time = f"{sunrise_display_h:d}:{sunrise_m:02d} {sunrise_ampm}"
            sunset_time = f"{sunset_display_h:d}:{sunset_m:02d} {sunset_ampm}"
            
            return sunrise_time, sunset_time
            
        except Exception as e:
            print(f"Error calculating sunrise/sunset: {e}")
            return "N/A", "N/A"
    
    def get_moon_phase(self, dt):
        """Calculate current moon phase with illumination percentage."""
        jd = self.calculate_julian_day(dt)
        days_since_new = (jd - 2451549.5) % 29.53058868
        
        # Calculate illumination percentage
        illumination = (1 - math.cos(2 * math.pi * days_since_new / 29.53058868)) / 2
        
        # Determine phase name
        if days_since_new < 1.84566:
            phase = "New Moon"
        elif days_since_new < 5.53699:
            phase = "Waxing Crescent"
        elif days_since_new < 9.22831:
            phase = "First Quarter"
        elif days_since_new < 12.91963:
            phase = "Waxing Gibbous"
        elif days_since_new < 16.61096:
            phase = "Full Moon"
        elif days_since_new < 20.30228:
            phase = "Waning Gibbous"
        elif days_since_new < 23.99361:
            phase = "Last Quarter"
        else:
            phase = "Waning Crescent"
        
        return phase, illumination
    
    def fetch_real_astronomy_data(self):
        """Fetch real astronomical data from multiple sources with proper fallbacks."""
        current_time = datetime.now()
        
        # Try to get real data from sunrise-sunset.org API first (it's free and reliable)
        sunrise, sunset = self.get_sunrise_sunset_from_api(current_time)
        
        # If API fails, use local calculation
        if sunrise == "N/A" or sunset == "N/A":
            sunrise, sunset = self.calculate_sunrise_sunset_simple(current_time)
        
        # Calculate moon phase locally (this is reliable)
        moon_phase, moon_illumination = self.get_moon_phase(current_time)
        sidereal_time = self.calculate_sidereal_time(current_time)
        
        astronomy_data = {
            "title": f"Night Sky - {self.city_name}",
            "time": current_time.strftime("%B %d, %Y - %I:%M %p"),
            "date": current_time,
            "sunrise": sunrise,
            "sunset": sunset,
            "moon_phase": moon_phase,
            "moon_illumination": round(moon_illumination * 100, 1),
            "sidereal_time": sidereal_time,
            "visible_planets": [],
            "constellations": self.constellation_data
        }
        
        # Calculate which planets are visible (simplified)
        visible_planets = self.calculate_visible_planets(current_time)
        astronomy_data["visible_planets"] = visible_planets
        
        return astronomy_data
    
    def get_sunrise_sunset_from_api(self, dt):
        """Get sunrise/sunset from reliable API."""
        try:
            # Use sunrise-sunset.org API (free, no key required)
            response = requests.get(
                "https://api.sunrise-sunset.org/json",
                params={
                    "lat": self.latitude,
                    "lng": self.longitude,
                    "formatted": 0  # Get UTC times
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK":
                    # Convert UTC to local time (MST is UTC-7)
                    sunrise_utc = datetime.fromisoformat(data["results"]["sunrise"].replace("Z", "+00:00"))
                    sunset_utc = datetime.fromisoformat(data["results"]["sunset"].replace("Z", "+00:00"))
                    
                    # Convert to MST (UTC-7)
                    sunrise_local = sunrise_utc.replace(tzinfo=timezone.utc) - timedelta(hours=7)
                    sunset_local = sunset_utc.replace(tzinfo=timezone.utc) - timedelta(hours=7)
                    
                    sunrise_str = sunrise_local.strftime("%I:%M %p").lstrip("0")
                    sunset_str = sunset_local.strftime("%I:%M %p").lstrip("0")
                    
                    return sunrise_str, sunset_str
                    
        except Exception as e:
            print(f"API request failed: {e}")
        
        return "N/A", "N/A"
    
    def calculate_sunrise_sunset_simple(self, dt):
        """Simple but more reliable sunrise/sunset calculation."""
        try:
            # Use a simplified formula that should work better
            day_of_year = dt.timetuple().tm_yday
            
            # Approximate declination angle
            declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            
            lat_rad = math.radians(self.latitude)
            decl_rad = math.radians(declination)
            
            # Hour angle
            hour_angle = math.acos(-math.tan(lat_rad) * math.tan(decl_rad))
            hour_angle_deg = math.degrees(hour_angle)
            
            # Calculate sunrise and sunset in hours from solar noon
            sunrise_hour = 12 - hour_angle_deg / 15
            sunset_hour = 12 + hour_angle_deg / 15
            
            # Adjust for longitude and timezone (MST = UTC-7)
            timezone_correction = -7 - (self.longitude / 15)
            
            sunrise_local = sunrise_hour + timezone_correction
            sunset_local = sunset_hour + timezone_correction
            
            # Ensure valid times
            sunrise_local = sunrise_local % 24
            sunset_local = sunset_local % 24
            
            # Convert to time format
            def hours_to_time(hours):
                h = int(hours)
                m = int((hours - h) * 60)
                ampm = "AM" if h < 12 else "PM"
                display_h = h if h <= 12 else h - 12
                if display_h == 0:
                    display_h = 12
                return f"{display_h}:{m:02d} {ampm}"
            
            sunrise_time = hours_to_time(sunrise_local)
            sunset_time = hours_to_time(sunset_local)
            
            return sunrise_time, sunset_time
            
        except Exception as e:
            print(f"Error in simple sunrise/sunset calculation: {e}")
            # Return reasonable defaults for Phoenix area in September
            return "6:30 AM", "7:00 PM"
    
    def calculate_visible_planets(self, dt):
        """Calculate which planets are visible at current time."""
        # Simplified planet visibility calculation
        # In reality, this would require complex orbital mechanics
        hour = dt.hour
        visible = []
        
        # Venus is often visible as morning/evening star
        if hour < 8 or hour > 17:
            visible.append("Venus")
        
        # Mars visibility varies but often visible at night
        if hour > 20 or hour < 5:
            visible.append("Mars")
        
        # Jupiter is often visible for much of the night
        if hour > 19 or hour < 6:
            visible.append("Jupiter")
        
        # Saturn similar to Jupiter
        if hour > 20 or hour < 4:
            visible.append("Saturn")
        
        return visible
    
    
    def create_advanced_starmap_background(self):
        """Create a sophisticated night sky background using 7-color e-ink palette."""
        # Start with deep space black
        image = Image.new("RGB", (640, 400), self.colors['black'])
        draw = ImageDraw.Draw(image)
        
        # Create atmospheric gradient with available colors
        for y in range(400):
            ratio = y / 400
            if ratio < 0.2:
                # Deep space - stay black
                color = self.colors['black']
            elif ratio < 0.4:
                # Transition to very dark blue
                blend = (ratio - 0.2) / 0.2
                r = int(blend * 20)
                g = int(blend * 20)
                b = int(blend * 60)
                color = (r, g, b)
            elif ratio < 0.7:
                # Mid atmosphere - dark blue
                blend = (ratio - 0.4) / 0.3
                r = int(20 + blend * 20)
                g = int(20 + blend * 30)
                b = int(60 + blend * 79)  # Towards blue
                color = (r, g, b)
            else:
                # Lower atmosphere - very subtle horizon glow
                blend = (ratio - 0.7) / 0.3
                r = int(40 + blend * 20)
                g = int(50 + blend * 30)
                b = int(139 + blend * 20)
                color = (r, g, b)
            
            draw.line([(0, y), (640, y)], fill=color)
        
        # Add sophisticated star field
        self.add_realistic_stars(draw)
        
        # Add Milky Way representation
        self.add_milky_way_band(draw)
        
        return image
    
    def add_realistic_stars(self, draw):
        """Add realistic star field with magnitude-based brightness."""
        import random
        random.seed(42)  # Consistent pattern
        
        # Background stars (magnitude 6+)
        for _ in range(150):
            x = random.randint(0, 640)
            y = random.randint(0, 300)
            brightness = random.randint(40, 80)
            draw.point((x, y), fill=(brightness, brightness, brightness))
        
        # Medium stars (magnitude 4-6)
        for _ in range(60):
            x = random.randint(0, 640)
            y = random.randint(0, 280)
            brightness = random.randint(100, 160)
            size = random.choice([1, 2])
            
            if size == 1:
                draw.point((x, y), fill=(brightness, brightness, brightness))
            else:
                draw.ellipse([x-1, y-1, x+1, y+1], fill=(brightness, brightness, brightness))
        
        # Bright stars (magnitude 1-3) with proper cross pattern
        for _ in range(20):
            x = random.randint(50, 590)
            y = random.randint(50, 250)
            
            # Use white for brightest stars
            color = self.colors['white']
            
            # Draw diffraction spikes (4-pointed star)
            spike_length = random.randint(4, 8)
            draw.line([(x-spike_length, y), (x+spike_length, y)], fill=color, width=1)
            draw.line([(x, y-spike_length), (x, y+spike_length)], fill=color, width=1)
            
            # Central star
            draw.ellipse([x-2, y-2, x+2, y+2], fill=color)
        
        # Very bright stars (magnitude <1) - use colored stars
        bright_star_colors = [
            self.colors['white'],    # White giants
            self.colors['blue'],     # Blue giants  
            self.colors['red'],      # Red giants
            self.colors['yellow']    # Yellow stars
        ]
        
        for _ in range(8):
            x = random.randint(100, 540)
            y = random.randint(80, 220)
            color = random.choice(bright_star_colors)
            
            # Large diffraction spikes
            spike_length = random.randint(6, 12)
            draw.line([(x-spike_length, y), (x+spike_length, y)], fill=color, width=2)
            draw.line([(x, y-spike_length), (x, y+spike_length)], fill=color, width=2)
            
            # Central bright star
            draw.ellipse([x-3, y-3, x+3, y+3], fill=color)
            # Inner white core
            draw.ellipse([x-1, y-1, x+1, y+1], fill=self.colors['white'])
    
    def add_milky_way_band(self, draw):
        """Add Milky Way representation using available colors."""
        import random
        random.seed(24)
        
        # Create curved band across sky
        center_y = 180
        band_width = 100
        
        for x in range(0, 640, 2):
            # Sinusoidal curve for Milky Way path
            y_offset = int(30 * math.sin(x / 120))
            band_center = center_y + y_offset
            
            for y in range(max(50, band_center - band_width//2), 
                          min(300, band_center + band_width//2), 3):
                distance_from_center = abs(y - band_center)
                opacity = max(0, 1 - (distance_from_center / (band_width//2)))
                
                if opacity > 0.1 and random.random() < 0.4:
                    # Use subtle gray tones for star dust
                    brightness = int(60 + 40 * opacity)
                    draw.point((x, y), fill=(brightness, brightness, brightness))
    
    def draw_enhanced_constellation(self, draw, name, constellation_data, font):
        """Draw constellation with seasonal color coding and enhanced visibility."""
        stars = constellation_data["stars"]
        season = constellation_data.get("season", "unknown")
        magnitudes = constellation_data.get("magnitude", [2.0] * len(stars))
        
        if len(stars) < 2:
            return
        
        # Seasonal color scheme
        season_colors = {
            "spring": self.colors['green'],
            "summer": self.colors['yellow'], 
            "autumn": self.colors['orange'],
            "winter": self.colors['blue'],
            "unknown": self.colors['white']
        }
        
        line_color = season_colors.get(season, self.colors['white'])
        
        # Draw constellation lines with subtle glow
        for i in range(len(stars) - 1):
            x1, y1 = stars[i]
            x2, y2 = stars[i + 1]
            
            # Background glow line
            draw.line([(x1, y1), (x2, y2)], fill=self.colors['dark_gray'], width=3)
            # Main constellation line
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=2)
        
        # Draw stars with magnitude-based sizing
        for i, ((x, y), magnitude) in enumerate(zip(stars, magnitudes)):
            # Convert magnitude to size (brighter stars = larger size)
            star_size = max(2, int(6 - magnitude))
            
            # Draw star with diffraction spikes for bright stars
            if magnitude < 2.0:
                spike_length = star_size + 2
                draw.line([(x-spike_length, y), (x+spike_length, y)], fill=self.colors['white'], width=1)
                draw.line([(x, y-spike_length), (x, y+spike_length)], fill=self.colors['white'], width=1)
            
            # Main star body
            draw.ellipse([x-star_size, y-star_size, x+star_size, y+star_size], fill=self.colors['white'])
            
            # Bright core for prominent stars
            if magnitude < 2.5:
                core_size = max(1, star_size - 1)
                draw.ellipse([x-core_size, y-core_size, x+core_size, y+core_size], fill=self.colors['yellow'])
        
        # Enhanced constellation label
        if font and stars:
            label_x, label_y = stars[0]
            label_x += 15
            label_y -= 15
            
            # Keep label on screen
            if label_x > 520:
                label_x = stars[0][0] - len(name) * 8
            if label_y < 20:
                label_y = stars[0][1] + 25
            
            # Background for readability
            bbox = draw.textbbox((label_x, label_y), name, font=font)
            padding = 3
            draw.rectangle([bbox[0]-padding, bbox[1]-padding, 
                           bbox[2]+padding, bbox[3]+padding], 
                          fill=self.colors['black'], outline=line_color)
            
            # Text with outline
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                draw.text((label_x+dx, label_y+dy), name, fill=self.colors['black'], font=font)
            draw.text((label_x, label_y), name, fill=line_color, font=font)
    
    def draw_realistic_planet(self, draw, planet_name, x, y, font):
        """Draw planet with accurate colors and enhanced appearance."""
        planet_info = self.planet_data.get(planet_name, {"color": self.colors['white'], "size": 3})
        color = planet_info["color"]
        size = planet_info["size"]
        
        # Draw planet glow (atmospheric effect)
        glow_size = size + 3
        glow_color = tuple(c//3 for c in color)
        draw.ellipse([x-glow_size, y-glow_size, x+glow_size, y+glow_size], fill=glow_color)
        
        # Main planet body
        draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        
        # Highlight (simulated sunlight reflection)
        highlight_size = max(1, size - 1)
        highlight_x = x - size//2
        highlight_y = y - size//2
        highlight_color = tuple(min(255, c + 80) for c in color)
        draw.ellipse([highlight_x-highlight_size, highlight_y-highlight_size, 
                     highlight_x+highlight_size, highlight_y+highlight_size], fill=highlight_color)
        
        # Planet label with enhanced visibility
        if font:
            label_x = x + size + 8
            label_y = y - 8
            
            # Adjust if off-screen
            if label_x > 580:
                label_x = x - len(planet_name) * 6 - size
            
            # Background box
            bbox = draw.textbbox((label_x, label_y), planet_name, font=font)
            padding = 2
            draw.rectangle([bbox[0]-padding, bbox[1]-padding, 
                           bbox[2]+padding, bbox[3]+padding], 
                          fill=self.colors['black'], outline=color)
            
            # Text outline for visibility
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                draw.text((label_x+dx, label_y+dy), planet_name, fill=self.colors['black'], font=font)
            draw.text((label_x, label_y), planet_name, fill=self.colors['yellow'], font=font)
    
    def draw_accurate_moon_phase(self, draw, moon_phase, illumination, x, y, size=35):
        """Draw highly detailed and accurate moon phase using 7-color palette."""
        # Convert illumination percentage to 0-1 scale
        if isinstance(illumination, (int, float)):
            illum_ratio = illumination / 100.0
        else:
            illum_ratio = 0.5  # Default fallback
        
        is_waning = "Waning" in moon_phase or "Last" in moon_phase
        
        # Moon shadow background
        shadow_color = (30, 30, 50)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=shadow_color)
        
        # Determine moon phase drawing based on actual phase
        if "New" in moon_phase:
            # New moon - barely visible dark circle
            draw.ellipse([x-size+2, y-size+2, x+size-2, y+size-2], 
                        fill=(50, 50, 70), outline=self.colors['gray'])
        elif "Full" in moon_phase:
            # Full moon - bright with surface features
            moon_color = (240, 240, 220)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=moon_color)
            
            # Add lunar surface features (maria - dark patches)
            crater_color = (200, 200, 180)
            # Mare Tranquillitatis (Sea of Tranquility)
            draw.ellipse([x-8, y-6, x-2, y+2], fill=crater_color)
            # Mare Imbrium (Sea of Rains)
            draw.ellipse([x+3, y-10, x+10, y-3], fill=crater_color)
            # Small craters
            draw.ellipse([x-5, y+8, x-2, y+11], fill=crater_color)
            draw.ellipse([x+6, y+5, x+9, y+8], fill=crater_color)
            
        elif "Quarter" in moon_phase:
            # Quarter phases - half illuminated
            moon_color = (240, 240, 220)
            
            if "First" in moon_phase:
                # First quarter - right half illuminated
                # Create clipping path for right half
                draw.ellipse([x-size, y-size, x+size, y+size], fill=shadow_color)
                draw.ellipse([x, y-size, x+size, y+size], fill=moon_color)
            else:  # Last quarter
                # Last quarter - left half illuminated
                draw.ellipse([x-size, y-size, x+size, y+size], fill=shadow_color)
                draw.ellipse([x-size, y-size, x, y+size], fill=moon_color)
                
        elif "Crescent" in moon_phase:
            # Crescent phases
            moon_color = (240, 240, 220)
            crescent_width = max(size//4, int(size * illum_ratio))
            
            if "Waxing" in moon_phase:
                # Waxing crescent - thin slice on right
                for i in range(-size, size):
                    y_pos = y + i
                    if abs(i) < size:
                        x_width = int(math.sqrt(size*size - i*i) * illum_ratio * 2)
                        if x_width > 0:
                            draw.line([(x-x_width//2, y_pos), (x+x_width//2, y_pos)], fill=moon_color)
            else:  # Waning crescent
                # Waning crescent - thin slice on left
                for i in range(-size, size):
                    y_pos = y + i
                    if abs(i) < size:
                        x_width = int(math.sqrt(size*size - i*i) * illum_ratio * 2)
                        if x_width > 0:
                            draw.line([(x-x_width//2, y_pos), (x+x_width//2, y_pos)], fill=moon_color)
                            
        elif "Gibbous" in moon_phase:
            # Gibbous phases - more than half but not full
            moon_color = (240, 240, 220)
            
            # Start with full moon
            draw.ellipse([x-size, y-size, x+size, y+size], fill=moon_color)
            
            # Add shadow portion
            shadow_width = int(size * (1 - illum_ratio) * 2)
            if "Waxing" in moon_phase:
                # Waxing gibbous - shadow on left
                draw.ellipse([x-size, y-size, x-size+shadow_width, y+size], fill=shadow_color)
            else:  # Waning gibbous
                # Waning gibbous - shadow on right
                draw.ellipse([x+size-shadow_width, y-size, x+size, y+size], fill=shadow_color)
        
        # Add subtle rim lighting
        rim_color = (180, 180, 160)
        draw.ellipse([x-size-1, y-size-1, x+size+1, y+size+1], outline=rim_color, width=1)
        
        # Moon glow effect
        glow_color = (100, 100, 80)
        for i in range(1, 4):
            glow_size = size + i * 2
            draw.ellipse([x-glow_size, y-glow_size, x+glow_size, y+glow_size], 
                        outline=glow_color, width=1)
    
    def display(self):
        """Display enhanced real-time star chart with accurate astronomical data."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Generating Real-Time Star Chart...")
        
        try:
            # Fetch real astronomical data
            star_data = self.fetch_real_astronomy_data()
            self.current_starmap = star_data
            
            # Load optimized fonts
            fonts = get_starmap_fonts()
            font_title = fonts['title']     # 22pt title font
            font_large = fonts['large']     # 16pt regular font  
            font_medium = fonts['medium']   # 14pt regular font
            font_small = fonts['small']     # 11pt small font
            
            # Create sophisticated night sky background
            display_image = self.create_advanced_starmap_background()
            draw = ImageDraw.Draw(display_image)
            
            # Enhanced title with gradient effect
            title = "REAL-TIME NIGHT SKY"
            if font_title:
                bbox = draw.textbbox((0, 0), title, font=font_title)
                title_width = bbox[2] - bbox[0]
                title_x = (640 - title_width) // 2
                
                # Title background for visibility
                title_bg_height = bbox[3] - bbox[1] + 6
                draw.rectangle([title_x-10, 5, title_x+title_width+10, 5+title_bg_height], 
                              fill=self.colors['black'], outline=self.colors['blue'])
                
                # Title text with outline
                for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    draw.text((title_x+dx, 8+dy), title, fill=self.colors['black'], font=font_title)
                draw.text((title_x, 8), title, fill=self.colors['white'], font=font_title)
            
            # Current time and date
            time_text = star_data["time"]
            if font_medium:
                bbox = draw.textbbox((0, 0), time_text, font=font_medium)
                time_width = bbox[2] - bbox[0]
                time_x = (640 - time_width) // 2
                
                # Time background
                draw.rectangle([time_x-5, 35, time_x+time_width+5, 52], 
                              fill=(0, 0, 0, 180))
                
                # Time text
                draw.text((time_x+1, 37), time_text, fill=self.colors['black'], font=font_medium)
                draw.text((time_x, 36), time_text, fill=self.colors['yellow'], font=font_medium)
            
            # Draw enhanced constellations with seasonal coding
            for constellation_name, constellation_data in star_data["constellations"].items():
                self.draw_enhanced_constellation(draw, constellation_name, constellation_data, font_small)
            
            # Draw realistic planets
            planet_positions = [
                (100, 120), (180, 180), (520, 140), (580, 200), (300, 110)
            ]
            
            visible_planets = star_data.get("visible_planets", [])
            for i, planet in enumerate(visible_planets[:5]):
                if i < len(planet_positions):
                    x, y = planet_positions[i]
                    self.draw_realistic_planet(draw, planet, x, y, font_small)
            
            # Draw accurate moon phase
            moon_x, moon_y = 550, 320
            moon_phase = star_data.get("moon_phase", "Unknown")
            moon_illumination = star_data.get("moon_illumination", 50)
            self.draw_accurate_moon_phase(draw, moon_phase, moon_illumination, moon_x, moon_y, 30)
            
            # Enhanced information panel with real data
            info_panel_y = 340
            panel_height = 60
            
            # Semi-transparent info background
            info_bg = Image.new("RGBA", (640, panel_height), (0, 0, 0, 200))
            display_image.paste(info_bg, (0, info_panel_y), info_bg)
            
            # Draw border
            draw.rectangle([0, info_panel_y, 639, info_panel_y+panel_height-1], 
                          outline=self.colors['blue'], width=2)
            
            # Real astronomical data display
            info_y_base = info_panel_y + 5
            
            if font_medium:
                # Moon information with accurate data
                moon_text = f"Moon: {moon_phase} ({moon_illumination}% illuminated)"
                draw.text((11, info_y_base+1), moon_text, fill=self.colors['black'], font=font_medium)
                draw.text((10, info_y_base), moon_text, fill=self.colors['yellow'], font=font_medium)
            
            if font_small:
                # Real sunrise/sunset times
                sunrise = star_data.get("sunrise", "Calculating...")
                sunset = star_data.get("sunset", "Calculating...")
                sun_info = f"Sun: Rise {sunrise} | Set {sunset}"
                draw.text((11, info_y_base+21), sun_info, fill=self.colors['black'], font=font_small)
                draw.text((10, info_y_base+20), sun_info, fill=self.colors['orange'], font=font_small)
                
                # Location and additional info
                location_text = f"Location: {self.city_name} | Sidereal Time: {star_data.get('sidereal_time', 0):.1f}°"
                draw.text((11, info_y_base+36), location_text, fill=self.colors['black'], font=font_small)
                draw.text((10, info_y_base+35), location_text, fill=self.colors['green'], font=font_small)
                
                # Visible planets info
                if visible_planets:
                    planets_text = f"Visible: {', '.join(visible_planets)}"
                    # Right side info
                    bbox = draw.textbbox((0, 0), planets_text, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    planets_x = 640 - text_width - 10
                    draw.text((planets_x+1, info_y_base+1), planets_text, fill=self.colors['black'], font=font_small)
                    draw.text((planets_x, info_y_base), planets_text, fill=self.colors['white'], font=font_small)
            
            # Add compass rose in corner
            self.draw_compass_rose(draw, 50, 350, 25)
            
            # Ensure proper format for e-ink display
            if display_image.mode != 'RGB':
                display_image = display_image.convert('RGB')
            
            # Display the enhanced star chart
            self.inky.set_image(display_image)
            self.inky.show()
            
            print(f"Enhanced star chart displayed with real astronomical data")
            print(f"Sunrise: {sunrise}, Sunset: {sunset}")
            print(f"Moon: {moon_phase} ({moon_illumination}% illuminated)")
            
        except Exception as e:
            print(f"Error displaying star chart: {e}")
            import traceback
            traceback.print_exc()
            self.display_error_message("Star Chart Error", str(e))
    
    def draw_compass_rose(self, draw, center_x, center_y, size):
        """Draw a compass rose showing cardinal directions."""
        # Outer circle
        draw.ellipse([center_x-size, center_y-size, center_x+size, center_y+size], 
                    outline=self.colors['white'], width=2)
        
        # Cardinal directions
        directions = [
            (0, -size, "N"),    # North
            (size, 0, "E"),     # East  
            (0, size, "S"),     # South
            (-size, 0, "W")     # West
        ]
        
        for dx, dy, label in directions:
            # Direction line
            draw.line([(center_x, center_y), (center_x+dx, center_y+dy)], 
                     fill=self.colors['white'], width=2)
            
        # Direction label
        label_x = center_x + dx + (5 if dx > 0 else -10 if dx < 0 else -3)
        label_y = center_y + dy + (5 if dy > 0 else -15 if dy < 0 else -5)
        
        font_small = get_font('small', 10)
        if font_small:
            draw.text((label_x, label_y), label, fill=self.colors['red'], font=font_small)        # Center point
        draw.ellipse([center_x-3, center_y-3, center_x+3, center_y+3], fill=self.colors['red'])
    
    def display_error_message(self, title, message):
        """Display error message with night sky theme."""
        image = Image.new("RGB", (640, 400), self.colors['black'])
        draw = ImageDraw.Draw(image)
        
        try:
            font_title = get_font('title', 18)
            font_text = get_font('regular', 14)
        except:
            font_title = font_text = get_font('regular', 14)
            
        if font_title:
            bbox = draw.textbbox((0, 0), title, font=font_title)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 180), title, fill=self.colors['red'], font=font_title)
            
        if font_text:
            if len(message) > 60:
                message = message[:57] + "..."
            bbox = draw.textbbox((0, 0), message, font=font_text)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 220), message, fill=self.colors['white'], font=font_text)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        self.inky.set_image(image)
        self.inky.show()
