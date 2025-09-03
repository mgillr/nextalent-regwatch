#!/usr/bin/env python3
"""
RegWatch - Regulatory Watch System
Collects regulatory information from official sources and outputs in a standardized format.
"""

import os
import sys
import json
import logging
import yaml
import feedparser
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pytz
from urllib.parse import urljoin

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.filters.keyword_filter import KeywordFilter
from src.output.json_output import JSONOutput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('regwatch.log')
    ]
)

logger = logging.getLogger(__name__)

def load_config(config_path):
    """
    Load configuration from YAML file.
    
    Args:
        config_path (str): Path to the configuration file.
        
    Returns:
        dict: Configuration dictionary.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        return {
            "window_hours": 36,
            "max_items": 50,
            "sources": {},
            "keywords": {}
        }

def discover_feeds(url):
    """
    Discover RSS/Atom feeds from a webpage.
    
    Args:
        url (str): URL of the webpage.
        
    Returns:
        list: List of feed URLs.
    """
    feeds = []
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Look for link tags with RSS/Atom type
        for link in soup.find_all('link', rel='alternate'):
            if link.get('type') in ['application/rss+xml', 'application/atom+xml']:
                feed_url = link.get('href')
                if feed_url:
                    if not feed_url.startswith('http'):
                        feed_url = urljoin(url, feed_url)
                    feeds.append(feed_url)
        
        # Look for a tags with RSS/feed in href
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if any(term in href.lower() for term in ['rss', 'feed', 'atom']):
                if not href.startswith('http'):
                    href = urljoin(url, href)
                feeds.append(href)
                
        logger.info(f"Discovered {len(feeds)} feeds from {url}")
        return feeds
    except Exception as e:
        logger.error(f"Error discovering feeds from {url}: {e}")
        return []

def parse_feed(feed_url, sector, window_hours):
    """
    Parse an RSS/Atom feed.
    
    Args:
        feed_url (str): URL of the feed.
        sector (str): Sector of the feed.
        window_hours (int): Lookback window in hours.
        
    Returns:
        list: List of items from the feed.
    """
    items = []
    try:
        feed = feedparser.parse(feed_url)
        
        # Get the source name from the feed title or domain
        source = feed.feed.get('title', feed_url.split('/')[2])
        
        # Calculate the cutoff time
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        
        for entry in feed.entries:
            try:
                # Get the publication date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    # If no date is available, use current time
                    pub_date = datetime.now()
                
                # Skip items older than the cutoff time
                if pub_date < cutoff_time:
                    continue
                
                # Get the title and URL
                title = entry.title
                url = entry.link
                
                # Get the description
                description = ""
                if hasattr(entry, 'summary'):
                    description = entry.summary
                elif hasattr(entry, 'description'):
                    description = entry.description
                
                # Clean up the description (remove HTML tags)
                if description:
                    soup = BeautifulSoup(description, 'lxml')
                    description = soup.get_text()
                
                # Create the item
                item = {
                    'title': title,
                    'url': url,
                    'date': pub_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'source': source,
                    'description': description,
                    'sector': sector
                }
                
                items.append(item)
            except Exception as e:
                logger.error(f"Error processing feed entry: {e}")
        
        logger.info(f"Parsed {len(items)} items from {feed_url}")
        return items
    except Exception as e:
        logger.error(f"Error parsing feed {feed_url}: {e}")
        return []

def collect_from_sources(sources, window_hours):
    """
    Collect data from all sources.
    
    Args:
        sources (dict): Dictionary of sources by sector.
        window_hours (int): Lookback window in hours.
        
    Returns:
        list: List of collected items.
    """
    all_items = []
    
    for sector, urls in sources.items():
        logger.info(f"Collecting data for sector: {sector}")
        
        for url in urls:
            try:
                logger.info(f"Processing source: {url}")
                
                # Check if the URL is a feed
                if url.endswith('.xml') or 'rss' in url or 'feed' in url or 'atom' in url:
                    items = parse_feed(url, sector, window_hours)
                    all_items.extend(items)
                else:
                    # Discover feeds from the URL
                    feeds = discover_feeds(url)
                    
                    if feeds:
                        for feed_url in feeds:
                            items = parse_feed(feed_url, sector, window_hours)
                            all_items.extend(items)
                    else:
                        # If no feeds are found, try to scrape the page
                        logger.info(f"No feeds found for {url}, attempting to scrape")
                        # Scraping logic would go here
            except Exception as e:
                logger.error(f"Error processing source {url}: {e}")
    
    logger.info(f"Collected {len(all_items)} items from all sources")
    return all_items

def main():
    """Main function to run the RegWatch system."""
    logger.info("Starting RegWatch collection process")
    
    # Load configuration
    config_path = os.path.join(os.getcwd(), 'regwatch.yml')
    config = load_config(config_path)
    
    # Get configuration values
    window_hours = config.get('window_hours', 36)
    max_items = config.get('max_items', 50)
    sources = config.get('sources', {})
    
    # Initialize filters
    keyword_filter = KeywordFilter(config_path)
    
    # Initialize output handler
    json_output = JSONOutput()
    
    # Collect data from all sources
    all_data = collect_from_sources(sources, window_hours)
    
    # Filter data
    filtered_data = keyword_filter.filter(all_data)
    
    # Generate output
    uk_timezone = pytz.timezone('Europe/London')
    current_time = datetime.now(uk_timezone)
    
    output_data = {
        "lastUpdated": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sections": {
            "aviation": [],
            "space": [],
            "pharma": [],
            "automotive": [],
            "crossIndustry": []
        }
    }
    
    # Categorize filtered data into sections
    for item in filtered_data:
        if item.get('sector') in output_data['sections']:
            output_data['sections'][item['sector']].append(item)
        else:
            # Default to crossIndustry if sector not specified
            output_data['sections']['crossIndustry'].append(item)
    
    # Limit the number of items per section
    for sector in output_data['sections']:
        output_data['sections'][sector] = sorted(
            output_data['sections'][sector],
            key=lambda x: x.get('date', ''),
            reverse=True
        )[:max_items]
    
    # Save output
    json_output.save(output_data)
    
    # Generate widget files
    json_output.generate_widget(output_data)
    
    logger.info("RegWatch collection process completed")

if __name__ == "__main__":
    main()