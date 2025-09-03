# Nextalent RegWatch

A regulatory watch system that collects information from official regulatory sources, filters by keywords, and outputs data in a standardized format.

## Overview

RegWatch automatically collects regulatory information from various official sources such as:
- EASA (European Union Aviation Safety Agency)
- FAA (Federal Aviation Administration)
- EMA (European Medicines Agency)
- FDA (Food and Drug Administration)
- FCC (Federal Communications Commission)
- And many more...

The system filters the collected information by keywords for different sectors and outputs the data in a standardized JSON format. It also generates a widget that can be embedded in any website.

## Features

- **Automated Collection**: Pulls data from official regulatory sources via RSS feeds and web scraping
- **Feed Auto-Discovery**: Automatically discovers RSS/Atom feeds from landing pages
- **Keyword Filtering**: Filters by keywords per sector
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
   python src/main.py
   ```

## GitHub Actions

The repository includes a GitHub Actions workflow that runs the collector automatically on weekdays at 06:25 UK time and publishes the results to GitHub Pages.

## Testing

You can test a specific RSS feed using the included test script:

```
python test_feed.py https://example.com/feed.xml
```

## Customization

### Adding New Sources

To add new sources, simply update the `sources` section in the `regwatch.yml` file. You can add either direct RSS feed URLs or landing pages that contain links to RSS feeds.

### Customizing Keywords

To customize the keywords used for filtering, update the `keywords` section in the `regwatch.yml` file.

### Adjusting the Lookback Window

You can adjust how far back the system looks for new items by changing the `window_hours` value in the `regwatch.yml` file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.