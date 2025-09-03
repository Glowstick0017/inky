"""
Weather Forecast Screen - Rich Visual Design with Large Text
Displays beautiful weather forecast for Phoenix, Arizona with rich colors and visual elements
Updates every 15 minutes with current conditions and 5-day forecast
"""

import requests
import json
import math
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from .base_screen import BaseScreen
import config
from font_utils import get_weather_fonts

class WeatherScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.WEATHER_UPDATE_INTERVAL
        self.current_weather = None
        
        # Use coordinates from config
        self.latitude = config.WEATHER_LATITUDE
        self.longitude = config.WEATHER_LONGITUDE
        self.city_name = config.WEATHER_CITY_NAME
        
        # Weather API endpoint
        self.current_weather_url = "https://api.open-meteo.com/v1/forecast"
        
        # Weather descriptions
        self.weather_descriptions = {
            0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
            45: "Fog", 48: "Rime Fog", 51: "Light Drizzle", 53: "Moderate Drizzle",
            55: "Dense Drizzle", 61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
            71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
            80: "Rain Showers", 81: "Heavy Showers", 95: "Thunderstorm"
        }
        
        # Rich color themes for different weather conditions
        self.weather_themes = {
            # Clear and sunny - warm golden theme
            0: {
                "gradient": [(255, 215, 0), (255, 165, 0), (255, 140, 0)],
                "accent": (255, 255, 255),
                "pattern_color": (255, 255, 200),
                "text_color": (139, 69, 19)
            },
            1: {
                "gradient": [(255, 228, 181), (255, 215, 0), (255, 185, 15)],
                "accent": (255, 255, 255),
                "pattern_color": (255, 255, 220),
                "text_color": (139, 69, 19)
            },
            
            # Cloudy - blue-gray theme
            2: {
                "gradient": [(135, 206, 235), (100, 149, 237), (70, 130, 180)],
                "accent": (255, 255, 255),
                "pattern_color": (255, 255, 255),
                "text_color": (25, 25, 112)
            },
            3: {
                "gradient": [(105, 105, 105), (119, 136, 153), (112, 128, 144)],
                "accent": (255, 255, 255),
                "pattern_color": (220, 220, 220),
                "text_color": (47, 79, 79)
            },
            
            # Fog - soft gray-blue theme
            45: {
                "gradient": [(176, 196, 222), (169, 169, 169), (128, 128, 128)],
                "accent": (255, 255, 255),
                "pattern_color": (255, 255, 255),
                "text_color": (47, 79, 79)
            },
            48: {
                "gradient": [(176, 196, 222), (169, 169, 169), (128, 128, 128)],
                "accent": (255, 255, 255),
                "pattern_color": (255, 255, 255),
                "text_color": (47, 79, 79)
            },
            
            # Drizzle - light blue theme
            51: {
                "gradient": [(173, 216, 230), (135, 206, 235), (100, 149, 237)],
                "accent": (255, 255, 255),
                "pattern_color": (255, 255, 255),
                "text_color": (25, 25, 112)
            },
            53: {
                "gradient": [(173, 216, 230), (135, 206, 235), (100, 149, 237)],
                "accent": (255, 255, 255),
                "pattern_color": (255, 255, 255),
                "text_color": (25, 25, 112)
            },
            55: {
                "gradient": [(173, 216, 230), (135, 206, 235), (100, 149, 237)],
                "accent": (255, 255, 255),
                "pattern_color": (255, 255, 255),
                "text_color": (25, 25, 112)
            },
            
            # Rain - deep blue theme
            61: {
                "gradient": [(25, 25, 112), (70, 130, 180), (100, 149, 237)],
                "accent": (255, 255, 255),
                "pattern_color": (173, 216, 230),
                "text_color": (255, 255, 255)
            },
            63: {
                "gradient": [(0, 0, 139), (25, 25, 112), (70, 130, 180)],
                "accent": (255, 255, 255),
                "pattern_color": (173, 216, 230),
                "text_color": (255, 255, 255)
            },
            65: {
                "gradient": [(0, 0, 139), (25, 25, 112), (70, 130, 180)],
                "accent": (255, 255, 255),
                "pattern_color": (173, 216, 230),
                "text_color": (255, 255, 255)
            },
            
            # Snow - cool white-blue theme
            71: {
                "gradient": [(240, 248, 255), (220, 220, 220), (176, 196, 222)],
                "accent": (100, 149, 237),
                "pattern_color": (255, 255, 255),
                "text_color": (25, 25, 112)
            },
            73: {
                "gradient": [(240, 248, 255), (220, 220, 220), (176, 196, 222)],
                "accent": (100, 149, 237),
                "pattern_color": (255, 255, 255),
                "text_color": (25, 25, 112)
            },
            75: {
                "gradient": [(240, 248, 255), (220, 220, 220), (176, 196, 222)],
                "accent": (100, 149, 237),
                "pattern_color": (255, 255, 255),
                "text_color": (25, 25, 112)
            },
            
            # Showers - bright blue theme
            80: {
                "gradient": [(30, 144, 255), (65, 105, 225), (100, 149, 237)],
                "accent": (255, 255, 255),
                "pattern_color": (173, 216, 230),
                "text_color": (255, 255, 255)
            },
            81: {
                "gradient": [(30, 144, 255), (65, 105, 225), (100, 149, 237)],
                "accent": (255, 255, 255),
                "pattern_color": (173, 216, 230),
                "text_color": (255, 255, 255)
            },
            
            # Thunderstorm - dramatic purple-black
            95: {
                "gradient": [(25, 25, 112), (75, 0, 130), (72, 61, 139)],
                "accent": (255, 255, 0),
                "pattern_color": (255, 255, 0),
                "text_color": (255, 255, 255)
            }
        }
        
        # Fallback weather data
        self.fallback_weather = {
            "current": {
                "temperature": 89, "humidity": 28, "windspeed": 6, "weathercode": 0,
                "time": datetime.now().isoformat()
            },
            "daily": {
                "time": [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)],
                "temperature_2m_max": [92, 95, 88, 85, 90],
                "temperature_2m_min": [68, 71, 65, 63, 67],
                "weathercode": [0, 1, 2, 61, 0]
            }
        }
    
    def fetch_weather_data(self):
        """Fetch weather data from Open-Meteo API."""
        try:
            params = {
                'latitude': self.latitude, 'longitude': self.longitude,
                'current_weather': 'true', 'hourly': 'relative_humidity_2m',
                'daily': 'temperature_2m_max,temperature_2m_min,weathercode',
                'temperature_unit': 'fahrenheit', 'windspeed_unit': 'mph',
                'timezone': 'America/Phoenix', 'forecast_days': 5
            }
            
            response = requests.get(self.current_weather_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_weather', {})
                daily = data.get('daily', {})
                
                humidity = 28  # Default for Phoenix
                if 'hourly' in data and 'relative_humidity_2m' in data['hourly']:
                    humidity = data['hourly']['relative_humidity_2m'][0] or 28
                
                weather_data = {
                    "current": {
                        "temperature": current.get('temperature', 89),
                        "humidity": humidity,
                        "windspeed": current.get('windspeed', 0),
                        "weathercode": current.get('weathercode', 0),
                        "time": current.get('time', datetime.now().isoformat())
                    },
                    "daily": daily
                }
                return weather_data
                
        except Exception as e:
            print(f"Error fetching weather data: {e}")
        
        return self.fallback_weather
    
    def get_weather_theme(self, weather_code):
        """Get weather theme with fallback for unknown codes."""
        # Check if we have a specific theme for this weather code
        if weather_code in self.weather_themes:
            return self.weather_themes[weather_code]
        
        # Fallback themes based on weather type
        fallback_themes = {
            # Clear conditions (0-9)
            range(0, 10): self.weather_themes[0],
            # Cloudy conditions (10-49) 
            range(10, 50): self.weather_themes[3],
            # Drizzle/Rain conditions (50-69)
            range(50, 70): self.weather_themes[61],
            # Snow conditions (70-79)
            range(70, 80): self.weather_themes.get(71, self.weather_themes[3]),
            # Showers (80-89)
            range(80, 90): self.weather_themes.get(80, self.weather_themes[61]),
            # Thunderstorms (90-99)
            range(90, 100): self.weather_themes[95]
        }
        
        # Find appropriate fallback theme
        for code_range, theme in fallback_themes.items():
            if weather_code in code_range:
                return theme
        
        # Ultimate fallback - cloudy theme
        return self.weather_themes[3]

    def create_weather_background(self, weather_code):
        """Create rich, colorful weather-themed background with enhanced depth."""
        # Get theme with intelligent fallback
        theme = self.get_weather_theme(weather_code)
        
        image = Image.new("RGB", (640, 400), theme["gradient"][0])
        draw = ImageDraw.Draw(image)
        
        # Create enhanced multi-layer gradient background with atmospheric perspective
        for y in range(400):
            ratio = y / 400
            
            # Create a more complex, atmospheric gradient
            if ratio < 0.15:
                # Sky dome - highest atmosphere
                blend_ratio = ratio / 0.15
                # Add subtle color variations for realism
                r = int(theme["gradient"][0][0] * (1 - blend_ratio * 0.8) + theme["gradient"][1][0] * blend_ratio * 0.8)
                g = int(theme["gradient"][0][1] * (1 - blend_ratio * 0.8) + theme["gradient"][1][1] * blend_ratio * 0.8)
                b = int(theme["gradient"][0][2] * (1 - blend_ratio * 0.8) + theme["gradient"][1][2] * blend_ratio * 0.8)
                # Add atmospheric haze
                haze_factor = 1 - (ratio * 0.1)
                r = int(r * haze_factor + 255 * (1 - haze_factor) * 0.05)
                g = int(g * haze_factor + 255 * (1 - haze_factor) * 0.05)
                b = int(b * haze_factor + 255 * (1 - haze_factor) * 0.05)
            elif ratio < 0.35:
                # Upper atmosphere
                blend_ratio = (ratio - 0.15) / 0.2
                r = int(theme["gradient"][0][0] * (1 - blend_ratio) + theme["gradient"][1][0] * blend_ratio)
                g = int(theme["gradient"][0][1] * (1 - blend_ratio) + theme["gradient"][1][1] * blend_ratio)
                b = int(theme["gradient"][0][2] * (1 - blend_ratio) + theme["gradient"][1][2] * blend_ratio)
            elif ratio < 0.75:
                # Middle atmosphere - main gradient with subtle variations
                blend_ratio = (ratio - 0.35) / 0.4
                r = int(theme["gradient"][1][0] * (1 - blend_ratio) + theme["gradient"][2][0] * blend_ratio)
                g = int(theme["gradient"][1][1] * (1 - blend_ratio) + theme["gradient"][2][1] * blend_ratio)
                b = int(theme["gradient"][1][2] * (1 - blend_ratio) + theme["gradient"][2][2] * blend_ratio)
                # Add subtle atmospheric scattering effect
                scattering = math.sin(ratio * math.pi) * 0.03
                r = max(0, min(255, int(r + scattering * 20)))
                g = max(0, min(255, int(g + scattering * 15)))
                b = max(0, min(255, int(b + scattering * 10)))
            else:
                # Lower atmosphere - deeper with ground effect
                bottom_ratio = (ratio - 0.75) / 0.25
                base_r, base_g, base_b = theme["gradient"][2]
                # Create depth with progressive darkening
                darken_factor = 0.2 + bottom_ratio * 0.15
                r = int(base_r * (1 - darken_factor))
                g = int(base_g * (1 - darken_factor))
                b = int(base_b * (1 - darken_factor))
                # Add ground mist effect for certain weather conditions
                if weather_code in [45, 48]:  # Fog
                    mist_alpha = bottom_ratio * 0.3
                    r = int(r * (1 - mist_alpha) + 220 * mist_alpha)
                    g = int(g * (1 - mist_alpha) + 220 * mist_alpha)
                    b = int(b * (1 - mist_alpha) + 220 * mist_alpha)
            
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Add sophisticated depth layers
        self.add_depth_layers(draw, theme, weather_code)
        
        # Add enhanced texture overlay for depth
        self.add_texture_overlay(draw, theme)
        
        # Add weather-specific visual elements
        self.add_weather_visuals(draw, weather_code, theme)
        
        return image, theme
    
    def add_depth_layers(self, draw, theme, weather_code):
        """Add sophisticated atmospheric depth layers."""
        # Atmospheric haze layers that vary by weather condition
        if weather_code in [0, 1]:  # Clear weather - add heat shimmer layers
            for i in range(3):
                y_pos = 320 + i * 20
                alpha = 30 - i * 8
                # Subtle heat wave effect
                for x in range(0, 640, 40):
                    shimmer_y = y_pos + math.sin(x / 50) * 3
                    draw.ellipse([x, shimmer_y, x+35, shimmer_y+8], 
                               fill=(*theme["pattern_color"][:3], alpha))
        
        elif weather_code in [2, 3]:  # Cloudy - add cloud layers at different altitudes
            # High altitude cirrus-like wisps
            for i in range(2):
                y_base = 80 + i * 40
                alpha = 40 - i * 15
                for x in range(0, 640, 80):
                    # Wispy cloud streaks
                    draw.ellipse([x-10, y_base, x+60, y_base+12], 
                               fill=(255, 255, 255, alpha))
                    draw.ellipse([x+20, y_base+5, x+80, y_base+15], 
                               fill=(255, 255, 255, alpha-10))
        
        elif weather_code in [61, 63, 65, 80, 81]:  # Rain - add multiple rain cloud layers
            # Low hanging cloud bases
            for i in range(3):
                y_pos = 50 + i * 25
                alpha = 60 - i * 15
                # Layered storm clouds
                draw.ellipse([50 + i*150, y_pos, 200 + i*150, y_pos+30], 
                           fill=(105, 105, 105, alpha))
        
        elif weather_code in [71, 73, 75]:  # Snow - add multiple snow cloud layers
            # Heavy, low snow clouds
            for i in range(2):
                y_pos = 60 + i * 30
                alpha = 50 - i * 10
                for x in range(0, 640, 120):
                    draw.ellipse([x, y_pos, x+80, y_pos+25], 
                               fill=(220, 220, 220, alpha))
        
        # Add distant mountain/horizon silhouettes for depth
        horizon_y = 350
        # Create subtle horizon line with varying elevation
        horizon_points = []
        for x in range(0, 640, 20):
            y_offset = math.sin(x / 100) * 8 + math.cos(x / 80) * 5
            horizon_points.append((x, horizon_y + y_offset))
        
        # Draw horizon with atmospheric perspective
        horizon_color = [
            max(0, min(255, int(c * 0.6))) for c in theme["gradient"][2]
        ]
        
        for i, (x, y) in enumerate(horizon_points[:-1]):
            next_x, next_y = horizon_points[i + 1]
            # Fill below horizon
            draw.polygon([(x, y), (next_x, next_y), (next_x, 400), (x, 400)], 
                        fill=tuple(horizon_color))
    
    def add_texture_overlay(self, draw, theme):
        """Add sophisticated texture for visual depth."""
        import random
        random.seed(42)  # Consistent pattern
        
        # Add atmospheric particles/dust motes
        for i in range(120):
            x = random.randint(0, 640)
            y = random.randint(0, 400)
            # Vary particle size and opacity based on position (atmospheric perspective)
            size = max(1, int(3 - (y / 400) * 2))  # Smaller particles higher up
            alpha = max(10, int(40 - (y / 400) * 20))  # Fainter particles higher up
            
            particle_color = (*theme["pattern_color"][:3], alpha)
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                        fill=particle_color[:3])
        
        # Add subtle directional texture streaks for wind effect
        for i in range(30):
            start_x = random.randint(0, 600)
            start_y = random.randint(50, 300)
            length = random.randint(15, 40)
            angle = random.uniform(-15, 15)  # Slight wind angle
            
            end_x = start_x + length * math.cos(math.radians(angle))
            end_y = start_y + length * math.sin(math.radians(angle))
            
            streak_alpha = random.randint(8, 20)
            streak_color = (*theme["pattern_color"][:3], streak_alpha)
            draw.line([(start_x, start_y), (end_x, end_y)], 
                     fill=streak_color[:3], width=1)
    
    def add_weather_visuals(self, draw, weather_code, theme):
        """Add rich visual elements based on weather condition."""
        pattern_color = theme["pattern_color"]
        
        if weather_code in [0, 1]:  # Clear/sunny
            # Large sun with detailed rays
            sun_x, sun_y = 500, 80
            # Sun body with gradient effect
            draw.ellipse([sun_x-30, sun_y-30, sun_x+30, sun_y+30], fill=(255, 215, 0))
            draw.ellipse([sun_x-25, sun_y-25, sun_x+25, sun_y+25], fill=(255, 255, 0))
            draw.ellipse([sun_x-15, sun_y-15, sun_x+15, sun_y+15], fill=(255, 255, 200))
            
            # Detailed sun rays
            for angle in range(0, 360, 15):
                rad = math.radians(angle)
                x1 = sun_x + 35 * math.cos(rad)
                y1 = sun_y + 35 * math.sin(rad)
                x2 = sun_x + 55 * math.cos(rad)
                y2 = sun_y + 55 * math.sin(rad)
                draw.line([(x1, y1), (x2, y2)], fill=pattern_color, width=4)
            
            # Scattered light rays
            for angle in range(7, 360, 15):
                rad = math.radians(angle)
                x1 = sun_x + 60 * math.cos(rad)
                y1 = sun_y + 60 * math.sin(rad)
                x2 = sun_x + 75 * math.cos(rad)
                y2 = sun_y + 75 * math.sin(rad)
                draw.line([(x1, y1), (x2, y2)], fill=pattern_color, width=2)
        
        elif weather_code in [2, 3]:  # Cloudy
            # Multiple detailed clouds with varying sizes
            cloud_positions = [(120, 60), (350, 80), (520, 70)]
            cloud_sizes = [1.0, 1.2, 0.8]
            for i, (x, y) in enumerate(cloud_positions):
                self.draw_detailed_cloud(draw, x, y, pattern_color, scale=cloud_sizes[i])
        
        elif weather_code in [45, 48]:  # Fog
            # Fog layers with horizontal waves
            for y in range(100, 200, 15):
                for x in range(0, 640, 30):
                    draw.ellipse([x, y, x+25, y+8], fill=(*pattern_color[:3], 100))
            
        elif weather_code in [51, 53, 55]:  # Drizzle
            # Light rain with smaller droplets
            import random
            random.seed(weather_code)  # Consistent pattern per condition
            for _ in range(25):
                x = random.randint(50, 590)
                y = random.randint(120, 350)
                # Small drizzle drops
                draw.ellipse([x-1, y, x+1, y+8], fill=(135, 206, 235))
        
        elif weather_code in [61, 63, 65]:  # Rain
            # Rain clouds with droplets
            self.draw_detailed_cloud(draw, 300, 60, (169, 169, 169), scale=1.3)
            
            # Animated-style rain drops with varying intensity
            import random
            random.seed(42)  # Consistent pattern
            drop_count = 30 if weather_code == 61 else 45 if weather_code == 63 else 60
            for _ in range(drop_count):
                x = random.randint(50, 590)
                y = random.randint(120, 350)
                # Rain drop shape
                draw.ellipse([x-2, y, x+2, y+12], fill=(135, 206, 235))
                draw.ellipse([x-1, y+10, x+1, y+14], fill=(100, 149, 237))
        
        elif weather_code in [71, 73, 75]:  # Snow
            # Snow clouds and snowflakes
            self.draw_detailed_cloud(draw, 250, 50, (240, 248, 255), scale=1.2)
            self.draw_detailed_cloud(draw, 450, 70, (220, 220, 220), scale=0.9)
            
            # Snowflakes
            import random
            random.seed(weather_code)
            flake_count = 20 if weather_code == 71 else 35 if weather_code == 73 else 50
            for _ in range(flake_count):
                x = random.randint(50, 590)
                y = random.randint(120, 350)
                self.draw_snowflake(draw, x, y, pattern_color)
        
        elif weather_code in [80, 81]:  # Showers
            # Shower clouds with heavy droplets
            self.draw_detailed_cloud(draw, 200, 50, (105, 105, 105), scale=1.1)
            self.draw_detailed_cloud(draw, 400, 60, (128, 128, 128), scale=1.0)
            
            # Heavy shower drops
            import random
            random.seed(weather_code)
            for _ in range(40 if weather_code == 80 else 55):
                x = random.randint(50, 590)
                y = random.randint(120, 350)
                # Larger shower drops
                draw.ellipse([x-3, y, x+3, y+16], fill=(30, 144, 255))
                draw.ellipse([x-2, y+12, x+2, y+18], fill=(65, 105, 225))
        
        elif weather_code == 95:  # Thunderstorm
            # Dramatic storm clouds
            self.draw_detailed_cloud(draw, 200, 50, (105, 105, 105), scale=1.4)
            self.draw_detailed_cloud(draw, 400, 70, (105, 105, 105), scale=1.2)
            
            # Lightning bolts
            self.draw_lightning_bolt(draw, 250, 120, pattern_color)
            self.draw_lightning_bolt(draw, 450, 140, pattern_color)
            
            # Heavy rain
            import random
            random.seed(95)
            for _ in range(35):
                x = random.randint(50, 590)
                y = random.randint(120, 350)
                draw.ellipse([x-2, y, x+2, y+14], fill=(135, 206, 235))
    
    def draw_detailed_cloud(self, draw, x, y, color, scale=1.0):
        """Draw a detailed, fluffy cloud with optional scaling."""
        # Multiple overlapping circles for realistic cloud shape
        cloud_parts = [
            (x-20*scale, y+5*scale, 18*scale), (x-5*scale, y-5*scale, 22*scale), 
            (x+10*scale, y, 20*scale), (x+25*scale, y+3*scale, 18*scale), 
            (x+15*scale, y+15*scale, 16*scale), (x-10*scale, y+12*scale, 15*scale)
        ]
        
        for cx, cy, radius in cloud_parts:
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=color)
            # Add subtle highlight
            highlight_color = (min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20))
            draw.ellipse([cx-radius+3, cy-radius+2, cx+radius-3, cy+radius-8], 
                        fill=highlight_color)
    
    def draw_snowflake(self, draw, x, y, color):
        """Draw a detailed snowflake."""
        # Main cross
        draw.line([(x-4, y), (x+4, y)], fill=color, width=2)
        draw.line([(x, y-4), (x, y+4)], fill=color, width=2)
        # Diagonal lines
        draw.line([(x-3, y-3), (x+3, y+3)], fill=color, width=1)
        draw.line([(x-3, y+3), (x+3, y-3)], fill=color, width=1)
        # Center dot
        draw.ellipse([x-1, y-1, x+1, y+1], fill=color)
    
    def draw_lightning_bolt(self, draw, start_x, start_y, color):
        """Draw a dramatic lightning bolt."""
        points = [
            (start_x, start_y), (start_x-8, start_y+25), (start_x+4, start_y+30),
            (start_x-12, start_y+60), (start_x+8, start_y+65), (start_x-4, start_y+95)
        ]
        
        # Draw main bolt
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=color, width=6)
        
        # Add glow effect
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=(255, 255, 255), width=2)
    
    def create_weather_icon_large(self, weather_code, size=60):
        """Create stunning, detailed weather icons with professional quality."""
        icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        center = size // 2
        
        if weather_code in [0, 1]:  # Sunny/Clear - Premium sun design
            # Create radial gradient sun with multiple layers
            # Outer corona with gradient effect
            for radius in range(28, 18, -2):
                alpha = int(80 - (28-radius) * 8)
                corona_color = (255, 215, 0, alpha)
                draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                           fill=corona_color[:3])
            
            # Main sun body with sophisticated gradient
            draw.ellipse([center-18, center-18, center+18, center+18], fill=(255, 180, 0))
            draw.ellipse([center-15, center-15, center+15, center+15], fill=(255, 200, 20))
            draw.ellipse([center-12, center-12, center+12, center+12], fill=(255, 220, 50))
            draw.ellipse([center-9, center-9, center+9, center+9], fill=(255, 240, 100))
            draw.ellipse([center-6, center-6, center+6, center+6], fill=(255, 255, 150))
            draw.ellipse([center-3, center-3, center+3, center+3], fill=(255, 255, 200))
            
            # Dynamic sun rays with varying styles
            ray_styles = [
                {"length": 28, "width": 4, "color": (255, 200, 0)},
                {"length": 35, "width": 3, "color": (255, 220, 50)},
                {"length": 25, "width": 2, "color": (255, 240, 100)}
            ]
            
            for style_idx, style in enumerate(ray_styles):
                for i, angle in enumerate(range(style_idx * 10, 360, 30)):
                    if i % (style_idx + 1) == 0:  # Varied ray patterns
                        rad = math.radians(angle)
                        # Inner point
                        x1 = center + 20 * math.cos(rad)
                        y1 = center + 20 * math.sin(rad)
                        # Outer point with slight randomization
                        offset = style["length"] + (i % 3 - 1) * 3
                        x2 = center + offset * math.cos(rad)
                        y2 = center + offset * math.sin(rad)
                        
                        # Draw tapered ray
                        ray_points = [
                            (x1 + 2 * math.cos(rad + math.pi/2), y1 + 2 * math.sin(rad + math.pi/2)),
                            (x1 + 2 * math.cos(rad - math.pi/2), y1 + 2 * math.sin(rad - math.pi/2)),
                            (x2, y2)
                        ]
                        draw.polygon(ray_points, fill=style["color"])
        
        elif weather_code in [2, 3]:  # Cloudy - Volumetric cloud design
            if weather_code == 2:  # Partly cloudy - sophisticated sun-cloud interaction
                # Partial sun with realistic occlusion
                visible_arc = 180  # Degrees of sun visible
                for angle in range(-90, visible_arc - 90, 5):
                    rad = math.radians(angle)
                    arc_x = center - 12 + 15 * math.cos(rad)
                    arc_y = center - 8 + 15 * math.sin(rad)
                    draw.ellipse([arc_x-1, arc_y-1, arc_x+1, arc_y+1], fill=(255, 215, 0))
                
                # Visible sun rays emerging from behind cloud
                for angle in range(-110, visible_arc - 70, 20):
                    rad = math.radians(angle)
                    x1 = center - 12 + 18 * math.cos(rad)
                    y1 = center - 8 + 18 * math.sin(rad)
                    x2 = center - 12 + 30 * math.cos(rad)
                    y2 = center - 8 + 30 * math.sin(rad)
                    draw.line([(x1, y1), (x2, y2)], fill=(255, 230, 100), width=3)
            
            # Professional volumetric cloud with realistic shading
            # Cloud base layer (shadow)
            cloud_shadow_parts = [
                (center-22, center+2, 16), (center-8, center-8, 20), 
                (center+8, center-3, 18), (center+22, center+1, 16),
                (center+12, center+12, 15), (center-12, center+10, 14)
            ]
            
            for cx, cy, radius in cloud_shadow_parts:
                draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], 
                           fill=(140, 140, 140))
            
            # Mid-tone cloud layer
            cloud_mid_parts = [
                (center-20, center, 15), (center-6, center-10, 19), 
                (center+10, center-5, 17), (center+20, center-1, 15),
                (center+10, center+10, 14), (center-10, center+8, 13)
            ]
            
            for cx, cy, radius in cloud_mid_parts:
                draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], 
                           fill=(180, 180, 180))
            
            # Highlight layer for volume
            cloud_highlight_parts = [
                (center-18, center-2, 14), (center-4, center-12, 18), 
                (center+12, center-7, 16), (center+18, center-3, 14),
                (center+8, center+8, 13), (center-8, center+6, 12)
            ]
            
            for cx, cy, radius in cloud_highlight_parts:
                draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], 
                           fill=(220, 220, 220))
            
            # Bright highlights for realism
            highlight_spots = [
                (center-15, center-8, 8), (center-2, center-14, 10),
                (center+10, center-9, 9), (center+15, center-5, 7)
            ]
            
            for cx, cy, radius in highlight_spots:
                draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], 
                           fill=(245, 245, 245))
        
        elif weather_code in [45, 48]:  # Fog - Layered mist effect
            # Multiple fog layers with varying opacity
            fog_layers = [
                {"y_offset": -12, "width": 35, "height": 6, "color": (200, 200, 200)},
                {"y_offset": -4, "width": 40, "height": 7, "color": (180, 190, 200)},
                {"y_offset": 4, "width": 38, "height": 6, "color": (190, 195, 205)},
                {"y_offset": 12, "width": 42, "height": 8, "color": (170, 180, 190)},
                {"y_offset": 22, "width": 36, "height": 6, "color": (185, 190, 200)}
            ]
            
            for layer in fog_layers:
                y_pos = center + layer["y_offset"]
                # Create wispy fog effect
                draw.ellipse([center - layer["width"]//2, y_pos - layer["height"]//2,
                            center + layer["width"]//2, y_pos + layer["height"]//2], 
                           fill=layer["color"])
                
                # Add internal texture to fog
                for i in range(3):
                    mini_x = center - layer["width"]//4 + i * layer["width"]//6
                    mini_y = y_pos + (i % 2 - 0.5) * 2
                    draw.ellipse([mini_x-2, mini_y-1, mini_x+2, mini_y+1], 
                               fill=(220, 220, 220))
        
        elif weather_code in [51, 53, 55]:  # Drizzle - Delicate rain cloud
            # Soft drizzle cloud
            self.draw_professional_cloud(draw, center, center-8, 0.8, (160, 160, 160))
            
            # Fine drizzle drops with realistic physics
            drizzle_intensity = {51: 6, 53: 8, 55: 10}
            drop_count = drizzle_intensity.get(weather_code, 6)
            
            for i in range(drop_count):
                drop_x = center - 15 + i * 4
                drop_y = center + 5 + (i % 3) * 3
                # Small, delicate drops
                self.draw_realistic_raindrop(draw, drop_x, drop_y, 2, (120, 160, 200))
        
        elif weather_code in [61, 63, 65]:  # Rain - Professional rain design
            # Robust rain cloud with gradient
            self.draw_professional_cloud(draw, center, center-10, 1.0, (100, 100, 100))
            
            # Realistic rain drops with varying sizes
            rain_intensity = {61: 8, 63: 12, 65: 16}
            drop_count = rain_intensity.get(weather_code, 8)
            
            for i in range(drop_count):
                drop_x = center - 18 + i * 3
                drop_y = center + 2 + (i % 4) * 4
                drop_size = 3 + (i % 3)  # Varying drop sizes
                self.draw_realistic_raindrop(draw, drop_x, drop_y, drop_size, (80, 120, 180))
        
        elif weather_code in [71, 73, 75]:  # Snow - Beautiful crystalline design
            # Soft snow cloud
            self.draw_professional_cloud(draw, center, center-8, 0.9, (230, 230, 230))
            
            # Detailed snowflakes with crystalline structure
            snow_intensity = {71: 8, 73: 12, 75: 18}
            flake_count = snow_intensity.get(weather_code, 8)
            
            for i in range(flake_count):
                flake_x = center - 16 + (i % 5) * 6
                flake_y = center + 4 + (i // 5) * 8
                self.draw_crystalline_snowflake(draw, flake_x, flake_y, 3 + (i % 2))
        
        elif weather_code in [80, 81]:  # Showers - Dynamic storm design
            # Dark, dramatic shower cloud
            self.draw_professional_cloud(draw, center, center-10, 1.1, (80, 80, 80))
            
            # Heavy shower drops with splash effect
            shower_intensity = {80: 10, 81: 14}
            drop_count = shower_intensity.get(weather_code, 10)
            
            for i in range(drop_count):
                drop_x = center - 20 + i * 3.5
                drop_y = center + (i % 5) * 4
                # Larger, more dramatic drops
                self.draw_shower_drop(draw, drop_x, drop_y, 4 + (i % 2), (40, 100, 160))
        
        elif weather_code == 95:  # Thunderstorm - Epic storm design
            # Massive, dark storm cloud
            self.draw_professional_cloud(draw, center, center-10, 1.3, (60, 60, 60))
            
            # Dramatic lightning with realistic branching
            self.draw_realistic_lightning(draw, center-8, center+5, (255, 255, 100))
            self.draw_realistic_lightning(draw, center+12, center+8, (255, 255, 150))
            
            # Torrential rain
            for i in range(12):
                drop_x = center - 22 + i * 3.5
                drop_y = center + 5 + (i % 4) * 3
                self.draw_realistic_raindrop(draw, drop_x, drop_y, 4, (60, 100, 140))
        
        else:  # Default/Unknown weather - Stylized question mark
            # Elegant unknown weather indicator
            draw.ellipse([center-20, center-20, center+20, center+20], 
                        fill=(150, 150, 150), outline=(100, 100, 100), width=3)
            
            # Stylized question mark
            question_font_size = size // 3
            if question_font_size > 0:
                # Draw question mark manually for consistency
                # Question mark curve
                draw.arc([center-8, center-12, center+8, center-4], 
                        start=0, end=180, fill=(255, 255, 255), width=4)
                # Question mark stem
                draw.line([(center, center-4), (center, center+2)], 
                         fill=(255, 255, 255), width=4)
                # Question mark dot
                draw.ellipse([center-2, center+6, center+2, center+10], 
                           fill=(255, 255, 255))
        
        return icon
    
    def draw_professional_cloud(self, draw, center_x, center_y, scale, base_color):
        """Draw a professional, volumetric cloud with realistic shading."""
        # Cloud shadow layer for depth
        shadow_parts = [
            (center_x-18*scale, center_y+2, 14*scale), 
            (center_x-5*scale, center_y-8*scale, 18*scale),
            (center_x+8*scale, center_y-3*scale, 16*scale), 
            (center_x+20*scale, center_y+1, 14*scale),
            (center_x+10*scale, center_y+10*scale, 13*scale), 
            (center_x-8*scale, center_y+8*scale, 12*scale)
        ]
        
        shadow_color = tuple(max(0, int(c * 0.7)) for c in base_color)
        for cx, cy, radius in shadow_parts:
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=shadow_color)
        
        # Main cloud body
        main_parts = [
            (center_x-16*scale, center_y, 13*scale), 
            (center_x-3*scale, center_y-10*scale, 17*scale),
            (center_x+10*scale, center_y-5*scale, 15*scale), 
            (center_x+18*scale, center_y-1, 13*scale),
            (center_x+8*scale, center_y+8*scale, 12*scale), 
            (center_x-6*scale, center_y+6*scale, 11*scale)
        ]
        
        for cx, cy, radius in main_parts:
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=base_color)
        
        # Highlight layer for volume
        highlight_color = tuple(min(255, int(c * 1.3)) for c in base_color)
        highlight_parts = [
            (center_x-14*scale, center_y-2, 10*scale), 
            (center_x-1*scale, center_y-12*scale, 14*scale),
            (center_x+12*scale, center_y-7*scale, 12*scale), 
            (center_x+16*scale, center_y-3, 10*scale)
        ]
        
        for cx, cy, radius in highlight_parts:
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=highlight_color)
    
    def draw_realistic_raindrop(self, draw, x, y, size, color):
        """Draw a realistic water drop with proper teardrop shape."""
        # Main drop body (ellipse)
        draw.ellipse([x-size//2, y, x+size//2, y+size*2], fill=color)
        # Teardrop top (triangle)
        points = [(x, y), (x-size//2, y+size//2), (x+size//2, y+size//2)]
        draw.polygon(points, fill=color)
        # Highlight for realism
        highlight_color = tuple(min(255, int(c * 1.4)) for c in color)
        draw.ellipse([x-1, y+1, x+1, y+3], fill=highlight_color)
    
    def draw_shower_drop(self, draw, x, y, size, color):
        """Draw a heavy shower drop with splash effect."""
        # Main large drop
        self.draw_realistic_raindrop(draw, x, y, size, color)
        # Small splash drops around it
        for i, (dx, dy) in enumerate([(2, 3), (-2, 3), (0, 5)]):
            if i < size - 2:  # More splash for larger drops
                splash_x, splash_y = x + dx, y + dy * 2
                draw.ellipse([splash_x-1, splash_y, splash_x+1, splash_y+2], 
                           fill=tuple(int(c * 0.8) for c in color))
    
    def draw_crystalline_snowflake(self, draw, x, y, size):
        """Draw a detailed, crystalline snowflake."""
        # Main cross arms
        arm_length = size + 2
        draw.line([(x-arm_length, y), (x+arm_length, y)], fill=(255, 255, 255), width=2)
        draw.line([(x, y-arm_length), (x, y+arm_length)], fill=(255, 255, 255), width=2)
        
        # Diagonal arms
        diag_length = int(arm_length * 0.7)
        draw.line([(x-diag_length, y-diag_length), (x+diag_length, y+diag_length)], 
                 fill=(255, 255, 255), width=1)
        draw.line([(x-diag_length, y+diag_length), (x+diag_length, y-diag_length)], 
                 fill=(255, 255, 255), width=1)
        
        # Crystalline details on each arm
        for arm_x, arm_y in [(x-arm_length//2, y), (x+arm_length//2, y), 
                            (x, y-arm_length//2), (x, y+arm_length//2)]:
            # Small branch details
            draw.line([(arm_x-2, arm_y-1), (arm_x+2, arm_y+1)], fill=(240, 240, 255), width=1)
            draw.line([(arm_x-2, arm_y+1), (arm_x+2, arm_y-1)], fill=(240, 240, 255), width=1)
        
        # Central hexagonal core
        draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 255))
        draw.ellipse([x-1, y-1, x+1, y+1], fill=(240, 248, 255))
    
    def draw_realistic_lightning(self, draw, start_x, start_y, color):
        """Draw realistic lightning with branching and glow effect."""
        # Main lightning bolt with natural jagged path
        bolt_points = [
            (start_x, start_y),
            (start_x - 4, start_y + 8),
            (start_x + 2, start_y + 12),
            (start_x - 6, start_y + 20),
            (start_x + 4, start_y + 25),
            (start_x - 2, start_y + 32)
        ]
        
        # Draw main bolt with glow effect (multiple passes)
        for width, glow_color in [(8, (255, 255, 100, 50)), (5, (255, 255, 150, 80)), (2, color)]:
            for i in range(len(bolt_points) - 1):
                draw.line([bolt_points[i], bolt_points[i + 1]], 
                         fill=glow_color[:3], width=width)
        
        # Add small branching bolts for realism
        for i, (x, y) in enumerate(bolt_points[1:-1], 1):
            if i % 2 == 0:  # Every other point gets a branch
                # Small branch
                branch_end = (x + (-1)**i * 6, y + 4)
                for width, branch_color in [(4, (255, 255, 150, 60)), (1, color)]:
                    draw.line([(x, y), branch_end], fill=branch_color[:3], width=width)
    
    def draw_enhanced_water_drop(self, draw, x, y, color, size=8):
        """Draw a premium water drop icon with gradient and shine."""
        # Main drop shape with gradient effect
        # Shadow base
        draw.ellipse([x+1, y+4, x+size+1, y+size+4], fill=(100, 100, 100))
        
        # Main drop body
        drop_points = [
            (x + size//2, y),  # Top point
            (x, y + size//2),  # Left curve
            (x + size//4, y + size),  # Bottom left
            (x + 3*size//4, y + size),  # Bottom right  
            (x + size, y + size//2)  # Right curve
        ]
        draw.polygon(drop_points, fill=color)
        
        # Gradient effect with multiple layers
        for i in range(3):
            offset = i + 1
            lighter_color = tuple(min(255, int(c * (1 + i * 0.1))) for c in color)
            inner_points = [
                (x + size//2, y + offset),
                (x + offset, y + size//2),
                (x + size//4 + offset, y + size - offset),
                (x + 3*size//4 - offset, y + size - offset),
                (x + size - offset, y + size//2)
            ]
            draw.polygon(inner_points, fill=lighter_color)
        
        # Shine highlight
        draw.ellipse([x + size//3, y + size//4, x + size//3 + 2, y + size//4 + 2], 
                    fill=(255, 255, 255))
    
    def draw_enhanced_wind_arrow(self, draw, x, y, color, size=16):
        """Draw a sophisticated wind arrow with motion lines."""
        # Main arrow shaft with gradient
        shaft_width = 3
        # Arrow shaft shadow
        draw.line([(x, y+4), (x+size-4, y+4)], fill=(100, 100, 100), width=shaft_width+1)
        # Main arrow shaft
        draw.line([(x, y+3), (x+size-4, y+3)], fill=color, width=shaft_width)
        
        # Enhanced arrowhead with volume
        arrow_points = [
            (x+size-4, y),  # Top point
            (x+size, y+3),  # Arrow tip
            (x+size-4, y+6)  # Bottom point
        ]
        # Arrowhead shadow
        shadow_points = [(px+1, py+1) for px, py in arrow_points]
        draw.polygon(shadow_points, fill=(100, 100, 100))
        # Main arrowhead
        draw.polygon(arrow_points, fill=color)
        
        # Wind flow lines with varying lengths and curves
        flow_lines = [
            {"start": (x+size+4, y), "end": (x+size+10, y), "width": 2},
            {"start": (x+size+4, y+2), "end": (x+size+14, y+2), "width": 2},
            {"start": (x+size+4, y+4), "end": (x+size+12, y+4), "width": 2},
            {"start": (x+size+4, y+6), "end": (x+size+10, y+6), "width": 2}
        ]
        
        for i, line in enumerate(flow_lines):
            # Varying opacity for motion effect
            alpha = max(100, 255 - i * 30)
            line_color = (*color[:3], alpha) if len(color) > 3 else color
            draw.line([line["start"], line["end"]], fill=line_color[:3], width=line["width"])
            
            # Add subtle curves to suggest air flow
            mid_x = (line["start"][0] + line["end"][0]) // 2
            mid_y = line["start"][1] + math.sin(i) * 1
            draw.line([line["start"], (mid_x, mid_y)], fill=line_color[:3], width=line["width"])
            draw.line([(mid_x, mid_y), line["end"]], fill=line_color[:3], width=line["width"])
    
    def draw_enhanced_clock_icon(self, draw, x, y, color, size=10):
        """Draw a detailed clock icon with depth and style."""
        center_x, center_y = x + size//2, y + size//2
        radius = size//2
        
        # Clock shadow
        draw.ellipse([x+1, y+1, x+size+1, y+size+1], fill=(100, 100, 100))
        
        # Outer clock rim
        draw.ellipse([x, y, x+size, y+size], fill=(200, 200, 200))
        
        # Inner clock face
        draw.ellipse([x+1, y+1, x+size-1, y+size-1], fill=(240, 240, 240))
        
        # Clock numbers (simplified as dots)
        for hour in range(0, 12, 3):  # 12, 3, 6, 9 o'clock positions
            angle = math.radians(hour * 30 - 90)  # Start from 12 o'clock
            dot_x = center_x + (radius - 2) * math.cos(angle)
            dot_y = center_y + (radius - 2) * math.sin(angle)
            draw.ellipse([dot_x-1, dot_y-1, dot_x+1, dot_y+1], fill=color)
        
        # Clock hands
        # Hour hand (pointing to ~2 o'clock)
        hour_angle = math.radians(60 - 90)  # 2 o'clock position
        hour_x = center_x + (radius - 3) * 0.6 * math.cos(hour_angle)
        hour_y = center_y + (radius - 3) * 0.6 * math.sin(hour_angle)
        draw.line([(center_x, center_y), (hour_x, hour_y)], fill=color, width=2)
        
        # Minute hand (pointing to ~10 minutes)
        minute_angle = math.radians(60 - 90)  # 10 minutes position
        minute_x = center_x + (radius - 2) * 0.8 * math.cos(minute_angle)
        minute_y = center_y + (radius - 2) * 0.8 * math.sin(minute_angle)
        draw.line([(center_x, center_y), (minute_x, minute_y)], fill=color, width=1)
        
        # Center dot
        draw.ellipse([center_x-1, center_y-1, center_x+1, center_y+1], fill=color)
    
    def display(self):
        """Display weather with rich visuals and large text."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Weather screen...")
        
        try:
            # Fetch weather data
            weather_data = self.fetch_weather_data()
            self.current_weather = weather_data
            
            current = weather_data["current"]
            weather_code = current["weathercode"]
            
            # Load enhanced fonts with larger sizes using font utilities
            fonts = get_weather_fonts()
            font_header = fonts['header']   # 32pt title font
            font_temp = fonts['temp']       # 56pt bold font
            font_large = fonts['large']     # 22pt bold font
            font_medium = fonts['medium']   # 18pt regular font
            font_small = fonts['small']     # 15pt small font
            
            # Create rich weather background
            display_image, theme = self.create_weather_background(weather_code)
            draw = ImageDraw.Draw(display_image)
            
            # Header with location
            header_text = f"WEATHER - {self.city_name.upper()}"
            if font_header:
                # Text shadow for better visibility
                draw.text((42, 22), header_text, fill=(0, 0, 0, 100), font=font_header)
                draw.text((40, 20), header_text, fill=theme["accent"], font=font_header)
            
            # Main temperature - very large and prominent
            current_temp = int(current["temperature"])
            temp_text = f"{current_temp}°"
            if font_temp:
                # Position temperature prominently
                temp_x, temp_y = 60, 70
                # Shadow effect
                draw.text((temp_x + 3, temp_y + 3), temp_text, fill=(0, 0, 0, 120), font=font_temp)
                # Main temperature
                draw.text((temp_x, temp_y), temp_text, fill=theme["text_color"], font=font_temp)
            
            # Weather description - larger and clearer with shadow
            weather_desc = self.weather_descriptions.get(weather_code, "Unknown")
            if font_large:
                # Add shadow for better visibility
                draw.text((61, 141), weather_desc, fill=(0, 0, 0, 100), font=font_large)
                draw.text((60, 140), weather_desc, fill=theme["text_color"], font=font_large)
            
            # Enhanced large weather icon
            weather_icon = self.create_weather_icon_large(weather_code, 90)  # Larger icon
            display_image.paste(weather_icon, (420, 55), weather_icon)
            
            # Current conditions with enhanced layout and larger text
            conditions_y = 175
            humidity = current.get("humidity", 28)
            wind_speed = current.get("windspeed", 0)
            
            if font_large:  # Use larger font for conditions
                # Create enhanced condition indicators with better spacing
                # Enhanced humidity with premium water drop icon
                self.draw_enhanced_water_drop(draw, 35, conditions_y + 5, 
                                            tuple(int(c * 0.8) for c in theme["text_color"]), 10)
                humidity_text = f"Humidity: {humidity}%"
                draw.text((51, conditions_y + 1), humidity_text, fill=(0, 0, 0, 100), font=font_medium)
                draw.text((50, conditions_y), humidity_text, fill=theme["text_color"], font=font_medium)
                
                # Enhanced wind with sophisticated arrow icon
                self.draw_enhanced_wind_arrow(draw, 32, conditions_y + 28, 
                                            tuple(int(c * 0.8) for c in theme["text_color"]), 12)
                wind_text = f"Wind: {wind_speed:.1f} mph"
                draw.text((51, conditions_y + 26), wind_text, fill=(0, 0, 0, 100), font=font_medium)
                draw.text((50, conditions_y + 25), wind_text, fill=theme["text_color"], font=font_medium)
                
                # Enhanced time with detailed clock icon
                current_time = datetime.now().strftime("%I:%M %p")
                self.draw_enhanced_clock_icon(draw, 35, conditions_y + 53, 
                                            tuple(int(c * 0.8) for c in theme["text_color"]), 12)
                time_text = f"Updated: {current_time}"
                draw.text((51, conditions_y + 51), time_text, fill=(0, 0, 0, 100), font=font_small)
                draw.text((50, conditions_y + 50), time_text, fill=theme["text_color"], font=font_small)
            
            # Enhanced 5-Day forecast with better justified layout
            forecast_y = 250
            if font_large:
                draw.text((40, forecast_y), "5-DAY FORECAST", fill=theme["text_color"], font=font_large)
            
            daily = weather_data["daily"]
            
            # Calculate perfect spacing to fill screen width
            total_width = 640 - 80  # Screen width minus left/right margins (40 each)
            num_cards = min(5, len(daily["time"]))
            card_width = 100  # Slightly smaller cards
            total_card_width = num_cards * card_width
            total_spacing = total_width - total_card_width
            card_spacing = total_spacing / (num_cards - 1) if num_cards > 1 else 0
            
            for i in range(num_cards):
                # Precisely calculated positions for perfect justification
                card_x = int(40 + i * (card_width + card_spacing))
                card_y = forecast_y + 40
                
                # Enhanced forecast card with gradient effect
                card_overlay = Image.new("RGBA", (card_width, 90), (0, 0, 0, 0))
                card_draw = ImageDraw.Draw(card_overlay)
                
                # Create gradient card background
                for y in range(90):
                    alpha = int(60 + (y / 90) * 40)  # Gradient alpha from 60 to 100
                    card_draw.line([(0, y), (card_width, y)], fill=(*theme["accent"], alpha))
                
                # Add subtle border
                card_draw.rectangle([0, 0, card_width-1, 89], outline=(*theme["text_color"], 150), width=2)
                display_image.paste(card_overlay, (card_x, card_y), card_overlay)
                
                # Day label - larger text
                try:
                    date_obj = datetime.strptime(daily["time"][i], "%Y-%m-%d")
                    if i == 0:
                        day_text = "TODAY"
                    elif i == 1:
                        day_text = "TMRW"  # Shorter to fit better
                    else:
                        day_text = date_obj.strftime("%a").upper()
                except:
                    day_text = f"DAY {i+1}"
                
                if font_medium:  # Use larger font for day labels
                    bbox = draw.textbbox((0, 0), day_text, font=font_medium)
                    text_width = bbox[2] - bbox[0]
                    text_x = card_x + (card_width - text_width) // 2
                    draw.text((text_x, card_y + 5), day_text, fill=theme["text_color"], font=font_medium)
                
                # Enhanced weather icon for forecast
                forecast_code = daily["weathercode"][i]
                mini_icon = self.create_weather_icon_large(forecast_code, 35)  # Slightly larger icons
                icon_x = card_x + (card_width - 35) // 2
                display_image.paste(mini_icon, (icon_x, card_y + 28), mini_icon)
                
                # Temperatures with better layout
                high_temp = int(daily["temperature_2m_max"][i])
                low_temp = int(daily["temperature_2m_min"][i])
                
                if font_medium:
                    # High temp - larger and more prominent
                    high_text = f"{high_temp}°"
                    bbox = draw.textbbox((0, 0), high_text, font=font_medium)
                    text_width = bbox[2] - bbox[0]
                    text_x = card_x + (card_width - text_width) // 2
                    # Add shadow for high temp
                    draw.text((text_x + 1, card_y + 66), high_text, fill=(0, 0, 0, 100), font=font_medium)
                    draw.text((text_x, card_y + 65), high_text, fill=theme["text_color"], font=font_medium)
                    
                    # Low temp positioned better
                    low_text = f"{low_temp}°"
                    bbox = draw.textbbox((0, 0), low_text, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    low_x = card_x + card_width - text_width - 8  # Right-aligned within card
                    draw.text((low_x, card_y + 8), low_text, fill=(120, 120, 120), font=font_small)
            
            # Ensure final image is in correct format for e-ink display
            if display_image.mode != 'RGB':
                display_image = display_image.convert('RGB')
            
            # Display the weather
            self.inky.set_image(display_image)
            self.inky.show()
            
            print(f"Displayed weather: {current_temp}°F, {weather_desc}")
            
        except Exception as e:
            print(f"Error displaying weather: {e}")
            self.display_error_message("Weather Error", str(e))
    
    def display_error_message(self, title, message):
        """Display an error message with weather theme."""
        image = Image.new("RGB", (640, 400), (70, 130, 180))
        draw = ImageDraw.Draw(image)
        
        try:
            from font_utils import get_font
            font = get_font('regular', 16)
        except:
            font = None
            
        if font:
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 180), title, fill=(255, 255, 255), font=font)
            
            if len(message) > 50:
                message = message[:47] + "..."
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 210), message, fill=(200, 200, 200), font=font)
        
        # Ensure final image is in correct format for e-ink display
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        self.inky.set_image(image)
        self.inky.show()
