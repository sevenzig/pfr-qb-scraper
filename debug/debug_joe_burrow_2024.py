#!/usr/bin/env python3
"""
Debug script to find Joe Burrow in 2024 stats
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

def debug_joe_burrow_2024():
    """Debug Joe Burrow in 2024 stats"""
    print("Debugging Joe Burrow in 2024 stats...")
    
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
    
    # Look for Joe Burrow specifically
    print("\nSearching for Joe Burrow...")
    found = False
    
    for i, row in df.iterrows():
        player_name = str(row.get('Player', ''))
        team = str(row.get('Tm', ''))
        
        # Check various ways Joe Burrow might be listed
        if ('burrow' in player_name.lower() or 
            'joe' in player_name.lower() or
            player_name == 'Joe Burrow' or
            player_name == 'Joseph Burrow'):
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
        print("  Joe Burrow not found in 2024 stats")
        
        # Show all Cincinnati players
        print("\nAll Cincinnati players in 2024:")
        for i, row in df.iterrows():
            player_name = str(row.get('Player', ''))
            team = str(row.get('Tm', ''))
            if team == 'CIN':
                print(f"  {player_name} ({team})")
        
        # Show first 20 players to see the format
        print("\nFirst 20 players (to check format):")
        for i, row in df.head(20).iterrows():
            player_name = str(row.get('Player', ''))
            team = str(row.get('Tm', ''))
            print(f"  {i+1}. {player_name} ({team})")

if __name__ == "__main__":
    debug_joe_burrow_2024() 