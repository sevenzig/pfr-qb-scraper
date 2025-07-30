"""
Core Scraper - Main orchestration class for NFL QB data scraping.

This module provides the main CoreScraper class that orchestrates the entire
scraping process using dependency injection and proper error handling.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time

from .request_manager import RequestManager
from .html_parser import HTMLParser
from .pfr_data_extractor import PFRDataExtractor, ExtractionResult
from .pfr_structure_analyzer import PFRStructureAnalyzer
from .selenium_manager import SeleniumManager, SeleniumConfig

logger = logging.getLogger(__name__)


class Config:
    """Simple configuration class for testing."""
    def __init__(self):
        self.min_delay = 7.0
        self.max_delay = 10.0
        self.max_retries = 3
        self.timeout = 30


class DatabaseManager:
    """Simple database manager for testing."""
    def __init__(self):
        pass
    
    def insert_qb_basic_stats(self, data: Dict[str, Any]) -> bool:
        """Insert QB basic stats into database."""
        logger.info(f"Would insert basic stats: {data.get('player_name', 'Unknown')}")
        return True
    
    def insert_qb_splits(self, data: Dict[str, Any]) -> bool:
        """Insert QB splits into database."""
        logger.info(f"Would insert splits: {data.get('player_name', 'Unknown')}")
        return True
    
    def insert_qb_splits_advanced(self, data: Dict[str, Any]) -> bool:
        """Insert QB advanced splits into database."""
        logger.info(f"Would insert advanced splits: {data.get('player_name', 'Unknown')}")
        return True


class CoreScraper:
    """
    Core scraper class that orchestrates the entire NFL QB data scraping process.
    
    This class uses dependency injection to coordinate between different components:
    - RequestManager: Handles HTTP requests and rate limiting
    - HTMLParser: Parses HTML content
    - PFRDataExtractor: Extracts structured data from PFR pages
    - DatabaseManager: Handles database operations
    """
    
    def __init__(self, request_manager: RequestManager, html_parser: HTMLParser,
                 data_extractor: PFRDataExtractor, db_manager: DatabaseManager,
                 config: Config, selenium_manager: Optional[SeleniumManager] = None):
        """
        Initialize the CoreScraper with dependencies.
        
        Args:
            request_manager: Manager for HTTP requests and rate limiting
            html_parser: Parser for HTML content
            data_extractor: Extractor for structured data from PFR
            db_manager: Manager for database operations
            config: Application configuration
            selenium_manager: Optional Selenium manager for JavaScript-heavy pages
        """
        self.request_manager = request_manager
        self.html_parser = html_parser
        self.data_extractor = data_extractor
        self.db_manager = db_manager
        self.config = config
        self.selenium_manager = selenium_manager
        
        # Initialize structure analyzer for debugging and validation
        self.structure_analyzer = PFRStructureAnalyzer()
        
        logger.info("CoreScraper initialized with all dependencies")
        if self.selenium_manager:
            logger.info("Selenium manager available for JavaScript-heavy pages")
    
    def _fetch_page_with_fallback(self, url: str, enable_js: bool = False) -> Dict[str, Any]:
        """
        Fetch a page with fallback between RequestManager and SeleniumManager.
        
        Args:
            url: The URL to fetch
            enable_js: Whether JavaScript is required for this page
            
        Returns:
            Dict with 'success', 'content', and 'error' keys
        """
        # Try RequestManager first (faster, less resource-intensive)
        if not enable_js:
            logger.debug(f"Attempting to fetch {url} with RequestManager")
            result = self.request_manager.get_page(url)
            if result['success']:
                logger.debug(f"Successfully fetched {url} with RequestManager")
                return result
            else:
                logger.warning(f"RequestManager failed for {url}: {result['error']}")
        
        # Fallback to SeleniumManager if available
        if self.selenium_manager:
            logger.info(f"Attempting to fetch {url} with SeleniumManager")
            try:
                result = self.selenium_manager.get_page(url, enable_js=enable_js)
                if result['success']:
                    logger.info(f"Successfully fetched {url} with SeleniumManager")
                    return result
                else:
                    logger.error(f"SeleniumManager failed for {url}: {result['error']}")
            except Exception as e:
                logger.error(f"Error using SeleniumManager for {url}: {e}")
        
        # If both methods failed
        error_msg = f"Failed to fetch {url} with both RequestManager and SeleniumManager"
        logger.error(error_msg)
        return {'success': False, 'content': None, 'error': error_msg}
    
    def scrape_season_qbs(self, season: int, player_names: Optional[List[str]] = None,
                          splits_only: bool = False) -> Dict[str, Any]:
        """
        Scrape QB data for a specific season.
        
        Args:
            season: Season year to scrape
            player_names: Optional list of specific player names to scrape
            splits_only: If True, only scrape splits data (skip basic stats)
            
        Returns:
            Dictionary with scraping results and statistics
        """
        logger.info(f"Starting QB scraping for season {season}")
        
        # Get list of QBs to scrape
        if player_names:
            qbs_to_scrape = player_names
            logger.info(f"Scraping specific players: {qbs_to_scrape}")
        else:
            qbs_to_scrape = self._get_qb_list_for_season(season)
            logger.info(f"Found {len(qbs_to_scrape)} QBs to scrape for {season}")
        
        # Initialize results tracking
        results = {
            'season': season,
            'total_players': len(qbs_to_scrape),
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'total_data_extracted': 0,
            'start_time': datetime.now(),
            'player_results': [],
            'errors': [],
            'warnings': []
        }
        
        # Scrape each QB
        for i, player_name in enumerate(qbs_to_scrape, 1):
            logger.info(f"Scraping {player_name} ({i}/{len(qbs_to_scrape)})")
            
            try:
                player_result = self._scrape_single_qb(player_name, season, splits_only)
                results['player_results'].append(player_result)
                
                if player_result['success']:
                    results['successful_scrapes'] += 1
                    results['total_data_extracted'] += player_result['data_count']
                else:
                    results['failed_scrapes'] += 1
                    results['errors'].extend(player_result['errors'])
                
                results['warnings'].extend(player_result['warnings'])
                
            except Exception as e:
                error_msg = f"Unexpected error scraping {player_name}: {e}"
                logger.error(error_msg, exc_info=True)
                results['errors'].append(error_msg)
                results['failed_scrapes'] += 1
                
                # Add failed player result
                results['player_results'].append({
                    'player_name': player_name,
                    'success': False,
                    'errors': [error_msg],
                    'warnings': [],
                    'data_count': 0
                })
        
        # Calculate final statistics
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        results['success_rate'] = (results['successful_scrapes'] / results['total_players']) * 100
        
        logger.info(f"Season scraping complete for {season}:")
        logger.info(f"  - Success rate: {results['success_rate']:.1f}%")
        logger.info(f"  - Total data extracted: {results['total_data_extracted']}")
        logger.info(f"  - Duration: {results['duration']:.2f}s")
        
        return results
    
    def _scrape_single_qb(self, player_name: str, season: int, 
                          splits_only: bool) -> Dict[str, Any]:
        """
        Scrape data for a single QB.
        
        Args:
            player_name: Name of the QB to scrape
            season: Season year
            splits_only: If True, only scrape splits data
            
        Returns:
            Dictionary with scraping results for this player
        """
        logger.info(f"Scraping {player_name} for {season}")
        
        result = {
            'player_name': player_name,
            'season': season,
            'success': False,
            'data_count': 0,
            'errors': [],
            'warnings': [],
            'extracted_data': {}
        }
        
        try:
            # Get PFR ID for the player
            pfr_id = self._get_pfr_id(player_name)
            if not pfr_id:
                error_msg = f"Could not find PFR ID for {player_name}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
                return result
            
            # Scrape basic stats (unless splits_only is True)
            if not splits_only:
                basic_stats_result = self._scrape_basic_stats(pfr_id, player_name, season)
                if basic_stats_result['success']:
                    result['extracted_data']['basic_stats'] = basic_stats_result['data']
                    result['data_count'] += 1
                else:
                    result['errors'].extend(basic_stats_result['errors'])
                    result['warnings'].extend(basic_stats_result['warnings'])
            
            # Scrape splits data
            splits_result = self._scrape_splits_data(pfr_id, player_name, season)
            if splits_result['success']:
                result['extracted_data']['splits'] = splits_result['data']
                result['data_count'] += 1
            else:
                result['errors'].extend(splits_result['errors'])
                result['warnings'].extend(splits_result['warnings'])
            
            # Scrape advanced splits data
            advanced_splits_result = self._scrape_advanced_splits_data(pfr_id, player_name, season)
            if advanced_splits_result['success']:
                result['extracted_data']['advanced_splits'] = advanced_splits_result['data']
                result['data_count'] += 1
            else:
                result['errors'].extend(advanced_splits_result['errors'])
                result['warnings'].extend(advanced_splits_result['warnings'])
            
            # Determine overall success
            result['success'] = result['data_count'] > 0 and len(result['errors']) == 0
            
            logger.info(f"Scraping complete for {player_name}: {result['data_count']} data types extracted")
            
        except Exception as e:
            error_msg = f"Error scraping {player_name}: {e}"
            result['errors'].append(error_msg)
            logger.error(error_msg, exc_info=True)
        
        return result
    
    def _scrape_basic_stats(self, pfr_id: str, player_name: str, 
                           season: int) -> Dict[str, Any]:
        """
        Scrape basic stats for a QB.
        
        Args:
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            
        Returns:
            Dictionary with basic stats scraping results
        """
        logger.info(f"Scraping basic stats for {player_name}")
        
        try:
            # Build URL for basic stats
            url = f"https://www.pro-football-reference.com/players/{pfr_id[0]}/{pfr_id}.htm"
            
            # Get page content with fallback
            response = self._fetch_page_with_fallback(url, enable_js=False)
            if not response['success']:
                return {
                    'success': False,
                    'data': {},
                    'errors': [f"Failed to get basic stats page: {response['error']}"],
                    'warnings': []
                }
            
            # Parse HTML
            soup = self.html_parser.parse_html(response['content'])
            if not soup:
                return {
                    'success': False,
                    'data': {},
                    'errors': ["Failed to parse basic stats HTML"],
                    'warnings': []
                }
            
            # Extract data
            extraction_results = self.data_extractor.extract_all_qb_data(soup, player_name, season)
            
            # Get basic stats result
            basic_stats_result = extraction_results.get('basic_stats')
            if basic_stats_result and basic_stats_result.success:
                return {
                    'success': True,
                    'data': basic_stats_result.data,
                    'errors': basic_stats_result.errors,
                    'warnings': basic_stats_result.warnings
                }
            else:
                return {
                    'success': False,
                    'data': {},
                    'errors': basic_stats_result.errors if basic_stats_result else ["No basic stats found"],
                    'warnings': basic_stats_result.warnings if basic_stats_result else []
                }
                
        except Exception as e:
            error_msg = f"Error scraping basic stats for {player_name}: {e}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'data': {},
                'errors': [error_msg],
                'warnings': []
            }
    
    def _scrape_splits_data(self, pfr_id: str, player_name: str, 
                           season: int) -> Dict[str, Any]:
        """
        Scrape splits data for a QB.
        
        Args:
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            
        Returns:
            Dictionary with splits scraping results
        """
        logger.info(f"Scraping splits data for {player_name}")
        
        try:
            # Build URL for splits
            url = f"https://www.pro-football-reference.com/players/{pfr_id[0]}/{pfr_id}/splits/{season}/"
            
            # Get page content with fallback
            response = self._fetch_page_with_fallback(url, enable_js=False)
            if not response['success']:
                return {
                    'success': False,
                    'data': {},
                    'errors': [f"Failed to get splits page: {response['error']}"],
                    'warnings': []
                }
            
            # Parse HTML
            soup = self.html_parser.parse_html(response['content'])
            if not soup:
                return {
                    'success': False,
                    'data': {},
                    'errors': ["Failed to parse splits HTML"],
                    'warnings': []
                }
            
            # Extract data
            extraction_results = self.data_extractor.extract_all_qb_data(soup, player_name, season)
            
            # Get splits result
            splits_result = extraction_results.get('splits')
            if splits_result and splits_result.success:
                return {
                    'success': True,
                    'data': splits_result.data,
                    'errors': splits_result.errors,
                    'warnings': splits_result.warnings
                }
            else:
                return {
                    'success': False,
                    'data': {},
                    'errors': splits_result.errors if splits_result else ["No splits data found"],
                    'warnings': splits_result.warnings if splits_result else []
                }
                
        except Exception as e:
            error_msg = f"Error scraping splits for {player_name}: {e}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'data': {},
                'errors': [error_msg],
                'warnings': []
            }
    
    def _scrape_advanced_splits_data(self, pfr_id: str, player_name: str, 
                                    season: int) -> Dict[str, Any]:
        """
        Scrape advanced splits data for a QB.
        
        Args:
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            
        Returns:
            Dictionary with advanced splits scraping results
        """
        logger.info(f"Scraping advanced splits data for {player_name}")
        
        try:
            # Build URL for advanced splits
            url = f"https://www.pro-football-reference.com/players/{pfr_id[0]}/{pfr_id}/splits/{season}/"
            
            # Get page content with fallback (same URL as regular splits, but we'll extract different tables)
            response = self._fetch_page_with_fallback(url, enable_js=False)
            if not response['success']:
                return {
                    'success': False,
                    'data': {},
                    'errors': [f"Failed to get advanced splits page: {response['error']}"],
                    'warnings': []
                }
            
            # Parse HTML
            soup = self.html_parser.parse_html(response['content'])
            if not soup:
                return {
                    'success': False,
                    'data': {},
                    'errors': ["Failed to parse advanced splits HTML"],
                    'warnings': []
                }
            
            # Extract data
            extraction_results = self.data_extractor.extract_all_qb_data(soup, player_name, season)
            
            # Get advanced splits result
            advanced_splits_result = extraction_results.get('advanced_splits')
            if advanced_splits_result and advanced_splits_result.success:
                return {
                    'success': True,
                    'data': advanced_splits_result.data,
                    'errors': advanced_splits_result.errors,
                    'warnings': advanced_splits_result.warnings
                }
            else:
                return {
                    'success': False,
                    'data': {},
                    'errors': advanced_splits_result.errors if advanced_splits_result else ["No advanced splits data found"],
                    'warnings': advanced_splits_result.warnings if advanced_splits_result else []
                }
                
        except Exception as e:
            error_msg = f"Error scraping advanced splits for {player_name}: {e}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'data': {},
                'errors': [error_msg],
                'warnings': []
            }
    
    def _get_pfr_id(self, player_name: str) -> Optional[str]:
        """
        Get PFR ID for a player name.
        
        Args:
            player_name: Player's name
            
        Returns:
            PFR ID if found, None otherwise
        """
        # This is a simplified implementation
        # In a full implementation, you would query a database or API
        # to get the PFR ID for a given player name
        
        # For now, we'll use a simple mapping or return None
        # This should be implemented based on your player database
        logger.warning(f"PFR ID lookup not implemented for {player_name}")
        return None
    
    def _get_qb_list_for_season(self, season: int) -> List[str]:
        """
        Get list of QBs to scrape for a season.
        
        Args:
            season: Season year
            
        Returns:
            List of QB names to scrape
        """
        # This is a simplified implementation
        # In a full implementation, you would query a database or API
        # to get the list of QBs for a given season
        
        # For now, return a test list
        test_qbs = ["Joe Burrow", "Patrick Mahomes", "Josh Allen"]
        logger.info(f"Using test QB list for {season}: {test_qbs}")
        return test_qbs
    
    def analyze_page_structure(self, url: str) -> Dict[str, Any]:
        """
        Analyze the structure of a PFR page for debugging.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with page structure analysis
        """
        logger.info(f"Analyzing page structure for {url}")
        
        try:
            # Get page content
            response = self.request_manager.get_page(url)
            if not response['success']:
                return {
                    'success': False,
                    'error': f"Failed to get page: {response['error']}",
                    'analysis': {}
                }
            
            # Parse HTML
            soup = self.html_parser.parse_html(response['content'])
            if not soup:
                return {
                    'success': False,
                    'error': "Failed to parse HTML",
                    'analysis': {}
                }
            
            # Analyze structure
            analysis = self.structure_analyzer.analyze_page_structure(soup)
            
            return {
                'success': True,
                'url': url,
                'analysis': analysis
            }
            
        except Exception as e:
            error_msg = f"Error analyzing page structure: {e}"
            logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'error': error_msg,
                'analysis': {}
            } 