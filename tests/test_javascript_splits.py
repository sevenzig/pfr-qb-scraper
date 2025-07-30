#!/usr/bin/env python3
"""
Test to check if splits tables are loaded via JavaScript.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import SeleniumManager
from datetime import datetime
from bs4 import BeautifulSoup

def test_javascript_splits():
    """Test if splits tables are loaded via JavaScript"""
    print("=== Testing JavaScript Splits Loading ===")
    
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
        
        # Test 1: Get page WITHOUT JavaScript
        print("\n--- Test 1: WITHOUT JavaScript ---")
        result_no_js = selenium_manager.get_page(splits_url, enable_js=False)
        if result_no_js['success']:
            soup_no_js = BeautifulSoup(result_no_js['content'], 'html.parser')
            tables_no_js = soup_no_js.find_all('table')
            print(f"Tables found WITHOUT JavaScript: {len(tables_no_js)}")
            
            # Look for splits-related content
            page_text_no_js = soup_no_js.get_text().lower()
            if 'splits' in page_text_no_js:
                print("✓ 'splits' found in page text")
            else:
                print("✗ 'splits' NOT found in page text")
        
        # Test 2: Get page WITH JavaScript
        print("\n--- Test 2: WITH JavaScript ---")
        result_with_js = selenium_manager.get_page(splits_url, enable_js=True)
        if result_with_js['success']:
            soup_with_js = BeautifulSoup(result_with_js['content'], 'html.parser')
            tables_with_js = soup_with_js.find_all('table')
            print(f"Tables found WITH JavaScript: {len(tables_with_js)}")
            
            # Look for splits-related content
            page_text_with_js = soup_with_js.get_text().lower()
            if 'splits' in page_text_with_js:
                print("✓ 'splits' found in page text")
            else:
                print("✗ 'splits' NOT found in page text")
            
            # Look for specific splits patterns
            splits_patterns = ['home', 'away', 'win', 'loss', 'quarter', '1st down', '2nd down', '3rd down', '4th down']
            found_patterns = [p for p in splits_patterns if p in page_text_with_js]
            print(f"Splits patterns found: {found_patterns}")
            
            # Check if we have the right tables now
            if len(tables_with_js) != len(tables_no_js):
                print(f"✓ JavaScript changed table count: {len(tables_no_js)} → {len(tables_with_js)}")
            else:
                print(f"✗ JavaScript did not change table count: {len(tables_no_js)} → {len(tables_with_js)}")
        
        # Test 3: Check if we're on the right page
        print("\n--- Test 3: Page Validation ---")
        if result_with_js['success']:
            soup = BeautifulSoup(result_with_js['content'], 'html.parser')
            
            # Check page title
            title = soup.find('title')
            if title:
                print(f"Page title: {title.get_text()}")
            
            # Check for player name
            if 'joe burrow' in soup.get_text().lower():
                print("✓ Player name found on page")
            else:
                print("✗ Player name NOT found on page")
            
            # Check for season
            if '2024' in soup.get_text():
                print("✓ Season found on page")
            else:
                print("✗ Season NOT found on page")
            
            # Look for splits section
            splits_sections = soup.find_all(['div', 'section'], string=lambda text: text and 'splits' in text.lower())
            if splits_sections:
                print(f"✓ Found {len(splits_sections)} splits sections")
                for section in splits_sections:
                    print(f"  - {section.get_text()[:100]}...")
            else:
                print("✗ No splits sections found")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_javascript_splits() 