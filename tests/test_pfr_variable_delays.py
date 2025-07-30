#!/usr/bin/env python3
"""
Test PFR access with variable delays (7-12 seconds)
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

def test_pfr_with_variable_delays():
    """Test PFR access with variable delays (7-12 seconds)"""
    logger.info("Testing PFR access with variable delays (7-12 seconds)...")
    
    try:
        with WorkingSeleniumManager(
            headless=True, 
            min_delay=7.0, 
            max_delay=12.0
        ) as manager:
            
            # Test PFR main page
            logger.info("Testing PFR main page...")
            start_time = time.time()
            
            pfr_response = manager.get("https://www.pro-football-reference.com/")
            
            if pfr_response:
                logger.info(f"✅ PFR main page response length: {len(pfr_response)}")
                logger.info(f"⏱️  Time taken: {time.time() - start_time:.2f} seconds")
                
                # Check for key content
                if "Pro Football Reference" in pfr_response:
                    logger.info("✅ Found 'Pro Football Reference' in response")
                else:
                    logger.warning("⚠️  'Pro Football Reference' not found in response")
                
                # Test passing stats page
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
                    with open("pfr_passing_2024_sample.html", "w", encoding="utf-8") as f:
                        f.write(passing_response[:10000])  # First 10,000 characters
                    logger.info("📄 Saved PFR passing stats sample to pfr_passing_2024_sample.html")
                    
                    return True
                else:
                    logger.error("❌ Failed to get PFR passing stats response")
                    return False
            else:
                logger.error("❌ Failed to get PFR main page response")
                return False
                
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_pfr_with_variable_delays()
    if success:
        logger.info("🎉 PFR test with variable delays completed successfully!")
    else:
        logger.error("💥 PFR test with variable delays failed")
        sys.exit(1) 