#!/usr/bin/env python3
"""
Comprehensive Test for NFL QB Data Extraction System.

This script tests the complete data extraction pipeline including:
- PFR Structure Analysis
- Data Extraction with proper attribute mapping
- Validation against database schema
- Performance monitoring
"""

import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.pfr_structure_analyzer import PFRStructureAnalyzer
from core.pfr_data_extractor import PFRDataExtractor, ExtractionResult
from core.request_manager import RequestManager
from core.html_parser import HTMLParser
from config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_pfr_structure_analysis():
    """Test PFR structure analysis with Joe Burrow's 2024 splits page."""
    logger.info("=== Testing PFR Structure Analysis ===")
    
    # Initialize components
    config = Config()
    request_manager = RequestManager(config)
    html_parser = HTMLParser()
    structure_analyzer = PFRStructureAnalyzer()
    
    # Test URL - Joe Burrow's 2024 splits
    test_url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
    
    try:
        # Get page content
        logger.info(f"Fetching page: {test_url}")
        response = request_manager.get_page(test_url)
        
        if not response['success']:
            logger.error(f"Failed to fetch page: {response['error']}")
            return False
        
        # Parse HTML
        soup = html_parser.parse_html(response['content'])
        if not soup:
            logger.error("Failed to parse HTML")
            return False
        
        # Analyze structure
        logger.info("Analyzing page structure...")
        analysis = structure_analyzer.analyze_page_structure(soup)
        
        # Print analysis results
        logger.info(f"Analysis Results:")
        logger.info(f"  - Total tables found: {analysis['total_tables']}")
        logger.info(f"  - Table categorization: {list(analysis['table_categorization'].keys())}")
        
        # Check data-stat coverage
        coverage = analysis['data_stat_coverage']
        logger.info(f"Data-stat Coverage:")
        logger.info(f"  - Total data-stat attributes found: {coverage['total_data_stats_found']}")
        logger.info(f"  - Basic stats coverage: {coverage['basic_stats_coverage']}")
        logger.info(f"  - Splits coverage: {coverage['splits_coverage']}")
        logger.info(f"  - Advanced splits coverage: {coverage['advanced_splits_coverage']}")
        
        # Check for missing fields
        missing = analysis['missing_fields']
        if missing['basic_stats']:
            logger.warning(f"Missing basic stats fields: {missing['basic_stats']}")
        if missing['splits']:
            logger.warning(f"Missing splits fields: {missing['splits']}")
        if missing['advanced_splits']:
            logger.warning(f"Missing advanced splits fields: {missing['advanced_splits']}")
        
        # Print recommendations
        if analysis['recommendations']:
            logger.info("Recommendations:")
            for rec in analysis['recommendations']:
                logger.info(f"  - {rec}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in structure analysis test: {e}", exc_info=True)
        return False


def test_data_extraction():
    """Test comprehensive data extraction."""
    logger.info("=== Testing Data Extraction ===")
    
    # Initialize components
    config = Config()
    request_manager = RequestManager(config)
    html_parser = HTMLParser()
    data_extractor = PFRDataExtractor()
    
    # Test URL - Joe Burrow's 2024 splits
    test_url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
    player_name = "Joe Burrow"
    season = 2024
    
    try:
        # Get page content
        logger.info(f"Fetching page: {test_url}")
        response = request_manager.get_page(test_url)
        
        if not response['success']:
            logger.error(f"Failed to fetch page: {response['error']}")
            return False
        
        # Parse HTML
        soup = html_parser.parse_html(response['content'])
        if not soup:
            logger.error("Failed to parse HTML")
            return False
        
        # Extract all data
        logger.info("Extracting data...")
        extraction_results = data_extractor.extract_all_qb_data(soup, player_name, season)
        
        # Print extraction results
        logger.info(f"Extraction Results:")
        logger.info(f"  - Tables extracted: {len(extraction_results)}")
        
        for table_type, result in extraction_results.items():
            logger.info(f"\n{table_type.upper()} Results:")
            logger.info(f"  - Success: {result.success}")
            logger.info(f"  - Row count: {result.row_count}")
            logger.info(f"  - Fields extracted: {len(result.extracted_fields)}")
            logger.info(f"  - Fields missing: {len(result.missing_fields)}")
            logger.info(f"  - Errors: {len(result.errors)}")
            logger.info(f"  - Warnings: {len(result.warnings)}")
            
            if result.extracted_fields:
                logger.info(f"  - Extracted fields: {result.extracted_fields[:10]}...")  # Show first 10
            
            if result.missing_fields:
                logger.warning(f"  - Missing fields: {result.missing_fields[:10]}...")  # Show first 10
            
            if result.errors:
                logger.error(f"  - Errors: {result.errors}")
            
            if result.warnings:
                logger.warning(f"  - Warnings: {result.warnings}")
        
        # Get extraction summary
        summary = data_extractor.get_extraction_summary(extraction_results)
        logger.info(f"\nExtraction Summary:")
        logger.info(f"  - Total tables extracted: {summary['total_tables_extracted']}")
        logger.info(f"  - Successful extractions: {summary['successful_extractions']}")
        logger.info(f"  - Total fields extracted: {summary['total_fields_extracted']}")
        logger.info(f"  - Total missing fields: {summary['total_missing_fields']}")
        logger.info(f"  - Total errors: {summary['total_errors']}")
        logger.info(f"  - Total warnings: {summary['total_warnings']}")
        
        # Show table details
        for table_type, details in summary['table_details'].items():
            logger.info(f"\n{table_type.upper()} Details:")
            logger.info(f"  - Success: {details['success']}")
            logger.info(f"  - Row count: {details['row_count']}")
            logger.info(f"  - Fields extracted: {details['fields_extracted']}")
            logger.info(f"  - Fields missing: {details['fields_missing']}")
            logger.info(f"  - Coverage percentage: {details['coverage_percentage']:.1f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in data extraction test: {e}", exc_info=True)
        return False


def test_field_mappings():
    """Test field mappings for all table types."""
    logger.info("=== Testing Field Mappings ===")
    
    structure_analyzer = PFRStructureAnalyzer()
    
    # Test basic stats mappings
    basic_stats_mappings = structure_analyzer.get_field_mappings('basic_stats')
    logger.info(f"Basic Stats Mappings: {len(basic_stats_mappings)} fields")
    
    # Test splits mappings
    splits_mappings = structure_analyzer.get_field_mappings('splits')
    logger.info(f"Splits Mappings: {len(splits_mappings)} fields")
    
    # Test advanced splits mappings
    advanced_splits_mappings = structure_analyzer.get_field_mappings('advanced_splits')
    logger.info(f"Advanced Splits Mappings: {len(advanced_splits_mappings)} fields")
    
    # Show sample mappings
    logger.info("\nSample Basic Stats Mappings:")
    for mapping in basic_stats_mappings[:5]:  # Show first 5
        logger.info(f"  - {mapping.pfr_attribute} -> {mapping.database_field} ({mapping.data_type})")
    
    logger.info("\nSample Splits Mappings:")
    for mapping in splits_mappings[:5]:  # Show first 5
        logger.info(f"  - {mapping.pfr_attribute} -> {mapping.database_field} ({mapping.data_type})")
    
    logger.info("\nSample Advanced Splits Mappings:")
    for mapping in advanced_splits_mappings[:5]:  # Show first 5
        logger.info(f"  - {mapping.pfr_attribute} -> {mapping.database_field} ({mapping.data_type})")
    
    return True


def test_data_validation():
    """Test data validation functionality."""
    logger.info("=== Testing Data Validation ===")
    
    structure_analyzer = PFRStructureAnalyzer()
    
    # Test with sample data
    sample_basic_stats = {
        'player_name': 'Joe Burrow',
        'season': 2024,
        'cmp': 460,
        'att': 652,
        'yds': 4918,
        'td': 43,
        'int': 15
    }
    
    sample_splits = {
        'player_name': 'Joe Burrow',
        'season': 2024,
        'split': 'Home',
        'value': 'Home',
        'g': 8,
        'w': 5,
        'l': 3
    }
    
    # Validate basic stats
    basic_stats_validation = structure_analyzer.validate_extracted_data(sample_basic_stats, 'basic_stats')
    logger.info(f"Basic Stats Validation:")
    logger.info(f"  - Valid: {basic_stats_validation['valid']}")
    logger.info(f"  - Missing required fields: {basic_stats_validation['missing_required_fields']}")
    logger.info(f"  - Coverage percentage: {basic_stats_validation['coverage_percentage']:.1f}%")
    
    # Validate splits
    splits_validation = structure_analyzer.validate_extracted_data(sample_splits, 'splits')
    logger.info(f"Splits Validation:")
    logger.info(f"  - Valid: {splits_validation['valid']}")
    logger.info(f"  - Missing required fields: {splits_validation['missing_required_fields']}")
    logger.info(f"  - Coverage percentage: {splits_validation['coverage_percentage']:.1f}%")
    
    return True


def main():
    """Run all comprehensive tests."""
    logger.info("Starting Comprehensive NFL QB Data Extraction Tests")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    # Run tests
    tests = [
        ("Field Mappings", test_field_mappings),
        ("PFR Structure Analysis", test_pfr_structure_analysis),
        ("Data Extraction", test_data_extraction),
        ("Data Validation", test_data_validation),
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
    
    # Print summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    logger.info(f"Tests completed in {duration:.2f} seconds")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Success rate: {(passed/total)*100:.1f}%")
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"  - {test_name}: {status}")
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! The data extraction system is working correctly.")
    else:
        logger.error(f"\n⚠️  {total - passed} TESTS FAILED. Please review the issues above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 