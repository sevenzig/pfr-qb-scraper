#!/usr/bin/env python3
"""
Unified Core Scraper for NFL QB Data
Consolidates functionality from all legacy scrapers with enhanced features
"""

import asyncio
import logging
import sys
import os
import time
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union, Any, cast
from dataclasses import dataclass
from abc import ABC, abstractmethod

import pandas as pd
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from config.config import config
    from database.db_manager import DatabaseManager
    from models.qb_models import QBBasicStats, QBAdvancedStats, QBSplitStats, Player
    from utils.data_utils import normalize_pfr_team_code
except ImportError:
    # Fallback for testing
    config = None
    DatabaseManager = None
    QBBasicStats = None
    QBAdvancedStats = None
    QBSplitStats = None
    Player = None
    normalize_pfr_team_code = lambda x: x

logger = logging.getLogger(__name__)


@dataclass
class ScrapingMetrics:
    """Metrics for scraping performance tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_violations: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_requests_per_minute(self) -> float:
        """Calculate requests per minute"""
        if not self.start_time or not self.end_time:
            return 0.0
        duration = (self.end_time - self.start_time).total_seconds() / 60
        if duration == 0:
            return 0.0
        return self.total_requests / duration


class RateLimiter:
    """Rate limiter for respectful scraping"""
    
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.last_request_time = 0.0
    
    def wait(self):
        """Wait for rate limit delay"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()


class CoreScraper:
    """Unified core scraper that consolidates all legacy scraper functionality"""
    
    def __init__(self, config=None, rate_limit_delay: float = 2.0):
        """Initialize the core scraper"""
        self.config = config or self._create_mock_config()
        self.rate_limit_delay = rate_limit_delay
        self.rate_limiter = RateLimiter(rate_limit_delay)
        self.session = self._create_session()
        self.metrics = ScrapingMetrics()
        self.base_url = "https://www.pro-football-reference.com"
        
        # Initialize database manager if available
        if DatabaseManager is not None:
            self.db_manager = DatabaseManager()
        else:
            self.db_manager = None
    
    def _create_mock_config(self):
        """Create mock config for testing"""
        class MockConfig:
            app = type('obj', (object,), {'target_season': 2024})()
            scraping = type('obj', (object,), {'rate_limit_delay': 2.0})()
        return MockConfig()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def make_request_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rate limiting"""
        self.metrics.total_requests += 1
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self.rate_limiter.wait()
                
                # Make request
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    self.metrics.successful_requests += 1
                    return response
                elif response.status_code == 429:
                    self.metrics.rate_limit_violations += 1
                    logger.warning(f"Rate limited on attempt {attempt + 1}, waiting longer...")
                    time.sleep(5 * (attempt + 1))  # Exponential backoff
                else:
                    logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        self.metrics.failed_requests += 1
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    def scrape_player_season(self, player_name: str, season: int) -> Optional[Dict[str, Any]]:
        """Scrape complete season data for a player"""
        logger.info(f"Scraping season data for {player_name} ({season})")
        
        try:
            # First, get the player's main stats
            main_stats = self._scrape_player_main_stats(player_name, season)
            if not main_stats:
                logger.error(f"Could not find main stats for {player_name}")
                return None
            
            # Then scrape splits data
            splits_data = self._scrape_player_splits(main_stats)
            
            return {
                'main_stats': main_stats,
                'splits_data': splits_data,
                'player_url': main_stats.player_url,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping {player_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def scrape_season_qbs(self, season: int) -> List[Dict[str, Any]]:
        """Scrape all QBs for a given season"""
        logger.info(f"Scraping all QBs for {season} season")
        
        # Get all QB main stats first
        all_qb_stats = self._scrape_all_qb_main_stats(season)
        
        results = []
        total_qbs = len(all_qb_stats)
        
        for i, qb_stat in enumerate(all_qb_stats, 1):
            logger.info(f"Processing QB {i}/{total_qbs}: {qb_stat.player_name}")
            
            try:
                # Scrape splits for this QB
                splits_data = self._scrape_player_splits(qb_stat)
                
                results.append({
                    'main_stats': qb_stat,
                    'splits_data': splits_data,
                    'player_url': qb_stat.player_url,
                    'success': True
                })
                
            except Exception as e:
                logger.error(f"Error processing {qb_stat.player_name}: {e}")
                results.append({
                    'main_stats': qb_stat,
                    'splits_data': [],
                    'player_url': qb_stat.player_url,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def scrape_team_qbs(self, team_code: str, season: int) -> List[Dict[str, Any]]:
        """Scrape all QBs for a team in a season"""
        logger.info(f"Scraping QBs for team {team_code} in {season}")
        
        # Get all QBs for the season
        all_qbs = self.scrape_season_qbs(season)
        
        # Filter for the specific team
        team_qbs = [
            qb for qb in all_qbs 
            if qb['main_stats'].team == team_code
        ]
        
        logger.info(f"Found {len(team_qbs)} QBs for team {team_code}")
        return team_qbs
    
    def _scrape_all_qb_main_stats(self, season: int) -> List[Any]:
        """Scrape main QB statistics for a season with proper multi-team player handling"""
        url = f"{self.base_url}/years/{season}/passing.htm"
        logger.info(f"Scraping QB main stats for {season} season from {url}")
        
        response = self.make_request_with_retry(url)
        if not response:
            logger.error("Failed to fetch main passing page")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main passing table
        table = soup.find('table', {'id': 'passing'})
        if not table:
            logger.error("Could not find passing table")
            return []
        
        # Dictionary to aggregate stats by player
        player_stats = {}
        current_time = datetime.now()
        
        # Find all rows in the table body
        tbody = table.find('tbody')
        if not tbody:
            logger.error("Could not find table body")
            return []
        
        for row in tbody.find_all('tr'):
            # Skip header rows and empty rows
            row_classes = row.get('class', [])
            if isinstance(row_classes, list) and 'thead' in row_classes:
                continue
            
            # Extract position from the row
            pos_cell = row.find('td', {'data-stat': 'pos'})
            if not pos_cell:
                continue
            
            position = pos_cell.get_text(strip=True).upper()
            
            # Filter for QBs only
            if position != 'QB':
                continue
            
            try:
                # Extract player name and URL
                name_cell = row.find('td', {'data-stat': 'name_display'})
                if not name_cell:
                    continue
                
                name_link = name_cell.find('a')
                if not name_link:
                    continue
                
                player_name = name_link.get_text(strip=True)
                href = name_link.get('href', '')
                player_url = self.base_url + str(href) if href else ''
                base_pfr_id = self._extract_player_id_from_url(player_url)

                if not base_pfr_id:
                    logger.warning(f"Could not extract pfr_id for {player_name}, skipping.")
                    continue
                
                # Extract team
                team_cell = row.find('td', {'data-stat': 'team_name_abbr'})
                team_code = normalize_pfr_team_code(team_cell.get_text(strip=True) if team_cell else '')
                
                # Extract all the stats
                stats = self._extract_comprehensive_row_stats(cast(Tag, row))
                
                # Use base PFR ID for all records
                pfr_id = base_pfr_id
                
                # Check if this is a multi-team player
                is_multi_team = team_code and ('2TM' in team_code or '3TM' in team_code)
                
                if pfr_id in player_stats:
                    # Player already exists - aggregate stats for multi-team players
                    existing = player_stats[pfr_id]
                    if is_multi_team:
                        # For multi-team players, aggregate the stats
                        existing['teams'].add(team_code)
                        existing['stats'] = self._aggregate_stats(existing['stats'], stats)
                        logger.info(f"Aggregating stats for multi-team player {player_name} ({team_code})")
                    else:
                        # For single team players, just update team info if needed
                        existing['teams'].add(team_code)
                        logger.info(f"Updated team info for {player_name} ({team_code})")
                else:
                    # New player - create initial record
                    player_stats[pfr_id] = {
                        'pfr_id': pfr_id,
                        'player_name': player_name,
                        'player_url': player_url,
                        'season': season,
                        'teams': {team_code} if team_code else set(),
                        'stats': stats,
                        'is_multi_team': is_multi_team
                    }
                    logger.info(f"New player {player_name} ({team_code})")
                
            except Exception as e:
                logger.error(f"Error processing QB row: {e}")
                continue
        
        # Convert aggregated data to QBBasicStats objects
        qb_stats = []
        for pfr_id, player_data in player_stats.items():
            try:
                stats = player_data['stats']
                teams = player_data['teams']
                
                # Create team string for multi-team players
                if player_data['is_multi_team']:
                    team_str = ','.join(sorted(teams))
                    # Ensure team string doesn't exceed 10 characters
                    if len(team_str) > 10:
                        logger.warning(f"Team string '{team_str}' exceeds 10 characters, truncating")
                        # Try to keep as many teams as possible while staying under 10 chars
                        if len(teams) >= 3:
                            # For 3+ teams, take first two teams only
                            first_two_teams = sorted(list(teams))[:2]
                            team_str = ','.join(first_two_teams)
                            logger.info(f"Truncated to first two teams: {team_str}")
                        else:
                            # For 2 teams, truncate the string
                            team_str = team_str[:10]
                else:
                    team_str = list(teams)[0] if teams else ''
                    # Ensure single team string doesn't exceed 10 characters
                    if len(team_str) > 10:
                        logger.warning(f"Team string '{team_str}' exceeds 10 characters, truncating")
                        team_str = team_str[:10]
                
                # Create QBBasicStats object if available
                if QBBasicStats is not None:
                    qb_stat = QBBasicStats(
                        pfr_id=pfr_id,
                        player_name=player_data['player_name'],
                        player_url=player_data['player_url'],
                        season=season,
                        rk=self._safe_int(stats.get('rank')),
                        age=self._safe_int(stats.get('age')),
                        team=team_str,
                        pos='QB',
                        g=self._safe_int(stats.get('games', 0)),
                        gs=self._safe_int(stats.get('games_started', 0)),
                        qb_rec=stats.get('qb_record', ''),
                        cmp=self._safe_int(stats.get('completions', 0)),
                        att=self._safe_int(stats.get('attempts', 0)),
                        cmp_pct=self._safe_float(stats.get('completion_pct', 0)),
                        yds=self._safe_int(stats.get('pass_yards', 0)),
                        td=self._safe_int(stats.get('pass_tds', 0)),
                        td_pct=self._safe_float(stats.get('td_pct', 0)),
                        int=self._safe_int(stats.get('interceptions', 0)),
                        int_pct=self._safe_float(stats.get('int_pct', 0)),
                        first_downs=self._safe_int(stats.get('first_downs', 0)),
                        succ_pct=self._safe_float(stats.get('success_pct', 0)),
                        lng=self._safe_int(stats.get('longest_pass', 0)),
                        y_a=self._safe_float(stats.get('yards_per_attempt', 0)),
                        ay_a=self._safe_float(stats.get('adjusted_yards_per_attempt', 0)),
                        y_c=self._safe_float(stats.get('yards_per_completion', 0)),
                        y_g=self._safe_float(stats.get('yards_per_game', 0)),
                        rate=self._safe_float(stats.get('rating', 0)),
                        qbr=self._safe_float(stats.get('qbr', 0)),
                        sk=self._safe_int(stats.get('sacks', 0)),
                        sk_yds=self._safe_int(stats.get('sack_yards', 0)),
                        sk_pct=self._safe_float(stats.get('sack_pct', 0)),
                        ny_a=self._safe_float(stats.get('net_yards_per_attempt', 0)),
                        any_a=self._safe_float(stats.get('adjusted_net_yards_per_attempt', 0)),
                        four_qc=self._safe_int(stats.get('fourth_quarter_comebacks', 0)),
                        gwd=self._safe_int(stats.get('game_winning_drives', 0)),
                        awards=stats.get('awards', ''),
                        player_additional=stats.get('player_additional', ''),
                        scraped_at=current_time,
                        updated_at=current_time
                    )
                else:
                    # Mock object for testing
                    qb_stat = type('obj', (object,), {
                        'pfr_id': pfr_id,
                        'player_name': player_data['player_name'],
                        'player_url': player_data['player_url'],
                        'season': season,
                        'team': team_str
                    })()
                
                qb_stats.append(qb_stat)
                team_info = f"({team_str})" if team_str else ""
                logger.info(f"Final QB stats for {player_data['player_name']} {team_info}")
                
            except Exception as e:
                logger.error(f"Error creating QB stat object for {pfr_id}: {e}")
                continue
        
        logger.info(f"Successfully extracted stats for {len(qb_stats)} unique QBs")
        return qb_stats
    
    def _aggregate_stats(self, existing_stats: Dict[str, Any], new_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate stats for multi-team players"""
        aggregated = existing_stats.copy()
        
        # For numeric stats, sum them
        numeric_fields = [
            'completions', 'attempts', 'pass_yards', 'pass_tds', 'interceptions',
            'first_downs', 'longest_pass', 'sacks', 'sack_yards', 'fourth_quarter_comebacks',
            'game_winning_drives', 'games', 'games_started'
        ]
        
        for field in numeric_fields:
            existing_val = self._safe_int(existing_stats.get(field, 0))
            new_val = self._safe_int(new_stats.get(field, 0))
            aggregated[field] = existing_val + new_val
        
        # For percentage/rate stats, recalculate based on aggregated totals
        if aggregated.get('attempts', 0) > 0:
            aggregated['completion_pct'] = (aggregated.get('completions', 0) / aggregated.get('attempts', 0)) * 100
            aggregated['td_pct'] = (aggregated.get('pass_tds', 0) / aggregated.get('attempts', 0)) * 100
            aggregated['int_pct'] = (aggregated.get('interceptions', 0) / aggregated.get('attempts', 0)) * 100
        
        if aggregated.get('attempts', 0) > 0:
            aggregated['yards_per_attempt'] = aggregated.get('pass_yards', 0) / aggregated.get('attempts', 0)
        
        if aggregated.get('completions', 0) > 0:
            aggregated['yards_per_completion'] = aggregated.get('pass_yards', 0) / aggregated.get('completions', 0)
        
        if aggregated.get('games', 0) > 0:
            aggregated['yards_per_game'] = aggregated.get('pass_yards', 0) / aggregated.get('games', 0)
        
        # Keep the highest rating and QBR
        aggregated['rating'] = max(
            self._safe_float(existing_stats.get('rating', 0)),
            self._safe_float(new_stats.get('rating', 0))
        )
        aggregated['qbr'] = max(
            self._safe_float(existing_stats.get('qbr', 0)),
            self._safe_float(new_stats.get('qbr', 0))
        )
        
        # Keep the longest pass
        aggregated['longest_pass'] = max(
            self._safe_int(existing_stats.get('longest_pass', 0)),
            self._safe_int(new_stats.get('longest_pass', 0))
        )
        
        return aggregated
    
    def _scrape_player_main_stats(self, player_name: str, season: int) -> Optional[Any]:
        """Scrape main stats for a specific player"""
        # For now, get from the season scrape and filter
        all_qbs = self._scrape_all_qb_main_stats(season)
        
        # Find the specific player
        for qb in all_qbs:
            if qb.player_name.lower() == player_name.lower():
                return qb
        
        logger.error(f"Could not find player {player_name} in {season} season")
        return None
    
    def _scrape_player_splits(self, qb_stat: Any) -> List[Any]:
        """Scrape splits data for a player"""
        logger.info(f"Scraping splits for {qb_stat.player_name}")
        
        # Extract player ID from URL
        player_id = self._extract_player_id_from_url(qb_stat.player_url)
        if not player_id:
            logger.error(f"Could not extract player ID from URL: {qb_stat.player_url}")
            return []
        
        # Extract first letter of player ID for URL construction
        first_letter = player_id[0].upper() if player_id else None
        if not first_letter:
            logger.error(f"Could not extract first letter from player ID: {player_id}")
            return []
        
        # Construct splits URL with first letter
        splits_url = f"{self.base_url}/players/{first_letter}/{player_id}/splits/{qb_stat.season}/"
        
        response = self.make_request_with_retry(splits_url)
        if not response:
            logger.error(f"Failed to fetch splits page for {qb_stat.player_name}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        all_splits = []
        current_time = datetime.now()
        
        # Find all tables on the page
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on splits page for {qb_stat.player_name}")
        
        splits_tables_found = 0
        for table in tables:
            if self._is_splits_table(table):
                splits_tables_found += 1
                table_id = table.get('id', 'unknown')
                logger.info(f"Processing splits table: {table_id}")
                splits = self._process_splits_table(table, qb_stat, current_time)
                logger.info(f"Extracted {len(splits)} splits from table {table_id}")
                all_splits.extend(splits)
        
        logger.info(f"Total splits tables found: {splits_tables_found}")
        
        logger.info(f"Extracted {len(all_splits)} splits for {qb_stat.player_name}")
        return all_splits
    
    def _find_splits_tables(self, soup: BeautifulSoup) -> List[Tag]:
        """Find all splits tables in the page"""
        tables = soup.find_all('table')
        splits_tables = []
        
        logger.info(f"Found {len(tables)} total tables on page")
        
        for i, table in enumerate(tables):
            table_id = table.get('id', '')
            table_class = table.get('class', [])
            table_caption = table.find('caption')
            caption_text = table_caption.get_text() if table_caption else ''
            
            logger.info(f"Table {i+1}: id='{table_id}', class='{table_class}', caption='{caption_text[:50]}...'")
            
            if self._is_splits_table(table):
                logger.info(f"  -> Identified as splits table")
                splits_tables.append(table)
            else:
                logger.info(f"  -> Not a splits table")
        
        logger.info(f"Total splits tables found: {len(splits_tables)}")
        return splits_tables
    
    def _extract_player_id_from_url(self, player_url: str) -> Optional[str]:
        """Extract player ID from PFR URL"""
        if not player_url:
            return None
        
        # Pattern: /players/{first_letter}/{player_id}.htm
        match = re.search(r'/players/[A-Z]/([^.]+)\.htm', player_url)
        return match.group(1) if match else None
    
    def _is_splits_table(self, table: Tag) -> bool:
        """Check if a table contains splits data"""
        # Look for characteristic splits table features
        table_id = table.get('id', '')
        table_class = table.get('class', [])
        
        logger.info(f"Checking table: id='{table_id}', class='{table_class}'")
        
        # Check for splits-related IDs (more comprehensive)
        splits_keywords = ['splits', 'split', 'advanced', 'basic', 'situational', 'game']
        if any(keyword in table_id.lower() for keyword in splits_keywords):
            logger.info(f"Table {table_id} identified as splits table by ID")
            return True
        
        # Check for characteristic headers (more comprehensive)
        headers = table.find_all('th')
        header_texts = [header.get_text(strip=True).lower() for header in headers]
        logger.info(f"Table {table_id} headers: {header_texts}")
        
        # Look for splits-related header patterns
        splits_header_patterns = [
            'split', 'value', 'cmp', 'att', 'yds', 'td', 'int', 'rate',
            'wins', 'losses', 'ties', 'games', 'g', 'w', 'l', 't',
            'rush', 'sack', 'first', 'down'
        ]
        
        for header_text in header_texts:
            if any(pattern in header_text for pattern in splits_header_patterns):
                logger.info(f"Table {table_id} identified as splits table by header: {header_text}")
                return True
        
        # Check for data-stat attributes that indicate splits data
        cells = table.find_all(['td', 'th'])
        data_stats = set()
        for cell in cells:
            data_stat = cell.get('data-stat', '')
            if data_stat:
                data_stats.add(data_stat)
        
        splits_data_stats = {
            'split_value', 'pass_cmp', 'pass_att', 'pass_yds', 'pass_td',
            'wins', 'losses', 'ties', 'games', 'g', 'w', 'l', 't'
        }
        
        if data_stats.intersection(splits_data_stats):
            logger.info(f"Table {table_id} identified as splits table by data-stat attributes: {data_stats.intersection(splits_data_stats)}")
            return True
        
        logger.info(f"Table {table_id} rejected as splits table")
        return False
    
    def _process_splits_table(self, table: Tag, qb_stat: Any, current_time: datetime) -> List[Any]:
        """Process a splits table and extract data"""
        splits = []
        
        # Determine split type from table
        table_id = table.get('id', '')
        split_type = self._determine_split_type(table_id)
        
        # Determine if this is a basic splits table or advanced splits table
        is_advanced_splits = 'advanced' in table_id.lower() or 'splits_advanced' in table_id.lower()
        
        logger.info(f"Processing table {table_id} as {'advanced' if is_advanced_splits else 'basic'} splits")
        
        # Find all rows in the table
        rows = table.find_all('tr')
        logger.info(f"Found {len(rows)} rows in table {table_id}")
        
        processed_rows = 0
        header_row = True
        for row in rows:
            if header_row:
                header_row = False
                logger.info(f"Skipping first header row in table {table_id}")
                continue
            # Now process all rows, even if they contain <th>
            try:
                # Extract split data
                split_data = self._extract_split_row_stats(row)
                
                if split_data:
                    processed_rows += 1
                    logger.info(f"Successfully extracted split data: {split_data.get('value', 'unknown')}")
                    
                    if is_advanced_splits:
                        # Create QBAdvancedStats object for advanced splits
                        if QBAdvancedStats is not None:
                            split = QBAdvancedStats(
                                pfr_id=qb_stat.pfr_id,
                                player_name=qb_stat.player_name,
                                season=qb_stat.season,
                                split=split_type,
                                value=split_data.get('value', ''),
                                cmp=self._safe_int(split_data.get('completions', 0)),
                                att=self._safe_int(split_data.get('attempts', 0)),
                                inc=self._safe_int(split_data.get('incompletions', 0)),
                                cmp_pct=self._safe_float(split_data.get('completion_pct', 0.0)),
                                yds=self._safe_int(split_data.get('yards', 0)),
                                td=self._safe_int(split_data.get('touchdowns', 0)),
                                first_downs=self._safe_int(split_data.get('first_downs', 0)),
                                int=self._safe_int(split_data.get('interceptions', 0)),
                                rate=self._safe_float(split_data.get('rating', 0.0)),
                                sk=self._safe_int(split_data.get('sacks', 0)),
                                sk_yds=self._safe_int(split_data.get('sack_yards', 0)),
                                y_a=self._safe_float(split_data.get('yards_per_attempt', 0.0)),
                                ay_a=self._safe_float(split_data.get('adjusted_yards_per_attempt', 0.0)),
                                rush_att=self._safe_int(split_data.get('rush_attempts', 0)),
                                rush_yds=self._safe_int(split_data.get('rush_yards', 0)),
                                rush_y_a=self._safe_float(split_data.get('rush_yards_per_attempt', 0.0)),
                                rush_td=self._safe_int(split_data.get('rush_touchdowns', 0)),
                                rush_first_downs=self._safe_int(split_data.get('rush_first_downs', 0)),
                                scraped_at=current_time,
                                updated_at=current_time
                            )
                        else:
                            # Mock object for testing
                            split = type('obj', (object,), {
                                'pfr_id': qb_stat.pfr_id,
                                'player_name': qb_stat.player_name,
                                'season': qb_stat.season,
                                'split': split_type,
                                'value': split_data.get('value', ''),
                                'cmp': split_data.get('completions', 0),
                                'att': split_data.get('attempts', 0),
                                'yds': split_data.get('yards', 0),
                                'td': split_data.get('touchdowns', 0),
                                'int': split_data.get('interceptions', 0),
                                'rate': split_data.get('rating', 0.0)
                            })()
                    else:
                        # Create QBSplitStats object for basic splits (with wins, losses, ties)
                        if QBSplitStats is not None:
                            split = QBSplitStats(
                                pfr_id=qb_stat.pfr_id,
                                player_name=qb_stat.player_name,
                                season=qb_stat.season,
                                split=split_type,
                                value=split_data.get('value', ''),
                                g=self._safe_int(split_data.get('games', 0)),
                                w=self._safe_int(split_data.get('wins', 0)),
                                l=self._safe_int(split_data.get('losses', 0)),
                                t=self._safe_int(split_data.get('ties', 0)),
                                cmp=self._safe_int(split_data.get('completions', 0)),
                                att=self._safe_int(split_data.get('attempts', 0)),
                                inc=self._safe_int(split_data.get('incompletions', 0)),
                                cmp_pct=self._safe_float(split_data.get('completion_pct', 0.0)),
                                yds=self._safe_int(split_data.get('yards', 0)),
                                td=self._safe_int(split_data.get('touchdowns', 0)),
                                int=self._safe_int(split_data.get('interceptions', 0)),
                                rate=self._safe_float(split_data.get('rating', 0.0)),
                                sk=self._safe_int(split_data.get('sacks', 0)),
                                sk_yds=self._safe_int(split_data.get('sack_yards', 0)),
                                y_a=self._safe_float(split_data.get('yards_per_attempt', 0.0)),
                                ay_a=self._safe_float(split_data.get('adjusted_yards_per_attempt', 0.0)),
                                a_g=self._safe_float(split_data.get('attempts_per_game', 0.0)),
                                y_g=self._safe_float(split_data.get('yards_per_game', 0.0)),
                                rush_att=self._safe_int(split_data.get('rush_attempts', 0)),
                                rush_yds=self._safe_int(split_data.get('rush_yards', 0)),
                                rush_y_a=self._safe_float(split_data.get('rush_yards_per_attempt', 0.0)),
                                rush_td=self._safe_int(split_data.get('rush_touchdowns', 0)),
                                rush_a_g=self._safe_float(split_data.get('rush_attempts_per_game', 0.0)),
                                rush_y_g=self._safe_float(split_data.get('rush_yards_per_game', 0.0)),
                                total_td=self._safe_int(split_data.get('total_touchdowns', 0)),
                                pts=self._safe_int(split_data.get('points', 0)),
                                fmb=self._safe_int(split_data.get('fumbles', 0)),
                                fl=self._safe_int(split_data.get('fumbles_lost', 0)),
                                ff=self._safe_int(split_data.get('fumbles_forced', 0)),
                                fr=self._safe_int(split_data.get('fumbles_recovered', 0)),
                                fr_yds=self._safe_int(split_data.get('fumble_recovery_yards', 0)),
                                fr_td=self._safe_int(split_data.get('fumble_recovery_tds', 0)),
                                scraped_at=current_time,
                                updated_at=current_time
                            )
                        else:
                            # Mock object for testing
                            split = type('obj', (object,), {
                                'pfr_id': qb_stat.pfr_id,
                                'player_name': qb_stat.player_name,
                                'season': qb_stat.season,
                                'split': split_type,
                                'value': split_data.get('value', ''),
                                'w': split_data.get('wins', 0),
                                'l': split_data.get('losses', 0),
                                't': split_data.get('ties', 0),
                                'cmp': split_data.get('completions', 0),
                                'att': split_data.get('attempts', 0),
                                'yds': split_data.get('yards', 0),
                                'td': split_data.get('touchdowns', 0),
                                'int': split_data.get('interceptions', 0),
                                'rate': split_data.get('rating', 0.0)
                            })()
                    
                    splits.append(split)
            
            except Exception as e:
                logger.error(f"Error processing split row: {e}")
                continue
        
        # DEBUG: Print all splits extracted from this table
        import logging
        logging.getLogger(__name__).debug(f"Extracted splits from table '{table_id}': {splits}")
        return splits
    
    def _determine_split_type(self, table_id: str) -> str:
        """Determine the type of split from table ID"""
        table_id_lower = table_id.lower()
        
        if 'home' in table_id_lower or 'away' in table_id_lower:
            return 'home_away'
        elif 'quarter' in table_id_lower:
            return 'by_quarter'
        elif 'down' in table_id_lower:
            return 'by_down'
        elif 'distance' in table_id_lower:
            return 'by_distance'
        elif 'win' in table_id_lower or 'loss' in table_id_lower:
            return 'win_loss'
        elif 'month' in table_id_lower:
            return 'by_month'
        elif 'half' in table_id_lower:
            return 'by_half'
        else:
            return 'other'
    
    def _extract_comprehensive_row_stats(self, row: Tag) -> Dict[str, Any]:
        """Extract comprehensive stats from a table row"""
        stats = {}
        
        # Define the mapping of data-stat attributes to our field names
        stat_mapping = {
            'rank': 'rank',
            'age': 'age',
            'team_name_abbr': 'team',
            'qb_rec': 'qb_record',
            'g': 'games',
            'gs': 'games_started',
            'pass_cmp': 'completions',
            'pass_att': 'attempts',
            'pass_cmp_pct': 'completion_pct',
            'pass_yds': 'pass_yards',
            'pass_td': 'pass_tds',
            'pass_td_pct': 'td_pct',
            'pass_int': 'interceptions',
            'pass_int_pct': 'int_pct',
            'pass_first_down': 'first_downs',
            'pass_succ_pct': 'success_pct',
            'pass_long': 'longest_pass',
            'pass_yds_per_att': 'yards_per_attempt',
            'pass_adj_yds_per_att': 'adjusted_yards_per_attempt',
            'pass_yds_per_cmp': 'yards_per_completion',
            'pass_yds_per_g': 'yards_per_game',
            'pass_rating': 'rating',
            'qbr': 'qbr',
            'pass_sacked': 'sacks',
            'pass_sacked_yds': 'sack_yards',
            'pass_sacked_pct': 'sack_pct',
            'pass_net_yds_per_att': 'net_yards_per_attempt',
            'pass_adj_net_yds_per_att': 'adjusted_net_yards_per_attempt',
            'pass_4qc': 'fourth_quarter_comebacks',
            'pass_gwd': 'game_winning_drives',
            'awards': 'awards',
            'player_additional': 'player_additional'
        }
        
        for stat_attr, field_name in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            if cell:
                stats[field_name] = cell.get_text(strip=True)
        
        return stats
    
    def _extract_split_row_stats(self, row: Tag) -> Optional[Dict[str, Any]]:
        """Extract stats from a split table row (fully mapped for QBSplitStats)"""
        stats = {}
        # Get all cells in the row
        cells = row.find_all('td')
        logger.info(f"Found {len(cells)} cells in row")
        # Get the split value (usually first column)
        value_cell = row.find('td')
        if value_cell:
            stats['value'] = value_cell.get_text(strip=True)
            logger.info(f"Split value: {stats['value']}")
        # Comprehensive mapping for all QBSplitStats fields
        stat_mapping = {
            'g': 'games',                # Games
            'wins': 'wins',              # Wins
            'losses': 'losses',          # Losses
            'ties': 'ties',              # Ties
            'pass_cmp': 'completions',   # Completions
            'pass_att': 'attempts',      # Attempts
            'pass_inc': 'incompletions', # Incompletions
            'pass_cmp_pct': 'completion_pct', # Completion %
            'pass_yds': 'yards',         # Passing Yards
            'pass_td': 'touchdowns',     # Passing TDs
            'pass_int': 'interceptions', # Interceptions
            'pass_rating': 'rating',     # Passer Rating
            'pass_sacked': 'sacks',      # Sacks
            'pass_sacked_yds': 'sack_yards', # Sack Yards
            'pass_yds_per_att': 'yards_per_attempt', # Y/A
            'pass_adj_yds_per_att': 'adjusted_yards_per_attempt', # AY/A
            'pass_att_per_g': 'attempts_per_game', # A/G
            'pass_yds_per_g': 'yards_per_game',    # Y/G
            'rush_att': 'rush_attempts',           # Rush Attempts
            'rush_yds': 'rush_yards',              # Rush Yards
            'rush_yds_per_att': 'rush_yards_per_attempt', # Rush Y/A
            'rush_td': 'rush_touchdowns',          # Rush TDs
            'rush_att_per_g': 'rush_attempts_per_game',   # Rush A/G
            'rush_yds_per_g': 'rush_yards_per_game',      # Rush Y/G
            'total_td': 'total_touchdowns',        # Total TDs
            'scoring': 'points',                   # Points
            'fumbles': 'fumbles',                  # Fumbles
            'fumbles_lost': 'fumbles_lost',        # Fumbles Lost
            'fumbles_forced': 'fumbles_forced',    # Fumbles Forced
            'fumbles_rec': 'fumbles_recovered',    # Fumbles Recovered
            'fumbles_rec_yds': 'fumble_recovery_yards',   # Fumble Recovery Yards
            'fumbles_rec_td': 'fumble_recovery_tds',      # Fumble Recovery TDs
        }
        # Log all data-stat attributes found in the row
        data_stats_found = []
        for cell in cells:
            data_stat = cell.get('data-stat')
            if data_stat:
                data_stats_found.append(data_stat)
                cell_text = cell.get_text(strip=True)
                logger.info(f"Found data-stat '{data_stat}' with value '{cell_text}'")
        logger.info(f"Data-stat attributes found: {data_stats_found}")
        for stat_attr, field_name in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            if cell:
                stats[field_name] = cell.get_text(strip=True)
        # Patch: Add all QBSplitStats fields with correct mapping
        # (fields not present in the row will remain missing from stats)
        logger.info(f"Extracted split row stats: {stats}")
        return stats if stats else None
    
    def _safe_int(self, value: Union[str, int, float, None]) -> int:
        """Safely convert value to integer"""
        if value is None or value == '':
            return 0
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return 0
    
    def _safe_float(self, value: Union[str, int, float, None]) -> float:
        """Safely convert value to float"""
        if value is None or value == '':
            return 0.0
        try:
            return float(str(value))
        except (ValueError, TypeError):
            return 0.0
    
    def get_metrics(self) -> ScrapingMetrics:
        """Get scraping metrics"""
        return self.metrics
    
    def reset_metrics(self):
        """Reset scraping metrics"""
        self.metrics = ScrapingMetrics()
    
    def start_scraping_session(self):
        """Start a scraping session and record metrics"""
        self.metrics.start_time = datetime.now()
        logger.info("Started scraping session")
    
    def end_scraping_session(self):
        """End a scraping session and record metrics"""
        self.metrics.end_time = datetime.now()
        duration = (self.metrics.end_time - self.metrics.start_time).total_seconds()
        logger.info(f"Ended scraping session. Duration: {duration:.2f}s, "
                   f"Requests: {self.metrics.total_requests}, "
                   f"Success Rate: {self.metrics.get_success_rate():.1f}%") 