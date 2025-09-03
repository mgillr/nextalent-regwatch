#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze feed categorization and fix date parsing issues in the Nextalent Regulatory Radar
"""
import os, json, yaml, re
from datetime import datetime, timezone
from urllib.parse import urlparse

UTC = timezone.utc

def now_utc() -> datetime:
    return datetime.now(tz=UTC)

def iso_z(dt: datetime) -> str:
    """Convert datetime to ISO8601 Zulu format"""
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def load_config(path="regwatch.yml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg

def analyze_feed_categorization(regwatch_json_path="out/regwatch.json"):
    """Analyze how feeds are categorized and check for misclassifications"""
    print("Analyzing feed categorization...")
    
    # Load the current regwatch.json
    with open(regwatch_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Load the configuration
    cfg = load_config()
    keywords = cfg.get("keywords", {})
    
    # Count items per section
    section_counts = {section: len(items) for section, items in data["sections"].items()}
    print(f"Current section counts: {section_counts}")
    
    # Analyze source distribution
    source_distribution = {}
    for section, items in data["sections"].items():
        sources = {}
        for item in items:
            source = item.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        source_distribution[section] = sources
    
    print("\nSource distribution by section:")
    for section, sources in source_distribution.items():
        print(f"  {section}:")
        for source, count in sources.items():
            print(f"    - {source}: {count} items")
    
    # Check for potential misclassifications
    print("\nAnalyzing potential misclassifications...")
    misclassified = []
    
    # Source-based hints for classification
    source_hints = {
        "nasa": "space",
        "esa": "space",
        "fcc": "space",
        "easa": "aviation",
        "faa": "aviation",
        "ema": "pharma",
        "fda": "pharma",
        "nhtsa": "automotive",
        "transportation.gov": "automotive",
        "nist": "crossIndustry"
    }
    
    for section, items in data["sections"].items():
        for item in items:
            source = item.get("source", "").lower()
            feed_url = item.get("feed", "").lower()
            title = item.get("title", "").lower()
            
            # Check if source suggests a different section
            for src_key, hint_section in source_hints.items():
                if (src_key in source or src_key in feed_url) and hint_section != section:
                    # Special case for NASA items that might be cross-industry
                    if src_key == "nasa" and section == "crossIndustry":
                        # Check if it's truly cross-industry by looking at keywords
                        cross_industry_keywords = keywords.get("crossIndustry", [])
                        space_keywords = keywords.get("space", [])
                        
                        cross_hits = sum(1 for kw in cross_industry_keywords if kw.lower() in title)
                        space_hits = sum(1 for kw in space_keywords if kw.lower() in title)
                        
                        if cross_hits > space_hits:
                            # Correctly classified as cross-industry
                            continue
                    
                    misclassified.append({
                        "title": item.get("title"),
                        "source": source,
                        "current_section": section,
                        "suggested_section": hint_section,
                        "url": item.get("url")
                    })
    
    if misclassified:
        print("\nPotential misclassifications found:")
        for item in misclassified:
            print(f"  - {item['title']}")
            print(f"    Source: {item['source']}")
            print(f"    Current section: {item['current_section']}")
            print(f"    Suggested section: {item['suggested_section']}")
            print(f"    URL: {item['url']}")
            print()
    else:
        print("No potential misclassifications found.")
    
    # Check if we're using all sources from the config
    print("\nChecking source coverage...")
    config_sources = set()
    for section, urls in cfg.get("sources", {}).items():
        for url in urls:
            if any(url.endswith(ext) for ext in ['.xml', '.rss']) or '/rss' in url or '/feed' in url:
                domain = urlparse(url).netloc
                config_sources.add(domain)
    
    used_sources = set()
    for section, items in data["sections"].items():
        for item in items:
            feed_url = item.get("feed", "")
            if feed_url:
                domain = urlparse(feed_url).netloc
                used_sources.add(domain)
    
    missing_sources = config_sources - used_sources
    if missing_sources:
        print(f"Missing sources from config: {missing_sources}")
    else:
        print("All direct feed sources from config are being used.")
    
    return data

def fix_date_format(regwatch_json_path="out/regwatch.json"):
    """Fix date format issues in the regwatch.json file"""
    print("\nFixing date format issues...")
    
    # Load the current regwatch.json
    with open(regwatch_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Fix the date format in each item
    for section, items in data["sections"].items():
        for item in items:
            # Check if the published date is in the correct ISO format
            published = item.get("published", "")
            if published:
                try:
                    # Try to parse the date
                    if '+' in published or ' ' in published:
                        # Convert from formats like "2025-09-03 00:38:54+00:00"
                        dt = datetime.fromisoformat(published)
                        # Convert to ISO8601 Zulu format
                        item["published"] = iso_z(dt)
                except (ValueError, TypeError) as e:
                    print(f"Error parsing date '{published}': {e}")
                    # If we can't parse it, set to current time
                    item["published"] = iso_z(now_utc())
    
    # Write the fixed data back to the file
    with open(regwatch_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Also update the dated snapshot
    day = datetime.now(tz=UTC).date().isoformat()
    snapshot_path = f"out/regwatch-{day}.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated date formats in {regwatch_json_path} and {snapshot_path}")
    
    # Update widget.js with the fixed data
    update_widget_js(data)
    
    return data

def update_widget_js(data, out_dir="out"):
    """Update widget.js with the fixed data and improved date display"""
    print("\nUpdating widget.js with fixed data and improved date display...")
    
    widget_js = f"""// Nextalent Regulatory Radar Widget
// Generated: {iso_z(now_utc())}
(function() {{
  const data = {json.dumps(data, ensure_ascii=False, indent=2)};
  
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
    
    print("Updated widget.js with fixed data and improved date display")

def update_regwatch_improved_script():
    """Update the regwatch_improved.py script with better date handling"""
    print("\nUpdating regwatch_improved.py with better date handling...")
    
    # Read the current script
    with open("regwatch_improved.py", "r", encoding="utf-8") as f:
        script = f.read()
    
    # Update the build_digest function to ensure proper date formatting
    old_section = """        sections[k] = [
            {
                "title": x["title"],
                "url": x["url"],
                "source": x["source"],
                "summary": x["summary"],
                "published": iso_z(x["published"]) if x["published"] else ""
            } for x in arr
        ]"""
    
    new_section = """        sections[k] = [
            {
                "title": x["title"],
                "url": x["url"],
                "source": x["source"],
                "summary": x["summary"],
                "published": iso_z(x["published"]) if x["published"] else ""
            } for x in arr
        ]"""
    
    # Update the widget.js generation to include better date handling
    old_widget_section = """      for (const item of items) {{
        html += '<li>';
        html += '<a href="' + item.url + '" target="_blank">' + item.title + '</a>';
        html += '<span class="source">' + item.source + '</span>';
        html += '</li>';
      }}"""
    
    new_widget_section = """      for (const item of items) {{
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
      }}"""
    
    # Update the CSS to include date styling
    old_css_section = """      .nextalent-regwatch-widget .source {{
        display: block;
        font-size: 0.8em;
        color: #666;
      }}"""
    
    new_css_section = """      .nextalent-regwatch-widget .source {{
        display: block;
        font-size: 0.8em;
        color: #666;
      }}
      .nextalent-regwatch-widget .date {{
        display: inline-block;
        font-size: 0.8em;
        color: #666;
        margin-right: 10px;
      }}"""
    
    # Apply the changes
    script = script.replace(old_widget_section, new_widget_section)
    script = script.replace(old_css_section, new_css_section)
    
    # Write the updated script
    with open("regwatch_improved.py", "w", encoding="utf-8") as f:
        f.write(script)
    
    print("Updated regwatch_improved.py with better date handling")

def main():
    # Analyze feed categorization
    data = analyze_feed_categorization()
    
    # Fix date format issues
    data = fix_date_format()
    
    # Update the regwatch_improved.py script
    update_regwatch_improved_script()
    
    print("\nAnalysis and fixes completed successfully!")

if __name__ == "__main__":
    main()