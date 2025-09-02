#!/usr/bin/env python3
"""
Simple performance monitor for Pi Zero 2 W
Shows memory and CPU usage while dashboard runs
"""

import psutil
import time
import sys

def monitor_performance():
    """Monitor system performance optimized for Pi Zero 2 W."""
    print("Performance Monitor for Pi Zero 2 W")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        while True:
            # Get system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Get temperature (Pi-specific)
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = int(f.read()) / 1000.0
            except:
                temp = 0
            
            # Display compact stats
            print(f"\rCPU: {cpu_percent:4.1f}% | RAM: {memory.percent:4.1f}% ({memory.used//1024//1024}MB) | Temp: {temp:.1f}°C", end="")
            sys.stdout.flush()
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    monitor_performance()
