#!/usr/bin/env python3
import os
import re
import yaml
import json
from datetime import datetime, timezone
import feedparser
from bs4 import BeautifulSoup

UTC = timezone.utc

def improved_classify(item, keywords, fallback="crossIndustry"):
    """
    Improved classification with better keyword matching and source hints
    """
    text = f"{item['title']} {item['summary']}".lower()
    source = item['source'].lower()
    
    # Source-based hints
    source_hints = {
        "nasa": "space",
        "esa": "space",
        "fcc": "space",
        "easa": "aviation",
        "faa": "aviation",
        "ema": "pharma",
        "fda": "pharma",
        "nhtsa": "automotive"
    }
    
    # Check for source hints
    initial_hint = None
    for src_key, section in source_hints.items():
        if src_key in source:
            initial_hint = section
            break
    
    # Improved keyword matching with word boundaries
    best_section, best_hits = initial_hint or fallback, 0
    matches = {}
    
    for section, kws in keywords.items():
        hits = 0
        section_matches = []
        for kw in kws:
            kw_lower = kw.lower()
            # Use word boundary matching for short keywords
            if len(kw_lower) <= 3:
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                if re.search(pattern, text):
                    hits += 1
                    section_matches.append(kw)
            # For longer keywords, simple containment is fine
            elif kw_lower in text:
                hits += 1
                section_matches.append(kw)
        
        matches[section] = section_matches
        if hits > best_hits:
            best_section, best_hits = section, hits
    
    # If no keywords matched but we have a source hint, use that
    if best_hits == 0 and initial_hint:
        best_section = initial_hint
    
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
        
        section, matches = improved_classify(item, keywords)
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
                
    # Propose fix for regwatch.py
    print("\n\nProposed fix for regwatch.py:")
    print("""
def classify(item: dict, keywords: Dict[str, List[str]], fallback="crossIndustry") -> str:
    text = f"{item['title']} {item['summary']}".lower()
    source = item['source'].lower()
    
    # Source-based hints
    source_hints = {
        "nasa": "space",
        "esa": "space",
        "fcc": "space",
        "easa": "aviation",
        "faa": "aviation",
        "ema": "pharma",
        "fda": "pharma",
        "nhtsa": "automotive"
    }
    
    # Check for source hints
    initial_hint = None
    for src_key, section in source_hints.items():
        if src_key in source:
            initial_hint = section
            break
    
    # Improved keyword matching with word boundaries
    best_section, best_hits = initial_hint or fallback, 0
    
    for section, kws in keywords.items():
        hits = 0
        for kw in kws:
            kw_lower = kw.lower()
            # Use word boundary matching for short keywords
            if len(kw_lower) <= 3:
                pattern = r'\\b' + re.escape(kw_lower) + r'\\b'
                if re.search(pattern, text):
                    hits += 1
            # For longer keywords, simple containment is fine
            elif kw_lower in text:
                hits += 1
        
        if hits > best_hits:
            best_section, best_hits = section, hits
    
    # If no keywords matched but we have a source hint, use that
    if best_hits == 0 and initial_hint:
        best_section = initial_hint
    
    return best_section
""")

if __name__ == "__main__":
    main()