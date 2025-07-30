#!/usr/bin/env python3
"""
Analyze PFR Structure for Joe Burrow
Test script to understand the actual HTML structure of PFR's splits pages.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.pfr_structure_analyzer import PFRStructureAnalyzer
from src.core.selenium_manager import PFRSeleniumManager, ScrapingConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_joe_burrow_structure():
    """Analyze Joe Burrow's PFR structure"""
    print("=" * 80)
    print("PFR STRUCTURE ANALYSIS - JOE BURROW 2024")
    print("=" * 80)
    
    try:
        # Create Selenium manager
        selenium_config = ScrapingConfig(
            min_delay=7.0,
            max_delay=12.0,
            headless=True,
            enable_soft_block_detection=True
        )
        selenium_manager = PFRSeleniumManager(selenium_config)
        
        # Create analyzer
        analyzer = PFRStructureAnalyzer(selenium_manager)
        
        # Analyze Joe Burrow's splits page
        print("Analyzing Joe Burrow's PFR structure...")
        analysis = analyzer.analyze_player_splits_page(
            pfr_id="burrjo01",
            player_name="Joe Burrow",
            season=2024
        )
        
        # Generate and print report
        report = analyzer.generate_analysis_report(analysis)
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"pfr_structure_analysis_joe_burrow_{timestamp}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"\nReport saved to: {report_filename}")
        
        # Additional analysis
        print("\n" + "=" * 80)
        print("DETAILED ANALYSIS")
        print("=" * 80)
        
        if analysis.splits_tables:
            print(f"\nBASIC SPLITS TABLES ({len(analysis.splits_tables)}):")
            for i, table in enumerate(analysis.splits_tables):
                print(f"\nTable {i+1}: {table.table_id}")
                print(f"  Confidence: {table.confidence_score:.2f}")
                print(f"  Rows: {table.row_count}, Columns: {table.column_count}")
                print(f"  Headers: {table.headers}")
                print(f"  Data-stats: {table.data_stat_attributes}")
                print(f"  Sample Categories: {table.split_categories[:10]}")
                
                if table.sample_data:
                    print(f"  Sample Data (first row):")
                    for key, value in table.sample_data[0].items():
                        print(f"    {key}: {value}")
        
        if analysis.advanced_splits_tables:
            print(f"\nADVANCED SPLITS TABLES ({len(analysis.advanced_splits_tables)}):")
            for i, table in enumerate(analysis.advanced_splits_tables):
                print(f"\nTable {i+1}: {table.table_id}")
                print(f"  Confidence: {table.confidence_score:.2f}")
                print(f"  Rows: {table.row_count}, Columns: {table.column_count}")
                print(f"  Headers: {table.headers}")
                print(f"  Data-stats: {table.data_stat_attributes}")
                print(f"  Sample Categories: {table.split_categories[:10]}")
                
                if table.sample_data:
                    print(f"  Sample Data (first row):")
                    for key, value in table.sample_data[0].items():
                        print(f"    {key}: {value}")
        
        if analysis.other_tables:
            print(f"\nOTHER TABLES ({len(analysis.other_tables)}):")
            for i, table in enumerate(analysis.other_tables):
                print(f"\nTable {i+1}: {table.table_id}")
                print(f"  Type: {table.table_type}")
                print(f"  Confidence: {table.confidence_score:.2f}")
                print(f"  Rows: {table.row_count}, Columns: {table.column_count}")
                print(f"  Headers: {table.headers[:5]}...")  # First 5 headers
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Tables Found: {analysis.tables_found}")
        print(f"Basic Splits Tables: {len(analysis.splits_tables)}")
        print(f"Advanced Splits Tables: {len(analysis.advanced_splits_tables)}")
        print(f"Other Tables: {len(analysis.other_tables)}")
        print(f"Analysis Time: {analysis.analysis_time:.2f}s")
        
        if analysis.errors:
            print(f"\nErrors: {len(analysis.errors)}")
            for error in analysis.errors:
                print(f"  - {error}")
        
        if analysis.warnings:
            print(f"\nWarnings: {len(analysis.warnings)}")
            for warning in analysis.warnings:
                print(f"  - {warning}")
        
        return True
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        logger.exception("Analysis failed")
        return False

def main():
    """Main function"""
    print("Starting PFR Structure Analysis...")
    success = analyze_joe_burrow_structure()
    
    if success:
        print("\n✅ Analysis completed successfully!")
    else:
        print("\n❌ Analysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 