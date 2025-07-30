#!/usr/bin/env python3
"""
Scraping Operation for NFL QB Data
Orchestrates comprehensive scraping operations with enhanced splits extraction
"""

import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from src.database.db_manager import DatabaseManager
from src.scrapers.nfl_qb_scraper import NFLQBDataPipeline
from src.scrapers.enhanced_scraper import EnhancedPFRScraper
from src.core.splits_manager import SplitsManager
from src.core.selenium_manager import SeleniumManager, SeleniumConfig
from src.models.qb_models import QBBasicStats, QBSplitsType1, QBSplitsType2
from src.config.config import config

logger = logging.getLogger(__name__)


@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    success: bool
    season: int
    message: str
    scraped_records: int = 0
    saved_records: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class ScrapingOperation:
    """Orchestrates scraping operations with enhanced splits extraction"""
    
    def __init__(self, config, db_manager: DatabaseManager, min_delay: float = 7.0, max_delay: float = 12.0):
        self.config = config
        self.db_manager = db_manager
        self.min_delay = min_delay
        self.max_delay = max_delay
        
        # Initialize enhanced components with Selenium manager
        selenium_config = SeleniumConfig(
            headless=True,
            human_behavior_delay=(min_delay, max_delay)
        )
        self.selenium_manager = SeleniumManager(selenium_config)
        
        # Initialize splits manager first
        self.splits_manager = SplitsManager(self.selenium_manager)
        
        # Initialize enhanced scraper with the splits manager
        self.enhanced_scraper = EnhancedPFRScraper(rate_limit_delay=min_delay, splits_manager=self.splits_manager)
        
        # Initialize legacy pipeline for backwards compatibility
        self.legacy_pipeline = NFLQBDataPipeline(
            connection_string=config.get_database_url(),
            min_delay=min_delay,
            max_delay=max_delay
        )
        
        logger.info(f"Initialized ScrapingOperation with enhanced splits extraction")
    
    def execute(self, season: int, player_names: Optional[List[str]] = None, splits_only: bool = False) -> ScrapingResult:
        """
        Execute the scraping operation for a given season with enhanced splits extraction.

        Args:
            season: The season to scrape.
            player_names: Optional list of player names to scrape.
            splits_only: If True, only scrape splits data (skip main stats).

        Returns:
            A ScrapingResult object with the outcome.
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting enhanced scraping operation for season {season}")
            
            if splits_only:
                return self._execute_splits_only(season, player_names)
            elif player_names:
                return self._execute_specific_players(season, player_names)
            else:
                return self._execute_full_season(season)
                
        except Exception as e:
            logger.error(f"Scraping operation failed: {e}", exc_info=True)
            return ScrapingResult(
                success=False,
                season=season,
                message=str(e),
                errors=[str(e)],
                processing_time=time.time() - start_time
            )
        finally:
            processing_time = time.time() - start_time
            logger.info(f"Scraping operation completed in {processing_time:.2f} seconds")
    
    def _execute_full_season(self, season: int) -> ScrapingResult:
        """Execute full season scraping with enhanced splits extraction"""
        logger.info(f"Executing full season scraping for {season}")
        
        try:
            # Use enhanced scraper for comprehensive data extraction with context manager
            with self.enhanced_scraper as scraper:
                passing_stats, basic_splits, advanced_splits = scraper.scrape_all_qb_data(
                    season=season, 
                    use_concurrent_splits=False  # Respectful scraping by default
                )
            
            if not passing_stats:
                return ScrapingResult(
                    success=False,
                    season=season,
                    message="No QB passing stats found for the season",
                    errors=["No data found"]
                )
            
            # Insert data into database
            inserted_stats = self._insert_passing_stats(passing_stats)
            inserted_basic_splits = self._insert_basic_splits(basic_splits)
            inserted_advanced_splits = self._insert_advanced_splits(advanced_splits)
            
            # Get comprehensive metrics
            splits_summary = self.splits_manager.get_extraction_summary()
            
            # Create scraping log
            self._create_scraping_log(season, len(passing_stats), len(basic_splits), len(advanced_splits))
            
            return ScrapingResult(
                success=True,
                season=season,
                message=f"Successfully scraped {len(passing_stats)} QB records with enhanced splits extraction",
                scraped_records=len(passing_stats),
                saved_records=inserted_stats,
                processing_time=time.time() - time.time(),  # Will be set by caller
                warnings=splits_summary.get('warnings', [])
            )
            
        except Exception as e:
            logger.error(f"Full season scraping failed: {e}", exc_info=True)
            return ScrapingResult(
                success=False,
                season=season,
                message=f"Full season scraping failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _execute_specific_players(self, season: int, player_names: List[str]) -> ScrapingResult:
        """Execute scraping for specific players with enhanced splits extraction"""
        logger.info(f"Executing specific player scraping for {len(player_names)} players")
        
        try:
            # First get basic stats for the specified players
            passing_stats = []
            basic_splits = []
            advanced_splits = []
            
            # Use enhanced scraper with context manager
            with self.enhanced_scraper as scraper:
                for player_name in player_names:
                    logger.info(f"Processing player: {player_name}")
                    
                    # Get basic stats for this player
                    players, player_stats = scraper.get_qb_main_stats(season, [player_name])
                    if player_stats:
                        passing_stats.extend(player_stats)
                        
                        # Extract splits for this player
                        for stat in player_stats:
                            splits_result = self.splits_manager.extract_player_splits_by_name(
                                stat.player_name, stat.pfr_id, season
                            )
                            basic_splits.extend(splits_result.basic_splits)
                            advanced_splits.extend(splits_result.advanced_splits)
            
            if not passing_stats:
                return ScrapingResult(
                    success=False,
                    season=season,
                    message=f"No QB stats found for specified players: {player_names}",
                    errors=["No data found for specified players"]
                )
            
            # Insert data into database
            inserted_stats = self._insert_passing_stats(passing_stats)
            inserted_basic_splits = self._insert_basic_splits(basic_splits)
            inserted_advanced_splits = self._insert_advanced_splits(advanced_splits)
            
            return ScrapingResult(
                success=True,
                season=season,
                message=f"Successfully scraped {len(passing_stats)} QB records for specified players",
                scraped_records=len(passing_stats),
                saved_records=inserted_stats,
                processing_time=time.time() - time.time()  # Will be set by caller
            )
            
        except Exception as e:
            logger.error(f"Specific player scraping failed: {e}", exc_info=True)
            return ScrapingResult(
                success=False,
                season=season,
                message=f"Specific player scraping failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _execute_splits_only(self, season: int, player_names: Optional[List[str]] = None) -> ScrapingResult:
        """Execute splits-only scraping with enhanced splits extraction"""
        logger.info(f"Executing splits-only scraping for season {season}")
        
        try:
            # Get existing QB stats from database for splits extraction
            existing_stats = self.db_manager.get_qb_stats_for_season(season)
            
            # If no existing stats and no specific players requested, return error
            if not existing_stats and not player_names:
                return ScrapingResult(
                    success=False,
                    season=season,
                    message=f"No existing QB stats found in database for season {season}",
                    errors=["No existing data found"]
                )
            
            # If specific players requested, try to extract splits even if they don't exist in main stats
            if player_names:
                # First try to get existing stats for these players
                if existing_stats:
                    existing_stats = [stat for stat in existing_stats 
                                    if stat.player_name in player_names]
                
                # For players not in existing stats, create placeholder stats for splits extraction
                missing_players = []
                for player_name in player_names:
                    if not existing_stats or not any(stat.player_name == player_name for stat in existing_stats):
                        missing_players.append(player_name)
                
                # Create placeholder stats for missing players
                for player_name in missing_players:
                    # Try to extract PFR ID from the player name or use a default pattern
                    # This is a simplified approach - in production you might want to look up PFR IDs
                    pfr_id = self._get_pfr_id_for_player(player_name, season)
                    if pfr_id:
                        placeholder_stat = type('obj', (object,), {
                            'pfr_id': pfr_id,
                            'player_name': player_name,
                            'season': season,
                            'player_url': f"https://www.pro-football-reference.com/players/{pfr_id[0]}/{pfr_id}/",
                            'scraped_at': datetime.now()
                        })()
                        existing_stats.append(placeholder_stat)
                        logger.info(f"Created placeholder stats for {player_name} (PFR ID: {pfr_id})")
            
            # If still no stats to work with, return error
            if not existing_stats:
                return ScrapingResult(
                    success=False,
                    season=season,
                    message=f"No QB stats available for splits extraction",
                    errors=["No data available for splits extraction"]
                )
            
            # Extract splits using enhanced splits manager
            basic_splits, advanced_splits = self.splits_manager.extract_all_player_splits(
                existing_stats, use_concurrent=False
            )
            
            # Insert splits data
            inserted_basic_splits = self._insert_basic_splits(basic_splits)
            inserted_advanced_splits = self._insert_advanced_splits(advanced_splits)
            
            # Get splits manager summary
            splits_summary = self.splits_manager.get_extraction_summary()
            
            return ScrapingResult(
                success=True,
                season=season,
                message=f"Successfully extracted {len(basic_splits)} basic and {len(advanced_splits)} advanced splits",
                scraped_records=len(basic_splits) + len(advanced_splits),
                saved_records=inserted_basic_splits + inserted_advanced_splits,
                processing_time=time.time() - time.time(),  # Will be set by caller
                warnings=splits_summary.get('warnings', [])
            )
            
        except Exception as e:
            logger.error(f"Splits-only scraping failed: {e}", exc_info=True)
            return ScrapingResult(
                success=False,
                season=season,
                message=f"Splits-only scraping failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _insert_passing_stats(self, passing_stats: List[QBBasicStats]) -> int:
        """Insert passing stats into database"""
        if not passing_stats:
            return 0
        
        try:
            # Insert players first to satisfy foreign key constraints
            players = []
            for stat in passing_stats:
                # Create player object from QB stats
                player = type('obj', (object,), {
                    'pfr_id': stat.pfr_id,
                    'player_name': stat.player_name,
                    'position': 'QB',
                    'pfr_url': stat.player_url,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })()
                players.append(player)
            
            self.db_manager.insert_players(players)
            
            # Insert QB stats
            inserted_count = self.db_manager.insert_qb_basic_stats(passing_stats)
            logger.info(f"Inserted {inserted_count} QB passing stats")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Failed to insert passing stats: {e}")
            raise
    
    def _insert_basic_splits(self, basic_splits: List[QBSplitsType1]) -> int:
        """Insert basic splits into database"""
        if not basic_splits:
            return 0
        
        try:
            inserted_count = self.db_manager.insert_qb_splits(basic_splits)
            logger.info(f"Inserted {inserted_count} basic QB splits")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Failed to insert basic splits: {e}")
            raise
    
    def _insert_advanced_splits(self, advanced_splits: List[QBSplitsType2]) -> int:
        """Insert advanced splits into database"""
        if not advanced_splits:
            return 0
        
        try:
            inserted_count = self.db_manager.insert_qb_splits_advanced(advanced_splits)
            logger.info(f"Inserted {inserted_count} advanced QB splits")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Failed to insert advanced splits: {e}")
            raise
    
    def _create_scraping_log(self, season: int, stats_count: int, basic_splits_count: int, advanced_splits_count: int):
        """Create and insert scraping log"""
        try:
            from models.qb_models import ScrapingLog
            from src.utils.data_utils import generate_session_id
            
            log = ScrapingLog(
                session_id=generate_session_id(),
                season=season,
                start_time=datetime.now(),
                end_time=datetime.now(),
                total_players=stats_count,
                total_passing_stats=stats_count,
                total_splits=basic_splits_count,
                total_splits_advanced=advanced_splits_count,
                errors=[],
                warnings=[],
                rate_limit_violations=0,
                processing_time_seconds=0.0
            )
            
            self.db_manager.insert_scraping_log(log)
            logger.info("Created scraping log entry")
            
        except Exception as e:
            logger.warning(f"Failed to create scraping log: {e}")
    
    def get_metrics(self):
        """Get scraping metrics from enhanced scraper"""
        try:
            return self.enhanced_scraper.metrics
        except AttributeError:
            return None
    
    def reset_metrics(self):
        """Reset scraping metrics"""
        try:
            self.enhanced_scraper.metrics = type('obj', (object,), {
                'start_time': datetime.now(),
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'errors': [],
                'warnings': [],
                'rate_limit_violations': 0
            })()
        except AttributeError:
            pass 

    def _get_pfr_id_for_player(self, player_name: str, season: int) -> Optional[str]:
        """Get PFR ID for a player by name and season"""
        # This is a simplified lookup - in production you might want a more robust approach
        # For now, we'll use some common patterns for known players
        
        # Common PFR ID patterns for well-known players
        pfr_id_mapping = {
            "Joe Burrow": "burrjo01",
            "Patrick Mahomes": "mahompa00",
            "Josh Allen": "allenjo02",
            "Lamar Jackson": "jackla00",
            "Justin Herbert": "herbju00",
            "Dak Prescott": "prescda01",
            "Jalen Hurts": "hurtja00",
            "Tua Tagovailoa": "tagovtu00",
            "Kirk Cousins": "couski01",
            "Aaron Rodgers": "rodgaar00"
        }
        
        return pfr_id_mapping.get(player_name) 