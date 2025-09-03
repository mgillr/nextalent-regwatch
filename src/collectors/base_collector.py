"""Base collector class for all regulatory sources."""

from abc import ABC, abstractmethod

class BaseCollector(ABC):
    """Abstract base class for all collectors."""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def collect(self):
        """
        Collect data from the source.
        
        Returns:
            list: List of collected items with at least the following fields:
                - title: str
                - url: str
                - date: str (ISO format)
                - source: str
                - description: str
                - sector: str (one of: aviation, space, pharma, automotive, crossIndustry)
        """
        pass