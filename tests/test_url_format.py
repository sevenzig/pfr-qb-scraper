#!/usr/bin/env python3
"""
Test to check if the URL format works with a different player.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import SeleniumManager
from datetime import datetime
from bs4 import BeautifulSoup

def test_url_format():
    """Test URL format with different players"""
    print("=== Testing URL Format ===")
    
    # Initialize components
    selenium_manager = SeleniumManager()
    splits_extractor = SplitsExtractor(selenium_manager)
    
    # Test players who definitely played in 2024
    test_players = [
        ("mahompa01", "Patrick Mahomes", 2024),
        ("allenjo02", "Josh Allen", 2024),
        ("prescdak01", "Dak Prescott", 2024),
        ("burrowjo01", "Joe Burrow", 2023),  # Test 2023 for Joe Burrow
    ]
    
    for pfr_id, player_name, season in test_players:
        print(f"\n--- Testing {player_name} ({season}) ---")
        
        try:
            # Build splits URL
            splits_url = splits_extractor._build_enhanced_splits_url(pfr_id, season)
            print(f"URL: {splits_url}")
            
            # Get page content
            result = selenium_manager.get_page(splits_url, enable_js=True)
            if not result['success']:
                print(f"Failed to load page: {result['error']}")
                continue
            
            response = result['content']
            soup = BeautifulSoup(response, 'html.parser')
            
            # Check page title
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                print(f"Page title: {title_text}")
                
                if "500" in title_text or "error" in title_text.lower():
                    print("✗ Server error detected")
                    continue
                else:
                    print("✓ No server error")
            
            # Check for splits content
            page_text = soup.get_text().lower()
            if f'{season} splits' in page_text:
                print(f"✓ '{season} Splits' found in page text")
            else:
                print(f"✗ '{season} Splits' NOT found in page text")
            
            # Count tables
            tables = soup.find_all('table')
            print(f"Tables found: {len(tables)}")
            
            # Look for tables with data-stat attributes
            data_stat_tables = []
            for i, table in enumerate(tables):
                cells_with_data_stat = table.find_all(['td', 'th'], attrs={'data-stat': True})
                if len(cells_with_data_stat) > 5:
                    data_stats = [cell.get('data-stat') for cell in cells_with_data_stat[:5]]
                    data_stat_tables.append((i+1, data_stats))
            
            print(f"Tables with data-stat attributes: {len(data_stat_tables)}")
            if data_stat_tables:
                print("  Data-stat tables found:")
                for table_num, data_stats in data_stat_tables:
                    print(f"    Table {table_num}: {data_stats}")
            
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    test_url_format() 