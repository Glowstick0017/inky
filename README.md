# Inky Impression 4 Dashboard

An interactive 4-screen dashboard system for the Pimoroni Inky Impression 4" e-ink display. Switch between different information screens using the hardware buttons.

**Optimized for Raspberry Pi Zero 2 W** - Minimal resource usage, efficient code, small memory footprint.

## Screens

**Button A: Classical Artwork**
- Rotating classical artwork from the Metropolitan Museum of Art
- Updates every 5 minutes
- Displays artwork title, artist, and date

**Button B: Daily Quotes**
- Daily inspirational quotes with decorative styling
- Updates every hour
- Multiple API sources with fallback content

**Button C: Phoenix Arizona News**
- Local news headlines from Phoenix area using RSS feeds
- Updates every 30 minutes
- No API key required - uses Google News and local RSS feeds

**Button D: Weather Forecast**
- Current weather and 5-day forecast for Phoenix, AZ
- Updates every 15 minutes
- Uses Open-Meteo API (no key required)

## Requirements

- Raspberry Pi Zero 2 W (or any Pi with GPIO support)
- Pimoroni Inky Impression 4" (640x400, 7-color)
- Hardware buttons connected to GPIO pins (configurable in config.py)

## Quick Start

1. Install minimal dependencies:
   ```bash
   pip3 install requests Pillow
   ```

2. Configure your location in `config.py`

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
├── monitor.py                 # Performance monitoring for Pi Zero 2 W
├── test_setup.py              # Setup verification
└── screens/                   # Screen implementations
    ├── base_screen.py         # Base screen class
    ├── artwork_screen.py      # Classical artwork
    ├── quotes_screen.py       # Daily quotes
    ├── news_screen.py         # Local news (RSS feeds)
    └── weather_screen.py      # Weather forecast
```

## Performance

Optimized for Raspberry Pi Zero 2 W:
- Minimal memory usage (reduced image sizes, smaller caches)
- Efficient API calls (fewer requests, smart caching)
- Simple threading model
- No unnecessary dependencies

Monitor performance: `python3 monitor.py`

## API Sources

- **Artwork**: Metropolitan Museum of Art (free, no key required)
- **Weather**: Open-Meteo (free, no key required)
- **Quotes**: Multiple free quote APIs (no key required)
- **News**: RSS feeds from local sources + Google News (no key required)
