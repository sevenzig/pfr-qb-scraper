#!/usr/bin/env python3
"""
Test script to verify splits table categorization
"""

import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import PFRSeleniumManager
from src.config.config import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_splits_categorization():
    """Test splits table categorization for a known player"""
    
    # Initialize components
    selenium_manager = PFRSeleniumManager(config)
    splits_extractor = SplitsExtractor(selenium_manager)
    
    # Test with Joe Burrow (known to have both basic and advanced splits)
    pfr_id = "BurrJo00"
    player_name = "Joe Burrow"
    season = 2024
    
    print(f"Testing splits categorization for {player_name} ({pfr_id}) in {season}")
    print("=" * 60)
    
    try:
        # Extract splits
        result = splits_extractor.extract_player_splits(
            pfr_id, player_name, season, None
        )
        
        # Print results
        print(f"\nExtraction Results:")
        print(f"  Tables discovered: {result.tables_discovered}")
        print(f"  Tables processed: {result.tables_processed}")
        print(f"  Basic splits extracted: {len(result.basic_splits)}")
        print(f"  Advanced splits extracted: {len(result.advanced_splits)}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Warnings: {len(result.warnings)}")
        print(f"  Extraction time: {result.extraction_time:.2f}s")
        
        # Print errors if any
        if result.errors:
            print(f"\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
        
        # Print warnings if any
        if result.warnings:
            print(f"\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        # Print sample data
        if result.basic_splits:
            print(f"\nSample Basic Split:")
            sample_basic = result.basic_splits[0]
            print(f"  Split: {sample_basic.split}")
            print(f"  Value: {sample_basic.value}")
            print(f"  Games: {sample_basic.g}")
            print(f"  Completions: {sample_basic.cmp}")
            print(f"  Attempts: {sample_basic.att}")
        
        if result.advanced_splits:
            print(f"\nSample Advanced Split:")
            sample_advanced = result.advanced_splits[0]
            print(f"  Split: {sample_advanced.split}")
            print(f"  Value: {sample_advanced.value}")
            print(f"  Completions: {sample_advanced.cmp}")
            print(f"  Attempts: {sample_advanced.att}")
            print(f"  First Downs: {sample_advanced.first_downs}")
        
        # Success criteria
        success = (
            result.tables_discovered > 0 and
            result.tables_processed > 0 and
            len(result.basic_splits) > 0 and
            len(result.errors) == 0
        )
        
        print(f"\nTest {'PASSED' if success else 'FAILED'}")
        return success
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_splits_categorization()
    sys.exit(0 if success else 1) 