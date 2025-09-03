"""FAA (Federal Aviation Administration) collector."""

import requests
from datetime import datetime
import logging
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector

logger = logging.getLogger(__name__)

class FAACollector(BaseCollector):
    """Collector for FAA regulations and notices."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.faa.gov"
        self.regulations_url = f"{self.base_url}/regulations_policies/rulemaking/recently_published"
    
    def collect(self):
        """
        Collect regulatory information from FAA.
        
        Returns:
            list: List of collected items.
        """
        logger.info("Collecting data from FAA")
        
        try:
            response = requests.get(self.regulations_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            items = []
            
            # Find the latest publications
            table = soup.select_one('.table')
            if not table:
                logger.warning("No table found on FAA regulations page")
                return items
                
            rows = table.select('tbody tr')
            
            for row in rows:
                try:
                    cells = row.select('td')
                    if len(cells) < 3:
                        continue
                    
                    date_cell = cells[0]
                    title_cell = cells[1]
                    
                    date_str = date_cell.text.strip()
                    
                    # Parse date
                    try:
                        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                        iso_date = date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                    except (ValueError, AttributeError):
                        iso_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                    
                    title_link = title_cell.select_one('a')
                    if not title_link:
                        continue
                        
                    title = title_link.text.strip()
                    url = title_link.get('href')
                    if url and not url.startswith('http'):
                        url = f"{self.base_url}{url}"
                    
                    description = cells[2].text.strip() if len(cells) > 2 else ""
                    
                    items.append({
                        'title': title,
                        'url': url,
                        'date': iso_date,
                        'source': 'FAA',
                        'description': description,
                        'sector': 'aviation'
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing FAA publication: {e}")
            
            logger.info(f"Collected {len(items)} items from FAA")
            return items
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data from FAA: {e}")
            return []