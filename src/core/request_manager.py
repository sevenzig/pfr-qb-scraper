#!/usr/bin/env python3
"""
Request Manager for NFL QB Data Scraping
Handles all HTTP requests with rate limiting, retries, and metrics.
Enhanced with user agent rotation and better anti-detection measures.
"""

import logging
import time
import random
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass

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
    
    def get_requests_per_minute(self) -> float:
        """Calculate requests per minute"""
        if not self.start_time or not self.end_time:
            return 0.0
        duration_minutes = (self.end_time - self.start_time).total_seconds() / 60
        if duration_minutes == 0:
            return 0.0
        return self.total_requests / duration_minutes

    def start_session(self):
        """Records the start time of a scraping session."""
        self.start_time = datetime.now()

    def end_session(self):
        """Records the end time of a scraping session."""
        self.end_time = datetime.now()


class BrowserFingerprint:
    """Simulates realistic browser fingerprinting to avoid detection"""
    
    def __init__(self):
        # Common screen resolutions
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
            (1280, 720), (1600, 900), (1024, 768), (2560, 1440)
        ]
        
        # Common viewport sizes
        self.viewport_sizes = [
            (1920, 937), (1366, 625), (1536, 722), (1440, 789),
            (1280, 617), (1600, 789), (1024, 768), (2560, 1313)
        ]
        
        # Color depths
        self.color_depths = [24, 32]
        
        # Timezone offsets (in minutes)
        self.timezone_offsets = [-300, -240, -180, -120, -60, 0, 60, 120, 180, 240, 300, 360, 420, 480]
        
        # Language preferences
        self.languages = [
            'en-US,en;q=0.9',
            'en-US,en;q=0.9,es;q=0.8',
            'en-US,en;q=0.9,fr;q=0.8',
            'en-US,en;q=0.9,de;q=0.8',
            'en-US,en;q=0.9,it;q=0.8'
        ]
        
        # Generate a consistent fingerprint for this session
        self._generate_fingerprint()
    
    def _generate_fingerprint(self):
        """Generate a consistent browser fingerprint for this session"""
        self.screen_width, self.screen_height = random.choice(self.screen_resolutions)
        self.viewport_width, self.viewport_height = random.choice(self.viewport_sizes)
        self.color_depth = random.choice(self.color_depths)
        self.timezone_offset = random.choice(self.timezone_offsets)
        self.language = random.choice(self.languages)
        self.touch_support = random.choice([True, False])
        self.max_touch_points = random.choice([0, 1, 2, 5, 10]) if self.touch_support else 0
        
        # Device type based on screen size
        if self.screen_width < 768:
            self.device_type = 'mobile'
        elif self.screen_width < 1024:
            self.device_type = 'tablet'
        else:
            self.device_type = 'desktop'
    
    def get_headers(self, user_agent: str) -> Dict[str, str]:
        """Generate realistic browser headers based on fingerprint"""
        
        # Determine browser type from user agent
        if 'Chrome' in user_agent:
            browser = 'chrome'
            sec_ch_ua = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
        elif 'Firefox' in user_agent:
            browser = 'firefox'
            sec_ch_ua = '"Mozilla";v="5.0", "Firefox";v="121"'
        elif 'Safari' in user_agent:
            browser = 'safari'
            sec_ch_ua = '"Safari";v="17.1"'
        elif 'Edg' in user_agent:
            browser = 'edge'
            sec_ch_ua = '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"'
        else:
            browser = 'chrome'
            sec_ch_ua = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
        
        # Base headers that all browsers share
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': self.language,
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': sec_ch_ua,
            'Sec-Ch-Ua-Mobile': '?0' if self.device_type == 'desktop' else '?1',
            'Sec-Ch-Ua-Platform': '"Windows"' if 'Windows' in user_agent else '"macOS"' if 'Macintosh' in user_agent else '"Linux"',
            # Enhanced headers for better anti-detection
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-gpc': '1',  # Global Privacy Control
            'TE': 'trailers',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        # Browser-specific headers
        if browser == 'chrome':
            headers.update({
                'Sec-Ch-Ua-Full-Version': '"120.0.6099.109"',
                'Sec-Ch-Ua-Full-Version-List': '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.109", "Google Chrome";v="120.0.6099.109"',
                'Sec-Ch-Ua-Bitness': '"64"',
                'Sec-Ch-Ua-WoA64': '"?0"',
                'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
                'Sec-Ch-Ua-Model': '""',
            })
        elif browser == 'firefox':
            headers.update({
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            })
        elif browser == 'safari':
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
            })
        
        # Add realistic viewport and screen info
        headers['Viewport-Width'] = str(self.viewport_width)
        headers['DPR'] = '1'  # Device pixel ratio
        
        return headers


class UserAgentRotator:
    """Rotates user agents to avoid detection"""
    
    def __init__(self):
        # Realistic user agents from different browsers and operating systems (updated 2024)
        self.user_agents = [
            # Chrome on Windows (most common)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Firefox on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            
            # Chrome on Linux (less common but realistic)
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
    
    def __init__(self, base_delay: Optional[float] = None, jitter_range: Optional[float] = None):
        # Use random base delay between 5-8 seconds for better anti-detection
        self.base_delay = base_delay if base_delay is not None else random.uniform(5.0, 8.0)
        # Increased jitter range for more variation
        self.jitter_range = jitter_range if jitter_range is not None else 3.0
        self.last_request_time = 0.0
        self.consecutive_failures = 0
        self.max_delay = 15.0  # Increased maximum delay in seconds
    
    def wait(self):
        """Waits for the configured delay with jitter and adaptive backoff"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Calculate delay with jitter
        jitter = random.uniform(-self.jitter_range, self.jitter_range)
        delay = max(self.base_delay, self.base_delay + jitter)
        
        # Add adaptive backoff for consecutive failures
        if self.consecutive_failures > 0:
            backoff_multiplier = min(2 ** self.consecutive_failures, 6)  # Increased cap to 6x
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

    def __init__(self, config=None, rate_limit_delay: Optional[float] = None, jitter_range: Optional[float] = None):
        self.config = config or self._default_config()
        self.rate_limiter = RateLimiter(rate_limit_delay, jitter_range)
        self.user_agent_rotator = UserAgentRotator()
        self.browser_fingerprint = BrowserFingerprint()
        self.session = self._create_session()
        self.metrics = ScrapingMetrics()
        self._update_session_headers()
        
        # Session state for realistic browsing
        self._last_url = None
        self._session_start_time = time.time()
        self._request_count = 0
        self._consecutive_failures = 0
        self._session_duration = 0
    
    def _default_config(self):
        """Create default configuration if none provided."""
        class DefaultConfig:
            min_delay = 7.0
            max_delay = 10.0
            max_retries = 3
            timeout = 30
        return DefaultConfig()

    def _create_session(self) -> requests.Session:
        """
        Creates a requests session with a retry strategy.
        
        Returns:
            A new requests.Session object.
        """
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

    def _should_rotate_session(self) -> bool:
        """Determine if we should create a new session for better anti-detection"""
        return (
            self._request_count % 15 == 0 or  # Every 15 requests
            time.time() - self._session_start_time > 300 or  # Every 5 minutes
            self._consecutive_failures > 2  # After multiple failures
        )

    def _rotate_session(self):
        """Create a new session with fresh fingerprint and user agent"""
        logger.debug("Rotating session for anti-detection")
        self.session = self._create_session()
        self.browser_fingerprint = BrowserFingerprint()  # New fingerprint
        self._update_session_headers()
        self._session_start_time = time.time()
        self._request_count = 0
        self._consecutive_failures = 0

    def _update_session_headers(self):
        """Update session headers with a new user agent and realistic browser headers"""
        user_agent = self.user_agent_rotator.get_next_user_agent()
        headers = self.browser_fingerprint.get_headers(user_agent)
        
        # Add referer for subsequent requests (simulates browsing)
        if hasattr(self, '_last_url') and self._last_url:
            headers['Referer'] = self._last_url
        
        self.session.headers.update(headers)
        logger.debug(f"Updated headers with User-Agent: {user_agent[:50]}...")
    
    def set_initial_referer(self, referer: str):
        """Set an initial referer to simulate coming from a search engine or other site"""
        if not hasattr(self, '_last_url') or not self._last_url:
            self._last_url = referer
            self.session.headers['Referer'] = referer
            logger.debug(f"Set initial referer: {referer}")

    def _simulate_human_behavior(self):
        """Simulate more realistic human browsing behavior"""
        # Random small delays to simulate human reading time
        if random.random() < 0.4:  # 40% chance
            time.sleep(random.uniform(1.0, 3.0))
        
        # Simulate mouse movements and scrolling (just delays)
        if random.random() < 0.2:  # 20% chance
            time.sleep(random.uniform(0.2, 0.8))
        
        # Simulate occasional "thinking" time (like reading content)
        if random.random() < 0.15:  # 15% chance
            time.sleep(random.uniform(2.0, 5.0))
        
        # Simulate page load time variations
        if random.random() < 0.1:  # 10% chance
            time.sleep(random.uniform(0.5, 1.5))
        
        # Simulate occasional "mistakes" like double-clicks or back button usage
        if random.random() < 0.05:  # 5% chance
            time.sleep(random.uniform(0.1, 0.3))
        
        # Simulate network latency variations
        if random.random() < 0.3:  # 30% chance
            time.sleep(random.uniform(0.1, 0.5))

    def _check_for_soft_block(self, response: requests.Response) -> bool:
        """Check if response indicates a soft block (200 status but different content)"""
        # Check for common soft block indicators
        content = response.text.lower()
        soft_block_indicators = [
            'captcha',
            'verify you are human',
            'please wait',
            'access denied',
            'blocked',
            'suspicious activity',
            'too many requests',
            'rate limit',
            'security check'
        ]
        
        for indicator in soft_block_indicators:
            if indicator in content:
                logger.warning(f"Soft block detected: {indicator}")
                return True
        
        # Check for unusually short responses (might be block page)
        if len(response.text) < 1000 and 'html' in response.headers.get('content-type', ''):
            logger.warning("Suspiciously short response - possible soft block")
            return True
        
        return False

    def get(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """
        Makes an HTTP GET request with enhanced retry logic and rate limiting.

        Args:
            url: The URL to fetch.
            max_retries: The maximum number of retries for the request.

        Returns:
            A requests.Response object on success, or None on failure.
        """
        self.metrics.total_requests += 1
        self._request_count += 1
        
        # Check if we should rotate session
        if self._should_rotate_session():
            self._rotate_session()
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self.rate_limiter.wait()
                
                # Simulate human behavior
                self._simulate_human_behavior()
                
                # Rotate user agent for retries or periodically (less frequent)
                if attempt > 0 or self._request_count % 10 == 0:
                    self._update_session_headers()
                
                # Add realistic referer for subsequent requests
                if hasattr(self, '_last_url') and self._last_url and attempt == 0:
                    # Only add referer on first attempt to avoid detection
                    self.session.headers['Referer'] = self._last_url
                
                # Add random query parameters to avoid caching issues (less frequent)
                if '?' not in url and random.random() < 0.05:  # Reduced to 5% chance
                    url_with_params = f"{url}?_={int(time.time())}"
                else:
                    url_with_params = url
                
                response = self.session.get(url_with_params, timeout=30)
                
                # Check for soft blocks
                if response.status_code == 200 and self._check_for_soft_block(response):
                    self._consecutive_failures += 1
                    self.rate_limiter.record_failure()
                    wait_time = 30 * (attempt + 1)
                    logger.warning(f"Soft block detected on attempt {attempt + 1}. Waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code == 200:
                    self.metrics.successful_requests += 1
                    self.rate_limiter.record_success()
                    self._last_url = url
                    self._consecutive_failures = 0  # Reset on success
                    return response
                elif response.status_code == 429:
                    self.metrics.rate_limit_violations += 1
                    self.rate_limiter.record_failure()
                    self._consecutive_failures += 1
                    wait_time = 60 * (attempt + 1)  # Longer wait for rate limits
                    logger.warning(
                        f"Rate limited on attempt {attempt + 1} for {url}. "
                        f"Waiting {wait_time}s before retry."
                    )
                    time.sleep(wait_time)
                elif response.status_code == 403:
                    self.rate_limiter.record_failure()
                    self._consecutive_failures += 1
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
                        self._consecutive_failures += 1
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request for {url} failed on attempt {attempt + 1}: {e}")
                self.rate_limiter.record_failure()
                self._consecutive_failures += 1
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        self.metrics.failed_requests += 1
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    def get_metrics(self) -> ScrapingMetrics:
        """Returns the current scraping metrics."""
        return self.metrics

    def reset_metrics(self):
        """Resets the scraping metrics to zero."""
        self.metrics = ScrapingMetrics()

    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information for diagnostics"""
        return {
            'request_count': self._request_count,
            'session_duration': time.time() - self._session_start_time,
            'consecutive_failures': self._consecutive_failures,
            'current_user_agent': self.session.headers.get('User-Agent', 'Unknown')[:50],
            'last_url': self._last_url,
            'rate_limiter_base_delay': self.rate_limiter.base_delay,
            'rate_limiter_jitter_range': self.rate_limiter.jitter_range,
        }

    def is_session_healthy(self) -> bool:
        """Check if current session is healthy (not likely to be detected)"""
        return (
            self._consecutive_failures <= 2 and
            self._request_count < 20 and
            time.time() - self._session_start_time < 600  # Less than 10 minutes
        )

    def force_session_rotation(self):
        """Force a session rotation (useful when detection is suspected)"""
        logger.info("Forcing session rotation due to suspected detection")
        self._rotate_session()

    def start_session(self):
        """Starts a new scraping metrics session."""
        self.reset_metrics()
        self.metrics.start_session()
        
    def end_session(self):
        """Ends the current scraping metrics session."""
        self.metrics.end_session()

    def start_scraping_session(self):
        """Alias for start_session to maintain compatibility."""
        self.start_session()
        
    def end_scraping_session(self):
        """Alias for end_session to maintain compatibility."""
        self.end_session() 

    def get_page(self, url: str) -> Dict[str, Any]:
        """
        Fetch a web page with rate limiting, retries, and error handling.
        Args:
            url: The URL to fetch.
        Returns:
            Dict with 'success', 'content', and 'error' keys.
        """
        max_retries = getattr(self.config, 'max_retries', 3)
        timeout = getattr(self.config, 'timeout', 30)
        
        # Use the existing session which already has proper headers
        attempt = 0
        error = None
        while attempt < max_retries:
            # Use the existing rate limiter
            self.rate_limiter.wait()
            
            try:
                logger.info(f"Fetching URL (attempt {attempt+1}): {url}")
                response = self.session.get(url, timeout=timeout)
                if response.status_code == 200:
                    return {'success': True, 'content': response.text, 'error': None}
                else:
                    error = f"HTTP {response.status_code}: {response.reason}"
                    logger.warning(f"Request failed: {error}")
            except requests.RequestException as e:
                error = str(e)
                logger.warning(f"Request exception: {error}")
            
            # Exponential backoff for retries
            if attempt < max_retries - 1:
                backoff = 7.0 * (2 ** attempt)  # Start with 7s, then 14s, 28s
                logger.info(f"Retrying after {backoff:.1f}s...")
                time.sleep(backoff)
            attempt += 1
        return {'success': False, 'content': None, 'error': error} 