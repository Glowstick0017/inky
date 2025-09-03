"""
Modern System Dashboard Screen - Advanced Raspberry Pi Monitoring
Displays comprehensive system metrics with sleek modern design:
- Real-time CPU, Memory, Temperature, and Disk monitoring
- Network activity and system load visualization
- Running services and process information
- System health indicators with color-coded status
- Performance history graphs and trend analysis
Optimized for 640x400 e-ink display with modern card-based layout
Updates every 30 seconds with comprehensive system telemetry
"""

import os
import psutil
import subprocess
import time
import socket
import platform
from datetime import datetime, timedelta
from collections import deque
from PIL import Image, ImageDraw, ImageFont
from .base_screen import BaseScreen
import config
from font_utils import get_system_fonts, get_font

class SystemScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.SYSTEM_UPDATE_INTERVAL if hasattr(config, 'SYSTEM_UPDATE_INTERVAL') else 30
        self.current_stats = None
        
        # Performance history for trend analysis (last 10 readings)
        self.cpu_history = deque(maxlen=10)
        self.memory_history = deque(maxlen=10)
        self.temp_history = deque(maxlen=10)
        self.network_history = deque(maxlen=10)
        
        # Previous network stats for speed calculation
        self.prev_network_stats = None
        self.last_network_time = None
        
        # System health thresholds with enhanced granularity
        self.temp_thresholds = {
            "excellent": 40,    # Below 40°C - excellent
            "good": 50,         # 40-50°C - good
            "warm": 65,         # 50-65°C - warm
            "hot": 75,          # 65-75°C - hot
            "critical": 85      # Above 85°C - critical
        }
        
        self.cpu_thresholds = {
            "excellent": 15,    # Below 15% - excellent
            "good": 35,         # 15-35% - good
            "moderate": 60,     # 35-60% - moderate
            "high": 80,         # 60-80% - high
            "critical": 95      # Above 95% - critical
        }
        
        self.memory_thresholds = {
            "excellent": 30,    # Below 30% - excellent
            "good": 50,         # 30-50% - good
            "moderate": 70,     # 50-70% - moderate
            "high": 85,         # 70-85% - high
            "critical": 95      # Above 95% - critical
        }
        
        self.disk_thresholds = {
            "excellent": 40,    # Below 40% - excellent
            "good": 60,         # 40-60% - good
            "moderate": 75,     # 60-75% - moderate
            "high": 85,         # 75-85% - high
            "critical": 95      # Above 95% - critical
        }
    
    def get_system_stats(self):
        """Gather comprehensive system statistics with enhanced metrics."""
        try:
            stats = {}
            current_time = time.time()
            
            # CPU information with detailed metrics
            stats["cpu_percent"] = psutil.cpu_percent(interval=1)
            stats["cpu_count"] = psutil.cpu_count()
            stats["cpu_freq"] = psutil.cpu_freq()
            stats["load_avg"] = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            # CPU per-core usage (for advanced monitoring)
            stats["cpu_per_core"] = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Memory information with swap details
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            stats["memory_total"] = memory.total
            stats["memory_used"] = memory.used
            stats["memory_percent"] = memory.percent
            stats["memory_available"] = memory.available
            stats["memory_cached"] = memory.cached if hasattr(memory, 'cached') else 0
            stats["swap_total"] = swap.total
            stats["swap_used"] = swap.used
            stats["swap_percent"] = swap.percent
            
            # Disk usage with multiple mount points
            disk = psutil.disk_usage('/')
            stats["disk_total"] = disk.total
            stats["disk_used"] = disk.used
            stats["disk_percent"] = (disk.used / disk.total) * 100
            stats["disk_free"] = disk.free
            
            # Disk I/O statistics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                stats["disk_read_bytes"] = disk_io.read_bytes
                stats["disk_write_bytes"] = disk_io.write_bytes
                stats["disk_read_count"] = disk_io.read_count
                stats["disk_write_count"] = disk_io.write_count
            
            # System uptime and boot time
            boot_time = psutil.boot_time()
            stats["uptime"] = datetime.now() - datetime.fromtimestamp(boot_time)
            stats["boot_time"] = datetime.fromtimestamp(boot_time)
            
            # Temperature monitoring
            stats["temperature"] = self.get_cpu_temperature()
            
            # Network statistics with speed calculation
            net_io = psutil.net_io_counters()
            stats["bytes_sent"] = net_io.bytes_sent
            stats["bytes_recv"] = net_io.bytes_recv
            stats["packets_sent"] = net_io.packets_sent
            stats["packets_recv"] = net_io.packets_recv
            
            # Calculate network speed if we have previous stats
            if self.prev_network_stats and self.last_network_time:
                time_diff = current_time - self.last_network_time
                if time_diff > 0:
                    sent_speed = (stats["bytes_sent"] - self.prev_network_stats["bytes_sent"]) / time_diff
                    recv_speed = (stats["bytes_recv"] - self.prev_network_stats["bytes_recv"]) / time_diff
                    stats["network_send_speed"] = max(0, sent_speed)  # Bytes per second
                    stats["network_recv_speed"] = max(0, recv_speed)  # Bytes per second
                else:
                    stats["network_send_speed"] = 0
                    stats["network_recv_speed"] = 0
            else:
                stats["network_send_speed"] = 0
                stats["network_recv_speed"] = 0
            
            # Store current network stats for next calculation
            self.prev_network_stats = {
                "bytes_sent": stats["bytes_sent"],
                "bytes_recv": stats["bytes_recv"]
            }
            self.last_network_time = current_time
            
            # Process and system information
            stats["process_count"] = len(psutil.pids())
            
            # Top processes by CPU usage
            try:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        proc.info['cpu_percent'] = proc.cpu_percent()
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Sort by CPU usage and get top 3
                top_processes = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:3]
                stats["top_processes"] = top_processes
            except:
                stats["top_processes"] = []
            
            # System information
            stats["hostname"] = socket.gethostname()
            stats["platform"] = platform.platform()
            stats["architecture"] = platform.architecture()[0]
            stats["python_version"] = platform.python_version()
            
            # System load categories
            if hasattr(os, 'getloadavg'):
                load_1min = stats["load_avg"][0]
                cpu_count = stats["cpu_count"]
                stats["load_status"] = self.get_load_status(load_1min, cpu_count)
            else:
                stats["load_status"] = "unknown"
            
            # Network interface information
            try:
                net_if_stats = psutil.net_if_stats()
                active_interfaces = []
                for interface, stats_info in net_if_stats.items():
                    if stats_info.isup and interface != 'lo':  # Skip loopback
                        active_interfaces.append({
                            'name': interface,
                            'speed': stats_info.speed,
                            'mtu': stats_info.mtu
                        })
                stats["network_interfaces"] = active_interfaces[:2]  # Show top 2
            except:
                stats["network_interfaces"] = []
            
            # Update performance history
            self.cpu_history.append(stats["cpu_percent"])
            self.memory_history.append(stats["memory_percent"])
            self.temp_history.append(stats["temperature"])
            if stats["network_recv_speed"] > 0 or stats["network_send_speed"] > 0:
                total_speed = stats["network_recv_speed"] + stats["network_send_speed"]
                self.network_history.append(total_speed / 1024)  # KB/s
            
            return stats
            
        except Exception as e:
            print(f"Error gathering system stats: {e}")
            return self.get_fallback_stats()

    def get_load_status(self, load_avg, cpu_count):
        """Determine system load status based on load average."""
        load_ratio = load_avg / cpu_count
        if load_ratio < 0.5:
            return "excellent"
        elif load_ratio < 1.0:
            return "good"
        elif load_ratio < 1.5:
            return "moderate"
        elif load_ratio < 2.0:
            return "high"
        else:
            return "critical"
    
    def get_cpu_temperature(self):
        """Get CPU temperature for Raspberry Pi with enhanced detection."""
        try:
            # Method 1: /sys/class/thermal (most common)
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read().strip()) / 1000.0
                    return round(temp, 1)
            except:
                pass
            
            # Method 2: vcgencmd (Raspberry Pi specific)
            try:
                result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    temp_str = result.stdout.strip()
                    temp = float(temp_str.split('=')[1].split("'")[0])
                    return round(temp, 1)
            except:
                pass
            
            # Method 3: Using psutil sensors (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries and entries[0].current:
                            return round(entries[0].current, 1)
            except:
                pass
            
            # Method 4: Check for other thermal zones
            for i in range(5):
                try:
                    with open(f'/sys/class/thermal/thermal_zone{i}/temp', 'r') as f:
                        temp = float(f.read().strip()) / 1000.0
                        if 20 < temp < 100:  # Reasonable temperature range
                            return round(temp, 1)
                except:
                    continue
            
            # Fallback temperature
            return 42.0
            
        except Exception as e:
            print(f"Error getting temperature: {e}")
            return 42.0
    def get_load_status(self, load_avg, cpu_count):
        """Determine system load status based on load average."""
        load_ratio = load_avg / cpu_count
        if load_ratio < 0.5:
            return "excellent"
        elif load_ratio < 1.0:
            return "good"
        elif load_ratio < 1.5:
            return "moderate"
        elif load_ratio < 2.0:
            return "high"
        else:
            return "critical"
        """Get CPU temperature for Raspberry Pi."""
        try:
            # Try multiple methods for getting temperature
            
            # Method 1: /sys/class/thermal (most common)
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read().strip()) / 1000.0
                    return round(temp, 1)
            except:
                pass
            
            # Method 2: vcgencmd (Raspberry Pi specific)
            try:
                result = subprocess.run(['vcgencmd', 'measure_temp'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    temp_str = result.stdout.strip()
                    temp = float(temp_str.split('=')[1].split("'")[0])
                    return round(temp, 1)
            except:
                pass
            
            # Method 3: Using psutil sensors (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            return round(entries[0].current, 1)
            except:
                pass
            
            # Fallback
            return 45.0
            
        except Exception as e:
            print(f"Error getting temperature: {e}")
            return 45.0
    
    def get_fallback_stats(self):
        """Provide comprehensive fallback stats when system calls fail."""
        return {
            "cpu_percent": 35.0,
            "cpu_count": 4,
            "cpu_freq": type('obj', (object,), {'current': 1500.0, 'min': 600.0, 'max': 1800.0})(),
            "load_avg": (0.8, 0.6, 0.4),
            "cpu_per_core": [30.0, 40.0, 35.0, 25.0],
            "memory_total": 1073741824,     # 1GB
            "memory_used": 536870912,       # 512MB
            "memory_percent": 50.0,
            "memory_available": 536870912,
            "memory_cached": 134217728,     # 128MB
            "swap_total": 1073741824,       # 1GB
            "swap_used": 0,
            "swap_percent": 0.0,
            "disk_total": 32212254720,      # 30GB
            "disk_used": 9663676416,        # 9GB
            "disk_percent": 30.0,
            "disk_free": 22548578304,
            "disk_read_bytes": 1048576000,  # 1GB
            "disk_write_bytes": 524288000,  # 500MB
            "disk_read_count": 10000,
            "disk_write_count": 5000,
            "uptime": timedelta(days=2, hours=14, minutes=23),
            "boot_time": datetime.now() - timedelta(days=2, hours=14, minutes=23),
            "temperature": 45.5,
            "bytes_sent": 10485760,         # 10MB
            "bytes_recv": 104857600,        # 100MB
            "packets_sent": 50000,
            "packets_recv": 75000,
            "network_send_speed": 1024,     # 1KB/s
            "network_recv_speed": 5120,     # 5KB/s
            "process_count": 142,
            "top_processes": [
                {"pid": 1234, "name": "python3", "cpu_percent": 15.2, "memory_percent": 8.5},
                {"pid": 5678, "name": "chromium", "cpu_percent": 12.8, "memory_percent": 12.3},
                {"pid": 9012, "name": "systemd", "cpu_percent": 5.1, "memory_percent": 2.1}
            ],
            "hostname": "raspberrypi",
            "platform": "Linux-6.1.0-rpi7-rpi-v8-aarch64-with-glibc2.31",
            "architecture": "64bit",
            "python_version": "3.11.2",
            "load_status": "good",
            "network_interfaces": [
                {"name": "wlan0", "speed": 100, "mtu": 1500},
                {"name": "eth0", "speed": 1000, "mtu": 1500}
            ]
        }
    
    def get_metric_color(self, value, thresholds):
        """Get enhanced color based on metric value and refined thresholds."""
        if "excellent" in thresholds and value < thresholds["excellent"]:
            return (50, 255, 50)        # Bright green - excellent
        elif "good" in thresholds and value < thresholds["good"]:
            return (100, 220, 100)      # Light green - good
        elif "moderate" in thresholds and value < thresholds["moderate"]:
            return (255, 200, 50)       # Yellow-orange - moderate
        elif "high" in thresholds and value < thresholds["high"]:
            return (255, 140, 50)       # Orange - high
        else:
            return (255, 80, 80)        # Red - critical
    
    def get_status_text(self, value, thresholds):
        """Get status text for a metric value."""
        if "excellent" in thresholds and value < thresholds["excellent"]:
            return "EXCELLENT"
        elif "good" in thresholds and value < thresholds["good"]:
            return "GOOD"
        elif "moderate" in thresholds and value < thresholds["moderate"]:
            return "MODERATE"
        elif "high" in thresholds and value < thresholds["high"]:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def format_bytes(self, bytes_value):
        """Format bytes into human readable format with enhanced precision."""
        if bytes_value == 0:
            return "0B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while bytes_value >= 1024.0 and unit_index < len(units) - 1:
            bytes_value /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(bytes_value)}B"
        elif bytes_value >= 100:
            return f"{bytes_value:.0f}{units[unit_index]}"
        elif bytes_value >= 10:
            return f"{bytes_value:.1f}{units[unit_index]}"
        else:
            return f"{bytes_value:.2f}{units[unit_index]}"
    
    def format_speed(self, bytes_per_second):
        """Format network speed into human readable format."""
        return f"{self.format_bytes(bytes_per_second)}/s"
    
    def format_uptime(self, uptime_delta):
        """Format uptime into readable string with enhanced detail."""
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 365:
            years = days // 365
            remaining_days = days % 365
            return f"{years}y {remaining_days}d"
        elif days > 30:
            months = days // 30
            remaining_days = days % 30
            return f"{months}mo {remaining_days}d"
        elif days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def draw_mini_graph(self, draw, x, y, width, height, data, color):
        """Draw a miniature performance graph."""
        if len(data) < 2:
            return
        
        # Normalize data to fit in the height
        max_val = max(data) if max(data) > 0 else 1
        min_val = min(data)
        range_val = max_val - min_val if max_val > min_val else 1
        
        # Draw background
        draw.rectangle([x, y, x + width, y + height], fill=(20, 25, 35), outline=(60, 70, 90))
        
        # Draw data points
        points = []
        step = width / (len(data) - 1)
        for i, value in enumerate(data):
            px = x + int(i * step)
            py = y + height - int(((value - min_val) / range_val) * height)
            points.append((px, py))
        
        # Draw the line graph
        if len(points) > 1:
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=color, width=1)
    
    def create_system_background(self):
        """Create an ultra-modern tech-themed background with enhanced visual elements."""
        image = Image.new("RGB", (640, 400), (12, 15, 25))
        draw = ImageDraw.Draw(image)
        
        # Create sophisticated multi-layer gradient with depth
        for y in range(400):
            ratio = y / 400
            # Deep space gradient: dark navy to electric blue
            r = int(12 + (28 * ratio * ratio))  # Quadratic easing
            g = int(15 + (45 * ratio))
            b = int(25 + (65 * ratio))
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Add sophisticated hexagonal pattern overlay
        hex_color = (25, 35, 50, 80)  # Semi-transparent
        hex_size = 25
        
        for row in range(-2, 18):
            for col in range(-2, 30):
                offset_x = (col * hex_size * 1.5)
                offset_y = (row * hex_size * 0.866) + (hex_size * 0.433 if col % 2 else 0)
                
                if offset_x < 680 and offset_y < 420:
                    self.draw_hexagon(draw, offset_x, offset_y, hex_size // 3, (25, 35, 50))
        
        # Enhanced circuit-board style connections
        connection_color = (40, 80, 120)
        node_color = (60, 120, 180)
        
        # Horizontal connection lines
        for y in [80, 160, 240, 320]:
            draw.line([(20, y), (620, y)], fill=connection_color, width=1)
            
            # Connection nodes
            for x in range(80, 580, 100):
                draw.ellipse([x-3, y-3, x+3, y+3], fill=node_color, outline=(100, 150, 200))
                
                # Vertical connectors
                if y < 320:
                    draw.line([(x, y), (x, y + 80)], fill=connection_color, width=1)
        
        # Add subtle data flow indicators
        flow_color = (30, 90, 150)
        for i in range(8):
            x = 80 + (i * 70)
            y = 40
            # Small arrow indicators
            draw.polygon([(x, y), (x+5, y+3), (x, y+6), (x+2, y+3)], fill=flow_color)
            
        # Corner accent elements
        accent_color = (80, 140, 200)
        
        # Top-left corner
        draw.line([(0, 15), (30, 15)], fill=accent_color, width=2)
        draw.line([(15, 0), (15, 30)], fill=accent_color, width=2)
        
        # Top-right corner
        draw.line([(610, 15), (640, 15)], fill=accent_color, width=2)
        draw.line([(625, 0), (625, 30)], fill=accent_color, width=2)
        
        # Bottom corners
        draw.line([(0, 385), (30, 385)], fill=accent_color, width=2)
        draw.line([(15, 370), (15, 400)], fill=accent_color, width=2)
        draw.line([(610, 385), (640, 385)], fill=accent_color, width=2)
        draw.line([(625, 370), (625, 400)], fill=accent_color, width=2)
        
        return image
    
    def draw_hexagon(self, draw, x, y, size, color):
        """Draw a hexagon for the background pattern."""
        angles = [i * 60 for i in range(6)]
        points = []
        for angle in angles:
            px = x + size * 0.866 * (1 if angle in [0, 60, 300] else -1 if angle in [120, 180, 240] else 0)
            py = y + size * (0.5 if angle in [60, 120] else -0.5 if angle in [240, 300] else 1 if angle == 180 else -1 if angle == 0 else 0)
            points.append((int(px), int(py)))
        
        if len(points) == 6:
            draw.polygon(points, outline=color)
    
    def draw_status_icon(self, draw, x, y, metric_type, value, thresholds):
        """Draw an enhanced status icon with modern styling."""
        color = self.get_metric_color(value, thresholds)
        
        # Create layered circular indicator with depth
        radius = 8
        
        # Outer glow effect (simplified for e-ink)
        for r in range(radius + 3, radius - 1, -1):
            alpha_color = (
                max(0, color[0] - (radius + 3 - r) * 20),
                max(0, color[1] - (radius + 3 - r) * 20),
                max(0, color[2] - (radius + 3 - r) * 20)
            )
            draw.ellipse([x - r, y - r, x + r, y + r], outline=alpha_color)
        
        # Main indicator with gradient effect
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                    fill=color, outline=(255, 255, 255), width=2)
        
        # Inner highlight for depth
        highlight_color = (min(255, color[0] + 80), min(255, color[1] + 80), min(255, color[2] + 80))
        draw.ellipse([x - radius + 3, y - radius + 3, x + radius - 3, y + radius - 3], 
                    outline=highlight_color, width=1)
        
        # Status-specific icon inside
        icon_color = (255, 255, 255)
        if metric_type == "cpu":
            # CPU icon: small squares
            draw.rectangle([x-2, y-2, x, y], fill=icon_color)
            draw.rectangle([x+1, y-2, x+3, y], fill=icon_color)
            draw.rectangle([x-2, y+1, x, y+3], fill=icon_color)
            draw.rectangle([x+1, y+1, x+3, y+3], fill=icon_color)
        elif metric_type == "memory":
            # Memory icon: horizontal bars
            for i in range(3):
                draw.line([(x-3, y-2+i*2), (x+3, y-2+i*2)], fill=icon_color, width=1)
        elif metric_type == "temp":
            # Temperature icon: thermometer
            draw.line([(x, y-3), (x, y+2)], fill=icon_color, width=2)
            draw.ellipse([x-1, y+1, x+1, y+3], fill=icon_color)
        elif metric_type == "disk":
            # Disk icon: cylinder
            draw.ellipse([x-3, y-2, x+3, y], outline=icon_color)
            draw.ellipse([x-3, y+1, x+3, y+3], outline=icon_color)
            draw.line([(x-3, y-1), (x-3, y+2)], fill=icon_color)
            draw.line([(x+3, y-1), (x+3, y+2)], fill=icon_color)

    def draw_enhanced_metric_card(self, draw, x, y, width, height, title, value, unit, 
                                 percentage=None, color=None, subtitle="", trend_data=None):
        """Draw a modern metric card with enhanced styling and optional trend."""
        # Card background with subtle border
        card_bg = (30, 40, 55)
        border_color = (70, 90, 120)
        
        # Draw card background
        draw.rectangle([x, y, x + width - 1, y + height - 1], 
                      fill=card_bg, outline=border_color, width=1)
        
        # Add subtle inner border for depth
        inner_border = (50, 65, 85)
        draw.rectangle([x + 1, y + 1, x + width - 2, y + height - 2], 
                      outline=inner_border)
        
        # Title section with modern typography
        title_color = (180, 210, 255)
        if hasattr(self, 'font_small') and self.font_small:
            draw.text((x + 8, y + 6), title, fill=title_color, font=self.font_small)
        
        # Main value with dynamic sizing
        main_color = color if color else (255, 255, 255)
        value_text = f"{value}{unit}"
        
        if hasattr(self, 'font_large') and self.font_large:
            draw.text((x + 8, y + 22), value_text, fill=main_color, font=self.font_large)
        
        # Subtitle/additional info
        if subtitle:
            subtitle_color = (140, 170, 200)
            if hasattr(self, 'font_tiny') and self.font_tiny:
                draw.text((x + 8, y + height - 16), subtitle, fill=subtitle_color, font=self.font_tiny)
        
        # Progress bar if percentage provided
        if percentage is not None:
            bar_y = y + height - 8
            bar_width = width - 16
            self.draw_enhanced_progress_bar(draw, x + 8, bar_y, bar_width, 4, 
                                          percentage, 100, main_color)
        
        # Mini trend graph if data provided
        if trend_data and len(trend_data) > 1:
            graph_x = x + width - 60
            graph_y = y + 8
            self.draw_mini_graph(draw, graph_x, graph_y, 50, 20, trend_data, main_color)

    def draw_enhanced_progress_bar(self, draw, x, y, width, height, value, max_value, color):
        """Draw an enhanced horizontal progress bar with modern styling."""
        # Background bar with rounded effect
        bg_color = (20, 25, 35)
        border_color = (60, 70, 90)
        
        draw.rectangle([x, y, x + width, y + height], fill=bg_color, outline=border_color)
        
        # Calculate fill width
        fill_width = int((value / max_value) * (width - 2))
        
        if fill_width > 2:
            # Gradient fill effect (simplified for e-ink)
            fill_color = color
            draw.rectangle([x + 1, y + 1, x + fill_width, y + height - 1], fill=fill_color)
            
            # Highlight on top edge for depth
            highlight_color = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))
            if fill_width > 4:
                draw.line([(x + 1, y + 1), (x + fill_width - 1, y + 1)], fill=highlight_color)
    
    def display(self):
        """Display ultra-modern comprehensive system dashboard with advanced metrics."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Advanced System Dashboard...")
        
        try:
            # Get comprehensive system statistics
            stats = self.get_system_stats()
            self.current_stats = stats
            
            # Load enhanced font system
            fonts = get_system_fonts()
            self.font_title = fonts['title']      # 24pt title font
            self.font_large = fonts['large']      # 20pt bold font
            self.font_medium = fonts['medium']    # 16pt bold font
            self.font_small = fonts['small']      # 13pt regular font
            self.font_tiny = fonts['tiny']        # 11pt small font
            
            # Create ultra-modern background
            display_image = self.create_system_background()
            draw = ImageDraw.Draw(display_image)
            
            # Ultra-modern header with system info
            current_time = datetime.now().strftime("%H:%M:%S")
            title = f"◆ SYSTEM TELEMETRY ◆ {stats['hostname'].upper()} ◆ {current_time}"
            
            if self.font_title:
                bbox = draw.textbbox((0, 0), title, font=self.font_title)
                title_width = bbox[2] - bbox[0]
                title_x = (640 - title_width) // 2
                
                # Enhanced glow effect
                glow_color = (30, 60, 120)
                for offset in [(3, 3), (2, 2), (1, 1), (-1, -1), (-2, -2), (-3, -3)]:
                    draw.text((title_x + offset[0], 8 + offset[1]), title, fill=glow_color, font=self.font_title)
                
                # Main title with gradient effect
                draw.text((title_x, 8), title, fill=(150, 220, 255), font=self.font_title)
            
            # System status bar with enhanced info
            uptime_str = self.format_uptime(stats["uptime"])
            load_status = stats.get("load_status", "unknown").upper()
            load_color = self.get_metric_color(stats["load_avg"][0] * 100 / stats["cpu_count"], 
                                             {"excellent": 50, "good": 75, "moderate": 100, "high": 150, "critical": 200})
            
            status_text = f"⚡ {load_status} LOAD  •  ⏱️ UP {uptime_str}  •  🔄 {stats['process_count']} PROC"
            
            if self.font_small:
                bbox = draw.textbbox((0, 0), status_text, font=self.font_small)
                status_width = bbox[2] - bbox[0]
                status_x = (640 - status_width) // 2
                draw.text((status_x, 38), status_text, fill=(180, 220, 255), font=self.font_small)
            
            # ===== MAIN METRICS GRID (2x2) =====
            card_width = 280
            card_height = 65
            card_spacing = 40
            grid_start_y = 65
            
            # Row 1: CPU and Memory
            y_pos = grid_start_y
            
            # CPU PERFORMANCE CARD
            cpu_color = self.get_metric_color(stats["cpu_percent"], self.cpu_thresholds)
            cpu_status = self.get_status_text(stats["cpu_percent"], self.cpu_thresholds)
            cpu_subtitle = f"Load: {stats['load_avg'][0]:.2f}  •  {stats['cpu_count']} cores"
            
            self.draw_enhanced_metric_card(
                draw, 30, y_pos, card_width, card_height,
                "CPU PERFORMANCE", f"{stats['cpu_percent']:.1f}", "%",
                stats['cpu_percent'], cpu_color, cpu_subtitle, 
                list(self.cpu_history) if self.cpu_history else None
            )
            
            # CPU status icon
            self.draw_status_icon(draw, 290, y_pos + 20, "cpu", stats["cpu_percent"], self.cpu_thresholds)
            
            # MEMORY UTILIZATION CARD  
            memory_color = self.get_metric_color(stats["memory_percent"], self.memory_thresholds)
            memory_used_gb = stats["memory_used"] / (1024**3)
            memory_total_gb = stats["memory_total"] / (1024**3)
            memory_subtitle = f"{memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB used"
            
            self.draw_enhanced_metric_card(
                draw, 330, y_pos, card_width, card_height,
                "MEMORY UTILIZATION", f"{stats['memory_percent']:.1f}", "%",
                stats['memory_percent'], memory_color, memory_subtitle,
                list(self.memory_history) if self.memory_history else None
            )
            
            # Memory status icon
            self.draw_status_icon(draw, 590, y_pos + 20, "memory", stats["memory_percent"], self.memory_thresholds)
            
            # Row 2: Temperature and Disk
            y_pos += card_height + 15
            
            # THERMAL MONITORING CARD
            temp_color = self.get_metric_color(stats["temperature"], self.temp_thresholds)
            temp_status = self.get_status_text(stats["temperature"], self.temp_thresholds)
            temp_subtitle = f"Status: {temp_status}"
            
            self.draw_enhanced_metric_card(
                draw, 30, y_pos, card_width, card_height,
                "THERMAL MONITORING", f"{stats['temperature']:.1f}", "°C",
                (stats['temperature'] / 100) * 100, temp_color, temp_subtitle,
                list(self.temp_history) if self.temp_history else None
            )
            
            # Temperature status icon
            self.draw_status_icon(draw, 290, y_pos + 20, "temp", stats["temperature"], self.temp_thresholds)
            
            # STORAGE ANALYTICS CARD
            disk_color = self.get_metric_color(stats["disk_percent"], self.disk_thresholds)
            disk_used_str = self.format_bytes(stats["disk_used"])
            disk_total_str = self.format_bytes(stats["disk_total"])
            disk_subtitle = f"{disk_used_str} / {disk_total_str} allocated"
            
            self.draw_enhanced_metric_card(
                draw, 330, y_pos, card_width, card_height,
                "STORAGE ANALYTICS", f"{stats['disk_percent']:.1f}", "%",
                stats['disk_percent'], disk_color, disk_subtitle, None
            )
            
            # Disk status icon
            self.draw_status_icon(draw, 590, y_pos + 20, "disk", stats["disk_percent"], self.disk_thresholds)
            
            # ===== ADVANCED METRICS PANEL =====
            panel_y = 215
            panel_height = 140
            
            # Draw main info panel
            draw.rectangle([15, panel_y, 625, panel_y + panel_height - 1], 
                          fill=(25, 35, 50), outline=(70, 100, 140), width=2)
            
            # Panel title
            if self.font_medium:
                draw.text((25, panel_y + 8), "◆ NETWORK & SYSTEM ANALYTICS ◆", 
                         fill=(120, 200, 255), font=self.font_medium)
            
            # === LEFT COLUMN: Network Performance ===
            col1_x = 30
            info_y = panel_y + 30
            
            if self.font_small:
                # Network speeds
                send_speed = self.format_speed(stats.get('network_send_speed', 0))
                recv_speed = self.format_speed(stats.get('network_recv_speed', 0))
                
                draw.text((col1_x, info_y), "NETWORK ACTIVITY:", fill=(100, 180, 255), font=self.font_small)
                draw.text((col1_x, info_y + 18), f"↑ TX: {send_speed}", fill=(100, 255, 150), font=self.font_tiny)
                draw.text((col1_x, info_y + 32), f"↓ RX: {recv_speed}", fill=(255, 150, 100), font=self.font_tiny)
                
                # Total data transferred
                total_sent = self.format_bytes(stats["bytes_sent"])
                total_recv = self.format_bytes(stats["bytes_recv"])
                draw.text((col1_x, info_y + 50), f"Total TX: {total_sent}", fill=(150, 200, 150), font=self.font_tiny)
                draw.text((col1_x, info_y + 64), f"Total RX: {total_recv}", fill=(200, 150, 150), font=self.font_tiny)
                
                # Active network interfaces
                if stats.get("network_interfaces"):
                    interface = stats["network_interfaces"][0]
                    draw.text((col1_x, info_y + 82), f"Interface: {interface['name']}", 
                             fill=(180, 180, 255), font=self.font_tiny)
                    if interface.get('speed'):
                        draw.text((col1_x, info_y + 96), f"Link Speed: {interface['speed']}Mbps", 
                                 fill=(180, 180, 255), font=self.font_tiny)
            
            # === MIDDLE COLUMN: System Performance ===
            col2_x = 220
            
            if self.font_small:
                # Top processes
                draw.text((col2_x, info_y), "TOP PROCESSES:", fill=(255, 200, 100), font=self.font_small)
                
                if stats.get("top_processes"):
                    for i, proc in enumerate(stats["top_processes"][:3]):
                        proc_name = proc.get('name', 'unknown')[:12]  # Truncate long names
                        cpu_pct = proc.get('cpu_percent', 0)
                        mem_pct = proc.get('memory_percent', 0)
                        
                        proc_text = f"{proc_name}: {cpu_pct:.1f}% CPU, {mem_pct:.1f}% MEM"
                        draw.text((col2_x, info_y + 18 + i * 14), proc_text, 
                                 fill=(200, 220, 180), font=self.font_tiny)
                
                # Disk I/O if available
                if stats.get("disk_read_bytes") is not None:
                    disk_read = self.format_bytes(stats["disk_read_bytes"])
                    disk_write = self.format_bytes(stats["disk_write_bytes"])
                    draw.text((col2_x, info_y + 68), f"Disk Read: {disk_read}", 
                             fill=(150, 200, 255), font=self.font_tiny)
                    draw.text((col2_x, info_y + 82), f"Disk Write: {disk_write}", 
                             fill=(255, 200, 150), font=self.font_tiny)
            
            # === RIGHT COLUMN: System Information ===
            col3_x = 420
            
            if self.font_small:
                draw.text((col3_x, info_y), "SYSTEM INFO:", fill=(255, 150, 200), font=self.font_small)
                
                # Platform and architecture
                arch = stats.get("architecture", "unknown")
                draw.text((col3_x, info_y + 18), f"Arch: {arch}", fill=(200, 200, 255), font=self.font_tiny)
                
                # Boot time
                boot_time = stats.get("boot_time")
                if boot_time:
                    boot_str = boot_time.strftime("%m/%d %H:%M")
                    draw.text((col3_x, info_y + 32), f"Boot: {boot_str}", fill=(200, 200, 255), font=self.font_tiny)
                
                # Python version
                py_ver = stats.get("python_version", "unknown")
                draw.text((col3_x, info_y + 46), f"Python: {py_ver}", fill=(200, 200, 255), font=self.font_tiny)
                
                # Memory details
                if stats.get("swap_total", 0) > 0:
                    swap_pct = stats.get("swap_percent", 0)
                    draw.text((col3_x, info_y + 60), f"Swap: {swap_pct:.1f}%", 
                             fill=(255, 255, 150), font=self.font_tiny)
                
                # CPU frequency if available
                if stats.get("cpu_freq") and hasattr(stats["cpu_freq"], 'current'):
                    freq = stats["cpu_freq"].current
                    draw.text((col3_x, info_y + 74), f"CPU: {freq:.0f}MHz", 
                             fill=(150, 255, 150), font=self.font_tiny)
            
            # === BOTTOM STATUS BAR ===
            status_y = panel_y + panel_height - 25
            
            # Performance trend indicators
            if len(self.cpu_history) > 1:
                cpu_trend = "↗" if self.cpu_history[-1] > self.cpu_history[-2] else "↘" if self.cpu_history[-1] < self.cpu_history[-2] else "→"
                mem_trend = "↗" if len(self.memory_history) > 1 and self.memory_history[-1] > self.memory_history[-2] else "↘" if len(self.memory_history) > 1 and self.memory_history[-1] < self.memory_history[-2] else "→"
                
                trend_text = f"Trends: CPU {cpu_trend}  MEM {mem_trend}"
                if self.font_tiny:
                    draw.text((30, status_y), trend_text, fill=(120, 200, 180), font=self.font_tiny)
            
            # Last updated timestamp
            update_text = f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"
            if self.font_tiny:
                bbox = draw.textbbox((0, 0), update_text, font=self.font_tiny)
                update_width = bbox[2] - bbox[0]
                draw.text((625 - update_width, status_y), update_text, 
                         fill=(120, 140, 180), font=self.font_tiny)
            
            # System health indicator
            overall_health = self.calculate_system_health(stats)
            health_color = self.get_health_color(overall_health)
            health_text = f"Health: {overall_health.upper()}"
            
            if self.font_tiny:
                bbox = draw.textbbox((0, 0), health_text, font=self.font_tiny)
                health_width = bbox[2] - bbox[0]
                health_x = 320 - (health_width // 2)
                draw.text((health_x, status_y), health_text, fill=health_color, font=self.font_tiny)
            
            # Ensure image is in RGB format for e-ink display
            display_image = display_image.convert('RGB')
            
            # Display the ultra-modern system dashboard
            self.inky.set_image(display_image)
            self.inky.show()
            
            print(f"Ultra-Modern Dashboard: CPU {stats['cpu_percent']:.1f}%, "
                  f"RAM {stats['memory_percent']:.1f}%, Temp {stats['temperature']:.1f}°C, "
                  f"Health: {overall_health}")
            
        except Exception as e:
            print(f"Error displaying system dashboard: {e}")
            import traceback
            traceback.print_exc()
            self.display_error_message("System Dashboard Error", str(e))
    
    def calculate_system_health(self, stats):
        """Calculate overall system health based on all metrics."""
        health_scores = []
        
        # CPU health (inverted - lower is better)
        cpu_pct = stats.get("cpu_percent", 0)
        if cpu_pct < 25:
            health_scores.append(5)
        elif cpu_pct < 50:
            health_scores.append(4)
        elif cpu_pct < 75:
            health_scores.append(3)
        elif cpu_pct < 90:
            health_scores.append(2)
        else:
            health_scores.append(1)
        
        # Memory health
        mem_pct = stats.get("memory_percent", 0)
        if mem_pct < 40:
            health_scores.append(5)
        elif mem_pct < 60:
            health_scores.append(4)
        elif mem_pct < 80:
            health_scores.append(3)
        elif mem_pct < 95:
            health_scores.append(2)
        else:
            health_scores.append(1)
        
        # Temperature health
        temp = stats.get("temperature", 0)
        if temp < 45:
            health_scores.append(5)
        elif temp < 55:
            health_scores.append(4)
        elif temp < 70:
            health_scores.append(3)
        elif temp < 80:
            health_scores.append(2)
        else:
            health_scores.append(1)
        
        # Disk health
        disk_pct = stats.get("disk_percent", 0)
        if disk_pct < 50:
            health_scores.append(5)
        elif disk_pct < 70:
            health_scores.append(4)
        elif disk_pct < 85:
            health_scores.append(3)
        elif disk_pct < 95:
            health_scores.append(2)
        else:
            health_scores.append(1)
        
        # Calculate average health
        avg_health = sum(health_scores) / len(health_scores)
        
        if avg_health >= 4.5:
            return "excellent"
        elif avg_health >= 3.5:
            return "good"
        elif avg_health >= 2.5:
            return "moderate"
        elif avg_health >= 1.5:
            return "poor"
        else:
            return "critical"
    
    def get_health_color(self, health):
        """Get color for system health status."""
        health_colors = {
            "excellent": (50, 255, 50),
            "good": (100, 220, 100),
            "moderate": (255, 200, 50),
            "poor": (255, 140, 50),
            "critical": (255, 80, 80)
        }
        return health_colors.get(health, (200, 200, 200))
    
    def display_error_message(self, title, message):
        """Display an ultra-modern error message with enhanced system theme."""
        # Create enhanced background
        image = self.create_system_background()
        draw = ImageDraw.Draw(image)
        
        # Use font utilities for error display
        font_title = get_font('title', 24)
        font_text = get_font('regular', 16)
        font_small = get_font('small', 14)
        
        # Ultra-modern error panel
        panel_x, panel_y = 80, 120
        panel_width, panel_height = 480, 160
        
        # Draw error panel with gradient background
        for i in range(panel_height):
            factor = i / panel_height
            r = int(60 + (20 * factor))
            g = int(20 + (10 * factor))
            b = int(20 + (10 * factor))
            draw.line([(panel_x, panel_y + i), (panel_x + panel_width, panel_y + i)], fill=(r, g, b))
        
        # Enhanced border with glow effect
        border_colors = [(255, 120, 120), (200, 80, 80), (150, 60, 60)]
        for i, color in enumerate(border_colors):
            draw.rectangle([panel_x - i, panel_y - i, panel_x + panel_width + i, panel_y + panel_height + i], 
                          outline=color, width=1)
        
        # Error icon
        icon_x, icon_y = panel_x + 20, panel_y + 30
        icon_size = 25
        
        # Draw warning triangle
        draw.polygon([
            (icon_x + icon_size // 2, icon_y),
            (icon_x, icon_y + icon_size),
            (icon_x + icon_size, icon_y + icon_size)
        ], fill=(255, 200, 100), outline=(255, 255, 255), width=2)
        
        # Exclamation mark in triangle
        draw.line([(icon_x + icon_size // 2, icon_y + 8), (icon_x + icon_size // 2, icon_y + 16)], 
                 fill=(60, 20, 20), width=3)
        draw.ellipse([icon_x + icon_size // 2 - 1, icon_y + 19, icon_x + icon_size // 2 + 1, icon_y + 21], 
                    fill=(60, 20, 20))
        
        # Error title with enhanced styling
        if font_title:
            title_x = panel_x + 60
            # Glow effect for title
            for offset in [(2, 2), (1, 1), (-1, -1), (-2, -2)]:
                draw.text((title_x + offset[0], panel_y + 25 + offset[1]), title, 
                         fill=(100, 20, 20), font=font_title)
            # Main title
            draw.text((title_x, panel_y + 25), title, fill=(255, 180, 180), font=font_title)
            
        # Error message with word wrapping
        if font_text:
            # Truncate and wrap message
            max_chars = 45
            if len(message) > max_chars:
                # Try to break at word boundaries
                words = message.split()
                line1 = ""
                line2 = ""
                for word in words:
                    if len(line1 + word + " ") <= max_chars:
                        line1 += word + " "
                    else:
                        line2 = " ".join(words[words.index(word):])
                        break
                
                if len(line2) > max_chars:
                    line2 = line2[:max_chars - 3] + "..."
                
                # Draw both lines
                draw.text((panel_x + 30, panel_y + 70), line1.strip(), 
                         fill=(255, 220, 220), font=font_text)
                if line2:
                    draw.text((panel_x + 30, panel_y + 95), line2.strip(), 
                             fill=(255, 220, 220), font=font_text)
            else:
                draw.text((panel_x + 30, panel_y + 70), message, 
                         fill=(255, 220, 220), font=font_text)
        
        # Helpful message and status
        if font_small:
            help_text = "◆ System monitoring will resume automatically ◆"
            bbox = draw.textbbox((0, 0), help_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, panel_y + panel_height + 20), help_text, 
                     fill=(180, 220, 255), font=font_small)
            
            # Timestamp
            timestamp = datetime.now().strftime("Error at %H:%M:%S")
            bbox = draw.textbbox((0, 0), timestamp, font=font_small)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, panel_y + panel_height + 40), timestamp, 
                     fill=(150, 170, 200), font=font_small)
        
        # Ensure image is in RGB format for e-ink display
        image = image.convert('RGB')
        
        self.inky.set_image(image)
        self.inky.show()
