#!/usr/bin/env python3
"""
Debug script to check what's in the 2024 passing stats table
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

def check_2024_stats():
    """Check what's in the 2024 passing stats table"""
    print("Checking 2024 passing stats table...")
    
    # Get the main stats page for the season
    stats_url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    response = requests.get(stats_url, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the stats table
    table = soup.find('table', {'id': 'stats_passing'})
    if not table:
        print("Could not find passing stats table")
        return
    
    # Parse the table
    df = pd.read_html(str(table))[0]
    
    print(f"Found {len(df)} players in 2024 passing stats")
    print("\nFirst 10 players:")
    for i, row in df.head(10).iterrows():
        player_name = row.get('Player', 'Unknown')
        team = row.get('Tm', 'Unknown')
        print(f"  {i+1}. {player_name} ({team})")
    
    print("\nLooking for Joe Burrow...")
    # Search for Joe Burrow or variations
    for i, row in df.iterrows():
        player_name = row.get('Player', '')
        if 'burrow' in player_name.lower() or 'joe' in player_name.lower():
            team = row.get('Tm', 'Unknown')
            print(f"  Found: {player_name} ({team})")
    
    print("\nLooking for Cincinnati QBs...")
    # Search for Cincinnati QBs
    for i, row in df.iterrows():
        player_name = row.get('Player', '')
        team = row.get('Tm', '')
        if team == 'CIN':
            print(f"  {player_name} ({team})")

if __name__ == "__main__":
    check_2024_stats() 