#!/usr/bin/env python3
"""
Debug script to test name matching
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.data_utils import clean_player_name

def debug_name_matching():
    """Debug the name matching issue"""
    print("Debugging name matching...")
    
    # Test the clean_player_name function
    test_names = [
        "Joe Burrow",
        "Joseph Burrow", 
        "Burrow, Joe",
        "Joe Burrow*",
        "Joe Burrow+"
    ]
    
    print("Testing clean_player_name function:")
    for name in test_names:
        cleaned = clean_player_name(name)
        print(f"  '{name}' -> '{cleaned}'")
    
    # Now let's check what's actually in the table
    import requests
    import pandas as pd
    from bs4 import BeautifulSoup
    
    stats_url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    response = requests.get(stats_url, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'passing'})
    df = pd.read_html(str(table))[0]
    
    print(f"\nLooking for Joe Burrow in the table...")
    for i, row in df.iterrows():
        player_name = str(row.get('Player', ''))
        if 'burrow' in player_name.lower():
            print(f"  Raw name in table: '{player_name}'")
            cleaned_name = clean_player_name(player_name)
            print(f"  Cleaned name: '{cleaned_name}'")
            print(f"  Expected cleaned: '{clean_player_name('Joe Burrow')}'")
            print(f"  Match: {cleaned_name == clean_player_name('Joe Burrow')}")

if __name__ == "__main__":
    debug_name_matching() 