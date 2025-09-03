#!/usr/bin/env python3
import os
import yaml
import json
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone

UTC = timezone.utc

def classify(item, keywords, fallback="crossIndustry"):
    text = f"{item['title']} {item['summary']}".lower()
    best_section, best_hits = fallback, -1
    matches = {}
    
    for section, kws in keywords.items():
        hits = 0
        section_matches = []
        for kw in kws:
            kw_lower = kw.lower()
            if kw_lower in text:
                hits += 1
                section_matches.append(kw)
        
        matches[section] = section_matches
        if hits > best_hits:
            best_section, best_hits = section, hits
    
    return best_section, matches

def parse_feed(url):
    try:
        d = feedparser.parse(url)
        out = []
        for e in d.entries:
            # pick any available timestamp
            pub = None
            for key in ("published_parsed","updated_parsed","created_parsed"):
                t = getattr(e, key, None)
                if t:
                    pub = datetime(*t[:6], tzinfo=UTC); break
            
            title = getattr(e, "title", "").strip() or "(no title)"
            link = getattr(e, "link", url)
            # clean summary text
            summary_html = getattr(e, "summary", "") or ""
            summary = BeautifulSoup(summary_html, "html.parser").get_text(" ", strip=True)
            source_title = d.feed.get("title") or url.split("/")[2]
            
            out.append({
                "title": title,
                "url": link,
                "summary": summary,
                "published": pub,
                "source": source_title,
                "feed": url
            })
        return out
    except Exception as e:
        print(f"Error parsing feed {url}: {e}")
        return []

def main():
    # Load config
    with open("regwatch.yml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    
    keywords = cfg.get("keywords", {})
    
    # Test with NASA feed (known to work)
    nasa_feed = "https://www.nasa.gov/feed/"
    print(f"Testing with NASA feed: {nasa_feed}")
    
    items = parse_feed(nasa_feed)
    print(f"Found {len(items)} items in NASA feed")
    
    for i, item in enumerate(items[:5]):  # Check first 5 items
        print(f"\nItem {i+1}: {item['title']}")
        print(f"  Source: {item['source']}")
        print(f"  Date: {item['published']}")
        print(f"  Summary: {item['summary'][:100]}...")
        
        section, matches = classify(item, keywords)
        print(f"  Classified as: {section}")
        print("  Keyword matches:")
        for sec, kws in matches.items():
            if kws:
                print(f"    {sec}: {', '.join(kws)}")
    
    # Now check the current output file
    if os.path.exists("out/regwatch.json"):
        with open("out/regwatch.json", "r") as f:
            current = json.load(f)
        
        print("\n\nCurrent output file analysis:")
        print(f"Last updated: {current['lastUpdated']}")
        print("Sections:")
        for section, items in current.get("sections", {}).items():
            print(f"  {section}: {len(items)} items")
            for i, item in enumerate(items[:2]):  # Show first 2 items per section
                print(f"    {i+1}. {item['title']} - {item['source']} - {item['date']}")

if __name__ == "__main__":
    main()