#!/usr/bin/env python3
"""
Test PFR passing stats page with Selenium to verify JavaScript handling
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

def test_pfr_passing_stats():
    """Test PFR passing stats page with Selenium"""
    
    print("Testing PFR passing stats page with Selenium")
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
                
                # List all tables
                tables = soup.find_all('table')
                table_ids = [t.get('id', 'NO_ID') for t in tables]
                print(f"Available tables: {table_ids}")
                
                # Try alternative table IDs
                for table_id in ['stats', 'passing_stats', 'qb_stats']:
                    table = soup.find('table', {'id': table_id})
                    if table:
                        print(f"✅ Found table with id='{table_id}'")
                        break
                
                if not table:
                    print("❌ No suitable table found")
                    return False
            else:
                print("✅ Found table with id='passing'")
            
            # Check for table body
            tbody = table.find('tbody')
            if not tbody:
                print("❌ No table body found")
                return False
            
            # Count rows
            rows = tbody.find_all('tr')
            print(f"✅ Found {len(rows)} rows in table")
            
            # Check first few rows for QB data
            qb_count = 0
            for i, row in enumerate(rows[:10]):  # Check first 10 rows
                player_cell = row.find('td', {'data-stat': 'player'})
                pos_cell = row.find('td', {'data-stat': 'pos'})
                
                if player_cell and pos_cell:
                    player_name = player_cell.get_text(strip=True)
                    pos = pos_cell.get_text(strip=True)
                    
                    if pos.upper() == 'QB':
                        qb_count += 1
                        print(f"  QB {qb_count}: {player_name}")
                        
                        # Check for Joe Burrow specifically
                        if 'Burrow' in player_name:
                            print(f"  ✅ Found Joe Burrow!")
                            return True
            
            print(f"✅ Found {qb_count} QBs in first 10 rows")
            
            if qb_count == 0:
                print("❌ No QBs found in table")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_pfr_passing_stats()
    if success:
        print("\n🎉 PFR passing stats test PASSED!")
    else:
        print("\n❌ PFR passing stats test FAILED!") 