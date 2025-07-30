#!/usr/bin/env python3
"""
Direct test of the splits extractor functionality
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.selenium_manager import SeleniumManager, SeleniumConfig
    from scrapers.splits_extractor import SplitsExtractor
    from models.qb_models import QBSplitsType1, QBSplitsType2
except ImportError as e:
    print(f"Import error: {e}")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_splits_extraction_direct():
    """Test the splits extraction functionality directly"""
    logger.info("Testing splits extraction directly")
    
    try:
        # Initialize Selenium manager
        selenium_config = SeleniumConfig(
            headless=True,
            timeout=30,
            min_delay=7,
            max_delay=10
        )
        
        selenium_manager = SeleniumManager(selenium_config)
        
        # Initialize splits extractor
        splits_extractor = SplitsExtractor(selenium_manager)
        
        # Test Joe Burrow
        pfr_id = "burrjo01"
        player_name = "Joe Burrow"
        season = 2024
        scraped_at = datetime.now()
        
        logger.info(f"Extracting splits for {player_name}...")
        
        # Extract splits
        result = splits_extractor.extract_player_splits(
            pfr_id, player_name, season, scraped_at
        )
        
        # Log results
        logger.info(f"Extraction completed:")
        logger.info(f"  - Basic splits: {len(result.basic_splits)}")
        logger.info(f"  - Advanced splits: {len(result.advanced_splits)}")
        logger.info(f"  - Tables discovered: {result.tables_discovered}")
        logger.info(f"  - Tables processed: {result.tables_processed}")
        logger.info(f"  - Errors: {len(result.errors)}")
        logger.info(f"  - Warnings: {len(result.warnings)}")
        
        # Show sample data
        if result.basic_splits:
            logger.info("Sample basic splits:")
            for i, split in enumerate(result.basic_splits[:3]):
                logger.info(f"  {i+1}. {split.split} = {split.value}")
                logger.info(f"     G:{split.g} W:{split.w} L:{split.l} T:{split.t}")
                logger.info(f"     Cmp:{split.cmp} Att:{split.att} Yds:{split.yds} TD:{split.td}")
        
        if result.advanced_splits:
            logger.info("Sample advanced splits:")
            for i, split in enumerate(result.advanced_splits[:3]):
                logger.info(f"  {i+1}. {split.split} = {split.value}")
                logger.info(f"     Cmp:{split.cmp} Att:{split.att} Yds:{split.yds} TD:{split.td}")
                logger.info(f"     1D:{split.first_downs} Int:{split.int} Rate:{split.rate}")
        
        # Check for expected data
        basic_split_values = [split.value for split in result.basic_splits]
        advanced_split_values = [split.value for split in result.advanced_splits]
        
        logger.info("Expected basic splits found:")
        expected_basic = ["Home", "Away", "Win", "Loss"]
        for expected in expected_basic:
            found = expected in basic_split_values
            logger.info(f"  {expected}: {'✓' if found else '✗'}")
        
        logger.info("Expected advanced splits found:")
        expected_advanced = ["1st Down", "2nd Down", "3rd Down", "4th Down"]
        for expected in expected_advanced:
            found = expected in advanced_split_values
            logger.info(f"  {expected}: {'✓' if found else '✗'}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing splits extraction: {e}", exc_info=True)
        return None
    
    finally:
        # Clean up
        if 'selenium_manager' in locals():
            selenium_manager.end_session()


if __name__ == "__main__":
    logger.info("Starting direct splits extractor test")
    result = test_splits_extraction_direct()
    
    if result:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed")
        sys.exit(1) 