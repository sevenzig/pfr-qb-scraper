#!/usr/bin/env python3
"""
Debug script to examine the actual PFR splits page structure
"""

import sys
import os
import requests
from bs4 import BeautifulSoup

# Add the src directory to the Python path
sys.path.insert(0, 'src')

from utils.data_utils import build_splits_url

def debug_pfr_structure():
    """Debug the actual PFR splits page structure"""
    print("Debugging PFR splits page structure...")
    
    # Test with Joe Burrow's splits page
    pfr_id = "BurrJo00"
    season = 2024
    
    try:
        # Build the splits URL
        splits_url = build_splits_url(pfr_id, season)
        print(f"Splits URL: {splits_url}")
        
        # Make the request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(splits_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables on the page")
        
        for i, table in enumerate(tables):
            table_id = table.get('id', f'table_{i}')
            print(f"\nTable {i}: id='{table_id}'")
            
            # Check for tbody
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"  - Has tbody with {len(rows)} rows")
                
                # Look at the first few rows to understand structure
                for j, row in enumerate(rows[:5]):
                    ths = row.find_all('th')
                    tds = row.find_all('td')
                    
                    print(f"    Row {j}: {len(ths)} th, {len(tds)} td")
                    
                    # Check if this looks like a section header
                    if len(ths) == 1 and len(tds) > 10:
                        th_text = ths[0].get_text(strip=True)
                        print(f"      -> Potential section header: '{th_text}'")
                    
                    # Check first cell content
                    if tds:
                        first_cell = tds[0].get_text(strip=True)
                        if first_cell:
                            print(f"      -> First cell: '{first_cell}'")
            else:
                print(f"  - No tbody found")
        
        # Look for specific split categories
        print(f"\nLooking for specific split categories...")
        
        # Common split categories to look for
        expected_categories = [
            'Home', 'Away', 'Win', 'Loss', '1st Quarter', '2nd Quarter', 
            '3rd Quarter', '4th Quarter', 'Overtime', 'Leading', 'Tied', 'Trailing'
        ]
        
        for category in expected_categories:
            # Search for this category in any table
            found = False
            for table in tables:
                tbody = table.find('tbody')
                if tbody:
                    for row in tbody.find_all('tr'):
                        cells = row.find_all(['td', 'th'])
                        for cell in cells:
                            if category.lower() in cell.get_text(strip=True).lower():
                                print(f"  Found '{category}' in table")
                                found = True
                                break
                        if found:
                            break
                if found:
                    break
            
            if not found:
                print(f"  Category '{category}' not found")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pfr_structure() 