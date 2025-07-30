#!/usr/bin/env python3
"""
Simple test for PFR passing stats page with longer timeout
"""

import logging
import sys
import os
import time

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

def test_passing_stats_simple():
    """Simple test for passing stats page"""
    logger.info("Testing PFR passing stats page with longer timeout...")
    
    try:
        with WorkingSeleniumManager(
            headless=True, 
            min_delay=7.0, 
            max_delay=12.0
        ) as manager:
            
            # Test passing stats page directly
            logger.info("Testing PFR passing stats page...")
            start_time = time.time()
            
            passing_response = manager.get("https://www.pro-football-reference.com/years/2024/passing.htm")
            
            if passing_response:
                logger.info(f"✅ PFR passing stats response length: {len(passing_response)}")
                logger.info(f"⏱️  Time taken: {time.time() - start_time:.2f} seconds")
                
                # Check for key content
                if "passing" in passing_response.lower():
                    logger.info("✅ Found 'passing' in response")
                else:
                    logger.warning("⚠️  'passing' not found in response")
                
                # Check for player names
                if "Joe Burrow" in passing_response:
                    logger.info("✅ Found 'Joe Burrow' in response")
                else:
                    logger.warning("⚠️  'Joe Burrow' not found in response")
                
                if "Patrick Mahomes" in passing_response:
                    logger.info("✅ Found 'Patrick Mahomes' in response")
                else:
                    logger.warning("⚠️  'Patrick Mahomes' not found in response")
                
                # Save a sample for inspection
                with open("passing_stats_sample.html", "w", encoding="utf-8") as f:
                    f.write(passing_response[:15000])  # First 15,000 characters
                logger.info("📄 Saved passing stats sample to passing_stats_sample.html")
                
                return True
            else:
                logger.error("❌ Failed to get PFR passing stats response")
                return False
                
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_passing_stats_simple()
    if success:
        logger.info("🎉 Passing stats test completed successfully!")
    else:
        logger.error("💥 Passing stats test failed")
        sys.exit(1) 