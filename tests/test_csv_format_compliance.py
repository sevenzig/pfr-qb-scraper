#!/usr/bin/env python3
"""
Test script to validate CSV format compliance for QB splits extraction.
Ensures that scraped data matches advanced_stats_1.csv and advanced_stats.2.csv exactly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import SeleniumManager, SeleniumConfig
from src.config.config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_csv_format_compliance():
    """Test that the splits extractor matches CSV format exactly"""
    
    print("=== Testing CSV Format Compliance ===")
    
    # Load reference CSV files
    try:
        basic_csv = pd.read_csv('../setup/advanced_stats_1.csv')
        advanced_csv = pd.read_csv('../setup/advanced_stats.2.csv')
        print(f"✅ Loaded reference CSV files:")
        print(f"  - advanced_stats_1.csv: {len(basic_csv)} rows, {len(basic_csv.columns)} columns")
        print(f"  - advanced_stats.2.csv: {len(advanced_csv)} rows, {len(advanced_csv.columns)} columns")
    except FileNotFoundError as e:
        print(f"❌ Failed to load reference CSV files: {e}")
        return False
    
    # Get expected column names from CSV files
    basic_csv_columns = list(basic_csv.columns)
    advanced_csv_columns = list(advanced_csv.columns)
    
    print(f"\n--- CSV Column Analysis ---")
    print(f"Basic splits CSV columns ({len(basic_csv_columns)}):")
    for i, col in enumerate(basic_csv_columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\nAdvanced splits CSV columns ({len(advanced_csv_columns)}):")
    for i, col in enumerate(advanced_csv_columns, 1):
        print(f"  {i:2d}. {col}")
    
    # Get field lists from SplitsExtractor
    from src.scrapers.splits_extractor import SplitsExtractor
    
    print(f"\n--- Extractor Field Lists ---")
    print(f"Basic splits fields ({len(SplitsExtractor.QB_SPLITS_FIELDS)}):")
    for i, field in enumerate(SplitsExtractor.QB_SPLITS_FIELDS, 1):
        print(f"  {i:2d}. {field}")
    
    print(f"\nAdvanced splits fields ({len(SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS)}):")
    for i, field in enumerate(SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS, 1):
        print(f"  {i:2d}. {field}")
    
    # Validate field count matches
    basic_match = len(basic_csv_columns) == len(SplitsExtractor.QB_SPLITS_FIELDS)
    advanced_match = len(advanced_csv_columns) == len(SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS)
    
    print(f"\n--- Field Count Validation ---")
    print(f"Basic splits: CSV has {len(basic_csv_columns)} columns, extractor has {len(SplitsExtractor.QB_SPLITS_FIELDS)} fields")
    print(f"  {'✅' if basic_match else '❌'} Field count matches")
    
    print(f"Advanced splits: CSV has {len(advanced_csv_columns)} columns, extractor has {len(SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS)} fields")
    print(f"  {'✅' if advanced_match else '❌'} Field count matches")
    
    # Validate field names match (case-insensitive)
    def normalize_field_name(name):
        """Normalize field name for comparison"""
        return name.lower().replace(' ', '_').replace('%', '_pct').replace('1d', 'first_downs')
    
    basic_csv_fields_normalized = [normalize_field_name(col) for col in basic_csv_columns]
    advanced_csv_fields_normalized = [normalize_field_name(col) for col in advanced_csv_columns]
    
    basic_extractor_fields_normalized = [normalize_field_name(field) for field in SplitsExtractor.QB_SPLITS_FIELDS]
    advanced_extractor_fields_normalized = [normalize_field_name(field) for field in SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS]
    
    print(f"\n--- Field Name Validation ---")
    
    # Check basic splits field mapping
    basic_mismatches = []
    for i, (csv_field, extractor_field) in enumerate(zip(basic_csv_fields_normalized, basic_extractor_fields_normalized)):
        if csv_field != extractor_field:
            basic_mismatches.append((basic_csv_columns[i], SplitsExtractor.QB_SPLITS_FIELDS[i], csv_field, extractor_field))
    
    if basic_mismatches:
        print(f"❌ Basic splits field mismatches:")
        for csv_orig, extractor_orig, csv_norm, extractor_norm in basic_mismatches:
            print(f"  CSV: '{csv_orig}' -> '{csv_norm}' vs Extractor: '{extractor_orig}' -> '{extractor_norm}'")
    else:
        print(f"✅ Basic splits field names match")
    
    # Check advanced splits field mapping
    advanced_mismatches = []
    for i, (csv_field, extractor_field) in enumerate(zip(advanced_csv_fields_normalized, advanced_extractor_fields_normalized)):
        if csv_field != extractor_field:
            advanced_mismatches.append((advanced_csv_columns[i], SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS[i], csv_field, extractor_field))
    
    if advanced_mismatches:
        print(f"❌ Advanced splits field mismatches:")
        for csv_orig, extractor_orig, csv_norm, extractor_norm in advanced_mismatches:
            print(f"  CSV: '{csv_orig}' -> '{csv_norm}' vs Extractor: '{extractor_orig}' -> '{extractor_norm}'")
    else:
        print(f"✅ Advanced splits field names match")
    
    # Test CSV format validation method
    print(f"\n--- CSV Format Validation Method Test ---")
    
    # Create a mock SplitsExtractor instance
    selenium_manager = SeleniumManager(SeleniumConfig())
    extractor = SplitsExtractor(selenium_manager)
    
    # Test with valid data matching CSV format exactly
    valid_basic_data = {
        'split': 'League', 'value': 'NFL', 'g': 17, 'w': 9, 'l': 8, 't': 0,
        'cmp': 460, 'att': 652, 'inc': 192, 'cmp_pct': 70.55, 'yds': 4918,
        'td': 43, 'int': 9, 'rate': 108.5, 'sk': 48, 'yds.1': 278,
        'y/a': 7.54, 'ay/a': 8.24, 'a/g': 38.4, 'y/g': 289.3,
        'att.1': 42, 'yds.2': 201, 'y/a.1': 4.79, 'td.1': 2,
        'a/g.1': 2.5, 'y/g.1': 11.8, 'td.2': 2, 'pts': 12,
        'fmb': 11, 'fl': 5, 'ff': 0, 'fr': 2, 'yds.3': -3, 'td.3': 0
    }
    
    valid_advanced_data = {
        'split': 'Down', 'value': '1st', 'cmp': 179, 'att': 243, 'inc': 64,
        'cmp_pct': 73.66, 'yds': 2089, 'td': 12, '1d': 77, 'int': 3,
        'rate': 110.6, 'sk': 12, 'yds.1': -64, 'y/a': 8.6, 'ay/a': 9.03,
        'att.1': 18, 'yds.2': 51, 'y/a.1': 2.8, 'td.1': 0,
        '1d.1': 3
    }
    
    # Test basic splits validation
    basic_errors = extractor._validate_csv_format_compliance(valid_basic_data, 'basic_splits', 'Test Player', 2024)
    if basic_errors:
        print(f"❌ Basic splits validation failed: {basic_errors}")
    else:
        print(f"✅ Basic splits validation passed")
    
    # Test advanced splits validation
    advanced_errors = extractor._validate_csv_format_compliance(valid_advanced_data, 'advanced_splits', 'Test Player', 2024)
    if advanced_errors:
        print(f"❌ Advanced splits validation failed: {advanced_errors}")
    else:
        print(f"✅ Advanced splits validation passed")
    
    # Test with missing fields
    invalid_basic_data = valid_basic_data.copy()
    del invalid_basic_data['g']  # Remove a required field
    
    basic_errors = extractor._validate_csv_format_compliance(invalid_basic_data, 'basic_splits', 'Test Player', 2024)
    if basic_errors:
        print(f"✅ Basic splits validation correctly detected missing field: {basic_errors}")
    else:
        print(f"❌ Basic splits validation failed to detect missing field")
    
    # Summary
    all_tests_passed = (
        basic_match and advanced_match and 
        len(basic_mismatches) == 0 and len(advanced_mismatches) == 0 and
        len(basic_errors) == 0 and len(advanced_errors) == 0
    )
    
    print(f"\n--- Summary ---")
    if all_tests_passed:
        print(f"✅ All CSV format compliance tests passed!")
        print(f"   The splits extractor correctly matches the CSV format from advanced_stats_1.csv and advanced_stats.2.csv")
    else:
        print(f"❌ Some CSV format compliance tests failed")
        print(f"   Please review the field mappings and ensure they match the CSV format exactly")
    
    return all_tests_passed

if __name__ == "__main__":
    success = test_csv_format_compliance()
    sys.exit(0 if success else 1) 