#!/usr/bin/env python3
"""
Inky Impression 4 Dashboard
A 4-screen dashboard system controlled by the 4 buttons:
- Button A: Classical Artwork (rotates every 5 minutes)
- Button B: Daily Quotes with art
- Button C: Phoenix Arizona News
- Button D: Weather Forecast

Each button switches to its respective screen and starts its update cycle.
"""

import gpiod
import gpiodevice
import threading
import time
import sys
import os
from datetime import datetime, timedelta
from gpiod.line import Bias, Direction, Edge

# Import our screen modules
try:
    import config  # Import configuration
    from screens.artwork_screen import ArtworkScreen
    from screens.quotes_screen import QuotesScreen
    from screens.news_screen import NewsScreen
    from screens.weather_screen import WeatherScreen
except ImportError as e:
    print(f"Error importing screen modules: {e}")
    print("Make sure you're running from the dashboard directory")
    sys.exit(1)

# GPIO pins for each button (from config)
BUTTONS = [config.BUTTON_PINS['A'], config.BUTTON_PINS['B'], 
           config.BUTTON_PINS['C'], config.BUTTON_PINS['D']]
LABELS = ["A", "B", "C", "D"]

class InkyDashboard:
    def __init__(self):
        self.current_screen = None
        self.screen_thread = None
        self.stop_event = threading.Event()
        
        # Initialize screens
        self.screens = {
            "A": ArtworkScreen(),
            "B": QuotesScreen(), 
            "C": NewsScreen(),
            "D": WeatherScreen()
        }
        
        # Setup GPIO for buttons
        self.setup_buttons()
        
        # Start with artwork screen by default
        self.switch_screen(config.DEFAULT_SCREEN)
    
    def setup_buttons(self):
        """Setup GPIO buttons for screen switching."""
        INPUT = gpiod.LineSettings(
            direction=Direction.INPUT, 
            bias=Bias.PULL_UP, 
            edge_detection=Edge.FALLING
        )
        
        chip = gpiodevice.find_chip_by_platform()
        self.offsets = [chip.line_offset_from_id(id) for id in BUTTONS]
        line_config = dict.fromkeys(self.offsets, INPUT)
        self.request = chip.request_lines(consumer="inky4-dashboard", config=line_config)
    
    def handle_button(self, event):
        """Handle button press events."""
        try:
            index = self.offsets.index(event.line_offset)
            gpio_number = BUTTONS[index]
            label = LABELS[index]
            
            print(f"Button {label} pressed (GPIO #{gpio_number})")
            self.switch_screen(label)
            
        except ValueError:
            print(f"Unknown button pressed: {event.line_offset}")
    
    def switch_screen(self, screen_label):
        """Switch to a different screen and start its update cycle."""
        if self.current_screen == screen_label:
            return
            
        print(f"Switching to screen {screen_label}...")
        
        # Stop current screen thread
        if self.screen_thread and self.screen_thread.is_alive():
            self.stop_event.set()
            self.screen_thread.join(timeout=2.0)
            
        # Clear stop event for new screen
        self.stop_event.clear()
        
        # Add a small delay to ensure display is ready
        time.sleep(0.1)
        
        # Start new screen
        self.current_screen = screen_label
        screen = self.screens[screen_label]
        
        # Run initial display immediately
        screen.display()
        
        # Start background update thread for the screen
        self.screen_thread = threading.Thread(
            target=self.run_screen_loop, 
            args=(screen,)
        )
        self.screen_thread.daemon = True
        self.screen_thread.start()
    
    def run_screen_loop(self, screen):
        """Run the update loop for a screen."""
        while not self.stop_event.is_set():
            try:
                # Wait for the screen's update interval
                if self.stop_event.wait(screen.update_interval):
                    break  # Stop event was set
                    
                # Update the screen
                screen.display()
                
            except Exception as e:
                print(f"Error in screen loop: {e}")
                # Wait a bit before retrying
                if self.stop_event.wait(30):
                    break
    
    def run(self):
        """Main loop to handle button presses."""
        print("Inky Impression 4 Dashboard started!")
        print("Press buttons A, B, C, or D to switch screens")
        print("Current screen: Artwork (A)")
        print("Press Ctrl+C to exit")
        
        try:
            while True:
                for event in self.request.read_edge_events():
                    self.handle_button(event)
                    
        except KeyboardInterrupt:
            print("\nShutting down dashboard...")
            self.stop_event.set()
            if self.screen_thread and self.screen_thread.is_alive():
                self.screen_thread.join(timeout=2.0)
            
            # Don't clear the screen - keep last display visible
            print("Dashboard stopped. Screen will retain last display.")

if __name__ == "__main__":
    try:
        dashboard = InkyDashboard()
        dashboard.run()
    except Exception as e:
        print(f"Failed to start dashboard: {e}")
        # Don't clear the screen on error - keep display as is
        sys.exit(1)
