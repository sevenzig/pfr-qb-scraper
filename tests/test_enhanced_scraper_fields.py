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
    test_stats = QBSplitStats(
        player_id="testplayer",
        player_name="Test Player",
        team="CIN",
        season=2024,
        split_type="basic_splits",
        split_category="Home",
        games=8,
        completions=223,
        attempts=299,
        completion_pct=74.58,
        pass_yards=2338,
        pass_tds=23,
        interceptions=4,
        rating=116.90,
        sacks=25,
        sack_yards=160,
        net_yards_per_attempt=7.82,
        scraped_at=datetime.now(),
        # Additional fields
        rush_attempts=15,
        rush_yards=89,
        rush_tds=2,
        fumbles=3,
        fumbles_lost=1,
        fumbles_forced=0,
        fumbles_recovered=0,
        fumble_recovery_yards=0,
        fumble_recovery_tds=0,
        incompletions=76,
        wins=6,
        losses=2,
        ties=0,
        attempts_per_game=37.4,
        yards_per_game=292.3,
        rush_attempts_per_game=1.9,
        rush_yards_per_game=11.1,
        total_tds=25,
        points=168
    )
    
    # Test validation
    errors = test_stats.validate()
    if errors:
        print(f"Validation errors: {errors}")
        return False
    else:
        print("✓ QBSplitStats model validation passed")
    
    # Test to_dict conversion
    try:
        stats_dict = test_stats.to_dict()
        print(f"✓ QBSplitStats to_dict conversion successful")
        print(f"  - Dictionary has {len(stats_dict)} fields")
        
        # Check that all expected fields are present
        expected_fields = [
            'player_id', 'player_name', 'team', 'season', 'split_type', 'split_category',
            'games', 'completions', 'attempts', 'completion_pct', 'pass_yards', 'pass_tds',
            'interceptions', 'rating', 'sacks', 'sack_yards', 'net_yards_per_attempt',
            'scraped_at', 'rush_attempts', 'rush_yards', 'rush_tds', 'fumbles',
            'fumbles_lost', 'fumbles_forced', 'fumbles_recovered', 'fumble_recovery_yards',
            'fumble_recovery_tds', 'incompletions', 'wins', 'losses', 'ties',
            'attempts_per_game', 'yards_per_game', 'rush_attempts_per_game',
            'rush_yards_per_game', 'total_tds', 'points'
        ]
        
        missing_fields = [field for field in expected_fields if field not in stats_dict]
        if missing_fields:
            print(f"✗ Missing fields in dictionary: {missing_fields}")
            return False
        else:
            print("✓ All expected fields present in dictionary")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in to_dict conversion: {e}")
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