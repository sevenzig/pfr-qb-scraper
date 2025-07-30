#!/usr/bin/env python3
"""Debug HTML structure to understand table columns"""

import sys
sys.path.insert(0, 'src')

from core.selenium_manager import SeleniumManager
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_html_structure():
    """Debug the actual HTML structure of splits tables"""
    
    try:
        selenium_manager = SeleniumManager()
        test_url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
        
        print(f"Fetching: {test_url}")
        result = selenium_manager.get_page(test_url)
        
        if result['success']:
            soup = BeautifulSoup(result['content'], 'html.parser')
            
            # Analyze basic splits table
            print("\n=== BASIC SPLITS TABLE ANALYSIS ===")
            basic_div = soup.find('div', id='div_stats')
            if basic_div:
                basic_table = basic_div.find('table', id='stats')
                if basic_table:
                    # Find header row
                    header_row = basic_table.find('tr')
                    if header_row:
                        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                        print(f"Headers ({len(headers)}): {headers}")
                    
                    # Analyze first few data rows
                    tbody = basic_table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')[:5]  # First 5 rows
                        for i, row in enumerate(rows):
                            cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                            print(f"Row {i+1} ({len(cells)} cells): {cells}")
                            
                            # Show data-stat attributes
                            data_stats = [cell.get('data-stat', 'no-data-stat') for cell in row.find_all(['td', 'th'])]
                            print(f"  data-stat: {data_stats}")
            
            # Analyze advanced splits table  
            print("\n=== ADVANCED SPLITS TABLE ANALYSIS ===")
            advanced_div = soup.find('div', id='div_advanced_splits')
            if advanced_div:
                advanced_table = advanced_div.find('table', id='advanced_splits')
                if advanced_table:
                    # Find header row
                    header_row = advanced_table.find('tr')
                    if header_row:
                        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                        print(f"Headers ({len(headers)}): {headers}")
                    
                    # Analyze first few data rows
                    tbody = advanced_table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')[:5]  # First 5 rows
                        for i, row in enumerate(rows):
                            cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                            print(f"Row {i+1} ({len(cells)} cells): {cells}")
                            
                            # Show data-stat attributes
                            data_stats = [cell.get('data-stat', 'no-data-stat') for cell in row.find_all(['td', 'th'])]
                            print(f"  data-stat: {data_stats}")
        else:
            print(f"Failed to fetch page: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Debug failed: {e}")
    
    finally:
        if 'selenium_manager' in locals():
            selenium_manager.end_session()

if __name__ == "__main__":
    debug_html_structure()