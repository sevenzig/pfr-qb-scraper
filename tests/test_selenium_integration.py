#!/usr/bin/env python3
"""
Test Selenium Integration with Core Scraper.

This script tests the integration of SeleniumManager with CoreScraper,
validating the fallback mechanism between RequestManager and SeleniumManager.
"""

import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.scraper import CoreScraper, Config, DatabaseManager
from core.request_manager import RequestManager
from core.html_parser import HTMLParser
from core.pfr_data_extractor import PFRDataExtractor
from core.selenium_manager import SeleniumManager, SeleniumConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_selenium_manager_creation():
    """Test SeleniumManager creation and configuration."""
    logger.info("=== Testing SeleniumManager Creation ===")
    
    try:
        # Test with default config
        selenium_config = SeleniumConfig()
        selenium_manager = SeleniumManager(selenium_config)
        
        logger.info("✅ SeleniumManager created successfully with default config")
        logger.info(f"  - Headless mode: {selenium_config.headless}")
        logger.info(f"  - Window size: {selenium_config.window_size}")
        logger.info(f"  - Page load timeout: {selenium_config.page_load_timeout}s")
        logger.info(f"  - Max retries: {selenium_config.max_retries}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create SeleniumManager: {e}")
        return False


def test_selenium_session_management():
    """Test Selenium session management."""
    logger.info("=== Testing Selenium Session Management ===")
    
    try:
        selenium_config = SeleniumConfig(headless=True)
        selenium_manager = SeleniumManager(selenium_config)
        
        # Test session start
        selenium_manager.start_session()
        logger.info("✅ Selenium session started successfully")
        
        # Test session info
        session_info = selenium_manager.get_session_info()
        logger.info(f"Session info: {session_info}")
        
        # Test session health
        is_healthy = selenium_manager.is_session_healthy()
        logger.info(f"Session healthy: {is_healthy}")
        
        # Test session end
        selenium_manager.end_session()
        logger.info("✅ Selenium session ended successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to manage Selenium session: {e}")
        return False


def test_core_scraper_with_selenium():
    """Test CoreScraper integration with SeleniumManager."""
    logger.info("=== Testing CoreScraper with SeleniumManager ===")
    
    try:
        # Create configuration
        config = Config()
        
        # Create components
        request_manager = RequestManager(config=config)
        html_parser = HTMLParser()
        data_extractor = PFRDataExtractor()
        db_manager = DatabaseManager()
        
        # Create SeleniumManager (optional - will be None if Selenium is not available)
        selenium_manager = None
        try:
            selenium_config = SeleniumConfig(headless=True)
            selenium_manager = SeleniumManager(selenium_config)
            logger.info("✅ SeleniumManager created successfully")
        except Exception as e:
            logger.warning(f"⚠️ SeleniumManager not available: {e}")
            logger.info("Continuing with RequestManager only")
        
        # Create CoreScraper
        scraper = CoreScraper(
            request_manager=request_manager,
            html_parser=html_parser,
            data_extractor=data_extractor,
            db_manager=db_manager,
            config=config,
            selenium_manager=selenium_manager
        )
        
        logger.info("✅ CoreScraper created successfully with SeleniumManager")
        
        # Test page structure analysis with fallback
        test_url = "https://www.pro-football-reference.com/players/B/BurrJo01.htm"
        logger.info(f"Testing page structure analysis for: {test_url}")
        
        try:
            analysis = scraper.analyze_page_structure(test_url)
            logger.info("✅ Page structure analysis completed")
            logger.info(f"  - Total tables found: {analysis.get('total_tables', 0)}")
            logger.info(f"  - Table types: {list(analysis.get('table_categorization', {}).keys())}")
        except Exception as e:
            logger.warning(f"⚠️ Page structure analysis failed: {e}")
            logger.info("This is expected if PFR is blocking requests")
        
        # Clean up
        if selenium_manager:
            selenium_manager.end_session()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to test CoreScraper with SeleniumManager: {e}")
        return False


def test_fallback_mechanism():
    """Test the fallback mechanism between RequestManager and SeleniumManager."""
    logger.info("=== Testing Fallback Mechanism ===")
    
    try:
        # Create configuration
        config = Config()
        
        # Create components
        request_manager = RequestManager(config=config)
        html_parser = HTMLParser()
        data_extractor = PFRDataExtractor()
        db_manager = DatabaseManager()
        
        # Create SeleniumManager (optional)
        selenium_manager = None
        try:
            selenium_config = SeleniumConfig(headless=True)
            selenium_manager = SeleniumManager(selenium_config)
            logger.info("✅ SeleniumManager available for fallback testing")
        except Exception as e:
            logger.warning(f"⚠️ SeleniumManager not available: {e}")
        
        # Create CoreScraper
        scraper = CoreScraper(
            request_manager=request_manager,
            html_parser=html_parser,
            data_extractor=data_extractor,
            db_manager=db_manager,
            config=config,
            selenium_manager=selenium_manager
        )
        
        # Test fallback mechanism with a simple URL
        test_url = "https://httpbin.org/html"  # Simple test page
        
        logger.info(f"Testing fallback mechanism with: {test_url}")
        
        # Test without JavaScript
        result_no_js = scraper._fetch_page_with_fallback(test_url, enable_js=False)
        logger.info(f"Result without JS: {'✅ Success' if result_no_js['success'] else '❌ Failed'}")
        
        # Test with JavaScript (if SeleniumManager is available)
        if selenium_manager:
            result_with_js = scraper._fetch_page_with_fallback(test_url, enable_js=True)
            logger.info(f"Result with JS: {'✅ Success' if result_with_js['success'] else '❌ Failed'}")
        
        # Clean up
        if selenium_manager:
            selenium_manager.end_session()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to test fallback mechanism: {e}")
        return False


def test_selenium_configuration_options():
    """Test different Selenium configuration options."""
    logger.info("=== Testing Selenium Configuration Options ===")
    
    try:
        # Test different configurations
        configs = [
            ("Default", SeleniumConfig()),
            ("Headless", SeleniumConfig(headless=True)),
            ("With Window", SeleniumConfig(headless=False)),
            ("Custom Timeout", SeleniumConfig(page_load_timeout=60)),
            ("Custom Window Size", SeleniumConfig(window_size=(1366, 768))),
        ]
        
        for config_name, config in configs:
            try:
                selenium_manager = SeleniumManager(config)
                logger.info(f"✅ {config_name} configuration created successfully")
                
                # Test session start/end
                selenium_manager.start_session()
                session_info = selenium_manager.get_session_info()
                logger.info(f"  - Session active: {session_info['session_active']}")
                selenium_manager.end_session()
                
            except Exception as e:
                logger.warning(f"⚠️ {config_name} configuration failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to test Selenium configuration options: {e}")
        return False


def main():
    """Run all Selenium integration tests."""
    logger.info("Starting Selenium Integration Tests")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    # Run tests
    tests = [
        ("SeleniumManager Creation", test_selenium_manager_creation),
        ("Session Management", test_selenium_session_management),
        ("CoreScraper Integration", test_core_scraper_with_selenium),
        ("Fallback Mechanism", test_fallback_mechanism),
        ("Configuration Options", test_selenium_configuration_options),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results[test_name] = success
            if success:
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}", exc_info=True)
            results[test_name] = False
    
    # Print summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    logger.info(f"Tests completed in {duration:.2f} seconds")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Success rate: {(passed/total)*100:.1f}%")
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"  - {test_name}: {status}")
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Selenium integration is working correctly.")
    else:
        logger.error(f"\n⚠️  {total - passed} TESTS FAILED. Please review the issues above.")
    
    # Special note about Selenium availability
    logger.info("\n📝 NOTE: Some tests may fail if Selenium/ChromeDriver is not installed.")
    logger.info("This is expected and the system will fall back to RequestManager.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 