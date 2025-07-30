#!/usr/bin/env python3
"""
Test PFR scraping with variable delays (7-12 seconds)
"""

import logging
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.working_selenium_manager import WorkingSeleniumManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pfr_scraping():
    """Test scraping PFR with variable delays"""
    logger.info("Testing PFR scraping with variable delays (7-12 seconds)...")
    
    # Test URLs - start with main page, then specific player pages
    test_urls = [
        "https://www.pro-football-reference.com/",
        "https://www.pro-football-reference.com/players/B/BurrJo00.htm",  # Joe Burrow
        "https://www.pro-football-reference.com/players/M/MahoPa00.htm",  # Patrick Mahomes
    ]
    
    try:
        with WorkingSeleniumManager(
            headless=True,
            min_delay=7.0,
            max_delay=12.0
        ) as manager:
            
            for i, url in enumerate(test_urls, 1):
                logger.info(f"Request {i}/{len(test_urls)}: Testing {url}")
                
                try:
                    # Make request with variable delay
                    response = manager.get(url)
                    
                    if response:
                        logger.info(f"✅ SUCCESS: Got {len(response)} characters")
                        logger.info(f"   First 200 chars: {response[:200]}...")
                        
                        # Check if we got actual content (not error page)
                        if "Pro Football Reference" in response:
                            logger.info("   ✅ Confirmed: Got PFR content")
                        else:
                            logger.warning("   ⚠️  Warning: Content doesn't look like PFR")
                    else:
                        logger.error(f"❌ FAILED: No response received")
                        
                except Exception as e:
                    logger.error(f"❌ ERROR: {e}")
                
                # The manager will automatically apply the 7-12 second delay
                if i < len(test_urls):
                    logger.info(f"   Waiting for variable delay before next request...")
            
            # Print final metrics
            logger.info(f"\nFinal Metrics:")
            logger.info(f"  Total requests: {manager.metrics.total_requests}")
            logger.info(f"  Successful: {manager.metrics.successful_requests}")
            logger.info(f"  Failed: {manager.metrics.failed_requests}")
            logger.info(f"  Success rate: {manager.metrics.success_rate:.1f}%")
            
    except Exception as e:
        logger.error(f"Failed to initialize Selenium manager: {e}")
        return False
    
    return True

def test_pfr_player_page():
    """Test scraping a specific PFR player page"""
    logger.info("\nTesting specific PFR player page scraping...")
    
    player_url = "https://www.pro-football-reference.com/players/B/BurrJo00.htm"
    
    try:
        with WorkingSeleniumManager(
            headless=True,
            min_delay=7.0,
            max_delay=12.0
        ) as manager:
            
            logger.info(f"Scraping Joe Burrow's page: {player_url}")
            
            response = manager.get(player_url)
            
            if response:
                logger.info(f"✅ SUCCESS: Got {len(response)} characters")
                
                # Check for key content indicators
                checks = [
                    ("Joe Burrow", "Player name found"),
                    ("Cincinnati Bengals", "Team found"),
                    ("passing", "Passing stats section"),
                    ("rushing", "Rushing stats section"),
                ]
                
                for text, description in checks:
                    if text in response:
                        logger.info(f"   ✅ {description}")
                    else:
                        logger.warning(f"   ⚠️  {description} - NOT FOUND")
                
                # Save a sample for inspection
                with open("pfr_test_sample.html", "w", encoding="utf-8") as f:
                    f.write(response[:5000])  # First 5000 chars
                logger.info("   📄 Saved sample to pfr_test_sample.html")
                
            else:
                logger.error("❌ FAILED: No response received")
                
    except Exception as e:
        logger.error(f"Failed to scrape player page: {e}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("PFR Scraping Test with Variable Delays")
    logger.info("=" * 50)
    
    # Test basic PFR access
    success1 = test_pfr_scraping()
    
    # Test specific player page
    success2 = test_pfr_player_page()
    
    if success1 and success2:
        logger.info("\n🎉 All tests completed successfully!")
    else:
        logger.error("\n❌ Some tests failed. Check the logs above.") 