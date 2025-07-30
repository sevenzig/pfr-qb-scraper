#!/usr/bin/env python3
"""
Integration Test for Enhanced QB Splits Extraction
Quick validation of enhanced splits extraction functionality
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.enhanced_scraper import EnhancedPFRScraper
from src.core.splits_manager import SplitsManager
from src.core.request_manager import RequestManager
from src.utils.data_utils import build_enhanced_splits_url, validate_splits_url
from src.config.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_enhanced_components():
    """Test enhanced components initialization and basic functionality"""
    logger.info("=" * 60)
    logger.info("TESTING ENHANCED COMPONENTS")
    logger.info("=" * 60)
    
    test_results = []
    
    # Test 1: Enhanced URL Construction
    try:
        logger.info("Testing enhanced URL construction...")
        
        test_cases = [
            ("BurrJo00", 2024),
            ("MahomPa00", 2024),
            ("AlleJo00", 2024),
        ]
        
        for pfr_id, season in test_cases:
            url = build_enhanced_splits_url(pfr_id, season)
            assert url is not None, f"URL construction failed for {pfr_id}"
            
            is_valid = validate_splits_url(url)
            assert is_valid, f"URL validation failed for {pfr_id}"
            
            logger.info(f"  ✓ {pfr_id}: {url}")
        
        test_results.append(("URL Construction", True))
        logger.info("✓ Enhanced URL construction test PASSED")
        
    except Exception as e:
        logger.error(f"✗ Enhanced URL construction test FAILED: {e}")
        test_results.append(("URL Construction", False))
    
    # Test 2: Request Manager
    try:
        logger.info("Testing request manager initialization...")
        
        request_manager = RequestManager(
            rate_limit_delay=config.scraping.rate_limit_delay,
            jitter_range=config.scraping.jitter_range
        )
        
        assert request_manager is not None
        assert hasattr(request_manager, 'get')
        logger.info("  ✓ Request manager initialized successfully")
        
        test_results.append(("Request Manager", True))
        logger.info("✓ Request manager test PASSED")
        
    except Exception as e:
        logger.error(f"✗ Request manager test FAILED: {e}")
        test_results.append(("Request Manager", False))
    
    # Test 3: Splits Manager
    try:
        logger.info("Testing splits manager initialization...")
        
        request_manager = RequestManager(
            rate_limit_delay=config.scraping.rate_limit_delay,
            jitter_range=config.scraping.jitter_range
        )
        
        splits_manager = SplitsManager(request_manager)
        
        assert splits_manager is not None
        assert splits_manager.splits_extractor is not None
        logger.info("  ✓ Splits manager initialized successfully")
        
        # Test URL construction testing
        test_results_url = splits_manager.test_splits_url_construction("BurrJo00", 2024)
        assert isinstance(test_results_url, dict)
        assert 'pfr_id' in test_results_url
        logger.info("  ✓ URL construction testing verified")
        
        # Test summary generation
        summary = splits_manager.get_extraction_summary()
        assert isinstance(summary, dict)
        assert 'session_id' in summary
        logger.info("  ✓ Summary generation verified")
        
        test_results.append(("Splits Manager", True))
        logger.info("✓ Splits manager test PASSED")
        
    except Exception as e:
        logger.error(f"✗ Splits manager test FAILED: {e}")
        test_results.append(("Splits Manager", False))
    
    # Test 4: Enhanced Scraper
    try:
        logger.info("Testing enhanced scraper initialization...")
        
        enhanced_scraper = EnhancedPFRScraper(rate_limit_delay=config.scraping.rate_limit_delay)
        
        assert enhanced_scraper is not None
        assert enhanced_scraper.base_url == "https://www.pro-football-reference.com"
        assert enhanced_scraper.splits_manager is not None
        logger.info("  ✓ Enhanced scraper initialized successfully")
        
        # Test metrics tracking
        assert hasattr(enhanced_scraper, 'metrics')
        assert enhanced_scraper.metrics is not None
        logger.info("  ✓ Metrics tracking initialized")
        
        test_results.append(("Enhanced Scraper", True))
        logger.info("✓ Enhanced scraper test PASSED")
        
    except Exception as e:
        logger.error(f"✗ Enhanced scraper test FAILED: {e}")
        test_results.append(("Enhanced Scraper", False))
    
    return test_results


def test_data_models():
    """Test data model compatibility"""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING DATA MODELS")
    logger.info("=" * 60)
    
    test_results = []
    
    try:
        # Test QBSplitsType1 model
        from src.models.qb_models import QBSplitsType1
        
        # Create a sample splits object
        sample_split = QBSplitsType1(
            pfr_id="BurrJo00",
            player_name="Joe Burrow",
            season=2024,
            split="home_away",
            value="Home",
            g=8,
            w=6,
            l=2,
            t=0,
            cmp=200,
            att=300,
            inc=100,
            cmp_pct=66.7,
            yds=2500,
            td=20,
            int=5,
            rate=95.5,
            sk=15,
            sk_yds=120,
            y_a=8.3,
            ay_a=8.5,
            a_g=37.5,
            y_g=312.5,
            rush_att=30,
            rush_yds=150,
            rush_y_a=5.0,
            rush_td=2,
            rush_a_g=3.8,
            rush_y_g=18.8,
            total_td=22,
            pts=132,
            fmb=3,
            fl=1,
            ff=0,
            fr=0,
            fr_yds=0,
            fr_td=0,
            scraped_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Validate the object
        errors = sample_split.validate()
        assert len(errors) == 0, f"Validation errors: {errors}"
        
        logger.info("  ✓ QBSplitsType1 model test PASSED")
        test_results.append(("QBSplitsType1 Model", True))
        
    except Exception as e:
        logger.error(f"✗ QBSplitsType1 model test FAILED: {e}")
        test_results.append(("QBSplitsType1 Model", False))
    
    try:
        # Test QBSplitsType2 model
        from src.models.qb_models import QBSplitsType2
        
        # Create a sample advanced splits object
        sample_advanced_split = QBSplitsType2(
            pfr_id="BurrJo00",
            player_name="Joe Burrow",
            season=2024,
            split="down",
            value="1st Down",
            cmp=100,
            att=150,
            inc=50,
            cmp_pct=66.7,
            yds=1200,
            td=8,
            first_downs=45,
            int=2,
            rate=92.5,
            sk=8,
            sk_yds=60,
            y_a=8.0,
            ay_a=8.2,
            rush_att=15,
            rush_yds=75,
            rush_y_a=5.0,
            rush_td=1,
            rush_first_downs=8,
            scraped_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Validate the object
        errors = sample_advanced_split.validate()
        assert len(errors) == 0, f"Validation errors: {errors}"
        
        logger.info("  ✓ QBSplitsType2 model test PASSED")
        test_results.append(("QBSplitsType2 Model", True))
        
    except Exception as e:
        logger.error(f"✗ QBSplitsType2 model test FAILED: {e}")
        test_results.append(("QBSplitsType2 Model", False))
    
    return test_results


def test_configuration():
    """Test configuration compatibility"""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING CONFIGURATION")
    logger.info("=" * 60)
    
    test_results = []
    
    try:
        # Test configuration loading
        assert config is not None
        assert hasattr(config, 'scraping')
        assert hasattr(config, 'app')
        
        # Test scraping configuration
        assert config.scraping.rate_limit_delay >= 7.0, "Rate limit delay too low"
        assert config.scraping.max_workers >= 1, "Max workers too low"
        
        logger.info(f"  ✓ Rate limit delay: {config.scraping.rate_limit_delay}s")
        logger.info(f"  ✓ Max workers: {config.scraping.max_workers}")
        logger.info(f"  ✓ Jitter range: {config.scraping.jitter_range}s")
        
        test_results.append(("Configuration", True))
        logger.info("✓ Configuration test PASSED")
        
    except Exception as e:
        logger.error(f"✗ Configuration test FAILED: {e}")
        test_results.append(("Configuration", False))
    
    return test_results


def main():
    """Main integration test function"""
    logger.info("ENHANCED SPLITS EXTRACTION INTEGRATION TEST")
    logger.info("Quick validation of enhanced functionality")
    
    start_time = datetime.now()
    
    # Run all tests
    all_results = []
    
    # Test enhanced components
    component_results = test_enhanced_components()
    all_results.extend(component_results)
    
    # Test data models
    model_results = test_data_models()
    all_results.extend(model_results)
    
    # Test configuration
    config_results = test_configuration()
    all_results.extend(config_results)
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("INTEGRATION TEST SUMMARY")
    logger.info("=" * 80)
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, success in all_results if success)
    failed_tests = total_tests - passed_tests
    
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {failed_tests}")
    logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    logger.info("\nDetailed Results:")
    for test_name, success in all_results:
        status = "PASS" if success else "FAIL"
        logger.info(f"  {test_name}: {status}")
    
    # Performance metrics
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    logger.info(f"\nTotal Test Time: {total_time:.2f} seconds")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 ALL INTEGRATION TESTS PASSED!")
        logger.info("Enhanced splits extraction is ready for use.")
        return 0
    else:
        logger.error(f"\n❌ {failed_tests} test(s) failed.")
        logger.error("Please review the errors above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 