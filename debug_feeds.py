#!/usr/bin/env python3
import os
import yaml
import requests
from bs4 import BeautifulSoup
import urllib.parse as up
import feedparser
from datetime import datetime, timezone

UTC = timezone.utc

def discover_feeds(url: str):
    """Return list of feed URLs discovered on a landing page."""
    found = []
    print(f"Checking {url}...")
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"  Error: {e}")
        return found
    
    soup = BeautifulSoup(r.text, "html.parser")
    # <link rel="alternate" type="application/rss+xml" href="...">
    for link in soup.find_all("link", rel=lambda x: x and "alternate" in x.lower()):
        t = (link.get("type") or "").lower()
        href = (link.get("href") or "").strip()
        if "rss" in t or "atom" in t or href.endswith(".xml"):
            feed_url = up.urljoin(url, href)
            found.append(feed_url)
            print(f"  Found feed (link): {feed_url}")
    
    # visible anchors containing rss/xml/feed
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        label = (a.get_text() or "").strip().lower()
        if "rss" in label or href.lower().endswith((".rss",".xml","/rss","/feed")):
            feed_url = up.urljoin(url, href)
            found.append(feed_url)
            print(f"  Found feed (anchor): {feed_url}")
    
    # dedupe
    out, seen = [], set()
    for f in found:
        if f.startswith("http") and f not in seen:
            out.append(f); seen.add(f)
    
    if not out:
        print("  No feeds found")
    return out

def check_feed(url):
    print(f"Parsing feed: {url}")
    try:
        d = feedparser.parse(url)
        if not d.entries:
            print(f"  No entries in feed")
            return
        
        print(f"  Found {len(d.entries)} entries")
        for i, e in enumerate(d.entries[:3]):  # Show first 3 entries
            # pick any available timestamp
            pub = None
            for key in ("published_parsed","updated_parsed","created_parsed"):
                t = getattr(e, key, None)
                if t:
                    pub = datetime(*t[:6], tzinfo=UTC); break
            
            title = getattr(e, "title", "").strip() or "(no title)"
            link = getattr(e, "link", url)
            source_title = d.feed.get("title") or up.urlparse(url).netloc
            
            print(f"    Entry {i+1}: {title}")
            print(f"      Source: {source_title}")
            print(f"      URL: {link}")
            print(f"      Date: {pub}")
    except Exception as e:
        print(f"  Error parsing feed: {e}")

def main():
    # Load config
    with open("regwatch.yml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    
    sources = cfg.get("sources", {})
    
    # Check each source
    for section, urls in sources.items():
        print(f"\n=== {section.upper()} ===")
        for url in urls:
            if url.lower().endswith((".xml",".rss","/feed")):
                print(f"Direct feed: {url}")
                check_feed(url)
            else:
                feeds = discover_feeds(url)
                for feed in feeds:
                    check_feed(feed)

if __name__ == "__main__":
    main()