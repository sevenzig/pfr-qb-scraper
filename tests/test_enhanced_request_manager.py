#!/usr/bin/env python3
"""
Test script for enhanced request manager
Verifies user agent rotation and rate limiting work correctly
"""

import sys
import os
import time
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import after adding to path
try:
    from core.request_manager import RequestManager, UserAgentRotator, RateLimiter
    from config.config import config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_user_agent_rotation():
    """Test that user agents rotate correctly"""
    logger.info("Testing user agent rotation...")
    
    rotator = UserAgentRotator()
    
    # Test sequential rotation
    user_agents = []
    for i in range(5):
        user_agent = rotator.get_next_user_agent()
        user_agents.append(user_agent)
        logger.info(f"User agent {i+1}: {user_agent[:50]}...")
    
    # Verify we get different user agents
    unique_agents = set(user_agents)
    logger.info(f"Got {len(unique_agents)} unique user agents out of {len(user_agents)} requests")
    
    # Test random selection
    random_agent = rotator.get_random_user_agent()
    logger.info(f"Random user agent: {random_agent[:50]}...")
    
    return len(unique_agents) > 1

def test_rate_limiter():
    """Test that rate limiting works correctly"""
    logger.info("Testing rate limiter...")
    
    limiter = RateLimiter(base_delay=1.0, jitter_range=0.5)
    
    start_time = time.time()
    
    # Make 3 requests with rate limiting
    for i in range(3):
        logger.info(f"Request {i+1}")
        limiter.wait()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info(f"Total time for 3 requests: {total_time:.2f}s")
    
    # Should take at least 2 seconds (3 requests with 1s base delay)
    return total_time >= 2.0

def test_request_manager():
    """Test the full request manager"""
    logger.info("Testing request manager...")
    
    manager = RequestManager(rate_limit_delay=2.0, jitter_range=0.5)
    
    # Test a simple request to a reliable site
    test_url = "https://httpbin.org/user-agent"
    
    logger.info(f"Making request to {test_url}")
    response = manager.get(test_url)
    
    if response and response.status_code == 200:
        logger.info("Request successful!")
        logger.info(f"Response user agent: {response.json().get('user-agent', 'Unknown')}")
        
        # Check metrics
        metrics = manager.get_metrics()
        logger.info(f"Metrics: {metrics.total_requests} total, {metrics.successful_requests} successful")
        
        return True
    else:
        logger.error(f"Request failed: {response.status_code if response else 'No response'}")
        return False

def test_403_handling():
    """Test handling of 403 errors"""
    logger.info("Testing 403 error handling...")
    
    manager = RequestManager(rate_limit_delay=1.0, jitter_range=0.5)
    
    # Test with a URL that might return 403 (or any error)
    test_url = "https://httpbin.org/status/403"
    
    logger.info(f"Making request to {test_url} (expecting 403)")
    response = manager.get(test_url, max_retries=2)
    
    # Should handle 403 gracefully and return None after retries
    if response is None:
        logger.info("Correctly handled 403 error (returned None)")
        return True
    else:
        logger.warning(f"Unexpected response: {response.status_code}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting enhanced request manager tests...")
    
    tests = [
        ("User Agent Rotation", test_user_agent_rotation),
        ("Rate Limiter", test_rate_limiter),
        ("Request Manager", test_request_manager),
        ("403 Error Handling", test_403_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"Test {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed! Enhanced request manager is working correctly.")
        return 0
    else:
        logger.error("Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 