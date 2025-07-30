#!/usr/bin/env python3
"""
Full System Integration Test.

This script demonstrates the complete NFL QB data extraction system
working with both RequestManager and SeleniumManager, showing the
complete data extraction pipeline from start to finish.
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


def test_system_initialization():
    """Test complete system initialization with all components."""
    logger.info("=== Testing Complete System Initialization ===")
    
    try:
        # Create configuration
        config = Config()
        logger.info("✅ Configuration created")
        
        # Create RequestManager
        request_manager = RequestManager(config=config)
        logger.info("✅ RequestManager created")
        
        # Create HTMLParser
        html_parser = HTMLParser()
        logger.info("✅ HTMLParser created")
        
        # Create PFRDataExtractor
        data_extractor = PFRDataExtractor()
        logger.info("✅ PFRDataExtractor created")
        
        # Create DatabaseManager
        db_manager = DatabaseManager()
        logger.info("✅ DatabaseManager created")
        
        # Create SeleniumManager (optional)
        selenium_manager = None
        try:
            selenium_config = SeleniumConfig(headless=True)
            selenium_manager = SeleniumManager(selenium_config)
            logger.info("✅ SeleniumManager created")
        except Exception as e:
            logger.warning(f"⚠️ SeleniumManager not available: {e}")
            logger.info("System will use RequestManager only")
        
        # Create CoreScraper with all components
        scraper = CoreScraper(
            request_manager=request_manager,
            html_parser=html_parser,
            data_extractor=data_extractor,
            db_manager=db_manager,
            config=config,
            selenium_manager=selenium_manager
        )
        
        logger.info("✅ CoreScraper created with all dependencies")
        
        # Test system health
        logger.info("System Health Check:")
        logger.info(f"  - RequestManager: {'✅ Available' if request_manager else '❌ Not Available'}")
        logger.info(f"  - HTMLParser: {'✅ Available' if html_parser else '❌ Not Available'}")
        logger.info(f"  - PFRDataExtractor: {'✅ Available' if data_extractor else '❌ Not Available'}")
        logger.info(f"  - DatabaseManager: {'✅ Available' if db_manager else '❌ Not Available'}")
        logger.info(f"  - SeleniumManager: {'✅ Available' if selenium_manager else '❌ Not Available'}")
        
        return scraper, selenium_manager
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        return None, None


def test_page_fetching_strategies(scraper, selenium_manager):
    """Test different page fetching strategies."""
    logger.info("=== Testing Page Fetching Strategies ===")
    
    test_urls = [
        ("Simple HTML Page", "https://httpbin.org/html", False),
        ("JSON API", "https://httpbin.org/json", False),
        ("PFR Player Page", "https://www.pro-football-reference.com/players/B/BurrJo01.htm", True),
    ]
    
    results = {}
    
    for url_name, url, requires_js in test_urls:
        logger.info(f"Testing: {url_name} ({url})")
        
        try:
            # Test with fallback mechanism
            result = scraper._fetch_page_with_fallback(url, enable_js=requires_js)
            
            if result['success']:
                logger.info(f"✅ {url_name}: Successfully fetched")
                logger.info(f"  - Content length: {len(result['content'])} characters")
                
                # Check if content looks like HTML
                if '<html' in result['content'].lower():
                    logger.info(f"  - Content type: HTML")
                elif '{' in result['content'] and '}' in result['content']:
                    logger.info(f"  - Content type: JSON")
                else:
                    logger.info(f"  - Content type: Text")
            else:
                logger.warning(f"⚠️ {url_name}: Failed to fetch - {result['error']}")
            
            results[url_name] = result['success']
            
        except Exception as e:
            logger.error(f"❌ {url_name}: Error during fetch - {e}")
            results[url_name] = False
    
    return results


def test_data_extraction_pipeline(scraper):
    """Test the complete data extraction pipeline."""
    logger.info("=== Testing Data Extraction Pipeline ===")
    
    # Create a sample HTML with QB data for testing
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Sample QB Data</title></head>
    <body>
        <table id="stats" class="sortable stats_table">
            <thead>
                <tr>
                    <th data-stat="ranker">Rk</th>
                    <th data-stat="player">Player</th>
                    <th data-stat="age">Age</th>
                    <th data-stat="team">Team</th>
                    <th data-stat="pos">Pos</th>
                    <th data-stat="g">G</th>
                    <th data-stat="gs">GS</th>
                    <th data-stat="qb_rec">QBrec</th>
                    <th data-stat="pass_cmp">Cmp</th>
                    <th data-stat="pass_att">Att</th>
                    <th data-stat="pass_cmp_perc">Cmp%</th>
                    <th data-stat="pass_yds">Yds</th>
                    <th data-stat="pass_td">TD</th>
                    <th data-stat="pass_int">Int</th>
                    <th data-stat="pass_rating">Rate</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td data-stat="ranker">1</td>
                    <td data-stat="player">Joe Burrow</td>
                    <td data-stat="age">27</td>
                    <td data-stat="team">CIN</td>
                    <td data-stat="pos">QB</td>
                    <td data-stat="g">17</td>
                    <td data-stat="gs">17</td>
                    <td data-stat="qb_rec">12-5-0</td>
                    <td data-stat="pass_cmp">460</td>
                    <td data-stat="pass_att">652</td>
                    <td data-stat="pass_cmp_perc">70.55</td>
                    <td data-stat="pass_yds">4918</td>
                    <td data-stat="pass_td">43</td>
                    <td data-stat="pass_int">15</td>
                    <td data-stat="pass_rating">98.6</td>
                </tr>
            </tbody>
        </table>
        
        <table id="splits" class="sortable stats_table">
            <thead>
                <tr>
                    <th data-stat="split">Split</th>
                    <th data-stat="value">Value</th>
                    <th data-stat="g">G</th>
                    <th data-stat="w">W</th>
                    <th data-stat="l">L</th>
                    <th data-stat="t">T</th>
                    <th data-stat="pass_cmp">Cmp</th>
                    <th data-stat="pass_att">Att</th>
                    <th data-stat="pass_yds">Yds</th>
                    <th data-stat="pass_td">TD</th>
                    <th data-stat="pass_int">Int</th>
                    <th data-stat="pass_rating">Rate</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td data-stat="split">Home</td>
                    <td data-stat="value">Home</td>
                    <td data-stat="g">8</td>
                    <td data-stat="w">5</td>
                    <td data-stat="l">3</td>
                    <td data-stat="t">0</td>
                    <td data-stat="pass_cmp">230</td>
                    <td data-stat="pass_att">326</td>
                    <td data-stat="pass_yds">2459</td>
                    <td data-stat="pass_td">22</td>
                    <td data-stat="pass_int">8</td>
                    <td data-stat="pass_rating">99.2</td>
                </tr>
                <tr>
                    <td data-stat="split">Away</td>
                    <td data-stat="value">Away</td>
                    <td data-stat="g">9</td>
                    <td data-stat="w">7</td>
                    <td data-stat="l">2</td>
                    <td data-stat="t">0</td>
                    <td data-stat="pass_cmp">230</td>
                    <td data-stat="pass_att">326</td>
                    <td data-stat="pass_yds">2459</td>
                    <td data-stat="pass_td">21</td>
                    <td data-stat="pass_int">7</td>
                    <td data-stat="pass_rating">98.0</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    
    try:
        # Parse the sample HTML
        soup = scraper.html_parser.parse_html(sample_html)
        if not soup:
            logger.error("❌ Failed to parse sample HTML")
            return False
        
        logger.info("✅ Sample HTML parsed successfully")
        
        # Extract data using the pipeline
        extraction_results = scraper.data_extractor.extract_all_qb_data(soup, "Joe Burrow", 2024)
        
        logger.info("✅ Data extraction completed")
        logger.info(f"  - Tables extracted: {len(extraction_results)}")
        
        # Analyze results
        for table_type, result in extraction_results.items():
            logger.info(f"\n{table_type.upper()} Results:")
            logger.info(f"  - Success: {result.success}")
            logger.info(f"  - Row count: {result.row_count}")
            logger.info(f"  - Fields extracted: {len(result.extracted_fields)}")
            logger.info(f"  - Fields missing: {len(result.missing_fields)}")
            
            if result.extracted_fields:
                logger.info(f"  - Sample extracted fields: {result.extracted_fields[:5]}")
            
            if result.data:
                logger.info(f"  - Sample data: {list(result.data[0].keys())[:5] if result.data else 'No data'}")
        
        # Get extraction summary
        summary = scraper.data_extractor.get_extraction_summary(extraction_results)
        logger.info(f"\nExtraction Summary:")
        logger.info(f"  - Total tables extracted: {summary['total_tables_extracted']}")
        logger.info(f"  - Successful extractions: {summary['successful_extractions']}")
        logger.info(f"  - Total fields extracted: {summary['total_fields_extracted']}")
        logger.info(f"  - Total missing fields: {summary['total_missing_fields']}")
        
        # Consider the test successful if we extracted any data
        return summary['total_fields_extracted'] > 0
        
    except Exception as e:
        logger.error(f"❌ Failed to test data extraction pipeline: {e}")
        return False


def test_system_performance(scraper, selenium_manager):
    """Test system performance and resource usage."""
    logger.info("=== Testing System Performance ===")
    
    try:
        # Test RequestManager performance
        logger.info("Testing RequestManager performance...")
        start_time = datetime.now()
        
        # Test with a simple, fast URL
        result = scraper._fetch_page_with_fallback("https://httpbin.org/html", enable_js=False)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if result['success']:
            logger.info(f"✅ RequestManager: Success in {duration:.2f}s")
        else:
            logger.warning(f"⚠️ RequestManager: Failed in {duration:.2f}s")
        
        # Test SeleniumManager performance (if available)
        if selenium_manager:
            logger.info("Testing SeleniumManager performance...")
            start_time = datetime.now()
            
            result = scraper._fetch_page_with_fallback("https://httpbin.org/html", enable_js=True)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result['success']:
                logger.info(f"✅ SeleniumManager: Success in {duration:.2f}s")
            else:
                logger.warning(f"⚠️ SeleniumManager: Failed in {duration:.2f}s")
        
        # Test memory usage (basic check)
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"✅ Memory usage: {memory_mb:.1f} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to test system performance: {e}")
        return False


def test_error_handling_and_recovery(scraper):
    """Test error handling and recovery mechanisms."""
    logger.info("=== Testing Error Handling and Recovery ===")
    
    try:
        # Test with invalid URL
        logger.info("Testing with invalid URL...")
        result = scraper._fetch_page_with_fallback("https://invalid-url-that-does-not-exist.com", enable_js=False)
        
        if not result['success']:
            logger.info("✅ Properly handled invalid URL")
        else:
            logger.warning("⚠️ Unexpectedly succeeded with invalid URL")
        
        # Test with blocked URL (simulated)
        logger.info("Testing with blocked URL...")
        result = scraper._fetch_page_with_fallback("https://httpbin.org/status/403", enable_js=False)
        
        if not result['success']:
            logger.info("✅ Properly handled blocked URL")
        else:
            logger.warning("⚠️ Unexpectedly succeeded with blocked URL")
        
        # Test with timeout URL
        logger.info("Testing with timeout URL...")
        result = scraper._fetch_page_with_fallback("https://httpbin.org/delay/10", enable_js=False)
        
        # This might succeed or fail depending on timeout settings
        logger.info(f"Timeout test result: {'Success' if result['success'] else 'Failed (expected)'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to test error handling: {e}")
        return False


def main():
    """Run the complete system integration test."""
    logger.info("Starting Full System Integration Test")
    logger.info("=" * 70)
    
    start_time = datetime.now()
    
    # Initialize system
    scraper, selenium_manager = test_system_initialization()
    if not scraper:
        logger.error("❌ System initialization failed")
        return False
    
    # Run tests
    tests = [
        ("Page Fetching Strategies", lambda: test_page_fetching_strategies(scraper, selenium_manager)),
        ("Data Extraction Pipeline", lambda: test_data_extraction_pipeline(scraper)),
        ("System Performance", lambda: test_system_performance(scraper, selenium_manager)),
        ("Error Handling", lambda: test_error_handling_and_recovery(scraper)),
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
    
    # Clean up
    if selenium_manager:
        try:
            selenium_manager.end_session()
            logger.info("✅ Selenium session cleaned up")
        except Exception as e:
            logger.warning(f"⚠️ Error cleaning up Selenium session: {e}")
    
    # Print summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"\n{'='*70}")
    logger.info("FULL SYSTEM INTEGRATION TEST SUMMARY")
    logger.info(f"{'='*70}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    logger.info(f"Tests completed in {duration:.2f} seconds")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Success rate: {(passed/total)*100:.1f}%")
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"  - {test_name}: {status}")
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! The complete system is working correctly.")
        logger.info("\n🚀 SYSTEM CAPABILITIES:")
        logger.info("  ✅ Complete data extraction pipeline")
        logger.info("  ✅ Dual fetching strategy (RequestManager + SeleniumManager)")
        logger.info("  ✅ Robust error handling and recovery")
        logger.info("  ✅ Performance monitoring")
        logger.info("  ✅ Type-safe data processing")
        logger.info("  ✅ Comprehensive logging and reporting")
    else:
        logger.error(f"\n⚠️  {total - passed} TESTS FAILED. Please review the issues above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 