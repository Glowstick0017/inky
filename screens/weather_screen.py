"""
Weather Forecast Screen
Displays beautiful weather forecast for Phoenix, Arizona
Updates every 15 minutes with current conditions and 5-day forecast
"""

import requests
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
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
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy", 
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        # Simple weather icons using text characters
        self.weather_icons = {
            0: "☀️",    # Clear sky
            1: "🌤️",    # Mainly clear
            2: "⛅",    # Partly cloudy
            3: "☁️",    # Overcast
            45: "🌫️",   # Fog
            48: "🌫️",   # Depositing rime fog
            51: "🌦️",   # Light drizzle
            53: "🌦️",   # Moderate drizzle
            55: "🌧️",   # Dense drizzle
            61: "🌧️",   # Slight rain
            63: "🌧️",   # Moderate rain
            65: "⛈️",   # Heavy rain
            71: "🌨️",   # Slight snow
            73: "❄️",   # Moderate snow
            75: "❄️",   # Heavy snow
            80: "🌦️",   # Rain showers
            81: "🌦️",   # Moderate rain showers
            82: "⛈️",   # Violent rain showers
            95: "⛈️",   # Thunderstorm
            96: "⛈️",   # Thunderstorm with hail
            99: "⛈️"    # Thunderstorm with heavy hail
        }
        
        # Fallback weather data
        self.fallback_weather = {
            "current": {
                "temperature": 85,
                "humidity": 35,
                "windspeed": 8,
                "weathercode": 0,
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
                'latitude': self.latitude,
                'longitude': self.longitude,
                'current_weather': 'true',
                'daily': 'temperature_2m_max,temperature_2m_min,weathercode',
                'temperature_unit': 'fahrenheit',
                'windspeed_unit': 'mph',
                'timezone': 'America/Phoenix',
                'forecast_days': 5
            }
            
            response = requests.get(self.current_weather_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract current weather
                current = data.get('current_weather', {})
                daily = data.get('daily', {})
                
                weather_data = {
                    "current": {
                        "temperature": current.get('temperature', 0),
                        "windspeed": current.get('windspeed', 0),
                        "weathercode": current.get('weathercode', 0),
                        "time": current.get('time', datetime.now().isoformat())
                    },
                    "daily": daily
                }
                
                return weather_data
                
        except Exception as e:
            print(f"Error fetching weather data: {e}")
        
        # Return fallback data if API fails
        return self.fallback_weather
    
    def get_weather_icon(self, weather_code):
        """Get weather icon character for given weather code."""
        return self.weather_icons.get(weather_code, "🌡️")
    
    def get_weather_description(self, weather_code):
        """Get weather description for given weather code."""
        return self.weather_descriptions.get(weather_code, "Unknown")
    
    def draw_weather_icon_art(self, draw, x, y, weather_code, size=40):
        """Draw a simple ASCII art weather representation."""
        icon_char = self.get_weather_icon(weather_code)
        
        # For clear/sunny weather, draw a simple sun
        if weather_code in [0, 1]:
            # Sun circle
            draw.ellipse([x, y, x+size, y+size], outline=(255, 200, 0), width=3)
            # Sun rays
            ray_length = 15
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                import math
                rad = math.radians(angle)
                start_x = x + size//2 + int((size//2 + 5) * math.cos(rad))
                start_y = y + size//2 + int((size//2 + 5) * math.sin(rad))
                end_x = start_x + int(ray_length * math.cos(rad))
                end_y = start_y + int(ray_length * math.sin(rad))
                draw.line([start_x, start_y, end_x, end_y], fill=(255, 200, 0), width=2)
        
        # For cloudy weather, draw clouds
        elif weather_code in [2, 3]:
            # Simple cloud shapes
            draw.ellipse([x, y+10, x+15, y+25], fill=(180, 180, 180))
            draw.ellipse([x+10, y+5, x+30, y+25], fill=(160, 160, 160))
            draw.ellipse([x+20, y+10, x+35, y+25], fill=(180, 180, 180))
        
        # For rainy weather, draw rain drops
        elif weather_code in [61, 63, 65, 80, 81, 82]:
            # Cloud
            draw.ellipse([x, y, x+30, y+20], fill=(120, 120, 120))
            # Rain drops
            for i in range(4):
                drop_x = x + 5 + i * 6
                drop_y = y + 25
                draw.line([drop_x, drop_y, drop_x, drop_y+10], fill=(0, 100, 200), width=2)
    
    def display(self):
        """Display the weather forecast."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Weather screen...")
        
        try:
            # Fetch weather data
            weather_data = self.fetch_weather_data()
            self.current_weather = weather_data
            
            # Create display image
            image = Image.new("RGB", (self.inky.width, self.inky.height), (240, 248, 255))  # Light blue background
            draw = ImageDraw.Draw(image)
            
            # Load fonts
            try:
                font_header = ImageFont.load_default()
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            except:
                font_header = None
                font_large = None
                font_medium = None
                font_small = None
            
            # Draw header
            header_text = f"Weather - {self.city_name}"
            if font_header:
                bbox = draw.textbbox((0, 0), header_text, font=font_header)
                text_width = bbox[2] - bbox[0]
                x = (self.inky.width - text_width) // 2
                draw.text((x, 10), header_text, fill=(25, 25, 112), font=font_header)
            
            # Current weather section
            current = weather_data["current"]
            current_temp = int(current["temperature"])
            weather_code = current["weathercode"]
            wind_speed = current["windspeed"]
            
            # Draw current temperature (large)
            temp_text = f"{current_temp}°F"
            if font_large:
                bbox = draw.textbbox((0, 0), temp_text, font=font_large)
                text_width = bbox[2] - bbox[0]
                x = 50
                draw.text((x, 50), temp_text, fill=(25, 25, 112), font=font_large)
            
            # Weather icon art
            self.draw_weather_icon_art(draw, 180, 45, weather_code, 50)
            
            # Current conditions
            description = self.get_weather_description(weather_code)
            if font_medium:
                draw.text((50, 85), description, fill=(60, 60, 60), font=font_medium)
                draw.text((50, 105), f"Wind: {wind_speed} mph", fill=(60, 60, 60), font=font_medium)
            
            # Separator line
            draw.line([20, 130, self.inky.width - 20, 130], fill=(100, 100, 100), width=2)
            
            # 5-day forecast
            if font_medium:
                draw.text((20, 140), "5-Day Forecast", fill=(25, 25, 112), font=font_medium)
            
            daily = weather_data["daily"]
            forecast_start_y = 165
            
            for i in range(min(5, len(daily["time"]))):
                y_pos = forecast_start_y + (i * 35)
                
                if y_pos > self.inky.height - 40:
                    break
                
                # Date
                try:
                    date_obj = datetime.strptime(daily["time"][i], "%Y-%m-%d")
                    if i == 0:
                        day_text = "Today"
                    elif i == 1:
                        day_text = "Tomorrow"
                    else:
                        day_text = date_obj.strftime("%a")
                except:
                    day_text = f"Day {i+1}"
                
                if font_small:
                    draw.text((20, y_pos), day_text, fill=(60, 60, 60), font=font_small)
                
                # Weather icon (small)
                forecast_weather_code = daily["weathercode"][i]
                icon_char = self.get_weather_icon(forecast_weather_code)
                if font_medium:
                    draw.text((80, y_pos-2), icon_char, fill=(25, 25, 112), font=font_medium)
                
                # High/Low temperatures
                high_temp = int(daily["temperature_2m_max"][i])
                low_temp = int(daily["temperature_2m_min"][i])
                temp_text = f"{high_temp}°/{low_temp}°"
                
                if font_small:
                    bbox = draw.textbbox((0, 0), temp_text, font=font_small)
                    text_width = bbox[2] - bbox[0]
                    x = self.inky.width - text_width - 20
                    draw.text((x, y_pos), temp_text, fill=(25, 25, 112), font=font_small)
                
                # Condition description (abbreviated)
                condition = self.get_weather_description(forecast_weather_code)
                if len(condition) > 15:
                    condition = condition[:12] + "..."
                
                if font_small:
                    draw.text((120, y_pos), condition, fill=(100, 100, 100), font=font_small)
            
            # Footer with update time
            now = datetime.now()
            footer_text = f"Updated: {now.strftime('%m/%d %H:%M')}"
            if font_small:
                bbox = draw.textbbox((0, 0), footer_text, font=font_small)
                text_width = bbox[2] - bbox[0]
                x = self.inky.width - text_width - 10
                draw.text((x, self.inky.height - 15), footer_text, fill=(120, 120, 120), font=font_small)
            
            # Weather service attribution
            if font_small:
                draw.text((10, self.inky.height - 15), "Data: Open-Meteo", fill=(120, 120, 120), font=font_small)
            
            # Convert to Inky's palette and display
            self.inky.set_image(image)
            self.inky.show()
            
            print(f"Displayed weather: {current_temp}°F, {description}")
            
        except Exception as e:
            print(f"Error displaying weather: {e}")
            self.display_error_message("Weather Error", str(e))
    
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
