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
            
            # Rainy - deep blue theme
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
    
    def create_weather_background(self, weather_code):
        """Create rich, colorful weather-themed background."""
        # Get theme or default to clear sky
        theme = self.weather_themes.get(weather_code, self.weather_themes[0])
        
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
            # Sun body
            draw.ellipse([sun_x-30, sun_y-30, sun_x+30, sun_y+30], fill=(255, 215, 0))
            draw.ellipse([sun_x-25, sun_y-25, sun_x+25, sun_y+25], fill=(255, 255, 0))
            
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
            # Multiple detailed clouds
            cloud_positions = [(120, 60), (350, 80), (520, 70)]
            for x, y in cloud_positions:
                self.draw_detailed_cloud(draw, x, y, pattern_color)
        
        elif weather_code in [61, 63, 65]:  # Rain
            # Rain clouds with droplets
            self.draw_detailed_cloud(draw, 300, 60, (169, 169, 169))
            
            # Animated-style rain drops
            import random
            random.seed(42)  # Consistent pattern
            for _ in range(40):
                x = random.randint(50, 590)
                y = random.randint(120, 350)
                # Rain drop shape
                draw.ellipse([x-2, y, x+2, y+12], fill=(135, 206, 235))
                draw.ellipse([x-1, y+10, x+1, y+14], fill=(100, 149, 237))
        
        elif weather_code == 95:  # Thunderstorm
            # Dramatic storm clouds
            self.draw_detailed_cloud(draw, 200, 50, (105, 105, 105))
            self.draw_detailed_cloud(draw, 400, 70, (105, 105, 105))
            
            # Lightning bolts
            self.draw_lightning_bolt(draw, 250, 120, pattern_color)
            self.draw_lightning_bolt(draw, 450, 140, pattern_color)
    
    def draw_detailed_cloud(self, draw, x, y, color):
        """Draw a detailed, fluffy cloud."""
        # Multiple overlapping circles for realistic cloud shape
        cloud_parts = [
            (x-20, y+5, 18), (x-5, y-5, 22), (x+10, y, 20),
            (x+25, y+3, 18), (x+15, y+15, 16), (x-10, y+12, 15)
        ]
        
        for cx, cy, radius in cloud_parts:
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], fill=color)
            # Add subtle highlight
            draw.ellipse([cx-radius+3, cy-radius+2, cx+radius-3, cy+radius-8], 
                        fill=(min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20)))
    
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
        """Create large, detailed weather icons."""
        icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        center = size // 2
        
        if weather_code in [0, 1]:  # Sunny
            # Large sun
            draw.ellipse([center-20, center-20, center+20, center+20], fill=(255, 215, 0))
            draw.ellipse([center-15, center-15, center+15, center+15], fill=(255, 255, 0))
            # Sun rays
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = center + 25 * math.cos(rad)
                y1 = center + 25 * math.sin(rad)
                x2 = center + 35 * math.cos(rad)
                y2 = center + 35 * math.sin(rad)
                draw.line([(x1, y1), (x2, y2)], fill=(255, 215, 0), width=4)
        
        elif weather_code in [2, 3]:  # Cloudy
            # Detailed cloud
            draw.ellipse([center-25, center-5, center+5, center+15], fill=(169, 169, 169))
            draw.ellipse([center-15, center-15, center+15, center+5], fill=(192, 192, 192))
            draw.ellipse([center-5, center-10, center+25, center+10], fill=(169, 169, 169))
        
        elif weather_code in [61, 63, 65]:  # Rain
            # Cloud with rain
            draw.ellipse([center-20, center-20, center+20, center-5], fill=(105, 105, 105))
            # Rain drops
            for i in range(3):
                x = center - 10 + i * 10
                draw.line([(x, center), (x, center+15)], fill=(0, 100, 200), width=3)
        
        return icon
    
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
            header_text = f"⛅ {self.city_name.upper()}"
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
                # Create colorful condition indicators
                draw.text((60, conditions_y), f"💧 Humidity: {humidity}%", fill=theme["text_color"], font=font_medium)
                draw.text((60, conditions_y + 25), f"💨 Wind: {wind_speed} mph", fill=theme["text_color"], font=font_medium)
                current_time = datetime.now().strftime("%I:%M %p")
                draw.text((60, conditions_y + 50), f"🕒 Updated: {current_time}", fill=theme["text_color"], font=font_medium)
            
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
