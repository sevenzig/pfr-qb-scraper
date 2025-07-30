#!/usr/bin/env python3
"""
Test to debug table discovery and see what tables are being found.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import SeleniumManager
from datetime import datetime

def test_table_discovery():
    """Test table discovery for Joe Burrow to see what's happening"""
    print("=== Testing Table Discovery ===")
    
    # Initialize components
    selenium_manager = SeleniumManager()
    splits_extractor = SplitsExtractor(selenium_manager)
    
    try:
        # Build splits URL
        pfr_id = "burrowjo01"
        player_name = "Joe Burrow"
        season = 2024
        scraped_at = datetime.now()
        
        splits_url = splits_extractor._build_enhanced_splits_url(pfr_id, season)
        print(f"URL: {splits_url}")
        
        # Get page content
        result = selenium_manager.get_page(splits_url, enable_js=False)
        if not result['success']:
            print(f"Failed to load page: {result['error']}")
            return
        
        response = result['content']
        
        # Parse HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response, 'html.parser')
        
        # Find all tables
        all_tables = soup.find_all('table')
        print(f"\nTotal tables found: {len(all_tables)}")
        
        # Print all table IDs and classes
        for i, table in enumerate(all_tables):
            table_id = table.get('id', 'NO_ID')
            table_class = ' '.join(table.get('class', []))
            print(f"Table {i+1}: ID='{table_id}', Class='{table_class}'")
        
        # Test table discovery
        discovered_tables = splits_extractor._discover_splits_tables(soup)
        print(f"\nDiscovered splits tables: {len(discovered_tables)}")
        
        for table_info in discovered_tables:
            print(f"  - {table_info['id']} ({table_info['type']}) - Priority: {table_info['priority']}")
        
        # Test categorization on each table
        print(f"\n=== Testing categorization on each table ===")
        for i, table in enumerate(all_tables):
            table_id = table.get('id', 'NO_ID')
            categorization = splits_extractor._categorize_table(table)
            if categorization:
                print(f"Table {i+1} ({table_id}): {categorization['type']} (Priority: {categorization['priority']})")
            else:
                print(f"Table {i+1} ({table_id}): NOT CATEGORIZED")
        
        # Test priority table selection
        priority_tables = splits_extractor._get_priority_tables(discovered_tables)
        print(f"\nPriority tables selected: {len(priority_tables)}")
        for table_info in priority_tables:
            print(f"  - {table_info['id']} ({table_info['type']})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_table_discovery() 