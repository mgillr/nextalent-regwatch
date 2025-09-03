#!/usr/bin/env python3
"""
Run script for RegWatch.
"""

import os
import sys
import logging
from src.main import main

if __name__ == "__main__":
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
    logger.info("Starting RegWatch manually")
    
    # Run the main function
    main()
    
    logger.info("RegWatch completed")