#!/usr/bin/env python3
"""
Enhanced Splits Validation Script
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


def validate_enhanced_components():
    """Validate enhanced components"""
    logger.info("=" * 60)
    logger.info("VALIDATING ENHANCED COMPONENTS")
    logger.info("=" * 60)
    
    # Test 1: Enhanced URL Construction
    logger.info("Testing enhanced URL construction...")
    test_cases = [
        ("BurrJo00", 2024, "Joe Burrow"),
        ("MahomPa00", 2024, "Patrick Mahomes"),
        ("AlleJo00", 2024, "Josh Allen"),
    ]
    
    for pfr_id, season, player_name in test_cases:
        try:
            url = build_enhanced_splits_url(pfr_id, season)
            assert url is not None, f"URL construction failed for {player_name}"
            
            is_valid = validate_splits_url(url)
            assert is_valid, f"URL validation failed for {player_name}"
            
            logger.info(f"  ✓ {player_name}: {url}")
        except Exception as e:
            logger.error(f"  ✗ {player_name}: {e}")
            return False
    
    logger.info("✓ Enhanced URL construction validation PASSED")
    
    # Test 2: Request Manager
    logger.info("Testing request manager...")
    try:
        request_manager = RequestManager(
            rate_limit_delay=config.scraping.rate_limit_delay,
            jitter_range=config.scraping.jitter_range
        )
        assert request_manager is not None
        assert hasattr(request_manager, 'get')
        logger.info("  ✓ Request manager initialized successfully")
    except Exception as e:
        logger.error(f"  ✗ Request manager failed: {e}")
        return False
    
    # Test 3: Splits Manager
    logger.info("Testing splits manager...")
    try:
        request_manager = RequestManager(
            rate_limit_delay=config.scraping.rate_limit_delay,
            jitter_range=config.scraping.jitter_range
        )
        splits_manager = SplitsManager(request_manager)
        
        assert splits_manager is not None
        assert splits_manager.splits_extractor is not None
        
        # Test URL construction testing
        test_results = splits_manager.test_splits_url_construction("BurrJo00", 2024)
        assert isinstance(test_results, dict)
        assert 'pfr_id' in test_results
        
        # Test summary generation
        summary = splits_manager.get_extraction_summary()
        assert isinstance(summary, dict)
        assert 'session_id' in summary
        
        logger.info("  ✓ Splits manager initialized successfully")
    except Exception as e:
        logger.error(f"  ✗ Splits manager failed: {e}")
        return False
    
    # Test 4: Enhanced Scraper
    logger.info("Testing enhanced scraper...")
    try:
        enhanced_scraper = EnhancedPFRScraper(rate_limit_delay=config.scraping.rate_limit_delay)
        
        assert enhanced_scraper is not None
        assert enhanced_scraper.base_url == "https://www.pro-football-reference.com"
        assert enhanced_scraper.splits_manager is not None
        
        # Test metrics tracking
        assert hasattr(enhanced_scraper, 'metrics')
        assert enhanced_scraper.metrics is not None
        
        logger.info("  ✓ Enhanced scraper initialized successfully")
    except Exception as e:
        logger.error(f"  ✗ Enhanced scraper failed: {e}")
        return False
    
    return True


def validate_data_models():
    """Validate data models"""
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATING DATA MODELS")
    logger.info("=" * 60)
    
    # Test QBSplitsType1 model
    try:
        from src.models.qb_models import QBSplitsType1
        
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
        
        errors = sample_split.validate()
        assert len(errors) == 0, f"Validation errors: {errors}"
        
        logger.info("  ✓ QBSplitsType1 model validation PASSED")
    except Exception as e:
        logger.error(f"  ✗ QBSplitsType1 model validation failed: {e}")
        return False
    
    # Test QBSplitsType2 model
    try:
        from src.models.qb_models import QBSplitsType2
        
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
        
        errors = sample_advanced_split.validate()
        assert len(errors) == 0, f"Validation errors: {errors}"
        
        logger.info("  ✓ QBSplitsType2 model validation PASSED")
    except Exception as e:
        logger.error(f"  ✗ QBSplitsType2 model validation failed: {e}")
        return False
    
    return True


def validate_configuration():
    """Validate configuration"""
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATING CONFIGURATION")
    logger.info("=" * 60)
    
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
        
        logger.info("  ✓ Configuration validation PASSED")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Configuration validation failed: {e}")
        return False


def main():
    """Main validation function"""
    logger.info("ENHANCED SPLITS EXTRACTION VALIDATION")
    logger.info("Validating enhanced functionality")
    
    start_time = datetime.now()
    
    # Run all validations
    validations = [
        ("Enhanced Components", validate_enhanced_components),
        ("Data Models", validate_data_models),
        ("Configuration", validate_configuration),
    ]
    
    all_passed = True
    
    for validation_name, validation_func in validations:
        try:
            if not validation_func():
                all_passed = False
        except Exception as e:
            logger.error(f"Validation '{validation_name}' failed with exception: {e}")
            all_passed = False
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 80)
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    logger.info(f"Total Validation Time: {total_time:.2f} seconds")
    
    if all_passed:
        logger.info("\n🎉 ALL VALIDATIONS PASSED!")
        logger.info("Enhanced splits extraction is ready for use.")
        return 0
    else:
        logger.error("\n❌ Some validations failed.")
        logger.error("Please review the errors above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 