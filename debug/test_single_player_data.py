#!/usr/bin/env python3
"""Debug script to test single player data extraction"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests
from bs4 import BeautifulSoup
from scrapers.enhanced_scraper import EnhancedPFRScraper
from utils.data_utils import safe_int, safe_float, normalize_pfr_team_code
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_joe_burrow_page():
    """Test scraping Joe Burrow's 2024 stats directly"""
    
    # Joe Burrow's splits page
    url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
    
    print("=== Testing Joe Burrow 2024 Data Extraction ===")
    print(f"URL: {url}")
    
    try:
        # Test direct request
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check what tables exist
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables on page")
        
        for i, table in enumerate(tables):
            table_id = table.get('id', f'table_{i}')
            rows = table.find_all('tr')
            print(f"  Table {i}: ID='{table_id}', Rows={len(rows)}")
            
            # Look for stats in first few rows
            if len(rows) > 1:
                for j, row in enumerate(rows[:3]):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_texts = [cell.get_text(strip=True) for cell in cells[:5]]
                        print(f"    Row {j}: {cell_texts}")
        
        # Test enhanced scraper
        print("\n=== Testing Enhanced Scraper ===")
        scraper = EnhancedPFRScraper(rate_limit_delay=1.0)
        
        # Test basic stats extraction for Joe Burrow
        basic_stats = scraper.get_qb_main_stats(2024)
        
        joe_burrow_stats = None
        for stat in basic_stats[1]:  # QBBasicStats is second element
            if 'Burrow' in stat.player_name:
                joe_burrow_stats = stat
                break
        
        if joe_burrow_stats:
            print("Joe Burrow basic stats found:")
            print(f"  Name: {joe_burrow_stats.player_name}")
            print(f"  Team: {joe_burrow_stats.team}")
            print(f"  Completions: {joe_burrow_stats.cmp}")
            print(f"  Attempts: {joe_burrow_stats.att}")
            print(f"  Yards: {joe_burrow_stats.yds}")
            print(f"  TDs: {joe_burrow_stats.td}")
            print(f"  Rating: {joe_burrow_stats.rate}")
        else:
            print("Joe Burrow not found in basic stats!")
            print("Available players:")
            for stat in basic_stats[1][:5]:
                print(f"  - {stat.player_name} ({stat.team})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_2024_passing_table():
    """Test the main 2024 passing stats table"""
    url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    
    print("\n=== Testing 2024 Passing Stats Table ===")
    print(f"URL: {url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for the passing table
        passing_table = soup.find('table', {'id': 'passing'})
        if not passing_table:
            print("No passing table found!")
            tables = soup.find_all('table')
            print(f"Available tables: {[t.get('id') for t in tables]}")
            return
        
        print("Found passing table!")
        
        # Get header row
        header_row = passing_table.find('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
            print(f"Headers: {headers[:10]}...")  # First 10 headers
        
        # Get first few data rows
        data_rows = passing_table.find('tbody').find_all('tr') if passing_table.find('tbody') else []
        print(f"Found {len(data_rows)} data rows")
        
        for i, row in enumerate(data_rows[:3]):
            cells = row.find_all(['td', 'th'])
            if cells:
                player_name = cells[0].get_text(strip=True) if len(cells) > 0 else "N/A"
                team = cells[1].get_text(strip=True) if len(cells) > 1 else "N/A"
                completions = cells[5].get_text(strip=True) if len(cells) > 5 else "N/A"
                attempts = cells[6].get_text(strip=True) if len(cells) > 6 else "N/A"
                yards = cells[8].get_text(strip=True) if len(cells) > 8 else "N/A"
                
                print(f"  Row {i}: {player_name} ({team}) - {completions}/{attempts}, {yards} yds")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_2024_passing_table()
    test_joe_burrow_page() 