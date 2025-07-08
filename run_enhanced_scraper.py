#!/usr/bin/env python3
"""
Wrapper script to run the enhanced QB scraper from the project root.
This ensures proper import paths for the src modules.
"""

import sys
import os

# Add the current directory to Python path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now we can import from src
from src.config.config import config
from src.database.db_manager import DatabaseManager
from src.models.qb_models import QBBasicStats, QBAdvancedStats, QBSplitStats
from src.scrapers.enhanced_scraper import EnhancedPFRScraper

# Import the main scraper logic
from scripts.enhanced_qb_scraper import EnhancedQBScraper, main

if __name__ == "__main__":
    main() 