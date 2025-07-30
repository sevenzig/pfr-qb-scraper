#!/usr/bin/env python3
"""
Test script to verify access to Pro Football Reference
Tests the 403 error fix with actual PFR URLs
"""

import sys
import os
import time
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the enhanced request manager
from core.request_manager import RequestManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pfr_main_page():
    """Test access to PFR main page"""
    logger.info("Testing access to PFR main page...")
    
    manager = RequestManager(rate_limit_delay=5.0, jitter_range=2.0)
    
    # Test with PFR main page
    test_url = "https://www.pro-football-reference.com/"
    
    logger.info(f"Making request to {test_url}")
    response = manager.get(test_url)
    
    if response and response.status_code == 200:
        logger.info("✅ Successfully accessed PFR main page!")
        logger.info(f"Response length: {len(response.text)} characters")
        
        # Check if we got actual PFR content
        if "Pro Football Reference" in response.text:
            logger.info("✅ Confirmed we got PFR content")
            
            # Check metrics
            metrics = manager.get_metrics()
            logger.info(f"Metrics: {metrics.total_requests} total, {metrics.successful_requests} successful")
            logger.info(f"Success rate: {metrics.get_success_rate():.1f}%")
            
            return True
        else:
            logger.warning("⚠️ Got response but content doesn't look like PFR")
            return False
    else:
        logger.error(f"❌ Failed to access PFR: {response.status_code if response else 'No response'}")
        return False

def test_pfr_passing_stats():
    """Test access to PFR passing stats page"""
    logger.info("Testing access to PFR passing stats page...")
    
    manager = RequestManager(rate_limit_delay=5.0, jitter_range=2.0)
    
    # Test with 2024 passing stats page
    test_url = "https://www.pro-football-reference.com/years/2024/passing.htm"
    
    logger.info(f"Making request to {test_url}")
    response = manager.get(test_url)
    
    if response and response.status_code == 200:
        logger.info("✅ Successfully accessed PFR passing stats!")
        logger.info(f"Response length: {len(response.text)} characters")
        
        # Check if we got actual stats content
        if "passing" in response.text.lower() and "2024" in response.text:
            logger.info("✅ Confirmed we got passing stats content")
            
            # Check metrics
            metrics = manager.get_metrics()
            logger.info(f"Metrics: {metrics.total_requests} total, {metrics.successful_requests} successful")
            logger.info(f"Success rate: {metrics.get_success_rate():.1f}%")
            
            return True
        else:
            logger.warning("⚠️ Got response but content doesn't look like passing stats")
            return False
    else:
        logger.error(f"❌ Failed to access passing stats: {response.status_code if response else 'No response'}")
        return False

def test_pfr_player_page():
    """Test access to a specific player page"""
    logger.info("Testing access to PFR player page...")
    
    manager = RequestManager(rate_limit_delay=5.0, jitter_range=2.0)
    
    # Test with Joe Burrow's page
    test_url = "https://www.pro-football-reference.com/players/B/BurrJo00.htm"
    
    logger.info(f"Making request to {test_url}")
    response = manager.get(test_url)
    
    if response and response.status_code == 200:
        logger.info("✅ Successfully accessed player page!")
        logger.info(f"Response length: {len(response.text)} characters")
        
        # Check if we got actual player content
        if "Joe Burrow" in response.text or "burrow" in response.text.lower():
            logger.info("✅ Confirmed we got player content")
            
            # Check metrics
            metrics = manager.get_metrics()
            logger.info(f"Metrics: {metrics.total_requests} total, {metrics.successful_requests} successful")
            logger.info(f"Success rate: {metrics.get_success_rate():.1f}%")
            
            return True
        else:
            logger.warning("⚠️ Got response but content doesn't look like player page")
            return False
    else:
        logger.error(f"❌ Failed to access player page: {response.status_code if response else 'No response'}")
        return False

def test_multiple_requests():
    """Test multiple requests to verify rate limiting and user agent rotation"""
    logger.info("Testing multiple requests with rate limiting...")
    
    manager = RequestManager(rate_limit_delay=3.0, jitter_range=1.0)
    
    # Test URLs
    test_urls = [
        "https://www.pro-football-reference.com/",
        "https://www.pro-football-reference.com/years/2024/passing.htm",
        "https://www.pro-football-reference.com/players/B/BurrJo00.htm"
    ]
    
    successful_requests = 0
    total_requests = len(test_urls)
    
    for i, url in enumerate(test_urls, 1):
        logger.info(f"Request {i}/{total_requests}: {url}")
        response = manager.get(url)
        
        if response and response.status_code == 200:
            successful_requests += 1
            logger.info(f"✅ Request {i} successful")
        else:
            logger.warning(f"⚠️ Request {i} failed: {response.status_code if response else 'No response'}")
        
        # Small delay between requests
        if i < total_requests:
            time.sleep(1)
    
    # Check overall metrics
    metrics = manager.get_metrics()
    logger.info(f"Overall metrics: {metrics.total_requests} total, {metrics.successful_requests} successful")
    logger.info(f"Success rate: {metrics.get_success_rate():.1f}%")
    
    # Consider it successful if we got at least 2 out of 3 requests
    return successful_requests >= 2

def main():
    """Run all PFR access tests"""
    logger.info("Starting PFR access tests...")
    logger.info("This will test if the 403 error fix is working with actual PFR URLs")
    
    tests = [
        ("PFR Main Page", test_pfr_main_page),
        ("PFR Passing Stats", test_pfr_passing_stats),
        ("PFR Player Page", test_pfr_player_page),
        ("Multiple Requests", test_multiple_requests),
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
    
    if passed >= 3:  # At least 3 out of 4 tests should pass
        logger.info("🎉 SUCCESS! The 403 error fix is working correctly.")
        logger.info("PFR access is working with the enhanced request manager.")
        return 0
    elif passed >= 2:
        logger.info("⚠️ PARTIAL SUCCESS! Some tests passed, but there may be issues.")
        logger.info("The fix is partially working, but may need adjustments.")
        return 1
    else:
        logger.error("❌ FAILURE! Most tests failed. The fix may not be working.")
        logger.error("Check network connectivity and PFR availability.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 