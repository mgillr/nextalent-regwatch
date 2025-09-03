#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refine the RegWatch feed to focus on technology, R&D, and regulatory content
"""
import os, json, yaml, re, time
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import feedparser
import requests

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

def parse_date(date_str):
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        # Try to parse the date
        if '+' in date_str or ' ' in date_str:
            # Convert from formats like "2025-09-03 00:38:54+00:00"
            dt = datetime.fromisoformat(date_str)
            return dt
        else:
            # Try ISO format
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt
    except (ValueError, TypeError) as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

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

def refine_feeds(regwatch_json_path="out/regwatch.json"):
    """Refine the RegWatch feed to focus on technology, R&D, and regulatory content"""
    print("Refining feeds to focus on technology, R&D, and regulatory content...")
    
    # Load the current regwatch.json
    with open(regwatch_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Load the configuration
    cfg = load_config()
    keywords = cfg.get("keywords", {})
    
    # Flatten all keywords into a single list
    all_keywords = []
    for section_keywords in keywords.values():
        all_keywords.extend(section_keywords)
    
    # Remove duplicates
    all_keywords = list(set(all_keywords))
    
    # Filter items in each section
    filtered_data = {
        "lastUpdated": data["lastUpdated"],
        "sections": {}
    }
    
    total_before = 0
    total_after = 0
    
    for section, items in data["sections"].items():
        total_before += len(items)
        filtered_items = [item for item in items if is_tech_focused(item, all_keywords)]
        filtered_data["sections"][section] = filtered_items
        total_after += len(filtered_items)
        
        print(f"Section {section}: {len(items)} items -> {len(filtered_items)} items")
    
    print(f"Total: {total_before} items -> {total_after} items")
    
    # Write the filtered data back to the file
    with open(regwatch_json_path, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    # Also update the dated snapshot
    day = datetime.now(tz=UTC).date().isoformat()
    snapshot_path = f"out/regwatch-{day}.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated {regwatch_json_path} and {snapshot_path} with tech-focused content")
    
    # Update widget.js with the filtered data
    update_widget_js(filtered_data)
    
    return filtered_data

def update_widget_js(data, out_dir="out"):
    """Update widget.js with the filtered data"""
    print("Updating widget.js with tech-focused content...")
    
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
    
    print("Updated widget.js with tech-focused content")

def update_regwatch_improved_script():
    """Update the regwatch_improved.py script to focus on technology, R&D, and regulatory content"""
    print("Updating regwatch_improved.py to focus on technology, R&D, and regulatory content...")
    
    # Create a new function to add to regwatch_improved.py
    new_function = """
def is_tech_focused(item, tech_keywords):
    \"\"\"Check if an item is focused on technology, R&D, or regulatory content\"\"\"
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
"""
    
    # Read the current script
    with open("regwatch_improved.py", "r", encoding="utf-8") as f:
        script = f.read()
    
    # Find the position to insert the new function (before build_digest)
    build_digest_pos = script.find("def build_digest")
    if build_digest_pos == -1:
        print("Could not find build_digest function in regwatch_improved.py")
        return
    
    # Find the last import statement
    import_pos = script.rfind("import", 0, build_digest_pos)
    if import_pos == -1:
        print("Could not find import statements in regwatch_improved.py")
        return
    
    # Find the end of the import block
    import_end_pos = script.find("\n\n", import_pos)
    if import_end_pos == -1:
        print("Could not find end of import block in regwatch_improved.py")
        return
    
    # Insert the new function after the imports
    updated_script = script[:import_end_pos + 2] + new_function + script[import_end_pos + 2:]
    
    # Update the build_digest function to filter items
    old_build_digest = """def build_digest(items: List[dict], cfg: dict) -> dict:
    \"\"\"Build the final digest from collected items\"\"\"
    window = int(cfg["window_hours"])
    cutoff = now_utc() - timedelta(hours=window)
    fresh = [it for it in items if it["published"] and it["published"] >= cutoff]
    
    if not fresh:
        # fallback to latest N across everything
        items_sorted = sorted(items, key=lambda x: x["published"] or datetime(1970,1,1,tzinfo=UTC), reverse=True)
        fresh = items_sorted[: int(cfg["max_items"])]

    # classify
    keywords = cfg["keywords"]
    sections: Dict[str, List[dict]] = {k: [] for k in cfg["sources"].keys()}
    sections.setdefault("crossIndustry", [])
    for it in fresh:
        sec = classify(it, keywords, fallback="crossIndustry")
        sections.setdefault(sec, []).append(it)"""
    
    new_build_digest = """def build_digest(items: List[dict], cfg: dict) -> dict:
    \"\"\"Build the final digest from collected items\"\"\"
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
        sections.setdefault(sec, []).append(it)"""
    
    # Replace the build_digest function
    updated_script = updated_script.replace(old_build_digest, new_build_digest)
    
    # Write the updated script
    with open("regwatch_improved.py", "w", encoding="utf-8") as f:
        f.write(updated_script)
    
    print("Updated regwatch_improved.py to focus on technology, R&D, and regulatory content")

def main():
    # Refine feeds to focus on technology, R&D, and regulatory content
    filtered_data = refine_feeds()
    
    # Update the regwatch_improved.py script
    update_regwatch_improved_script()
    
    print("\nRefinement completed successfully!")

if __name__ == "__main__":
    main()