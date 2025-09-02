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
        """Create rich, colorful weather-themed background."""
        # Get theme with intelligent fallback
        theme = self.get_weather_theme(weather_code)
        
        image = Image.new("RGB", (640, 400), theme["gradient"][0])
        draw = ImageDraw.Draw(image)
        
        # Create rich gradient background
        for y in range(400):
            ratio = y / 400
            if ratio < 0.33:
                # Top third
                blend_ratio = ratio * 3
                r = int(theme["gradient"][0][0] * (1 - blend_ratio) + theme["gradient"][1][0] * blend_ratio)
                g = int(theme["gradient"][0][1] * (1 - blend_ratio) + theme["gradient"][1][1] * blend_ratio)
                b = int(theme["gradient"][0][2] * (1 - blend_ratio) + theme["gradient"][1][2] * blend_ratio)
            elif ratio < 0.66:
                # Middle third
                blend_ratio = (ratio - 0.33) * 3
                r = int(theme["gradient"][1][0] * (1 - blend_ratio) + theme["gradient"][2][0] * blend_ratio)
                g = int(theme["gradient"][1][1] * (1 - blend_ratio) + theme["gradient"][2][1] * blend_ratio)
                b = int(theme["gradient"][1][2] * (1 - blend_ratio) + theme["gradient"][2][2] * blend_ratio)
            else:
                # Bottom third - stay at final color
                r, g, b = theme["gradient"][2]
            
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Add weather-specific visual elements
        self.add_weather_visuals(draw, weather_code, theme)
        
        return image, theme
    
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
        """Create large, detailed weather icons for all weather conditions."""
        icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        center = size // 2
        
        if weather_code in [0, 1]:  # Sunny/Clear
            # Large sun with rays
            draw.ellipse([center-20, center-20, center+20, center+20], fill=(255, 215, 0))
            draw.ellipse([center-15, center-15, center+15, center+15], fill=(255, 255, 0))
            draw.ellipse([center-8, center-8, center+8, center+8], fill=(255, 255, 200))
            # Sun rays
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = center + 25 * math.cos(rad)
                y1 = center + 25 * math.sin(rad)
                x2 = center + 35 * math.cos(rad)
                y2 = center + 35 * math.sin(rad)
                draw.line([(x1, y1), (x2, y2)], fill=(255, 215, 0), width=3)
        
        elif weather_code in [2, 3]:  # Partly cloudy/Overcast
            if weather_code == 2:  # Partly cloudy - sun behind cloud
                # Small sun
                draw.ellipse([center-25, center-20, center-5, center], fill=(255, 215, 0))
                # Sun rays (partial)
                for angle in range(180, 360, 30):
                    rad = math.radians(angle)
                    x1 = center-15 + 15 * math.cos(rad)
                    y1 = center-10 + 15 * math.sin(rad)
                    x2 = center-15 + 25 * math.cos(rad)
                    y2 = center-10 + 25 * math.sin(rad)
                    draw.line([(x1, y1), (x2, y2)], fill=(255, 215, 0), width=2)
            
            # Cloud
            draw.ellipse([center-20, center-5, center+10, center+15], fill=(169, 169, 169))
            draw.ellipse([center-10, center-15, center+20, center+5], fill=(192, 192, 192))
            draw.ellipse([center-5, center-10, center+25, center+10], fill=(169, 169, 169))
        
        elif weather_code in [45, 48]:  # Fog
            # Horizontal fog lines
            for y_offset in range(-15, 20, 6):
                draw.ellipse([center-20, center+y_offset-2, center+20, center+y_offset+2], 
                           fill=(176, 196, 222))
        
        elif weather_code in [51, 53, 55]:  # Drizzle
            # Small cloud
            draw.ellipse([center-15, center-20, center+15, center-5], fill=(169, 169, 169))
            # Light drizzle drops
            for i in range(2):
                x = center - 8 + i * 8
                draw.line([(x, center), (x, center+12)], fill=(135, 206, 235), width=2)
        
        elif weather_code in [61, 63, 65]:  # Rain
            # Cloud
            draw.ellipse([center-18, center-20, center+18, center-5], fill=(105, 105, 105))
            # Rain drops with varying intensity
            drop_count = 3 if weather_code == 61 else 4 if weather_code == 63 else 5
            for i in range(drop_count):
                x = center - 12 + i * 6
                drop_length = 12 if weather_code == 61 else 15 if weather_code == 63 else 18
                draw.line([(x, center), (x, center+drop_length)], fill=(0, 100, 200), width=3)
        
        elif weather_code in [71, 73, 75]:  # Snow
            # Snow cloud
            draw.ellipse([center-18, center-20, center+18, center-5], fill=(220, 220, 220))
            # Snowflakes
            flake_count = 3 if weather_code == 71 else 4 if weather_code == 73 else 6
            for i in range(flake_count):
                x = center - 12 + i * 5
                y = center + 2 + (i % 2) * 8
                self.draw_mini_snowflake(draw, x, y)
        
        elif weather_code in [80, 81]:  # Showers
            # Dark cloud
            draw.ellipse([center-18, center-20, center+18, center-5], fill=(105, 105, 105))
            # Heavy shower drops
            drop_count = 4 if weather_code == 80 else 5
            for i in range(drop_count):
                x = center - 10 + i * 5
                draw.ellipse([x-1, center+2+i*3, x+1, center+16+i*3], fill=(30, 144, 255))
        
        elif weather_code == 95:  # Thunderstorm
            # Dark storm cloud
            draw.ellipse([center-20, center-20, center+20, center-5], fill=(75, 75, 75))
            # Lightning bolt
            points = [(center-3, center), (center-8, center+8), (center, center+10), 
                     (center-5, center+18)]
            for i in range(len(points)-1):
                draw.line([points[i], points[i+1]], fill=(255, 255, 0), width=3)
            # Rain
            for i in range(3):
                x = center - 6 + i * 6
                draw.line([(x, center+5), (x, center+15)], fill=(0, 100, 200), width=2)
        
        else:  # Default/Unknown weather
            # Generic cloud
            draw.ellipse([center-15, center-10, center+15, center+10], fill=(169, 169, 169))
            draw.text((center-5, center-5), "?", fill=(255, 255, 255))
        
        return icon
    
    def draw_mini_snowflake(self, draw, x, y):
        """Draw a small snowflake for icons."""
        # Simple snowflake
        draw.line([(x-3, y), (x+3, y)], fill=(255, 255, 255), width=1)
        draw.line([(x, y-3), (x, y+3)], fill=(255, 255, 255), width=1)
        draw.line([(x-2, y-2), (x+2, y+2)], fill=(255, 255, 255), width=1)
        draw.line([(x-2, y+2), (x+2, y-2)], fill=(255, 255, 255), width=1)
    
    def draw_water_drop(self, draw, x, y, color):
        """Draw a simple water drop icon."""
        # Water drop shape
        draw.ellipse([x, y+3, x+6, y+9], fill=color)
        draw.polygon([(x+3, y), (x+1, y+5), (x+5, y+5)], fill=color)
    
    def draw_wind_arrow(self, draw, x, y, color):
        """Draw a simple wind arrow icon."""
        # Horizontal arrow with wind lines
        draw.line([(x, y+3), (x+8, y+3)], fill=color, width=2)
        draw.line([(x+6, y+1), (x+8, y+3), (x+6, y+5)], fill=color, width=2)
        # Wind lines
        draw.line([(x+10, y+1), (x+14, y+1)], fill=color, width=1)
        draw.line([(x+10, y+3), (x+16, y+3)], fill=color, width=1)
        draw.line([(x+10, y+5), (x+14, y+5)], fill=color, width=1)
    
    def draw_clock_icon(self, draw, x, y, color):
        """Draw a simple clock icon."""
        # Clock circle
        draw.ellipse([x, y, x+8, y+8], outline=color, width=1)
        # Clock hands
        draw.line([(x+4, y+4), (x+4, y+2)], fill=color, width=1)  # Hour hand
        draw.line([(x+4, y+4), (x+6, y+4)], fill=color, width=1)  # Minute hand
    
    def display(self):
        """Display weather with rich visuals and large text."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Weather screen...")
        
        try:
            # Fetch weather data
            weather_data = self.fetch_weather_data()
            self.current_weather = weather_data
            
            current = weather_data["current"]
            weather_code = current["weathercode"]
            
            # Create rich weather background
            display_image, theme = self.create_weather_background(weather_code)
            draw = ImageDraw.Draw(display_image)
            
            # Load large fonts
            try:
                font_header = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 28)
                font_temp = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 48)  # Very large temp
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 20)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 14)
            except:
                try:
                    font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
                    font_temp = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
                    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                except:
                    font_header = font_temp = font_large = font_medium = font_small = ImageFont.load_default()
            
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
            
            # Weather description - large and clear
            weather_desc = self.weather_descriptions.get(weather_code, "Unknown")
            if font_large:
                draw.text((60, 140), weather_desc, fill=theme["text_color"], font=font_large)
            
            # Large weather icon
            weather_icon = self.create_weather_icon_large(weather_code, 80)
            display_image.paste(weather_icon, (420, 60), weather_icon)
            
            # Current conditions with larger text and colorful icons
            conditions_y = 180
            humidity = current.get("humidity", 28)
            wind_speed = current.get("windspeed", 0)
            
            if font_medium:
                # Create colorful condition indicators with simple icons
                # Draw humidity icon (water drop shape)
                self.draw_water_drop(draw, 40, conditions_y + 5, theme["text_color"])
                draw.text((60, conditions_y), f"Humidity: {humidity}%", fill=theme["text_color"], font=font_medium)
                
                # Draw wind icon (arrow shape)
                self.draw_wind_arrow(draw, 40, conditions_y + 30, theme["text_color"])
                draw.text((60, conditions_y + 25), f"Wind: {wind_speed} mph", fill=theme["text_color"], font=font_medium)
                
                # Draw clock icon (circle with hands)
                self.draw_clock_icon(draw, 40, conditions_y + 55, theme["text_color"])
                current_time = datetime.now().strftime("%I:%M %p")
                draw.text((60, conditions_y + 50), f"Updated: {current_time}", fill=theme["text_color"], font=font_medium)
            
            # 5-Day forecast with larger cards
            forecast_y = 260
            if font_large:
                draw.text((40, forecast_y), "5-DAY FORECAST", fill=theme["text_color"], font=font_large)
            
            daily = weather_data["daily"]
            card_width = 110
            card_spacing = 10
            
            for i in range(min(5, len(daily["time"]))):
                card_x = 40 + i * (card_width + card_spacing)
                card_y = forecast_y + 35
                
                if card_x + card_width > 600:
                    break
                
                # Create semi-transparent forecast card
                card_overlay = Image.new("RGBA", (card_width, 80), (*theme["accent"], 80))
                display_image.paste(card_overlay, (card_x, card_y), card_overlay)
                
                # Day label
                try:
                    date_obj = datetime.strptime(daily["time"][i], "%Y-%m-%d")
                    if i == 0:
                        day_text = "TODAY"
                    elif i == 1:
                        day_text = "TOMORROW"
                    else:
                        day_text = date_obj.strftime("%a").upper()
                except:
                    day_text = f"DAY {i+1}"
                
                if font_small:
                    bbox = draw.textbbox((0, 0), day_text, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    text_x = card_x + (card_width - text_width) // 2
                    draw.text((text_x, card_y + 8), day_text, fill=theme["text_color"], font=font_small)
                
                # Weather icon for forecast
                forecast_code = daily["weathercode"][i]
                mini_icon = self.create_weather_icon_large(forecast_code, 30)
                icon_x = card_x + (card_width - 30) // 2
                display_image.paste(mini_icon, (icon_x, card_y + 25), mini_icon)
                
                # Temperatures
                high_temp = int(daily["temperature_2m_max"][i])
                low_temp = int(daily["temperature_2m_min"][i])
                
                if font_medium:
                    # High temp
                    high_text = f"{high_temp}°"
                    bbox = draw.textbbox((0, 0), high_text, font=font_medium)
                    text_width = bbox[2] - bbox[0]
                    text_x = card_x + (card_width - text_width) // 2
                    draw.text((text_x, card_y + 57), high_text, fill=theme["text_color"], font=font_medium)
                    
                    # Low temp (smaller)
                    low_text = f"{low_temp}°"
                    bbox = draw.textbbox((0, 0), low_text, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    text_x = card_x + (card_width - text_width) // 2
                    draw.text((text_x + 30, card_y + 60), low_text, fill=(100, 100, 100), font=font_small)
            
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
            font = ImageFont.load_default()
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
        
        self.inky.set_image(image)
        self.inky.show()
