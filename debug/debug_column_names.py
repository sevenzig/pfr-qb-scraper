#!/usr/bin/env python3
"""
Debug script to check column names in the 2024 passing table
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

def debug_column_names():
    """Check the actual column names in the 2024 passing table"""
    print("Checking column names in 2024 passing table...")
    
    # Get the main stats page for the season
    stats_url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    response = requests.get(stats_url, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the passing table
    table = soup.find('table', {'id': 'passing'})
    if not table:
        print("Could not find passing table")
        return
    
    # Parse the table
    df = pd.read_html(str(table))[0]
    
    print(f"Found {len(df)} players in 2024 passing table")
    print(f"DataFrame columns: {list(df.columns)}")
    
    # Look for Joe Burrow and show his data
    print("\nLooking for Joe Burrow...")
    for i, row in df.iterrows():
        player_name = str(row.get('Player', ''))
        if 'burrow' in player_name.lower():
            print(f"  Found Joe Burrow at row {i}")
            print(f"  All columns for Joe Burrow:")
            for col in df.columns:
                value = row.get(col, 'N/A')
                print(f"    {col}: {value}")
            break

if __name__ == "__main__":
    debug_column_names() 