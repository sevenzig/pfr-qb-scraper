#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.core.working_selenium_manager import WorkingSeleniumManager
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_data_stats():
    """Debug the data-stat attributes in the PFR table"""
    
    print("Debugging PFR data-stat attributes")
    print("=" * 60)
    
    # PFR 2024 passing stats URL
    url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    
    try:
        # Use Selenium manager
        with WorkingSeleniumManager(headless=True, min_delay=7.0, max_delay=12.0) as manager:
            response = manager.get(url)
            
            if not response:
                print("❌ Failed to load page")
                return
            
            print(f"✅ Page loaded successfully ({len(response)} characters)")
            
            soup = BeautifulSoup(response, 'html.parser')
            
            # Find the main passing stats table
            table = soup.find('table', {'id': 'passing'})
            if not table:
                print("❌ Could not find passing table")
                return
            
            print("✅ Found passing table")
            
            # Get the header row to see all data-stat attributes
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    data_stats = []
                    for cell in header_row.find_all(['th', 'td']):
                        data_stat = cell.get('data-stat')
                        if data_stat:
                            data_stats.append(data_stat)
                    
                    print(f"\nFound {len(data_stats)} data-stat attributes:")
                    for i, stat in enumerate(data_stats, 1):
                        print(f"  {i:2d}. {stat}")
            
            # Check Joe Burrow's row specifically
            tbody = table.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    player_cell = row.find('td', {'data-stat': 'name_display'})
                    if player_cell:
                        player_name = player_cell.get_text(strip=True)
                        if 'Burrow' in player_name:
                            print(f"\nJoe Burrow row data-stat values:")
                            for cell in row.find_all('td'):
                                data_stat = cell.get('data-stat')
                                value = cell.get_text(strip=True)
                                if data_stat and value:
                                    print(f"  {data_stat}: {value}")
                            break
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_data_stats() 