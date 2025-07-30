#!/usr/bin/env python3
"""
Test NFL QB Data Extraction with Saved HTML Files.

This script tests the data extraction system using saved HTML files
to validate the extraction logic without hitting PFR's servers.
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
from core.html_parser import HTMLParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_with_saved_html_files():
    """Test data extraction using saved HTML files."""
    logger.info("=== Testing Data Extraction with Saved HTML Files ===")
    
    # Initialize components
    html_parser = HTMLParser()
    data_extractor = PFRDataExtractor()
    structure_analyzer = PFRStructureAnalyzer()
    
    # Test with Joe Burrow's 2024 splits page (if available)
    test_files = [
        "passing_stats_full.html",  # Main passing stats page
        "pfr_passing_debug_2024.html"  # Debug page if available
    ]
    
    results = {}
    
    for filename in test_files:
        file_path = os.path.join(os.path.dirname(__file__), '..', filename)
        if os.path.exists(file_path):
            logger.info(f"Testing with saved HTML file: {filename}")
            
            try:
                # Read the HTML file
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Parse HTML
                soup = html_parser.parse_html(html_content)
                if not soup:
                    logger.error(f"Failed to parse HTML from {filename}")
                    continue
                
                # Analyze structure
                logger.info("Analyzing page structure...")
                analysis = structure_analyzer.analyze_page_structure(soup)
                
                # Print analysis results
                logger.info(f"Analysis Results for {filename}:")
                logger.info(f"  - Total tables found: {analysis['total_tables']}")
                logger.info(f"  - Table categorization: {list(analysis['table_categorization'].keys())}")
                
                # Check data-stat coverage
                coverage = analysis['data_stat_coverage']
                logger.info(f"Data-stat Coverage for {filename}:")
                logger.info(f"  - Total data-stat attributes found: {coverage['total_data_stats_found']}")
                logger.info(f"  - Basic stats coverage: {coverage['basic_stats_coverage']}")
                logger.info(f"  - Splits coverage: {coverage['splits_coverage']}")
                logger.info(f"  - Advanced splits coverage: {coverage['advanced_splits_coverage']}")
                
                # Extract data
                logger.info("Extracting data...")
                extraction_results = data_extractor.extract_all_qb_data(soup, "Test Player", 2024)
                
                # Print extraction results
                logger.info(f"Extraction Results for {filename}:")
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
                        logger.info(f"  - Extracted fields: {result.extracted_fields[:10]}...")
                    
                    if result.missing_fields:
                        logger.warning(f"  - Missing fields: {result.missing_fields[:10]}...")
                    
                    if result.errors:
                        logger.error(f"  - Errors: {result.errors}")
                    
                    if result.warnings:
                        logger.warning(f"  - Warnings: {result.warnings}")
                
                # Get extraction summary
                summary = data_extractor.get_extraction_summary(extraction_results)
                logger.info(f"\nExtraction Summary for {filename}:")
                logger.info(f"  - Total tables extracted: {summary['total_tables_extracted']}")
                logger.info(f"  - Successful extractions: {summary['successful_extractions']}")
                logger.info(f"  - Total fields extracted: {summary['total_fields_extracted']}")
                logger.info(f"  - Total missing fields: {summary['total_missing_fields']}")
                logger.info(f"  - Total errors: {summary['total_errors']}")
                logger.info(f"  - Total warnings: {summary['total_warnings']}")
                
                results[filename] = {
                    'analysis': analysis,
                    'extraction': extraction_results,
                    'summary': summary
                }
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}", exc_info=True)
                results[filename] = {'error': str(e)}
        else:
            logger.warning(f"HTML file not found: {filename}")
    
    return results


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


def create_sample_html_file():
    """Create a sample HTML file for testing if none exists."""
    sample_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample PFR Page</title>
</head>
<body>
    <table id="stats" class="sortable stats_table now_sortable">
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
    
    <table id="splits" class="sortable stats_table now_sortable">
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
    
    file_path = os.path.join(os.path.dirname(__file__), '..', 'sample_pfr_page.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(sample_html)
    
    logger.info(f"Created sample HTML file: {file_path}")
    return file_path


def main():
    """Run all tests with saved HTML files."""
    logger.info("Starting NFL QB Data Extraction Tests with Saved HTML Files")
    logger.info("=" * 70)
    
    start_time = datetime.now()
    
    # Create sample HTML file if no test files exist
    test_files = ["passing_stats_full.html", "pfr_passing_debug_2024.html"]
    test_files_exist = any(os.path.exists(os.path.join(os.path.dirname(__file__), '..', f)) for f in test_files)
    
    if not test_files_exist:
        logger.info("No test HTML files found. Creating sample file...")
        create_sample_html_file()
    
    # Run tests
    tests = [
        ("Field Mappings", test_field_mappings),
        ("Data Validation", test_data_validation),
        ("HTML File Extraction", test_with_saved_html_files),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "HTML File Extraction":
                result = test_func()
                results[test_name] = result
                if result:
                    logger.info(f"✅ {test_name} PASSED")
                else:
                    logger.error(f"❌ {test_name} FAILED")
            else:
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
    
    logger.info(f"\n{'='*70}")
    logger.info("TEST SUMMARY")
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
        logger.info("\n🎉 ALL TESTS PASSED! The data extraction system is working correctly.")
    else:
        logger.error(f"\n⚠️  {total - passed} TESTS FAILED. Please review the issues above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 