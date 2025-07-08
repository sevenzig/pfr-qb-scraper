#!/usr/bin/env python3
"""
Examine the passing_advanced table structure on Joe Burrow's page
"""

import sys
sys.path.append('src')

import requests
from bs4 import BeautifulSoup
from scrapers.enhanced_scraper import EnhancedPFRScraper

def main():
    """Examine the passing_advanced table structure"""
    print("Examining passing_advanced table on Joe Burrow's page...")
    
    scraper = EnhancedPFRScraper(rate_limit_delay=1.0)
    player_url = "https://www.pro-football-reference.com/players/B/BurrJo01.htm"
    
    response = scraper.make_request_with_retry(player_url)
    if not response:
        print("❌ Failed to fetch Joe Burrow's page")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the passing_advanced table
    table = soup.find('table', {'id': 'passing_advanced'})
    if not table:
        print("❌ Could not find passing_advanced table")
        return
    
    print("✅ Found passing_advanced table")
    
    # Examine the table structure
    print("\n🔍 Table structure analysis:")
    
    # Look at headers
    thead = table.find('thead')
    if thead:
        header_rows = thead.find_all('tr')
        print(f"  Header rows: {len(header_rows)}")
        
        for i, row in enumerate(header_rows):
            headers = row.find_all(['th', 'td'])
            print(f"    Row {i+1} headers:")
            for j, header in enumerate(headers):
                header_text = header.get_text(strip=True)
                data_stat = header.get('data-stat', 'no-data-stat')
                print(f"      {j+1}. '{header_text}' (data-stat: '{data_stat}')")
    
    # Look at the first few data rows
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
        print(f"\n📊 Data rows: {len(rows)}")
        
        for i, row in enumerate(rows[:3]):  # First 3 rows
            print(f"\n  Row {i+1}:")
            cells = row.find_all(['td', 'th'])
            
            for j, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                data_stat = cell.get('data-stat', 'no-data-stat')
                print(f"    {j+1}. '{cell_text}' (data-stat: '{data_stat}')")
    
    # Also check the regular passing table for comparison
    print("\n🔍 Comparing with regular passing table:")
    passing_table = soup.find('table', {'id': 'passing'})
    if passing_table:
        tbody = passing_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            if rows:
                first_row = rows[0]
                cells = first_row.find_all(['td', 'th'])
                print(f"  Regular passing table first row has {len(cells)} cells")
                print("  First few cells:")
                for j, cell in enumerate(cells[:5]):
                    cell_text = cell.get_text(strip=True)
                    data_stat = cell.get('data-stat', 'no-data-stat')
                    print(f"    {j+1}. '{cell_text}' (data-stat: '{data_stat}')")

if __name__ == "__main__":
    main() 