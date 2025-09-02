"""
Weather Forecast Screen - App-Like Design with Dynamic Backgrounds
Displays beautiful weather forecast for Phoenix, Arizona with weather-themed backgrounds
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
        
        # Weather API endpoints (using Open-Meteo - free, no API key required)
        self.current_weather_url = "https://api.open-meteo.com/v1/forecast"
        
        # Weather code mappings for Open-Meteo
        self.weather_descriptions = {
            0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing Rime Fog", 51: "Light Drizzle", 53: "Moderate Drizzle",
            55: "Dense Drizzle", 56: "Light Freezing Drizzle", 57: "Dense Freezing Drizzle",
            61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain", 66: "Light Freezing Rain",
            67: "Heavy Freezing Rain", 71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
            77: "Snow Grains", 80: "Slight Rain Showers", 81: "Moderate Rain Showers",
            82: "Violent Rain Showers", 85: "Slight Snow Showers", 86: "Heavy Snow Showers",
            95: "Thunderstorm", 96: "Thunderstorm with Slight Hail", 99: "Thunderstorm with Heavy Hail"
        }
        
        # Weather background themes with colors and patterns
        self.weather_themes = {
            # Clear and sunny
            0: {"gradient": [(255, 215, 0), (255, 165, 0), (255, 140, 0)], "pattern": "sun_rays"},
            1: {"gradient": [(255, 228, 181), (255, 215, 0), (255, 185, 15)], "pattern": "scattered_clouds"},
            
            # Cloudy
            2: {"gradient": [(200, 230, 255), (150, 190, 230), (120, 160, 200)], "pattern": "puffy_clouds"},
            3: {"gradient": [(140, 140, 140), (100, 100, 100), (80, 80, 80)], "pattern": "overcast"},
            
            # Fog
            45: {"gradient": [(230, 230, 230), (200, 200, 200), (170, 170, 170)], "pattern": "fog_wisps"},
            48: {"gradient": [(230, 230, 230), (200, 200, 200), (170, 170, 170)], "pattern": "fog_wisps"},
            
            # Rain
            61: {"gradient": [(100, 149, 237), (70, 130, 180), (25, 25, 112)], "pattern": "rain_drops"},
            63: {"gradient": [(70, 130, 180), (25, 25, 112), (0, 0, 139)], "pattern": "heavy_rain"},
            65: {"gradient": [(25, 25, 112), (0, 0, 139), (0, 0, 80)], "pattern": "downpour"},
            
            # Thunderstorms
            95: {"gradient": [(75, 0, 130), (25, 25, 112), (0, 0, 0)], "pattern": "lightning"},
            96: {"gradient": [(75, 0, 130), (25, 25, 112), (0, 0, 0)], "pattern": "lightning"},
            99: {"gradient": [(75, 0, 130), (25, 25, 112), (0, 0, 0)], "pattern": "lightning"},
            
            # Snow (rare in Phoenix but included)
            71: {"gradient": [(230, 230, 250), (176, 196, 222), (135, 206, 235)], "pattern": "snowflakes"},
            73: {"gradient": [(176, 196, 222), (135, 206, 235), (70, 130, 180)], "pattern": "snowflakes"},
            75: {"gradient": [(135, 206, 235), (70, 130, 180), (25, 25, 112)], "pattern": "snowflakes"}
        }
        
        # Fallback weather data for Phoenix
        self.fallback_weather = {
            "current": {
                "temperature": 85, "humidity": 35, "windspeed": 8, "weathercode": 0,
                "time": datetime.now().isoformat()
            },
            "daily": {
                "time": [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)],
                "temperature_2m_max": [89, 92, 86, 83, 87],
                "temperature_2m_min": [65, 68, 63, 61, 66],
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
                
                # Get humidity from hourly data (first value)
                humidity = 35  # Default for Phoenix
                if 'hourly' in data and 'relative_humidity_2m' in data['hourly']:
                    humidity = data['hourly']['relative_humidity_2m'][0] or 35
                
                weather_data = {
                    "current": {
                        "temperature": current.get('temperature', 85),
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
    
    def create_weather_background(self, weather_code):
        """Create a dynamic weather-themed background."""
        image = Image.new("RGB", (640, 400), (135, 206, 235))  # Default sky blue
        draw = ImageDraw.Draw(image)
        
        # Get theme for weather code, default to clear sky
        theme = self.weather_themes.get(weather_code, self.weather_themes[0])
        gradient_colors = theme["gradient"]
        pattern = theme["pattern"]
        
        # Create gradient background
        for y in range(400):
            # Interpolate between gradient colors
            ratio = y / 400
            if ratio < 0.5:
                # Top half: first to second color
                blend_ratio = ratio * 2
                r = int(gradient_colors[0][0] * (1 - blend_ratio) + gradient_colors[1][0] * blend_ratio)
                g = int(gradient_colors[0][1] * (1 - blend_ratio) + gradient_colors[1][1] * blend_ratio)
                b = int(gradient_colors[0][2] * (1 - blend_ratio) + gradient_colors[1][2] * blend_ratio)
            else:
                # Bottom half: second to third color
                blend_ratio = (ratio - 0.5) * 2
                r = int(gradient_colors[1][0] * (1 - blend_ratio) + gradient_colors[2][0] * blend_ratio)
                g = int(gradient_colors[1][1] * (1 - blend_ratio) + gradient_colors[2][1] * blend_ratio)
                b = int(gradient_colors[1][2] * (1 - blend_ratio) + gradient_colors[2][2] * blend_ratio)
            
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Add weather pattern overlays
        self.add_weather_pattern(draw, pattern, weather_code)
        
        return image
    
    def add_weather_pattern(self, draw, pattern, weather_code):
        """Add weather-specific pattern overlays."""
        if pattern == "sun_rays":
            # Draw sun rays radiating from top-right
            center_x, center_y = 520, 80
            for angle in range(0, 360, 15):
                rad = math.radians(angle)
                x1 = center_x + 40 * math.cos(rad)
                y1 = center_y + 40 * math.sin(rad)
                x2 = center_x + 80 * math.cos(rad)
                y2 = center_y + 80 * math.sin(rad)
                draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 200, 120), width=3)
        
        elif pattern == "puffy_clouds":
            # Draw fluffy cloud shapes
            cloud_positions = [(100, 50), (300, 80), (500, 60)]
            for x, y in cloud_positions:
                self.draw_cloud(draw, x, y, size=60, opacity=180)
        
        elif pattern == "rain_drops":
            # Draw rain drops
            import random
            random.seed(42)  # Consistent pattern
            for _ in range(30):
                x = random.randint(0, 640)
                y = random.randint(100, 400)
                draw.line([(x, y), (x + 3, y + 15)], fill=(200, 200, 255), width=2)
        
        elif pattern == "lightning":
            # Draw stylized lightning bolts
            self.draw_lightning(draw, 200, 50)
            self.draw_lightning(draw, 450, 120)
        
        elif pattern == "snowflakes":
            # Draw snowflakes (if ever needed in Phoenix!)
            import random
            random.seed(42)
            for _ in range(20):
                x = random.randint(0, 640)
                y = random.randint(0, 300)
                self.draw_snowflake(draw, x, y)
    
    def draw_cloud(self, draw, x, y, size=40, opacity=200):
        """Draw a fluffy cloud."""
        # Multiple overlapping circles for cloud effect
        cloud_color = (255, 255, 255, opacity)
        for i, (offset_x, offset_y, radius) in enumerate([(0, 5, size//2), (size//3, 0, size//2.5), 
                                                          (size//1.5, 3, size//2.2), (-size//4, 2, size//3)]):
            draw.ellipse([x + offset_x - radius, y + offset_y - radius, 
                         x + offset_x + radius, y + offset_y + radius], 
                        fill=(255, 255, 255))
    
    def draw_lightning(self, draw, start_x, start_y):
        """Draw a stylized lightning bolt."""
        points = [
            (start_x, start_y), (start_x - 10, start_y + 30), (start_x + 5, start_y + 35),
            (start_x - 15, start_y + 70), (start_x + 10, start_y + 75), (start_x - 5, start_y + 110)
        ]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=(255, 255, 0), width=4)
    
    def draw_snowflake(self, draw, x, y):
        """Draw a simple snowflake."""
        size = 8
        # Six-pointed star
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            end_x = x + size * math.cos(rad)
            end_y = y + size * math.sin(rad)
            draw.line([(x, y), (end_x, end_y)], fill=(255, 255, 255), width=2)
    
    def create_glass_panel(self, width, height):
        """Create a translucent glass-like panel for app overlay."""
        panel = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(panel)
        
        # Glass background with gradient
        for y in range(height):
            alpha = int(120 - (y / height) * 40)  # Fade from top to bottom
            draw.line([(0, y), (width, y)], fill=(255, 255, 255, alpha))
        
        # Glass border
        draw.rectangle([(0, 0), (width-1, height-1)], outline=(255, 255, 255, 150), width=2)
        
        return panel
    
    def get_weather_icon_modern(self, weather_code, size=40):
        """Create modern weather icons using geometric shapes."""
        icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Clear/sunny
        if weather_code in [0, 1]:
            # Modern sun with rays
            center = size // 2
            draw.ellipse([center-12, center-12, center+12, center+12], fill=(255, 215, 0))
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = center + 16 * math.cos(rad)
                y1 = center + 16 * math.sin(rad)
                x2 = center + 20 * math.cos(rad)
                y2 = center + 20 * math.sin(rad)
                draw.line([(x1, y1), (x2, y2)], fill=(255, 215, 0), width=3)
        
        # Cloudy
        elif weather_code in [2, 3]:
            # Modern cloud shape
            draw.ellipse([5, 15, 25, 30], fill=(160, 160, 160))
            draw.ellipse([15, 10, 35, 25], fill=(140, 140, 140))
            draw.ellipse([25, 15, 40, 30], fill=(160, 160, 160))
        
        # Rainy
        elif weather_code in [61, 63, 65]:
            # Cloud with rain
            draw.ellipse([8, 5, 32, 20], fill=(120, 120, 120))
            # Rain drops
            for i in range(3):
                x = 12 + i * 8
                draw.line([(x, 25), (x, 35)], fill=(0, 100, 200), width=3)
        
        return icon
    
    def display(self):
        """Display weather with app-like interface and dynamic backgrounds."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Weather screen...")
        
        try:
            # Fetch weather data
            weather_data = self.fetch_weather_data()
            self.current_weather = weather_data
            
            current = weather_data["current"]
            weather_code = current["weathercode"]
            
            # Create dynamic weather background
            display_image = self.create_weather_background(weather_code)
            
            # Create glass panel overlay for app-like appearance
            glass_panel = self.create_glass_panel(580, 350)
            display_image.paste(glass_panel, (30, 25), glass_panel)
            
            draw = ImageDraw.Draw(display_image)
            
            # Load fonts
            try:
                font_header = ImageFont.load_default()
                font_large = ImageFont.load_default()  
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            except:
                font_header = font_large = font_medium = font_small = None
            
            # App-style header with location
            header_text = f"📍 {self.city_name.upper()}"
            if font_header:
                draw.text((50, 40), header_text, fill=(40, 40, 40), font=font_header)
            
            # Main weather display - Current conditions
            current_temp = int(current["temperature"])
            weather_desc = self.weather_descriptions.get(weather_code, "Unknown")
            
            # Large temperature display
            temp_text = f"{current_temp}°"
            if font_large:
                # Bold effect for temperature
                for offset in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                    draw.text((50 + offset[0], 80 + offset[1]), temp_text, fill=(20, 20, 20), font=font_large)
            
            # Weather description
            if font_medium:
                draw.text((50, 120), weather_desc, fill=(60, 60, 60), font=font_medium)
            
            # Modern weather icon
            weather_icon = self.get_weather_icon_modern(weather_code, 80)
            display_image.paste(weather_icon, (450, 70), weather_icon)
            
            # Current conditions panel
            conditions_y = 160
            humidity = current.get("humidity", 35)
            wind_speed = current.get("windspeed", 0)
            
            if font_small:
                # Humidity with icon
                draw.text((50, conditions_y), f"💧 {humidity}%", fill=(60, 60, 60), font=font_small)
                # Wind with icon  
                draw.text((150, conditions_y), f"💨 {wind_speed} mph", fill=(60, 60, 60), font=font_small)
                # Time
                current_time = datetime.now().strftime("%I:%M %p")
                draw.text((300, conditions_y), f"🕒 {current_time}", fill=(60, 60, 60), font=font_small)
            
            # 5-Day forecast in card style
            forecast_y = 200
            if font_medium:
                draw.text((50, forecast_y), "5-DAY FORECAST", fill=(40, 40, 40), font=font_medium)
            
            daily = weather_data["daily"]
            card_width = 100
            card_height = 120
            
            for i in range(min(5, len(daily["time"]))):
                card_x = 50 + i * (card_width + 10)
                card_y = forecast_y + 25
                
                if card_x + card_width > 590:  # Don't exceed panel bounds
                    break
                
                # Create mini glass card for each day
                mini_card = self.create_glass_panel(card_width, card_height)
                display_image.paste(mini_card, (card_x, card_y), mini_card)
                
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
                    draw.text((text_x, card_y + 10), day_text, fill=(40, 40, 40), font=font_small)
                
                # Mini weather icon
                forecast_code = daily["weathercode"][i]
                mini_icon = self.get_weather_icon_modern(forecast_code, 30)
                icon_x = card_x + (card_width - 30) // 2
                display_image.paste(mini_icon, (icon_x, card_y + 30), mini_icon)
                
                # High/Low temperatures
                high_temp = int(daily["temperature_2m_max"][i])
                low_temp = int(daily["temperature_2m_min"][i])
                
                if font_small:
                    # High temp (bold)
                    high_text = f"{high_temp}°"
                    bbox = draw.textbbox((0, 0), high_text, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    text_x = card_x + (card_width - text_width) // 2
                    # Bold effect
                    for offset in [(0, 0), (1, 0)]:
                        draw.text((text_x + offset[0], card_y + 70 + offset[1]), high_text, fill=(20, 20, 20), font=font_small)
                    
                    # Low temp (gray)
                    low_text = f"{low_temp}°"
                    bbox = draw.textbbox((0, 0), low_text, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    text_x = card_x + (card_width - text_width) // 2
                    draw.text((text_x, card_y + 90), low_text, fill=(100, 100, 100), font=font_small)
            
            # Footer with update time and data source
            footer_y = 380
            if font_small:
                update_time = datetime.now().strftime("Updated %I:%M %p")
                draw.text((50, footer_y), update_time, fill=(120, 120, 120), font=font_small)
                draw.text((300, footer_y), "Data: Open-Meteo", fill=(120, 120, 120), font=font_small)
            
            # Display the weather
            self.inky.set_image(display_image)
            self.inky.show()
            
            print(f"Displayed weather: {current_temp}°F, {weather_desc}")
            
        except Exception as e:
            print(f"Error displaying weather: {e}")
            self.display_error_message("Weather Error", str(e))
    
    def display_error_message(self, title, message):
        """Display an error message with weather theme."""
        image = Image.new("RGB", (640, 400), (100, 149, 237))  # Sky blue
        draw = ImageDraw.Draw(image)
        
        # Glass panel for error
        glass_panel = self.create_glass_panel(400, 200)
        image.paste(glass_panel, (120, 100), glass_panel)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        if font:
            # Draw error title
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 180), title, fill=(200, 50, 50), font=font)
            
            # Draw error message
            if len(message) > 50:
                message = message[:47] + "..."
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 210), message, fill=(80, 80, 80), font=font)
        
        self.inky.set_image(image)
        self.inky.show()
