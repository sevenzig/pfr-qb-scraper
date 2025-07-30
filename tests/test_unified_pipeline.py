#!/usr/bin/env python3
"""
Test Unified Scraping Pipeline
Test the new unified pipeline with Joe Burrow's data to validate proper extraction.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.unified_scraping_pipeline import UnifiedScrapingPipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_unified_pipeline():
    """Test the unified scraping pipeline with Joe Burrow"""
    print("=" * 80)
    print("TESTING UNIFIED SCRAPING PIPELINE - JOE BURROW 2024")
    print("=" * 80)
    
    try:
        # Create unified pipeline
        print("Creating unified scraping pipeline...")
        pipeline = UnifiedScrapingPipeline(rate_limit_delay=7.0)
        
        # Test with Joe Burrow
        print("Testing with Joe Burrow (2024 season)...")
        result = pipeline.scrape_player_splits(
            pfr_id="burrjo01",
            player_name="Joe Burrow",
            season=2024
        )
        
        # Generate and print report
        report = pipeline.generate_pipeline_report(result)
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"unified_pipeline_test_joe_burrow_{timestamp}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"\nReport saved to: {report_filename}")
        
        # Validate results
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        
        # Check success
        if result.success:
            print("✅ Pipeline completed successfully")
        else:
            print("❌ Pipeline failed")
        
        # Check data extraction
        print(f"\nData Extraction:")
        print(f"  Basic Splits: {len(result.basic_splits)}")
        print(f"  Advanced Splits: {len(result.advanced_splits)}")
        
        if result.extraction_result:
            print(f"  Rows Processed: {result.extraction_result.rows_processed}")
            print(f"  Rows Extracted: {result.extraction_result.rows_extracted}")
            if result.extraction_result.rows_processed > 0:
                success_rate = result.extraction_result.rows_extracted / result.extraction_result.rows_processed
                print(f"  Success Rate: {success_rate:.1%}")
        
        # Check structure analysis
        if result.structure_analysis:
            print(f"\nStructure Analysis:")
            print(f"  Tables Found: {result.structure_analysis.tables_found}")
            print(f"  Basic Splits Tables: {len(result.structure_analysis.splits_tables)}")
            print(f"  Advanced Splits Tables: {len(result.structure_analysis.advanced_splits_tables)}")
        
        # Check for expected data
        print(f"\nData Quality Check:")
        
        # Check basic splits
        if result.basic_splits:
            print(f"  ✅ Basic splits extracted: {len(result.basic_splits)} records")
            
            # Check for Joe Burrow's known stats
            league_split = next((split for split in result.basic_splits if split.split == 'League'), None)
            if league_split:
                print(f"  ✅ League split found:")
                print(f"    - Completions: {league_split.cmp} (expected: 460)")
                print(f"    - Attempts: {league_split.att} (expected: 652)")
                print(f"    - Completion %: {league_split.cmp_pct} (expected: 70.55)")
                print(f"    - Yards: {league_split.yds} (expected: 4918)")
                print(f"    - TDs: {league_split.td} (expected: 43)")
                
                # Validate against known values
                if league_split.cmp == 460:
                    print("    ✅ Completions match expected value")
                else:
                    print(f"    ❌ Completions mismatch: got {league_split.cmp}, expected 460")
                
                if league_split.att == 652:
                    print("    ✅ Attempts match expected value")
                else:
                    print(f"    ❌ Attempts mismatch: got {league_split.att}, expected 652")
            else:
                print("  ❌ League split not found in basic splits")
        else:
            print("  ❌ No basic splits extracted")
        
        # Check advanced splits
        if result.advanced_splits:
            print(f"  ✅ Advanced splits extracted: {len(result.advanced_splits)} records")
            
            # Check for down splits
            down_splits = [split for split in result.advanced_splits if split.split == 'Down']
            if down_splits:
                print(f"  ✅ Down splits found: {len(down_splits)} records")
                
                # Check first down data
                first_down = next((split for split in down_splits if split.value == '1st'), None)
                if first_down:
                    print(f"    - 1st Down: {first_down.cmp} completions, {first_down.att} attempts")
                else:
                    print("    ❌ 1st down data not found")
            else:
                print("  ❌ No down splits found in advanced splits")
        else:
            print("  ❌ No advanced splits extracted")
        
        # Check errors and warnings
        print(f"\nError Analysis:")
        print(f"  Errors: {len(result.errors)}")
        if result.errors:
            for error in result.errors:
                print(f"    - {error}")
        
        print(f"  Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"    - {warning}")
        
        # Performance analysis
        print(f"\nPerformance Analysis:")
        print(f"  Processing Time: {result.processing_time:.2f}s")
        if result.processing_time < 30:
            print("  ✅ Processing time is reasonable")
        else:
            print("  ⚠️  Processing time is slow")
        
        # Overall assessment
        print(f"\n" + "=" * 80)
        print("OVERALL ASSESSMENT")
        print("=" * 80)
        
        if result.success and len(result.basic_splits) > 0 and len(result.advanced_splits) > 0:
            print("✅ EXCELLENT: Pipeline is working correctly!")
            print("  - Successfully extracted both basic and advanced splits")
            print("  - Data quality appears good")
            print("  - Ready for production use")
        elif result.success and (len(result.basic_splits) > 0 or len(result.advanced_splits) > 0):
            print("⚠️  PARTIAL SUCCESS: Pipeline extracted some data but not complete")
            print("  - Some data extracted successfully")
            print("  - May need adjustments for complete extraction")
        else:
            print("❌ FAILURE: Pipeline did not extract expected data")
            print("  - No data extracted or pipeline failed")
            print("  - Requires investigation and fixes")
        
        # Clean up
        pipeline.close()
        
        return result.success
        
    except Exception as e:
        print(f"Error during testing: {e}")
        logger.exception("Test failed")
        return False

def main():
    """Main function"""
    print("Starting Unified Pipeline Test...")
    success = test_unified_pipeline()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 