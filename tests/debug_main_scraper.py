#!/usr/bin/env python3
"""
Debug what the main scraper is getting for Joe Burrow
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.scrapers.enhanced_scraper import EnhancedPFRScraper
from src.core.selenium_manager import SeleniumManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_main_scraper():
    """Debug what the main scraper is getting for Joe Burrow"""
    
    print("DEBUGGING MAIN SCRAPER")
    print("=" * 60)
    
    # Initialize scraper
    selenium_manager = SeleniumManager()
    scraper = EnhancedPFRScraper(selenium_manager)
    
    try:
        # Get Joe Burrow's main stats
        print("\n--- GETTING MAIN STATS ---")
        players, qb_stats = scraper.get_qb_main_stats(2024, ["Joe Burrow"])
        
        print(f"Found {len(players)} players")
        print(f"Found {len(qb_stats)} QB stats")
        
        for stat in qb_stats:
            print(f"\nJoe Burrow 2024 Stats:")
            print(f"  PFR ID: {stat.pfr_id}")
            print(f"  Player Name: {stat.player_name}")
            print(f"  Season: {stat.season}")
            print(f"  Team: {stat.team}")
            print(f"  Games: {stat.g}")
            print(f"  Games Started: {stat.gs}")
            print(f"  Completions: {stat.cmp}")
            print(f"  Attempts: {stat.att}")
            print(f"  Yards: {stat.yds}")
            print(f"  TDs: {stat.td}")
            print(f"  INTs: {stat.int}")
            print(f"  Rating: {stat.rate}")
            print(f"  Player URL: {stat.player_url}")
        
        # Check the actual URL being scraped
        print("\n--- CHECKING SCRAPED URL ---")
        if qb_stats:
            stat = qb_stats[0]
            print(f"Scraped from: {stat.player_url}")
            
            # Get the actual page content
            print("\n--- GETTING ACTUAL PAGE CONTENT ---")
            selenium_manager.start_session()
            page_data = selenium_manager.get_page(stat.player_url, enable_js=True)
            
            if page_data['success']:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(page_data['html'], 'html.parser')
                
                # Look for the stats table
                stats_table = soup.find('table', id='stats')
                if stats_table:
                    print("Found stats table")
                    # Look for 2024 row
                    rows = stats_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            cell_texts = [c.get_text(strip=True) for c in cells]
                            if '2024' in cell_texts:
                                print(f"2024 row found: {cell_texts[:10]}")  # First 10 cells
                                break
                else:
                    print("No stats table found")
            else:
                print(f"Failed to get page: {page_data['error']}")
        
    except Exception as e:
        print(f"Error debugging main scraper: {e}")
        logger.error(f"Error debugging main scraper: {e}", exc_info=True)
    
    finally:
        selenium_manager.end_session()

if __name__ == "__main__":
    debug_main_scraper() 