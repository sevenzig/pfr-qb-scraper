#!/usr/bin/env python3
"""
Debug script to examine what tables are available on Joe Burrow's page
"""

import sys
sys.path.append('src')

import requests
from bs4 import BeautifulSoup
import re
from scrapers.enhanced_scraper import EnhancedPFRScraper

def main():
    """Debug splits scraping by examining Joe Burrow's page"""
    print("Debugging splits scraping for Joe Burrow...")
    
    scraper = EnhancedPFRScraper(rate_limit_delay=1.0)
    player_url = "https://www.pro-football-reference.com/players/B/BurrJo01.htm"
    
    print(f"Fetching Joe Burrow's page: {player_url}")
    
    response = scraper.make_request_with_retry(player_url)
    if not response:
        print("❌ Failed to fetch Joe Burrow's page")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables
    all_tables = soup.find_all('table')
    print(f"\n📊 Found {len(all_tables)} total tables on Joe Burrow's page")
    
    # List all table IDs
    print("\n🔍 All table IDs found:")
    for i, table in enumerate(all_tables):
        table_id = table.get('id', f'no-id-{i}')
        table_class = table.get('class', [])
        print(f"  {i+1}. ID: '{table_id}' | Classes: {table_class}")
    
    # Look for splits-related tables with different patterns
    print("\n🎯 Looking for splits tables with different patterns:")
    
    patterns = [
        r'splits.*',
        r'.*splits.*',
        r'passing.*splits.*',
        r'game.*splits.*',
        r'situational.*',
        r'advanced.*',
        r'home.*away.*',
        r'quarter.*',
        r'red.*zone.*'
    ]
    
    for pattern in patterns:
        matches = soup.find_all('table', {'id': re.compile(pattern, re.IGNORECASE)})
        if matches:
            print(f"  ✅ Pattern '{pattern}' found {len(matches)} tables:")
            for match in matches:
                print(f"    - ID: '{match.get('id', 'no-id')}'")
    
    # Look for tables with specific data-stat attributes that indicate splits
    print("\n🔍 Looking for tables with splits-related data-stat attributes:")
    
    splits_tables = []
    for table in all_tables:
        # Check if table has rows with split_value data-stat
        rows = table.find_all('tr')
        for row in rows:
            split_cell = row.find('td', {'data-stat': 'split_value'})
            if split_cell:
                table_id = table.get('id', 'unknown')
                print(f"  ✅ Found table '{table_id}' with split_value cells")
                splits_tables.append(table)
                break
    
    print(f"\n📈 Total splits tables found: {len(splits_tables)}")
    
    # Examine the first few splits tables in detail
    for i, table in enumerate(splits_tables[:3]):
        print(f"\n🔍 Examining splits table {i+1}:")
        table_id = table.get('id', 'unknown')
        print(f"  Table ID: {table_id}")
        
        # Look at the first few rows
        rows = table.find_all('tr')
        print(f"  Total rows: {len(rows)}")
        
        for j, row in enumerate(rows[:5]):  # First 5 rows
            split_cell = row.find('td', {'data-stat': 'split_value'})
            if split_cell:
                split_value = split_cell.get_text(strip=True)
                print(f"    Row {j+1}: split_value = '{split_value}'")
            
            # Check for other data-stat attributes
            data_stats = row.find_all('td')
            if data_stats:
                stats_found = []
                for cell in data_stats:
                    stat_name = cell.get('data-stat', '')
                    if stat_name:
                        stats_found.append(stat_name)
                if stats_found:
                    print(f"    Row {j+1} data-stats: {stats_found[:5]}...")  # First 5

if __name__ == "__main__":
    main() 