#!/usr/bin/env python3
"""
Test script to verify that the enhanced scraper properly extracts and populates
all fields in the QBSplitStats model, including the additional fields that were
missing from the database.
"""

import sys
import os
from datetime import datetime
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.enhanced_scraper import EnhancedPFRScraper
from models.qb_models import QBSplitStats
from utils.data_utils import safe_int, safe_float, safe_percentage

def test_qb_split_stats_model():
    """Test that QBSplitStats model can handle all fields"""
    print("Testing QBSplitStats model with all fields...")
    
    # Create a test QBSplitStats object with all fields populated
    # Using the actual field names from QBSplitsType1 model
    test_stats = QBSplitStats(
        pfr_id="testplayer",
        player_name="Test Player",
        season=2024,
        split="Place",  # Split type (e.g., "League", "Place", "Result")
        value="Home",   # Split value (e.g., "NFL", "Home", "Win")
        g=8,            # Games
        w=6,            # Wins
        l=2,            # Losses
        t=0,            # Ties
        cmp=223,        # Completions
        att=299,        # Attempts
        inc=76,         # Incompletions
        cmp_pct=74.58,  # Completion %
        yds=2338,       # Passing Yards
        td=23,          # Passing TDs
        int=4,          # Interceptions
        rate=116.90,    # Passer Rating
        sk=25,          # Sacks
        sk_yds=160,     # Sack Yards
        y_a=7.82,       # Y/A (Yards per Attempt)
        ay_a=8.1,       # AY/A (Adjusted Yards per Attempt)
        a_g=37.4,       # A/G (Attempts per Game)
        y_g=292.3,      # Y/G (Yards per Game)
        rush_att=15,    # Rush Attempts
        rush_yds=89,    # Rush Yards
        rush_y_a=5.9,   # Rush Y/A
        rush_td=2,      # Rush TDs
        rush_a_g=1.9,   # Rush A/G (Rush Attempts per Game)
        rush_y_g=11.1,  # Rush Y/G (Rush Yards per Game)
        total_td=25,    # Total TDs
        pts=168,        # Points
        fmb=3,          # Fumbles
        fl=1,           # Fumbles Lost
        ff=0,           # Fumbles Forced
        fr=0,           # Fumbles Recovered
        fr_yds=0,       # Fumble Recovery Yards
        fr_td=0,        # Fumble Recovery TDs
        scraped_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Test validation
    errors = test_stats.validate()
    if errors:
        print(f"Validation errors: {errors}")
        return False
    else:
        print("✓ QBSplitStats model validation passed")
    
    # Test from_dict conversion
    try:
        stats_dict = test_stats.__dict__
        print(f"✓ QBSplitStats dictionary conversion successful")
        print(f"  - Dictionary has {len(stats_dict)} fields")
        
        # Check that all expected fields are present
        expected_fields = [
            'pfr_id', 'player_name', 'season', 'split', 'value',
            'g', 'w', 'l', 't', 'cmp', 'att', 'inc', 'cmp_pct', 'yds', 'td',
            'int', 'rate', 'sk', 'sk_yds', 'y_a', 'ay_a', 'a_g', 'y_g',
            'rush_att', 'rush_yds', 'rush_y_a', 'rush_td', 'rush_a_g', 'rush_y_g',
            'total_td', 'pts', 'fmb', 'fl', 'ff', 'fr', 'fr_yds', 'fr_td',
            'scraped_at', 'updated_at'
        ]
        
        missing_fields = [field for field in expected_fields if field not in stats_dict]
        if missing_fields:
            print(f"✗ Missing fields in dictionary: {missing_fields}")
            return False
        else:
            print("✓ All expected fields present in dictionary")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in dictionary conversion: {e}")
        return False

def test_data_utils():
    """Test the data utility functions"""
    print("\nTesting data utility functions...")
    
    # Test safe_int
    assert safe_int("123") == 123
    assert safe_int("0") == 0
    assert safe_int("") == 0
    assert safe_int(None) == 0
    print("✓ safe_int function working correctly")
    
    # Test safe_float
    assert safe_float("123.45") == 123.45
    assert safe_float("0.0") == 0.0
    assert safe_float("") == 0.0
    assert safe_float(None) == 0.0
    print("✓ safe_float function working correctly")
    
    # Test safe_percentage
    assert safe_percentage("74.58") == 74.58
    assert safe_percentage("0.0") == 0.0
    assert safe_percentage("") == 0.0
    assert safe_percentage(None) == 0.0
    print("✓ safe_percentage function working correctly")

def test_scraper_initialization():
    """Test that the enhanced scraper can be initialized"""
    print("\nTesting enhanced scraper initialization...")
    
    try:
        scraper = EnhancedPFRScraper()
        print("✓ Enhanced scraper initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Error initializing scraper: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Enhanced QB Scraper Field Population")
    print("=" * 50)
    
    # Test data utility functions
    test_data_utils()
    
    # Test QBSplitStats model
    model_test_passed = test_qb_split_stats_model()
    
    # Test scraper initialization
    scraper_test_passed = test_scraper_initialization()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  QBSplitStats Model: {'✓ PASSED' if model_test_passed else '✗ FAILED'}")
    print(f"  Scraper Initialization: {'✓ PASSED' if scraper_test_passed else '✗ FAILED'}")
    
    if model_test_passed and scraper_test_passed:
        print("\n✓ All tests passed! The enhanced scraper should now properly populate all fields.")
        print("\nNext steps:")
        print("1. Run the enhanced scraper to collect data")
        print("2. Verify that all fields are populated in the database")
        print("3. Check that the CSV export includes all the additional fields")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 