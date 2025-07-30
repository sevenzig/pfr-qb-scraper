#!/usr/bin/env python3
"""
Example: Using Selenium Manager with Variable Delays (7-12 seconds)
"""

import logging
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.working_selenium_manager import WorkingSeleniumManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example of basic usage with variable delays"""
    logger.info("Example: Basic usage with variable delays (7-12 seconds)")
    
    try:
        # Initialize with variable delays
        with WorkingSeleniumManager(
            headless=True,
            min_delay=7.0,    # Minimum 7 seconds between requests
            max_delay=12.0    # Maximum 12 seconds between requests
        ) as manager:
            
            # Test URLs
            test_urls = [
                "https://httpbin.org/delay/1",
                "https://httpbin.org/delay/1",
                "https://httpbin.org/delay/1"
            ]
            
            for i, url in enumerate(test_urls, 1):
                logger.info(f"Request {i}: Making request to {url}")
                
                result = manager.get(url)
                
                if result:
                    logger.info(f"Request {i}: SUCCESS ({len(result)} characters)")
                else:
                    logger.warning(f"Request {i}: FAILED")
                
                # The manager will automatically wait 7-12 seconds before the next request
                if i < len(test_urls):
                    logger.info(f"Request {i}: Waiting for variable delay before next request...")
            
            # Show metrics
            metrics = manager.get_metrics()
            logger.info(f"\nFinal Metrics:")
            logger.info(f"  Total requests: {metrics.total_requests}")
            logger.info(f"  Successful: {metrics.successful_requests}")
            logger.info(f"  Failed: {metrics.failed_requests}")
            logger.info(f"  Success rate: {metrics.get_success_rate():.1f}%")
            
    except Exception as e:
        logger.error(f"Example failed: {e}")


def example_custom_delays():
    """Example with custom delay ranges"""
    logger.info("\nExample: Custom delay ranges")
    
    try:
        # Different delay ranges for different scenarios
        scenarios = [
            ("Conservative", 10.0, 15.0),
            ("Moderate", 7.0, 12.0),
            ("Aggressive", 3.0, 8.0)
        ]
        
        for name, min_delay, max_delay in scenarios:
            logger.info(f"\nTesting {name} delays ({min_delay}-{max_delay}s):")
            
            with WorkingSeleniumManager(
                headless=True,
                min_delay=min_delay,
                max_delay=max_delay
            ) as manager:
                
                # Make a single test request
                result = manager.get("https://httpbin.org/delay/1")
                
                if result:
                    logger.info(f"  {name}: SUCCESS")
                else:
                    logger.warning(f"  {name}: FAILED")
                
                # Show the delay that was applied
                metrics = manager.get_metrics()
                logger.info(f"  {name}: Made {metrics.total_requests} request(s)")
            
    except Exception as e:
        logger.error(f"Custom delays example failed: {e}")


def example_pfr_access():
    """Example of accessing PFR with variable delays"""
    logger.info("\nExample: PFR access with variable delays")
    
    try:
        with WorkingSeleniumManager(
            headless=True,
            min_delay=7.0,
            max_delay=12.0
        ) as manager:
            
            # Test PFR main page
            logger.info("Testing PFR main page access...")
            result = manager.get("https://www.pro-football-reference.com/")
            
            if result and "Pro Football Reference" in result:
                logger.info("✅ PFR main page access successful!")
                
                # Test a player page
                logger.info("Testing player page access...")
                player_result = manager.get("https://www.pro-football-reference.com/players/B/BurrJo01.htm")
                
                if player_result and "Joe Burrow" in player_result:
                    logger.info("✅ Player page access successful!")
                else:
                    logger.warning("⚠️ Player page access failed")
            else:
                logger.warning("⚠️ PFR main page access failed")
            
            # Show metrics
            metrics = manager.get_metrics()
            logger.info(f"\nPFR Access Metrics:")
            logger.info(f"  Total requests: {metrics.total_requests}")
            logger.info(f"  Successful: {metrics.successful_requests}")
            logger.info(f"  Failed: {metrics.failed_requests}")
            logger.info(f"  Success rate: {metrics.get_success_rate():.1f}%")
            
    except Exception as e:
        logger.error(f"PFR access example failed: {e}")


if __name__ == "__main__":
    logger.info("Selenium Manager Variable Delay Examples")
    logger.info("=" * 50)
    
    # Example 1: Basic usage
    example_basic_usage()
    
    # Example 2: Custom delays
    example_custom_delays()
    
    # Example 3: PFR access (commented out to avoid actual requests)
    # example_pfr_access()
    
    logger.info("\nExamples completed!")
    logger.info("\nKey Points:")
    logger.info("  - min_delay and max_delay control the random delay range")
    logger.info("  - Each request waits 7-12 seconds (or your custom range)")
    logger.info("  - Delays are random and distributed across the range")
    logger.info("  - Use conservative delays (7-12s) for PFR to avoid blocks") 