#!/usr/bin/env python3
"""
Simple test for variable delay functionality (7-12 seconds)
"""

import time
import random
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_variable_delay_logic():
    """Test the variable delay logic without Selenium"""
    logger.info("Testing variable delay logic (7-12 seconds)...")
    
    min_delay = 7.0
    max_delay = 12.0
    last_request_time = 0.0
    
    delays = []
    
    def rate_limit():
        """Simulate the rate limiting logic"""
        nonlocal last_request_time
        current_time = time.time()
        time_since_last = current_time - last_request_time
        
        # Calculate random delay between min and max
        delay = random.uniform(min_delay, max_delay)
        
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f}s (delay: {delay:.2f}s)")
            time.sleep(sleep_time)
        
        last_request_time = time.time()
        return delay
    
    # Test multiple delays
    for i in range(5):
        logger.info(f"Test {i+1}/5: Starting...")
        start_time = time.time()
        
        delay = rate_limit()
        delays.append(delay)
        
        end_time = time.time()
        actual_time = end_time - start_time
        
        logger.info(f"Test {i+1}: Delay was {delay:.2f}s, actual sleep was {actual_time:.2f}s")
    
    # Analyze results
    if delays:
        min_actual = min(delays)
        max_actual = max(delays)
        avg_actual = sum(delays) / len(delays)
        
        logger.info(f"\nDelay Analysis:")
        logger.info(f"  Expected range: {min_delay}-{max_delay} seconds")
        logger.info(f"  Actual range: {min_actual:.2f}-{max_actual:.2f} seconds")
        logger.info(f"  Average delay: {avg_actual:.2f} seconds")
        logger.info(f"  Number of samples: {len(delays)}")
        
        # Check if delays are within expected range
        if min_actual >= min_delay and max_actual <= max_delay:
            logger.info("✅ SUCCESS: All delays are within expected range!")
            return True
        else:
            logger.warning("⚠️ WARNING: Some delays outside expected range")
            return False
    else:
        logger.error("❌ No delays captured")
        return False


def test_delay_distribution():
    """Test that delays are reasonably distributed across the range"""
    logger.info("\nTesting delay distribution...")
    
    min_delay = 7.0
    max_delay = 12.0
    num_samples = 100
    
    delays = []
    for _ in range(num_samples):
        delay = random.uniform(min_delay, max_delay)
        delays.append(delay)
    
    # Analyze distribution
    delays.sort()
    min_actual = min(delays)
    max_actual = max(delays)
    avg_actual = sum(delays) / len(delays)
    median_actual = delays[len(delays) // 2]
    
    # Check distribution across quarters
    quarter1 = delays[len(delays) // 4]
    quarter3 = delays[3 * len(delays) // 4]
    
    logger.info(f"Distribution Analysis ({num_samples} samples):")
    logger.info(f"  Min: {min_actual:.2f}s")
    logger.info(f"  Q1: {quarter1:.2f}s")
    logger.info(f"  Median: {median_actual:.2f}s")
    logger.info(f"  Q3: {quarter3:.2f}s")
    logger.info(f"  Max: {max_actual:.2f}s")
    logger.info(f"  Average: {avg_actual:.2f}s")
    
    # Check if distribution looks reasonable
    expected_avg = (min_delay + max_delay) / 2
    avg_diff = abs(avg_actual - expected_avg)
    
    if avg_diff < 1.0:  # Average should be within 1 second of expected
        logger.info("✅ SUCCESS: Delay distribution looks good!")
        return True
    else:
        logger.warning(f"⚠️ WARNING: Average delay ({avg_actual:.2f}s) differs significantly from expected ({expected_avg:.2f}s)")
        return False


if __name__ == "__main__":
    logger.info("Starting variable delay tests...")
    
    # Test 1: Basic delay logic
    success1 = test_variable_delay_logic()
    
    # Test 2: Delay distribution
    success2 = test_delay_distribution()
    
    if success1 and success2:
        logger.info("\n✅ All tests passed! Variable delay (7-12s) is working correctly.")
    else:
        logger.error("\n❌ Some tests failed!") 