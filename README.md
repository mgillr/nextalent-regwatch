# Nextalent RegWatch

A regulatory watch system that collects information from official regulatory sources, filters by keywords, and outputs data in a standardized format.

## Overview

RegWatch automatically collects regulatory information from various official sources such as:
- EASA (European Union Aviation Safety Agency)
- FAA (Federal Aviation Administration)
- EMA (European Medicines Agency)
- FDA (Food and Drug Administration)
- FCC (Federal Communications Commission)
- NASA (National Aeronautics and Space Administration)
- NHTSA (National Highway Traffic Safety Administration)
- NIST (National Institute of Standards and Technology)
- And many more...

The system filters the collected information by keywords for different sectors and outputs the data in a standardized JSON format. It also generates a widget that can be embedded in any website.

## Live Demo

You can view the live demo at: [https://mgillr.github.io/nextalent-regwatch/](https://mgillr.github.io/nextalent-regwatch/)

## Features

- **Automated Collection**: Pulls data from official regulatory sources via RSS feeds and web scraping
- **Feed Auto-Discovery**: Automatically discovers RSS/Atom feeds from landing pages
- **Smart Classification**: Uses source-based hints and keyword matching to accurately classify items
- **Keyword Filtering**: Filters by keywords per sector with word boundary matching for short keywords
- **Standardized Output**: Outputs data in a consistent JSON format
- **Embeddable Widget**: Provides a widget that can be embedded in any website
- **Daily Updates**: Runs automatically on weekdays at 06:25 UK time
- **Configurable**: Easy to configure via YAML file

## Output Format

The output is in the following JSON format:

```json
{
  "lastUpdated": "2025-09-02T06:25:00Z",
  "sections": {
    "aviation": [],
    "space": [],
    "pharma": [],
    "automotive": [],
    "crossIndustry": []
  }
}
```

## Widget

The system generates a widget (widget.js and index.html) that can be embedded in any website. To use the widget, add the following HTML to your website:

```html
<div id="regwatch-container"></div>
<script src="https://[your-github-username].github.io/nextalent-regwatch/widget.js"></script>
```

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/[your-github-username]/nextalent-regwatch.git
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the sources and keywords in `regwatch.yml`:
   ```yaml
   # Lookback window in hours and max fallback items if nothing new
   window_hours: 36
   max_items: 50

   # Official sources (RSS or landing pages; the script auto-discovers feed links)
   sources:
     aviation:
       - https://www.easa.europa.eu/en/rss
       - https://www.faa.gov/newsroom
     # ... more sources ...

   # Keyword cues per section
   keywords:
     aviation: ["EASA", "FAA", "SMS", "airworthiness", ...]
     # ... more keywords ...
   ```

4. Run the collector:
   ```
   python regwatch.py
   ```
   
   This will:
   - Read sources from regwatch.yml
   - Auto-discover RSS/Atom feeds on landing pages
   - Parse items, filter by recency, and classify by keywords
   - Output to the ./out directory:
     - regwatch.json (Lovable schema)
     - regwatch-YYYY-MM-DD.json (dated snapshot for fallback)
     - widget.js (data + renderer; optional embed)
     - index.html (standalone fallback page)

## GitHub Actions

The repository includes a GitHub Actions workflow that runs the collector automatically on weekdays at 06:25 UK time and publishes the results to GitHub Pages.

## Testing

You can test a specific RSS feed using the included test script:

```
python test_feed.py https://example.com/feed.xml
```

You can also run a quick test of the regwatch.py script with a minimal configuration:

```
python test_regwatch.py
```

This will create a test configuration, fetch a few feeds, and output the results to the test_out directory.

## Customization

### Adding New Sources

To add new sources, simply update the `sources` section in the `regwatch.yml` file. You can add either direct RSS feed URLs or landing pages that contain links to RSS feeds.

### Customizing Keywords

To customize the keywords used for filtering, update the `keywords` section in the `regwatch.yml` file.

### Adjusting the Lookback Window

You can adjust how far back the system looks for new items by changing the `window_hours` value in the `regwatch.yml` file. The default is 36 hours, but you can increase it to capture more items.

### Classification System

The system uses a smart classification approach:

1. **Source-Based Hints**: Items are first classified based on their source (e.g., NASA → space, EASA → aviation)
2. **Feed URL Checking**: The system also checks the feed URL for classification hints
3. **Keyword Matching**: If source-based classification doesn't yield results, items are classified based on keyword matches
4. **Word Boundary Matching**: For short keywords (≤ 3 characters), the system uses word boundary matching to prevent false matches

## License

This project is licensed under the MIT License - see the LICENSE file for details.