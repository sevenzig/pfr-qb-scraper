#!/usr/bin/env python3
"""
Scrape Command for NFL QB Data Scraping
CLI command for executing comprehensive scraping operations
"""

import logging
import argparse
from typing import Dict, Any, Optional, List
from argparse import ArgumentParser, Namespace

from src.cli.base_command import BaseCommand
from src.operations.scraping_operation import ScrapingOperation
from src.database.db_manager import DatabaseManager
from src.config.config import config


class ScrapeCommand(BaseCommand):
    """Command to scrape NFL QB data"""
    
    @property
    def name(self) -> str:
        """Command name"""
        return "scrape"
    
    @property
    def description(self) -> str:
        """Command description"""
        return "Scrape NFL QB data from Pro Football Reference"
    
    @property
    def aliases(self) -> List[str]:
        """Command aliases"""
        return ["s"]
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add scrape-specific arguments"""
        parser.add_argument(
            '--season', 
            type=int, 
            default=self.config.app.target_season,
            help=f'Season year to scrape (default: {self.config.app.target_season})'
        )
        parser.add_argument(
            '--min-delay', 
            type=float, 
            default=7.0,
            help='Minimum delay between requests in seconds (default: 7.0)'
        )
        parser.add_argument(
            '--max-delay', 
            type=float, 
            default=12.0,
            help='Maximum delay between requests in seconds (default: 12.0)'
        )
        parser.add_argument(
            '--splits-only', 
            action='store_true',
            help='Only scrape splits data (skip main stats)'
        )
        parser.add_argument(
            '--players', 
            nargs='+',
            help='Specific player names to scrape'
        )
        parser.add_argument(
            '--validate', 
            action='store_true',
            help='Validate data integrity after scraping'
        )
        parser.add_argument(
            '--progress', 
            action='store_true',
            help='Enable detailed progress tracking'
        )
    
    def validate_args(self, args: Namespace) -> List[str]:
        """Validate scrape command arguments"""
        errors = []
        
        # Validate season
        if args.season < 1970 or args.season > 2030:
            errors.append(f"Invalid season: {args.season}. Must be between 1970 and 2030.")
        
        # Validate min delay
        if args.min_delay < 0.1 or args.min_delay > 60:
            errors.append(f"Invalid min delay: {args.min_delay}. Must be between 0.1 and 60 seconds.")
        
        # Validate max delay
        if args.max_delay < 0.1 or args.max_delay > 60:
            errors.append(f"Invalid max delay: {args.max_delay}. Must be between 0.1 and 60 seconds.")
        
        # Validate min <= max
        if args.min_delay > args.max_delay:
            errors.append(f"Min delay ({args.min_delay}) cannot be greater than max delay ({args.max_delay}).")
        
        # Validate player names if provided
        if args.players:
            for player in args.players:
                if not player.strip():
                    errors.append("Player names cannot be empty.")
                    break
        
        return errors
    
    def run(self, args: Namespace) -> int:
        """Execute the scrape command"""
        try:
            # Validate arguments
            validation_errors = self.validate_args(args)
            if validation_errors:
                for error in validation_errors:
                    self.print_error(error)
                return 1
            
            self.logger.info(f"Starting scrape for season {args.season}")
            
            # Show configuration
            self.print_section_header("Scraping Configuration")
            self.print_info(f"Season: {args.season}")
            self.print_info(f"Delay Range: {args.min_delay}s - {args.max_delay}s")
            self.print_info(f"Splits Only: {'Yes' if args.splits_only else 'No'}")
            self.print_info(f"Progress Tracking: {'Yes' if args.progress else 'No'}")
            if args.players:
                self.print_info(f"Players: {', '.join(args.players)}")
            
            # Run scraping
            self.print_section_header("Running Scraper")
            
            # Initialize database manager and scraping operation
            db_manager = DatabaseManager()
            scraping_operation = ScrapingOperation(
                config=self.config,
                db_manager=db_manager,
                min_delay=args.min_delay,
                max_delay=args.max_delay
            )
            
            # Execute the scraping operation
            result = scraping_operation.execute(
                args.season, 
                player_names=args.players,
                splits_only=args.splits_only
            )
            
            # Print results
            self._print_scraping_results(result, scraping_operation)
            
            # Validate if requested
            if args.validate and result.success:
                self.logger.info("Running post-scrape validation")
                return self._run_validation()
            
            return 0 if result.success else 1
            
        except (ConnectionError, OSError) as e:
            return self.handle_error(e, "Connection error during scraping")
        except ValueError as e:
            return self.handle_error(e, "Invalid data during scraping")
        except Exception as e:
            return self.handle_error(e, "Scraping failed")
    
    def _print_scraping_results(self, result, scraping_operation) -> None:
        """Print scraping results in a formatted way"""
        self.print_section_header("Scraping Results")
        
        self.print_info(f"Season: {result.season}")
        self.print_info(f"Scraped Records: {result.scraped_records}")
        self.print_info(f"Saved Records: {result.saved_records}")
        self.print_info(f"Message: {result.message}")
        
        if result.success:
            self.print_success("Scraping completed successfully")
        else:
            self.print_error("Scraping failed")
            if result.errors:
                for error in result.errors:
                    self.print_error(f"  - {error}")
        
        # Show warnings if any
        if result.warnings:
            self.print_section_header("Warnings")
            for warning in result.warnings:
                self.print_warning(f"  - {warning}")
        
        # Show enhanced splits extraction summary if available
        try:
            splits_summary = scraping_operation.splits_manager.get_extraction_summary()
            if splits_summary:
                self._print_splits_summary(splits_summary)
        except (AttributeError, TypeError) as e:
            self.logger.debug(f"Splits summary not available: {e}")
        except Exception as e:
            self.logger.debug(f"Could not get splits summary: {e}")
        
        # Show performance metrics if available
        try:
            metrics = scraping_operation.get_metrics()
            if metrics:
                self._print_performance_metrics(metrics)
        except (AttributeError, TypeError) as e:
            self.logger.debug(f"Metrics not available: {e}")
        except Exception as e:
            self.logger.debug(f"Could not get metrics: {e}")
    
    def _print_splits_summary(self, splits_summary: Dict[str, Any]) -> None:
        """Print enhanced splits extraction summary"""
        self.print_section_header("Enhanced Splits Extraction Summary")
        
        self.print_info(f"Session ID: {splits_summary.get('session_id', 'N/A')}")
        self.print_info(f"Processing Time: {splits_summary.get('processing_time_seconds', 0):.2f}s")
        self.print_info(f"Total Players: {splits_summary.get('total_players', 0)}")
        self.print_info(f"Successful Extractions: {splits_summary.get('successful_extractions', 0)}")
        self.print_info(f"Failed Extractions: {splits_summary.get('failed_extractions', 0)}")
        self.print_info(f"Success Rate: {splits_summary.get('success_rate', 0):.1f}%")
        
        # Splits data summary
        self.print_info(f"Total Basic Splits: {splits_summary.get('total_basic_splits', 0)}")
        self.print_info(f"Total Advanced Splits: {splits_summary.get('total_advanced_splits', 0)}")
        self.print_info(f"Average Basic Splits per Player: {splits_summary.get('average_basic_splits_per_player', 0):.1f}")
        self.print_info(f"Average Advanced Splits per Player: {splits_summary.get('average_advanced_splits_per_player', 0):.1f}")
        
        # Quality metrics
        self.print_info(f"Total Errors: {splits_summary.get('total_errors', 0)}")
        self.print_info(f"Total Warnings: {splits_summary.get('total_warnings', 0)}")
        self.print_info(f"Rate Limit Violations: {splits_summary.get('rate_limit_violations', 0)}")
        
        # Quality assessment
        success_rate = splits_summary.get('success_rate', 0)
        if success_rate >= 90:
            self.print_success("Excellent extraction quality")
        elif success_rate >= 80:
            self.print_info("Good extraction quality")
        elif success_rate >= 70:
            self.print_warning("Acceptable extraction quality")
        else:
            self.print_error("Poor extraction quality - review needed")
    
    def _print_performance_metrics(self, metrics) -> None:
        """Print performance metrics"""
        self.print_section_header("Performance Metrics")
        
        total_requests = getattr(metrics, 'total_requests', 0)
        successful_requests = getattr(metrics, 'successful_requests', 0)
        failed_requests = getattr(metrics, 'failed_requests', 0)
        success_rate = getattr(metrics, 'get_success_rate', lambda: 0)()
        requests_per_minute = getattr(metrics, 'get_requests_per_minute', lambda: 0)()
        rate_limit_violations = getattr(metrics, 'rate_limit_violations', 0)
        
        self.print_info(f"Total Requests: {total_requests}")
        self.print_info(f"Successful Requests: {successful_requests}")
        self.print_info(f"Failed Requests: {failed_requests}")
        self.print_info(f"Success Rate: {success_rate:.1f}%")
        self.print_info(f"Requests per Minute: {requests_per_minute:.1f}")
        self.print_info(f"Rate Limit Violations: {rate_limit_violations}")
        
        # Performance assessment
        if success_rate >= 95:
            self.print_success("Excellent performance")
        elif success_rate >= 85:
            self.print_info("Good performance")
        elif success_rate >= 75:
            self.print_warning("Acceptable performance")
        else:
            self.print_error("Poor performance - review needed")
        
        if rate_limit_violations > 0:
            self.print_warning(f"Rate limit violations detected: {rate_limit_violations}")
        else:
            self.print_success("No rate limit violations")
    
    def _run_validation(self) -> int:
        """Run data validation after scraping"""
        try:
            from src.cli.commands.validate_command import ValidateCommand
            
            # Create validate command and run it
            validate_cmd = ValidateCommand()
            validate_cmd.setup_logging(self.logger.isEnabledFor(logging.DEBUG))
            
            # Create minimal args for validation
            from argparse import Namespace
            validate_args = Namespace()
            
            return validate_cmd.run(validate_args)
            
        except ImportError as e:
            return self.handle_error(e, "Validation module not available")
        except Exception as e:
            return self.handle_error(e, "Post-scrape validation failed") 