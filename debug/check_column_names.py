#!/usr/bin/env python3
"""Debug script to check actual column names and data values"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests
from bs4 import BeautifulSoup
from scrapers.enhanced_scraper import EnhancedPFRScraper
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_column_names():
    """Check the actual column names and sample data"""
    
    print("=== Checking Column Names and Data ===")
    
    try:
        # Create scraper and get HTML
        scraper = EnhancedPFRScraper(rate_limit_delay=1.0)
        url = f"{scraper.base_url}/years/2024/passing.htm"
        
        response = scraper.make_request_with_retry(url)
        if not response:
            print("Failed to get response")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse using the simple table method
        df = scraper.parse_simple_table(soup, 'passing')
        
        if df is None:
            print("Failed to parse table")
            return
        
        print(f"DataFrame shape: {df.shape}")
        print(f"Column names: {list(df.columns)}")
        
        # Show first few rows
        print("\nFirst 3 rows:")
        print(df.head(3).to_string())
        
        # Check specific columns we're looking for
        print("\nChecking specific column names:")
        expected_cols = ['Player', 'Tm', 'Pos', 'G', 'GS', 'Cmp', 'Att', 'Yds', 'TD', 'Rate']
        for col in expected_cols:
            if col in df.columns:
                print(f"  ✓ {col}: {df[col].iloc[0] if len(df) > 0 else 'N/A'}")
            else:
                print(f"  ✗ {col}: NOT FOUND")
        
        # Check for QB filtering
        print("\nPosition values in first 10 rows:")
        if 'Pos' in df.columns:
            for i in range(min(10, len(df))):
                player = df['Player'].iloc[i] if 'Player' in df.columns else 'N/A'
                pos = df['Pos'].iloc[i] if 'Pos' in df.columns else 'N/A'
                team = df['Tm'].iloc[i] if 'Tm' in df.columns else 'N/A'
                print(f"  {i}: {player} - {pos} - {team}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_column_names() 