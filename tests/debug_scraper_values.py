#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.scrapers.selenium_enhanced_scraper import SeleniumEnhancedPFRScraper
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_scraper_values():
    """Debug what values the scraper is calculating"""
    
    print("Debugging scraper values")
    print("=" * 60)
    
    try:
        # Use Selenium scraper
        with SeleniumEnhancedPFRScraper(min_delay=7.0, max_delay=12.0) as scraper:
            # Get Joe Burrow's stats
            players, stats = scraper.get_qb_main_stats(2024, player_names=["Joe Burrow"])
            
            if stats:
                stat = stats[0]  # Joe Burrow's stats
                print(f"Joe Burrow 2024 stats:")
                print(f"  Player: {stat.player_name}")
                print(f"  PFR ID: {stat.pfr_id}")
                print(f"  Team: {stat.team}")
                print(f"  Completions: {stat.cmp}")
                print(f"  Attempts: {stat.att}")
                print(f"  Incompletions: {stat.inc}")
                print(f"  Success %: {stat.succ_pct}")
                print(f"  Completion %: {stat.cmp_pct}")
                print(f"  First Downs: {stat.first_downs}")
                print(f"  Yards: {stat.yds}")
                print(f"  TDs: {stat.td}")
                
                # Calculate expected values
                if stat.att and stat.cmp:
                    expected_inc = stat.att - stat.cmp
                    print(f"  Expected inc: {expected_inc}")
                
                if stat.succ_pct == 0.0:
                    print(f"  ⚠️  Success % is 0.0 - this should be scraped from 'pass_success'")
                
                if stat.inc is None:
                    print(f"  ⚠️  Incompletions is None - should be calculated as att - cmp")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_scraper_values() 