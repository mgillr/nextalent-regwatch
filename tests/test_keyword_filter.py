"""Tests for the keyword filter."""

import unittest
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.filters.keyword_filter import KeywordFilter

class TestKeywordFilter(unittest.TestCase):
    """Tests for the KeywordFilter class."""
    
    def setUp(self):
        """Set up the test case."""
        self.filter = KeywordFilter()
    
    def test_filter_with_matching_keywords(self):
        """Test filtering items with matching keywords."""
        items = [
            {
                'title': 'New Aviation Safety Regulation',
                'description': 'A new regulation for aircraft safety',
                'sector': 'aviation'
            },
            {
                'title': 'Pharmaceutical Guidelines Update',
                'description': 'Updated guidelines for drug trials',
                'sector': 'pharma'
            },
            {
                'title': 'Unrelated News',
                'description': 'Something completely unrelated',
                'sector': 'crossIndustry'
            }
        ]
        
        filtered = self.filter.filter(items)
        
        # The first two items should match, the third should not
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]['title'], 'New Aviation Safety Regulation')
        self.assertEqual(filtered[1]['title'], 'Pharmaceutical Guidelines Update')
    
    def test_filter_with_no_matching_keywords(self):
        """Test filtering items with no matching keywords."""
        items = [
            {
                'title': 'Unrelated News',
                'description': 'Something completely unrelated',
                'sector': 'crossIndustry'
            }
        ]
        
        filtered = self.filter.filter(items)
        
        # No items should match
        self.assertEqual(len(filtered), 0)

if __name__ == '__main__':
    unittest.main()