"""
Configuration file for Inky Impression 4 Dashboard
4-Screen System: Artwork+Quotes, Weather, Star Chart, System Monitor
Modify these settings to customize your dashboard
"""

# Weather Configuration  
WEATHER_LATITUDE = 33.4484     # Phoenix latitude
WEATHER_LONGITUDE = -112.0740  # Phoenix longitude
WEATHER_CITY_NAME = "Phoenix, AZ"

# Location Configuration (used by Star Chart and Weather)
LOCATION_LATITUDE = 33.4484    # Your location latitude
LOCATION_LONGITUDE = -112.0740 # Your location longitude
LOCATION_CITY = "Phoenix, AZ"  # Your city name

# Update Intervals (in seconds)
ARTWORK_UPDATE_INTERVAL = 1800    # 30 minutes - Artwork with quotes
WEATHER_UPDATE_INTERVAL = 900    # 15 minutes - Weather forecast
STARMAP_UPDATE_INTERVAL = 3600   # 1 hour - Star chart
SYSTEM_UPDATE_INTERVAL = 300     # 5 minutes - System monitoring

# Display Configuration
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 400

# Button GPIO Pins - Updated for 4-screen layout
BUTTON_PINS = {
    'A': 5,   # Artwork + Quotes
    'B': 6,   # Weather
    'C': 16,  # Star Chart  
    'D': 24   # System Monitor
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
    'error': (200, 0, 0),               # Red
    'success': (0, 150, 0),             # Green
    'warning': (255, 165, 0),           # Orange
    'critical': (255, 0, 0)             # Red
}

# System Monitor Thresholds
SYSTEM_THRESHOLDS = {
    'cpu_warning': 75,      # CPU usage warning threshold (%)
    'cpu_critical': 90,     # CPU usage critical threshold (%)
    'memory_warning': 80,   # Memory usage warning threshold (%)
    'memory_critical': 95,  # Memory usage critical threshold (%)
    'temp_warning': 65,     # Temperature warning threshold (°C)
    'temp_critical': 80,    # Temperature critical threshold (°C)
    'disk_warning': 85,     # Disk usage warning threshold (%)
    'disk_critical': 95     # Disk usage critical threshold (%)
}
