#!/usr/bin/env python3
"""
Debug script to examine Joe Burrow's splits page structure
"""

import sys
sys.path.append('src')

import requests
from bs4 import BeautifulSoup
from scrapers.enhanced_scraper import EnhancedPFRScraper

def main():
    """Debug Joe Burrow's splits page structure"""
    print("Debugging Joe Burrow's splits page structure...")
    
    scraper = EnhancedPFRScraper(rate_limit_delay=1.0)
    splits_url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
    
    print(f"Fetching splits page: {splits_url}")
    
    response = scraper.make_request_with_retry(splits_url)
    if not response:
        print("❌ Failed to fetch splits page")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables
    all_tables = soup.find_all('table')
    print(f"\n📊 Found {len(all_tables)} total tables")
    
    # List all table IDs
    print("\n🔍 All table IDs found:")
    for i, table in enumerate(all_tables):
        table_id = table.get('id', f'no-id-{i}')
        print(f"  {i+1}. ID: '{table_id}'")
    
    # Examine the first table in detail
    if all_tables:
        print(f"\n🔍 Examining first table (ID: '{all_tables[0].get('id', 'no-id')}'):")
        
        # Look at headers
        thead = all_tables[0].find('thead')
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
        tbody = all_tables[0].find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"\n📊 Data rows: {len(rows)}")
            
            for i, row in enumerate(rows[:5]):  # First 5 rows
                print(f"\n  Row {i+1}:")
                cells = row.find_all(['td', 'th'])
                
                for j, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    data_stat = cell.get('data-stat', 'no-data-stat')
                    print(f"    {j+1}. '{cell_text}' (data-stat: '{data_stat}')")
    
    # Also check if there are any divs with splits data
    print("\n🔍 Looking for splits data in divs:")
    splits_divs = soup.find_all('div', {'id': lambda x: x and 'splits' in x.lower()})
    print(f"  Found {len(splits_divs)} divs with 'splits' in ID")
    
    for div in splits_divs:
        print(f"    - ID: '{div.get('id', 'no-id')}'")
    
    # Look for any elements with splits-related content
    print("\n🔍 Looking for splits-related content:")
    splits_elements = soup.find_all(text=lambda text: text and 'Split' in text)
    print(f"  Found {len(splits_elements)} elements containing 'Split'")
    
    for i, element in enumerate(splits_elements[:10]):  # First 10
        print(f"    {i+1}. '{element.strip()}'")

if __name__ == "__main__":
    main() 