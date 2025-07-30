#!/usr/bin/env python3
"""
Test script for the fixed splits extractor
Verifies that all missing data is now being extracted correctly
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
    from config.config import config
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


def test_joe_burrow_splits():
    """Test splits extraction for Joe Burrow"""
    logger.info("Testing splits extraction for Joe Burrow")
    
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
    
    # Test parameters
    pfr_id = "burrjo01"
    player_name = "Joe Burrow"
    season = 2024
    scraped_at = datetime.now()
    
    try:
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
        logger.info(f"  - Extraction time: {result.extraction_time:.2f}s")
        
        # Log errors if any
        if result.errors:
            logger.error("Extraction errors:")
            for error in result.errors:
                logger.error(f"  - {error}")
        
        # Log warnings if any
        if result.warnings:
            logger.warning("Extraction warnings:")
            for warning in result.warnings:
                logger.warning(f"  - {warning}")
        
        # Analyze basic splits
        if result.basic_splits:
            logger.info("Basic splits analysis:")
            logger.info(f"  - Total rows: {len(result.basic_splits)}")
            
            # Count non-null values for each field
            field_counts = {}
            for split in result.basic_splits:
                for field_name, field_value in split.__dict__.items():
                    if field_name not in ['pfr_id', 'player_name', 'season', 'scraped_at', 'updated_at']:
                        if field_value is not None and field_value != '':
                            field_counts[field_name] = field_counts.get(field_name, 0) + 1
            
            logger.info("  - Field completion rates:")
            for field_name, count in sorted(field_counts.items()):
                percentage = (count / len(result.basic_splits)) * 100
                logger.info(f"    {field_name}: {count}/{len(result.basic_splits)} ({percentage:.1f}%)")
            
            # Show sample data
            logger.info("  - Sample basic splits:")
            for i, split in enumerate(result.basic_splits[:5]):
                logger.info(f"    {i+1}. {split.split} = {split.value}")
                logger.info(f"       G:{split.g} W:{split.w} L:{split.l} T:{split.t}")
                logger.info(f"       Cmp:{split.cmp} Att:{split.att} Yds:{split.yds} TD:{split.td}")
        
        # Analyze advanced splits
        if result.advanced_splits:
            logger.info("Advanced splits analysis:")
            logger.info(f"  - Total rows: {len(result.advanced_splits)}")
            
            # Count non-null values for each field
            field_counts = {}
            for split in result.advanced_splits:
                for field_name, field_value in split.__dict__.items():
                    if field_name not in ['pfr_id', 'player_name', 'season', 'scraped_at', 'updated_at']:
                        if field_value is not None and field_value != '':
                            field_counts[field_name] = field_counts.get(field_name, 0) + 1
            
            logger.info("  - Field completion rates:")
            for field_name, count in sorted(field_counts.items()):
                percentage = (count / len(result.advanced_splits)) * 100
                logger.info(f"    {field_name}: {count}/{len(result.advanced_splits)} ({percentage:.1f}%)")
            
            # Show sample data
            logger.info("  - Sample advanced splits:")
            for i, split in enumerate(result.advanced_splits[:5]):
                logger.info(f"    {i+1}. {split.split} = {split.value}")
                logger.info(f"       Cmp:{split.cmp} Att:{split.att} Yds:{split.yds} TD:{split.td}")
                logger.info(f"       1D:{split.first_downs} Int:{split.int} Rate:{split.rate}")
        
        # Validate results
        validation_errors = splits_extractor.validate_extraction_result(result)
        if validation_errors:
            logger.error("Validation errors:")
            for error in validation_errors:
                logger.error(f"  - {error}")
        else:
            logger.info("Validation passed - no errors found")
        
        # Check if we have the expected data
        expected_basic_splits = [
            "Home", "Away", "Win", "Loss", "Tie", 
            "1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "Overtime"
        ]
        
        expected_advanced_splits = [
            "1st Down", "2nd Down", "3rd Down", "4th Down",
            "1-3 Yards", "4-6 Yards", "7-9 Yards", "10+ Yards"
        ]
        
        basic_split_values = [split.value for split in result.basic_splits]
        advanced_split_values = [split.value for split in result.advanced_splits]
        
        logger.info("Expected vs Actual basic splits:")
        for expected in expected_basic_splits:
            found = expected in basic_split_values
            logger.info(f"  {expected}: {'✓' if found else '✗'}")
        
        logger.info("Expected vs Actual advanced splits:")
        for expected in expected_advanced_splits:
            found = expected in advanced_split_values
            logger.info(f"  {expected}: {'✓' if found else '✗'}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing splits extraction: {e}", exc_info=True)
        return None
    
    finally:
        # Clean up
        selenium_manager.end_session()


def test_multiple_players():
    """Test splits extraction for multiple players"""
    logger.info("Testing splits extraction for multiple players")
    
    # Test players
    test_players = [
        ("burrjo01", "Joe Burrow"),
        ("allenjo02", "Josh Allen"),
        ("mahompa00", "Patrick Mahomes")
    ]
    
    # Initialize Selenium manager
    selenium_config = SeleniumConfig(
        headless=True,
        timeout=30,
        min_delay=7,
        max_delay=10
    )
    
    selenium_manager = SeleniumManager(selenium_config)
    splits_extractor = SplitsExtractor(selenium_manager)
    
    total_basic_splits = 0
    total_advanced_splits = 0
    total_errors = 0
    
    try:
        for pfr_id, player_name in test_players:
            logger.info(f"Testing {player_name}...")
            
            result = splits_extractor.extract_player_splits(
                pfr_id, player_name, 2024, datetime.now()
            )
            
            total_basic_splits += len(result.basic_splits)
            total_advanced_splits += len(result.advanced_splits)
            total_errors += len(result.errors)
            
            logger.info(f"  {player_name}: {len(result.basic_splits)} basic, {len(result.advanced_splits)} advanced splits")
            
            if result.errors:
                logger.warning(f"  Errors for {player_name}: {result.errors}")
        
        logger.info(f"Multi-player test completed:")
        logger.info(f"  - Total basic splits: {total_basic_splits}")
        logger.info(f"  - Total advanced splits: {total_advanced_splits}")
        logger.info(f"  - Total errors: {total_errors}")
        
    except Exception as e:
        logger.error(f"Error in multi-player test: {e}", exc_info=True)
    
    finally:
        selenium_manager.end_session()


if __name__ == "__main__":
    logger.info("Starting splits extractor tests")
    
    # Test Joe Burrow
    result = test_joe_burrow_splits()
    
    # Test multiple players
    test_multiple_players()
    
    logger.info("Splits extractor tests completed") 