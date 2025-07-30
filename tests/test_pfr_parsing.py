#!/usr/bin/env python3
"""Test the new PFR parsing logic"""

import sys
sys.path.insert(0, 'src')

from scrapers.splits_extractor import SplitsExtractor

def test_parsing_logic():
    """Test the split category and value parsing"""
    
    extractor = SplitsExtractor(None)  # Don't need selenium for this test
    
    print("=== TESTING BASIC SPLITS PARSING ===")
    
    # Test basic splits parsing
    test_cases_basic = [
        ("PlaceHome", None, ("Place", "Home")),
        ("Road", "Place", ("Place", "Road")),
        ("ResultWin", None, ("Result", "Win")),
        ("Loss", "Result", ("Result", "Loss")),
        ("MonthSeptember", None, ("Month", "September")),
        ("October", "Month", ("Month", "October")),
        ("ConferenceAFC", None, ("Conference", "AFC")),
        ("NFC", "Conference", ("Conference", "NFC")),
    ]
    
    for first_cell, current_category, expected in test_cases_basic:
        result = extractor._parse_pfr_split_category_and_value(first_cell, current_category)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} '{first_cell}' (current: {current_category}) -> {result} (expected: {expected})")
    
    print("\n=== TESTING ADVANCED SPLITS PARSING ===")
    
    # Test advanced splits parsing
    test_cases_advanced = [
        ("Down1st", None, ("Down", "1st")),
        ("2nd", "Down", ("Down", "2nd")), 
        ("Yards To Go1-3", None, ("Yards To Go", "1-3")),
        ("4-6", "Yards To Go", ("Yards To Go", "4-6")),
        ("Field PositionOwn 1-10", None, ("Field Position", "Own 1-10")),
        ("Own 21-50", "Field Position", ("Field Position", "Own 21-50")),
        ("QuarterEarly", None, ("Quarter", "Early")),
        ("2nd Half", "Quarter", ("Quarter", "2nd Half")),
    ]
    
    for first_cell, current_category, expected in test_cases_advanced:
        result = extractor._parse_pfr_advanced_split_category_and_value(first_cell, current_category)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} '{first_cell}' (current: {current_category}) -> {result} (expected: {expected})")
    
    print("\n=== TESTING SAFE CONVERSION FUNCTIONS ===")
    
    # Test safe conversion functions
    conversion_tests = [
        ("123", extractor._safe_int, 123),
        ("45.67", extractor._safe_float, 45.67),
        ("89.5%", extractor._safe_percentage, 89.5),
        ("", extractor._safe_int, None),
        ("N/A", extractor._safe_float, None),
    ]
    
    for value, func, expected in conversion_tests:
        result = func(value)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} {func.__name__}('{value}') -> {result} (expected: {expected})")

if __name__ == "__main__":
    test_parsing_logic()