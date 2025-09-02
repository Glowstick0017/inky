"""
System Dashboard Screen - Raspberry Pi Zero 2 W Monitoring
Displays system stats: CPU usage, memory, temperature, uptime, disk usage
Optimized for 640x400 e-ink display with large, readable metrics
Updates every 60 seconds with real-time system information
"""

import os
import psutil
import subprocess
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from .base_screen import BaseScreen
import config
from font_manager import font_manager

class SystemScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.SYSTEM_UPDATE_INTERVAL if hasattr(config, 'SYSTEM_UPDATE_INTERVAL') else 60
        self.current_stats = None
        
        # Temperature thresholds for color coding
        self.temp_thresholds = {
            "low": 50,       # Below 50°C - green
            "medium": 65,    # 50-65°C - yellow  
            "high": 75,      # 65-75°C - orange
            "critical": 80   # Above 80°C - red
        }
        
        # Memory and CPU thresholds
        self.cpu_thresholds = {
            "low": 25,       # Below 25% - green
            "medium": 50,    # 25-50% - yellow
            "high": 75,      # 50-75% - orange
            "critical": 90   # Above 90% - red
        }
        
        self.memory_thresholds = {
            "low": 50,       # Below 50% - green
            "medium": 70,    # 50-70% - yellow
            "high": 85,      # 70-85% - orange
            "critical": 95   # Above 95% - red
        }
        
        self.disk_thresholds = {
            "low": 50,       # Below 50% - green
            "medium": 70,    # 50-70% - yellow
            "high": 85,      # 70-85% - orange
            "critical": 95   # Above 95% - red
        }
    
    def get_system_stats(self):
        """Gather comprehensive system statistics."""
        try:
            stats = {}
            
            # CPU information
            stats["cpu_percent"] = psutil.cpu_percent(interval=1)
            stats["cpu_count"] = psutil.cpu_count()
            stats["load_avg"] = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            # Memory information
            memory = psutil.virtual_memory()
            stats["memory_total"] = memory.total
            stats["memory_used"] = memory.used
            stats["memory_percent"] = memory.percent
            stats["memory_available"] = memory.available
            
            # Disk usage
            disk = psutil.disk_usage('/')
            stats["disk_total"] = disk.total
            stats["disk_used"] = disk.used
            stats["disk_percent"] = (disk.used / disk.total) * 100
            stats["disk_free"] = disk.free
            
            # System uptime
            boot_time = psutil.boot_time()
            stats["uptime"] = datetime.now() - datetime.fromtimestamp(boot_time)
            
            # Temperature (Raspberry Pi specific)
            stats["temperature"] = self.get_cpu_temperature()
            
            # Network stats
            net_io = psutil.net_io_counters()
            stats["bytes_sent"] = net_io.bytes_sent
            stats["bytes_recv"] = net_io.bytes_recv
            
            # Process count
            stats["process_count"] = len(psutil.pids())
            
            # System info
            stats["hostname"] = os.uname().nodename
            stats["kernel"] = os.uname().release
            
            return stats
            
        except Exception as e:
            print(f"Error gathering system stats: {e}")
            return self.get_fallback_stats()
    
    def get_cpu_temperature(self):
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
        """Provide fallback stats when system calls fail."""
        return {
            "cpu_percent": 25.0,
            "cpu_count": 4,
            "load_avg": (0.5, 0.3, 0.2),
            "memory_total": 536870912,  # 512MB
            "memory_used": 268435456,   # 256MB
            "memory_percent": 50.0,
            "memory_available": 268435456,
            "disk_total": 32212254720,  # 30GB
            "disk_used": 8053063680,    # 7.5GB
            "disk_percent": 25.0,
            "disk_free": 24159191040,
            "uptime": timedelta(hours=12, minutes=34),
            "temperature": 45.0,
            "bytes_sent": 1048576,      # 1MB
            "bytes_recv": 10485760,     # 10MB
            "process_count": 85,
            "hostname": "raspberrypi",
            "kernel": "6.1.0-rpi7-rpi-v8"
        }
    
    def get_metric_color(self, value, thresholds):
        """Get color based on metric value and thresholds."""
        if value < thresholds["low"]:
            return (0, 255, 0)      # Green
        elif value < thresholds["medium"]:
            return (255, 255, 0)    # Yellow
        elif value < thresholds["high"]:
            return (255, 165, 0)    # Orange
        else:
            return (255, 0, 0)      # Red
    
    def format_bytes(self, bytes_value):
        """Format bytes into human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}PB"
    
    def format_uptime(self, uptime_delta):
        """Format uptime into readable string."""
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def create_system_background(self):
        """Create a modern tech-themed background with enhanced visual depth."""
        image = Image.new("RGB", (640, 400), (15, 20, 30))
        draw = ImageDraw.Draw(image)
        
        # Create sophisticated multi-layer gradient
        for y in range(400):
            ratio = y / 400
            # Deep space blue to tech cyan gradient
            r = int(15 + (25 * ratio))
            g = int(20 + (35 * ratio))  
            b = int(30 + (50 * ratio))
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Add subtle diagonal tech pattern
        pattern_color = (35, 45, 65, 100)
        overlay = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
        pattern_draw = ImageDraw.Draw(overlay)
        
        # Diagonal lines pattern
        for x in range(-400, 640, 30):
            pattern_draw.line([(x, 0), (x + 400, 400)], fill=pattern_color, width=1)
        
        # Add circuit-board style connection points
        for i in range(15):
            x = (i * 45) + 20
            y = 30 + (i % 3) * 120
            pattern_draw.ellipse([x-2, y-2, x+2, y+2], fill=(60, 120, 180, 150))
            # Connection lines
            if i < 14:
                next_x = ((i+1) * 45) + 20
                next_y = 30 + ((i+1) % 3) * 120
                pattern_draw.line([(x, y), (next_x, next_y)], fill=(40, 80, 120, 80), width=1)
        
        # Composite the pattern overlay
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        return image
    
    def draw_status_icon(self, draw, x, y, metric_type, value, thresholds):
        """Draw a status icon based on metric value."""
        color = self.get_metric_color(value, thresholds)
        
        # Create a small circular indicator
        radius = 6
        
        # Main indicator with glow effect
        # Outer glow circles
        for r in range(radius + 3, radius, -1):
            alpha_factor = (radius + 3 - r) / 3
            glow_color = (
                int(color[0] * 0.3 * alpha_factor),
                int(color[1] * 0.3 * alpha_factor),
                int(color[2] * 0.3 * alpha_factor)
            )
            draw.ellipse([x - r, y - r, x + r, y + r], fill=glow_color)
        
        # Main indicator
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                    fill=color, outline=(255, 255, 255), width=1)
        
        # Inner highlight
        highlight_color = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))
        draw.ellipse([x - radius + 2, y - radius + 2, x + radius - 2, y + radius - 2], 
                    outline=highlight_color)

    def draw_metric_card(self, draw, x, y, width, height, title, value, unit, percentage, color, detail_text=""):
        """Draw a modern metric card with enhanced styling."""
        # Card background with subtle gradient
        card_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        card_draw = ImageDraw.Draw(card_overlay)
        
        # Card background gradient
        for i in range(height):
            factor = i / height
            bg_r = int(35 + (15 * factor))
            bg_g = int(45 + (20 * factor))
            bg_b = int(65 + (25 * factor))
            alpha = 180
            card_draw.line([(0, i), (width, i)], fill=(bg_r, bg_g, bg_b, alpha))
        
        # Card border
        card_draw.rectangle([0, 0, width-1, height-1], outline=(80, 100, 140, 255), width=1)
        
        return card_overlay
        """Draw an enhanced horizontal progress bar with glow effects."""
        # Outer shadow/glow
        shadow_color = (color[0]//4, color[1]//4, color[2]//4)
        draw.rectangle([x-1, y-1, x + width + 1, y + height + 1], fill=shadow_color)
        
        # Background bar with gradient
        draw.rectangle([x, y, x + width, y + height], fill=(25, 30, 40), outline=(60, 70, 90))
        
        # Inner gradient background
        for i in range(height):
            factor = i / height
            bg_r = int(25 + (15 * factor))
            bg_g = int(30 + (20 * factor))
            bg_b = int(40 + (25 * factor))
            draw.line([(x+1, y+i), (x + width-1, y+i)], fill=(bg_r, bg_g, bg_b))
        
        # Fill bar based on percentage with gradient
        fill_width = int((value / max_value) * (width - 2))
        if fill_width > 2:
            for i in range(height - 2):
                factor = i / (height - 2)
                fill_r = int(color[0] * (0.8 + 0.4 * factor))
                fill_g = int(color[1] * (0.8 + 0.4 * factor))
                fill_b = int(color[2] * (0.8 + 0.4 * factor))
                # Clamp values
                fill_r = min(255, fill_r)
                fill_g = min(255, fill_g)
                fill_b = min(255, fill_b)
                draw.line([(x + 1, y + 1 + i), (x + fill_width, y + 1 + i)], 
                         fill=(fill_r, fill_g, fill_b))
            
            # Add highlight on top edge of fill
            highlight_color = (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40))
            draw.line([(x + 1, y + 1), (x + fill_width, y + 1)], fill=highlight_color, width=1)
    
    def display(self):
        """Display comprehensive system statistics with modern card-based layout."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating System Dashboard...")
        
        try:
            # Get system statistics
            stats = self.get_system_stats()
            self.current_stats = stats
            
            # Create enhanced background
            display_image = self.create_system_background()
            draw = ImageDraw.Draw(display_image)
            
            # Load fonts with better sizing using font manager
            font_title = font_manager.get_font('title', 24)
            font_large = font_manager.get_font('bold', 20)
            font_medium = font_manager.get_font('bold', 16)
            font_small = font_manager.get_font('regular', 13)
            font_tiny = font_manager.get_font('small', 11)
            
            # Modern header with glow effect
            title = f"SYSTEM MONITOR • {stats['hostname'].upper()}"
            if font_title:
                bbox = draw.textbbox((0, 0), title, font=font_title)
                title_width = bbox[2] - bbox[0]
                title_x = (640 - title_width) // 2
                # Glow effect
                for offset in [(2, 2), (1, 1), (-1, -1), (-2, -2)]:
                    draw.text((title_x + offset[0], 12 + offset[1]), title, fill=(20, 40, 80), font=font_title)
                # Main title
                draw.text((title_x, 12), title, fill=(120, 200, 255), font=font_title)
            
            # Status bar with time and uptime
            current_time = datetime.now().strftime("%I:%M:%S %p")
            uptime_str = self.format_uptime(stats["uptime"])
            status_text = f"⏰ {current_time}  •  ⏱️ {uptime_str}"
            if font_small:
                bbox = draw.textbbox((0, 0), status_text, font=font_small)
                status_width = bbox[2] - bbox[0]
                status_x = (640 - status_width) // 2
                draw.text((status_x, 45), status_text, fill=(180, 220, 255), font=font_small)
            
            # Card layout - 2x2 grid of main metrics
            card_width = 290
            card_height = 70
            card_margin = 20
            
            # Row 1: CPU and Memory
            y_start = 75
            
            # CPU Card
            cpu_color = self.get_metric_color(stats["cpu_percent"], self.cpu_thresholds)
            cpu_card = self.draw_metric_card(draw, 25, y_start, card_width, card_height, 
                                           "CPU", f"{stats['cpu_percent']:.1f}", "%", 
                                           stats["cpu_percent"], cpu_color)
            display_image = Image.alpha_composite(display_image.convert('RGBA'), cpu_card).convert('RGB')
            
            # CPU content
            draw.text((35, y_start + 10), "CPU USAGE", fill=(200, 220, 255), font=font_small)
            draw.text((35, y_start + 28), f"{stats['cpu_percent']:.1f}%", fill=cpu_color, font=font_large)
            draw.text((35, y_start + 52), f"Load: {stats['load_avg'][0]:.2f}", fill=(150, 170, 200), font=font_tiny)
            
            # CPU status icon
            self.draw_status_icon(draw, 275, y_start + 20, "cpu", stats["cpu_percent"], self.cpu_thresholds)
            
            # CPU progress bar
            self.draw_metric_bar(draw, 150, y_start + 35, 150, 8, stats["cpu_percent"], 100, cpu_color)
            
            # Memory Card
            memory_color = self.get_metric_color(stats["memory_percent"], self.memory_thresholds)
            memory_card = self.draw_metric_card(draw, 325, y_start, card_width, card_height,
                                              "RAM", f"{stats['memory_percent']:.1f}", "%",
                                              stats["memory_percent"], memory_color)
            display_image = Image.alpha_composite(display_image.convert('RGBA'), memory_card).convert('RGB')
            
            # Memory content
            memory_used_gb = stats["memory_used"] / (1024**3)
            memory_total_gb = stats["memory_total"] / (1024**3)
            draw.text((335, y_start + 10), "MEMORY USAGE", fill=(200, 220, 255), font=font_small)
            draw.text((335, y_start + 28), f"{stats['memory_percent']:.1f}%", fill=memory_color, font=font_large)
            draw.text((335, y_start + 52), f"{memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB", fill=(150, 170, 200), font=font_tiny)
            
            # Memory status icon
            self.draw_status_icon(draw, 575, y_start + 20, "memory", stats["memory_percent"], self.memory_thresholds)
            
            # Memory progress bar
            self.draw_metric_bar(draw, 450, y_start + 35, 150, 8, stats["memory_percent"], 100, memory_color)
            
            # Row 2: Temperature and Disk
            y_start += card_height + card_margin
            
            # Temperature Card
            temp_color = self.get_metric_color(stats["temperature"], self.temp_thresholds)
            temp_card = self.draw_metric_card(draw, 25, y_start, card_width, card_height,
                                            "TEMP", f"{stats['temperature']:.1f}", "°C",
                                            stats["temperature"], temp_color)
            display_image = Image.alpha_composite(display_image.convert('RGBA'), temp_card).convert('RGB')
            
            # Temperature content
            draw.text((35, y_start + 10), "CPU TEMPERATURE", fill=(200, 220, 255), font=font_small)
            draw.text((35, y_start + 28), f"{stats['temperature']:.1f}°C", fill=temp_color, font=font_large)
            temp_status = "OPTIMAL" if stats["temperature"] < 50 else "NORMAL" if stats["temperature"] < 65 else "WARM" if stats["temperature"] < 75 else "HOT"
            draw.text((35, y_start + 52), temp_status, fill=temp_color, font=font_tiny)
            
            # Temperature status icon
            self.draw_status_icon(draw, 275, y_start + 20, "temp", stats["temperature"], self.temp_thresholds)
            
            # Temperature progress bar (scaled 0-100°C)
            self.draw_metric_bar(draw, 150, y_start + 35, 150, 8, stats["temperature"], 100, temp_color)
            
            # Disk Card
            disk_color = self.get_metric_color(stats["disk_percent"], self.disk_thresholds)
            disk_card = self.draw_metric_card(draw, 325, y_start, card_width, card_height,
                                            "DISK", f"{stats['disk_percent']:.1f}", "%",
                                            stats["disk_percent"], disk_color)
            display_image = Image.alpha_composite(display_image.convert('RGBA'), disk_card).convert('RGB')
            
            # Disk content
            draw.text((335, y_start + 10), "DISK USAGE", fill=(200, 220, 255), font=font_small)
            draw.text((335, y_start + 28), f"{stats['disk_percent']:.1f}%", fill=disk_color, font=font_large)
            draw.text((335, y_start + 52), f"{self.format_bytes(stats['disk_used'])} / {self.format_bytes(stats['disk_total'])}", fill=(150, 170, 200), font=font_tiny)
            
            # Disk status icon
            self.draw_status_icon(draw, 575, y_start + 20, "disk", stats["disk_percent"], self.disk_thresholds)
            
            # Disk progress bar
            self.draw_metric_bar(draw, 450, y_start + 35, 150, 8, stats["disk_percent"], 100, disk_color)
            
            # Bottom info panel
            y_info = 240
            info_height = 120
            
            # Info panel background
            info_overlay = Image.new('RGBA', (640, info_height), (0, 0, 0, 0))
            info_draw = ImageDraw.Draw(info_overlay)
            
            # Info panel gradient
            for i in range(info_height):
                factor = i / info_height
                bg_r = int(25 + (20 * factor))
                bg_g = int(35 + (25 * factor))
                bg_b = int(55 + (30 * factor))
                alpha = 160
                info_draw.line([(20, i), (620, i)], fill=(bg_r, bg_g, bg_b, alpha))
            
            # Info panel border
            info_draw.rectangle([20, 0, 620, info_height-1], outline=(80, 120, 160, 255), width=2)
            
            # Composite info panel
            info_positioned = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
            info_positioned.paste(info_overlay, (0, y_info))
            display_image = Image.alpha_composite(display_image.convert('RGBA'), info_positioned).convert('RGB')
            
            # Network and Process Information
            if font_medium:
                # Network section
                draw.text((35, y_info + 15), "NETWORK ACTIVITY", fill=(120, 200, 255), font=font_small)
                network_text = f"↑ {self.format_bytes(stats['bytes_sent'])}   ↓ {self.format_bytes(stats['bytes_recv'])}"
                draw.text((35, y_info + 35), network_text, fill=(100, 255, 150), font=font_medium)
                
                # Process information
                draw.text((350, y_info + 15), "SYSTEM INFO", fill=(120, 200, 255), font=font_small)
                process_text = f"Processes: {stats['process_count']}"
                draw.text((350, y_info + 35), process_text, fill=(255, 200, 100), font=font_medium)
                
                # Kernel info
                draw.text((35, y_info + 65), f"Kernel: {stats['kernel']}", fill=(150, 170, 200), font=font_tiny)
                
                # Last updated
                updated_text = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
                bbox = draw.textbbox((0, 0), updated_text, font=font_tiny)
                update_width = bbox[2] - bbox[0]
                update_x = 620 - update_width
                draw.text((update_x, y_info + 85), updated_text, fill=(120, 140, 180), font=font_tiny)
            
            # Display the enhanced system dashboard
            self.inky.set_image(display_image)
            self.inky.show()
            
            print(f"Enhanced System Dashboard: CPU {stats['cpu_percent']:.1f}%, RAM {stats['memory_percent']:.1f}%, Temp {stats['temperature']:.1f}°C")
            
        except Exception as e:
            print(f"Error displaying system dashboard: {e}")
            self.display_error_message("System Dashboard Error", str(e))
    
    def display_error_message(self, title, message):
        """Display an enhanced error message with modern system theme."""
        # Create enhanced background
        image = self.create_system_background()
        draw = ImageDraw.Draw(image)
        
        # Use font manager for error display
        font_title = font_manager.get_font('title', 24)
        font_text = font_manager.get_font('regular', 16)
        font_small = font_manager.get_font('small', 14)
        
        # Error panel
        panel_x, panel_y = 100, 150
        panel_width, panel_height = 440, 100
        
        # Error panel background
        error_overlay = Image.new('RGBA', (panel_width, panel_height), (0, 0, 0, 0))
        error_draw = ImageDraw.Draw(error_overlay)
        
        # Error panel gradient (red theme)
        for i in range(panel_height):
            factor = i / panel_height
            bg_r = int(60 + (20 * factor))
            bg_g = int(20 + (10 * factor))
            bg_b = int(20 + (10 * factor))
            alpha = 200
            error_draw.line([(0, i), (panel_width, i)], fill=(bg_r, bg_g, bg_b, alpha))
        
        # Error panel border
        error_draw.rectangle([0, 0, panel_width-1, panel_height-1], outline=(255, 100, 100, 255), width=2)
        
        # Position and composite error panel
        error_positioned = Image.new('RGBA', (640, 400), (0, 0, 0, 0))
        error_positioned.paste(error_overlay, (panel_x, panel_y))
        image = Image.alpha_composite(image.convert('RGBA'), error_positioned).convert('RGB')
            
        if font_title:
            # Draw error title with glow
            bbox = draw.textbbox((0, 0), title, font=font_title)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            # Glow effect
            for offset in [(2, 2), (1, 1), (-1, -1), (-2, -2)]:
                draw.text((x + offset[0], 170 + offset[1]), title, fill=(100, 20, 20), font=font_title)
            # Main title
            draw.text((x, 170), title, fill=(255, 150, 150), font=font_title)
            
        if font_text:
            # Draw error message (truncated)
            if len(message) > 50:
                message = message[:47] + "..."
            bbox = draw.textbbox((0, 0), message, font=font_text)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 210), message, fill=(255, 200, 200), font=font_text)
        
        if font_small:
            # Add helpful message
            help_text = "System monitoring will retry automatically"
            bbox = draw.textbbox((0, 0), help_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 235), help_text, fill=(200, 200, 255), font=font_small)
        
        self.inky.set_image(image)
        self.inky.show()
