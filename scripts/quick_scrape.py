#!/usr/bin/env python3
"""
Quick script to scrape a single player using configuration file
Just modify player_config.py and run this script!
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import configuration
from player_config import *

# Import scraping function
from scrape_single_player import scrape_single_player, setup_logging

def main():
    """Main function using configuration file"""
    print(f"Quick Scrape - {PLAYER_NAME} ({SEASON})")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Run the scrape
    results = scrape_single_player(
        player_name=PLAYER_NAME,
        season=SEASON,
        save_to_db=SAVE_TO_DATABASE
    )
    
    # Show final result
    if results['success']:
        print(f"\n🎉 SUCCESS! Scraped data for {PLAYER_NAME}")
        print(f"📊 Found {len(results['splits'])} splits")
        if SAVE_TO_DATABASE:
            print("💾 Data saved to database")
        else:
            print("📝 Data scraped but not saved (SAVE_TO_DATABASE = False)")
    else:
        print(f"\n❌ FAILED to scrape data for {PLAYER_NAME}")
        print("Check the logs for details")
    
    return results['success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 