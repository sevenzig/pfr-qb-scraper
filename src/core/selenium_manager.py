#!/usr/bin/env python3
"""
Selenium Manager for NFL QB Data Scraping
Handles browser automation for JavaScript-heavy pages and anti-bot bypass.
"""

import logging
import time
import random
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from .request_manager import UserAgentRotator

logger = logging.getLogger(__name__)


@dataclass
class SeleniumConfig:
    """Configuration for Selenium browser automation"""
    headless: bool = True
    window_size: tuple = (1920, 1080)
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    page_load_timeout: int = 30
    implicit_wait: int = 10
    explicit_wait: int = 15
    scroll_pause_time: float = 2.0
    human_behavior_delay: tuple = (1.0, 3.0)
    max_retries: int = 3
    retry_delay: float = 5.0


class HumanBehaviorSimulator:
    """Simulates realistic human browsing behavior"""
    
    def __init__(self, driver: webdriver.Chrome, config: SeleniumConfig):
        self.driver = driver
        self.config = config
        self.actions = ActionChains(driver)
    
    def random_scroll(self):
        """Perform random scrolling to simulate human behavior"""
        try:
            # Get page height
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            if page_height > 1000:
                # Random scroll to different positions
                scroll_positions = [
                    random.randint(100, page_height // 3),
                    random.randint(page_height // 3, 2 * page_height // 3),
                    random.randint(2 * page_height // 3, page_height - 100)
                ]
                
                for position in scroll_positions:
                    self.driver.execute_script(f"window.scrollTo(0, {position});")
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    # Sometimes scroll back up
                    if random.random() < 0.3:
                        self.driver.execute_script(f"window.scrollTo(0, {position - 200});")
                        time.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            logger.debug(f"Error during random scroll: {e}")
    
    def mouse_movement(self):
        """Simulate mouse movements"""
        try:
            # Get viewport size
            viewport_width = self.driver.execute_script("return window.innerWidth;")
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, viewport_width - 100)
                y = random.randint(100, viewport_height - 100)
                self.actions.move_by_offset(x, y).perform()
                time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            logger.debug(f"Error during mouse movement: {e}")
    
    def random_click(self):
        """Perform random clicks on non-interactive elements"""
        try:
            # Find some non-interactive elements to click
            elements = self.driver.find_elements(By.TAG_NAME, "div")
            if elements:
                # Click on a random div (if it's not interactive)
                element = random.choice(elements[:10])  # First 10 elements
                if element.is_displayed() and element.is_enabled():
                    self.actions.click(element).perform()
                    time.sleep(random.uniform(0.2, 0.5))
        except Exception as e:
            logger.debug(f"Error during random click: {e}")
    
    def simulate_reading(self):
        """Simulate time spent reading content"""
        reading_time = random.uniform(*self.config.human_behavior_delay)
        logger.debug(f"Simulating reading time: {reading_time:.2f}s")
        time.sleep(reading_time)
    
    def perform_human_behavior(self):
        """Perform a sequence of human-like behaviors"""
        behaviors = [
            self.random_scroll,
            self.mouse_movement,
            self.random_click,
            self.simulate_reading
        ]
        
        # Randomly choose 2-3 behaviors to perform
        selected_behaviors = random.sample(behaviors, random.randint(2, 3))
        
        for behavior in selected_behaviors:
            behavior()
            time.sleep(random.uniform(0.5, 1.0))


class SeleniumManager:
    """Manages Selenium browser automation for web scraping"""
    
    def __init__(self, config: Optional[SeleniumConfig] = None):
        """
        Initialize the Selenium manager.
        
        Args:
            config: Configuration for Selenium browser automation
        """
        self.config = config or SeleniumConfig()
        self.driver = None
        self.wait = None
        self.human_simulator = None
        self.session_start_time = None
        self.request_count = 0
        self.max_requests_per_session = random.randint(20, 40)
        self.user_agent_rotator = UserAgentRotator()
        
    def _create_driver(self) -> webdriver.Chrome:
        """Create and configure Chrome WebDriver"""
        options = Options()
        
        # Basic options
        if self.config.headless:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
        # Rotate User-Agent for each session
        user_agent = self.user_agent_rotator.get_random_user_agent()
        options.add_argument(f"--user-agent={user_agent}")
        self.config.user_agent = user_agent  # For logging/debugging
        
        # Anti-detection options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance options
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Don't load images for faster scraping
        options.add_argument("--disable-javascript")  # Disable JS for basic pages
        
        # Privacy options
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Create driver
        try:
            driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            driver.set_page_load_timeout(self.config.page_load_timeout)
            driver.implicitly_wait(self.config.implicit_wait)
            
            # Remove automation indicators
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    def start_session(self):
        """Start a new browser session"""
        try:
            logger.info("Starting new Selenium browser session")
            self.driver = self._create_driver()
            self.wait = WebDriverWait(self.driver, self.config.explicit_wait)
            self.human_simulator = HumanBehaviorSimulator(self.driver, self.config)
            self.session_start_time = time.time()
            self.request_count = 0
            
            logger.info("Selenium session started successfully")
        except Exception as e:
            logger.error(f"Failed to start Selenium session: {e}")
            raise
    
    def end_session(self):
        """End the current browser session"""
        if self.driver:
            try:
                logger.info("Ending Selenium browser session")
                self.driver.quit()
                self.driver = None
                self.wait = None
                self.human_simulator = None
                logger.info("Selenium session ended successfully")
            except Exception as e:
                logger.error(f"Error ending Selenium session: {e}")
    
    def _should_rotate_session(self) -> bool:
        """Determine if we should create a new session"""
        if not self.driver:
            return True
        
        session_duration = time.time() - self.session_start_time
        return (
            self.request_count >= self.max_requests_per_session or
            session_duration > 600 or  # 10 minutes
            not self.is_session_healthy()
        )
    
    def is_session_healthy(self) -> bool:
        """Check if the current session is healthy"""
        try:
            if not self.driver:
                return False
            
            # Try to get page title to check if browser is responsive
            self.driver.title
            return True
        except Exception:
            return False
    
    def get_page(self, url: str, enable_js: bool = False) -> Dict[str, Any]:
        """
        Fetch a web page using Selenium.
        
        Args:
            url: The URL to fetch
            enable_js: Whether to enable JavaScript (for dynamic content)
            
        Returns:
            Dict with 'success', 'content', and 'error' keys
        """
        if self._should_rotate_session():
            self.end_session()
            self.start_session()
        
        self.request_count += 1
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Fetching URL with Selenium (attempt {attempt + 1}): {url}")
                
                # Configure JavaScript based on need
                if enable_js:
                    # Re-enable JavaScript for dynamic content
                    self.driver.execute_script("document.documentElement.style.pointerEvents = 'auto';")
                
                # Navigate to URL
                self.driver.get(url)
                
                # Wait for page to load
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Simulate human behavior
                if self.human_simulator:
                    self.human_simulator.perform_human_behavior()
                
                # Check for common blocking indicators
                if self._is_blocked():
                    raise Exception("Page appears to be blocked or showing anti-bot page")
                
                # Get page content
                page_source = self.driver.page_source
                
                # Check if content is meaningful
                if len(page_source) < 1000:
                    raise Exception("Page content is suspiciously short")
                
                logger.info(f"Successfully fetched page: {url}")
                return {
                    'success': True,
                    'content': page_source,
                    'error': None
                }
                
            except TimeoutException:
                error_msg = f"Timeout loading page: {url}"
                logger.warning(f"{error_msg} (attempt {attempt + 1})")
                if attempt == self.config.max_retries - 1:
                    return {'success': False, 'content': None, 'error': error_msg}
                    
            except WebDriverException as e:
                error_msg = f"WebDriver error: {str(e)}"
                logger.warning(f"{error_msg} (attempt {attempt + 1})")
                if attempt == self.config.max_retries - 1:
                    return {'success': False, 'content': None, 'error': error_msg}
                    
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.warning(f"{error_msg} (attempt {attempt + 1})")
                if attempt == self.config.max_retries - 1:
                    return {'success': False, 'content': None, 'error': error_msg}
            
            # Wait before retry
            if attempt < self.config.max_retries - 1:
                wait_time = self.config.retry_delay * (2 ** attempt)
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        return {'success': False, 'content': None, 'error': 'Max retries exceeded'}
    
    def _is_blocked(self) -> bool:
        """Check if the page shows signs of being blocked"""
        try:
            page_text = self.driver.page_source.lower()
            
            # Common blocking indicators
            blocking_indicators = [
                'captcha',
                'verify you are human',
                'please wait',
                'access denied',
                'blocked',
                'suspicious activity',
                'too many requests',
                'rate limit',
                'security check',
                'cloudflare',
                'checking your browser'
            ]
            
            for indicator in blocking_indicators:
                if indicator in page_text:
                    logger.warning(f"Blocking indicator detected: {indicator}")
                    return True
            
            # Check for unusually short content
            if len(page_text) < 1000:
                logger.warning("Suspiciously short page content")
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking for blocking indicators: {e}")
            return False
    
    def wait_for_element(self, by: By, value: str, timeout: Optional[int] = None) -> bool:
        """Wait for a specific element to be present on the page"""
        try:
            wait_time = timeout or self.config.explicit_wait
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return False
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session"""
        return {
            'session_active': self.driver is not None,
            'session_duration': time.time() - self.session_start_time if self.session_start_time else 0,
            'request_count': self.request_count,
            'max_requests_per_session': self.max_requests_per_session,
            'session_healthy': self.is_session_healthy()
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.start_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.end_session() 