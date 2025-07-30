#!/usr/bin/env python3
"""Simple debug script for splits extraction"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

# Import modules
from core.selenium_manager import SeleniumManager, SeleniumConfig
from scrapers.splits_extractor import SplitsExtractor

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('scrapers.splits_extractor').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

def test_splits():
    """Test splits extraction with debug logging"""
    
    selenium_config = SeleniumConfig(
        headless=True,  # Back to headless to avoid crashes
        page_load_timeout=20,
        implicit_wait=8
    )
    
    selenium_manager = SeleniumManager(selenium_config)
    splits_extractor = SplitsExtractor(selenium_manager)
    
    try:
        logger.info("Starting splits extraction test for Joe Burrow...")
        
        result = splits_extractor.extract_player_splits(
            pfr_id="burrjo01",
            player_name="Joe Burrow", 
            season=2024,
            scraped_at=datetime.now()
        )
        
        print(f"\n=== RESULTS ===")
        print(f"Basic splits: {len(result.basic_splits)}")
        print(f"Advanced splits: {len(result.advanced_splits)}")
        print(f"Tables discovered: {result.tables_discovered}")
        print(f"Tables processed: {result.tables_processed}")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        
        if result.basic_splits:
            print(f"\nFirst 3 basic splits:")
            for i, split in enumerate(result.basic_splits[:3]):
                print(f"  {i+1}. {split.split} = {split.value}")
        
        if result.advanced_splits:
            print(f"\nFirst 3 advanced splits:")
            for i, split in enumerate(result.advanced_splits[:3]):
                print(f"  {i+1}. {split.split} = {split.value}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return None
    
    finally:
        selenium_manager.end_session()

if __name__ == "__main__":
    result = test_splits()