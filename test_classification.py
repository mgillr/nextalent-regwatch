#!/usr/bin/env python3
import re
import yaml
import json
import os
from datetime import datetime, timezone

UTC = timezone.utc

def classify(item, keywords, fallback="crossIndustry"):
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

def main():
    # Load config
    with open("regwatch.yml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    
    keywords = cfg.get("keywords", {})
    
    # Test items from different sources
    test_items = [
        {
            "title": "NASA 2026 Human Lander Challenge",
            "summary": "NASA's Human Lander Challenge (HuLC) is an initiative supporting its Exploration Systems Development Mission Directorate's (ESDMD's) efforts to explore innovative solutions for a variety of known technology development areas for human landing systems (HLS).",
            "source": "NASA",
            "published": datetime.now(tz=UTC)
        },
        {
            "title": "EASA publishes new revision of Easy Access Rules for Standardised European Rules of the Air (SERA)",
            "summary": "The European Union Aviation Safety Agency (EASA) published a new revision of the Easy Access Rules for Standardised European Rules of the Air (SERA).",
            "source": "EASA",
            "published": datetime.now(tz=UTC)
        },
        {
            "title": "FDA Approves New Drug for Treatment of Rare Disease",
            "summary": "The U.S. Food and Drug Administration today approved a new drug for the treatment of a rare genetic disorder.",
            "source": "FDA",
            "published": datetime.now(tz=UTC)
        },
        {
            "title": "FCC Adopts New 5-Year Rule for Deorbiting Satellites",
            "summary": "The Federal Communications Commission adopted a new rule requiring satellite operators to deorbit their satellites within 5 years of the end of their mission.",
            "source": "FCC",
            "published": datetime.now(tz=UTC)
        },
        {
            "title": "European Commission Adopts New AI Act",
            "summary": "The European Commission today adopted the AI Act, a new regulation on artificial intelligence that aims to ensure AI systems used in the EU are safe and respect fundamental rights.",
            "source": "European Commission",
            "published": datetime.now(tz=UTC)
        }
    ]
    
    print("Testing classification with sample items:")
    for i, item in enumerate(test_items):
        section = classify(item, keywords)
        print(f"{i+1}. {item['title']} (Source: {item['source']}) -> {section}")
    
    # Now check the current output file
    if os.path.exists("out/regwatch.json"):
        with open("out/regwatch.json", "r") as f:
            current = json.load(f)
        
        print("\nCurrent output file analysis:")
        print(f"Last updated: {current['lastUpdated']}")
        print("Sections:")
        for section, items in current.get("sections", {}).items():
            print(f"  {section}: {len(items)} items")
            for i, item in enumerate(items[:2]):  # Show first 2 items per section
                print(f"    {i+1}. {item['title']} - {item['source']} - {item['date']}")
    
    print("\nWith our improved classification, we should see items properly categorized across all sections.")
    print("The current issue is that only space items are showing up because:")
    print("1. NASA items are being classified as space due to source-based classification")
    print("2. Other sources may not be properly discovered or parsed")
    print("3. Keyword matching may be too broad, causing misclassifications")
    
    print("\nTo fix this, we need to:")
    print("1. Commit our improved classification logic")
    print("2. Trigger a new GitHub Actions workflow run")
    print("3. Check the results to see if items are properly classified across all sections")

if __name__ == "__main__":
    main()