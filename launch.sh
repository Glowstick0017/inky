#!/bin/bash
# Simple launcher for Inky Impression 4 Dashboard
# Optimized for Raspberry Pi Zero 2 W

echo "Starting Inky Dashboard (optimized for Pi Zero 2 W)..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Run from dashboard directory."
    exit 1
fi

# Simple dependency check
python3 -c "import requests, PIL" 2>/dev/null || {
    echo "Installing minimal dependencies..."
    pip3 install requests Pillow
}

# Start the dashboard with reduced output for Pi Zero
echo "Launching dashboard..."
python3 main.py

echo "Dashboard stopped."
