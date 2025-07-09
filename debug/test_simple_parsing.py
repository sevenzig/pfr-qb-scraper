#!/usr/bin/env python3
"""Test the new simple table parsing method"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.enhanced_scraper import EnhancedPFRScraper
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_simple_parsing():
    """Test the new simple table parsing"""
    
    print("=== Testing Simple Table Parsing ===")
    
    scraper = EnhancedPFRScraper(rate_limit_delay=1.0)
    
    # Test the new get_qb_main_stats method
    print("Testing get_qb_main_stats with new parsing...")
    
    try:
        results = scraper.get_qb_main_stats(2024)
        players, basic_stats = results
        
        print(f"Found {len(players)} players")
        print(f"Found {len(basic_stats)} basic stats")
        
        if basic_stats:
            print("\nFirst few players:")
            for i, stat in enumerate(basic_stats[:5]):
                print(f"  {i+1}. {stat.player_name} ({stat.team}) - {stat.cmp}/{stat.att}, {stat.yds} yds")
        else:
            print("No basic stats found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_parsing() 