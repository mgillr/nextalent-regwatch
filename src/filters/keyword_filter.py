"""Keyword filter for regulatory data."""

import logging
import json
import os

logger = logging.getLogger(__name__)

class KeywordFilter:
    """Filter for regulatory data based on keywords."""
    
    def __init__(self, keywords_file=None):
        """
        Initialize the keyword filter.
        
        Args:
            keywords_file (str, optional): Path to the keywords JSON file.
                If not provided, uses the default keywords.
        """
        self.keywords = self._load_keywords(keywords_file)
    
    def _load_keywords(self, keywords_file):
        """
        Load keywords from a file or use defaults.
        
        Args:
            keywords_file (str, optional): Path to the keywords JSON file.
            
        Returns:
            dict: Dictionary of keywords by sector.
        """
        default_keywords = {
            "aviation": [
                "regulation", "safety", "aircraft", "airline", "pilot", "flight", 
                "certification", "airworthiness", "drone", "uav", "uas", "easa", "faa"
            ],
            "space": [
                "satellite", "launch", "orbit", "space", "rocket", "spacecraft", 
                "mission", "nasa", "esa", "spacex", "blue origin", "virgin galactic"
            ],
            "pharma": [
                "drug", "medicine", "clinical", "trial", "approval", "fda", "ema", 
                "pharmaceutical", "vaccine", "therapy", "treatment", "patient"
            ],
            "automotive": [
                "vehicle", "car", "autonomous", "self-driving", "electric", "ev", 
                "battery", "charging", "emission", "safety", "recall"
            ],
            "crossIndustry": [
                "regulation", "compliance", "standard", "safety", "security", 
                "certification", "approval", "guideline", "directive", "policy"
            ]
        }
        
        if keywords_file and os.path.exists(keywords_file):
            try:
                with open(keywords_file, 'r') as f:
                    custom_keywords = json.load(f)
                logger.info(f"Loaded custom keywords from {keywords_file}")
                return custom_keywords
            except Exception as e:
                logger.error(f"Error loading keywords from {keywords_file}: {e}")
                return default_keywords
        else:
            logger.info("Using default keywords")
            return default_keywords
    
    def filter(self, items):
        """
        Filter items based on keywords.
        
        Args:
            items (list): List of items to filter.
            
        Returns:
            list: Filtered list of items.
        """
        filtered_items = []
        
        for item in items:
            # Get the sector from the item
            sector = item.get('sector', 'crossIndustry')
            
            # Get keywords for this sector and cross-industry
            sector_keywords = self.keywords.get(sector, [])
            cross_industry_keywords = self.keywords.get('crossIndustry', [])
            
            # Combine keywords
            all_keywords = sector_keywords + cross_industry_keywords
            
            # Check if any keyword is in the title or description
            title = item.get('title', '').lower()
            description = item.get('description', '').lower()
            
            if any(keyword.lower() in title or keyword.lower() in description for keyword in all_keywords):
                filtered_items.append(item)
        
        logger.info(f"Filtered {len(items)} items down to {len(filtered_items)} items")
        return filtered_items