#!/usr/bin/env python3
"""
Test Unified Pipeline Command
CLI command to test the new unified scraping pipeline.
"""

import argparse
import logging
from datetime import datetime
from typing import Optional

from ..base_command import BaseCommand
from ...core.unified_scraping_pipeline import UnifiedScrapingPipeline

logger = logging.getLogger(__name__)


class TestUnifiedCommand(BaseCommand):
    """Test the unified scraping pipeline with a specific player"""
    
    def __init__(self):
        super().__init__()
    
    @property
    def name(self) -> str:
        """Command name"""
        return "test-unified"
    
    @property
    def description(self) -> str:
        """Command description"""
        return "Test the new unified scraping pipeline to validate proper data extraction"
    
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments"""
        parser.add_argument(
            '--player-id',
            type=str,
            default='burrjo01',
            help='PFR player ID to test (default: burrjo01 for Joe Burrow)'
        )
        
        parser.add_argument(
            '--player-name',
            type=str,
            default='Joe Burrow',
            help='Player name for testing (default: Joe Burrow)'
        )
        
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season to test (default: 2024)'
        )
        
        parser.add_argument(
            '--rate-limit',
            type=float,
            default=7.0,
            help='Rate limit delay in seconds (default: 7.0)'
        )
        
        parser.add_argument(
            '--save-report',
            action='store_true',
            help='Save detailed report to file'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
    
    def run(self, args: argparse.Namespace) -> int:
        """Run the test unified pipeline command"""
        try:
            # Set up logging
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            
            self.print_section_header("Testing Unified Scraping Pipeline")
            self.print_info(f"Player: {args.player_name} ({args.player_id})")
            self.print_info(f"Season: {args.season}")
            self.print_info(f"Rate Limit: {args.rate_limit}s")
            
            # Create unified pipeline
            self.print_info("Creating unified scraping pipeline...")
            with UnifiedScrapingPipeline(rate_limit_delay=args.rate_limit) as pipeline:
                # Test the pipeline
                self.print_info(f"Testing pipeline with {args.player_name}...")
                result = pipeline.scrape_player_splits(
                    pfr_id=args.player_id,
                    player_name=args.player_name,
                    season=args.season
                )
                
                # Generate report
                report = pipeline.generate_pipeline_report(result)
                
                # Print results
                self._print_results(result, report, args)
                
                # Save report if requested
                if args.save_report:
                    self._save_report(report, args)
                
                # Return success/failure
                return 0 if result.success else 1
                
        except KeyboardInterrupt:
            self.print_warning("Test interrupted by user")
            return 1
        except Exception as e:
            return self.handle_error(e, "Test unified pipeline failed")
    
    def _print_results(self, result, report: str, args: argparse.Namespace) -> None:
        """Print test results"""
        self.print_section_header("Test Results")
        
        # Overall success
        if result.success:
            self.print_success("Pipeline completed successfully")
        else:
            self.print_error("Pipeline failed")
        
        # Data extraction summary
        self.print_info(f"Basic Splits: {len(result.basic_splits)}")
        self.print_info(f"Advanced Splits: {len(result.advanced_splits)}")
        
        if result.extraction_result:
            self.print_info(f"Rows Processed: {result.extraction_result.rows_processed}")
            self.print_info(f"Rows Extracted: {result.extraction_result.rows_extracted}")
            if result.extraction_result.rows_processed > 0:
                success_rate = result.extraction_result.rows_extracted / result.extraction_result.rows_processed
                self.print_info(f"Success Rate: {success_rate:.1%}")
        
        # Structure analysis
        if result.structure_analysis:
            self.print_info(f"Tables Found: {result.structure_analysis.tables_found}")
            self.print_info(f"Basic Splits Tables: {len(result.structure_analysis.splits_tables)}")
            self.print_info(f"Advanced Splits Tables: {len(result.structure_analysis.advanced_splits_tables)}")
        
        # Performance
        self.print_info(f"Processing Time: {result.processing_time:.2f}s")
        
        # Data quality check
        self._print_data_quality_check(result)
        
        # Errors and warnings
        if result.errors:
            self.print_section_header("Errors")
            for error in result.errors:
                self.print_error(f"  - {error}")
        
        if result.warnings:
            self.print_section_header("Warnings")
            for warning in result.warnings:
                self.print_warning(f"  - {warning}")
        
        # Overall assessment
        self._print_overall_assessment(result)
    
    def _print_data_quality_check(self, result) -> None:
        """Print data quality check results"""
        self.print_section_header("Data Quality Check")
        
        # Check basic splits
        if result.basic_splits:
            self.print_success(f"Basic splits extracted: {len(result.basic_splits)} records")
            
            # Check for known stats (Joe Burrow specific)
            if result.player_name == "Joe Burrow":
                league_split = next((split for split in result.basic_splits if split.split == 'League'), None)
                if league_split:
                    self.print_info("League split validation:")
                    self.print_info(f"  - Completions: {league_split.cmp} (expected: 460)")
                    self.print_info(f"  - Attempts: {league_split.att} (expected: 652)")
                    
                    if league_split.cmp == 460 and league_split.att == 652:
                        self.print_success("  ✅ Data matches expected values")
                    else:
                        self.print_warning("  ⚠️  Data doesn't match expected values")
        else:
            self.print_error("No basic splits extracted")
        
        # Check advanced splits
        if result.advanced_splits:
            self.print_success(f"Advanced splits extracted: {len(result.advanced_splits)} records")
            
            down_splits = [split for split in result.advanced_splits if split.split == 'Down']
            if down_splits:
                self.print_success(f"Down splits found: {len(down_splits)} records")
            else:
                self.print_warning("No down splits found")
        else:
            self.print_error("No advanced splits extracted")
    
    def _print_overall_assessment(self, result) -> None:
        """Print overall assessment"""
        self.print_section_header("Overall Assessment")
        
        if result.success and len(result.basic_splits) > 0 and len(result.advanced_splits) > 0:
            self.print_success("EXCELLENT: Pipeline is working correctly!")
            self.print_info("  - Successfully extracted both basic and advanced splits")
            self.print_info("  - Data quality appears good")
            self.print_info("  - Ready for production use")
        elif result.success and (len(result.basic_splits) > 0 or len(result.advanced_splits) > 0):
            self.print_warning("PARTIAL SUCCESS: Pipeline extracted some data but not complete")
            self.print_info("  - Some data extracted successfully")
            self.print_info("  - May need adjustments for complete extraction")
        else:
            self.print_error("FAILURE: Pipeline did not extract expected data")
            self.print_info("  - No data extracted or pipeline failed")
            self.print_info("  - Requires investigation and fixes")
    
    def _save_report(self, report: str, args: argparse.Namespace) -> None:
        """Save detailed report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"unified_pipeline_test_{args.player_id}_{args.season}_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(report)
            self.print_success(f"Detailed report saved to: {filename}")
        except Exception as e:
            self.print_error(f"Failed to save report: {e}") 