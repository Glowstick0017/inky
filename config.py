"""
Configuration file for Inky Impression 4 Dashboard
Modify these settings to customize your dashboard
"""

# API Configuration
NEWS_API_KEY = "YOUR_NEWS_API_KEY_HERE"  # Get free key from https://newsapi.org
NEWS_LOCATION_QUERY = 'Phoenix Arizona OR "Phoenix AZ" OR "Arizona Cardinals" OR "Sky Harbor"'

# Weather Configuration  
WEATHER_LATITUDE = 33.4484     # Phoenix latitude
WEATHER_LONGITUDE = -112.0740  # Phoenix longitude
WEATHER_CITY_NAME = "Phoenix, AZ"

# Update Intervals (in seconds)
ARTWORK_UPDATE_INTERVAL = 300    # 5 minutes
QUOTES_UPDATE_INTERVAL = 3600    # 1 hour  
NEWS_UPDATE_INTERVAL = 1800      # 30 minutes
WEATHER_UPDATE_INTERVAL = 900    # 15 minutes

# Display Configuration
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 400

# Button GPIO Pins
BUTTON_PINS = {
    'A': 5,   # Artwork
    'B': 6,   # Quotes
    'C': 16,  # News
    'D': 24   # Weather
}

# Default startup screen
DEFAULT_SCREEN = 'A'  # Start with artwork

# Font Preferences (if you have custom fonts installed)
FONT_PATHS = {
    'header': None,    # Use default
    'large': None,     # Use default
    'medium': None,    # Use default
    'small': None      # Use default
}

# Color Preferences (for styling)
COLORS = {
    'background': (255, 255, 255),      # White
    'text_primary': (0, 0, 0),          # Black
    'text_secondary': (100, 100, 100),  # Gray
    'accent': (0, 50, 100),             # Dark blue
    'error': (200, 0, 0)                # Red
}
