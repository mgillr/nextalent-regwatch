#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nextalent Regulatory Radar collector (Improved Version)
- Reads sources from regwatch.yml (official regulators + EU/US/UK institutions)
- Focuses on direct feed URLs for better reliability
- Parses items, filters by recency, classifies by keywords with source hints
- Outputs (to ./out):
    regwatch.json                 (Lovable schema)
    regwatch-YYYY-MM-DD.json      (dated snapshot for fallback)
    widget.js                     (data + renderer; optional embed)
    index.html                    (standalone fallback page)
"""
import os, sys, json, traceback, re, time
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import feedparser
import yaml


def is_tech_focused(item, tech_keywords):
    """Check if an item is focused on technology, R&D, or regulatory content"""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    
    # Count the number of tech keywords in the text
    tech_keyword_count = sum(1 for kw in tech_keywords if kw.lower() in text)
    
    # Check for regulatory terms
    regulatory_terms = [
        "regulation", "directive", "standard", "compliance", "certification",
        "safety", "security", "guideline", "framework", "policy", "requirement",
        "technical specification", "protocol", "iso", "iec", "etsi", "cen", 
        "cenelec", "astm", "ieee", "itu", "approval", "authorization"
    ]
    regulatory_count = sum(1 for term in regulatory_terms if term in text)
    
    # Check for R&D terms
    rd_terms = [
        "research", "development", "innovation", "technology", "technical", 
        "engineering", "design", "prototype", "testing", "validation", "verification",
        "experiment", "laboratory", "study", "analysis", "methodology", "algorithm",
        "system", "architecture", "implementation", "performance", "efficiency",
        "improvement", "enhancement", "advancement", "breakthrough", "discovery"
    ]
    rd_count = sum(1 for term in rd_terms if term in text)
    
    # Check for non-technical terms that indicate general news
    general_news_terms = [
        "interview", "appointment", "promotion", "hire", "join", "welcome",
        "congratulate", "award", "recognition", "celebrate", "anniversary",
        "event", "conference", "webinar", "workshop", "meeting", "summit",
        "exhibition", "expo", "show", "fair", "festival", "competition",
        "contest", "challenge", "hackathon", "datathon", "week in", "month in",
        "year in", "review", "recap", "summary", "highlights", "roundup"
    ]
    general_news_count = sum(1 for term in general_news_terms if term in text)
    
    # Calculate a relevance score
    relevance_score = tech_keyword_count * 2 + regulatory_count + rd_count - general_news_count
    
    # Return True if the item is tech-focused
    return relevance_score >= 2
UTC = timezone.utc

# ---------- Utils ----------
def now_utc() -> datetime:
    return datetime.now(tz=UTC)

def iso_z(dt: datetime) -> str:
    # ISO8601 Zulu
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

# ---------- Config ----------
def load_config(path="regwatch.yml") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError("regwatch.yml not found")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("window_hours", 168)  # Default to 7 days for better coverage
    cfg.setdefault("max_items", 50)
    cfg.setdefault("sources", {})
    cfg.setdefault("keywords", {})
    return cfg

# ---------- Feed discovery ----------
def get_direct_feeds(sources: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Extract direct feed URLs from sources configuration"""
    feed_map: Dict[str, List[str]] = {}
    for section, urls in sources.items():
        feeds = []
        for u in urls:
            # Only use direct feed URLs (ending with .xml, /rss, etc.)
            if any(u.endswith(ext) for ext in ['.xml', '.rss']) or '/rss' in u or '/feed' in u:
                feeds.append(u)
        feed_map[section] = feeds
    return feed_map

# ---------- Feed parsing ----------
def parse_feed(url: str) -> List[dict]:
    """Parse a feed URL and return a list of items"""
    print(f"Fetching feed: {url}")
    
    # Add User-Agent to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        d = feedparser.parse(url, request_headers=headers)
        items = []
        
        for entry in d.entries[:10]:  # Limit to 10 items per feed
            # Extract publication date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime.fromtimestamp(
                    datetime(*entry.published_parsed[:6]).timestamp(), 
                    tz=UTC
                )
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime.fromtimestamp(
                    datetime(*entry.updated_parsed[:6]).timestamp(), 
                    tz=UTC
                )
            else:
                published = now_utc()
            
            # Extract source
            source = d.feed.title if hasattr(d.feed, 'title') else urlparse(url).netloc
            
            # Extract summary
            summary = ""
            if hasattr(entry, 'summary'):
                summary = entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description
            elif hasattr(entry, 'content') and entry.content:
                summary = entry.content[0].value
                
            # Clean up summary (remove HTML tags)
            summary = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)
            
            # Limit summary length
            if len(summary) > 300:
                summary = summary[:297] + "..."
            
            # Create item
            item = {
                'title': getattr(entry, 'title', '').strip() or '(no title)',
                'summary': summary,
                'source': source,
                'published': published,
                'url': getattr(entry, 'link', url),
                'feed': url
            }
            
            items.append(item)
        
        print(f"Found {len(items)} items in feed: {url}")
        return items
    except Exception as e:
        print(f"Error parsing feed {url}: {e}")
        return []

# ---------- Classification / filtering ----------
def classify(item: dict, keywords: Dict[str, List[str]], fallback="crossIndustry") -> str:
    """Improved classification with source hints"""
    text = f"{item['title']} {item['summary']}".lower()
    source = item.get('source', '').lower()
    feed_url = item.get('feed', '').lower()
    
    # Source-based hints
    source_hints = {
        "nasa": "space",
        "esa": "space",
        "fcc": "space",
        "easa": "aviation",
        "faa": "aviation",
        "ema": "pharma",
        "fda": "pharma",
        "nhtsa": "automotive",
        "transportation.gov": "automotive"
    }
    
    # Check for source hints in both source name and feed URL
    initial_hint = None
    for src_key, section in source_hints.items():
        if src_key in source or src_key in feed_url:
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
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
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

def build_digest(items: List[dict], cfg: dict) -> dict:
    """Build the final digest from collected items"""
    window = int(cfg["window_hours"])
    cutoff = now_utc() - timedelta(hours=window)
    fresh = [it for it in items if it["published"] and it["published"] >= cutoff]
    
    if not fresh:
        # fallback to latest N across everything
        items_sorted = sorted(items, key=lambda x: x["published"] or datetime(1970,1,1,tzinfo=UTC), reverse=True)
        fresh = items_sorted[: int(cfg["max_items"])]

    # Flatten all keywords into a single list for tech focus check
    all_keywords = []
    for section_keywords in cfg["keywords"].values():
        all_keywords.extend(section_keywords)
    all_keywords = list(set(all_keywords))
    
    # Filter for tech-focused items
    fresh = [it for it in fresh if is_tech_focused(it, all_keywords)]

    # classify
    keywords = cfg["keywords"]
    sections: Dict[str, List[dict]] = {k: [] for k in cfg["sources"].keys()}
    sections.setdefault("crossIndustry", [])
    for it in fresh:
        sec = classify(it, keywords, fallback="crossIndustry")
        sections.setdefault(sec, []).append(it)

    # sort and trim each section
    for k in list(sections.keys()):
        arr = sorted(sections[k], key=lambda x: x["published"] or datetime(1970,1,1,tzinfo=UTC), reverse=True)[:12]
        # normalize fields for output
        sections[k] = [
            {
                "title": x["title"],
                "url": x["url"],
                "source": x["source"],
                "summary": x["summary"],
                "published": iso_z(x["published"]) if x["published"] else ""
            } for x in arr
        ]

    return {
        "lastUpdated": iso_z(now_utc()),
        "sections": {k: v for k, v in sections.items() if v}  # drop empty
    }

# ---------- Writers ----------
def write_json(digest: dict, out_dir="out"):
    ensure_dir(out_dir)
    path = os.path.join(out_dir, "regwatch.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)

def write_snapshot(digest: dict, out_dir="out"):
    ensure_dir(out_dir)
    day = datetime.now(tz=UTC).date().isoformat()
    path = os.path.join(out_dir, f"regwatch-{day}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)

def write_widget_js(digest: dict, out_dir="out"):
    """Generate widget.js with embedded data and rendering code"""
    ensure_dir(out_dir)
    
    widget_js = f"""// Nextalent Regulatory Radar Widget
// Generated: {iso_z(now_utc())}
(function() {{
  const data = {json.dumps(digest, ensure_ascii=False, indent=2)};
  
  // Widget rendering code
  function renderWidget(container) {{
    if (!container) return;
    
    // Create widget HTML
    let html = '<div class="nextalent-regwatch-widget">';
    html += '<h2>Regulatory Radar</h2>';
    html += '<p>Last updated: ' + new Date(data.lastUpdated).toLocaleString() + '</p>';
    
    // Render sections
    for (const [section, items] of Object.entries(data.sections)) {{
      if (items.length === 0) continue;
      
      const sectionTitle = section.charAt(0).toUpperCase() + section.slice(1);
      html += '<div class="section">';
      html += '<h3>' + sectionTitle + '</h3>';
      html += '<ul>';
      
      for (const item of items) {{
        // Format the date properly
        let dateStr = '';
        if (item.published) {{
          try {{
            const pubDate = new Date(item.published);
            dateStr = pubDate.toLocaleDateString();
          }} catch (e) {{
            console.error('Error parsing date:', item.published);
          }}
        }}
        
        html += '<li>';
        html += '<a href="' + item.url + '" target="_blank">' + item.title + '</a>';
        if (dateStr) {{
          html += '<span class="date">' + dateStr + '</span>';
        }}
        html += '<span class="source">' + item.source + '</span>';
        html += '</li>';
      }}
      
      html += '</ul>';
      html += '</div>';
    }}
    
    html += '</div>';
    
    // Add CSS
    const style = document.createElement('style');
    style.textContent = `
      .nextalent-regwatch-widget {{
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 5px;
      }}
      .nextalent-regwatch-widget h2 {{
        margin-top: 0;
        color: #333;
      }}
      .nextalent-regwatch-widget .section {{
        margin-bottom: 20px;
      }}
      .nextalent-regwatch-widget h3 {{
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
      }}
      .nextalent-regwatch-widget ul {{
        list-style-type: none;
        padding-left: 0;
      }}
      .nextalent-regwatch-widget li {{
        margin-bottom: 8px;
      }}
      .nextalent-regwatch-widget .source {{
        display: block;
        font-size: 0.8em;
        color: #666;
      }}
      .nextalent-regwatch-widget .date {{
        display: inline-block;
        font-size: 0.8em;
        color: #666;
        margin-right: 10px;
      }}
    `;
    
    // Render to container
    container.innerHTML = html;
    document.head.appendChild(style);
  }}
  
  // Initialize widget when DOM is ready
  function init() {{
    const container = document.getElementById('nextalent-regwatch-container');
    renderWidget(container);
  }}
  
  // Check if DOM is already loaded
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', init);
  }} else {{
    init();
  }}
}})();
"""
    
    with open(os.path.join(out_dir, "widget.js"), "w", encoding="utf-8") as f:
        f.write(widget_js)

def write_fallback_html(out_dir="out"):
    """Generate a standalone HTML page that loads the widget"""
    ensure_dir(out_dir)
    
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nextalent Regulatory Radar</title>
</head>
<body>
  <div id="nextalent-regwatch-container"></div>
  <script src="widget.js"></script>
</body>
</html>
"""
    
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

# ---------- Main ----------
def main():
    cfg = load_config()
    feed_map = get_direct_feeds(cfg["sources"])
    
    # Known working feeds to ensure we have content in each section
    fallback_feeds = {
        "aviation": [
            "https://www.easa.europa.eu/newsroom-and-events/news/feed.xml",
            "https://www.easa.europa.eu/newsroom-and-events/press-releases/feed.xml"
        ],
        "space": [
            "https://www.nasa.gov/feed/",
            "https://www.esa.int/rssfeed/Our_Activities/Space_News"
        ],
        "pharma": [
            "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml"
        ],
        "automotive": [
            "https://www.nhtsa.gov/rss.xml"
        ],
        "crossIndustry": [
            "https://www.nist.gov/news-events/news/rss.xml"
        ]
    }
    
    # Add fallback feeds if a section has no feeds
    for section, feeds in fallback_feeds.items():
        if section not in feed_map or not feed_map[section]:
            feed_map[section] = feeds
    
    # Collect items from all feeds
    all_items = []
    for section, feeds in feed_map.items():
        print(f"Processing {len(feeds)} feeds for section: {section}")
        for url in feeds:
            try:
                items = parse_feed(url)
                all_items.extend(items)
                # Add a small delay to avoid overwhelming servers
                time.sleep(1)
            except Exception as e:
                print(f"Error processing feed {url}: {e}")
    
    if not all_items:
        print("No items fetched. Check feed URLs and network connectivity.")
    
    # Build and write output
    digest = build_digest(all_items, cfg)
    write_json(digest)
    write_snapshot(digest)
    write_widget_js(digest)
    write_fallback_html()
    
    # Print summary
    print("\nClassification summary:")
    for section, items in digest["sections"].items():
        print(f"- {section}: {len(items)} items")
    
    print("\nGenerated output files in ./out")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)