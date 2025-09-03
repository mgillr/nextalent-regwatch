#!/usr/bin/env python3
"""
Test script for regwatch.py with a minimal configuration.
"""

import os
import yaml
import json
from regwatch import load_config, discover_feeds, parse_feed, classify, build_digest, write_json, write_snapshot, write_widget_js, write_fallback_html

# Create a minimal test configuration
test_config = {
    "window_hours": 36,
    "max_items": 5,
    "sources": {
        "aviation": ["https://www.faa.gov/rss/"],
        "space": ["https://www.nasa.gov/rss/dyn/breaking_news.rss"]
    },
    "keywords": {
        "aviation": ["FAA", "aircraft", "safety", "pilot"],
        "space": ["NASA", "space", "rocket", "satellite"]
    }
}

# Save the test configuration
with open("test_regwatch.yml", "w") as f:
    yaml.dump(test_config, f)

# Load the test configuration
cfg = load_config("test_regwatch.yml")
print("Configuration loaded successfully")

# Test feed discovery
print("\nTesting feed discovery...")
feeds = discover_feeds("https://www.nasa.gov/news/")
print(f"Discovered {len(feeds)} feeds")

# Test feed parsing
print("\nTesting feed parsing...")
items = parse_feed("https://www.nasa.gov/rss/dyn/breaking_news.rss")
print(f"Parsed {len(items)} items")

# Test classification
if items:
    print("\nTesting classification...")
    item = items[0]
    sector = classify(item, cfg["keywords"])
    print(f"Classified item as: {sector}")

# Test digest building
print("\nTesting digest building...")
digest = build_digest(items, cfg)
print(f"Built digest with {sum(len(v) for v in digest['sections'].values())} items")

# Test output
print("\nTesting output...")
write_json(digest, "test_out")
write_snapshot(digest, "test_out")
write_widget_js(digest, "test_out")
write_fallback_html("test_out")
print("Output files created in test_out directory")

# Clean up
os.remove("test_regwatch.yml")
print("\nTest completed successfully")