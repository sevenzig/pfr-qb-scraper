#!/usr/bin/env python3
"""
Test Core Functionality
Simple test script to test the new core components without CLI dependencies.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_core_imports():
    """Test that all core modules can be imported"""
    print("Testing core module imports...")
    
    try:
        from src.core.pfr_structure_analyzer import PFRStructureAnalyzer, PFRStructureAnalysis, TableStructure
        print("✅ PFRStructureAnalyzer imported successfully")
        
        from src.core.pfr_data_extractor import PFRDataExtractor, ExtractionResult
        print("✅ PFRDataExtractor imported successfully")
        
        from src.core.unified_scraping_pipeline import UnifiedScrapingPipeline, PipelineResult
        print("✅ UnifiedScrapingPipeline imported successfully")
        
        from src.core.selenium_manager import PFRSeleniumManager, ScrapingConfig
        print("✅ PFRSeleniumManager imported successfully")
        
        from src.utils.data_utils import build_splits_url
        print("✅ build_splits_url imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        logger.exception("Import test failed")
        return False

def test_basic_functionality():
    """Test basic functionality without making actual requests"""
    print("\nTesting basic functionality...")
    
    try:
        # Test URL building
        from src.utils.data_utils import build_splits_url
        test_url = build_splits_url("burrjo01", 2024)
        print(f"✅ URL built successfully: {test_url}")
        
        # Test data extractor initialization
        from src.core.pfr_data_extractor import PFRDataExtractor
        extractor = PFRDataExtractor()
        print("✅ PFRDataExtractor initialized successfully")
        
        # Test structure analyzer initialization (without selenium)
        from src.core.pfr_structure_analyzer import PFRStructureAnalyzer
        analyzer = PFRStructureAnalyzer(selenium_manager=None)
        print("✅ PFRStructureAnalyzer initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        logger.exception("Basic functionality test failed")
        return False

def test_pipeline_creation():
    """Test pipeline creation without making requests"""
    print("\nTesting pipeline creation...")
    
    try:
        from src.core.unified_scraping_pipeline import UnifiedScrapingPipeline
        
        # Create pipeline with a very short delay for testing
        pipeline = UnifiedScrapingPipeline(rate_limit_delay=1.0)
        print("✅ UnifiedScrapingPipeline created successfully")
        
        # Test pipeline configuration
        print(f"  - Enable structure analysis: {pipeline.enable_structure_analysis}")
        print(f"  - Enable data extraction: {pipeline.enable_data_extraction}")
        print(f"  - Enable validation: {pipeline.enable_validation}")
        print(f"  - Max retries: {pipeline.max_retries}")
        
        # Clean up
        pipeline.close()
        print("✅ Pipeline closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline creation test failed: {e}")
        logger.exception("Pipeline creation test failed")
        return False

def main():
    """Main test function"""
    print("=" * 80)
    print("CORE FUNCTIONALITY TEST")
    print("=" * 80)
    
    # Test imports
    if not test_core_imports():
        print("\n❌ Import tests failed!")
        sys.exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed!")
        sys.exit(1)
    
    # Test pipeline creation
    if not test_pipeline_creation():
        print("\n❌ Pipeline creation tests failed!")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ ALL CORE TESTS PASSED!")
    print("=" * 80)
    print("\nThe core components are working correctly.")
    print("You can now test the full pipeline with:")
    print("  python -m src.cli.cli_main test-unified")
    print("\nOr run the structure analysis with:")
    print("  python tests/analyze_pfr_structure.py")

if __name__ == "__main__":
    main() 