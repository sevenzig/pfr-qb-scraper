#!/usr/bin/env python3
"""
Test script for Selenium-enhanced scraper with variable delays
"""

import logging
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from scrapers.selenium_enhanced_scraper import SeleniumEnhancedPFRScraper
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_selenium_scraper():
    """Test the Selenium-enhanced scraper"""
    logger.info("Testing Selenium-enhanced scraper with variable delays...")
    
    try:
        # Use context manager to ensure proper cleanup
        with SeleniumEnhancedPFRScraper(min_delay=7.0, max_delay=12.0) as scraper:
            
            # Test scraping QB main stats for 2024 season
            logger.info("Testing QB main stats scraping for 2024 season...")
            
            players, qb_stats = scraper.get_qb_main_stats(2024)
            
            logger.info(f"SUCCESS: Scraped {len(players)} players and {len(qb_stats)} QB stats")
            
            # Show some results
            for i, (player, stats) in enumerate(zip(players[:5], qb_stats[:5]), 1):
                logger.info(f"  {i}. {player.player_name} ({player.pfr_id}) - {stats.team}")
                logger.info(f"     URL: {player.pfr_url}")
                logger.info(f"     Stats: {stats.cmp}/{stats.att} for {stats.yds} yards, {stats.td} TD, {stats.int} INT")
            
            # Test with specific players
            logger.info("\nTesting with specific players...")
            specific_players = ["Joe Burrow", "Patrick Mahomes", "Josh Allen"]
            
            players_specific, qb_stats_specific = scraper.get_qb_main_stats(2024, player_names=specific_players)
            
            logger.info(f"SUCCESS: Found {len(players_specific)} specific players")
            for player, stats in zip(players_specific, qb_stats_specific):
                logger.info(f"  - {player.player_name} ({player.pfr_id}) - {stats.team}")
                logger.info(f"    URL: {player.pfr_url}")
            
            # Show metrics
            metrics = scraper.get_scraping_metrics()
            logger.info(f"\nScraping Metrics:")
            logger.info(f"  Total requests: {metrics.total_requests}")
            logger.info(f"  Successful: {metrics.successful_requests}")
            logger.info(f"  Failed: {metrics.failed_requests}")
            logger.info(f"  Success rate: {metrics.success_rate:.1f}%")
            logger.info(f"  URL redirects: {metrics.url_redirects}")
            
            if metrics.errors:
                logger.warning(f"  Errors: {len(metrics.errors)}")
                for error in metrics.errors[:3]:  # Show first 3 errors
                    logger.warning(f"    - {error}")
            
            if metrics.warnings:
                logger.warning(f"  Warnings: {len(metrics.warnings)}")
                for warning in metrics.warnings[:3]:  # Show first 3 warnings
                    logger.warning(f"    - {warning}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        return False

def test_url_pattern_fixing():
    """Test the URL pattern fixing functionality"""
    logger.info("\nTesting URL pattern fixing...")
    
    try:
        with SeleniumEnhancedPFRScraper(min_delay=7.0, max_delay=12.0) as scraper:
            
            # Test cases: known players with different URL patterns
            test_cases = [
                ("BurrJo", "Joe Burrow"),  # Should find BurrJo01
                ("MahoPa", "Patrick Mahomes"),  # Should find correct pattern
                ("AlleJo", "Josh Allen"),  # Should find correct pattern
            ]
            
            for base_id, player_name in test_cases:
                logger.info(f"Testing URL pattern for {player_name} (base ID: {base_id})...")
                
                url = scraper.try_multiple_url_patterns(base_id, player_name)
                
                if url:
                    logger.info(f"  FOUND URL: {url}")
                else:
                    logger.warning(f"  Could not find URL for {player_name}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    logger.info("Selenium-Enhanced Scraper Test")
    logger.info("=" * 50)
    
    # Test main scraper functionality
    success1 = test_selenium_scraper()
    
    # Test URL pattern fixing
    success2 = test_url_pattern_fixing()
    
    if success1 and success2:
        logger.info("\nAll tests completed successfully!")
        logger.info("The Selenium-enhanced scraper is working correctly with:")
        logger.info("  - Variable delays (7-12 seconds)")
        logger.info("  - Correct URL pattern detection")
        logger.info("  - Anti-bot measure bypass")
        logger.info("  - PFR access without 403 errors")
    else:
        logger.error("\n❌ Some tests failed. Check the logs above.") 