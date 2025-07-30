#!/usr/bin/env python3
"""
Test script for enhanced scraper with fixed request manager
Tests a single player scrape to verify 403 errors are resolved
"""

import sys
import os
import logging
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.enhanced_scraper import EnhancedPFRScraper
from config.config import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_player_scrape():
    """Test scraping a single player to verify the fix works"""
    logger.info("Testing enhanced scraper with single player...")
    
    # Create scraper with conservative settings
    scraper = EnhancedPFRScraper(rate_limit_delay=5.0)
    
    # Test with a well-known QB
    test_player = "Joe Burrow"
    test_season = 2024
    
    logger.info(f"Testing scrape for {test_player} ({test_season})")
    
    try:
        # Get main stats
        logger.info("Getting main stats...")
        players, stats = scraper.get_qb_main_stats(test_season, [test_player])
        
        if players and stats:
            logger.info(f"Successfully scraped main stats for {test_player}")
            logger.info(f"Found {len(players)} players and {len(stats)} stat records")
            
            # Get metrics
            metrics = scraper.get_scraping_metrics()
            logger.info(f"Scraping metrics:")
            logger.info(f"  Total requests: {metrics.total_requests}")
            logger.info(f"  Successful: {metrics.successful_requests}")
            logger.info(f"  Failed: {metrics.failed_requests}")
            logger.info(f"  Rate limit violations: {metrics.rate_limit_violations}")
            logger.info(f"  Success rate: {metrics.get_success_rate():.1f}%")
            
            return True
        else:
            logger.error("No data returned from scraper")
            return False
            
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return False

def test_request_manager_directly():
    """Test the request manager directly with PFR URLs"""
    logger.info("Testing request manager directly with PFR...")
    
    from core.request_manager import RequestManager
    
    manager = RequestManager(rate_limit_delay=5.0, jitter_range=2.0)
    
    # Test with a simple PFR page
    test_url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    
    logger.info(f"Making request to {test_url}")
    response = manager.get(test_url)
    
    if response and response.status_code == 200:
        logger.info("Successfully accessed PFR!")
        logger.info(f"Response length: {len(response.text)} characters")
        
        # Check if we got actual content
        if "Pro Football Reference" in response.text:
            logger.info("Confirmed we got PFR content")
            return True
        else:
            logger.warning("Got response but content doesn't look like PFR")
            return False
    else:
        logger.error(f"Failed to access PFR: {response.status_code if response else 'No response'}")
        return False

def main():
    """Run the tests"""
    logger.info("Starting enhanced scraper fix tests...")
    
    tests = [
        ("Request Manager Direct Test", test_request_manager_directly),
        ("Single Player Scrape Test", test_single_player_scrape),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"Test {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
        
        # Add delay between tests
        time.sleep(2)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed! The 403 error fix is working.")
        return 0
    else:
        logger.error("Some tests failed. The fix may need adjustment.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 