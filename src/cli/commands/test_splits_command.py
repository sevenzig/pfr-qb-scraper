#!/usr/bin/env python3
"""
Test Splits Command for NFL QB Data Scraping
CLI command for testing splits extraction functionality
"""

import logging
import argparse
from typing import Dict, Any, List
from argparse import ArgumentParser, Namespace

from src.cli.base_command import BaseCommand
from src.scrapers.enhanced_scraper import EnhancedPFRScraper
from src.core.splits_manager import SplitsManager
from src.core.request_manager import RequestManager
from src.config.config import config
from src.utils.data_utils import build_enhanced_splits_url, validate_splits_url

logger = logging.getLogger(__name__)


class TestSplitsCommand(BaseCommand):
    """Test enhanced splits extraction functionality"""
    
    @property
    def name(self) -> str:
        return "test-splits"
    
    @property
    def description(self) -> str:
        return "Test enhanced splits extraction with comprehensive error handling"
    
    def __init__(self):
        super().__init__()
        self.help_text = """
Test enhanced splits extraction functionality.

Usage:
  test-splits [OPTIONS]

Options:
  --player-name TEXT     Test splits extraction for specific player
  --pfr-id TEXT         PFR ID for the player (required if --player-name is used)
  --season INTEGER      Season year (default: 2024)
  --concurrent          Use concurrent processing for multiple players
  --url-test            Test URL construction only
  --validate            Validate extracted data
  --verbose             Enable verbose logging
  --help                Show this help message

Examples:
  # Test URL construction for Joe Burrow
  test-splits --player-name "Joe Burrow" --pfr-id "BurrJo00" --url-test
  
  # Test full splits extraction for Joe Burrow
  test-splits --player-name "Joe Burrow" --pfr-id "BurrJo00" --validate
  
  # Test splits extraction for 2024 season with concurrent processing
  test-splits --season 2024 --concurrent --verbose
        """
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments"""
        parser.add_argument(
            '--player-name',
            type=str,
            help='Test splits extraction for specific player'
        )
        parser.add_argument(
            '--pfr-id',
            type=str,
            help='PFR ID for the player (required if --player-name is used)'
        )
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season year (default: 2024)'
        )
        parser.add_argument(
            '--concurrent',
            action='store_true',
            help='Use concurrent processing for multiple players'
        )
        parser.add_argument(
            '--url-test',
            action='store_true',
            help='Test URL construction only'
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate extracted data'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
    
    def run(self, args: Namespace) -> int:
        """Execute the test splits command"""
        try:
            # Configure logging
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
                logging.getLogger('src.scrapers.splits_extractor').setLevel(logging.DEBUG)
                logging.getLogger('src.operations.splits_manager').setLevel(logging.DEBUG)
            
            logger.info("Starting enhanced splits extraction test")
            
            # Initialize components
            request_manager = RequestManager(
                rate_limit_delay=config.scraping.rate_limit_delay,
                jitter_range=config.scraping.jitter_range
            )
            
            scraper = EnhancedPFRScraper(rate_limit_delay=config.scraping.rate_limit_delay)
            splits_manager = SplitsManager(request_manager)
            
            # Test URL construction if requested
            if args.url_test:
                return self._test_url_construction(args, splits_manager)
            
            # Test specific player if provided
            if args.player_name and args.pfr_id:
                return self._test_single_player(args, splits_manager)
            
            # Test comprehensive extraction
            return self._test_comprehensive_extraction(args, scraper)
            
        except Exception as e:
            logger.error(f"Test splits command failed: {str(e)}", exc_info=True)
            return 1
    
    def _test_url_construction(self, args, splits_manager: SplitsManager) -> int:
        """Test URL construction functionality"""
        logger.info("Testing URL construction functionality")
        
        if not args.pfr_id:
            logger.error("PFR ID is required for URL construction test")
            return 1
        
        # Test URL construction
        test_results = splits_manager.test_splits_url_construction(args.pfr_id, args.season)
        
        logger.info("URL Construction Test Results:")
        logger.info(f"  PFR ID: {test_results['pfr_id']}")
        logger.info(f"  Season: {test_results['season']}")
        
        if test_results['urls_tested']:
            logger.info("  URLs Tested:")
            for method, url in test_results['urls_tested']:
                logger.info(f"    {method}: {url}")
        
        if test_results['valid_urls']:
            logger.info("  Valid URLs:")
            for method, url in test_results['valid_urls']:
                logger.info(f"    {method}: {url}")
        
        if test_results['errors']:
            logger.error("  Errors:")
            for error in test_results['errors']:
                logger.error(f"    {error}")
        
        # Test URL validation
        if test_results['valid_urls']:
            for method, url in test_results['valid_urls']:
                is_valid = validate_splits_url(url)
                logger.info(f"  URL validation for {method}: {'PASS' if is_valid else 'FAIL'}")
        
        return 0 if test_results['valid_urls'] else 1
    
    def _test_single_player(self, args, splits_manager: SplitsManager) -> int:
        """Test splits extraction for a single player"""
        logger.info(f"Testing splits extraction for {args.player_name} (PFR ID: {args.pfr_id})")
        
        try:
            # Extract splits for the player
            result = splits_manager.extract_player_splits_by_name(
                args.player_name, args.pfr_id, args.season
            )
            
            # Log results
            logger.info("Single Player Test Results:")
            logger.info(f"  Player: {args.player_name}")
            logger.info(f"  PFR ID: {args.pfr_id}")
            logger.info(f"  Season: {args.season}")
            logger.info(f"  Basic Splits: {len(result.basic_splits)}")
            logger.info(f"  Advanced Splits: {len(result.advanced_splits)}")
            logger.info(f"  Tables Discovered: {result.tables_discovered}")
            logger.info(f"  Tables Processed: {result.tables_processed}")
            logger.info(f"  Extraction Time: {result.extraction_time:.2f}s")
            
            if result.errors:
                logger.error("  Errors:")
                for error in result.errors:
                    logger.error(f"    {error}")
            
            if result.warnings:
                logger.warning("  Warnings:")
                for warning in result.warnings:
                    logger.warning(f"    {warning}")
            
            # Validate data if requested
            if args.validate:
                validation_results = splits_manager.validate_splits_data(
                    result.basic_splits, result.advanced_splits
                )
                
                logger.info("Data Validation Results:")
                logger.info(f"  Basic Splits Validated: {validation_results['basic_splits_validated']}")
                logger.info(f"  Advanced Splits Validated: {validation_results['advanced_splits_validated']}")
                
                if validation_results['errors']:
                    logger.error("  Validation Errors:")
                    for error in validation_results['errors']:
                        logger.error(f"    {error}")
                
                if validation_results['warnings']:
                    logger.warning("  Validation Warnings:")
                    for warning in validation_results['warnings']:
                        logger.warning(f"    {warning}")
            
            # Log sample data
            if result.basic_splits:
                logger.info("Sample Basic Split:")
                sample = result.basic_splits[0]
                logger.info(f"  Split: {sample.split}")
                logger.info(f"  Value: {sample.value}")
                logger.info(f"  Games: {sample.g}")
                logger.info(f"  Completions: {sample.cmp}")
                logger.info(f"  Attempts: {sample.att}")
                logger.info(f"  Yards: {sample.yds}")
                logger.info(f"  TDs: {sample.td}")
            
            if result.advanced_splits:
                logger.info("Sample Advanced Split:")
                sample = result.advanced_splits[0]
                logger.info(f"  Split: {sample.split}")
                logger.info(f"  Value: {sample.value}")
                logger.info(f"  Completions: {sample.cmp}")
                logger.info(f"  Attempts: {sample.att}")
                logger.info(f"  First Downs: {sample.first_downs}")
                logger.info(f"  Yards: {sample.yds}")
                logger.info(f"  TDs: {sample.td}")
            
            return 0 if not result.errors else 1
            
        except Exception as e:
            logger.error(f"Single player test failed: {str(e)}", exc_info=True)
            return 1
    
    def _test_comprehensive_extraction(self, args, scraper: EnhancedPFRScraper) -> int:
        """Test comprehensive splits extraction"""
        logger.info(f"Testing comprehensive splits extraction for {args.season} season")
        
        try:
            # Scrape all QB data including splits
            passing_stats, basic_splits, advanced_splits = scraper.scrape_all_qb_data(
                args.season, use_concurrent_splits=args.concurrent
            )
            
            # Log comprehensive results
            logger.info("Comprehensive Extraction Test Results:")
            logger.info(f"  Season: {args.season}")
            logger.info(f"  QB Players: {len(passing_stats)}")
            logger.info(f"  Basic Splits: {len(basic_splits)}")
            logger.info(f"  Advanced Splits: {len(advanced_splits)}")
            
            # Get splits manager summary
            summary = scraper.splits_manager.get_extraction_summary()
            logger.info("Splits Manager Summary:")
            logger.info(f"  Session ID: {summary['session_id']}")
            logger.info(f"  Processing Time: {summary['processing_time_seconds']:.2f}s")
            logger.info(f"  Success Rate: {summary['success_rate']:.1f}%")
            logger.info(f"  Average Basic Splits per Player: {summary['average_basic_splits_per_player']:.1f}")
            logger.info(f"  Average Advanced Splits per Player: {summary['average_advanced_splits_per_player']:.1f}")
            logger.info(f"  Total Errors: {summary['total_errors']}")
            logger.info(f"  Total Warnings: {summary['total_warnings']}")
            
            # Validate data if requested
            if args.validate:
                validation_results = scraper.splits_manager.validate_splits_data(
                    basic_splits, advanced_splits
                )
                
                logger.info("Data Validation Results:")
                logger.info(f"  Basic Splits Validated: {validation_results['basic_splits_validated']}")
                logger.info(f"  Advanced Splits Validated: {validation_results['advanced_splits_validated']}")
                
                if validation_results['errors']:
                    logger.error("  Validation Errors:")
                    for error in validation_results['errors']:
                        logger.error(f"    {error}")
                
                if validation_results['warnings']:
                    logger.warning("  Validation Warnings:")
                    for warning in validation_results['warnings']:
                        logger.warning(f"    {warning}")
            
            # Check for required columns (34 for basic, 20 for advanced)
            if basic_splits:
                sample_basic = basic_splits[0]
                basic_columns = [
                    'g', 'w', 'l', 't', 'cmp', 'att', 'inc', 'cmp_pct', 'yds', 'td',
                    'int', 'rate', 'sk', 'sk_yds', 'y_a', 'ay_a', 'a_g', 'y_g',
                    'rush_att', 'rush_yds', 'rush_y_a', 'rush_td', 'rush_a_g', 'rush_y_g',
                    'total_td', 'pts', 'fmb', 'fl', 'ff', 'fr', 'fr_yds', 'fr_td'
                ]
                missing_basic = [col for col in basic_columns if getattr(sample_basic, col, None) is None]
                if missing_basic:
                    logger.warning(f"Missing basic splits columns: {missing_basic}")
                else:
                    logger.info("All 34 basic splits columns present")
            
            if advanced_splits:
                sample_advanced = advanced_splits[0]
                advanced_columns = [
                    'cmp', 'att', 'inc', 'cmp_pct', 'yds', 'td', 'first_downs',
                    'int', 'rate', 'sk', 'sk_yds', 'y_a', 'ay_a',
                    'rush_att', 'rush_yds', 'rush_y_a', 'rush_td', 'rush_first_downs'
                ]
                missing_advanced = [col for col in advanced_columns if getattr(sample_advanced, col, None) is None]
                if missing_advanced:
                    logger.warning(f"Missing advanced splits columns: {missing_advanced}")
                else:
                    logger.info("All 20 advanced splits columns present")
            
            return 0 if len(passing_stats) > 0 else 1
            
        except Exception as e:
            logger.error(f"Comprehensive extraction test failed: {str(e)}", exc_info=True)
            return 1 