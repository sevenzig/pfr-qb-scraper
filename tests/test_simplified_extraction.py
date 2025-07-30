#!/usr/bin/env python3
"""Test the simplified parsing approach for splits extraction"""

import sys
sys.path.insert(0, 'src')

from scrapers.splits_extractor import SplitsExtractor
from core.selenium_manager import SeleniumManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simplified_extraction():
    """Test if simplified approach can extract target 51 basic + 54 advanced splits"""
    
    print("=== TESTING SIMPLIFIED SPLITS EXTRACTION ===")
    
    try:
        # Initialize selenium manager and extractor
        selenium_manager = SeleniumManager()
        extractor = SplitsExtractor(selenium_manager)
        
        # Test URL for Joe Burrow 2024 splits
        test_url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
        
        print(f"Testing URL: {test_url}")
        print("Expected results:")
        print("- Basic splits: 51 rows (matching burrow_2024_splits.csv)")
        print("- Advanced splits: 54 rows (matching burrow_2024_advanced_splits.csv)")
        print("- Total: 105 splits\n")
        
        # Extract splits using simplified approach
        print("Starting extraction...")
        from datetime import datetime
        result = extractor.extract_player_splits("burrjo01", "Joe Burrow", 2024, datetime.now())
        
        # Combine both types of splits
        all_splits = result.basic_splits + result.advanced_splits
        
        # Count basic vs advanced splits from result
        basic_splits = result.basic_splits
        advanced_splits = result.advanced_splits
        
        print(f"\n=== EXTRACTION RESULTS ===")
        print(f"Basic splits extracted: {len(basic_splits)}")
        print(f"Advanced splits extracted: {len(advanced_splits)}")
        print(f"Total splits extracted: {len(all_splits)}")
        
        # Check against targets
        basic_target = 51
        advanced_target = 54
        total_target = 105
        
        basic_success = len(basic_splits) == basic_target
        advanced_success = len(advanced_splits) == advanced_target
        total_success = len(all_splits) == total_target
        
        print(f"\n=== SUCCESS ANALYSIS ===")
        print(f"Basic splits: {'PASS' if basic_success else 'FAIL'} ({len(basic_splits)}/{basic_target})")
        print(f"Advanced splits: {'PASS' if advanced_success else 'FAIL'} ({len(advanced_splits)}/{advanced_target})")
        print(f"Total extraction: {'PASS' if total_success else 'FAIL'} ({len(all_splits)}/{total_target})")
        
        # Show sample data from each type
        if basic_splits:
            print(f"\n=== SAMPLE BASIC SPLIT ===")
            sample = basic_splits[0]
            print(f"Split: {sample.split}, Value: {sample.value}")
            print(f"Games: {sample.g}, Completions: {sample.cmp}")
        
        if advanced_splits:
            print(f"\n=== SAMPLE ADVANCED SPLIT ===")
            sample = advanced_splits[0]
            print(f"Split: {sample.split}, Value: {sample.value}")
            print(f"Completions: {sample.cmp}, Attempts: {sample.att}")
        
        # Show extraction errors and warnings
        if result.errors:
            print(f"\n=== EXTRACTION ERRORS ===")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"ERROR: {error}")
        
        if result.warnings:
            print(f"\n=== EXTRACTION WARNINGS ===")
            for warning in result.warnings[:5]:  # Show first 5 warnings
                print(f"WARNING: {warning}")
        
        return total_success
        
    except Exception as e:
        logger.error(f"Extraction test failed: {e}")
        return False
    
    finally:
        if 'selenium_manager' in locals():
            selenium_manager.end_session()

def validate_against_csv():
    """Compare extraction results with reference CSV files"""
    
    print("\n=== CSV VALIDATION ===")
    
    # Read reference CSV files
    import csv
    
    basic_csv_path = "C:\\Users\\scootypuffjr\\Projects\\pfr-qb-scraper\\setup\\burrow_2024_splits.csv"
    advanced_csv_path = "C:\\Users\\scootypuffjr\\Projects\\pfr-qb-scraper\\setup\\burrow_2024_advanced_splits.csv"
    
    try:
        # Count rows in basic splits CSV
        with open(basic_csv_path, 'r', encoding='utf-8') as f:
            basic_reader = csv.reader(f)
            basic_rows = list(basic_reader)
            basic_data_rows = len(basic_rows) - 1  # Exclude header
        
        # Count rows in advanced splits CSV  
        with open(advanced_csv_path, 'r', encoding='utf-8') as f:
            advanced_reader = csv.reader(f)
            advanced_rows = list(advanced_reader)
            advanced_data_rows = len(advanced_rows) - 1  # Exclude header
        
        print(f"Reference CSV basic splits: {basic_data_rows} rows")
        print(f"Reference CSV advanced splits: {advanced_data_rows} rows")
        print(f"Reference CSV total: {basic_data_rows + advanced_data_rows} rows")
        
        return basic_data_rows, advanced_data_rows
        
    except Exception as e:
        logger.error(f"CSV validation failed: {e}")
        return None, None

if __name__ == "__main__":
    # Validate against CSV first
    basic_target, advanced_target = validate_against_csv()
    
    if basic_target and advanced_target:
        print(f"\nTarget: {basic_target} basic + {advanced_target} advanced = {basic_target + advanced_target} total splits")
    
    # Test simplified extraction
    print("\n" + "="*50)
    success = test_simplified_extraction()
    
    print(f"\n{'='*50}")
    print(f"OVERALL TEST: {'PASS' if success else 'FAIL'}")
    
    if not success:
        print("\nTo debug extraction issues:")
        print("1. Check if Chrome WebDriver is accessible")
        print("2. Verify PFR website structure hasn't changed")
        print("3. Review simplified parsing logic in splits_extractor.py")