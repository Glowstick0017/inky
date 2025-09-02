"""
Phoenix Arizona News Screen
Displays recent local news headlines from Phoenix, Arizona
Updates every 30 minutes with fresh news from RSS feeds
"""

import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from .base_screen import BaseScreen
import config

class NewsScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.NEWS_UPDATE_INTERVAL
        self.current_news = []
        
        # RSS feeds for Phoenix area news (no API keys required)
        self.rss_feeds = [
            {
                'url': 'https://www.azcentral.com/rss/news/',
                'source': 'Arizona Republic'
            },
            {
                'url': 'https://www.abc15.com/rss.xml',
                'source': 'ABC15 Arizona'
            },
            {
                'url': 'https://www.fox10phoenix.com/rss.xml',
                'source': 'FOX 10 Phoenix'
            },
            {
                'url': 'https://ktar.com/feed/',
                'source': 'KTAR News'
            }
        ]
        
        # Alternative: Google News RSS (no API key needed)
        self.google_news_url = f"https://news.google.com/rss/search?q={config.NEWS_LOCATION_QUERY.replace(' ', '%20')}&hl=en-US&gl=US&ceid=US:en"
        
        # Fallback news for when API is unavailable
        self.fallback_news = [
            {
                "title": "Phoenix Weather Update: Sunny Skies Continue",
                "source": "Arizona Republic",
                "publishedAt": datetime.now().isoformat(),
                "description": "Beautiful weather continues across the Phoenix metro area with clear skies and mild temperatures."
            },
            {
                "title": "New Development Project Announced in Downtown Phoenix",
                "source": "Phoenix Business Journal", 
                "publishedAt": (datetime.now() - timedelta(hours=2)).isoformat(),
                "description": "City officials announce major mixed-use development project in the heart of downtown Phoenix."
            },
            {
                "title": "Arizona Cardinals Training Camp Update",
                "source": "ESPN Phoenix",
                "publishedAt": (datetime.now() - timedelta(hours=4)).isoformat(),
                "description": "Latest updates from the Arizona Cardinals training camp preparations for the upcoming season."
            },
            {
                "title": "Phoenix Sky Harbor Airport Expansion Plans",
                "source": "AZ Central",
                "publishedAt": (datetime.now() - timedelta(hours=6)).isoformat(),
                "description": "Sky Harbor International Airport announces new terminal expansion to accommodate growing passenger traffic."
            },
            {
                "title": "Local Phoenix Business Wins State Award",
                "source": "Phoenix Magazine",
                "publishedAt": (datetime.now() - timedelta(hours=8)).isoformat(),
                "description": "Local Phoenix technology company receives recognition for innovation and community contribution."
            }
        ]
    
    def parse_rss_feed(self, feed_url, source_name):
        """Parse an RSS feed and extract news items."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(feed_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                # Handle different RSS formats
                items = []
                
                # Standard RSS format
                for item in root.findall('.//item')[:5]:  # Get top 5 items
                    title = item.find('title')
                    pub_date = item.find('pubDate')
                    description = item.find('description')
                    
                    if title is not None and title.text:
                        news_item = {
                            'title': title.text.strip(),
                            'source': source_name,
                            'publishedAt': pub_date.text if pub_date is not None else datetime.now().isoformat(),
                            'description': description.text if description is not None else ''
                        }
                        items.append(news_item)
                
                # Also try Atom format
                if not items:
                    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry')[:5]:
                        title = entry.find('.//{http://www.w3.org/2005/Atom}title')
                        updated = entry.find('.//{http://www.w3.org/2005/Atom}updated')
                        summary = entry.find('.//{http://www.w3.org/2005/Atom}summary')
                        
                        if title is not None and title.text:
                            news_item = {
                                'title': title.text.strip(),
                                'source': source_name,
                                'publishedAt': updated.text if updated is not None else datetime.now().isoformat(),
                                'description': summary.text if summary is not None else ''
                            }
                            items.append(news_item)
                
                return items
                
        except Exception as e:
            print(f"Error parsing RSS feed {feed_url}: {e}")
            
        return []

    def fetch_phoenix_news(self):
        """Fetch recent news from Phoenix area RSS feeds."""
        all_news = []
        
        # First try Google News for Phoenix
        try:
            google_items = self.parse_rss_feed(self.google_news_url, 'Google News')
            all_news.extend(google_items[:3])  # Get top 3 from Google
            print(f"Fetched {len(google_items)} items from Google News")
        except Exception as e:
            print(f"Failed to fetch from Google News: {e}")
        
        # Try each local RSS feed
        for feed_info in self.rss_feeds:
            try:
                items = self.parse_rss_feed(feed_info['url'], feed_info['source'])
                all_news.extend(items[:2])  # Get top 2 from each local source
                print(f"Fetched {len(items)} items from {feed_info['source']}")
            except Exception as e:
                print(f"Failed to fetch from {feed_info['source']}: {e}")
        
        # Filter for Phoenix-related content from local sources
        phoenix_keywords = [
            'phoenix', 'arizona', 'az', 'scottsdale', 'tempe', 'mesa', 
            'glendale', 'chandler', 'peoria', 'surprise', 'avondale',
            'cardinals', 'diamondbacks', 'suns', 'coyotes', 'sky harbor'
        ]
        
        phoenix_news = []
        for item in all_news:
            title_lower = item['title'].lower()
            desc_lower = item.get('description', '').lower()
            
            # Always include Google News items (already filtered) or local items with Phoenix keywords
            if 'Google News' in item['source'] or any(keyword in title_lower or keyword in desc_lower for keyword in phoenix_keywords):
                phoenix_news.append(item)
        
        # Sort by publication date (most recent first)
        try:
            phoenix_news.sort(key=lambda x: self.parse_date(x['publishedAt']), reverse=True)
        except:
            pass  # Keep original order if date parsing fails
        
        # Remove duplicates based on title similarity
        unique_news = []
        for item in phoenix_news:
            title_words = set(item['title'].lower().split())
            is_duplicate = False
            
            for existing in unique_news:
                existing_words = set(existing['title'].lower().split())
                # If more than 70% of words match, consider it a duplicate
                if len(title_words & existing_words) / max(len(title_words), len(existing_words)) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_news.append(item)
        
        # Return top 4 items, or fallback if no news found
        if unique_news:
            return unique_news[:4]
        else:
            return self.fallback_news[:4]
    
    def parse_date(self, date_string):
        """Parse various date formats from RSS feeds."""
        import email.utils
        
        try:
            # Try RFC 2822 format (common in RSS)
            time_tuple = email.utils.parsedate_tz(date_string)
            if time_tuple:
                return datetime(*time_tuple[:6])
        except:
            pass
        
        try:
            # Try ISO format
            return datetime.fromisoformat(date_string.replace('Z', '+00:00').replace('+00:00', ''))
        except:
            pass
        
        # Return current time if parsing fails
        return datetime.now()
    
    def format_time_ago(self, published_at):
        """Format the published time as 'X hours ago' or 'X minutes ago'."""
        try:
            # Parse the ISO timestamp
            if published_at.endswith('Z'):
                published_at = published_at[:-1] + '+00:00'
            
            # Handle different datetime formats
            try:
                published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except:
                # Try parsing without timezone info
                published_time = datetime.fromisoformat(published_at[:19])
            
            now = datetime.now()
            
            # Make published_time timezone-naive for comparison
            if published_time.tzinfo:
                published_time = published_time.replace(tzinfo=None)
            
            time_diff = now - published_time
            
            if time_diff.days > 0:
                return f"{time_diff.days}d ago"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                return f"{hours}h ago"
            elif time_diff.seconds > 60:
                minutes = time_diff.seconds // 60
                return f"{minutes}m ago"
            else:
                return "Just now"
                
        except Exception as e:
            print(f"Error formatting time: {e}")
            return "Recent"
    
    def truncate_text(self, text, max_length):
        """Truncate text to fit within specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within specified width."""
        if not font:
            # Simple fallback wrapping
            words = text.split()
            chars_per_line = max_width // 8  # Rough estimate
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= chars_per_line:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            
            # Create a temporary image to measure text
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def display(self):
        """Display the Phoenix area news."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Phoenix News screen...")
        
        try:
            # Fetch latest news
            news_items = self.fetch_phoenix_news()
            self.current_news = news_items
            
            # Create display image
            image = Image.new("RGB", (self.inky.width, self.inky.height), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Load fonts
            try:
                font_header = ImageFont.load_default()
                font_title = ImageFont.load_default()
                font_meta = ImageFont.load_default()
            except:
                font_header = None
                font_title = None
                font_meta = None
            
            # Draw header
            header_text = "Phoenix Arizona News"
            if font_header:
                bbox = draw.textbbox((0, 0), header_text, font=font_header)
                text_width = bbox[2] - bbox[0]
                x = (self.inky.width - text_width) // 2
                draw.text((x, 10), header_text, fill=(0, 50, 100), font=font_header)
            
            # Draw header underline
            draw.line([50, 30, self.inky.width - 50, 30], fill=(0, 50, 100), width=2)
            
            # Display news items
            y_pos = 45
            max_items = min(4, len(news_items))  # Show up to 4 news items
            
            for i, item in enumerate(news_items[:max_items]):
                if y_pos > self.inky.height - 50:  # Leave space at bottom
                    break
                
                # News item number
                item_number = f"{i+1}."
                if font_title:
                    draw.text((10, y_pos), item_number, fill=(100, 100, 100), font=font_title)
                
                # Title (wrapped and truncated)
                title = self.truncate_text(item['title'], 80)
                title_lines = self.wrap_text(title, font_title, self.inky.width - 50)
                
                title_y = y_pos
                for line in title_lines[:2]:  # Max 2 lines per title
                    if font_title:
                        draw.text((30, title_y), line, fill=(0, 0, 0), font=font_title)
                    title_y += 15
                
                # Source and time
                source = item['source']
                time_ago = self.format_time_ago(item['publishedAt'])
                meta_text = f"{source} • {time_ago}"
                
                if font_meta:
                    draw.text((30, title_y + 2), meta_text, fill=(120, 120, 120), font=font_meta)
                
                # Separator line
                separator_y = title_y + 20
                if i < max_items - 1:  # Don't draw line after last item
                    draw.line([30, separator_y, self.inky.width - 30, separator_y], 
                             fill=(200, 200, 200), width=1)
                
                y_pos = separator_y + 15
            
            # Footer with update time
            now = datetime.now()
            footer_text = f"Updated: {now.strftime('%m/%d %H:%M')}"
            if font_meta:
                bbox = draw.textbbox((0, 0), footer_text, font=font_meta)
                text_width = bbox[2] - bbox[0]
                x = self.inky.width - text_width - 10
                draw.text((x, self.inky.height - 15), footer_text, fill=(150, 150, 150), font=font_meta)
            
            # News icon/indicator
            if font_header:
                draw.text((10, 10), "📰", fill=(0, 50, 100), font=font_header)
            
            # Convert to Inky's palette and display
            self.inky.set_image(image)
            self.inky.show()
            
            print(f"Displayed {len(news_items)} news items")
            
        except Exception as e:
            print(f"Error displaying news: {e}")
            self.display_error_message("News Error", str(e))
    
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
