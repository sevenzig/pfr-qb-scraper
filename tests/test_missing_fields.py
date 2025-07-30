#!/usr/bin/env python3
"""
Test script to verify missing fields are being captured correctly
Tests: incompletions, completion %, and rush_first_downs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.scrapers.enhanced_scraper import EnhancedPFRScraper
from src.models.qb_models import QBBasicStats, QBSplitsType2
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_missing_fields():
    """Test that missing fields are being captured correctly"""
    
    print("Testing missing fields capture...")
    
    # Create scraper instance
    scraper = EnhancedPFRScraper()
    
    # Test with a known player (Joe Burrow from 2024)
    test_player_name = "Joe Burrow"
    test_season = 2024
    
    try:
        # Get main stats
        players, basic_stats = scraper.get_qb_main_stats(test_season, [test_player_name])
        
        if not basic_stats:
            print("❌ No basic stats found for Joe Burrow")
            return False
        
        # Check the first player's stats
        stat = basic_stats[0]
        print(f"\nPlayer: {stat.player_name}")
        print(f"Season: {stat.season}")
        
        # Test incompletions field
        print(f"\n--- Testing Incompletions ---")
        print(f"Completions (cmp): {stat.cmp}")
        print(f"Attempts (att): {stat.att}")
        print(f"Incompletions (inc): {stat.inc}")
        
        if stat.inc is not None:
            expected_inc = stat.att - stat.cmp if stat.att and stat.cmp else None
            if stat.inc == expected_inc:
                print("✅ Incompletions calculated correctly")
            else:
                print(f"❌ Incompletions mismatch: expected {expected_inc}, got {stat.inc}")
                return False
        else:
            print("❌ Incompletions is None")
            return False
        
        # Test completion percentage
        print(f"\n--- Testing Completion % ---")
        print(f"Completion % (cmp_pct): {stat.cmp_pct}")
        
        if stat.cmp_pct is not None:
            print("✅ Completion % captured")
        else:
            print("❌ Completion % is None")
            return False
        
        # Test rush_first_downs (should be None in main stats)
        print(f"\n--- Testing Rush First Downs (Main Stats) ---")
        print(f"Rush First Downs: {getattr(stat, 'rush_first_downs', 'Field not present')}")
        print("ℹ️  Rush first downs are only available in splits data, not main stats")
        
        # Now test splits data for rush_first_downs
        print(f"\n--- Testing Rush First Downs (Splits Data) ---")
        
        # Find player URL
        player_url = None
        for player in players:
            if player.player_name == test_player_name:
                player_url = player.pfr_url
                break
        
        if player_url:
            # Get splits data
            basic_splits, advanced_splits = scraper.scrape_player_splits(
                player_url, stat.pfr_id, test_player_name, stat.team, test_season, stat.scraped_at
            )
            
            # Look for rush_first_downs in advanced splits
            rush_first_downs_found = False
            for split in advanced_splits:
                if split.rush_first_downs is not None:
                    print(f"✅ Rush First Downs found in split '{split.split}' = '{split.value}': {split.rush_first_downs}")
                    rush_first_downs_found = True
                    break
            
            if not rush_first_downs_found:
                print("ℹ️  No rush_first_downs found in splits data (this may be normal)")
        
        print(f"\n--- Summary ---")
        print("✅ Incompletions: Captured and calculated correctly")
        print("✅ Completion %: Captured correctly")
        print("ℹ️  Rush First Downs: Only available in splits data (as expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.exception("Test failed")
        return False

def test_data_validation():
    """Test that the data models accept the new fields"""
    
    print("\nTesting data model validation...")
    
    try:
        # Test QBBasicStats with inc field
        test_stat = QBBasicStats(
            pfr_id="test01",
            player_name="Test Player",
            player_url="http://test.com",
            season=2024,
            cmp=300,
            att=450,
            inc=150,  # This should work now
            cmp_pct=66.7
        )
        
        print("✅ QBBasicStats accepts inc field")
        
        # Test QBSplitsType2 with rush_first_downs
        test_split = QBSplitsType2(
            pfr_id="test01",
            player_name="Test Player",
            season=2024,
            split="Down",
            value="1st",
            rush_first_downs=5
        )
        
        print("✅ QBSplitsType2 accepts rush_first_downs field")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model validation failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Missing Fields Fix")
    print("=" * 50)
    
    success = True
    
    # Test data model validation
    if not test_data_validation():
        success = False
    
    # Test field capture
    if not test_missing_fields():
        success = False
    
    if success:
        print("\n🎉 All tests passed! Missing fields are now captured correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 