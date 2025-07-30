#!/usr/bin/env python3
"""
Test the fixed splits extractor with enhanced table discovery and field mapping
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.selenium_manager import SeleniumManager, SeleniumConfig
from scrapers.splits_extractor import SplitsExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Reduce selenium logging noise
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

def test_fixed_splits_extractor():
    """Test the fixed splits extractor"""
    
    logger.info("=== TESTING FIXED SPLITS EXTRACTOR ===")
    
    # Create enhanced Selenium config
    selenium_config = SeleniumConfig(
        headless=True,
        page_load_timeout=60,
        implicit_wait=15
    )
    
    selenium_manager = SeleniumManager(selenium_config)
    splits_extractor = SplitsExtractor(selenium_manager)
    
    try:
        # Test with Jalen Hurts 2024
        pfr_id = 'HurtJa00'
        player_name = 'Jalen Hurts'
        season = 2024
        
        logger.info(f"Testing extraction for {player_name} ({pfr_id}) - {season}")
        
        # Extract splits
        result = splits_extractor.extract_player_splits(
            pfr_id=pfr_id,
            player_name=player_name,
            season=season,
            scraped_at=datetime.now()
        )
        
        # Log results
        logger.info("=== EXTRACTION RESULTS ===")
        logger.info(f"Tables discovered: {result.tables_discovered}")
        logger.info(f"Tables processed: {result.tables_processed}")
        logger.info(f"Basic splits extracted: {len(result.basic_splits)}")
        logger.info(f"Advanced splits extracted: {len(result.advanced_splits)}")
        logger.info(f"Errors: {len(result.errors)}")
        logger.info(f"Warnings: {len(result.warnings)}")
        logger.info(f"Extraction time: {result.extraction_time:.2f}s")
        
        # Show errors if any
        if result.errors:
            logger.error("ERRORS:")
            for error in result.errors:
                logger.error(f"  - {error}")
        
        # Show warnings if any
        if result.warnings:
            logger.warning("WARNINGS:")
            for warning in result.warnings:
                logger.warning(f"  - {warning}")
        
        # Sample data
        if result.basic_splits:
            logger.info("=== SAMPLE BASIC SPLITS DATA ===")
            for i, split in enumerate(result.basic_splits[:3]):
                logger.info(f"Basic Split {i+1}: {split.split} = {split.value}")
                logger.info(f"  Games: {split.g}, Wins: {split.w}, Losses: {split.l}")
                logger.info(f"  Passing: {split.cmp}/{split.att} ({split.cmp_pct}%), {split.yds} yds, {split.td} TD")
        
        if result.advanced_splits:
            logger.info("=== SAMPLE ADVANCED SPLITS DATA ===")
            for i, split in enumerate(result.advanced_splits[:3]):
                logger.info(f"Advanced Split {i+1}: {split.split} = {split.value}")
                logger.info(f"  Passing: {split.cmp}/{split.att} ({split.cmp_pct}%), {split.yds} yds, {split.td} TD")
                logger.info(f"  First downs: {split.first_downs}")
        
        # Overall success evaluation
        success = (
            result.tables_discovered >= 2 and 
            result.tables_processed >= 2 and
            (len(result.basic_splits) > 0 or len(result.advanced_splits) > 0) and
            len(result.errors) == 0
        )
        
        if success:
            logger.info("✅ EXTRACTION SUCCESSFUL!")
            return True
        else:
            logger.error("❌ EXTRACTION FAILED")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        return False
        
    finally:
        try:
            selenium_manager.close()
        except:
            pass

if __name__ == "__main__":
    success = test_fixed_splits_extractor()
    sys.exit(0 if success else 1)