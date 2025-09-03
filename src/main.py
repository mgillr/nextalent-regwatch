#!/usr/bin/env python3
"""
RegWatch - Regulatory Watch System
Collects regulatory information from official sources and outputs in a standardized format.
"""

import os
import sys
import json
import logging
from datetime import datetime
import pytz

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.easa import EASACollector
from src.collectors.faa import FAACollector
from src.collectors.ema import EMACollector
from src.collectors.fda import FDACollector
from src.collectors.fcc import FCCCollector
from src.filters.keyword_filter import KeywordFilter
from src.output.json_output import JSONOutput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('regwatch.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the RegWatch system."""
    logger.info("Starting RegWatch collection process")
    
    # Initialize collectors
    collectors = [
        EASACollector(),
        FAACollector(),
        EMACollector(),
        FDACollector(),
        FCCCollector()
    ]
    
    # Initialize filters
    keyword_filter = KeywordFilter()
    
    # Initialize output handler
    json_output = JSONOutput()
    
    # Collect data from all sources
    all_data = []
    for collector in collectors:
        try:
            logger.info(f"Collecting data from {collector.name}")
            data = collector.collect()
            all_data.extend(data)
        except Exception as e:
            logger.error(f"Error collecting data from {collector.name}: {e}")
    
    # Filter data
    filtered_data = keyword_filter.filter(all_data)
    
    # Generate output
    uk_timezone = pytz.timezone('Europe/London')
    current_time = datetime.now(uk_timezone)
    
    output_data = {
        "lastUpdated": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sections": {
            "aviation": [],
            "space": [],
            "pharma": [],
            "automotive": [],
            "crossIndustry": []
        }
    }
    
    # Categorize filtered data into sections
    for item in filtered_data:
        if item.get('sector') in output_data['sections']:
            output_data['sections'][item['sector']].append(item)
        else:
            # Default to crossIndustry if sector not specified
            output_data['sections']['crossIndustry'].append(item)
    
    # Save output
    json_output.save(output_data)
    
    # Generate widget files
    json_output.generate_widget(output_data)
    
    logger.info("RegWatch collection process completed")

if __name__ == "__main__":
    main()