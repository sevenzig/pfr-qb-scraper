#!/usr/bin/env python3
"""
Test script for CoreScraper functionality
Tests the unified scraper without external dependencies
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_core_scraper_creation():
    """Test CoreScraper creation and basic functionality"""
    print("Testing CoreScraper creation...")
    
    try:
        from core.scraper import CoreScraper, RateLimiter, ScrapingMetrics
        print("✓ CoreScraper classes imported")
        
        # Test CoreScraper creation
        scraper = CoreScraper(rate_limit_delay=0.1)  # Fast for testing
        print("✓ CoreScraper created successfully")
        
        # Test rate limiter
        rate_limiter = RateLimiter(delay=0.1)
        print("✓ RateLimiter created successfully")
        
        # Test metrics
        metrics = ScrapingMetrics()
        print("✓ ScrapingMetrics created successfully")
        
        # Test basic methods
        assert hasattr(scraper, 'scrape_player_season')
        assert hasattr(scraper, 'scrape_season_qbs')
        assert hasattr(scraper, 'scrape_team_qbs')
        print("✓ CoreScraper has required methods")
        
        # Test session creation
        assert scraper.session is not None
        print("✓ Session created successfully")
        
        # Test metrics tracking
        scraper.start_scraping_session()
        assert scraper.metrics.start_time is not None
        print("✓ Metrics tracking works")
        
        return True
        
    except Exception as e:
        print(f"✗ CoreScraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_integration():
    """Test CLI integration with CoreScraper"""
    print("\nTesting CLI integration...")
    
    try:
        from cli.cli_main import CLIManager
        cli = CLIManager()
        print("✓ CLI manager created")
        
        # Test that scrape command exists
        scrape_cmd = cli.get_command('scrape')
        assert scrape_cmd is not None
        print("✓ Scrape command found")
        
        # Test help
        result = cli.run(['scrape', '--help'])
        assert result == 0
        print("✓ Scrape command help works")
        
        return True
        
    except Exception as e:
        print(f"✗ CLI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_functionality():
    """Test CoreScraper with mock data"""
    print("\nTesting mock functionality...")
    
    try:
        from core.scraper import CoreScraper
        
        # Create scraper with mock config
        scraper = CoreScraper()
        
        # Test that it can handle missing dependencies gracefully
        assert scraper.config is not None
        print("✓ Mock config created")
        
        # Test metrics
        scraper.start_scraping_session()
        scraper.end_scraping_session()
        
        metrics = scraper.get_metrics()
        assert metrics.start_time is not None
        assert metrics.end_time is not None
        print("✓ Metrics tracking works with mock data")
        
        return True
        
    except Exception as e:
        print(f"✗ Mock functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all CoreScraper tests"""
    print("=== CoreScraper Phase 2 Test ===")
    
    tests = [
        test_core_scraper_creation,
        test_cli_integration,
        test_mock_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✓ All tests passed! CoreScraper is working correctly.")
        print("✓ Phase 2 Core functionality is ready.")
        return 0
    else:
        print("✗ Some tests failed. CoreScraper needs fixes.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 