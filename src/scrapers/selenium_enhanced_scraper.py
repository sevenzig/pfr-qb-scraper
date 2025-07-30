#!/usr/bin/env python3
"""
Selenium Enhanced PFR Scraper for NFL QB Data
Selenium-based scraper with advanced features and comprehensive data extraction
"""

import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..models.qb_models import (
    QBBasicStats, QBSplitsType1, QBSplitsType2, QBPassingStats,
    Player, Team, ScrapingLog, QBSplitStats
)
from ..utils.data_utils import (
    safe_int, safe_float, safe_percentage, clean_player_name,
    extract_pfr_id, build_splits_url, generate_session_id,
    calculate_processing_time, normalize_pfr_team_code
)
from ..config.config import config, SplitTypes, SplitCategories
from ..core.selenium_manager import SeleniumManager, SeleniumConfig

logger = logging.getLogger(__name__)

@dataclass
class SeleniumScrapingMetrics:
    """Metrics for tracking Selenium scraping performance"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    url_redirects: int = 0  # Track when we need to try different URL patterns
    start_time: Optional[datetime] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    def add_error(self, error: str):
        """Add error message"""
        self.errors.append(error)
        logger.error(error)
    
    def add_warning(self, warning: str):
        """Add warning message"""
        self.warnings.append(warning)
        logger.warning(warning)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

class SeleniumEnhancedPFRScraper:
    """Enhanced Pro Football Reference scraper using Selenium with variable delays"""
    
    def __init__(self, min_delay: float = 7.0, max_delay: float = 12.0):
        self.base_url = "https://www.pro-football-reference.com"
        self.min_delay = min_delay
        self.max_delay = max_delay
        
        # Initialize Selenium manager with variable delays
        self.selenium_manager = None
        
        # Metrics tracking
        self.metrics = SeleniumScrapingMetrics()
        self.metrics.start_time = datetime.now()
        
        # Known split patterns for automatic discovery
        self.split_patterns = {
            'down': [r'down', r'1st', r'2nd', r'3rd', r'4th'],
            'yards_to_go': [r'yards.*to.*go', r'1-3', r'4-6', r'7-9', r'10\+'],
            'down_and_yards': [r'down.*yards', r'1st.*10', r'2nd.*1-3', r'3rd.*10\+'],
            'field_position': [r'field.*position', r'own.*1-10', r'own.*1-20', r'own.*21-50', r'opp.*49-20', r'red.*zone', r'opp.*1-10'],
            'score_differential': [r'score.*differential', r'leading', r'tied', r'trailing'],
            'quarter': [r'quarter', r'1st.*qtr', r'2nd.*qtr', r'3rd.*qtr', r'4th.*qtr', r'ot', r'1st.*half', r'2nd.*half'],
            'game_situation': [r'game.*situation', r'leading.*2.*min', r'tied.*2.*min', r'trailing.*2.*min'],
            'snap_type': [r'snap.*type', r'huddle', r'no.*huddle', r'shotgun', r'under.*center'],
            'play_action': [r'play.*action', r'play action', r'non-play action'],
            'run_pass_option': [r'run.*pass.*option', r'rpo', r'non-rpo'],
            'time_in_pocket': [r'time.*pocket', r'2\.5.*seconds', r'2\.5\+.*seconds']
        }
    
    def __enter__(self):
        """Context manager entry"""
        config = SeleniumConfig(
            headless=True,
            human_behavior_delay=(self.min_delay, self.max_delay)
        )
        self.selenium_manager = SeleniumManager(config)
        self.selenium_manager.start_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.selenium_manager:
            self.selenium_manager.end_session()
    
    def make_request_with_selenium(self, url: str) -> Optional[str]:
        """
        Make HTTP request using Selenium manager
        
        Args:
            url: URL to request
            
        Returns:
            Page source HTML or None if failed
        """
        if not self.selenium_manager:
            raise RuntimeError("Selenium manager not initialized. Use context manager.")
        
        self.metrics.total_requests += 1
        
        try:
            result = self.selenium_manager.get_page(url, enable_js=False)
            
            if result['success']:
                self.metrics.successful_requests += 1
                return result['content']
            else:
                self.metrics.failed_requests += 1
                self.metrics.add_error(f"Request failed for {url}: {result['error']}")
                return None
                
        except Exception as e:
            self.metrics.failed_requests += 1
            self.metrics.add_error(f"Request failed for {url}: {e}")
            return None
    
    def try_multiple_url_patterns(self, base_pfr_id: str, player_name: str) -> Optional[str]:
        """
        Try multiple URL patterns to find the correct player page
        
        Args:
            base_pfr_id: Base PFR ID (e.g., 'BurrJo')
            player_name: Player name for logging
            
        Returns:
            Correct player URL or None if not found
        """
        # Extract first letter and base ID
        first_letter = base_pfr_id[0].upper()
        base_id = base_pfr_id[1:]  # Remove first letter
        
        # Try different URL patterns
        url_patterns = [
            f"{base_pfr_id}01",  # Most common pattern (Joe Burrow)
            f"{base_pfr_id}00",  # Original pattern (John Burrell)
            f"{base_pfr_id}02",  # Alternative pattern
            f"{base_pfr_id}03",  # Another alternative
        ]
        
        for pattern in url_patterns:
            url = f"{self.base_url}/players/{first_letter}/{pattern}.htm"
            logger.debug(f"Trying URL pattern: {url}")
            
            response = self.make_request_with_selenium(url)
            if response:
                # Check if this is the correct player by looking for their name
                if self._verify_player_page(response, player_name):
                    logger.info(f"Found correct URL for {player_name}: {url}")
                    return url
                else:
                    logger.debug(f"URL {url} returned different player, trying next pattern")
                    self.metrics.url_redirects += 1
        
        logger.warning(f"Could not find correct URL for {player_name} with base ID {base_pfr_id}")
        return None
    
    def _verify_player_page(self, html_content: str, player_name: str) -> bool:
        """
        Verify that the HTML content is for the correct player
        
        Args:
            html_content: Page HTML content
            player_name: Expected player name
            
        Returns:
            True if this is the correct player's page
        """
        # Look for player name in title or main content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check title
        title = soup.find('title')
        if title and player_name in title.get_text():
            return True
        
        # Check main heading
        h1 = soup.find('h1')
        if h1 and player_name in h1.get_text():
            return True
        
        # Check for player name in various locations
        player_name_clean = clean_player_name(player_name)
        if player_name_clean in html_content:
            return True
        
        return False
    
    def get_qb_main_stats(self, season: int, player_names: Optional[List[str]] = None) -> Tuple[List[Player], List[QBBasicStats]]:
        """
        Scrape main QB statistics for a season using Selenium
        
        Args:
            season: Season year to scrape
            player_names: Optional list of specific player names to scrape
            
        Returns:
            Tuple of (players, basic_stats)
        """
        logger.info(f"Scraping QB main stats for {season} season using Selenium")
        
        # URL for the main passing stats page
        main_stats_url = f"{self.base_url}/years/{season}/passing.htm"
        
        response = self.make_request_with_selenium(main_stats_url)
        if not response:
            raise RuntimeError(f"Failed to load main stats page for {season}")
        
        # Save a sample for debugging
        with open(f"pfr_passing_debug_{season}.html", "w", encoding="utf-8") as f:
            f.write(response[:50000])  # First 50K chars
        logger.info(f"Saved debug sample to pfr_passing_debug_{season}.html")
        
        soup = BeautifulSoup(response, 'html.parser')
        
        # Find the main passing stats table
        table = soup.find('table', {'id': 'passing'})
        if not table:
            # Try alternative table IDs
            table = soup.find('table', {'id': 'stats'})
            if not table:
                table = soup.find('table', {'id': 'passing_stats'})
                if not table:
                    # Debug: List all table IDs
                    tables = soup.find_all('table')
                    table_ids = [t.get('id', 'NO_ID') for t in tables]
                    logger.warning(f"Could not find passing stats table. Available tables: {table_ids}")
                    raise RuntimeError("Could not find passing stats table")
        
        logger.info(f"Found table with ID: {table.get('id', 'NO_ID')}")
        
        # Extract player data
        players_list = []
        basic_stats_list = []
        current_time = datetime.now()
        
        # Process each row in the table
        tbody = table.find('tbody')
        if not tbody:
            raise RuntimeError("Could not find table body")
        
        rows = tbody.find_all('tr')
        logger.info(f"Found {len(rows)} total rows in passing stats table")
        
        # Debug: Check first few rows
        for i, row in enumerate(rows[:3]):
            player_cell = row.find('td', {'data-stat': 'player'})
            pos_cell = row.find('td', {'data-stat': 'pos'})
            if player_cell:
                player_name = player_cell.get_text(strip=True)
                pos = pos_cell.get_text(strip=True) if pos_cell else "N/A"
                logger.debug(f"Row {i}: {player_name} - {pos}")
            else:
                # Try to find any text in the row
                all_cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in all_cells if cell.get_text(strip=True)]
                logger.debug(f"Row {i}: No player cell found. Cell texts: {cell_texts[:3]}...")
                
                # Check if this row has any links
                links = row.find_all('a')
                if links:
                    link_texts = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
                    logger.debug(f"Row {i}: Found links: {link_texts[:3]}...")
        
        for row in rows:
            try:
                # Extract player name and URL from the Player column (column 2)
                player_cell = row.find('td', {'data-stat': 'name_display'})
                if not player_cell:
                    continue
                
                player_name_anchor = player_cell.find('a')
                if not player_name_anchor:
                    continue
                
                player_name = player_name_anchor.get_text(strip=True)
                
                # Filter by specific players if requested
                if player_names and player_name not in player_names:
                    continue
                
                # Check if this is a QB
                pos_cell = row.find('td', {'data-stat': 'pos'})
                if not pos_cell or pos_cell.get_text(strip=True).upper() != 'QB':
                    continue
                
                # Extract the href from the player link
                href = player_name_anchor.get('href', '')
                if not href:
                    continue
                
                # Construct full player URL
                player_url = urljoin(self.base_url, href)
                
                # Extract PFR ID from URL - this is already the correct ID
                match = re.search(r'/players/[A-Z]/([A-Za-z0-9]+)\.htm', player_url)
                if not match:
                    continue
                
                pfr_id = match.group(1)
                
                # Use the URL directly since we already have the correct one from the main table
                correct_player_url = player_url
                
                # PFR ID is already extracted above
                
                # Extract team and stats
                team_cell = row.find('td', {'data-stat': 'team_name_abbr'})
                team_code = normalize_pfr_team_code(team_cell.get_text(strip=True)) if team_cell else ''
                
                if not team_code:
                    logger.warning(f"Player {player_name} has no team associated, skipping")
                    continue
                
                # Create player and stats objects
                player = Player(
                    pfr_id=pfr_id, 
                    player_name=player_name, 
                    pfr_url=correct_player_url, 
                    created_at=current_time, 
                    updated_at=current_time
                )
                
                stats = self._extract_stats_from_row(row)
                stats['team'] = team_code
                
                basic_stats = QBBasicStats(
                    pfr_id=pfr_id, 
                    player_name=player_name, 
                    player_url=correct_player_url, 
                    season=season, 
                    **stats
                )
                basic_stats.scraped_at = current_time
                basic_stats.updated_at = current_time
                
                players_list.append(player)
                basic_stats_list.append(basic_stats)
                
                logger.debug(f"Successfully processed {player_name} ({pfr_id})")
                
            except Exception as e:
                self.metrics.add_error(f"Error processing row for {player_name if 'player_name' in locals() else 'unknown'}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(players_list)} QB players with basic stats for {season}")
        return players_list, basic_stats_list
    
    def _extract_stats_from_row(self, row) -> Dict[str, Any]:
        """Helper to extract stats from a BeautifulSoup row tag into a dictionary."""
        
        def get_stat(stat_name):
            cell = row.find('td', {'data-stat': stat_name})
            return cell.get_text(strip=True) if cell else None

        # Extract basic stats
        cmp_val = safe_int(get_stat('pass_cmp'))
        att_val = safe_int(get_stat('pass_att'))
        
        # Calculate incompletions (not directly available in main table)
        inc_val = None
        if cmp_val is not None and att_val is not None:
            inc_val = att_val - cmp_val
            logger.debug(f"Calculated inc: {att_val} - {cmp_val} = {inc_val}")

        return {
            'rk': safe_int(get_stat('rank')),
            'age': safe_int(get_stat('age')),
            'pos': get_stat('pos') or 'QB',
            'g': safe_int(get_stat('g')),
            'gs': safe_int(get_stat('gs')),
            'qb_rec': get_stat('qb_rec'),
            'cmp': cmp_val,
            'att': att_val,
            'inc': inc_val,  # Calculated field
            'cmp_pct': safe_percentage(get_stat('pass_cmp_pct')),
            'yds': safe_int(get_stat('pass_yds')),
            'td': safe_int(get_stat('pass_td')),
            'td_pct': safe_percentage(get_stat('pass_td_pct')),
            'int': safe_int(get_stat('pass_int')),
            'int_pct': safe_percentage(get_stat('pass_int_pct')),
            'first_downs': safe_int(get_stat('pass_first_down')),
            'succ_pct': safe_percentage(get_stat('pass_success')),
            'lng': safe_int(get_stat('pass_long')),
            'y_a': safe_float(get_stat('pass_yds_per_att')),
            'ay_a': safe_float(get_stat('pass_adj_yds_per_att')),
            'y_c': safe_float(get_stat('pass_yds_per_cmp')),
            'y_g': safe_float(get_stat('pass_yds_per_g')),
            'rate': safe_float(get_stat('pass_rating')),
            'qbr': safe_float(get_stat('qbr')),
            'sk': safe_int(get_stat('pass_sacked')),
            'sk_yds': safe_int(get_stat('pass_sacked_yds')),
            'sk_pct': safe_percentage(get_stat('pass_sacked_pct')),
            'ny_a': safe_float(get_stat('pass_net_yds_per_att')),
            'any_a': safe_float(get_stat('pass_adj_net_yds_per_att')),
            'four_qc': safe_int(get_stat('pass_4qc')),
            'gwd': safe_int(get_stat('pass_gwd')),
            'awards': get_stat('awards')
        }
    
    def scrape_player_splits(self, player_url: str, pfr_id: str, player_name: str,
                             team: str, season: int, scraped_at: datetime) -> Tuple[List[QBSplitStats], List[QBSplitsType2]]:
        """
        Scrape splits data for a specific player using Selenium
        
        Args:
            player_url: Player's PFR URL
            pfr_id: Player's PFR ID
            player_name: Player's name
            team: Player's team
            season: Season year
            scraped_at: Timestamp
            
        Returns:
            Tuple of (basic_splits, advanced_splits)
        """
        basic_splits: List[QBSplitStats] = []
        advanced_splits: List[QBSplitsType2] = []
        
        # Build splits URL
        try:
            splits_url = build_splits_url(pfr_id, season)
        except Exception as exc:
            self.metrics.add_error(f"Could not build splits URL for {player_name}: {exc}")
            return basic_splits, advanced_splits

        response = self.make_request_with_selenium(splits_url)
        if not response:
            logger.warning(f"Could not load splits page for {player_name}")
            return basic_splits, advanced_splits

        soup = BeautifulSoup(response, 'html.parser')
        
        # Process splits data (simplified for now)
        # TODO: Implement full splits processing logic
        
        logger.debug(f"Scraped splits for {player_name} ({len(basic_splits)} basic, {len(advanced_splits)} advanced)")
        return basic_splits, advanced_splits
    
    def process_players_concurrently(self, qb_stats: List[QBBasicStats], 
                                   max_workers: int = None) -> Tuple[List[QBSplitStats], List[QBSplitsType2]]:
        """
        Process multiple players for splits data (simplified for now)
        
        Args:
            qb_stats: List of QB basic stats
            max_workers: Maximum concurrent workers (not used in Selenium version)
            
        Returns:
            Tuple of (basic_splits, advanced_splits)
        """
        basic_splits: List[QBSplitStats] = []
        advanced_splits: List[QBSplitsType2] = []
        
        logger.info(f"Processing splits for {len(qb_stats)} players")
        
        for i, qb_stat in enumerate(qb_stats, 1):
            logger.info(f"Processing player {i}/{len(qb_stats)}: {qb_stat.player_name}")
            
            try:
                player_splits, player_advanced = self.scrape_player_splits(
                    qb_stat.player_url,
                    qb_stat.pfr_id,
                    qb_stat.player_name,
                    qb_stat.team,
                    qb_stat.season,
                    qb_stat.scraped_at
                )
                
                basic_splits.extend(player_splits)
                advanced_splits.extend(player_advanced)
                
            except Exception as e:
                self.metrics.add_error(f"Error processing splits for {qb_stat.player_name}: {e}")
                continue
        
        logger.info(f"Completed splits processing: {len(basic_splits)} basic, {len(advanced_splits)} advanced")
        return basic_splits, advanced_splits
    
    def get_scraping_metrics(self) -> SeleniumScrapingMetrics:
        """Get scraping metrics"""
        return self.metrics
    
    def reset_metrics(self):
        """Reset scraping metrics"""
        self.metrics = SeleniumScrapingMetrics()
    
    def create_scraping_log(self, season: int) -> ScrapingLog:
        """Create scraping log entry"""
        current_time = datetime.now()
        
        return ScrapingLog(
            session_id=generate_session_id(),
            season=season,
            start_time=self.metrics.start_time or current_time,
            end_time=current_time,
            total_players=0,  # Will be set by caller
            total_passing_stats=0,  # Will be set by caller
            total_splits=0,  # Will be set by caller
            total_splits_advanced=0,  # Will be set by caller
            success_rate=self.metrics.success_rate,
            errors=self.metrics.errors,
            warnings=self.metrics.warnings,
            created_at=current_time,
            updated_at=current_time
        ) 