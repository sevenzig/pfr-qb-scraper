#!/usr/bin/env python3
"""
Debug the splits URL to see what data we're actually getting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.selenium_manager import SeleniumManager
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_splits_url():
    """Debug the splits URL for Joe Burrow"""
    
    print("DEBUGGING SPLITS URL")
    print("=" * 60)
    
    # Initialize Selenium manager
    selenium_manager = SeleniumManager()
    
    try:
        # Build the splits URL
        pfr_id = "burrjo01"
        season = 2024
        splits_url = f"https://www.pro-football-reference.com/players/B/{pfr_id}/splits/{season}/"
        
        print(f"Splits URL: {splits_url}")
        
        # Get the page
        print("\n--- GETTING PAGE ---")
        selenium_manager.start_session()
        page_data = selenium_manager.get_page(splits_url, enable_js=True)
        soup = BeautifulSoup(page_data.get('html', ''), 'html.parser')
        
        if not soup:
            print("Failed to get page")
            return
        
        # Find all tables
        print("\n--- FINDING TABLES ---")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            table_id = table.get('id', 'NO_ID')
            table_class = table.get('class', [])
            print(f"Table {i+1}: ID='{table_id}', Class='{table_class}'")
            
            # Check if it has headers
            headers = table.find_all('th')
            if headers:
                header_texts = [h.get_text(strip=True) for h in headers[:5]]  # First 5 headers
                print(f"  Headers: {header_texts}")
            
            # Check if it has data rows
            rows = table.find_all('tr')
            data_rows = [r for r in rows if r.find_all('td')]
            print(f"  Data rows: {len(data_rows)}")
            
            if data_rows:
                # Show first few data rows
                for j, row in enumerate(data_rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [c.get_text(strip=True) for c in cells[:5]]  # First 5 cells
                    print(f"    Row {j+1}: {cell_texts}")
        
        # Look for specific splits tables
        print("\n--- LOOKING FOR SPECIFIC SPLITS ---")
        
        # Check for opponent splits
        opponent_tables = soup.find_all('table', id=lambda x: x and 'opponent' in x.lower())
        print(f"Opponent tables: {len(opponent_tables)}")
        
        # Check for quarter splits
        quarter_tables = soup.find_all('table', id=lambda x: x and 'quarter' in x.lower())
        print(f"Quarter tables: {len(quarter_tables)}")
        
        # Check for down and distance
        down_tables = soup.find_all('table', id=lambda x: x and 'down' in x.lower())
        print(f"Down tables: {len(down_tables)}")
        
        # Check for any table with splits data
        splits_tables = soup.find_all('table', id=lambda x: x and 'splits' in x.lower())
        print(f"Splits tables: {len(splits_tables)}")
        
        # Check the main content area
        print("\n--- MAIN CONTENT ---")
        main_content = soup.find('div', id='content')
        if main_content:
            print("Found main content area")
            # Look for any text that mentions splits
            splits_text = main_content.find_all(text=lambda text: text and 'split' in text.lower())
            print(f"Text mentioning splits: {len(splits_text)}")
            for text in splits_text[:5]:
                print(f"  {text.strip()}")
        
    except Exception as e:
        print(f"Error debugging splits URL: {e}")
        logger.error(f"Error debugging splits URL: {e}", exc_info=True)
    
    finally:
        selenium_manager.end_session()

if __name__ == "__main__":
    debug_splits_url() 