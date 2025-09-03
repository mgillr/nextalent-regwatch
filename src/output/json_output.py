"""JSON output handler for RegWatch."""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class JSONOutput:
    """Output handler for JSON data."""
    
    def __init__(self, output_dir=None):
        """
        Initialize the JSON output handler.
        
        Args:
            output_dir (str, optional): Directory to save output files.
                If not provided, uses the current directory.
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'data')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save(self, data):
        """
        Save data to JSON files.
        
        Args:
            data (dict): Data to save.
        """
        # Save to latest.json
        latest_path = os.path.join(self.output_dir, 'latest.json')
        self._save_json(data, latest_path)
        
        # Save to date-stamped file
        today = datetime.now().strftime('%Y-%m-%d')
        dated_path = os.path.join(self.output_dir, f'regwatch-{today}.json')
        self._save_json(data, dated_path)
        
        logger.info(f"Saved data to {latest_path} and {dated_path}")
    
    def _save_json(self, data, path):
        """
        Save data to a JSON file.
        
        Args:
            data (dict): Data to save.
            path (str): Path to save the file.
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving JSON to {path}: {e}")
    
    def generate_widget(self, data):
        """
        Generate widget files (widget.js and index.html).
        
        Args:
            data (dict): Data to include in the widget.
        """
        try:
            # Create widget.js
            widget_js_path = os.path.join(self.output_dir, 'widget.js')
            with open(widget_js_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_widget_js(data))
            
            # Create index.html
            widget_html_path = os.path.join(self.output_dir, 'index.html')
            with open(widget_html_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_widget_html())
            
            logger.info(f"Generated widget files at {widget_js_path} and {widget_html_path}")
        except Exception as e:
            logger.error(f"Error generating widget files: {e}")
    
    def _generate_widget_js(self, data):
        """
        Generate the widget.js file content.
        
        Args:
            data (dict): Data to include in the widget.
            
        Returns:
            str: Content of the widget.js file.
        """
        # Convert data to JSON string
        data_json = json.dumps(data, ensure_ascii=False)
        
        return f"""// RegWatch Widget
(function() {{
  // Widget data
  const regwatchData = {data_json};
  
  // Create widget
  function createRegwatchWidget() {{
    const container = document.getElementById('regwatch-container');
    if (!container) return;
    
    // Create header
    const header = document.createElement('div');
    header.className = 'regwatch-header';
    header.innerHTML = '<h2>Regulatory Watch</h2>';
    container.appendChild(header);
    
    // Create last updated info
    const lastUpdated = document.createElement('div');
    lastUpdated.className = 'regwatch-updated';
    const date = new Date(regwatchData.lastUpdated);
    lastUpdated.innerHTML = `<p>Last updated: ${{date.toLocaleDateString()}} ${{date.toLocaleTimeString()}}</p>`;
    container.appendChild(lastUpdated);
    
    // Create sections
    const sections = document.createElement('div');
    sections.className = 'regwatch-sections';
    
    // Add each section
    for (const [sectionName, items] of Object.entries(regwatchData.sections)) {{
      if (items.length === 0) continue;
      
      const section = document.createElement('div');
      section.className = 'regwatch-section';
      
      // Section header
      const sectionHeader = document.createElement('h3');
      sectionHeader.textContent = sectionName.charAt(0).toUpperCase() + sectionName.slice(1);
      section.appendChild(sectionHeader);
      
      // Section items
      const itemsList = document.createElement('ul');
      items.slice(0, 5).forEach(item => {{
        const listItem = document.createElement('li');
        listItem.innerHTML = `<a href="${{item.url}}" target="_blank">${{item.title}}</a>
                             <span class="regwatch-source">${{item.source}}</span>`;
        itemsList.appendChild(listItem);
      }});
      
      section.appendChild(itemsList);
      sections.appendChild(section);
    }}
    
    container.appendChild(sections);
    
    // Add CSS
    const style = document.createElement('style');
    style.textContent = `
      #regwatch-container {{
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 5px;
      }}
      .regwatch-header h2 {{
        margin-top: 0;
        color: #333;
      }}
      .regwatch-updated {{
        font-size: 0.8em;
        color: #666;
        margin-bottom: 15px;
      }}
      .regwatch-section {{
        margin-bottom: 20px;
      }}
      .regwatch-section h3 {{
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
        color: #444;
      }}
      .regwatch-section ul {{
        padding-left: 20px;
      }}
      .regwatch-section li {{
        margin-bottom: 8px;
      }}
      .regwatch-source {{
        font-size: 0.8em;
        color: #666;
        margin-left: 10px;
      }}
    `;
    document.head.appendChild(style);
  }}
  
  // Initialize when DOM is loaded
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', createRegwatchWidget);
  }} else {{
    createRegwatchWidget();
  }}
}})();
"""
    
    def _generate_widget_html(self):
        """
        Generate the index.html file content.
        
        Returns:
            str: Content of the index.html file.
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RegWatch Widget Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        header {
            background-color: #f4f4f4;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        h1 {
            margin: 0;
        }
        footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>RegWatch Widget Demo</h1>
            <p>This page demonstrates the RegWatch widget that can be embedded in any website.</p>
        </header>
        
        <main>
            <!-- RegWatch Widget Container -->
            <div id="regwatch-container"></div>
        </main>
        
        <footer>
            <p>&copy; 2025 Nextalent RegWatch. All rights reserved.</p>
        </footer>
    </div>
    
    <!-- Include the RegWatch Widget Script -->
    <script src="widget.js"></script>
</body>
</html>
"""