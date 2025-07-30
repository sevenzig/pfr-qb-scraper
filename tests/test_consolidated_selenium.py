#!/usr/bin/env python3
"""
Comprehensive test script for the consolidated Selenium manager and PFR scraper
Tests all major functionality including anti-detection features and data extraction.
"""

import sys
import os
import time
import logging
import json
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.selenium_manager import (
    PFRSeleniumManager, PFRScraper, ScrapingConfig, 
    ScrapingMetrics, UserAgentRotator, BrowserFingerprint
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_configuration():
    """Test configuration system"""
    logger.info("Testing configuration system...")
    
    # Test default config
    config = ScrapingConfig()
    assert config.headless == True
    assert config.min_delay == 7.0
    assert config.max_delay == 12.0
    assert config.requests_before_rotation == 12
    
    # Test custom config
    custom_config = ScrapingConfig(
        headless=False,
        min_delay=5.0,
        max_delay=10.0,
        requests_before_rotation=8
    )
    assert custom_config.headless == False
    assert custom_config.min_delay == 5.0
    assert custom_config.max_delay == 10.0
    assert custom_config.requests_before_rotation == 8
    
    # Test config to dict
    config_dict = config.to_dict()
    assert 'headless' in config_dict
    assert 'min_delay' in config_dict
    assert 'max_delay' in config_dict
    
    logger.info("✅ Configuration system test passed!")
    return True


def test_user_agent_rotation():
    """Test user agent rotation"""
    logger.info("Testing user agent rotation...")
    
    rotator = UserAgentRotator()
    
    # Test rotation
    ua1 = rotator.get_next_user_agent()
    ua2 = rotator.get_next_user_agent()
    ua3 = rotator.get_next_user_agent()
    
    assert ua1 != ua2 or ua2 != ua3  # Should rotate
    assert "Chrome" in ua1 or "Firefox" in ua1 or "Safari" in ua1 or "Edg" in ua1
    
    # Test random selection
    random_ua = rotator.get_random_user_agent()
    assert "Mozilla" in random_ua
    
    logger.info("✅ User agent rotation test passed!")
    return True


def test_browser_fingerprint():
    """Test browser fingerprinting"""
    logger.info("Testing browser fingerprinting...")
    
    fingerprint = BrowserFingerprint()
    
    # Test fingerprint properties
    assert hasattr(fingerprint, 'screen_width')
    assert hasattr(fingerprint, 'screen_height')
    assert hasattr(fingerprint, 'viewport_width')
    assert hasattr(fingerprint, 'viewport_height')
    assert hasattr(fingerprint, 'color_depth')
    assert hasattr(fingerprint, 'timezone_offset')
    assert hasattr(fingerprint, 'language')
    assert hasattr(fingerprint, 'device_type')
    
    # Test realistic values
    assert fingerprint.screen_width > 0
    assert fingerprint.screen_height > 0
    assert fingerprint.color_depth in [24, 32]
    assert fingerprint.device_type in ['mobile', 'tablet', 'desktop']
    
    logger.info("✅ Browser fingerprinting test passed!")
    return True


def test_selenium_manager_basic():
    """Test basic Selenium manager functionality"""
    logger.info("Testing basic Selenium manager functionality...")
    
    config = ScrapingConfig(
        headless=True,
        min_delay=1.0,  # Fast for testing
        max_delay=2.0,
        requests_before_rotation=5
    )
    
    try:
        with PFRSeleniumManager(config) as manager:
            # Test basic page access
            result = manager.get("https://httpbin.org/html")
            
            if result and "httpbin" in result.lower():
                logger.info("✅ Basic page access works!")
                
                # Test metrics
                metrics = manager.get_metrics()
                assert metrics.total_requests > 0
                assert metrics.successful_requests > 0
                assert metrics.success_rate > 0
                
                logger.info(f"Metrics: {metrics}")
                logger.info("✅ Basic Selenium manager test passed!")
                return True
            else:
                logger.error("❌ Basic page access failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Basic Selenium manager test failed: {e}")
        return False


def test_pfr_access():
    """Test PFR access specifically"""
    logger.info("Testing PFR access...")
    
    config = ScrapingConfig(
        headless=True,
        min_delay=7.0,
        max_delay=12.0,
        requests_before_rotation=3,  # Fast rotation for testing
        enable_soft_block_detection=True
    )
    
    try:
        with PFRSeleniumManager(config) as manager:
            # Test PFR main page
            result = manager.get("https://www.pro-football-reference.com/")
            
            if result and "Pro Football Reference" in result:
                logger.info("✅ PFR main page access works!")
                
                # Test player page
                player_result = manager.get("https://www.pro-football-reference.com/players/B/BurrJo01.htm")
                
                if player_result and "Joe Burrow" in player_result:
                    logger.info("✅ PFR player page access works!")
                    
                    # Test passing stats page
                    passing_result = manager.get("https://www.pro-football-reference.com/years/2023/passing.htm")
                    
                    if passing_result and "passing" in passing_result.lower():
                        logger.info("✅ PFR passing stats page access works!")
                        
                        # Get final metrics
                        metrics = manager.get_metrics()
                        logger.info(f"Final metrics: {metrics}")
                        
                        return True
                    else:
                        logger.warning("⚠️ PFR passing stats page access failed")
                        return False
                else:
                    logger.warning("⚠️ PFR player page access failed")
                    return False
            else:
                logger.error("❌ PFR main page access failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ PFR access test failed: {e}")
        return False


def test_session_rotation():
    """Test session rotation functionality"""
    logger.info("Testing session rotation...")
    
    config = ScrapingConfig(
        headless=True,
        min_delay=1.0,  # Fast for testing
        max_delay=2.0,
        requests_before_rotation=3,  # Rotate every 3 requests
        max_session_duration=60,  # 1 minute
        log_session_rotation=True
    )
    
    try:
        with PFRSeleniumManager(config) as manager:
            initial_rotations = manager.metrics.session_rotations
            
            # Make multiple requests to trigger rotation
            for i in range(5):
                logger.info(f"Request {i+1}")
                result = manager.get("https://httpbin.org/html")
                if not result:
                    logger.error(f"Request {i+1} failed")
                    return False
            
            # Check if rotation occurred
            final_rotations = manager.metrics.session_rotations
            if final_rotations > initial_rotations:
                logger.info(f"✅ Session rotation works! Rotations: {final_rotations}")
                return True
            else:
                logger.warning("⚠️ Session rotation may not have occurred")
                return False
                
    except Exception as e:
        logger.error(f"❌ Session rotation test failed: {e}")
        return False


def test_soft_block_detection():
    """Test soft block detection"""
    logger.info("Testing soft block detection...")
    
    config = ScrapingConfig(
        headless=True,
        min_delay=1.0,
        max_delay=2.0,
        enable_soft_block_detection=True,
        min_content_length=100
    )
    
    try:
        with PFRSeleniumManager(config) as manager:
            # Test with normal page (should not be blocked)
            result = manager.get("https://httpbin.org/html")
            if result and len(result) > 100:
                logger.info("✅ Normal page not detected as blocked")
                
                # Test with very short response (should be detected as blocked)
                # We'll simulate this by checking the detection logic
                is_blocked = manager._check_for_soft_block("short")
                if is_blocked:
                    logger.info("✅ Short response correctly detected as blocked")
                    return True
                else:
                    logger.warning("⚠️ Short response not detected as blocked")
                    return False
            else:
                logger.error("❌ Normal page access failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Soft block detection test failed: {e}")
        return False


def test_pfr_scraper():
    """Test the high-level PFR scraper"""
    logger.info("Testing PFR scraper...")
    
    config = ScrapingConfig(
        headless=True,
        min_delay=7.0,
        max_delay=12.0,
        requests_before_rotation=5,
        enable_soft_block_detection=True
    )
    
    try:
        with PFRScraper(config) as scraper:
            # Test player scraping
            player_url = "https://www.pro-football-reference.com/players/B/BurrJo01.htm"
            player_data = scraper.scrape_player_stats(player_url)
            
            if 'error' not in player_data:
                logger.info("✅ Player scraping works!")
                logger.info(f"Player name: {player_data.get('player_name', 'Unknown')}")
                
                # Test batch scraping
                urls = [
                    "https://www.pro-football-reference.com/players/B/BurrJo01.htm",
                    "https://www.pro-football-reference.com/players/M/MahoPa00.htm"
                ]
                
                batch_results = scraper.batch_scrape(urls)
                success_count = sum(1 for r in batch_results if 'error' not in r)
                
                if success_count > 0:
                    logger.info(f"✅ Batch scraping works! ({success_count}/{len(urls)} successful)")
                    
                    # Get metrics
                    metrics = scraper.get_metrics()
                    logger.info(f"Final metrics: {metrics}")
                    
                    return True
                else:
                    logger.warning("⚠️ Batch scraping failed")
                    return False
            else:
                logger.warning(f"⚠️ Player scraping failed: {player_data['error']}")
                return False
                
    except Exception as e:
        logger.error(f"❌ PFR scraper test failed: {e}")
        return False


def test_metrics_and_monitoring():
    """Test metrics and monitoring functionality"""
    logger.info("Testing metrics and monitoring...")
    
    config = ScrapingConfig(
        headless=True,
        min_delay=1.0,
        max_delay=2.0
    )
    
    try:
        with PFRSeleniumManager(config) as manager:
            # Start session
            manager.start_session()
            
            # Make some requests
            for i in range(3):
                manager.get("https://httpbin.org/html")
            
            # End session
            manager.end_session()
            
            # Check metrics
            metrics = manager.get_metrics()
            
            assert metrics.total_requests >= 3
            assert metrics.success_rate >= 0
            assert metrics.average_response_time >= 0
            assert metrics.total_duration >= 0
            
            logger.info(f"Metrics: {metrics}")
            logger.info(f"Success rate: {metrics.success_rate:.1f}%")
            logger.info(f"Average response time: {metrics.average_response_time:.2f}s")
            logger.info(f"Total duration: {metrics.total_duration:.2f}s")
            
            logger.info("✅ Metrics and monitoring test passed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Metrics and monitoring test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and recovery"""
    logger.info("Testing error handling...")
    
    config = ScrapingConfig(
        headless=True,
        min_delay=1.0,
        max_delay=2.0,
        max_consecutive_failures=2
    )
    
    try:
        with PFRSeleniumManager(config) as manager:
            # Test with invalid URL
            result = manager.get("https://invalid-url-that-does-not-exist.com")
            if result is None:
                logger.info("✅ Invalid URL correctly handled")
                
                # Test with another invalid URL to trigger failure handling
                result2 = manager.get("https://another-invalid-url.com")
                if result2 is None:
                    logger.info("✅ Multiple failures correctly handled")
                    
                    # Check if session rotation was triggered
                    if manager.consecutive_failures >= 2:
                        logger.info("✅ Failure threshold reached")
                        return True
                    else:
                        logger.warning("⚠️ Failure threshold not reached")
                        return False
                else:
                    logger.error("❌ Second invalid URL not handled correctly")
                    return False
            else:
                logger.error("❌ Invalid URL not handled correctly")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    logger.info("Starting comprehensive Selenium manager tests...")
    
    tests = [
        ("Configuration System", test_configuration),
        ("User Agent Rotation", test_user_agent_rotation),
        ("Browser Fingerprinting", test_browser_fingerprint),
        ("Basic Selenium Manager", test_selenium_manager_basic),
        ("PFR Access", test_pfr_access),
        ("Session Rotation", test_session_rotation),
        ("Soft Block Detection", test_soft_block_detection),
        ("PFR Scraper", test_pfr_scraper),
        ("Metrics and Monitoring", test_metrics_and_monitoring),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            start_time = time.time()
            success = test_func()
            end_time = time.time()
            
            if success:
                logger.info(f"✅ {test_name} PASSED ({end_time - start_time:.2f}s)")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED ({end_time - start_time:.2f}s)")
                failed += 1
            
            results.append((test_name, success, end_time - start_time))
            
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
            failed += 1
            results.append((test_name, False, 0))
        
        # Small delay between tests
        time.sleep(1)
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total tests: {len(tests)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success rate: {passed/len(tests)*100:.1f}%")
    
    if failed == 0:
        logger.info("\n🎉 ALL TESTS PASSED! The consolidated Selenium manager is ready for production.")
    else:
        logger.info(f"\n⚠️ {failed} test(s) failed. Please review the errors above.")
    
    # Print detailed results
    logger.info(f"\nDetailed Results:")
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {status} {test_name} ({duration:.2f}s)")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 