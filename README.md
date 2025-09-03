# Nextalent RegWatch

A regulatory watch system that collects information from official regulatory sources, filters by keywords, and outputs data in a standardized format.

## Overview

RegWatch automatically collects regulatory information from various official sources such as:
- EASA (European Union Aviation Safety Agency)
- FAA (Federal Aviation Administration)
- EMA (European Medicines Agency)
- FDA (Food and Drug Administration)
- FCC (Federal Communications Commission)

The system filters the collected information by keywords for different sectors and outputs the data in a standardized JSON format. It also generates a widget that can be embedded in any website.

## Features

- **Automated Collection**: Pulls data from official regulatory sources
- **Keyword Filtering**: Filters by keywords per sector
- **Standardized Output**: Outputs data in a consistent JSON format
- **Embeddable Widget**: Provides a widget that can be embedded in any website
- **Daily Updates**: Runs automatically on weekdays at 06:25 UK time

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

3. Run the collector:
   ```
   python src/main.py
   ```

## GitHub Actions

The repository includes a GitHub Actions workflow that runs the collector automatically on weekdays at 06:25 UK time and publishes the results to GitHub Pages.

## Customization

### Adding New Sources

To add a new source, create a new collector class in the `src/collectors` directory that extends the `BaseCollector` class.

### Customizing Keywords

To customize the keywords used for filtering, create a JSON file with the following structure:

```json
{
  "aviation": ["keyword1", "keyword2", ...],
  "space": ["keyword1", "keyword2", ...],
  "pharma": ["keyword1", "keyword2", ...],
  "automotive": ["keyword1", "keyword2", ...],
  "crossIndustry": ["keyword1", "keyword2", ...]
}
```

Then, pass the path to this file to the `KeywordFilter` constructor.

## License

This project is licensed under the MIT License - see the LICENSE file for details.