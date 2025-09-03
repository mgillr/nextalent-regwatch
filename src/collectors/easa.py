"""EASA (European Union Aviation Safety Agency) collector."""

import requests
from datetime import datetime
import logging
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector

logger = logging.getLogger(__name__)

class EASACollector(BaseCollector):
    """Collector for EASA regulations and notices."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.easa.europa.eu"
        self.regulations_url = f"{self.base_url}/en/document-library"
    
    def collect(self):
        """
        Collect regulatory information from EASA.
        
        Returns:
            list: List of collected items.
        """
        logger.info("Collecting data from EASA")
        
        try:
            response = requests.get(self.regulations_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            items = []
            
            # Find the latest publications
            publications = soup.select('.views-row')
            
            for pub in publications[:20]:  # Limit to 20 most recent
                try:
                    title_elem = pub.select_one('.field-content a')
                    if not title_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    url = title_elem.get('href')
                    if url and not url.startswith('http'):
                        url = f"{self.base_url}{url}"
                    
                    date_elem = pub.select_one('.date-display-single')
                    date_str = date_elem.text.strip() if date_elem else ""
                    
                    # Parse date
                    try:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                        iso_date = date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except (ValueError, AttributeError):
                        iso_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                    
                    description_elem = pub.select_one('.field-content p')
                    description = description_elem.text.strip() if description_elem else ""
                    
                    items.append({
                        'title': title,
                        'url': url,
                        'date': iso_date,
                        'source': 'EASA',
                        'description': description,
                        'sector': 'aviation'
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing EASA publication: {e}")
            
            logger.info(f"Collected {len(items)} items from EASA")
            return items
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data from EASA: {e}")
            return []