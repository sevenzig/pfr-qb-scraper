#!/usr/bin/env python3
"""
Test script to verify variable delay functionality (7-12 seconds)
"""

import time
import logging
from src.core.working_selenium_manager import WorkingSeleniumManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_variable_delay():
    """Test that the variable delay works correctly"""
    logger.info("Testing variable delay functionality (7-12 seconds)...")
    
    try:
        with WorkingSeleniumManager(
            headless=True, 
            min_delay=7.0, 
            max_delay=12.0
        ) as manager:
            
            # Test multiple requests to see the variable delays
            test_urls = [
                "https://httpbin.org/delay/1",
                "https://httpbin.org/delay/1", 
                "https://httpbin.org/delay/1"
            ]
            
            for i, url in enumerate(test_urls, 1):
                start_time = time.time()
                logger.info(f"Request {i}: Starting request to {url}")
                
                result = manager.get(url)
                
                end_time = time.time()
                request_time = end_time - start_time
                
                if result:
                    logger.info(f"Request {i}: SUCCESS (took {request_time:.2f}s)")
                else:
                    logger.warning(f"Request {i}: FAILED (took {request_time:.2f}s)")
                
                # Show the delay that was applied
                if i < len(test_urls):  # Don't show for last request
                    logger.info(f"Request {i}: Waiting for variable delay (7-12s) before next request...")
                
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    
    logger.info("Variable delay test completed!")
    return True


def test_delay_range():
    """Test that delays are actually within the specified range"""
    logger.info("Testing delay range validation...")
    
    delays = []
    
    try:
        with WorkingSeleniumManager(
            headless=True,
            min_delay=7.0,
            max_delay=12.0
        ) as manager:
            
            # Override the _rate_limit method to capture delays
            original_rate_limit = manager._rate_limit
            
            def capture_delay():
                start_time = time.time()
                original_rate_limit()
                end_time = time.time()
                actual_delay = end_time - start_time
                delays.append(actual_delay)
                logger.info(f"Captured delay: {actual_delay:.2f}s")
            
            manager._rate_limit = capture_delay
            
            # Make a few requests to capture delays
            for i in range(5):
                logger.info(f"Capturing delay {i+1}/5...")
                manager.get("https://httpbin.org/delay/1")
            
    except Exception as e:
        logger.error(f"Delay range test failed: {e}")
        return False
    
    # Analyze the captured delays
    if delays:
        min_actual = min(delays)
        max_actual = max(delays)
        avg_actual = sum(delays) / len(delays)
        
        logger.info(f"Delay Analysis:")
        logger.info(f"  Expected range: 7.0-12.0 seconds")
        logger.info(f"  Actual range: {min_actual:.2f}-{max_actual:.2f} seconds")
        logger.info(f"  Average delay: {avg_actual:.2f} seconds")
        logger.info(f"  Number of samples: {len(delays)}")
        
        # Check if delays are within expected range (with some tolerance)
        tolerance = 0.5  # 0.5 second tolerance
        if min_actual >= (7.0 - tolerance) and max_actual <= (12.0 + tolerance):
            logger.info("✅ SUCCESS: Delays are within expected range!")
            return True
        else:
            logger.warning("⚠️ WARNING: Some delays outside expected range")
            return False
    else:
        logger.error("❌ No delays captured")
        return False


if __name__ == "__main__":
    logger.info("Starting variable delay tests...")
    
    # Test 1: Basic functionality
    success1 = test_variable_delay()
    
    # Test 2: Delay range validation
    success2 = test_delay_range()
    
    if success1 and success2:
        logger.info("✅ All tests passed!")
    else:
        logger.error("❌ Some tests failed!") 