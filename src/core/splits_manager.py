#!/usr/bin/env python3
"""
Splits Manager for NFL QB Data Scraping
Integrates dedicated splits extractor with existing scraper architecture
Provides comprehensive QB splits extraction with proper error handling and logging
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models.qb_models import QBSplitsType1, QBSplitsType2, QBPassingStats
from ..scrapers.splits_extractor import SplitsExtractor, SplitsExtractionResult
from .selenium_manager import SeleniumManager
from ..config.config import config
from ..utils.data_utils import (
    generate_session_id, calculate_processing_time,
    build_enhanced_splits_url, validate_splits_url
)

logger = logging.getLogger(__name__)


@dataclass
class SplitsManagerMetrics:
    """Metrics tracking for splits manager operations"""
    start_time: datetime
    total_players: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    total_basic_splits: int = 0
    total_advanced_splits: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    rate_limit_violations: int = 0
    
    def add_extraction_result(self, result: SplitsExtractionResult):
        """Add extraction result to metrics"""
        self.total_basic_splits += len(result.basic_splits)
        self.total_advanced_splits += len(result.advanced_splits)
        self.total_errors += len(result.errors)
        self.total_warnings += len(result.warnings)
        
        if result.errors:
            self.failed_extractions += 1
        else:
            self.successful_extractions += 1


class SplitsManager:
    """
    Comprehensive splits manager for QB data extraction
    
    Features:
    - Integrated splits extraction for all QB players
    - Comprehensive error handling and logging
    - Rate limiting and respectful scraping
    - Progress tracking and metrics collection
    - Support for both basic and advanced splits
    - Validation and quality assurance
    """
    
    def __init__(self, selenium_manager: SeleniumManager):
        self.selenium_manager = selenium_manager
        self.splits_extractor = SplitsExtractor(selenium_manager)
        self.metrics = SplitsManagerMetrics(start_time=datetime.now())
        
        # Configuration
        self.max_workers = config.scraping.max_workers
        self.rate_limit_delay = config.scraping.rate_limit_delay
        self.session_id = generate_session_id()
        
        logger.info(f"Initialized SplitsManager with session ID: {self.session_id}")
    
    def extract_all_player_splits(self, qb_stats: List[QBPassingStats], 
                                 use_concurrent: bool = False) -> Tuple[List[QBSplitsType1], List[QBSplitsType2]]:
        """
        Extract splits data for all QB players
        
        Args:
            qb_stats: List of QB passing stats to extract splits for
            use_concurrent: Whether to use concurrent processing
            
        Returns:
            Tuple of (basic_splits, advanced_splits) lists
        """
        logger.info(f"Starting splits extraction for {len(qb_stats)} players")
        self.metrics.total_players = len(qb_stats)
        
        all_basic_splits = []
        all_advanced_splits = []
        
        if use_concurrent and self.max_workers > 1:
            logger.info(f"Using concurrent processing with {self.max_workers} workers")
            basic_splits, advanced_splits = self._extract_splits_concurrent(qb_stats)
        else:
            logger.info("Using sequential processing")
            basic_splits, advanced_splits = self._extract_splits_sequential(qb_stats)
        
        all_basic_splits.extend(basic_splits)
        all_advanced_splits.extend(advanced_splits)
        
        # Log final results
        processing_time = calculate_processing_time(self.metrics.start_time, datetime.now())
        logger.info(f"Splits extraction completed: "
                   f"{len(all_basic_splits)} basic splits, {len(all_advanced_splits)} advanced splits "
                   f"({self.metrics.successful_extractions}/{self.metrics.total_players} successful) "
                   f"in {processing_time:.2f}s")
        
        return all_basic_splits, all_advanced_splits
    
    def _extract_splits_sequential(self, qb_stats: List[QBPassingStats]) -> Tuple[List[QBSplitsType1], List[QBSplitsType2]]:
        """Extract splits data sequentially"""
        all_basic_splits = []
        all_advanced_splits = []
        
        for i, qb_stat in enumerate(qb_stats, 1):
            try:
                logger.info(f"Processing splits for {qb_stat.player_name} ({i}/{len(qb_stats)})")
                
                # Extract splits for this player
                result = self.splits_extractor.extract_player_splits(
                    qb_stat.pfr_id, qb_stat.player_name, qb_stat.season, datetime.now()
                )
                
                # Add to metrics
                self.metrics.add_extraction_result(result)
                
                # Add extracted data
                all_basic_splits.extend(result.basic_splits)
                all_advanced_splits.extend(result.advanced_splits)
                
                # Log progress
                if result.errors:
                    logger.warning(f"Errors extracting splits for {qb_stat.player_name}: {result.errors}")
                else:
                    logger.info(f"Successfully extracted {len(result.basic_splits)} basic and "
                               f"{len(result.advanced_splits)} advanced splits for {qb_stat.player_name}")
                
                # Rate limiting
                if i < len(qb_stats):  # Don't delay after the last player
                    time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                error_msg = f"Unexpected error processing splits for {qb_stat.player_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.metrics.failed_extractions += 1
                self.metrics.total_errors += 1
                continue
        
        return all_basic_splits, all_advanced_splits
    
    def _extract_splits_concurrent(self, qb_stats: List[QBPassingStats]) -> Tuple[List[QBSplitsType1], List[QBSplitsType2]]:
        """Extract splits data concurrently"""
        all_basic_splits = []
        all_advanced_splits = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks
            future_to_player = {}
            for qb_stat in qb_stats:
                future = executor.submit(
                    self._extract_single_player_splits,
                    qb_stat
                )
                future_to_player[future] = qb_stat.player_name
            
            # Collect results
            for future in as_completed(future_to_player):
                player_name = future_to_player[future]
                try:
                    result = future.result()
                    
                    # Add to metrics
                    self.metrics.add_extraction_result(result)
                    
                    # Add extracted data
                    all_basic_splits.extend(result.basic_splits)
                    all_advanced_splits.extend(result.advanced_splits)
                    
                    # Log progress
                    if result.errors:
                        logger.warning(f"Errors extracting splits for {player_name}: {result.errors}")
                    else:
                        logger.info(f"Successfully extracted {len(result.basic_splits)} basic and "
                                   f"{len(result.advanced_splits)} advanced splits for {player_name}")
                    
                except Exception as e:
                    error_msg = f"Error processing splits for {player_name}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.metrics.failed_extractions += 1
                    self.metrics.total_errors += 1
        
        return all_basic_splits, all_advanced_splits
    
    def _extract_single_player_splits(self, qb_stat: QBPassingStats) -> SplitsExtractionResult:
        """Extract splits for a single player (for concurrent processing)"""
        try:
            return self.splits_extractor.extract_player_splits(
                qb_stat.pfr_id, qb_stat.player_name, qb_stat.season, datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in single player extraction for {qb_stat.player_name}: {str(e)}")
            return SplitsExtractionResult(
                basic_splits=[], advanced_splits=[], 
                errors=[f"Extraction failed: {str(e)}"], warnings=[],
                tables_discovered=0, tables_processed=0, extraction_time=0.0
            )
    
    def validate_splits_data(self, basic_splits: List[QBSplitsType1], 
                           advanced_splits: List[QBSplitsType2]) -> Dict[str, List[str]]:
        """
        Validate extracted splits data
        
        Args:
            basic_splits: List of basic splits data
            advanced_splits: List of advanced splits data
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'errors': [],
            'warnings': [],
            'basic_splits_validated': 0,
            'advanced_splits_validated': 0
        }
        
        # Validate basic splits
        for split in basic_splits:
            try:
                errors = split.validate()
                if errors:
                    validation_results['errors'].extend([
                        f"Basic split validation error for {split.player_name}: {error}"
                        for error in errors
                    ])
                else:
                    validation_results['basic_splits_validated'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Exception validating basic split for {split.player_name}: {str(e)}"
                )
        
        # Validate advanced splits
        for split in advanced_splits:
            try:
                errors = split.validate()
                if errors:
                    validation_results['errors'].extend([
                        f"Advanced split validation error for {split.player_name}: {error}"
                        for error in errors
                    ])
                else:
                    validation_results['advanced_splits_validated'] += 1
            except Exception as e:
                validation_results['errors'].append(
                    f"Exception validating advanced split for {split.player_name}: {str(e)}"
                )
        
        return validation_results
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get comprehensive extraction summary"""
        processing_time = calculate_processing_time(self.metrics.start_time, datetime.now())
        
        return {
            'session_id': self.session_id,
            'start_time': self.metrics.start_time.isoformat(),
            'processing_time': processing_time,
            'total_players': self.metrics.total_players,
            'successful_extractions': self.metrics.successful_extractions,
            'failed_extractions': self.metrics.failed_extractions,
            'success_rate': (self.metrics.successful_extractions / self.metrics.total_players * 100) if self.metrics.total_players > 0 else 0,
            'total_basic_splits': self.metrics.total_basic_splits,
            'total_advanced_splits': self.metrics.total_advanced_splits,
            'total_errors': self.metrics.total_errors,
            'total_warnings': self.metrics.total_warnings,
            'rate_limit_violations': self.metrics.rate_limit_violations,
            'average_basic_splits_per_player': (self.metrics.total_basic_splits / self.metrics.successful_extractions) if self.metrics.successful_extractions > 0 else 0,
            'average_advanced_splits_per_player': (self.metrics.total_advanced_splits / self.metrics.successful_extractions) if self.metrics.successful_extractions > 0 else 0
        }
    
    def log_extraction_summary(self):
        """Log comprehensive extraction summary"""
        summary = self.get_extraction_summary()
        
        logger.info("=== Splits Extraction Summary ===")
        logger.info(f"Session ID: {summary['session_id']}")
        logger.info(f"Processing Time: {summary['processing_time']:.2f}s")
        logger.info(f"Total Players: {summary['total_players']}")
        logger.info(f"Successful Extractions: {summary['successful_extractions']}")
        logger.info(f"Failed Extractions: {summary['failed_extractions']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Total Basic Splits: {summary['total_basic_splits']}")
        logger.info(f"Total Advanced Splits: {summary['total_advanced_splits']}")
        logger.info(f"Average Basic Splits per Player: {summary['average_basic_splits_per_player']:.1f}")
        logger.info(f"Average Advanced Splits per Player: {summary['average_advanced_splits_per_player']:.1f}")
        logger.info(f"Total Errors: {summary['total_errors']}")
        logger.info(f"Total Warnings: {summary['total_warnings']}")
        logger.info(f"Rate Limit Violations: {summary['rate_limit_violations']}")
        logger.info("================================")
    
    def extract_player_splits_by_name(self, player_name: str, pfr_id: str, 
                                    season: int) -> SplitsExtractionResult:
        """
        Extract splits for a specific player by name
        
        Args:
            player_name: Player's name
            pfr_id: Player's PFR ID
            season: Season year
            
        Returns:
            SplitsExtractionResult with extracted data
        """
        try:
            logger.info(f"Extracting splits for {player_name} (PFR ID: {pfr_id}, Season: {season})")
            
            result = self.splits_extractor.extract_player_splits(
                pfr_id, player_name, season, datetime.now()
            )
            
            # Add to metrics
            self.metrics.add_extraction_result(result)
            
            if result.errors:
                logger.warning(f"Errors extracting splits for {player_name}: {result.errors}")
            else:
                logger.info(f"Successfully extracted {len(result.basic_splits)} basic and "
                           f"{len(result.advanced_splits)} advanced splits for {player_name}")
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error extracting splits for {player_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.metrics.failed_extractions += 1
            self.metrics.total_errors += 1
            
            return SplitsExtractionResult(
                basic_splits=[], advanced_splits=[], 
                errors=[error_msg], warnings=[],
                tables_discovered=0, tables_processed=0, extraction_time=0.0
            )
    
    def test_splits_url_construction(self, pfr_id: str, season: int) -> Dict[str, Any]:
        """
        Test splits URL construction for debugging
        
        Args:
            pfr_id: Player's PFR ID
            season: Season year
            
        Returns:
            Dictionary with test results
        """
        try:
            url = build_enhanced_splits_url(pfr_id, season)
            is_valid = validate_splits_url(url) if url else False
            
            return {
                'pfr_id': pfr_id,
                'season': season,
                'constructed_url': url,
                'is_valid': is_valid,
                'error': None
            }
        except Exception as e:
            return {
                'pfr_id': pfr_id,
                'season': season,
                'constructed_url': None,
                'is_valid': False,
                'error': str(e)
            } 