#!/usr/bin/env python3
"""
Debug test for Selenium page source issues
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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_page_source_debug():
    """Debug page source issues"""
    logger.info("Debugging page source issues...")
    
    try:
        with WorkingSeleniumManager(
            headless=True, 
            min_delay=2.0,  # Shorter delays for debugging
            max_delay=3.0
        ) as manager:
            
            # Test httpbin.org
            logger.info("Testing httpbin.org...")
            response = manager.get("https://httpbin.org/html")
            
            if response:
                logger.info(f"✅ httpbin.org response length: {len(response)}")
                logger.info(f"First 200 chars: {response[:200]}")
            else:
                logger.error("❌ httpbin.org failed")
            
            # Test a simple HTML page
            logger.info("Testing simple HTML page...")
            response2 = manager.get("https://httpbin.org/")
            
            if response2:
                logger.info(f"✅ httpbin.org root response length: {len(response2)}")
                logger.info(f"First 200 chars: {response2[:200]}")
            else:
                logger.error("❌ httpbin.org root failed")
            
            return True
                
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_page_source_debug()
    if success:
        logger.info("🎉 Debug test completed")
    else:
        logger.error("💥 Debug test failed")
        sys.exit(1) 