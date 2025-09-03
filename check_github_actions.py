#!/usr/bin/env python3
import os
import requests
import json
import yaml
from datetime import datetime

def check_github_pages():
    print("Checking GitHub Pages output:")
    try:
        r = requests.get("https://mgillr.github.io/nextalent-regwatch/regwatch.json")
        r.raise_for_status()
        data = r.json()
        
        print(f"  Last updated: {data.get('lastUpdated', 'unknown')}")
        
        sections = data.get('sections', {})
        print("  Sections in output:")
        for section, items in sections.items():
            print(f"    {section}: {len(items)} items")
            
        # Check for empty sections
        empty_sections = []
        for section in ['aviation', 'space', 'pharma', 'automotive', 'crossIndustry']:
            if section not in sections or not sections[section]:
                empty_sections.append(section)
        
        if empty_sections:
            print("  Empty sections:")
            for section in empty_sections:
                print(f"    - {section}")
        
        return data
    except Exception as e:
        print(f"  Error accessing GitHub Pages: {e}")
        return None

def check_workflow_logs():
    # This would require GitHub API access with the token
    # For simplicity, we'll just check the workflow file
    print("\nChecking GitHub Actions workflow file:")
    try:
        with open(".github/workflows/daily.yml", "r") as f:
            workflow = yaml.safe_load(f)
        
        print("  Workflow file found")
        
        # Check for key steps
        steps = []
        for job in workflow.get('jobs', {}).values():
            for step in job.get('steps', []):
                steps.append(step.get('name', 'unnamed step'))
        
        print("  Workflow steps:")
        for step in steps:
            print(f"    - {step}")
        
        return workflow
    except Exception as e:
        print(f"  Error checking workflow file: {e}")
        return None

def check_regwatch_script():
    print("\nChecking regwatch.py script:")
    try:
        with open("regwatch.py", "r") as f:
            content = f.read()
        
        # Check for key functions
        functions = [
            "discover_feeds",
            "harvest_all_sources",
            "parse_feed",
            "classify",
            "build_digest"
        ]
        
        for func in functions:
            if func in content:
                print(f"  Found function: {func}")
            else:
                print(f"  Missing function: {func}")
        
        # Check for potential issues
        issues = []
        
        if "requests.get" in content and "timeout" not in content:
            issues.append("No timeout set for requests.get() calls")
        
        if "User-Agent" not in content:
            issues.append("No User-Agent header set for requests")
        
        if "try:" in content and "except Exception" in content:
            print("  Error handling found")
        else:
            issues.append("Limited error handling")
        
        if issues:
            print("  Potential issues:")
            for issue in issues:
                print(f"    - {issue}")
        
        return content
    except Exception as e:
        print(f"  Error checking regwatch.py: {e}")
        return None

def main():
    # Check GitHub Pages output
    data = check_github_pages()
    
    # Check workflow file
    workflow = check_workflow_logs()
    
    # Check regwatch script
    script = check_regwatch_script()
    
    # Provide recommendations
    print("\nRecommendations:")
    
    if data and 'sections' in data and len(data['sections']) == 1 and 'space' in data['sections']:
        print("1. The issue appears to be that only space feeds are being successfully processed.")
        print("   This could be due to:")
        print("   - Only NASA/space feeds are accessible without special headers")
        print("   - Other feeds might require User-Agent headers or have rate limiting")
        print("   - Feed discovery might be failing for non-space sources")
        
        print("\n2. Try adding these improvements to regwatch.py:")
        print("   - Add User-Agent headers to all requests")
        print("   - Implement retry logic with exponential backoff")
        print("   - Add direct feed URLs instead of landing pages")
        print("   - Add more verbose logging to debug feed discovery issues")
        
        print("\n3. For immediate results, add some known working feeds directly:")
        print("   - For aviation: https://www.easa.europa.eu/newsroom-and-events/news/feed.xml")
        print("   - For pharma: https://www.fda.gov/about-fda/contact-fda/rss-feeds/drug-safety-podcasts.xml")
        print("   - For automotive: https://www.nhtsa.gov/rss.xml")
        print("   - For crossIndustry: https://www.nist.gov/news-events/news/rss.xml")
    else:
        print("1. Check if the GitHub Actions workflow is completing successfully")
        print("2. Verify that the feed discovery process is working for all sections")
        print("3. Add direct feed URLs instead of landing pages for more reliable discovery")

if __name__ == "__main__":
    main()