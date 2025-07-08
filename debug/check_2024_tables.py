#!/usr/bin/env python3
"""
Check what tables are available for 2024 on PFR
"""

import requests
from bs4 import BeautifulSoup

def check_2024_tables():
    """Check what tables are available for 2024"""
    print("Checking 2024 tables on PFR...")
    
    # Get the main stats page for the season
    stats_url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    response = requests.get(stats_url, timeout=10)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on the page")
        
        for i, table in enumerate(tables):
            table_id = table.get('id', f'no_id_{i}')
            print(f"  Table {i+1}: {table_id}")
        
        # Check if there's a passing stats table
        passing_table = soup.find('table', {'id': 'stats_passing'})
        if passing_table:
            print("✓ Found stats_passing table")
        else:
            print("✗ No stats_passing table found")
            
        # Check page title
        title = soup.find('title')
        if title:
            print(f"Page title: {title.text}")
            
        # Check for any error messages
        error_divs = soup.find_all('div', class_='error')
        if error_divs:
            print("Error messages found:")
            for div in error_divs:
                print(f"  {div.text}")
    else:
        print(f"Failed to load page: {response.status_code}")
        print(f"Response text: {response.text[:500]}...")

if __name__ == "__main__":
    check_2024_tables() 