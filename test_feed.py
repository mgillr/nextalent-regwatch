#!/usr/bin/env python3
"""
Test script to parse a single RSS feed.
"""

import sys
import logging
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_feed(feed_url):
    """
    Test parsing an RSS/Atom feed.
    
    Args:
        feed_url (str): URL of the feed.
    """
    logger.info(f"Testing feed: {feed_url}")
    
    try:
        feed = feedparser.parse(feed_url)
        
        logger.info(f"Feed title: {feed.feed.get('title', 'Unknown')}")
        logger.info(f"Feed description: {feed.feed.get('description', 'None')}")
        logger.info(f"Number of entries: {len(feed.entries)}")
        
        if feed.entries:
            entry = feed.entries[0]
            logger.info("\nFirst entry:")
            logger.info(f"Title: {entry.title}")
            logger.info(f"Link: {entry.link}")
            
            if hasattr(entry, 'published'):
                logger.info(f"Published: {entry.published}")
            elif hasattr(entry, 'updated'):
                logger.info(f"Updated: {entry.updated}")
            
            if hasattr(entry, 'summary'):
                summary = entry.summary
                soup = BeautifulSoup(summary, 'lxml')
                logger.info(f"Summary: {soup.get_text()[:200]}...")
            
    except Exception as e:
        logger.error(f"Error parsing feed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Please provide a feed URL")
        logger.info("Usage: python test_feed.py <feed_url>")
        sys.exit(1)
    
    feed_url = sys.argv[1]
    test_feed(feed_url)