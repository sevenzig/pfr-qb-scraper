#!/usr/bin/env python3
"""
Test script to see what's in the 2024 passing table
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

def test_2024_passing():
    """Test the 2024 passing table"""
    print("Testing 2024 passing table...")
    
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
    
    # Look for Joe Burrow
    print("\nSearching for Joe Burrow...")
    found = False
    
    for i, row in df.iterrows():
        player_name = str(row.get('Player', ''))
        team = str(row.get('Tm', ''))
        
        if 'burrow' in player_name.lower():
            print(f"  Found: {player_name} ({team})")
            found = True
            
            # Show his stats
            print(f"    Games: {row.get('G', 'N/A')}")
            print(f"    Completions: {row.get('Cmp', 'N/A')}")
            print(f"    Attempts: {row.get('Att', 'N/A')}")
            print(f"    Yards: {row.get('Yds', 'N/A')}")
            print(f"    TDs: {row.get('TD', 'N/A')}")
            print(f"    INTs: {row.get('Int', 'N/A')}")
    
    if not found:
        print("  Joe Burrow not found")
        
        # Show all Cincinnati players
        print("\nAll Cincinnati players:")
        for i, row in df.iterrows():
            player_name = str(row.get('Player', ''))
            team = str(row.get('Tm', ''))
            if team == 'CIN':
                print(f"  {player_name} ({team})")
        
        # Show first 10 players to see format
        print("\nFirst 10 players:")
        for i, row in df.head(10).iterrows():
            player_name = str(row.get('Player', ''))
            team = str(row.get('Tm', ''))
            print(f"  {i+1}. {player_name} ({team})")

if __name__ == "__main__":
    test_2024_passing() 