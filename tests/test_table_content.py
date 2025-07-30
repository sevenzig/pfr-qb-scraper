#!/usr/bin/env python3
"""
Test to examine the actual content of each table to understand classification.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import SeleniumManager
from datetime import datetime
from bs4 import BeautifulSoup

def test_table_content():
    """Examine the content of each table to understand classification"""
    print("=== Testing Table Content Analysis ===")
    
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
        soup = BeautifulSoup(response, 'html.parser')
        
        # Find all tables
        all_tables = soup.find_all('table')
        print(f"\nTotal tables found: {len(all_tables)}")
        
        # Analyze each table
        for i, table in enumerate(all_tables):
            print(f"\n=== Table {i+1} Analysis ===")
            
            # Get table info
            table_id = table.get('id', 'NO_ID')
            table_class = ' '.join(table.get('class', []))
            print(f"ID: '{table_id}', Class: '{table_class}'")
            
            # Extract headers
            headers = splits_extractor._extract_table_headers(table)
            print(f"Headers: {headers}")
            
            # Get table text (first 200 chars)
            table_text = table.get_text()[:200]
            print(f"Text preview: {table_text}...")
            
            # Test categorization
            categorization = splits_extractor._categorize_table(table)
            if categorization:
                print(f"Classification: {categorization['type']} (Priority: {categorization['priority']})")
            else:
                print(f"Classification: NOT CATEGORIZED")
            
            # Test specific indicators
            has_basic = splits_extractor._has_basic_splits_indicators(table)
            has_advanced = splits_extractor._has_advanced_splits_indicators(table)
            print(f"Has basic indicators: {has_basic}")
            print(f"Has advanced indicators: {has_advanced}")
            
            # Look for specific patterns
            table_text_lower = table.get_text().lower()
            
            # Basic patterns
            basic_patterns = ['home', 'away', 'win', 'loss', 'tie', 'quarter', 'overtime', 'league', 'place', 'result', 'month', 'day', 'time', 'conference', 'division', 'opponent', 'stadium']
            basic_found = [p for p in basic_patterns if p in table_text_lower]
            print(f"Basic patterns found: {basic_found}")
            
            # Advanced patterns
            advanced_patterns = ['1st down', '2nd down', '3rd down', '4th down', 'yards to go', 'field position', 'score differential', 'snap type', 'play action', 'time in pocket', 'leading', 'trailing', 'tied']
            advanced_found = [p for p in advanced_patterns if p in table_text_lower]
            print(f"Advanced patterns found: {advanced_found}")
            
            print("-" * 50)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_table_content() 