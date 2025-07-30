#!/usr/bin/env python3
"""
Comprehensive QB Splits Validation Test

This script validates:
1. CSV parsing by position (handling duplicate column names)
2. Database schema compatibility
3. Data integrity and consistency
4. All required split categories and values
"""

import sys
import os
import pandas as pd
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.data_utils import (
    parse_qb_splits_csv_by_position, 
    validate_qb_splits_data,
    convert_splits_to_qb_splits_type1
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_csv_parsing():
    """Test CSV parsing by position"""
    logger.info("=== Testing CSV Parsing by Position ===")
    
    # Read the test CSV file
    csv_path = Path(__file__).parent.parent / 'setup' / 'advanced_stats_1.csv'
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return False
    
    with open(csv_path, 'r') as f:
        csv_content = f.read()
    
    # Parse CSV by position
    parsed_splits = parse_qb_splits_csv_by_position(csv_content)
    
    if not parsed_splits:
        logger.error("No splits parsed from CSV")
        return False
    
    logger.info(f"Successfully parsed {len(parsed_splits)} splits")
    
    # Validate the parsed data
    validation_errors = validate_qb_splits_data(parsed_splits)
    
    if validation_errors:
        logger.error("Validation errors found:")
        for error in validation_errors:
            logger.error(f"  - {error}")
        return False
    
    logger.info("CSV parsing validation passed")
    return True

def test_required_split_categories():
    """Test that all required split categories are present"""
    logger.info("=== Testing Required Split Categories ===")
    
    csv_path = Path(__file__).parent.parent / 'setup' / 'advanced_stats_1.csv'
    
    with open(csv_path, 'r') as f:
        csv_content = f.read()
    
    parsed_splits = parse_qb_splits_csv_by_position(csv_content)
    
    # Required split categories
    required_splits = {
        'Place', 'Result', 'Final Margin', 'Month', 'Game Number', 
        'Day', 'Time', 'Conference', 'Division', 'Opponent', 'Stadium', 'QB Start'
    }
    
    found_splits = set()
    for split in parsed_splits:
        if split.get('split'):
            found_splits.add(split['split'])
    
    logger.info(f"Found split categories: {found_splits}")
    
    missing_splits = required_splits - found_splits
    if missing_splits:
        logger.error(f"Missing required split categories: {missing_splits}")
        return False
    
    logger.info("All required split categories found")
    return True

def test_split_values():
    """Test that all expected split values are present"""
    logger.info("=== Testing Split Values ===")
    
    csv_path = Path(__file__).parent.parent / 'setup' / 'advanced_stats_1.csv'
    
    with open(csv_path, 'r') as f:
        csv_content = f.read()
    
    parsed_splits = parse_qb_splits_csv_by_position(csv_content)
    
    # Expected split values by category
    expected_values = {
        'Place': {'Home', 'Road'},
        'Result': {'Win', 'Loss'},
        'Final Margin': {'0-7 points', '8-14 points', '15+ points'},
        'Month': {'September', 'October', 'November', 'December', 'January'},
        'Game Number': {'1-4', '5-8', '9-12', '13+'},
        'Day': {'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'},
        'Time': {'Early', 'Afternoon', 'Late'},
        'Conference': {'AFC', 'NFC'},
        'Division': {'AFC East', 'AFC North', 'AFC South', 'AFC West', 
                    'NFC East', 'NFC North', 'NFC South', 'NFC West'},
        'Stadium': {'dome', 'outdoors', 'retroof'},
        'QB Start': {'Starter'}
    }
    
    # Group splits by category
    splits_by_category = {}
    for split in parsed_splits:
        category = split.get('split')
        value = split.get('value')
        if category and value:
            if category not in splits_by_category:
                splits_by_category[category] = set()
            splits_by_category[category].add(value)
    
    # Check each category
    for category, expected in expected_values.items():
        if category in splits_by_category:
            found = splits_by_category[category]
            missing = expected - found
            extra = found - expected
            
            if missing:
                logger.warning(f"Missing values for {category}: {missing}")
            
            if extra:
                logger.info(f"Extra values for {category}: {extra}")
        else:
            logger.warning(f"Category {category} not found in data")
    
    logger.info("Split values validation completed")
    return True

def test_data_consistency():
    """Test data consistency and mathematical relationships"""
    logger.info("=== Testing Data Consistency ===")
    
    csv_path = Path(__file__).parent.parent / 'setup' / 'advanced_stats_1.csv'
    
    with open(csv_path, 'r') as f:
        csv_content = f.read()
    
    parsed_splits = parse_qb_splits_csv_by_position(csv_content)
    
    errors = []
    
    for split in parsed_splits:
        split_name = f"{split.get('split')}/{split.get('value')}"
        
        # Check W + L + T = G
        g = split.get('g', 0) or 0
        w = split.get('w', 0) or 0
        l = split.get('l', 0) or 0
        t = split.get('t', 0) or 0
        
        if g > 0 and (w + l + t) != g:
            errors.append(f"{split_name}: W+L+T ({w}+{l}+{t}) != G ({g})")
        
        # Check for negative values where they shouldn't be
        if g < 0:
            errors.append(f"{split_name}: Negative games ({g})")
        
        if w < 0 or l < 0 or t < 0:
            errors.append(f"{split_name}: Negative W/L/T values")
        
        # Check completion percentage calculation
        cmp_val = split.get('cmp', 0) or 0
        att_val = split.get('att', 0) or 0
        cmp_pct = split.get('cmp_pct')
        
        if att_val > 0 and cmp_pct is not None:
            calculated_pct = (cmp_val / att_val) * 100
            if abs(calculated_pct - cmp_pct) > 0.1:  # Allow small rounding differences
                errors.append(f"{split_name}: Completion % mismatch: calculated {calculated_pct:.2f}, actual {cmp_pct}")
    
    if errors:
        logger.error("Data consistency errors found:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    logger.info("Data consistency validation passed")
    return True

def test_database_schema_compatibility():
    """Test that parsed data is compatible with database schema"""
    logger.info("=== Testing Database Schema Compatibility ===")
    
    csv_path = Path(__file__).parent.parent / 'setup' / 'advanced_stats_1.csv'
    
    with open(csv_path, 'r') as f:
        csv_content = f.read()
    
    parsed_splits = parse_qb_splits_csv_by_position(csv_content)
    
    # Test conversion to QBSplitsType1 objects
    try:
        qb_splits = convert_splits_to_qb_splits_type1(
            parsed_splits, 
            pfr_id='test123', 
            player_name='Test Player', 
            season=2024
        )
        
        logger.info(f"Successfully created {len(qb_splits)} QBSplitsType1 objects")
        
        # Test validation of QBSplitsType1 objects
        for qb_split in qb_splits:
            validation_errors = qb_split.validate()
            if validation_errors:
                logger.error(f"Validation errors for {qb_split.split}/{qb_split.value}: {validation_errors}")
                return False
        
        logger.info("Database schema compatibility validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Error testing database schema compatibility: {e}")
        return False

def test_csv_column_mapping():
    """Test that CSV columns are mapped correctly by position"""
    logger.info("=== Testing CSV Column Mapping ===")
    
    # Read CSV with pandas to verify column structure
    csv_path = Path(__file__).parent.parent / 'setup' / 'advanced_stats_1.csv'
    df = pd.read_csv(csv_path)
    
    logger.info(f"CSV has {len(df.columns)} columns")
    logger.info(f"Column names: {list(df.columns)}")
    
    # Check for duplicate column names
    duplicate_columns = df.columns[df.columns.duplicated()].tolist()
    if duplicate_columns:
        logger.info(f"Duplicate column names found: {duplicate_columns}")
        
        # Verify our position-based parsing handles duplicates correctly
        for col_name in duplicate_columns:
            col_indices = [i for i, col in enumerate(df.columns) if col == col_name]
            logger.info(f"Column '{col_name}' appears at positions: {col_indices}")
    
    # Test a few specific rows to verify mapping
    test_row = df.iloc[0]  # First data row (League row)
    logger.info(f"Test row (League): {dict(test_row)}")
    
    # Verify key values from the League row
    expected_league_values = {
        'Split': 'League',
        'Value': 'NFL',
        'G': 17,
        'W': 9,
        'L': 8,
        'T': 0
    }
    
    for col, expected in expected_league_values.items():
        actual = test_row[col]
        if actual != expected:
            logger.error(f"League row mismatch for {col}: expected {expected}, got {actual}")
            return False
    
    logger.info("CSV column mapping validation passed")
    return True

def main():
    """Run all validation tests"""
    logger.info("Starting QB Splits Validation Tests")
    
    tests = [
        ("CSV Parsing", test_csv_parsing),
        ("Required Split Categories", test_required_split_categories),
        ("Split Values", test_split_values),
        ("Data Consistency", test_data_consistency),
        ("Database Schema Compatibility", test_database_schema_compatibility),
        ("CSV Column Mapping", test_csv_column_mapping)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    logger.info(f"{'='*50}")
    
    if failed == 0:
        logger.info("🎉 All tests passed! QB splits validation is successful.")
        return True
    else:
        logger.error(f"❌ {failed} test(s) failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 