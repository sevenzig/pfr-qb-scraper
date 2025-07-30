#!/usr/bin/env python3
"""
Test script to compare different approaches for accessing PFR data
Tests enhanced request manager, Selenium, and alternative data sources
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the request managers
from core.request_manager import RequestManager
from core.selenium_manager import SeleniumRequestManager, test_selenium_setup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_enhanced_request_manager():
    """Test the enhanced request manager with PFR"""
    logger.info("=== Testing Enhanced Request Manager ===")
    
    manager = RequestManager(rate_limit_delay=5.0, jitter_range=2.0)
    
    # Test URLs
    test_urls = [
        "https://www.pro-football-reference.com/",
        "https://www.pro-football-reference.com/years/2024/passing.htm",
        "https://www.pro-football-reference.com/players/B/BurrJo01.htm"
    ]
    
    results = []
    
    for url in test_urls:
        logger.info(f"Testing: {url}")
        start_time = time.time()
        
        response = manager.get(url)
        
        if response and response.status_code == 200:
            duration = time.time() - start_time
            content_length = len(response.text)
            
            # Check for PFR content
            if "Pro Football Reference" in response.text:
                status = "✅ SUCCESS (PFR content)"
            else:
                status = "⚠️ SUCCESS (no PFR content)"
            
            results.append({
                'url': url,
                'status': status,
                'duration': f"{duration:.2f}s",
                'content_length': f"{content_length:,} chars"
            })
            
            logger.info(f"  {status} - {duration:.2f}s - {content_length:,} chars")
        else:
            status_code = response.status_code if response else "No response"
            results.append({
                'url': url,
                'status': f"❌ FAILED ({status_code})",
                'duration': "N/A",
                'content_length': "N/A"
            })
            
            logger.error(f"  ❌ FAILED ({status_code})")
    
    # Print summary
    logger.info("\nEnhanced Request Manager Results:")
    for result in results:
        logger.info(f"  {result['url']}: {result['status']} - {result['duration']} - {result['content_length']}")
    
    metrics = manager.get_metrics()
    logger.info(f"  Total requests: {metrics.total_requests}")
    logger.info(f"  Success rate: {metrics.get_success_rate():.1f}%")
    
    return results


def test_selenium_approach():
    """Test Selenium-based approach"""
    logger.info("\n=== Testing Selenium Approach ===")
    
    # First check if Selenium is available
    if not test_selenium_setup():
        logger.error("❌ Selenium not available or not working")
        return []
    
    try:
        with SeleniumRequestManager(headless=True, rate_limit_delay=5.0) as manager:
            test_urls = [
                "https://www.pro-football-reference.com/",
                "https://www.pro-football-reference.com/years/2024/passing.htm"
            ]
            
            results = []
            
            for url in test_urls:
                logger.info(f"Testing: {url}")
                start_time = time.time()
                
                page_source = manager.get(url)
                
                if page_source:
                    duration = time.time() - start_time
                    content_length = len(page_source)
                    
                    # Check for PFR content
                    if "Pro Football Reference" in page_source:
                        status = "✅ SUCCESS (PFR content)"
                    else:
                        status = "⚠️ SUCCESS (no PFR content)"
                    
                    results.append({
                        'url': url,
                        'status': status,
                        'duration': f"{duration:.2f}s",
                        'content_length': f"{content_length:,} chars"
                    })
                    
                    logger.info(f"  {status} - {duration:.2f}s - {content_length:,} chars")
                else:
                    results.append({
                        'url': url,
                        'status': "❌ FAILED",
                        'duration': "N/A",
                        'content_length': "N/A"
                    })
                    
                    logger.error(f"  ❌ FAILED")
            
            # Print summary
            logger.info("\nSelenium Results:")
            for result in results:
                logger.info(f"  {result['url']}: {result['status']} - {result['duration']} - {result['content_length']}")
            
            metrics = manager.get_metrics()
            logger.info(f"  Total requests: {metrics.total_requests}")
            logger.info(f"  Success rate: {metrics.get_success_rate():.1f}%")
            
            return results
            
    except Exception as e:
        logger.error(f"❌ Selenium test failed: {e}")
        return []


def test_alternative_data_sources():
    """Test alternative data sources for NFL QB data"""
    logger.info("\n=== Testing Alternative Data Sources ===")
    
    # Alternative sources that might have similar data
    alternative_sources = [
        {
            'name': 'ESPN Stats',
            'url': 'https://www.espn.com/nfl/stats/player/_/stat/passing',
            'description': 'ESPN NFL passing stats'
        },
        {
            'name': 'NFL.com Stats',
            'url': 'https://www.nfl.com/stats/player-stats/category/passing/2024/reg/all/passingyards/desc',
            'description': 'NFL.com official stats'
        },
        {
            'name': 'Football Reference (Alternative)',
            'url': 'https://www.football-reference.com/years/2024/passing.htm',
            'description': 'Alternative Football Reference URL'
        }
    ]
    
    manager = RequestManager(rate_limit_delay=3.0, jitter_range=1.0)
    results = []
    
    for source in alternative_sources:
        logger.info(f"Testing: {source['name']} - {source['url']}")
        start_time = time.time()
        
        response = manager.get(source['url'])
        
        if response and response.status_code == 200:
            duration = time.time() - start_time
            content_length = len(response.text)
            
            # Check for relevant content
            if any(keyword in response.text.lower() for keyword in ['passing', 'quarterback', 'qb', 'stats']):
                status = "✅ SUCCESS (relevant content)"
            else:
                status = "⚠️ SUCCESS (no relevant content)"
            
            results.append({
                'name': source['name'],
                'url': source['url'],
                'status': status,
                'duration': f"{duration:.2f}s",
                'content_length': f"{content_length:,} chars",
                'description': source['description']
            })
            
            logger.info(f"  {status} - {duration:.2f}s - {content_length:,} chars")
        else:
            status_code = response.status_code if response else "No response"
            results.append({
                'name': source['name'],
                'url': source['url'],
                'status': f"❌ FAILED ({status_code})",
                'duration': "N/A",
                'content_length': "N/A",
                'description': source['description']
            })
            
            logger.error(f"  ❌ FAILED ({status_code})")
    
    # Print summary
    logger.info("\nAlternative Sources Results:")
    for result in results:
        logger.info(f"  {result['name']}: {result['status']} - {result['duration']} - {result['content_length']}")
    
    return results


def test_proxy_approach():
    """Test using proxy rotation (conceptual)"""
    logger.info("\n=== Testing Proxy Approach (Conceptual) ===")
    
    # This is a conceptual test - would need actual proxy implementation
    logger.info("Proxy rotation approach would require:")
    logger.info("  1. Rotating proxy service (e.g., Bright Data, SmartProxy)")
    logger.info("  2. Proxy authentication and rotation")
    logger.info("  3. IP geolocation to match user agent")
    logger.info("  4. Session management across proxies")
    
    logger.info("Estimated cost: $50-200/month for reliable proxy service")
    logger.info("Success rate: 80-95% with good proxy rotation")
    
    return [{'name': 'Proxy Rotation', 'status': '🔧 REQUIRES IMPLEMENTATION', 'cost': '$50-200/month'}]


def generate_recommendations(results):
    """Generate recommendations based on test results"""
    logger.info("\n=== RECOMMENDATIONS ===")
    
    # Analyze results
    enhanced_success = any('SUCCESS' in r['status'] for r in results.get('enhanced', []))
    selenium_success = any('SUCCESS' in r['status'] for r in results.get('selenium', []))
    alternative_success = any('SUCCESS' in r['status'] for r in results.get('alternatives', []))
    
    if enhanced_success:
        logger.info("✅ Enhanced Request Manager works - RECOMMENDED")
        logger.info("   - Lowest cost and complexity")
        logger.info("   - Good for moderate scraping needs")
        logger.info("   - Easy to maintain and debug")
    
    if selenium_success:
        logger.info("✅ Selenium approach works - RECOMMENDED for heavy scraping")
        logger.info("   - Handles JavaScript execution")
        logger.info("   - More reliable for complex sites")
        logger.info("   - Higher resource usage")
        logger.info("   - Requires browser driver setup")
    
    if alternative_success:
        logger.info("✅ Alternative sources available - CONSIDER")
        logger.info("   - May have different data formats")
        logger.info("   - Could be more reliable")
        logger.info("   - Requires data mapping/transformation")
    
    if not enhanced_success and not selenium_success:
        logger.info("❌ Both approaches failed - CONSIDER PROXY ROTATION")
        logger.info("   - PFR may have sophisticated anti-bot measures")
        logger.info("   - Proxy rotation could help bypass IP-based blocking")
        logger.info("   - Consider commercial proxy services")
    
    logger.info("\n=== NEXT STEPS ===")
    if enhanced_success:
        logger.info("1. Deploy enhanced request manager with conservative settings")
        logger.info("2. Monitor success rates and adjust rate limiting")
        logger.info("3. Implement data validation and error recovery")
    
    if selenium_success:
        logger.info("1. Set up Selenium environment (Chrome/Firefox drivers)")
        logger.info("2. Test with full scraping workflow")
        logger.info("3. Optimize for performance and reliability")
    
    logger.info("4. Consider implementing both approaches with fallback")
    logger.info("5. Monitor PFR's anti-bot measures and adapt accordingly")


def main():
    """Run all tests and generate recommendations"""
    logger.info("Starting comprehensive PFR access testing...")
    
    results = {}
    
    # Test enhanced request manager
    try:
        results['enhanced'] = test_enhanced_request_manager()
    except Exception as e:
        logger.error(f"Enhanced request manager test failed: {e}")
        results['enhanced'] = []
    
    # Test Selenium approach
    try:
        results['selenium'] = test_selenium_approach()
    except Exception as e:
        logger.error(f"Selenium test failed: {e}")
        results['selenium'] = []
    
    # Test alternative sources
    try:
        results['alternatives'] = test_alternative_data_sources()
    except Exception as e:
        logger.error(f"Alternative sources test failed: {e}")
        results['alternatives'] = []
    
    # Test proxy approach (conceptual)
    results['proxy'] = test_proxy_approach()
    
    # Generate recommendations
    generate_recommendations(results)
    
    logger.info("\n=== TESTING COMPLETE ===")
    logger.info("Check the logs above for detailed results and recommendations.")


if __name__ == "__main__":
    main() 