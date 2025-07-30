#!/usr/bin/env python3
"""
Diagnose PFR Structure
Quick diagnostic script to examine the actual HTML structure of Joe Burrow's PFR page.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.selenium_manager import SeleniumManager, SeleniumConfig
from src.utils.data_utils import build_splits_url

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def diagnose_pfr_structure():
    """Diagnose the actual PFR structure"""
    print("=" * 80)
    print("PFR STRUCTURE DIAGNOSIS - JOE BURROW 2024")
    print("=" * 80)
    
    try:
        # Create Selenium manager
        selenium_config = SeleniumConfig(
            min_delay=3.0,
            max_delay=5.0,
            headless=True,
            enable_soft_block_detection=True
        )
        selenium_manager = SeleniumManager(selenium_config)
        
        # Get Joe Burrow's splits page
        splits_url = build_splits_url("burrjo01", 2024)
        print(f"Loading: {splits_url}")
        
        html_content = selenium_manager.get(splits_url)
        if not html_content:
            print("❌ Failed to load page")
            return False
        
        print(f"✅ Page loaded successfully ({len(html_content)} characters)")
        
        # Parse HTML and examine structure
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\n--- TABLE {i+1} ---")
            
            # Get table info
            table_id = table.get('id', 'NO_ID')
            table_class = ' '.join(table.get('class', []))
            print(f"ID: {table_id}")
            print(f"Class: {table_class}")
            
            # Find headers
            headers = []
            thead = table.find('thead')
            if thead:
                header_rows = thead.find_all('tr')
                for row in header_rows:
                    cells = row.find_all(['th', 'td'])
                    for cell in cells:
                        header_text = cell.get_text(strip=True)
                        if header_text:
                            headers.append(header_text)
            
            print(f"Headers: {headers[:10]}...")  # First 10 headers
            
            # Find data-stat attributes
            data_stats = []
            cells = table.find_all(['td', 'th'])
            for cell in cells:
                data_stat = cell.get('data-stat')
                if data_stat and data_stat not in data_stats:
                    data_stats.append(data_stat)
            
            print(f"Data-stats: {data_stats[:10]}...")  # First 10 data-stats
            
            # Find first few rows of data
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')[:3]  # First 3 rows
                print(f"Sample data (first 3 rows):")
                
                for j, row in enumerate(rows):
                    print(f"  Row {j+1}:")
                    cells = row.find_all(['td', 'th'])
                    for k, cell in enumerate(cells):
                        data_stat = cell.get('data-stat')
                        cell_text = cell.get_text(strip=True)
                        if cell_text:
                            print(f"    Cell {k+1} ({data_stat}): {cell_text}")
        
        # Look for specific patterns
        print(f"\n--- SEARCHING FOR SPECIFIC PATTERNS ---")
        
        # Look for "League" split
        league_cells = soup.find_all(text=lambda text: text and 'League' in text)
        print(f"Found {len(league_cells)} cells containing 'League'")
        
        # Look for completion/attempt data
        completion_cells = soup.find_all(attrs={'data-stat': 'cmp'})
        print(f"Found {len(completion_cells)} cells with data-stat='cmp'")
        if completion_cells:
            print(f"First completion cell: {completion_cells[0].get_text(strip=True)}")
        
        attempt_cells = soup.find_all(attrs={'data-stat': 'att'})
        print(f"Found {len(attempt_cells)} cells with data-stat='att'")
        if attempt_cells:
            print(f"First attempt cell: {attempt_cells[0].get_text(strip=True)}")
        
        # Look for any cells with numbers
        import re
        number_cells = soup.find_all(text=re.compile(r'\d+'))
        print(f"Found {len(number_cells)} cells containing numbers")
        if number_cells:
            print(f"Sample number cells: {number_cells[:5]}")
        
        # Clean up
        selenium_manager.end_session()
        
        return True
        
    except Exception as e:
        print(f"Error during diagnosis: {e}")
        logger.exception("Diagnosis failed")
        return False

def main():
    """Main function"""
    print("Starting PFR Structure Diagnosis...")
    success = diagnose_pfr_structure()
    
    if success:
        print("\n✅ Diagnosis completed successfully!")
    else:
        print("\n❌ Diagnosis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 