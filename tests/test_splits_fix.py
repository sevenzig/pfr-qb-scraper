#!/usr/bin/env python3
"""
Test script to verify the updated scraper can handle both tables from splits pages
"""

import sys
import os
import pandas as pd
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.enhanced_scraper import EnhancedPFRScraper
from models.qb_models import QBSplitStats

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_csv_processing():
    """Test processing the CSV files to verify the data structure"""
    
    print("=== Testing CSV Processing ===")
    
    # Load the CSV files
    try:
        df1 = pd.read_csv('setup/advanced_stats_1.csv')
        df2 = pd.read_csv('setup/advanced_stats.2.csv')
        
        print(f"Table 1 shape: {df1.shape}")
        print(f"Table 2 shape: {df2.shape}")
        
        print(f"\nTable 1 columns: {list(df1.columns)}")
        print(f"Table 2 columns: {list(df2.columns)}")
        
        # Show the first few rows of each table
        print(f"\nTable 1 first 3 rows:")
        print(df1.head(3))
        
        print(f"\nTable 2 first 3 rows:")
        print(df2.head(3))
        
        # Check for unique split types in each table
        print(f"\nTable 1 unique values in first column:")
        print(df1.iloc[:, 0].unique())
        
        print(f"\nTable 2 unique values in first column:")
        print(df2.iloc[:, 0].unique())
        
        return True
        
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return False

def test_scraper_methods():
    """Test the scraper methods with the CSV data"""
    
    print("\n=== Testing Scraper Methods ===")
    
    # Create scraper instance
    scraper = EnhancedPFRScraper()
    
    # Load CSV data
    df1 = pd.read_csv('setup/advanced_stats_1.csv')
    df2 = pd.read_csv('setup/advanced_stats.2.csv')
    
    # Test processing each table
    test_player_id = "test_player_123"
    test_player_name = "Test Player"
    test_team = "Test Team"
    test_season = 2024
    test_scraped_at = pd.Timestamp.now()
    
    print("Testing Table 1 processing...")
    try:
        # Process a few categories from table 1
        categories_to_test = ['League', 'Place', 'Result']
        
        for category in categories_to_test:
            print(f"Processing category: {category}")
            splits = scraper.process_splits_table(
                df1, test_player_id, test_player_name, test_team, 
                test_season, "basic_splits", category, test_scraped_at, "Split"
            )
            print(f"  Found {len(splits)} split records")
            
            if splits:
                for split in splits[:2]:  # Show first 2
                    print(f"    - {split.split_category}: {split.games} games, {split.completions}/{split.attempts} passes")
    
    except Exception as e:
        print(f"Error processing table 1: {e}")
    
    print("\nTesting Table 2 processing...")
    try:
        # Process a few categories from table 2
        categories_to_test = ['Down', 'Yards To Go', 'Field Position']
        
        for category in categories_to_test:
            print(f"Processing category: {category}")
            splits = scraper.process_splits_table(
                df2, test_player_id, test_player_name, test_team, 
                test_season, "situational_splits", category, test_scraped_at, "Split"
            )
            print(f"  Found {len(splits)} split records")
            
            if splits:
                for split in splits[:2]:  # Show first 2
                    print(f"    - {split.split_category}: {split.games} games, {split.completions}/{split.attempts} passes")
    
    except Exception as e:
        print(f"Error processing table 2: {e}")

def main():
    """Main test function"""
    print("Testing Enhanced Scraper with Multiple Tables")
    print("=" * 50)
    
    # Test CSV processing
    if not test_csv_processing():
        print("CSV processing test failed!")
        return
    
    # Test scraper methods
    test_scraper_methods()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main() 