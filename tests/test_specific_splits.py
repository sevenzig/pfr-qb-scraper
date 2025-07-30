#!/usr/bin/env python3
"""
Test to specifically look for the splits tables by their content and structure.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import SeleniumManager
from datetime import datetime
from bs4 import BeautifulSoup

def test_specific_splits():
    """Test to specifically find the splits tables"""
    print("=== Testing Specific Splits Table Discovery ===")
    
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
        
        # Get page content with JavaScript
        result = selenium_manager.get_page(splits_url, enable_js=True)
        if not result['success']:
            print(f"Failed to load page: {result['error']}")
            return
        
        response = result['content']
        soup = BeautifulSoup(response, 'html.parser')
        
        print(f"\n=== Page Analysis ===")
        
        # Check page title
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text()}")
        
        # Look for splits-specific content
        page_text = soup.get_text().lower()
        if '2024 splits' in page_text:
            print("✓ '2024 Splits' found in page text")
        else:
            print("✗ '2024 Splits' NOT found in page text")
        
        if '2024 advanced splits' in page_text:
            print("✓ '2024 Advanced Splits' found in page text")
        else:
            print("✗ '2024 Advanced Splits' NOT found in page text")
        
        # Look for specific splits patterns
        splits_patterns = ['home', 'away', 'win', 'loss', 'quarter', '1st down', '2nd down', '3rd down', '4th down', 'red zone']
        found_patterns = [p for p in splits_patterns if p in page_text]
        print(f"Splits patterns found: {found_patterns}")
        
        print(f"\n=== Table Discovery Methods ===")
        
        # Method 1: Find all tables
        all_tables = soup.find_all('table')
        print(f"Method 1 - All tables: {len(all_tables)}")
        
        # Method 2: Look for tables with splits content
        splits_tables = []
        for i, table in enumerate(all_tables):
            table_text = table.get_text().lower()
            if any(pattern in table_text for pattern in ['home', 'away', 'win', 'loss', 'quarter', '1st down', '2nd down']):
                splits_tables.append((i+1, table))
                print(f"  Table {i+1} contains splits content")
        
        print(f"Method 2 - Tables with splits content: {len(splits_tables)}")
        
        # Method 3: Look for tables with specific headers
        header_tables = []
        for i, table in enumerate(all_tables):
            headers = splits_extractor._extract_table_headers(table)
            header_text = ' '.join(headers).lower()
            if any(header in header_text for header in ['split', 'value', 'passing', 'rushing']):
                header_tables.append((i+1, table, headers))
                print(f"  Table {i+1} has splits headers: {headers[:5]}...")
        
        print(f"Method 3 - Tables with splits headers: {len(header_tables)}")
        
        # Method 4: Look for tables by ID or class
        id_tables = []
        for i, table in enumerate(all_tables):
            table_id = table.get('id', '').lower()
            table_class = ' '.join(table.get('class', [])).lower()
            if 'split' in table_id or 'split' in table_class:
                id_tables.append((i+1, table, table_id, table_class))
                print(f"  Table {i+1} has splits ID/class: ID='{table_id}', Class='{table_class}'")
        
        print(f"Method 4 - Tables with splits ID/class: {len(id_tables)}")
        
        # Method 5: Look for tables in specific containers
        container_tables = []
        splits_containers = soup.find_all(['div', 'section'], string=lambda text: text and 'split' in text.lower())
        print(f"Found {len(splits_containers)} containers with 'split' in text")
        
        for container in splits_containers:
            container_tables.extend(container.find_all('table'))
            print(f"  Container '{container.get_text()[:50]}...' has {len(container.find_all('table'))} tables")
        
        print(f"Method 5 - Tables in splits containers: {len(container_tables)}")
        
        # Method 6: Look for tables with data-stat attributes (like the HTML you showed)
        data_stat_tables = []
        for i, table in enumerate(all_tables):
            cells_with_data_stat = table.find_all(['td', 'th'], attrs={'data-stat': True})
            if len(cells_with_data_stat) > 10:  # Tables with lots of data-stat attributes
                data_stats = [cell.get('data-stat') for cell in cells_with_data_stat[:10]]
                data_stat_tables.append((i+1, table, data_stats))
                print(f"  Table {i+1} has data-stat attributes: {data_stats}")
        
        print(f"Method 6 - Tables with data-stat attributes: {len(data_stat_tables)}")
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Total tables found: {len(all_tables)}")
        print(f"Tables with splits content: {len(splits_tables)}")
        print(f"Tables with splits headers: {len(header_tables)}")
        print(f"Tables with splits ID/class: {len(id_tables)}")
        print(f"Tables in splits containers: {len(container_tables)}")
        print(f"Tables with data-stat attributes: {len(data_stat_tables)}")
        
        # Show the best candidates
        if data_stat_tables:
            print(f"\n=== Best Candidates (Tables with data-stat attributes) ===")
            for i, table, data_stats in data_stat_tables:
                print(f"Table {i}: {data_stats}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_splits() 