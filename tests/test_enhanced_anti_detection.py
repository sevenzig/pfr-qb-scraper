#!/usr/bin/env python3
"""
Test script for enhanced anti-detection features in RequestManager
Demonstrates the improved session rotation, soft block detection, and behavioral patterns.
"""

import sys
import os
import time
import logging
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.request_manager import RequestManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_session_rotation():
    """Test session rotation functionality"""
    logger.info("Testing session rotation...")
    
    manager = RequestManager()
    
    # Simulate multiple requests to trigger session rotation
    for i in range(20):
        logger.info(f"Request {i+1}")
        
        # Get session info before request
        session_info = manager.get_session_info()
        logger.info(f"Session info: {session_info}")
        
        # Check if session is healthy
        is_healthy = manager.is_session_healthy()
        logger.info(f"Session healthy: {is_healthy}")
        
        # Simulate a request (we'll use a test URL)
        test_url = "https://httpbin.org/headers"
        response = manager.get(test_url)
        
        if response:
            logger.info(f"Request successful: {response.status_code}")
        else:
            logger.warning("Request failed")
        
        # Small delay between requests
        time.sleep(1)
    
    # Get final metrics
    metrics = manager.get_metrics()
    logger.info(f"Final metrics: {metrics}")


def test_soft_block_detection():
    """Test soft block detection functionality"""
    logger.info("Testing soft block detection...")
    
    manager = RequestManager()
    
    # Test with a URL that might return different content
    test_urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/403",
        "https://httpbin.org/status/429",
    ]
    
    for url in test_urls:
        logger.info(f"Testing URL: {url}")
        response = manager.get(url)
        
        if response:
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response length: {len(response.text)}")
            
            # Check for soft block
            if response.status_code == 200:
                is_soft_block = manager._check_for_soft_block(response)
                logger.info(f"Soft block detected: {is_soft_block}")
        else:
            logger.warning("Request failed")
        
        time.sleep(2)


def test_behavioral_patterns():
    """Test realistic behavioral patterns"""
    logger.info("Testing behavioral patterns...")
    
    manager = RequestManager()
    
    # Simulate realistic browsing pattern
    urls = [
        "https://httpbin.org/headers",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/ip",
    ]
    
    for i, url in enumerate(urls):
        logger.info(f"Browsing to: {url}")
        
        # Simulate human behavior
        manager._simulate_human_behavior()
        
        response = manager.get(url)
        if response:
            logger.info(f"Successfully loaded: {url}")
        else:
            logger.warning(f"Failed to load: {url}")
        
        # Simulate reading time
        time.sleep(random.uniform(2, 5))


def test_rate_limiting():
    """Test enhanced rate limiting"""
    logger.info("Testing enhanced rate limiting...")
    
    manager = RequestManager()
    
    # Test multiple rapid requests to see rate limiting in action
    for i in range(5):
        logger.info(f"Rate limit test request {i+1}")
        
        start_time = time.time()
        response = manager.get("https://httpbin.org/delay/1")
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"Request duration: {duration:.2f}s")
        
        if response:
            logger.info("Request successful")
        else:
            logger.warning("Request failed")


def test_session_health_monitoring():
    """Test session health monitoring"""
    logger.info("Testing session health monitoring...")
    
    manager = RequestManager()
    
    # Monitor session health over time
    for i in range(10):
        session_info = manager.get_session_info()
        is_healthy = manager.is_session_healthy()
        
        logger.info(f"Request {i+1}:")
        logger.info(f"  Session healthy: {is_healthy}")
        logger.info(f"  Request count: {session_info['request_count']}")
        logger.info(f"  Consecutive failures: {session_info['consecutive_failures']}")
        logger.info(f"  Session duration: {session_info['session_duration']:.1f}s")
        
        # Make a request
        response = manager.get("https://httpbin.org/headers")
        
        if not response:
            logger.warning("Request failed - session might be compromised")
            if not manager.is_session_healthy():
                logger.info("Forcing session rotation...")
                manager.force_session_rotation()
        
        time.sleep(1)


def main():
    """Run all anti-detection tests"""
    logger.info("Starting enhanced anti-detection tests...")
    
    try:
        # Test 1: Session rotation
        test_session_rotation()
        time.sleep(2)
        
        # Test 2: Soft block detection
        test_soft_block_detection()
        time.sleep(2)
        
        # Test 3: Behavioral patterns
        test_behavioral_patterns()
        time.sleep(2)
        
        # Test 4: Rate limiting
        test_rate_limiting()
        time.sleep(2)
        
        # Test 5: Session health monitoring
        test_session_health_monitoring()
        
        logger.info("All anti-detection tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import random
    exit(main()) 