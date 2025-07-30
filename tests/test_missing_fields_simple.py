#!/usr/bin/env python3
"""
Simple test script to verify missing fields are being captured correctly
Tests: incompletions, completion %, and rush_first_downs
This test doesn't require HTTP requests to PFR
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models.qb_models import QBBasicStats, QBSplitsType2
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_models():
    """Test that the data models accept the new fields"""
    
    print("Testing data model validation...")
    
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

def test_scraper_logic():
    """Test the scraper logic with mock HTML data"""
    
    print("\nTesting scraper logic with mock data...")
    
    # Mock HTML data representing a QB stats row
    mock_html = """
    <tr>
        <td data-stat="rank">1</td>
        <td data-stat="name_display"><a href="/players/B/BurrJo01.htm">Joe Burrow</a></td>
        <td data-stat="age">28</td>
        <td data-stat="team_name_abbr"><a href="/teams/cin/2024.htm">CIN</a></td>
        <td data-stat="pos">QB</td>
        <td data-stat="games">17</td>
        <td data-stat="games_started">17</td>
        <td data-stat="qb_rec">9-8-0</td>
        <td data-stat="pass_cmp">460</td>
        <td data-stat="pass_att">652</td>
        <td data-stat="pass_cmp_pct">70.6</td>
        <td data-stat="pass_yds">4918</td>
        <td data-stat="pass_td">43</td>
        <td data-stat="pass_td_pct">6.6</td>
        <td data-stat="pass_int">9</td>
        <td data-stat="pass_int_pct">1.4</td>
        <td data-stat="pass_first_down">253</td>
        <td data-stat="pass_success">53.6</td>
        <td data-stat="pass_long">70</td>
        <td data-stat="pass_yds_per_att">7.5</td>
        <td data-stat="pass_adj_yds_per_att">8.24</td>
        <td data-stat="pass_yds_per_cmp">10.7</td>
        <td data-stat="pass_yds_per_g">289.3</td>
        <td data-stat="pass_rating">108.5</td>
        <td data-stat="qbr">74.7</td>
        <td data-stat="pass_sacked">48</td>
        <td data-stat="pass_sacked_yds">278</td>
        <td data-stat="pass_sacked_pct">6.86</td>
        <td data-stat="pass_net_yds_per_att">6.63</td>
        <td data-stat="pass_adj_net_yds_per_att">7.28</td>
        <td data-stat="comebacks">1</td>
        <td data-stat="gwd">2</td>
        <td data-stat="awards">PB,AP MVP-4,AP OPoY-5,AP CPoY-1</td>
    </tr>
    """
    
    try:
        from src.scrapers.enhanced_scraper import EnhancedPFRScraper
        from src.utils.data_utils import safe_int, safe_float, safe_percentage
        
        # Create scraper instance
        scraper = EnhancedPFRScraper()
        
        # Parse the mock HTML
        soup = BeautifulSoup(mock_html, 'html.parser')
        row = soup.find('tr')
        
        # Test the _extract_stats_from_row method
        stats = scraper._extract_stats_from_row(row)
        
        print(f"Extracted stats: {stats}")
        
        # Test specific fields
        print(f"\n--- Testing Extracted Fields ---")
        print(f"Completions (cmp): {stats['cmp']}")
        print(f"Attempts (att): {stats['att']}")
        print(f"Incompletions (inc): {stats['inc']}")
        print(f"Completion % (cmp_pct): {stats['cmp_pct']}")
        
        # Verify incompletions calculation
        expected_inc = stats['att'] - stats['cmp'] if stats['att'] and stats['cmp'] else None
        if stats['inc'] == expected_inc:
            print("✅ Incompletions calculated correctly")
        else:
            print(f"❌ Incompletions mismatch: expected {expected_inc}, got {stats['inc']}")
            return False
        
        # Verify completion percentage
        if stats['cmp_pct'] is not None:
            print("✅ Completion % captured correctly")
        else:
            print("❌ Completion % is None")
            return False
        
        # Verify rush_first_downs is not in main stats (as expected)
        if 'rush_first_downs' not in stats:
            print("✅ Rush first downs correctly not present in main stats (as expected)")
        else:
            print("❌ Rush first downs unexpectedly present in main stats")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper logic test failed: {e}")
        logger.exception("Test failed")
        return False

def test_database_schema():
    """Test that the database schema includes the new fields"""
    
    print("\nTesting database schema...")
    
    try:
        # Read the schema file
        with open('sql/schema.sql', 'r') as f:
            schema_content = f.read()
        
        # Check for inc field in qb_passing_stats table
        if 'inc INTEGER,  -- Incompletions (calculated: att - cmp)' in schema_content:
            print("✅ Database schema includes inc field")
        else:
            print("❌ Database schema missing inc field")
            return False
        
        # Check for rush_first_downs field in qb_splits_advanced table
        if 'rush_first_downs INTEGER,  -- Rush First Downs' in schema_content:
            print("✅ Database schema includes rush_first_downs field")
        else:
            print("❌ Database schema missing rush_first_downs field")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Missing Fields Fix (Simple Version)")
    print("=" * 50)
    
    success = True
    
    # Test data model validation
    if not test_data_models():
        success = False
    
    # Test scraper logic with mock data
    if not test_scraper_logic():
        success = False
    
    # Test database schema
    if not test_database_schema():
        success = False
    
    if success:
        print("\n🎉 All tests passed! Missing fields are now captured correctly.")
        print("\nSummary of fixes:")
        print("✅ Incompletions (inc): Added to scraper, model, and database schema")
        print("✅ Completion % (cmp_pct): Already working correctly")
        print("✅ Rush First Downs: Available in splits data (as expected)")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 