"""
Phoenix Arizona News Screen
Displays recent local news headlines with images and engaging layout
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
        
        # News sources with better API coverage
        self.news_sources = [
            {
                'name': 'NewsAPI',
                'type': 'newsapi',
                'url': 'https://newsapi.org/v2/everything',
                'params': {
                    'q': 'Phoenix Arizona OR "Phoenix AZ" OR "Arizona Cardinals" OR "Sky Harbor"',
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 10
                }
            },
            {
                'name': 'Google News RSS',
                'type': 'rss',
                'url': f"https://news.google.com/rss/search?q={config.NEWS_LOCATION_QUERY.replace(' ', '%20')}&hl=en-US&gl=US&ceid=US:en"
            }
        ]
        
        # Enhanced fallback news with images
        self.fallback_news = [
            {
                "title": "Phoenix Breaks Temperature Records as Summer Heat Continues",
                "source": "Arizona Republic",
                "publishedAt": datetime.now().isoformat(),
                "description": "Phoenix metro area experiences unprecedented temperatures as the summer heat wave extends into its third week, affecting local businesses and energy usage.",
                "urlToImage": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=640&h=200&fit=crop"
            },
            {
                "title": "New Technology Hub Opens in Downtown Phoenix",
                "source": "Phoenix Business Journal", 
                "publishedAt": (datetime.now() - timedelta(hours=2)).isoformat(),
                "description": "Major technology companies announce new collaborative workspace in downtown Phoenix, expected to bring hundreds of high-tech jobs to the area.",
                "urlToImage": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=640&h=200&fit=crop"
            },
            {
                "title": "Arizona Cardinals Begin Training Camp with New Acquisitions",
                "source": "ESPN Phoenix",
                "publishedAt": (datetime.now() - timedelta(hours=4)).isoformat(),
                "description": "The Arizona Cardinals start their training camp with several new players, raising hopes for an improved season performance.",
                "urlToImage": "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=640&h=200&fit=crop"
            },
            {
                "title": "Phoenix Sky Harbor Airport Announces Sustainability Initiative",
                "source": "AZ Central",
                "publishedAt": (datetime.now() - timedelta(hours=6)).isoformat(),
                "description": "Sky Harbor International Airport unveils comprehensive environmental sustainability program including solar power expansion and waste reduction.",
                "urlToImage": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=640&h=200&fit=crop"
            }
        ]
    
    def get_news_from_api(self):
        """Fetch news from NewsAPI (requires API key) or use RSS feeds."""
        news_items = []
        
        # Try NewsAPI first if API key is available
        if hasattr(config, 'NEWS_API_KEY') and config.NEWS_API_KEY != "YOUR_NEWS_API_KEY_HERE":
            try:
                source = self.news_sources[0]  # NewsAPI
                params = source['params'].copy()
                params['apiKey'] = config.NEWS_API_KEY
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(source['url'], params=params, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    for article in articles[:5]:  # Top 5 articles
                        if article.get('title') and article.get('description'):
                            news_items.append({
                                'title': article['title'],
                                'description': article['description'],
                                'source': article.get('source', {}).get('name', 'NewsAPI'),
                                'publishedAt': article.get('publishedAt', ''),
                                'urlToImage': article.get('urlToImage', '')
                            })
                    
                    if news_items:
                        return news_items
                        
            except Exception as e:
                print(f"Error fetching from NewsAPI: {e}")
        
        # Fall back to RSS feeds
        try:
            source = self.news_sources[1]  # Google News RSS
            news_items = self.parse_rss_feed(source['url'], 'Google News')
            if news_items:
                return news_items
        except Exception as e:
            print(f"Error fetching from RSS: {e}")
        
        # Return fallback news
        return self.fallback_news
    
    def parse_rss_feed(self, feed_url, source_name):
        """Parse an RSS feed and extract news items."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(feed_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
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
                            'publishedAt': pub_date.text if pub_date is not None else '',
                            'description': description.text.strip() if description is not None and description.text else '',
                            'urlToImage': ''  # RSS usually doesn't include images easily
                        }
                        items.append(news_item)
                
                return items
                
        except Exception as e:
            print(f"Error parsing RSS feed {feed_url}: {e}")
        
        return []
    
    def download_news_image(self, image_url, target_size=(300, 150)):
        """Download and resize news image."""
        if not image_url:
            return None
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Resize to target size
                image = image.resize(target_size, Image.Resampling.LANCZOS)
                
                # Enhance for e-ink display
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.3)
                
                return image
                
        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            
        return None
    
    def create_news_background(self):
        """Create a professional news background."""
        image = Image.new("RGB", (640, 400), (245, 245, 250))
        draw = ImageDraw.Draw(image)
        
        # Create header bar
        draw.rectangle([(0, 0), (640, 60)], fill=(30, 50, 100))
        
        # Add subtle grid pattern
        for x in range(0, 640, 40):
            draw.line([(x, 60), (x, 400)], fill=(240, 240, 245), width=1)
        
        for y in range(60, 400, 30):
            draw.line([(0, y), (640, y)], fill=(240, 240, 245), width=1)
        
        return image
    
    def wrap_text_news(self, text, font, max_width, max_lines=3):
        """Wrap text for news display."""
        words = text.split()
        lines = []
        current_line = []
        
        # Create a temporary image to measure text
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
        """Display news with modern layout and images."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating Phoenix News screen...")
        
        try:
            # Get fresh news
            news_items = self.get_news_from_api()
            
            if news_items:
                print(f"Displaying {len(news_items)} news items")
                self.current_news = news_items
            else:
                print("Using fallback news")
                news_items = self.fallback_news
            
            # Create professional background
            display_image = self.create_news_background()
            draw = ImageDraw.Draw(display_image)
            
            # Load fonts
            try:
                font_header = ImageFont.load_default()
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
                font_small = ImageFont.load_default()
            except:
                font_header = font_title = font_text = font_small = None
            
            # Draw header
            header_text = "PHOENIX NEWS"
            if font_header:
                bbox = draw.textbbox((0, 0), header_text, font=font_header)
                text_width = bbox[2] - bbox[0]
                x = (640 - text_width) // 2
                draw.text((x, 20), header_text, fill=(255, 255, 255), font=font_header)
            
            # Display top 2 news items with larger format
            y_offset = 80
            
            for i, news_item in enumerate(news_items[:2]):
                if y_offset > 350:  # Don't exceed screen bounds
                    break
                    
                # Create news item container
                container_height = 140
                draw.rectangle([(20, y_offset), (620, y_offset + container_height)], 
                             fill=(255, 255, 255), outline=(200, 200, 200), width=2)
                
                # Try to download and display image
                news_image = None
                if news_item.get('urlToImage'):
                    news_image = self.download_news_image(news_item['urlToImage'], (200, 120))
                
                if news_image:
                    # Place image on the left
                    display_image.paste(news_image, (30, y_offset + 10))
                    text_x_start = 250
                    text_width = 350
                else:
                    # No image, use full width for text
                    text_x_start = 40
                    text_width = 560
                
                # Draw title (larger, bold-style by drawing twice with offset)
                title = news_item.get('title', 'No Title')
                if len(title) > 60:
                    title = title[:57] + "..."
                
                if font_title:
                    title_lines = self.wrap_text_news(title, font_title, text_width, 2)
                    for j, line in enumerate(title_lines):
                        y = y_offset + 15 + (j * 18)
                        # Bold effect
                        draw.text((text_x_start + 1, y), line, fill=(20, 40, 80), font=font_title)
                        draw.text((text_x_start, y), line, fill=(20, 40, 80), font=font_title)
                
                # Draw description
                description = news_item.get('description', '')
                if len(description) > 120:
                    description = description[:117] + "..."
                
                if font_text and description:
                    desc_lines = self.wrap_text_news(description, font_text, text_width, 3)
                    for j, line in enumerate(desc_lines):
                        y = y_offset + 55 + (j * 15)
                        draw.text((text_x_start, y), line, fill=(60, 60, 60), font=font_text)
                
                # Draw source and time
                source_text = news_item.get('source', 'Unknown')
                try:
                    pub_time = datetime.fromisoformat(news_item.get('publishedAt', '').replace('Z', '+00:00'))
                    time_text = pub_time.strftime("%H:%M")
                except:
                    time_text = datetime.now().strftime("%H:%M")
                
                info_text = f"{source_text} • {time_text}"
                if font_small:
                    draw.text((text_x_start, y_offset + 115), info_text, fill=(100, 100, 100), font=font_small)
                
                y_offset += container_height + 20
            
            # Display current time
            current_time = datetime.now().strftime("%A, %B %d • %H:%M")
            if font_small:
                bbox = draw.textbbox((0, 0), current_time, font=font_small)
                text_width = bbox[2] - bbox[0]
                x = 640 - text_width - 20
                draw.text((x, 370), current_time, fill=(150, 150, 150), font=font_small)
            
            # Display the news
            self.inky.set_image(display_image)
            self.inky.show()
            
        except Exception as e:
            print(f"Error displaying news: {e}")
            self.display_error_message("News Error", str(e))
    
    def display_error_message(self, title, message):
        """Display an error message on the screen."""
        image = Image.new("RGB", (640, 400), (245, 245, 250))
        draw = ImageDraw.Draw(image)
        
        # Create header bar
        draw.rectangle([(0, 0), (640, 60)], fill=(200, 60, 60))
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        if font:
            # Draw error title in header
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 20), title, fill=(255, 255, 255), font=font)
            
            # Draw error message
            if len(message) > 70:
                message = message[:67] + "..."
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            x = (640 - text_width) // 2
            draw.text((x, 200), message, fill=(100, 100, 100), font=font)
        
        self.inky.set_image(image)
        self.inky.show()
