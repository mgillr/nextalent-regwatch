#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test classification logic for Nextalent Regulatory Radar
"""
import json
import yaml
import re
from datetime import datetime

def load_config(path="regwatch.yml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg

def classify_simple(item, keywords, fallback="crossIndustry"):
    """Original classification logic"""
    text = f"{item['title']} {item['summary']}".lower()
    best_section, best_hits = fallback, -1
    for section, kws in keywords.items():
        hits = 0
        for kw in kws:
            if kw.lower() in text:
                hits += 1
        if hits > best_hits:
            best_section, best_hits = section, hits
    return best_section if best_hits >= 0 else fallback

def classify_with_source_hints(item, keywords, fallback="crossIndustry"):
    """Improved classification with source hints"""
    text = f"{item['title']} {item['summary']}".lower()
    
    # Source-based hints for classification
    source_hints = {
        "nasa": "space",
        "esa": "space",
        "easa": "aviation",
        "faa": "aviation",
        "ntsb": "aviation",
        "ema": "pharma",
        "fda": "pharma",
        "nhtsa": "automotive",
        "transportation": "automotive"
    }
    
    # Check source first
    source_lower = item.get('source', '').lower()
    for source_key, section in source_hints.items():
        if source_key in source_lower:
            return section
    
    # Then check content with improved keyword matching
    best_section, best_hits = fallback, 0
    for section, kws in keywords.items():
        hits = 0
        for kw in kws:
            kw_lower = kw.lower()
            # For short keywords (3 chars or less), check for word boundaries
            if len(kw_lower) <= 3:
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', text):
                    hits += 1
            # For longer keywords, simple substring match is fine
            elif kw_lower in text:
                hits += 1
        if hits > best_hits:
            best_section, best_hits = section, hits
    
    return best_section if best_hits > 0 else fallback

def main():
    cfg = load_config()
    keywords = cfg["keywords"]
    
    # Sample items from different sources
    test_items = [
        {
            "title": "EASA publishes Annual Safety Review 2025",
            "summary": "The European Union Aviation Safety Agency (EASA) has published the Annual Safety Review (ASR) 2025, which provides a statistical summary of aviation safety in EASA Member States.",
            "source": "EASA",
            "expected_section": "aviation"
        },
        {
            "title": "NASA 2026 Human Lander Challenge",
            "summary": "NASA's Human Lander Challenge (HuLC) is an initiative supporting its Exploration Systems Development Mission Directorate's (ESDMD's) efforts to explore innovative solutions for a variety of known technology development areas for human landing systems (HLS).",
            "source": "NASA",
            "expected_section": "space"
        },
        {
            "title": "FDA Approves New Drug for Rare Disease",
            "summary": "The Food and Drug Administration today approved a new treatment for a rare genetic disorder affecting fewer than 1,000 patients worldwide.",
            "source": "FDA",
            "expected_section": "pharma"
        },
        {
            "title": "NHTSA Issues New Safety Standards for Autonomous Vehicles",
            "summary": "The National Highway Traffic Safety Administration has issued new safety standards for autonomous vehicles that will take effect in 2026.",
            "source": "NHTSA",
            "expected_section": "automotive"
        },
        {
            "title": "EU Commission Proposes New AI Regulation Framework",
            "summary": "The European Commission has proposed a new regulatory framework for artificial intelligence that aims to address the risks associated with specific uses of AI.",
            "source": "European Commission",
            "expected_section": "crossIndustry"
        },
        {
            "title": "New Guidance on Electric Vehicle Charging Infrastructure",
            "summary": "The Department of Transportation has issued new guidance on the deployment of electric vehicle charging infrastructure along highways and in communities.",
            "source": "Department of Transportation",
            "expected_section": "automotive"
        },
        {
            "title": "Advances in Quantum Computing Pose Risks to Encryption Standards",
            "summary": "NIST researchers warn that advances in quantum computing could break current encryption standards within the next decade.",
            "source": "NIST",
            "expected_section": "crossIndustry"
        },
        {
            "title": "FAA Updates Drone Registration Requirements",
            "summary": "The Federal Aviation Administration has updated its requirements for registering unmanned aerial vehicles (UAVs) or drones.",
            "source": "FAA",
            "expected_section": "aviation"
        },
        {
            "title": "EMA Releases New Guidelines for Biosimilar Approval",
            "summary": "The European Medicines Agency has released new guidelines for the approval of biosimilar medications in the European Union.",
            "source": "EMA",
            "expected_section": "pharma"
        },
        {
            "title": "NASA Artemis Program Update: Lunar Gateway Progress",
            "summary": "NASA provided an update on the Artemis program, focusing on progress with the Lunar Gateway station that will orbit the Moon.",
            "source": "NASA",
            "expected_section": "space"
        }
    ]
    
    print("Testing classification logic...")
    print("\nSimple classification vs. Source-hints classification:")
    print("-" * 80)
    print(f"{'Item':<40} | {'Expected':<15} | {'Simple':<15} | {'Source Hints':<15}")
    print("-" * 80)
    
    simple_correct = 0
    source_hints_correct = 0
    
    for item in test_items:
        simple_result = classify_simple(item, keywords)
        source_hints_result = classify_with_source_hints(item, keywords)
        
        simple_match = "✓" if simple_result == item["expected_section"] else "✗"
        source_hints_match = "✓" if source_hints_result == item["expected_section"] else "✗"
        
        if simple_result == item["expected_section"]:
            simple_correct += 1
        if source_hints_result == item["expected_section"]:
            source_hints_correct += 1
        
        title = item["title"][:35] + "..." if len(item["title"]) > 35 else item["title"]
        print(f"{title:<40} | {item['expected_section']:<15} | {simple_result:<13} {simple_match} | {source_hints_result:<13} {source_hints_match}")
    
    print("-" * 80)
    print(f"Accuracy - Simple: {simple_correct}/{len(test_items)} ({simple_correct/len(test_items)*100:.1f}%), Source Hints: {source_hints_correct}/{len(test_items)} ({source_hints_correct/len(test_items)*100:.1f}%)")
    
    # Now test with real data from NASA feed
    print("\n\nTesting with real NASA feed items...")
    nasa_items = [
        {
            "title": "NASA 2026 Human Lander Challenge",
            "summary": "NASA's Human Lander Challenge (HuLC) is an initiative supporting its Exploration Systems Development Mission Directorate's (ESDMD's) efforts to explore innovative solutions for a variety of known technology development areas for human landing systems (HLS).",
            "source": "NASA"
        },
        {
            "title": "Lydia Rodriguez Builds a Career of Service and Support at NASA",
            "summary": "Lydia Rodriguez is an office administrator in the Flight Operations Directorate's Operations Division and Operations Tools and Procedures Branch at NASA's Johnson Space Center in Houston.",
            "source": "NASA"
        },
        {
            "title": "What's Up: September 2025 Skywatching Tips from NASA",
            "summary": "Saturn's spectacle, a Conjunction, and the Autumnal Equinox Saturn shines throughout the month, a conjunction sparkles in the sky, and we welcome the autumnal equinox.",
            "source": "NASA"
        },
        {
            "title": "Circular Star Trails",
            "summary": "On July 26, 2025, NASA astronaut Nichole Ayers took this long-exposure photograph – taken over 31 minutes from a window inside the International Space Station's Kibo laboratory module – capturing the circular arcs of star trails.",
            "source": "NASA"
        },
        {
            "title": "Advancing Single-Photon Sensing Image Sensors to Enable the Search for Life Beyond Earth",
            "summary": "A NASA-sponsored team is advancing single-photon sensing Complementary Metal-Oxide-Semiconductor (CMOS) detector technology that will enable future NASA astrophysics space missions to search for life on other planets.",
            "source": "NASA"
        },
        {
            "title": "Tech From NASA's Hurricane-hunting TROPICS Flies on Commercial Satellites",
            "summary": "NASA science and American industry have worked hand-in-hand for more than 60 years, transforming novel technologies created with NASA research into commercial products like cochlear implants, memory-foam mattresses, and more.",
            "source": "NASA"
        }
    ]
    
    print("\nClassification of NASA items:")
    print("-" * 80)
    print(f"{'Item':<40} | {'Simple':<15} | {'Source Hints':<15}")
    print("-" * 80)
    
    for item in nasa_items:
        simple_result = classify_simple(item, keywords)
        source_hints_result = classify_with_source_hints(item, keywords)
        
        title = item["title"][:35] + "..." if len(item["title"]) > 35 else item["title"]
        print(f"{title:<40} | {simple_result:<15} | {source_hints_result:<15}")
    
    print("-" * 80)
    
    # Test with EASA items
    print("\n\nTesting with real EASA feed items...")
    easa_items = [
        {
            "title": "EASA launches new film addressing passengers for an even safer, greener future for air travel",
            "summary": "Today, EASA proudly launches its new corporate film, putting the spotlight on the people at the heart of European aviation safety.",
            "source": "EASA"
        },
        {
            "title": "EASA publishes new revision of Easy Access Rules for Standardised European Rules of the Air (SERA)",
            "summary": "The European Union Aviation Safety Agency (EASA) has published Revision from August 2025 of the Easy Access Rules for Standardised European Rules of the Air (SERA).",
            "source": "EASA"
        },
        {
            "title": "EASA publishes Annual Safety Review 2025",
            "summary": "The European Union Aviation Safety Agency (EASA) has published the Annual Safety Review (ASR) 2025, which provides a statistical summary of aviation safety in EASA Member States.",
            "source": "EASA"
        }
    ]
    
    print("\nClassification of EASA items:")
    print("-" * 80)
    print(f"{'Item':<40} | {'Simple':<15} | {'Source Hints':<15}")
    print("-" * 80)
    
    for item in easa_items:
        simple_result = classify_simple(item, keywords)
        source_hints_result = classify_with_source_hints(item, keywords)
        
        title = item["title"][:35] + "..." if len(item["title"]) > 35 else item["title"]
        print(f"{title:<40} | {simple_result:<15} | {source_hints_result:<15}")
    
    print("-" * 80)

if __name__ == "__main__":
    main()