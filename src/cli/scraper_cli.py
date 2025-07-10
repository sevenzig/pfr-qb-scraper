#!/usr/bin/env python3
"""
Command-line interface for NFL QB Data Scraping System
Provides various commands for scraping, monitoring, and data management

NOTE: This is the legacy CLI interface. For new functionality, use cli_main.py
      This file is maintained for backwards compatibility during migration.
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ..scrapers.nfl_qb_scraper import NFLQBDataPipeline
from ..database.db_manager import DatabaseManager
from ..config.config import config

logger = logging.getLogger(__name__)

class ScraperCLI:
    """Command-line interface for NFL QB scraper"""
    
    def __init__(self):
        self.pipeline = None
    
    def setup_logging(self, verbose: bool = False):
        """Setup logging configuration"""
        level = logging.DEBUG if verbose else logging.INFO
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/cli.log'),
                logging.StreamHandler()
            ]
        )
    
    def scrape_command(self, args):
        """Handle scrape command"""
        try:
            # Initialize pipeline
            self.pipeline = NFLQBDataPipeline(rate_limit_delay=args.rate_limit)
            
            # Run scraping
            results = self.pipeline.run_pipeline(
                season=args.season,
                splits_only=args.splits_only,
                specific_players=args.players
            )
            
            # Print results
            self._print_scraping_results(results)
            
            # Validate if requested
            if args.validate:
                self.validate_command(args)
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            sys.exit(1)
    
    def validate_command(self, args):
        """Handle validate command"""
        try:
            db_manager = DatabaseManager()
            
            logger.info("Validating data integrity...")
            validation_errors = db_manager.validate_data_integrity()
            
            if validation_errors:
                print("=== DATA INTEGRITY ISSUES ===")
                for table, errors in validation_errors.items():
                    print(f"\n{table.upper()}:")
                    for error in errors:
                        print(f"  - {error}")
            else:
                print("✓ Data integrity validation passed")
            
            # Show database stats
            stats = db_manager.get_database_stats()
            print("\n=== DATABASE STATISTICS ===")
            for key, value in stats.items():
                print(f"{key}: {value}")
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            sys.exit(1)
    
    def monitor_command(self, args):
        """Handle monitor command"""
        try:
            db_manager = DatabaseManager()
            
            # Get recent scraping sessions
            if args.recent:
                self._show_recent_sessions(db_manager, args.hours)
            
            # Show performance metrics
            if args.performance:
                self._show_performance_metrics(db_manager)
            
            # Show data quality metrics
            if args.quality:
                self._show_data_quality_metrics(db_manager)
            
            # Show all if no specific option
            if not any([args.recent, args.performance, args.quality]):
                self._show_recent_sessions(db_manager, 24)
                print()
                self._show_performance_metrics(db_manager)
                print()
                self._show_data_quality_metrics(db_manager)
            
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            sys.exit(1)
    
    def health_command(self, args):
        """Handle health command"""
        try:
            db_manager = DatabaseManager()
            
            logger.info("Performing health check...")
            health_results = db_manager.health_check()
            
            print("=== HEALTH CHECK RESULTS ===")
            for key, value in health_results.items():
                status = "✓" if value else "✗"
                print(f"{status} {key}: {value}")
            
            # Overall health
            all_healthy = all(
                health_results[k] for k in ['connection_ok', 'tables_exist', 'data_accessible']
            )
            if all_healthy:
                print("\n✓ All health checks passed")
            else:
                print("\n✗ Some health checks failed")
                sys.exit(1)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            sys.exit(1)
    
    def cleanup_command(self, args):
        """Handle cleanup command"""
        try:
            db_manager = DatabaseManager()
            
            logger.info(f"Cleaning up old scraping logs (older than {args.days} days)...")
            deleted_count = db_manager.cleanup_old_data(args.days)
            
            print(f"✓ Cleaned up {deleted_count} old scraping log records")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            sys.exit(1)
    
    def _print_scraping_results(self, results: Dict[str, Any]):
        """Print scraping results in a formatted way"""
        print("=== SCRAPING RESULTS ===")
        print(f"Session ID: {results['session_id']}")
        print(f"Season: {results['season']}")
        print(f"Success: {'✓' if results['success'] else '✗'}")
        print(f"Processing Time: {results.get('processing_time', 0):.2f} seconds")
        print(f"QB Stats Records: {results['qb_stats_count']}")
        print(f"QB Splits Records: {results['qb_splits_count']}")
        
        if results.get('scraping_metrics'):
            metrics = results['scraping_metrics']
            print(f"\n=== PERFORMANCE METRICS ===")
            print(f"Total Requests: {metrics.total_requests}")
            print(f"Successful Requests: {metrics.successful_requests}")
            print(f"Failed Requests: {metrics.failed_requests}")
            print(f"Success Rate: {metrics.get_success_rate():.1f}%")
            print(f"Requests per Minute: {metrics.get_requests_per_minute():.1f}")
            print(f"Rate Limit Violations: {metrics.rate_limit_violations}")
        
        if results.get('warnings'):
            print(f"\n=== WARNINGS ({len(results['warnings'])}) ===")
            for warning in results['warnings'][:5]:  # Show first 5 warnings
                print(f"  {warning}")
            if len(results['warnings']) > 5:
                print(f"  ... and {len(results['warnings']) - 5} more warnings")
    
    def _show_recent_sessions(self, db_manager: DatabaseManager, hours: int):
        """Show recent scraping sessions"""
        print(f"=== RECENT SCRAPING SESSIONS (Last {hours} hours) ===")
        
        # This would require a query to get recent sessions
        # For now, just show a placeholder
        print("Recent sessions feature not yet implemented")
    
    def _show_performance_metrics(self, db_manager: DatabaseManager):
        """Show performance metrics"""
        print("=== PERFORMANCE METRICS ===")
        
        stats = db_manager.get_database_stats()
        print(f"Total QB Stats Records: {stats.get('qb_stats_count', 0)}")
        print(f"Total QB Splits Records: {stats.get('qb_splits_count', 0)}")
        print(f"Unique Players: {stats.get('unique_players', 0)}")
        print(f"Unique Teams: {stats.get('unique_teams', 0)}")
        print(f"Seasons Covered: {stats.get('unique_seasons', 0)}")
    
    def _show_data_quality_metrics(self, db_manager: DatabaseManager):
        """Show data quality metrics"""
        print("=== DATA QUALITY METRICS ===")
        
        validation_errors = db_manager.validate_data_integrity()
        total_errors = sum(len(errors) for errors in validation_errors.values())
        
        if total_errors == 0:
            print("✓ No data integrity issues found")
        else:
            print(f"✗ Found {total_errors} data integrity issues")
            for table, errors in validation_errors.items():
                if errors:
                    print(f"  {table}: {len(errors)} issues")

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='NFL QB Data Scraping System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape 2024 season data
  python scraper_cli.py scrape --season 2024
  
  # Scrape only splits for specific players
  python scraper_cli.py scrape --splits-only --players "Patrick Mahomes" "Josh Allen"
  
  # Validate data integrity
  python scraper_cli.py validate
  
  # Monitor system health
  python scraper_cli.py health
  
  # Show recent activity
  python scraper_cli.py monitor --recent --hours 24
        """
    )
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape QB data')
    scrape_parser.add_argument('--season', type=int, default=config.app.target_season,
                              help='Season year to scrape (default: 2024)')
    scrape_parser.add_argument('--rate-limit', type=float, default=config.scraping.rate_limit_delay,
                              help='Rate limit delay in seconds (default: 3.0)')
    scrape_parser.add_argument('--splits-only', action='store_true',
                              help='Only scrape splits data (skip main stats)')
    scrape_parser.add_argument('--players', nargs='+',
                              help='Specific player names to scrape')
    scrape_parser.add_argument('--validate', action='store_true',
                              help='Validate data integrity after scraping')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate data integrity')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor system and data')
    monitor_parser.add_argument('--recent', action='store_true',
                               help='Show recent scraping sessions')
    monitor_parser.add_argument('--performance', action='store_true',
                               help='Show performance metrics')
    monitor_parser.add_argument('--quality', action='store_true',
                               help='Show data quality metrics')
    monitor_parser.add_argument('--hours', type=int, default=24,
                               help='Hours to look back for recent sessions (default: 24)')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Perform health check')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data')
    cleanup_parser.add_argument('--days', type=int, default=30,
                               help='Days to keep logs (default: 30)')
    
    return parser

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = ScraperCLI()
    cli.setup_logging(args.verbose)
    
    # Execute command
    if args.command == 'scrape':
        cli.scrape_command(args)
    elif args.command == 'validate':
        cli.validate_command(args)
    elif args.command == 'monitor':
        cli.monitor_command(args)
    elif args.command == 'health':
        cli.health_command(args)
    elif args.command == 'cleanup':
        cli.cleanup_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 