#!/usr/bin/env python3
"""
Debug script to examine PFR table structure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.core.working_selenium_manager import WorkingSeleniumManager
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_table_structure():
    """Debug the table structure from PFR"""
    
    print("Debugging PFR table structure")
    print("=" * 60)
    
    # PFR 2024 passing stats URL
    url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    
    try:
        # Use Selenium manager
        with WorkingSeleniumManager(headless=True, min_delay=7.0, max_delay=12.0) as manager:
            print(f"Navigating to: {url}")
            
            # Get the page
            response = manager.get(url)
            
            if not response:
                print("❌ Failed to load page")
                return False
            
            print(f"✅ Page loaded successfully ({len(response)} characters)")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response, 'html.parser')
            
            # Look for the passing stats table
            table = soup.find('table', {'id': 'passing'})
            if not table:
                print("❌ Could not find table with id='passing'")
                return False
            
            print("✅ Found table with id='passing'")
            
            # Check for table body
            tbody = table.find('tbody')
            if not tbody:
                print("❌ No table body found")
                return False
            
            # Count rows
            rows = tbody.find_all('tr')
            print(f"✅ Found {len(rows)} rows in table")
            
            # Examine first few rows in detail
            print("\nExamining first 5 rows:")
            print("-" * 40)
            
            for i, row in enumerate(rows[:5]):
                print(f"\nRow {i+1}:")
                
                # Get all cells
                cells = row.find_all(['td', 'th'])
                print(f"  Total cells: {len(cells)}")
                
                # Check each cell
                for j, cell in enumerate(cells[:10]):  # First 10 cells
                    cell_text = cell.get_text(strip=True)
                    data_stat = cell.get('data-stat', 'NO_DATA_STAT')
                    print(f"    Cell {j+1}: data-stat='{data_stat}' = '{cell_text}'")
                
                # Look for player links
                player_links = row.find_all('a')
                if player_links:
                    print(f"  Player links found: {len(player_links)}")
                    for link in player_links[:3]:  # First 3 links
                        link_text = link.get_text(strip=True)
                        href = link.get('href', 'NO_HREF')
                        print(f"    Link: '{link_text}' -> {href}")
                
                # Check for position data
                pos_cells = row.find_all('td', {'data-stat': 'pos'})
                if pos_cells:
                    for pos_cell in pos_cells:
                        pos_text = pos_cell.get_text(strip=True)
                        print(f"  Position: '{pos_text}'")
                else:
                    print("  No position cell found")
                
                print()
            
            # Check for any QB references in the entire table
            print("Searching for QB references in entire table:")
            print("-" * 40)
            
            qb_found = False
            for i, row in enumerate(rows):
                row_text = row.get_text()
                if 'QB' in row_text:
                    qb_found = True
                    print(f"Row {i+1} contains 'QB': {row_text[:100]}...")
                    
                    # Get the specific QB row details
                    cells = row.find_all(['td', 'th'])
                    for j, cell in enumerate(cells[:5]):  # First 5 cells
                        cell_text = cell.get_text(strip=True)
                        data_stat = cell.get('data-stat', 'NO_DATA_STAT')
                        print(f"  Cell {j+1}: data-stat='{data_stat}' = '{cell_text}'")
                    break
            
            if not qb_found:
                print("❌ No 'QB' references found in any row")
                
                # Check what positions are actually in the table
                print("\nChecking what positions are actually in the table:")
                positions = set()
                for row in rows:
                    pos_cells = row.find_all('td', {'data-stat': 'pos'})
                    for pos_cell in pos_cells:
                        pos_text = pos_cell.get_text(strip=True)
                        if pos_text:
                            positions.add(pos_text)
                
                print(f"Found positions: {sorted(positions)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = debug_table_structure()
    if success:
        print("\n🎉 Debug completed!")
    else:
        print("\n❌ Debug failed!") 