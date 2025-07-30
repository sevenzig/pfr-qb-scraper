#!/usr/bin/env python3
"""
Simple test for enhanced request manager
Tests basic functionality without complex imports
"""

import sys
import os
import time
import random
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ScrapingMetrics:
    """Metrics for scraping performance tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_violations: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

class UserAgentRotator:
    """Rotates user agents to avoid detection"""
    
    def __init__(self):
        # Realistic user agents from different browsers and operating systems
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Firefox on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        ]
        self.current_index = 0
    
    def get_next_user_agent(self) -> str:
        """Get the next user agent in rotation"""
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return random.choice(self.user_agents)

class RateLimiter:
    """Enhanced rate limiter with jitter and adaptive delays"""
    
    def __init__(self, base_delay: float = 3.0, jitter_range: float = 1.0):
        self.base_delay = base_delay
        self.jitter_range = jitter_range
        self.last_request_time = 0.0
        self.consecutive_failures = 0
        self.max_delay = 10.0  # Maximum delay in seconds
    
    def wait(self):
        """Waits for the configured delay with jitter and adaptive backoff"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Calculate delay with jitter
        jitter = random.uniform(-self.jitter_range, self.jitter_range)
        delay = max(self.base_delay, self.base_delay + jitter)
        
        # Add adaptive backoff for consecutive failures
        if self.consecutive_failures > 0:
            backoff_multiplier = min(2 ** self.consecutive_failures, 4)  # Cap at 4x
            delay = min(delay * backoff_multiplier, self.max_delay)
        
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def record_failure(self):
        """Record a failed request to increase backoff"""
        self.consecutive_failures += 1
    
    def record_success(self):
        """Record a successful request to reset backoff"""
        self.consecutive_failures = 0

class RequestManager:
    """Enhanced HTTP request manager with user agent rotation and better anti-detection"""

    def __init__(self, rate_limit_delay: float = 3.0, jitter_range: float = 1.0):
        self.rate_limiter = RateLimiter(rate_limit_delay, jitter_range)
        self.user_agent_rotator = UserAgentRotator()
        self.session = self._create_session()
        self.metrics = ScrapingMetrics()
        self._update_session_headers()

    def _create_session(self) -> requests.Session:
        """Creates a requests session with a retry strategy."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,  # Increased backoff factor
            status_forcelist=[429, 403, 500, 502, 503, 504],  # Added 403
            respect_retry_after_header=True,
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session

    def _update_session_headers(self):
        """Update session headers with a new user agent and realistic browser headers"""
        user_agent = self.user_agent_rotator.get_next_user_agent()
        
        # More realistic browser headers
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Add referer for subsequent requests (simulates browsing)
        if hasattr(self, '_last_url') and self._last_url:
            headers['Referer'] = self._last_url
        
        self.session.headers.update(headers)
        logger.debug(f"Updated headers with User-Agent: {user_agent[:50]}...")

    def get(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Makes an HTTP GET request with enhanced retry logic and rate limiting."""
        self.metrics.total_requests += 1
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self.rate_limiter.wait()
                
                # Rotate user agent every few requests to avoid detection
                if attempt > 0 or self.metrics.total_requests % 5 == 0:
                    self._update_session_headers()
                
                # Add a small random delay to simulate human behavior
                if attempt == 0:
                    time.sleep(random.uniform(0.1, 0.5))
                
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    self.metrics.successful_requests += 1
                    self.rate_limiter.record_success()
                    self._last_url = url
                    return response
                elif response.status_code == 429:
                    self.metrics.rate_limit_violations += 1
                    self.rate_limiter.record_failure()
                    wait_time = 60 * (attempt + 1)  # Longer wait for rate limits
                    logger.warning(
                        f"Rate limited on attempt {attempt + 1} for {url}. "
                        f"Waiting {wait_time}s before retry."
                    )
                    time.sleep(wait_time)
                elif response.status_code == 403:
                    self.rate_limiter.record_failure()
                    wait_time = 30 * (attempt + 1)  # Wait for 403 errors
                    logger.warning(
                        f"Access forbidden (403) on attempt {attempt + 1} for {url}. "
                        f"Waiting {wait_time}s before retry."
                    )
                    time.sleep(wait_time)
                    # Rotate user agent immediately for 403 errors
                    self._update_session_headers()
                else:
                    logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1} for {url}")
                    if response.status_code >= 500:
                        self.rate_limiter.record_failure()
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request for {url} failed on attempt {attempt + 1}: {e}")
                self.rate_limiter.record_failure()
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        self.metrics.failed_requests += 1
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    def get_metrics(self) -> ScrapingMetrics:
        """Returns the current scraping metrics."""
        return self.metrics

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
    
    # Test with a URL that returns 403
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
    logger.info("Starting simple request manager tests...")
    
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