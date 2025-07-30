#!/usr/bin/env python3
"""
Test script for enhanced splits extraction functionality
Comprehensive testing of URL construction, table discovery, and data extraction
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.splits_extractor import SplitsExtractor, SplitsExtractionResult
from src.core.splits_manager import SplitsManager
from src.core.request_manager import RequestManager
from src.config.config import config
from src.utils.data_utils import build_enhanced_splits_url, validate_splits_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_url_construction():
    """Test enhanced URL construction functionality"""
    logger.info("=" * 60)
    logger.info("TESTING URL CONSTRUCTION")
    logger.info("=" * 60)
    
    test_cases = [
        ("BurrJo00", 2024, "Joe Burrow"),
        ("MahomPa00", 2024, "Patrick Mahomes"),
        ("AlleJo00", 2024, "Josh Allen"),
        ("HerbJu00", 2024, "Justin Herbert"),
    ]
    
    for pfr_id, season, player_name in test_cases:
        logger.info(f"\nTesting URL construction for {player_name} ({pfr_id})")
        
        try:
            # Test enhanced URL construction
            url = build_enhanced_splits_url(pfr_id, season)
            if url:
                logger.info(f"  ✓ Built URL: {url}")
                
                # Test URL validation
                is_valid = validate_splits_url(url)
                logger.info(f"  ✓ URL validation: {'PASS' if is_valid else 'FAIL'}")
                
                if is_valid:
                    logger.info(f"  ✓ URL construction test PASSED for {player_name}")
                else:
                    logger.error(f"  ✗ URL validation FAILED for {player_name}")
            else:
                logger.error(f"  ✗ URL construction FAILED for {player_name}")
                
        except Exception as e:
            logger.error(f"  ✗ URL construction ERROR for {player_name}: {str(e)}")


def test_splits_extractor():
    """Test the dedicated splits extractor"""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING SPLITS EXTRACTOR")
    logger.info("=" * 60)
    
    # Initialize components
    request_manager = RequestManager(
        rate_limit_delay=config.scraping.rate_limit_delay,
        jitter_range=config.scraping.jitter_range
    )
    
    splits_extractor = SplitsExtractor(request_manager)
    
    # Test with Joe Burrow (known to have splits data)
    pfr_id = "BurrJo00"
    player_name = "Joe Burrow"
    season = 2024
    
    logger.info(f"Testing splits extraction for {player_name}")
    
    try:
        # Extract splits
        result = splits_extractor.extract_player_splits(
            pfr_id, player_name, season, datetime.now()
        )
        
        # Log results
        logger.info(f"  Extraction completed in {result.extraction_time:.2f}s")
        logger.info(f"  Tables discovered: {result.tables_discovered}")
        logger.info(f"  Tables processed: {result.tables_processed}")
        logger.info(f"  Basic splits extracted: {len(result.basic_splits)}")
        logger.info(f"  Advanced splits extracted: {len(result.advanced_splits)}")
        
        if result.errors:
            logger.error("  Errors encountered:")
            for error in result.errors:
                logger.error(f"    - {error}")
        
        if result.warnings:
            logger.warning("  Warnings:")
            for warning in result.warnings:
                logger.warning(f"    - {warning}")
        
        # Validate extraction result
        validation_errors = splits_extractor.validate_extraction_result(result)
        if validation_errors:
            logger.error("  Validation errors:")
            for error in validation_errors:
                logger.error(f"    - {error}")
        else:
            logger.info("  ✓ Extraction validation PASSED")
        
        # Check for required columns
        if result.basic_splits:
            sample_basic = result.basic_splits[0]
            basic_columns = [
                'g', 'w', 'l', 't', 'cmp', 'att', 'inc', 'cmp_pct', 'yds', 'td',
                'int', 'rate', 'sk', 'sk_yds', 'y_a', 'ay_a', 'a_g', 'y_g',
                'rush_att', 'rush_yds', 'rush_y_a', 'rush_td', 'rush_a_g', 'rush_y_g',
                'total_td', 'pts', 'fmb', 'fl', 'ff', 'fr', 'fr_yds', 'fr_td'
            ]
            missing_basic = [col for col in basic_columns if getattr(sample_basic, col, None) is None]
            if missing_basic:
                logger.warning(f"  Missing basic splits columns: {missing_basic}")
            else:
                logger.info("  ✓ All 34 basic splits columns present")
        
        if result.advanced_splits:
            sample_advanced = result.advanced_splits[0]
            advanced_columns = [
                'cmp', 'att', 'inc', 'cmp_pct', 'yds', 'td', 'first_downs',
                'int', 'rate', 'sk', 'sk_yds', 'y_a', 'ay_a',
                'rush_att', 'rush_yds', 'rush_y_a', 'rush_td', 'rush_first_downs'
            ]
            missing_advanced = [col for col in advanced_columns if getattr(sample_advanced, col, None) is None]
            if missing_advanced:
                logger.warning(f"  Missing advanced splits columns: {missing_advanced}")
            else:
                logger.info("  ✓ All 20 advanced splits columns present")
        
        # Log sample data
        if result.basic_splits:
            logger.info("  Sample basic split:")
            sample = result.basic_splits[0]
            logger.info(f"    Split: {sample.split}")
            logger.info(f"    Value: {sample.value}")
            logger.info(f"    Games: {sample.g}")
            logger.info(f"    Completions: {sample.cmp}")
            logger.info(f"    Attempts: {sample.att}")
            logger.info(f"    Yards: {sample.yds}")
            logger.info(f"    TDs: {sample.td}")
        
        if result.advanced_splits:
            logger.info("  Sample advanced split:")
            sample = result.advanced_splits[0]
            logger.info(f"    Split: {sample.split}")
            logger.info(f"    Value: {sample.value}")
            logger.info(f"    Completions: {sample.cmp}")
            logger.info(f"    Attempts: {sample.att}")
            logger.info(f"    First Downs: {sample.first_downs}")
            logger.info(f"    Yards: {sample.yds}")
            logger.info(f"    TDs: {sample.td}")
        
        return len(result.basic_splits) > 0 or len(result.advanced_splits) > 0
        
    except Exception as e:
        logger.error(f"  ✗ Splits extraction ERROR: {str(e)}", exc_info=True)
        return False


def test_splits_manager():
    """Test the splits manager functionality"""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING SPLITS MANAGER")
    logger.info("=" * 60)
    
    # Initialize components
    request_manager = RequestManager(
        rate_limit_delay=config.scraping.rate_limit_delay,
        jitter_range=config.scraping.jitter_range
    )
    
    splits_manager = SplitsManager(request_manager)
    
    # Test URL construction
    pfr_id = "BurrJo00"
    season = 2024
    
    logger.info(f"Testing splits manager URL construction for PFR ID: {pfr_id}")
    
    try:
        test_results = splits_manager.test_splits_url_construction(pfr_id, season)
        
        logger.info("  URL Construction Test Results:")
        logger.info(f"    PFR ID: {test_results['pfr_id']}")
        logger.info(f"    Season: {test_results['season']}")
        
        if test_results['urls_tested']:
            logger.info("    URLs Tested:")
            for method, url in test_results['urls_tested']:
                logger.info(f"      {method}: {url}")
        
        if test_results['valid_urls']:
            logger.info("    Valid URLs:")
            for method, url in test_results['valid_urls']:
                logger.info(f"      {method}: {url}")
        
        if test_results['errors']:
            logger.error("    Errors:")
            for error in test_results['errors']:
                logger.error(f"      {error}")
        
        # Test single player extraction
        logger.info(f"\nTesting single player extraction for Joe Burrow")
        result = splits_manager.extract_player_splits_by_name("Joe Burrow", pfr_id, season)
        
        logger.info(f"  Single Player Extraction Results:")
        logger.info(f"    Basic Splits: {len(result.basic_splits)}")
        logger.info(f"    Advanced Splits: {len(result.advanced_splits)}")
        logger.info(f"    Tables Discovered: {result.tables_discovered}")
        logger.info(f"    Tables Processed: {result.tables_processed}")
        logger.info(f"    Extraction Time: {result.extraction_time:.2f}s")
        
        if result.errors:
            logger.error("    Errors:")
            for error in result.errors:
                logger.error(f"      {error}")
        
        # Get extraction summary
        summary = splits_manager.get_extraction_summary()
        logger.info(f"  Extraction Summary:")
        logger.info(f"    Session ID: {summary['session_id']}")
        logger.info(f"    Processing Time: {summary['processing_time_seconds']:.2f}s")
        logger.info(f"    Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"    Total Basic Splits: {summary['total_basic_splits']}")
        logger.info(f"    Total Advanced Splits: {summary['total_advanced_splits']}")
        logger.info(f"    Total Errors: {summary['total_errors']}")
        logger.info(f"    Total Warnings: {summary['total_warnings']}")
        
        return len(result.basic_splits) > 0 or len(result.advanced_splits) > 0
        
    except Exception as e:
        logger.error(f"  ✗ Splits manager ERROR: {str(e)}", exc_info=True)
        return False


def main():
    """Main test function"""
    logger.info("ENHANCED SPLITS EXTRACTION TEST SUITE")
    logger.info("Testing comprehensive QB splits extraction functionality")
    
    # Track test results
    test_results = []
    
    # Test 1: URL Construction
    try:
        test_url_construction()
        test_results.append(("URL Construction", True))
        logger.info("✓ URL Construction test completed")
    except Exception as e:
        logger.error(f"✗ URL Construction test failed: {str(e)}")
        test_results.append(("URL Construction", False))
    
    # Test 2: Splits Extractor
    try:
        extractor_success = test_splits_extractor()
        test_results.append(("Splits Extractor", extractor_success))
        if extractor_success:
            logger.info("✓ Splits Extractor test PASSED")
        else:
            logger.error("✗ Splits Extractor test FAILED")
    except Exception as e:
        logger.error(f"✗ Splits Extractor test failed: {str(e)}")
        test_results.append(("Splits Extractor", False))
    
    # Test 3: Splits Manager
    try:
        manager_success = test_splits_manager()
        test_results.append(("Splits Manager", manager_success))
        if manager_success:
            logger.info("✓ Splits Manager test PASSED")
        else:
            logger.error("✗ Splits Manager test FAILED")
    except Exception as e:
        logger.error(f"✗ Splits Manager test failed: {str(e)}")
        test_results.append(("Splits Manager", False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "PASS" if success else "FAIL"
        logger.info(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    logger.info(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Enhanced splits extraction is working correctly.")
        return 0
    else:
        logger.error(f"❌ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 