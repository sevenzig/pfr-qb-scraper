#!/usr/bin/env python3
"""
Debug script to examine PFR splits table structure
"""

import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.splits_extractor import SplitsExtractor
from core.selenium_manager import SeleniumManager
from config.config import config
from bs4 import BeautifulSoup, Tag

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def debug_splits_tables():
    """Debug splits table structure for Joe Burrow"""
    
    # Initialize components
    selenium_manager = SeleniumManager(config)
    splits_extractor = SplitsExtractor(selenium_manager)
    
    # Test with Joe Burrow 2024
    pfr_id = "BurrJo00"
    player_name = "Joe Burrow"
    season = 2024
    
    try:
        # Build URL
        splits_url = splits_extractor._build_enhanced_splits_url(pfr_id, season)
        print(f"🔗 Splits URL: {splits_url}")
        
        # Fetch page
        page_source = selenium_manager.get(splits_url)
        if not page_source:
            print("❌ Failed to fetch page")
            return
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"\n📊 Found {len(tables)} total tables")
        
        for i, table in enumerate(tables):
            table_id = table.get('id', f'no_id_{i}')
            table_class = ' '.join(table.get('class', []))
            
            print(f"\n🔍 Table {i+1}: ID='{table_id}', Class='{table_class}'")
            
            # Extract headers
            headers = splits_extractor._extract_table_headers(table)
            print(f"   📋 Headers ({len(headers)}): {headers}")
            
            # Check categorization
            table_info = splits_extractor._categorize_table(table)
            if table_info:
                print(f"   ✅ Categorized as: {table_info['type']} (by {table_info['category']})")
            else:
                print(f"   ❌ Not categorized as splits table")
            
            # Check for advanced indicators
            has_advanced = splits_extractor._has_advanced_splits_indicators(table)
            print(f"   🔬 Has advanced indicators: {has_advanced}")
            
            # Show first few rows
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')[:3]  # First 3 rows
                print(f"   📝 First {len(rows)} data rows:")
                for j, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True)[:20] for cell in cells[:5]]  # First 5 cells, truncated
                    print(f"      Row {j+1}: {cell_texts}")
        
        print(f"\n🎯 Summary:")
        discovered_tables = splits_extractor._discover_splits_tables(soup)
        for table_info in discovered_tables:
            print(f"   - {table_info['id']}: {table_info['type']} ({table_info['category']})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        selenium_manager.end_session()

if __name__ == "__main__":
    debug_splits_tables() 