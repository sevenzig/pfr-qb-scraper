#!/usr/bin/env python3
"""
NFL QB Data Pipeline
Main pipeline for scraping NFL quarterback data from Pro Football Reference
"""

import logging
import os
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from src.scrapers.selenium_enhanced_scraper import SeleniumEnhancedPFRScraper
from src.database.db_manager import DatabaseManager
from src.models.qb_models import QBBasicStats, QBAdvancedStats, QBSplitStats, Player, Team, ScrapingLog
from src.utils.data_utils import (
    safe_int, safe_float, safe_percentage, clean_player_name,
    generate_player_id, extract_pfr_id, generate_session_id, calculate_processing_time
)
from src.config.config import config

# Configure logging
def setup_logging():
    """Setup comprehensive logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
        handlers=[
            logging.FileHandler(config.logging.file_path),
            logging.StreamHandler()
        ]
    )

# Setup logging and create logger
setup_logging()
logger = logging.getLogger(__name__)

class NFLQBDataPipeline:
    """Main pipeline orchestrating the entire scraping and database process"""
    
    def __init__(self, connection_string: Optional[str] = None, min_delay: float = 7.0, max_delay: float = 12.0):
        self.db_manager = DatabaseManager(connection_string or config.get_database_url())
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.session_id = generate_session_id()
        
        logger.info(f"Initialized NFL QB Data Pipeline (Session: {self.session_id})")

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------

    def reset_metrics(self):
        """Expose underlying scraper.reset_metrics for external callers."""
        # Create a temporary scraper to reset metrics
        with SeleniumEnhancedPFRScraper(min_delay=self.min_delay, max_delay=self.max_delay) as scraper:
            scraper.reset_metrics()

    def get_metrics(self):
        """Expose underlying scraper.get_scraping_metrics for metrics reporting."""
        # Create a temporary scraper to get metrics
        with SeleniumEnhancedPFRScraper(min_delay=self.min_delay, max_delay=self.max_delay) as scraper:
            return scraper.get_scraping_metrics()
    
    def run_pipeline(self, season: int, splits_only: bool = False, 
                    specific_players: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute the complete data pipeline
        
        Args:
            season: Season year to scrape
            splits_only: Only scrape splits data (skip main stats)
            specific_players: List of specific player names to scrape (if None, scrape all)
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        start_time = datetime.now()
        results = {
            'session_id': self.session_id,
            'season': season,
            'start_time': start_time,
            'end_time': None,
            'success': False,
            'qb_stats_count': 0,
            'qb_splits_count': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            logger.info(f"Starting NFL QB data pipeline for {season} season")
            
            # Validate configuration
            config_errors = config.validate()
            if config_errors:
                raise ValueError(f"Configuration errors: {', '.join(config_errors)}")
            
            # Test database connection
            if not self.db_manager.test_connection():
                raise ConnectionError("Database connection test failed")
            
            # Create tables if they don't exist
            self.db_manager.create_tables()
            
            qb_stats = []
            qb_splits: List[Any] = []
            advanced_splits: List[Any] = []
            
            if not splits_only:
                # Scrape main QB statistics using Selenium
                logger.info("Scraping main QB statistics using Selenium...")
                
                with SeleniumEnhancedPFRScraper(min_delay=self.min_delay, max_delay=self.max_delay) as scraper:
                    players, qb_stats = scraper.get_qb_main_stats(season)
                    
                    # Insert players first to satisfy foreign key constraints
                    self.db_manager.insert_players(players)
                    
                    # Insert into database
                    inserted_count = self.db_manager.insert_qb_basic_stats(qb_stats)
                    results['qb_stats_count'] = inserted_count
                    logger.info(f"Inserted {inserted_count} QB records into database")
            
            # Scrape splits data
            if qb_stats or specific_players:
                logger.info("Scraping QB splits data...")
                
                if specific_players:
                    # Filter QB stats to specific players
                    filtered_stats = [stat for stat in qb_stats 
                                    if stat.player_name in specific_players]
                    if not filtered_stats:
                        logger.warning(f"No QB stats found for specified players: {specific_players}")
                        return results
                else:
                    filtered_stats = qb_stats
                
                # Scrape splits with concurrent processing (basic & advanced)
                basic_splits, advanced_splits = self.scraper.process_players_concurrently(
                    filtered_stats,
                    max_workers=config.scraping.max_workers,
                )

                # Insert into respective tables
                if basic_splits:
                    inserted_basic = self.db_manager.insert_qb_splits(basic_splits)
                    results['qb_splits_count'] = inserted_basic
                    logger.info("Inserted %s basic QB splits", inserted_basic)
                else:
                    logger.warning("No basic QB splits found")

                if advanced_splits:
                    self.db_manager.insert_qb_splits_advanced(advanced_splits)
                else:
                    logger.warning("No advanced QB splits found")
            
            # Create scraping log
            scraping_log = self.scraper.create_scraping_log(season)
            scraping_log.total_qb_stats = results['qb_stats_count']
            scraping_log.total_qb_splits = results['qb_splits_count']
            scraping_log.total_splits_advanced = len(advanced_splits)
            
            # Insert scraping log
            self.db_manager.insert_scraping_log(scraping_log)
            
            # Update results
            results['end_time'] = datetime.now()
            results['success'] = True
            results['processing_time'] = calculate_processing_time(start_time, results['end_time'])
            results['scraping_metrics'] = self.scraper.get_scraping_metrics()
            
            # Log final statistics
            self._log_final_statistics(results)
            
            logger.info(f"Pipeline completed successfully for {season} season")
            
        except Exception as e:
            results['end_time'] = datetime.now()
            results['success'] = False
            results['errors'].append(str(e))
            logger.error(f"Pipeline failed: {e}")
            raise
        
        finally:
            # Always close database connections
            self.db_manager.close()
        
        return results
    
    def _log_final_statistics(self, results: Dict[str, Any]):
        """Log final pipeline statistics"""
        metrics = results.get('scraping_metrics')
        if metrics:
            logger.info("=== PIPELINE STATISTICS ===")
            logger.info(f"Session ID: {results['session_id']}")
            logger.info(f"Season: {results['season']}")
            logger.info(f"Processing Time: {results.get('processing_time', 0):.2f} seconds")
            logger.info(f"QB Stats Records: {results['qb_stats_count']}")
            logger.info(f"QB Splits Records: {results['qb_splits_count']}")
            logger.info(f"Total Requests: {metrics.total_requests}")
            logger.info(f"Successful Requests: {metrics.successful_requests}")
            logger.info(f"Failed Requests: {metrics.failed_requests}")
            logger.info(f"Success Rate: {metrics.get_success_rate():.1f}%")
            logger.info(f"Requests per Minute: {metrics.get_requests_per_minute():.1f}")
            logger.info(f"Rate Limit Violations: {metrics.rate_limit_violations}")
            logger.info(f"Errors: {len(metrics.errors)}")
            logger.info(f"Warnings: {len(metrics.warnings)}")
            
            if metrics.errors:
                logger.info("=== ERRORS ===")
                for error in metrics.errors[:10]:  # Show first 10 errors
                    logger.error(f"  {error}")
                if len(metrics.errors) > 10:
                    logger.error(f"  ... and {len(metrics.errors) - 10} more errors")
            
            if metrics.warnings:
                logger.info("=== WARNINGS ===")
                for warning in metrics.warnings[:10]:  # Show first 10 warnings
                    logger.warning(f"  {warning}")
                if len(metrics.warnings) > 10:
                    logger.warning(f"  ... and {len(metrics.warnings) - 10} more warnings")
    
    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """
        Validate data integrity across the database
        
        Returns:
            Dictionary of validation errors by table
        """
        logger.info("Validating data integrity...")
        return self.db_manager.validate_data_integrity()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database statistics
        """
        return self.db_manager.get_database_stats()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Returns:
            Health check results
        """
        logger.info("Performing health check...")
        return self.db_manager.health_check()

    def scrape_season_qbs(self, season: int, player_names: Optional[List[str]] = None):
        """
        Scrape QB data for a specific season, with an option to filter for specific players.
        
        Args:
            season: Season year to scrape
            player_names: Optional list of player names to filter for
        
        Returns:
            Dictionary with scraping results
        """
        # Scrape all main QB statistics first
        logger.info("Scraping all main QB statistics...")
        
        with SeleniumEnhancedPFRScraper(min_delay=self.min_delay, max_delay=self.max_delay) as scraper:
            players_to_process, stats_to_process = scraper.get_qb_main_stats(season, player_names=player_names)

            if not stats_to_process:
                logger.warning(f"No QB stats found for specified players: {player_names}")
                return {"success": False, "message": "No data found for specified players."}
            
            # Insert players first to satisfy foreign key constraints
            self.db_manager.insert_players(players_to_process)
            
            # Insert into database
            inserted_count = self.db_manager.insert_qb_basic_stats(stats_to_process)
            logger.info(f"Inserted {inserted_count} QB records into database")
            
            # Scrape splits data
            logger.info("Scraping QB splits data...")
            
            basic_splits, advanced_splits = scraper.process_players_concurrently(
                stats_to_process,
                max_workers=config.scraping.max_workers,
            )

            if basic_splits:
                inserted_basic = self.db_manager.insert_qb_splits(basic_splits)
                logger.info("Inserted %s basic QB split records", inserted_basic)
            else:
                logger.warning("No basic QB splits found")

            if advanced_splits:
                inserted_adv = self.db_manager.insert_qb_splits_advanced(advanced_splits)
                logger.info("Inserted %s advanced QB split records", inserted_adv)
            else:
                logger.warning("No advanced QB splits found")
            
            # Log results
            log = scraper.create_scraping_log(season)
            log.total_players = len(players_to_process)
            log.total_passing_stats = len(stats_to_process)
            log.total_splits = len(basic_splits)
            log.total_splits_advanced = len(advanced_splits)
            self.db_manager.insert_scraping_log(log)
        
        return {
            "success": True,
            "season": season,
            "qb_stats_count": len(stats_to_process),
            "qb_splits_count": len(basic_splits),
            "qb_splits_advanced_count": len(advanced_splits),
            "log_session_id": log.session_id
        }
    
    def scrape_team_qbs(self, team_code: str, season: int):
        """
        Scrape QB data for a specific team in a specific season
        
        Args:
            team_code: Team code (e.g., 'BUF', 'KAN', 'LAR')
            season: Season year to scrape
        
        Returns:
            Dictionary with scraping results
        """
        # Scrape main QB statistics
        logger.info(f"Scraping main QB statistics for {team_code} in {season} season...")
        
        with SeleniumEnhancedPFRScraper(min_delay=self.min_delay, max_delay=self.max_delay) as scraper:
            players, qb_stats = scraper.get_qb_main_stats(season, team_code)
            
            # Insert players first to satisfy foreign key constraints
            self.db_manager.insert_players(players)
            
            # Insert into database
            inserted_count = self.db_manager.insert_qb_basic_stats(qb_stats)
            logger.info(f"Inserted {inserted_count} QB records into database")
            
            # Scrape splits data using Selenium
            logger.info("Scraping QB splits data using Selenium...")
            
            basic_splits, advanced_splits = scraper.process_players_concurrently(
                qb_stats,
                max_workers=config.scraping.max_workers,
            )

            if basic_splits:
                self.db_manager.insert_qb_splits(basic_splits)
            if advanced_splits:
                self.db_manager.insert_qb_splits_advanced(advanced_splits)
            
            # Log results
            log = scraper.create_scraping_log(season)
            log.total_players = len(players)
            log.total_passing_stats = len(qb_stats)
            log.total_splits = len(basic_splits)
            log.total_splits_advanced = len(advanced_splits)
            self.db_manager.insert_scraping_log(log)
        
        return {
            "success": True,
            "season": season,
            "team_code": team_code,
            "qb_stats_count": len(qb_stats),
            "qb_splits_count": len(basic_splits),
            "qb_splits_advanced_count": len(advanced_splits),
            "log_session_id": log.session_id
        }

def main():
    """Main execution function"""
    # Setup logging
    setup_logging()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='NFL QB Data Scraping System')
    parser.add_argument('--season', type=int, default=config.app.target_season,
                       help='Season year to scrape (default: 2024)')
    parser.add_argument('--min-delay', type=float, default=7.0,
                       help='Minimum delay between requests in seconds (default: 7.0)')
    parser.add_argument('--max-delay', type=float, default=12.0,
                       help='Maximum delay between requests in seconds (default: 12.0)')
    parser.add_argument('--splits-only', action='store_true',
                       help='Only scrape splits data (skip main stats)')
    parser.add_argument('--players', nargs='+',
                       help='Specific player names to scrape')
    parser.add_argument('--validate', action='store_true',
                       help='Validate data integrity after scraping')
    parser.add_argument('--health-check', action='store_true',
                       help='Perform health check only')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics only')
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        pipeline = NFLQBDataPipeline(min_delay=args.min_delay, max_delay=args.max_delay)
        
        # Handle different modes
        if args.health_check:
            health_results = pipeline.health_check()
            print("=== HEALTH CHECK RESULTS ===")
            for key, value in health_results.items():
                print(f"{key}: {value}")
            return
        
        if args.stats:
            stats = pipeline.get_database_stats()
            print("=== DATABASE STATISTICS ===")
            for key, value in stats.items():
                print(f"{key}: {value}")
            return
        
        # Run main pipeline
        results = pipeline.run_pipeline(
            season=args.season,
            splits_only=args.splits_only,
            specific_players=args.players
        )
        
        # Validate data if requested
        if args.validate and results['success']:
            logger.info("Validating data integrity...")
            validation_errors = pipeline.validate_data_integrity()
            if validation_errors:
                logger.warning("Data integrity validation found issues:")
                for table, errors in validation_errors.items():
                    for error in errors:
                        logger.warning(f"  {table}: {error}")
            else:
                logger.info("Data integrity validation passed")
        
        # Print summary
        print("=== PIPELINE SUMMARY ===")
        print(f"Success: {results['success']}")
        print(f"Season: {results['season']}")
        print(f"QB Stats: {results['qb_stats_count']}")
        print(f"QB Splits: {results['qb_splits_count']}")
        print(f"Processing Time: {results.get('processing_time', 0):.2f} seconds")
        
        if not results['success']:
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 