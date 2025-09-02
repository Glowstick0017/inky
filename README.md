# Inky Impression 4 Dashboard

An interactive 4-screen dashboard system for the Pimoroni Inky Impression 4" e-ink display. Switch between different information screens using the hardware buttons.

**Optimized for Raspberry Pi Zero 2 W** - Minimal resource usage, efficient code, small memory footprint.

## Screens

**Button A: Artwork + Quotes**
- Beautiful artwork paired with inspiring quotes
- Rotating artwork from multiple sources (Unsplash, Wikimedia)
- Elegant quote overlay with large, readable typography
- Updates every 5 minutes with fresh content

**Button B: Weather Forecast**
- Rich, colorful weather display with theme-based backgrounds
- Current conditions and 5-day forecast for Phoenix, AZ
- Comprehensive weather icons for all conditions
- Updates every 15 minutes using Open-Meteo API

**Button C: Star Chart**
- Interactive night sky view with constellations and planets
- Real-time astronomy data for current viewing conditions
- Major constellations with connecting lines and labels
- Visible planets with distinctive markers and labels
- Updates every 30 minutes

**Button D: System Dashboard**
- Real-time Raspberry Pi system monitoring
- CPU usage, memory, temperature, disk space
- Network statistics and process count
- Color-coded metrics with progress bars
- Updates every 60 seconds

## Requirements

- Raspberry Pi Zero 2 W (or any Pi with GPIO support)
- Pimoroni Inky Impression 4" (640x400, 7-color)
- Hardware buttons connected to GPIO pins (configurable in config.py)

## Quick Start

1. Install dependencies:
   ```bash
   pip3 install requests Pillow psutil
   ```

2. Configure your location and preferences in `config.py`:
   ```python
   # Location Configuration
   LOCATION_LATITUDE = 33.4484    # Your latitude
   LOCATION_LONGITUDE = -112.0740 # Your longitude
   LOCATION_CITY = "Your City"    # Your city name
   
   # Update intervals (seconds)
   ARTWORK_UPDATE_INTERVAL = 300    # 5 minutes
   WEATHER_UPDATE_INTERVAL = 900    # 15 minutes  
   STARMAP_UPDATE_INTERVAL = 3600   # 1 hour
   SYSTEM_UPDATE_INTERVAL = 60      # 1 minute
   ```

3. Run the dashboard:
   ```bash
   python3 main.py
   ```

4. Use buttons A, B, C, D to switch between screens.

## Configuration

Edit locations in `config.py`:

- **Weather Location**: Change coordinates for your city
- **News Sources**: Modify RSS feeds for different regions
- **Update Intervals**: Modify refresh rates for each screen

## Project Structure

```
impression4_dashboard/
├── main.py                    # Main dashboard controller
├── config.py                  # All configuration settings
├── requirements.txt           # Minimal dependencies  
├── test_setup.py              # Setup verification
└── screens/                   # Screen implementations
    ├── base_screen.py         # Base screen class
    ├── artwork_screen.py      # Classical artwork with quotes
    ├── starmap_screen.py      # Night sky star chart
    ├── system_screen.py       # System monitoring dashboard
    └── weather_screen.py      # Weather forecast
```

## Performance

Optimized for Raspberry Pi Zero 2 W:
- Minimal memory usage (reduced image sizes, smaller caches)
- Efficient API calls (fewer requests, smart caching)
- Simple threading model
- No unnecessary dependencies

## API Sources

- **Artwork**: Metropolitan Museum of Art (free, no key required)
- **Weather**: Open-Meteo (free, no key required)
- **Quotes**: Multiple free quote APIs (no key required)
- **News**: RSS feeds from local sources + Google News (no key required)
