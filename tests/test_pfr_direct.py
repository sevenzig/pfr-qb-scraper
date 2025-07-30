#!/usr/bin/env python3
"""
Direct test to access PFR data
"""

import logging
import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.working_selenium_manager import WorkingSeleniumManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pfr_direct():
    """Test direct access to PFR data"""
    logger.info("Testing direct PFR access...")
    
    try:
        with WorkingSeleniumManager(headless=True, min_delay=7.0, max_delay=12.0) as manager:
            # Test the main passing stats page
            url = "https://www.pro-football-reference.com/years/2024/passing.htm"
            
            logger.info(f"Accessing: {url}")
            response = manager.get(url)
            
            if not response:
                logger.error("Failed to get response")
                return False
            
            logger.info(f"Got response: {len(response)} characters")
            
            # Save the full response
            with open("pfr_full_response.html", "w", encoding="utf-8") as f:
                f.write(response)
            
            logger.info("Saved full response to pfr_full_response.html")
            
            # Check if we can find the table
            if "id=\"passing\"" in response:
                logger.info("Found passing table ID in response")
            else:
                logger.warning("Passing table ID not found in response")
            
            # Check for player names
            if "Joe Burrow" in response:
                logger.info("Found Joe Burrow in response")
            else:
                logger.warning("Joe Burrow not found in response")
            
            if "Patrick Mahomes" in response:
                logger.info("Found Patrick Mahomes in response")
            else:
                logger.warning("Patrick Mahomes not found in response")
            
            # Check for table structure
            if "<table" in response:
                logger.info("Found table tags in response")
            else:
                logger.warning("No table tags found in response")
            
            return True
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pfr_direct()
    if success:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed")
        sys.exit(1) 