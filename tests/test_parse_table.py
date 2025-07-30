#!/usr/bin/env python3
"""
Test script to check if parse_table_data is working
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.enhanced_scraper import EnhancedPFRScraper
import requests
from bs4 import BeautifulSoup

def test_parse_table():
    """Test the parse_table_data method"""
    print("Testing parse_table_data method...")
    
    # Create scraper instance
    scraper = EnhancedPFRScraper()
    
    # Get the 2024 passing page
    stats_url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    response = requests.get(stats_url, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Test parsing with 'passing' table ID
    print("Testing with 'passing' table ID...")
    df = scraper.parse_table_data(soup, 'passing')
    
    if df is not None:
        print(f"✓ Successfully parsed table with {len(df)} rows")
        
        # Look for Joe Burrow
        for i, row in df.iterrows():
            player_name = str(row.get('Player', ''))
            if 'burrow' in player_name.lower():
                print(f"  Found Joe Burrow: {player_name}")
                print(f"    Games: {row.get('G', 'N/A')}")
                print(f"    Yards: {row.get('Yds', 'N/A')}")
                print(f"    TDs: {row.get('TD', 'N/A')}")
                break
    else:
        print("✗ Failed to parse table with 'passing' ID")
    
    # Test parsing with 'passing' table ID
    print("\nTesting with 'passing' table ID...")
    df2 = scraper.parse_table_data(soup, 'passing')
    
    if df2 is not None:
        print(f"✓ Successfully parsed table with {len(df2)} rows")
    else:
        print("✗ Failed to parse table with 'passing' ID")

if __name__ == "__main__":
    test_parse_table() 