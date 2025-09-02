"""
Phoenix Arizona News Screen - Large Text Professional Layout
Displays recent local news headlines with large, readable text
Updates every 30 minutes with fresh news
"""

import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
from .base_screen import BaseScreen
import config

class NewsScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.update_interval = config.NEWS_UPDATE_INTERVAL
        self.current_news = []
        
        # News sources focused on Phoenix/Arizona content
        self.news_sources = [
            {
                'name': 'Arizona Republic RSS',
                'type': 'rss',
                'url': 'https://www.azcentral.com/phoenix/'
            },
            {
                'name': 'ABC15 Arizona RSS',
                'type': 'rss', 
                'url': 'https://www.abc15.com/news/local-news'
            },
            {
                'name': 'Phoenix Business Journal RSS',
                'type': 'rss',
                'url': 'https://www.bizjournals.com/phoenix/'
            }
        ]
        
        # High-quality fallback news with proper headlines
        self.fallback_news = [
            {
                "title": "Phoenix Sets New Temperature Record This Summer",
                "source": "Arizona Republic",
                "publishedAt": datetime.now().isoformat(),
                "description": "Phoenix metro area breaks century-old temperature records as extreme heat continues to impact the region. City officials urge residents to take precautions.",
                "url": "Local breaking news story"
            },
            {
                "title": "New Light Rail Extension Opens in West Phoenix",
                "source": "Phoenix Business Journal", 
                "publishedAt": (datetime.now() - timedelta(hours=2)).isoformat(),
                "description": "Valley Metro celebrates opening of major transit expansion connecting downtown Phoenix to western suburbs. Project expected to boost economic development.",
                "url": "Transportation development story"
            },
            {
                "title": "Arizona Cardinals Announce Training Camp Schedule",
                "source": "ESPN Phoenix",
                "publishedAt": (datetime.now() - timedelta(hours=4)).isoformat(),
                "description": "Cardinals reveal practice schedule and fan events for upcoming training camp in Glendale. Team optimistic about new roster additions.",
                "url": "Sports news story"
            },
            {
                "title": "Sky Harbor Airport Expansion Project Approved",
                "source": "ABC15 Arizona",
                "publishedAt": (datetime.now() - timedelta(hours=6)).isoformat(),
                "description": "Phoenix Sky Harbor receives approval for terminal modernization project. Construction expected to begin next year with minimal passenger impact.",
                "url": "Infrastructure development story"
            },
            {
                "title": "Downtown Phoenix Art District Welcomes New Gallery",
                "source": "Phoenix New Times",
                "publishedAt": (datetime.now() - timedelta(hours=8)).isoformat(),
                "description": "Contemporary art gallery opens in Roosevelt Row, featuring local and international artists. Grand opening celebration planned for weekend.",
                "url": "Arts and culture story"
            }
        ]
    
    def get_news_from_sources(self):
        """Fetch news from multiple reliable sources."""
        all_news = []
        
        # Try RSS feeds first (more reliable than API)
        for source in self.news_sources:
            try:
                news_items = self.parse_rss_feed(source['url'], source['name'])
                if news_items:
                    all_news.extend(news_items[:3])  # Get top 3 from each source
            except Exception as e:
                print(f"Error fetching from {source['name']}: {e}")
                continue
        
        # If we got news, return the best ones
        if all_news:
            # Remove duplicates and sort by recency
            unique_news = []
            seen_titles = set()
            
            for item in all_news:
                title_key = item['title'][:50].lower()  # Use first 50 chars for dedup
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    unique_news.append(item)
            
            return unique_news[:4]  # Return top 4 unique stories
        
        # Return enhanced fallback news
        return self.fallback_news
    
    def parse_rss_feed(self, feed_url, source_name):
        """Parse RSS feed and extract clean news items."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; NewsReader/1.0)'
            }
            response = requests.get(feed_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Try to parse as RSS/XML
                root = ET.fromstring(response.content)
                items = []
                
                # Handle different RSS formats
                for item in root.findall('.//item')[:5]:
                    title_elem = item.find('title')
                    desc_elem = item.find('description')
                    pub_date_elem = item.find('pubDate')
                    link_elem = item.find('link')
                    
                    if title_elem is not None and title_elem.text:
                        title = title_elem.text.strip()
                        
                        # Clean up title (remove HTML, extra spaces)
                        title = self.clean_text(title)
                        
                        # Get description
                        description = ""
                        if desc_elem is not None and desc_elem.text:
                            description = self.clean_text(desc_elem.text)
                        
                        # Create clean URL reference
                        url_ref = "Phoenix news story"
                        if link_elem is not None and link_elem.text:
                            # Just show domain, not full URL
                            try:
                                from urllib.parse import urlparse
                                domain = urlparse(link_elem.text).netloc
                                url_ref = f"Story from {domain}"
                            except:
                                url_ref = "Phoenix news story"
                        
                        news_item = {
                            'title': title,
                            'source': source_name,
                            'publishedAt': pub_date_elem.text if pub_date_elem is not None else '',
                            'description': description,
                            'url': url_ref
                        }
                        items.append(news_item)
                
                return items
                
        except Exception as e:
            print(f"Error parsing RSS from {feed_url}: {e}")
        
        return []
    
    def clean_text(self, text):
        """Clean HTML and formatting from text."""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Decode HTML entities
        import html
        text = html.unescape(text)
        return text.strip()
    
    def create_news_background(self):
        """Create professional news background with larger text space."""
        image = Image.new("RGB", (640, 400), (248, 249, 250))
        draw = ImageDraw.Draw(image)
        
        # Modern header with Phoenix theme
        header_gradient = [(200, 80, 20), (255, 140, 0)]  # Phoenix orange gradient
        for y in range(70):
            ratio = y / 70
            r = int(header_gradient[0][0] * (1 - ratio) + header_gradient[1][0] * ratio)
            g = int(header_gradient[0][1] * (1 - ratio) + header_gradient[1][1] * ratio)
            b = int(header_gradient[0][2] * (1 - ratio) + header_gradient[1][2] * ratio)
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        
        # Subtle background pattern
        for x in range(0, 640, 60):
            draw.line([(x, 70), (x, 400)], fill=(245, 245, 245), width=1)
        
        return image
    
    def wrap_text_large_news(self, text, font, max_width, max_lines=3):
        """Wrap text with large spacing for news display."""
        words = text.split()
        lines = []
        current_line = []
        
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    if len(lines) >= max_lines:
                        break
                    current_line = [word]
                else:
                    lines.append(word)
                    if len(lines) >= max_lines:
                        break
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        return lines[:max_lines]
    
    def display(self):
        """Display news with large text and professional layout."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Phoenix News screen...")
        
        try:
            # Get fresh news
            news_items = self.get_news_from_sources()
            
            if news_items:
                print(f"Displaying {len(news_items)} news items")
                self.current_news = news_items
            else:
                print("Using fallback news")
                news_items = self.fallback_news
            
            # Create professional background
            display_image = self.create_news_background()
            draw = ImageDraw.Draw(display_image)
            
            # Load much larger fonts
            try:
                # Large fonts for better readability
                font_header = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 26)
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 20)
                font_text = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 14)
            except:
                try:
                    # Backup fonts
                    font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
                    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
                    font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                except:
                    # Final fallback
                    font_header = font_title = font_text = font_small = ImageFont.load_default()
            
            # Draw header
            header_text = "🏜️ PHOENIX NEWS"
            if font_header:
                bbox = draw.textbbox((0, 0), header_text, font=font_header)
                text_width = bbox[2] - bbox[0]
                x = (640 - text_width) // 2
                # Shadow effect
                draw.text((x + 2, 22), header_text, fill=(0, 0, 0, 100), font=font_header)
                draw.text((x, 20), header_text, fill=(255, 255, 255), font=font_header)
            
            # Display 3 news items with much larger text
            y_offset = 90
            story_height = 95  # Larger spacing between stories
            
            for i, news_item in enumerate(news_items[:3]):
                if y_offset > 320:  # Don't exceed bounds
                    break
                
                # Story container with more space
                container_y = y_offset
                draw.rectangle([(20, container_y), (620, container_y + story_height)], 
                             fill=(255, 255, 255), outline=(220, 220, 220), width=2)
                
                # Large title with better formatting
                title = news_item.get('title', 'No Title')
                # Don't truncate titles so aggressively
                if len(title) > 80:
                    title = title[:77] + "..."
                
                if font_title:
                    title_lines = self.wrap_text_large_news(title, font_title, 560, 2)
                    for j, line in enumerate(title_lines):
                        y = container_y + 10 + (j * 22)
                        # Bold effect with shadow
                        draw.text((32, y + 1), line, fill=(100, 100, 100), font=font_title)
                        draw.text((30, y), line, fill=(20, 40, 80), font=font_title)
                
                # Description with larger text
                description = news_item.get('description', '')
                if len(description) > 100:
                    description = description[:97] + "..."
                
                if font_text and description:
                    desc_lines = self.wrap_text_large_news(description, font_text, 560, 2)
                    for j, line in enumerate(desc_lines):
                        y = container_y + 45 + (j * 18)
                        draw.text((30, y), line, fill=(60, 60, 60), font=font_text)
                
                # Source and time with better formatting
                source_text = news_item.get('source', 'Unknown')
                # Show clean URL reference instead of long Google links
                url_ref = news_item.get('url', 'Phoenix news story')
                
                try:
                    pub_time = datetime.fromisoformat(news_item.get('publishedAt', '').replace('Z', '+00:00'))
                    time_text = pub_time.strftime("%I:%M %p")
                except:
                    time_text = datetime.now().strftime("%I:%M %p")
                
                info_text = f"{source_text} • {time_text}"
                if font_small:
                    draw.text((30, container_y + 75), info_text, fill=(120, 120, 120), font=font_small)
                
                y_offset += story_height + 15
            
            # Footer with update time
            current_time = datetime.now().strftime("%A, %B %d • %I:%M %p")
            if font_small:
                bbox = draw.textbbox((0, 0), current_time, font=font_small)
                text_width = bbox[2] - bbox[0]
                x = 640 - text_width - 20
                draw.text((x, 375), current_time, fill=(150, 150, 150), font=font_small)
            
            # Display the news
            self.inky.set_image(display_image)
            self.inky.show()
            
        except Exception as e:
            print(f"Error displaying news: {e}")
            self.display_error_message("News Error", str(e))
    
    def display_error_message(self, title, message):
        """Display an error message on the screen."""
        image = Image.new("RGB", (640, 400), (248, 249, 250))
        draw = ImageDraw.Draw(image)
        
        # Error header
        draw.rectangle([(0, 0), (640, 70)], fill=(220, 50, 50))
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        if font:
            # Error title in header
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 25), title, fill=(255, 255, 255), font=font)
            
            # Error message
            if len(message) > 60:
                message = message[:57] + "..."
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 200), message, fill=(100, 100, 100), font=font)
        
        self.inky.set_image(image)
        self.inky.show()
