#!/usr/bin/env python3
"""
Debug script to test the scraper and see what data it's processing
"""

import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.enhanced_scraper import EnhancedPFRScraper
from src.models.qb_models import QBSplitStats, QBSplitsType1
from src.database.db_manager import DatabaseManager

def test_scraper_data_processing():
    """Test the scraper's data processing capabilities"""
    print("Testing scraper data processing...")
    
    # Initialize scraper
    scraper = EnhancedPFRScraper()
    
    # Test with a known player (Joe Burrow)
    test_player_url = "https://www.pro-football-reference.com/players/B/BurrJo00.htm"
    pfr_id = "BurrJo00"
    player_name = "Joe Burrow"
    team = "CIN"
    season = 2024
    scraped_at = datetime.now()
    
    print(f"Testing with player: {player_name} ({pfr_id})")
    
    try:
        # Scrape splits data
        basic_splits, advanced_splits = scraper.scrape_player_splits(
            test_player_url, pfr_id, player_name, team, season, scraped_at
        )
        
        print(f"✓ Successfully scraped data:")
        print(f"  - Basic splits: {len(basic_splits)} records")
        print(f"  - Advanced splits: {len(advanced_splits)} records")
        
        # Check the first few basic splits
        if basic_splits:
            print(f"\nFirst basic split details:")
            first_split = basic_splits[0]
            print(f"  - Split type: {first_split.split}")
            print(f"  - Split value: {first_split.value}")
            print(f"  - Games: {first_split.g}")
            print(f"  - Completions: {first_split.cmp}")
            print(f"  - Attempts: {first_split.att}")
            print(f"  - Yards: {first_split.yds}")
            print(f"  - Rush attempts: {first_split.rush_att}")
            print(f"  - Rush yards: {first_split.rush_yds}")
            print(f"  - Rush TDs: {first_split.rush_td}")
            print(f"  - Total TDs: {first_split.total_td}")
            print(f"  - Fumbles: {first_split.fmb}")
            print(f"  - Fumbles lost: {first_split.fl}")
        
        # Check split types and values
        split_types = set()
        split_values = set()
        for split in basic_splits:
            split_types.add(split.split)
            split_values.add(split.value)
        
        print(f"\nSplit types found: {sorted(split_types)}")
        print(f"Split values found: {sorted(split_values)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error scraping data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_insertion():
    """Test database insertion with sample data"""
    print("\nTesting database insertion...")
    
    try:
        db_manager = DatabaseManager()
        
        # Test connection
        if not db_manager.test_connection():
            print("✗ Database connection failed")
            return False
        
        print("✓ Database connection successful")
        
        # Create a test split record
        test_split = QBSplitStats(
            pfr_id="test01",
            player_name="Test Player",
            season=2024,
            split="Place",
            value="Home",
            g=8,
            w=6,
            l=2,
            t=0,
            cmp=223,
            att=299,
            inc=76,
            cmp_pct=74.58,
            yds=2338,
            td=23,
            int=4,
            rate=116.90,
            sk=25,
            sk_yds=160,
            y_a=7.82,
            ay_a=8.1,
            a_g=37.4,
            y_g=292.3,
            rush_att=15,
            rush_yds=89,
            rush_y_a=5.9,
            rush_td=2,
            rush_a_g=1.9,
            rush_y_g=11.1,
            total_td=25,
            pts=168,
            fmb=3,
            fl=1,
            ff=0,
            fr=0,
            fr_yds=0,
            fr_td=0,
            scraped_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Insert the test record
        inserted_count = db_manager.insert_qb_splits([test_split])
        print(f"✓ Successfully inserted {inserted_count} test record(s)")
        
        # Query to verify insertion
        result = db_manager.query(
            "SELECT * FROM qb_splits WHERE pfr_id = %s AND season = %s",
            ("test01", 2024)
        )
        
        if result:
            print(f"✓ Found {len(result)} record(s) in database")
            record = result[0]
            print(f"  - Split: {record['split']}")
            print(f"  - Value: {record['value']}")
            print(f"  - Rush attempts: {record['rush_att']}")
            print(f"  - Rush yards: {record['rush_yds']}")
            print(f"  - Rush TDs: {record['rush_td']}")
        else:
            print("✗ No records found in database")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error in database test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Debugging QB Scraper Data Processing")
    print("=" * 50)
    
    # Test scraper data processing
    scraper_test_passed = test_scraper_data_processing()
    
    # Test database insertion
    db_test_passed = test_database_insertion()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  Scraper Data Processing: {'✓ PASSED' if scraper_test_passed else '✗ FAILED'}")
    print(f"  Database Insertion: {'✓ PASSED' if db_test_passed else '✗ FAILED'}")
    
    if scraper_test_passed and db_test_passed:
        print("\n✓ All tests passed! The scraper should be working correctly.")
    else:
        print("\n✗ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 