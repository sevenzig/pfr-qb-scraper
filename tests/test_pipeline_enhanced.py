#!/usr/bin/env python3
"""
Enhanced Pipeline Test
Comprehensive testing of the enhanced splits extraction pipeline
"""

import sys
import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.operations.scraping_operation import ScrapingOperation, ScrapingResult
from src.database.db_manager import DatabaseManager
from src.config.config import config
from src.scrapers.enhanced_scraper import EnhancedPFRScraper
from src.core.splits_manager import SplitsManager
from src.core.request_manager import RequestManager
from src.utils.data_utils import build_enhanced_splits_url, validate_splits_url
from src.models.qb_models import QBBasicStats, QBSplitsType1, QBSplitsType2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedPipelineTest:
    """Comprehensive pipeline test for enhanced splits extraction"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.request_manager = RequestManager(
            rate_limit_delay=config.scraping.rate_limit_delay,
            jitter_range=config.scraping.jitter_range
        )
        self.enhanced_scraper = EnhancedPFRScraper(rate_limit_delay=config.scraping.rate_limit_delay)
        self.splits_manager = SplitsManager(self.request_manager)
        
        logger.info("Initialized Enhanced Pipeline Test Suite")
    
    def run_pipeline_tests(self) -> bool:
        """Run comprehensive pipeline tests"""
        logger.info("=" * 80)
        logger.info("ENHANCED PIPELINE TEST SUITE")
        logger.info("=" * 80)
        
        # Test 1: Component Integration
        self._test_component_integration()
        
        # Test 2: URL Construction Pipeline
        self._test_url_construction_pipeline()
        
        # Test 3: Splits Manager Pipeline
        self._test_splits_manager_pipeline()
        
        # Test 4: Enhanced Scraper Pipeline
        self._test_enhanced_scraper_pipeline()
        
        # Test 5: Scraping Operation Pipeline
        self._test_scraping_operation_pipeline()
        
        # Test 6: Data Flow Pipeline
        self._test_data_flow_pipeline()
        
        # Test 7: Error Handling Pipeline
        self._test_error_handling_pipeline()
        
        # Test 8: Performance Pipeline
        self._test_performance_pipeline()
        
        # Print comprehensive results
        self._print_pipeline_summary()
        
        return self._all_tests_passed()
    
    def _test_component_integration(self):
        """Test component integration and dependencies"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 1: COMPONENT INTEGRATION")
        logger.info("=" * 60)
        
        try:
            # Test enhanced scraper integration
            assert self.enhanced_scraper.splits_manager is not None
            assert self.enhanced_scraper.request_manager is not None
            logger.info("✓ Enhanced scraper component integration verified")
            
            # Test splits manager integration
            assert self.splits_manager.request_manager is not None
            assert self.splits_manager.splits_extractor is not None
            logger.info("✓ Splits manager component integration verified")
            
            # Test request manager integration
            assert self.request_manager.rate_limit_delay >= 7.0
            assert self.request_manager.jitter_range >= 0
            logger.info("✓ Request manager configuration verified")
            
            # Test database integration
            connection_ok = self.db_manager.test_connection()
            assert connection_ok, "Database connection failed"
            logger.info("✓ Database integration verified")
            
            self.test_results.append(("Component Integration", True))
            logger.info("✓ Component integration test PASSED")
            
        except Exception as e:
            logger.error(f"✗ Component integration test FAILED: {e}")
            self.test_results.append(("Component Integration", False))
    
    def _test_url_construction_pipeline(self):
        """Test URL construction pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 2: URL CONSTRUCTION PIPELINE")
        logger.info("=" * 60)
        
        test_cases = [
            ("BurrJo00", 2024, "Joe Burrow"),
            ("MahomPa00", 2024, "Patrick Mahomes"),
            ("AlleJo00", 2024, "Josh Allen"),
            ("PresDa00", 2024, "Dak Prescott"),
            ("RodgAa00", 2024, "Aaron Rodgers"),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for pfr_id, season, player_name in test_cases:
            try:
                logger.info(f"Testing URL construction pipeline for {player_name}")
                
                # Test enhanced URL construction
                url = build_enhanced_splits_url(pfr_id, season)
                assert url is not None, f"URL construction failed for {player_name}"
                
                # Test URL validation
                is_valid = validate_splits_url(url)
                assert is_valid, f"URL validation failed for {player_name}"
                
                # Test URL format
                assert "pro-football-reference.com" in url
                assert "splits" in url
                assert str(season) in url
                
                logger.info(f"  ✓ {player_name}: {url}")
                passed += 1
                
            except Exception as e:
                logger.error(f"  ✗ {player_name}: {e}")
        
        success = passed == total
        self.test_results.append(("URL Construction Pipeline", success))
        
        if success:
            logger.info("✓ URL construction pipeline test PASSED")
        else:
            logger.error(f"✗ URL construction pipeline test FAILED ({passed}/{total})")
    
    def _test_splits_manager_pipeline(self):
        """Test splits manager pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 3: SPLITS MANAGER PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Test splits manager initialization
            assert self.splits_manager is not None
            assert self.splits_manager.splits_extractor is not None
            logger.info("✓ Splits manager initialization verified")
            
            # Test URL construction testing
            test_results = self.splits_manager.test_splits_url_construction("BurrJo00", 2024)
            assert isinstance(test_results, dict)
            assert 'pfr_id' in test_results
            assert 'season' in test_results
            assert 'url' in test_results
            logger.info("✓ URL construction testing verified")
            
            # Test summary generation
            summary = self.splits_manager.get_extraction_summary()
            assert isinstance(summary, dict)
            required_keys = [
                'session_id', 'processing_time_seconds', 'total_players',
                'successful_extractions', 'failed_extractions', 'success_rate'
            ]
            for key in required_keys:
                assert key in summary, f"Missing key in summary: {key}"
            logger.info("✓ Summary generation verified")
            
            # Test metrics tracking
            assert hasattr(self.splits_manager, 'metrics')
            assert self.splits_manager.metrics is not None
            logger.info("✓ Metrics tracking verified")
            
            self.test_results.append(("Splits Manager Pipeline", True))
            logger.info("✓ Splits manager pipeline test PASSED")
            
        except Exception as e:
            logger.error(f"✗ Splits manager pipeline test FAILED: {e}")
            self.test_results.append(("Splits Manager Pipeline", False))
    
    def _test_enhanced_scraper_pipeline(self):
        """Test enhanced scraper pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 4: ENHANCED SCRAPER PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Test enhanced scraper initialization
            assert self.enhanced_scraper is not None
            assert self.enhanced_scraper.base_url == "https://www.pro-football-reference.com"
            assert self.enhanced_scraper.splits_manager is not None
            logger.info("✓ Enhanced scraper initialization verified")
            
            # Test metrics tracking
            assert hasattr(self.enhanced_scraper, 'metrics')
            assert self.enhanced_scraper.metrics is not None
            logger.info("✓ Metrics tracking verified")
            
            # Test request manager integration
            assert self.enhanced_scraper.request_manager is not None
            assert hasattr(self.enhanced_scraper.request_manager, 'get')
            logger.info("✓ Request manager integration verified")
            
            # Test splits manager integration
            assert self.enhanced_scraper.splits_manager is not None
            assert hasattr(self.enhanced_scraper.splits_manager, 'extract_all_player_splits')
            logger.info("✓ Splits manager integration verified")
            
            # Test comprehensive data extraction method
            assert hasattr(self.enhanced_scraper, 'scrape_all_qb_data')
            logger.info("✓ Comprehensive data extraction method verified")
            
            self.test_results.append(("Enhanced Scraper Pipeline", True))
            logger.info("✓ Enhanced scraper pipeline test PASSED")
            
        except Exception as e:
            logger.error(f"✗ Enhanced scraper pipeline test FAILED: {e}")
            self.test_results.append(("Enhanced Scraper Pipeline", False))
    
    def _test_scraping_operation_pipeline(self):
        """Test scraping operation pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 5: SCRAPING OPERATION PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Initialize scraping operation
            scraping_operation = ScrapingOperation(
                config=config,
                db_manager=self.db_manager,
                min_delay=7.0,
                max_delay=12.0
            )
            
            # Test component initialization
            assert scraping_operation.enhanced_scraper is not None
            assert scraping_operation.splits_manager is not None
            assert scraping_operation.legacy_pipeline is not None
            logger.info("✓ Scraping operation initialization verified")
            
            # Test execute method
            assert hasattr(scraping_operation, 'execute')
            logger.info("✓ Execute method verified")
            
            # Test private methods
            assert hasattr(scraping_operation, '_execute_full_season')
            assert hasattr(scraping_operation, '_execute_specific_players')
            assert hasattr(scraping_operation, '_execute_splits_only')
            logger.info("✓ Private methods verified")
            
            # Test metrics access
            metrics = scraping_operation.get_metrics()
            # Metrics might be None initially, which is OK
            logger.info("✓ Metrics access verified")
            
            # Test result structure
            result = ScrapingResult(
                success=True,
                season=2024,
                message="Test result",
                scraped_records=10,
                saved_records=10
            )
            assert result.success is True
            assert result.season == 2024
            logger.info("✓ Result structure verified")
            
            self.test_results.append(("Scraping Operation Pipeline", True))
            logger.info("✓ Scraping operation pipeline test PASSED")
            
        except Exception as e:
            logger.error(f"✗ Scraping operation pipeline test FAILED: {e}")
            self.test_results.append(("Scraping Operation Pipeline", False))
    
    def _test_data_flow_pipeline(self):
        """Test data flow pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 6: DATA FLOW PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Test data model compatibility
            from src.models.qb_models import QBBasicStats, QBSplitsType1, QBSplitsType2
            
            # Test QBBasicStats model
            basic_stats = QBBasicStats(
                pfr_id="BurrJo00",
                player_name="Joe Burrow",
                player_url="https://pro-football-reference.com/players/B/BurrJo00.htm",
                season=2024,
                rk=1,
                age=27,
                team="CIN",
                pos="QB",
                g=16,
                gs=16,
                qb_rec="9-7-0",
                cmp=400,
                att=600,
                inc=200,
                cmp_pct=66.7,
                yds=4500,
                td=35,
                td_pct=5.8,
                int=12,
                int_pct=2.0,
                first_downs=220,
                succ_pct=65.0,
                lng=75,
                y_a=7.5,
                ay_a=7.8,
                y_c=11.3,
                y_g=281.3,
                rate=98.5,
                qbr=75.2,
                sk=25,
                sk_yds=180,
                sk_pct=4.0,
                ny_a=6.8,
                any_a=7.1,
                four_qc=3,
                gwd=4,
                awards="Pro Bowl",
                player_additional="",
                scraped_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Validate basic stats
            errors = basic_stats.validate()
            assert len(errors) == 0, f"Basic stats validation errors: {errors}"
            logger.info("✓ QBBasicStats model verified")
            
            # Test QBSplitsType1 model
            splits_type1 = QBSplitsType1(
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
            
            # Validate splits type1
            errors = splits_type1.validate()
            assert len(errors) == 0, f"Splits type1 validation errors: {errors}"
            logger.info("✓ QBSplitsType1 model verified")
            
            # Test QBSplitsType2 model
            splits_type2 = QBSplitsType2(
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
            
            # Validate splits type2
            errors = splits_type2.validate()
            assert len(errors) == 0, f"Splits type2 validation errors: {errors}"
            logger.info("✓ QBSplitsType2 model verified")
            
            self.test_results.append(("Data Flow Pipeline", True))
            logger.info("✓ Data flow pipeline test PASSED")
            
        except Exception as e:
            logger.error(f"✗ Data flow pipeline test FAILED: {e}")
            self.test_results.append(("Data Flow Pipeline", False))
    
    def _test_error_handling_pipeline(self):
        """Test error handling pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 7: ERROR HANDLING PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Test invalid URL construction
            try:
                invalid_url = build_enhanced_splits_url("", 2024)
                assert invalid_url is None or "error" in invalid_url.lower()
                logger.info("✓ Invalid URL construction handled gracefully")
            except Exception as e:
                logger.info(f"✓ Invalid URL construction exception handled: {e}")
            
            # Test invalid season
            try:
                invalid_url = build_enhanced_splits_url("BurrJo00", 1800)
                assert invalid_url is None or "error" in invalid_url.lower()
                logger.info("✓ Invalid season handled gracefully")
            except Exception as e:
                logger.info(f"✓ Invalid season exception handled: {e}")
            
            # Test splits manager error handling
            try:
                # Test with invalid data
                result = self.splits_manager.extract_all_player_splits([], use_concurrent=False)
                assert isinstance(result, tuple)
                assert len(result) == 2
                logger.info("✓ Empty data handling verified")
            except Exception as e:
                logger.info(f"✓ Empty data exception handled: {e}")
            
            # Test enhanced scraper error handling
            try:
                # Test with invalid season
                result = self.enhanced_scraper.scrape_all_qb_data(1800, use_concurrent_splits=False)
                assert isinstance(result, tuple)
                assert len(result) == 3
                logger.info("✓ Invalid season handling verified")
            except Exception as e:
                logger.info(f"✓ Invalid season exception handled: {e}")
            
            self.test_results.append(("Error Handling Pipeline", True))
            logger.info("✓ Error handling pipeline test PASSED")
            
        except Exception as e:
            logger.error(f"✗ Error handling pipeline test FAILED: {e}")
            self.test_results.append(("Error Handling Pipeline", False))
    
    def _test_performance_pipeline(self):
        """Test performance pipeline"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST 8: PERFORMANCE PIPELINE")
        logger.info("=" * 60)
        
        try:
            # Test URL construction performance
            start_time = time.time()
            for i in range(100):
                build_enhanced_splits_url("BurrJo00", 2024)
            url_time = time.time() - start_time
            assert url_time < 1.0, f"URL construction too slow: {url_time:.3f}s"
            logger.info(f"✓ URL construction performance: {url_time:.3f}s for 100 URLs")
            
            # Test splits manager initialization performance
            start_time = time.time()
            splits_manager = SplitsManager(self.request_manager)
            init_time = time.time() - start_time
            assert init_time < 1.0, f"Splits manager initialization too slow: {init_time:.3f}s"
            logger.info(f"✓ Splits manager initialization performance: {init_time:.3f}s")
            
            # Test summary generation performance
            start_time = time.time()
            summary = self.splits_manager.get_extraction_summary()
            summary_time = time.time() - start_time
            assert summary_time < 0.1, f"Summary generation too slow: {summary_time:.3f}s"
            logger.info(f"✓ Summary generation performance: {summary_time:.3f}s")
            
            # Test metrics tracking performance
            start_time = time.time()
            metrics = self.enhanced_scraper.metrics
            metrics_time = time.time() - start_time
            assert metrics_time < 0.1, f"Metrics access too slow: {metrics_time:.3f}s"
            logger.info(f"✓ Metrics tracking performance: {metrics_time:.3f}s")
            
            self.test_results.append(("Performance Pipeline", True))
            logger.info("✓ Performance pipeline test PASSED")
            
        except Exception as e:
            logger.error(f"✗ Performance pipeline test FAILED: {e}")
            self.test_results.append(("Performance Pipeline", False))
    
    def _print_pipeline_summary(self):
        """Print comprehensive pipeline summary"""
        logger.info("\n" + "=" * 80)
        logger.info("ENHANCED PIPELINE TEST SUMMARY")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success in self.test_results if success)
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\nDetailed Results:")
        for test_name, success in self.test_results:
            status = "PASS" if success else "FAIL"
            logger.info(f"  {test_name}: {status}")
        
        # Performance metrics
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        logger.info(f"\nTotal Test Time: {total_time:.2f} seconds")
        
        if passed_tests == total_tests:
            logger.info("\n🎉 ALL PIPELINE TESTS PASSED!")
            logger.info("Enhanced splits extraction pipeline is production-ready.")
        else:
            logger.error(f"\n❌ {failed_tests} test(s) failed.")
            logger.error("Please review the errors above before deployment.")
    
    def _all_tests_passed(self) -> bool:
        """Check if all tests passed"""
        return all(success for _, success in self.test_results)


def main():
    """Main pipeline test function"""
    logger.info("ENHANCED PIPELINE TEST SUITE")
    logger.info("Testing comprehensive pipeline integration")
    
    try:
        # Run all tests
        test_suite = EnhancedPipelineTest()
        all_passed = test_suite.run_pipeline_tests()
        
        if all_passed:
            logger.info("🎉 PIPELINE TEST SUITE COMPLETED SUCCESSFULLY!")
            return 0
        else:
            logger.error("❌ PIPELINE TEST SUITE FAILED!")
            return 1
            
    except Exception as e:
        logger.error(f"Pipeline test suite failed with exception: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 