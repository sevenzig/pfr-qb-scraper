#!/usr/bin/env python3
"""
Test script to verify the updated scraper works with real player data
"""

import sys
import os
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.enhanced_scraper import EnhancedPFRScraper
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_player_splits():
    """Test scraping splits for a real player"""
    
    print("=== Testing Real Player Splits Scraping ===")
    
    # Create scraper instance
    scraper = EnhancedPFRScraper(rate_limit_delay=2.0)  # 2 second delay for testing
    
    # Test with Joe Burrow's 2024 splits page
    test_url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
    
    print(f"Testing with URL: {test_url}")
    
    try:
        # Test splits discovery
        print("Testing splits discovery...")
        discovered_splits = scraper.discover_splits_from_page_url(test_url)
        
        print(f"Discovered {len(discovered_splits)} split types:")
        for split_type, categories in discovered_splits.items():
            print(f"  {split_type}: {len(categories)} categories")
            # Show first few categories
            category_list = list(categories.keys())
            print(f"    Categories: {category_list[:5]}...")
        
        # Test actual scraping
        print("\nTesting actual splits scraping...")
        splits_data = scraper.scrape_player_splits(
            test_url,
            "joe_burrow",
            "Joe Burrow", 
            "CIN",
            2024,
            datetime.now()
        )
        
        print(f"Successfully scraped {len(splits_data)} split records!")
        
        if splits_data:
            # Show some examples
            print("\nSample split records:")
            for i, split in enumerate(splits_data[:5]):
                print(f"  {i+1}. {split.split_type}/{split.split_category}: "
                      f"{split.completions}/{split.attempts} passes, {split.pass_yards} yards")
        
        # Show metrics
        metrics = scraper.get_scraping_metrics()
        print(f"\nScraping Metrics:")
        print(f"  Total requests: {metrics.total_requests}")
        print(f"  Successful requests: {metrics.successful_requests}")
        print(f"  Failed requests: {metrics.failed_requests}")
        print(f"  Success rate: {metrics.get_success_rate():.1f}%")
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Testing Enhanced Scraper with Real Player Data")
    print("=" * 50)
    
    success = test_real_player_splits()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")

if __name__ == "__main__":
    main() 