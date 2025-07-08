#!/usr/bin/env python3
"""
Enhanced Pro Football Reference scraper with automatic split discovery
Comprehensive QB data extraction with robust error handling and rate limiting
"""

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
import random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass

from models.qb_models import Player, QBBasicStats, QBAdvancedStats, QBSplitStats, Team, ScrapingLog
from utils.data_utils import (
    safe_int, safe_float, safe_percentage, clean_player_name, 
    generate_player_id, calculate_passer_rating, normalize_split_type,
    generate_session_id, calculate_processing_time
)
from config.config import config, SplitTypes, SplitCategories

logger = logging.getLogger(__name__)

@dataclass
class ScrapingMetrics:
    """Metrics for tracking scraping performance"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_violations: int = 0
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
    
    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_requests_per_minute(self) -> float:
        """Calculate requests per minute"""
        if not self.start_time:
            return 0.0
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        if elapsed == 0:
            return 0.0
        return self.total_requests / elapsed

class EnhancedPFRScraper:
    """Enhanced Pro Football Reference scraper with automatic split discovery"""
    
    def __init__(self, rate_limit_delay: float = None):
        self.base_url = "https://www.pro-football-reference.com"
        self.rate_limit_delay = rate_limit_delay or config.get_rate_limit_delay()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.scraping.user_agent
        })
        
        # Rate limiting lock
        self.rate_limit_lock = threading.Lock()
        self.last_request_time = 0
        
        # Metrics tracking
        self.metrics = ScrapingMetrics()
        self.metrics.start_time = datetime.now()
        
        # Known split patterns for automatic discovery - updated based on actual PFR structure
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
    
    def respect_rate_limit(self):
        """Implement rate limiting with jitter"""
        with self.rate_limit_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Add jitter to avoid thundering herd
            jitter = random.uniform(-config.scraping.jitter_range, config.scraping.jitter_range)
            required_delay = max(2.0, self.rate_limit_delay + jitter)
            
            if time_since_last < required_delay:
                sleep_time = required_delay - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
    
    def make_request_with_retry(self, url: str, max_retries: int = None) -> Optional[requests.Response]:
        """
        Make HTTP request with comprehensive error handling and retry logic
        
        Args:
            url: URL to request
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response object or None if all retries failed
        """
        max_retries = max_retries or config.scraping.max_retries
        self.metrics.total_requests += 1
        
        for attempt in range(max_retries):
            try:
                self.respect_rate_limit()
                
                response = self.session.get(
                    url, 
                    timeout=config.scraping.timeout,
                    headers={'User-Agent': config.scraping.user_agent}
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    self.metrics.rate_limit_violations += 1
                    wait_time = 60 * (attempt + 1)  # Exponential backoff for rate limits
                    logger.warning(f"Rate limited, waiting {wait_time} seconds (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                self.metrics.successful_requests += 1
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries}): {url}")
                if attempt == max_retries - 1:
                    self.metrics.add_error(f"Request timeout after {max_retries} attempts: {url}")
                    self.metrics.failed_requests += 1
                    return None
                time.sleep(5 * (attempt + 1))
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries}): {url}")
                if attempt == max_retries - 1:
                    self.metrics.add_error(f"Connection error after {max_retries} attempts: {url}")
                    self.metrics.failed_requests += 1
                    return None
                time.sleep(10 * (attempt + 1))
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    self.metrics.add_error(f"Request failed after {max_retries} attempts: {url} - {e}")
                    self.metrics.failed_requests += 1
                    return None
                time.sleep(5 * (attempt + 1))
        
        return None
    
    def parse_table_data(self, soup: BeautifulSoup, table_id: str) -> Optional[pd.DataFrame]:
        """
        Parse HTML table data manually using BeautifulSoup to preserve original structure
        
        Args:
            soup: BeautifulSoup object
            table_id: ID of the table to parse (may include index like 'splits_table_0')
            
        Returns:
            DataFrame with table data or None if parsing failed
        """
        try:
            # Find the table by ID
            table = soup.find('table', {'id': table_id})
            
            # If no ID match, check if it's a generated ID with index
            if not table and table_id.startswith('splits_table_'):
                try:
                    # Extract index from table_id (e.g., 'splits_table_1' -> index 1)
                    index_str = table_id.split('_')[-1]
                    table_index = int(index_str)
                    
                    # Find all tables and get the one at the specified index
                    tables = soup.find_all('table')
                    if 0 <= table_index < len(tables):
                        table = tables[table_index]
                        logger.debug(f"Found table at index {table_index} for ID {table_id}")
                except (ValueError, IndexError):
                    logger.debug(f"Could not parse table index from ID: {table_id}")
            
            if not table:
                # If still no table found, try to find the largest table (likely the splits table)
                tables = soup.find_all('table')
                if not tables:
                    logger.debug("No tables found on page")
                    return None
                
                # Find the table with the most rows (likely the splits table)
                largest_table = max(tables, key=lambda t: len(t.find_all('tr')))
                table = largest_table
                logger.debug(f"Selected table with {len(table.find_all('tr'))} rows as splits table")
            
            # Find the tbody
            tbody = table.find('tbody')
            if not tbody:
                logger.debug("No tbody found in table")
                return None
            
            rows = tbody.find_all('tr')
            logger.debug(f"Processing {len(rows)} rows in splits table")
            
            # Extract headers from the first thead row (if it exists)
            headers = []
            data_rows = []
            
            for i, row in enumerate(rows):
                ths = row.find_all('th')
                tds = row.find_all('td')
                
                # Check if this is a column header row (class="thead")
                if 'thead' in row.get('class', []):
                    # Extract column headers
                    headers = [th.get_text(strip=True) for th in ths]
                    logger.debug(f"Found column headers: {headers}")
                    continue
                
                # Check if this is a section header row (one th with section name)
                if len(ths) == 1 and len(tds) > 0 and ths[0].get_text(strip=True):
                    # This is a section header, skip it for data extraction
                    continue
                
                # This should be a data row with split values and stats
                if len(ths) >= 1 and len(tds) > 0:
                    # Extract the split value from the first th (if not empty) or first td
                    split_value = ths[0].get_text(strip=True) if ths[0].get_text(strip=True) else tds[0].get_text(strip=True)
                    
                    # Extract all the stat values from tds - these contain nested tables with actual stats
                    stat_values = []
                    for td in tds:
                        # Check if this td contains a nested table with stats
                        nested_table = td.find('table')
                        if nested_table:
                            # Extract stats from the nested table
                            nested_rows = nested_table.find_all('tr')
                            nested_stats = []
                            for nested_row in nested_rows:
                                nested_cells = nested_row.find_all(['td', 'th'])
                                for cell in nested_cells:
                                    cell_text = cell.get_text(strip=True)
                                    if cell_text:
                                        nested_stats.append(cell_text)
                            stat_values.append(' '.join(nested_stats) if nested_stats else td.get_text(strip=True))
                        else:
                            # No nested table, just get the text
                            stat_values.append(td.get_text(strip=True))
                    
                    # Combine split value with stat values
                    row_data = [split_value] + stat_values
                    data_rows.append(row_data)
                    
                    logger.debug(f"Row {i}: split_value='{split_value}', stats={stat_values[:3]}...")
            
            if not headers:
                # If no headers found, create default headers
                if data_rows:
                    max_cols = max(len(row) for row in data_rows)
                    headers = ['Split'] + [f'Col_{i}' for i in range(max_cols - 1)]
                    logger.debug(f"Created default headers: {headers}")
            
            if not data_rows:
                logger.debug("No data rows found")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            logger.debug(f"Successfully parsed table '{table_id}' with {len(df)} rows and {len(df.columns)} columns")
            logger.debug(f"DataFrame columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error parsing table data: {e}")
            return None
    
    def discover_all_splits(self, player_url: str) -> Dict[str, List[str]]:
        """
        Automatically discover all available split tables on a player page
        
        Args:
            player_url: URL of the player's page
            
        Returns:
            Dictionary mapping split types to their categories
        """
        logger.info(f"Discovering splits for player page: {player_url}")
        
        response = self.make_request_with_retry(player_url)
        if not response:
            return {}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        discovered_splits = {}
        
        # Find all tables on the page
        tables = soup.find_all('table')
        
        for table in tables:
            table_id = table.get('id', '')
            if not table_id:
                continue
            
            # Try to identify split type from table ID or content
            split_type = self.identify_split_type(table_id, table)
            if split_type:
                categories = self.extract_split_categories(table)
                if categories:
                    discovered_splits[split_type] = categories
                    logger.info(f"Discovered split type '{split_type}' with {len(categories)} categories")
        
        return discovered_splits
    
    def identify_split_type(self, table_id: str, table_element) -> Optional[str]:
        """
        Identify split type from table ID or content
        
        Args:
            table_id: Table ID
            table_element: Table HTML element
            
        Returns:
            Split type or None if not identified
        """
        # Check table ID first
        table_id_lower = table_id.lower()
        
        # Log table ID for debugging
        logger.debug(f"Analyzing table ID: {table_id}")
        
        for split_type, patterns in self.split_patterns.items():
            for pattern in patterns:
                if re.search(pattern, table_id_lower, re.IGNORECASE):
                    logger.debug(f"Identified split type '{split_type}' from table ID pattern '{pattern}'")
                    return split_type
        
        # Check table headers
        headers = []
        header_row = table_element.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.get_text(strip=True).lower())
        
        header_text = ' '.join(headers)
        logger.debug(f"Table headers: {header_text}")
        
        for split_type, patterns in self.split_patterns.items():
            for pattern in patterns:
                if re.search(pattern, header_text, re.IGNORECASE):
                    logger.debug(f"Identified split type '{split_type}' from header pattern '{pattern}'")
                    return split_type
        
        # Check table content for split indicators
        tbody = table_element.find('tbody')
        if tbody:
            # Look for common split indicators in the first column
            first_column_values = []
            for row in tbody.find_all('tr')[:5]:  # Check first 5 rows
                first_cell = row.find(['td', 'th'])
                if first_cell:
                    cell_text = first_cell.get_text(strip=True).lower()
                    first_column_values.append(cell_text)
            
            content_text = ' '.join(first_column_values)
            logger.debug(f"First column content: {content_text}")
            
            for split_type, patterns in self.split_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content_text, re.IGNORECASE):
                        logger.debug(f"Identified split type '{split_type}' from content pattern '{pattern}'")
                        return split_type
        
        # If no specific pattern matches, check if it looks like a splits table
        if self._looks_like_splits_table(table_element):
            logger.debug(f"Table {table_id} appears to be a splits table based on structure")
            return 'general_splits'
        
        return None
    
    def _looks_like_splits_table(self, table_element) -> bool:
        """
        Check if a table looks like a splits table based on structure
        
        Args:
            table_element: Table HTML element
            
        Returns:
            True if table appears to be a splits table
        """
        # Check for common splits table characteristics
        tbody = table_element.find('tbody')
        if not tbody:
            return False
        
        # Look for rows with split categories in first column
        split_indicators = [
            'home', 'away', '1st quarter', '2nd quarter', '3rd quarter', '4th quarter',
            '1st half', '2nd half', 'overtime', 'september', 'october', 'november',
            'december', 'january', '1st down', '2nd down', '3rd down', '4th down',
            'win', 'loss', 'ahead', 'behind', 'tied', 'red zone', 'goal line',
            'sunday', 'monday', 'thursday', 'saturday', 'regular season', 'playoffs'
        ]
        
        rows_checked = 0
        split_like_rows = 0
        
        for row in tbody.find_all('tr')[:10]:  # Check first 10 rows
            if row.get('class') and 'thead' in row.get('class'):
                continue
            
            first_cell = row.find(['td', 'th'])
            if first_cell:
                cell_text = first_cell.get_text(strip=True).lower()
                rows_checked += 1
                
                # Check if this row looks like a split category
                for indicator in split_indicators:
                    if indicator in cell_text:
                        split_like_rows += 1
                        break
        
        # If more than 50% of rows look like splits, consider it a splits table
        if rows_checked > 0 and (split_like_rows / rows_checked) > 0.5:
            return True
        
        return False
    
    def extract_split_categories(self, table_element) -> List[str]:
        """
        Extract split categories from table
        
        Args:
            table_element: Table HTML element
            
        Returns:
            List of split categories
        """
        categories = []
        
        tbody = table_element.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                # Skip header rows
                if row.get('class') and 'thead' in row.get('class'):
                    continue
                
                # Skip empty rows
                if not row.get_text(strip=True):
                    continue
                
                # Get first cell (usually contains the category)
                first_cell = row.find(['td', 'th'])
                if first_cell:
                    category = first_cell.get_text(strip=True)
                    
                    # Clean up the category text
                    category = self._clean_category_text(category)
                    
                    # Only add non-empty, meaningful categories
                    if category and len(category) > 0 and category not in categories:
                        # Skip categories that are just numbers or common table artifacts
                        if not self._is_table_artifact(category):
                            categories.append(category)
                            logger.debug(f"Extracted category: {category}")
        
        logger.debug(f"Extracted {len(categories)} categories from table")
        return categories
    
    def _clean_category_text(self, category: str) -> str:
        """
        Clean up category text by removing common artifacts
        
        Args:
            category: Raw category text
            
        Returns:
            Cleaned category text
        """
        # Remove common table artifacts
        category = category.strip()
        
        # Remove asterisks and other common symbols
        category = re.sub(r'[*†‡§]', '', category)
        
        # Remove extra whitespace
        category = re.sub(r'\s+', ' ', category)
        
        return category.strip()
    
    def _is_table_artifact(self, category: str) -> bool:
        """
        Check if a category is just a table artifact (not a real split category)
        
        Args:
            category: Category text to check
            
        Returns:
            True if it's a table artifact
        """
        # Common table artifacts to ignore
        artifacts = [
            'split', 'category', 'type', 'total', 'overall', 'summary',
            'average', 'avg', 'mean', 'median', 'min', 'max',
            'rank', 'ranking', 'position', 'pos', 'player', 'name',
            'team', 'tm', 'games', 'g', 'games played', 'gp'
        ]
        
        category_lower = category.lower()
        
        # Check if it's just a number
        if category.isdigit():
            return True
        
        # Check if it's a common artifact
        for artifact in artifacts:
            if artifact in category_lower:
                return True
        
        # Check if it's too short to be meaningful
        if len(category) < 2:
            return True
        
        return False
    
    def get_qb_main_stats(self, season: int) -> Tuple[List[Player], List[QBBasicStats], List[QBAdvancedStats]]:
        """
        Scrape main QB statistics for a given season
        
        Args:
            season: Season year
            
        Returns:
            List of QBStats objects
        """
        url = f"{self.base_url}/years/{season}/passing.htm"
        logger.info(f"Scraping QB main stats for {season} season")
        
        response = self.make_request_with_retry(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        df = self.parse_table_data(soup, 'passing')
        
        if df is None:
            logger.error(f"Failed to parse QB stats table for {season}")
            return []
        
        players_list = []
        basic_stats_list = []
        advanced_stats_list = []
        current_time = datetime.now()
        
        for _, row in df.iterrows():
            try:
                # Skip header rows and empty rows
                if row.get('Player', '') == 'Player' or not row.get('Player'):
                    continue
                
                # Filter for QBs only - check position column
                position = row.get('Pos', '').strip().upper()
                if position != 'QB':
                    continue
                
                # Extract player name and generate PFR ID
                player_name = clean_player_name(row.get('Player', ''))
                if not player_name:
                    continue
                
                # Try to find player URL to get PFR ID
                player_url = self.find_player_url(player_name)
                pfr_id = generate_player_id(player_name, player_url)
                
                # Create Player object first
                player = Player(
                    pfr_id=pfr_id,
                    player_name=player_name,
                    pfr_url=player_url or '',
                    created_at=current_time,
                    updated_at=current_time
                )
                
                # Create QBBasicStats object
                basic_stats = QBBasicStats(
                    pfr_id=pfr_id,
                    season=season,
                    team=row.get('Tm', ''),
                    games_played=safe_int(row.get('G', '0')),
                    games_started=safe_int(row.get('GS', '0')),
                    completions=safe_int(row.get('Cmp', '0')),
                    attempts=safe_int(row.get('Att', '0')),
                    completion_pct=safe_percentage(row.get('Cmp%', '0')),
                    pass_yards=safe_int(row.get('Yds', '0')),
                    pass_tds=safe_int(row.get('TD', '0')),
                    interceptions=safe_int(row.get('Int', '0')),
                    longest_pass=safe_int(row.get('Lng', '0')),
                    rating=safe_float(row.get('Rate', '0')),
                    sacks=safe_int(row.get('Sk', '0')),
                    sack_yards=safe_int(row.get('Yds.1', '0')),
                    net_yards_per_attempt=safe_float(row.get('NY/A', '0')),
                    scraped_at=current_time,
                    updated_at=current_time
                )
                
                # Create QBAdvancedStats object
                advanced_stats = QBAdvancedStats(
                    pfr_id=pfr_id,
                    season=season,
                    qbr=safe_float(row.get('QBR', None)),
                    adjusted_net_yards_per_attempt=safe_float(row.get('ANY/A', '0')),
                    fourth_quarter_comebacks=safe_int(row.get('4QC', '0')),
                    game_winning_drives=safe_int(row.get('GWD', '0')),
                    scraped_at=current_time,
                    updated_at=current_time
                )
                
                # Validate all objects
                player_errors = player.validate()
                basic_errors = basic_stats.validate()
                advanced_errors = advanced_stats.validate()
                
                all_errors = player_errors + basic_errors + advanced_errors
                if all_errors:
                    for error in all_errors:
                        self.metrics.add_warning(f"Validation error for {player_name}: {error}")
                
                # Store all objects
                players_list.append(player)
                basic_stats_list.append(basic_stats)
                advanced_stats_list.append(advanced_stats)
                
            except Exception as e:
                self.metrics.add_error(f"Error processing QB stats row: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(players_list)} QB players with basic and advanced stats for {season}")
        return players_list, basic_stats_list, advanced_stats_list
    
    def find_player_url(self, player_name: str) -> Optional[str]:
        """
        Find player's PFR URL by searching
        
        Args:
            player_name: Player's name
            
        Returns:
            Player's PFR URL or None if not found
        """
        # This is a simplified approach - in production, you'd want to maintain
        # a mapping of player names to their PFR URLs
        
        # For now, generate a likely URL based on naming conventions
        # PFR uses format: /players/[FirstLetter]/[LastName][FirstName][##].htm
        parts = player_name.split()
        if len(parts) < 2:
            return None
        
        first_name = parts[0]
        last_name = parts[-1]
        
        # Generate potential URL
        first_letter = last_name[0].upper()
        player_code = f"{last_name[:4]}{first_name[:2]}00"
        
        return f"{self.base_url}/players/{first_letter}/{player_code}.htm"
    
    def scrape_player_splits(self, player_url: str, pfr_id: str, player_name: str, 
                           team: str, season: int, scraped_at: datetime) -> List[QBSplitStats]:
        """
        Scrape all splits for a specific player
        """
        splits = []
        response = self.make_request_with_retry(player_url)
        if not response:
            return splits
        soup = BeautifulSoup(response.content, 'html.parser')
        if '/splits/' in player_url:
            discovered_splits = self.discover_splits_from_page(soup)
        else:
            discovered_splits = self.discover_all_splits(player_url)
        for split_type, cat_to_col in discovered_splits.items():
            for category, split_value_col in cat_to_col.items():
                try:
                    table_id = self.find_table_id_for_split(soup, split_type, category)
                    if not table_id:
                        continue
                    df = self.parse_table_data(soup, table_id)
                    if df is not None:
                        split_stats = self.process_splits_table(
                            df, pfr_id, player_name, team, season, 
                            split_type, category, scraped_at, split_value_col
                        )
                        splits.extend(split_stats)
                except Exception as e:
                    self.metrics.add_error(f"Error processing split {split_type}/{category} for {player_name}: {e}")
                    continue
        return splits
    
    def discover_splits_from_page(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """
        Discover splits from a splits page (not main player page) using section-based logic.
        For each section, use the <tr><th>Section Name</th><td></td>...</tr> as the split type (section name),
        and collect split values under that section.
        Returns a dict mapping normalized split type to a dict of {category: original_section_name}.
        """
        discovered_splits = {}
        tables = soup.find_all('table')
        logger.debug(f"Found {len(tables)} tables on the page")
        
        # Process all tables that look like splits tables
        for table_idx, table in enumerate(tables):
            tbody = table.find('tbody')
            if not tbody:
                continue
                
            rows = tbody.find_all('tr')
            logger.debug(f"Table {table_idx}: {len(rows)} rows")
            
            # Only process tables with substantial data (likely splits tables)
            if len(rows) < 5:
                continue
                
            logger.debug(f"Processing table {table_idx} as potential splits table with {len(rows)} rows")
            
            current_split_type = None
            current_split_type_orig = None
            current_categories = []
            
            for row_idx, row in enumerate(rows):
                ths = row.find_all('th')
                tds = row.find_all('td')
                
                # Section header row: <tr><th>Section Name</th><td></td>...</tr>
                if len(ths) == 1 and len(tds) > 20 and ths[0].get_text(strip=True):
                    # Save previous section
                    if current_split_type and current_categories:
                        if current_split_type not in discovered_splits:
                            discovered_splits[current_split_type] = {}
                        discovered_splits[current_split_type].update({
                            cat: current_split_type_orig for cat in current_categories
                        })
                        logger.debug(f"Table {table_idx}: Discovered split type '{current_split_type}' with {len(current_categories)} categories")
                    
                    current_split_type_orig = ths[0].get_text(strip=True)
                    current_split_type = self._normalize_split_type(current_split_type_orig)
                    current_categories = []
                    logger.debug(f"Table {table_idx}, Row {row_idx}: New section header found, split_type='{current_split_type}' (orig='{current_split_type_orig}')")
                    continue
                
                # Skip thead rows (column headers)
                row_classes = row.get('class', [])
                if isinstance(row_classes, list) and 'thead' in row_classes:
                    continue
                
                # Data row - look for split values in the first column
                first_cell = row.find('td')
                if first_cell:
                    split_value = first_cell.get_text(strip=True)
                    if split_value and current_split_type and split_value not in current_categories:
                        current_categories.append(split_value)
                        logger.debug(f"Table {table_idx}, Row {row_idx}: Added category '{split_value}' to '{current_split_type}'")
            
            # Save the last section from this table
            if current_split_type and current_categories:
                if current_split_type not in discovered_splits:
                    discovered_splits[current_split_type] = {}
                discovered_splits[current_split_type].update({
                    cat: current_split_type_orig for cat in current_categories
                })
                logger.debug(f"Table {table_idx}: Final split type '{current_split_type}' with {len(current_categories)} categories")
        
        total_categories = sum(len(cats) for cats in discovered_splits.values())
        logger.info(f"Discovered {len(discovered_splits)} split types with {total_categories} total categories across all tables")
        return discovered_splits
    
    def _normalize_split_type(self, split_type: str) -> str:
        """
        Normalize split type text to a consistent format
        
        Args:
            split_type: Raw split type text
            
        Returns:
            Normalized split type
        """
        # Clean up the text
        normalized = split_type.lower().strip()
        
        # Remove common artifacts
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', '_', normalized)
        
        return normalized
    
    def find_table_id_for_split(self, soup: BeautifulSoup, split_type: str, category: str) -> Optional[str]:
        """
        Find table ID for a specific split type and category
        
        Args:
            soup: BeautifulSoup object
            split_type: Split type
            category: Split category
            
        Returns:
            Table ID or None if not found
        """
        # For PFR splits pages, we work with all splits tables
        # Find all tables that could contain the category
        tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                if len(rows) > 5:  # This is likely a splits table
                    # Check if this table contains the category
                    if self._table_contains_category(table, category):
                        table_id = table.get('id', f'splits_table_{table_idx}')
                        logger.debug(f"Found table {table_id} (index {table_idx}) containing category {category}")
                        return table_id
        
        logger.debug(f"Category '{category}' not found in any table")
        return None
    
    def _table_contains_category(self, table, category: str) -> bool:
        """
        Check if a table contains a specific category
        
        Args:
            table: Table HTML element
            category: Category to look for
            
        Returns:
            True if table contains the category
        """
        tbody = table.find('tbody')
        if not tbody:
            return False
        
        category_lower = category.lower()
        
        for row in tbody.find_all('tr'):
            if row.get('class') and 'thead' in row.get('class'):
                continue
            
            first_cell = row.find(['td', 'th'])
            if first_cell:
                cell_text = first_cell.get_text(strip=True).lower()
                
                # Check for exact match or partial match
                if category_lower in cell_text or cell_text in category_lower:
                    return True
        
        return False
    
    def process_splits_table(self, df: pd.DataFrame, pfr_id: str, player_name: str,
                           team: str, season: int, split_type: str, split_category: str,
                           scraped_at: datetime, split_value_col: str) -> List[QBSplitStats]:
        """
        Process individual splits table data
        """
        splits = []
        
        # For PFR splits tables, the split values are in the first column (empty header)
        # The split_value_col parameter is the original section name, but we need to use the first column
        if len(df.columns) == 0:
            logger.debug(f"No columns found in DataFrame for {split_type}/{split_category}")
            return splits
        
        # Use the first column for split values (it has an empty header)
        split_value_column = df.columns[0]
        logger.debug(f"Using first column '{split_value_column}' for split values")
        
        # Find rows where the first column matches our split category
        matching_rows = df[df[split_value_column] == split_category]
        if matching_rows.empty:
            logger.debug(f"No matching row found for split category '{split_category}' in column '{split_value_column}'")
            logger.debug(f"Available values in first column: {df[split_value_column].unique()}")
            return splits
        
        logger.debug(f"Found {len(matching_rows)} matching rows for split category '{split_category}'")
        
        for _, row in matching_rows.iterrows():
            try:
                # Extract stats from the row using the correct column names
                # The DataFrame columns are: ['Split', 'Value', 'G', 'W', 'L', 'T', 'Cmp', 'Att', 'Inc', 'Cmp%', 'Yds', 'TD', 'Int', 'Rate', 'Sk', 'Yds', 'Y/A', 'AY/A', 'A/G', 'Y/G', 'Att', 'Yds', 'Y/A', 'TD', 'A/G', 'Y/G', 'TD', 'Pts', 'Fmb', 'FL', 'FF', 'FR', 'Yds', 'TD']
                
                # Get the raw data from each column using proper pandas Series indexing
                # Convert Series to scalar values to avoid ambiguous truth value errors
                games_data = str(row['G'].iloc[0]) if 'G' in row.index and len(row['G']) > 0 else ''  # Games played
                completions_data = str(row['Cmp'].iloc[0]) if 'Cmp' in row.index and len(row['Cmp']) > 0 else ''  # Completions
                attempts_data = str(row['Att'].iloc[0]) if 'Att' in row.index and len(row['Att']) > 0 else ''  # Attempts
                completion_pct_data = str(row['Cmp%'].iloc[0]) if 'Cmp%' in row.index and len(row['Cmp%']) > 0 else ''  # Completion percentage
                pass_yards_data = str(row['Yds'].iloc[0]) if 'Yds' in row.index and len(row['Yds']) > 0 else ''  # Passing yards
                pass_tds_data = str(row['TD'].iloc[0]) if 'TD' in row.index and len(row['TD']) > 0 else ''  # Passing touchdowns
                interceptions_data = str(row['Int'].iloc[0]) if 'Int' in row.index and len(row['Int']) > 0 else ''  # Interceptions
                rating_data = str(row['Rate'].iloc[0]) if 'Rate' in row.index and len(row['Rate']) > 0 else ''  # Passer rating
                sacks_data = str(row['Sk'].iloc[0]) if 'Sk' in row.index and len(row['Sk']) > 0 else ''  # Sacks
                sack_yards_data = str(row['Yds'].iloc[0]) if 'Yds' in row.index and len(row['Yds']) > 0 else ''  # Sack yards (second 'Yds' column)
                
                # Additional fields from the extended schema
                incompletions_data = str(row['Inc'].iloc[0]) if 'Inc' in row.index and len(row['Inc']) > 0 else ''  # Incompletions
                wins_data = str(row['W'].iloc[0]) if 'W' in row.index and len(row['W']) > 0 else ''  # Wins
                losses_data = str(row['L'].iloc[0]) if 'L' in row.index and len(row['L']) > 0 else ''  # Losses
                ties_data = str(row['T'].iloc[0]) if 'T' in row.index and len(row['T']) > 0 else ''  # Ties
                attempts_per_game_data = str(row['A/G'].iloc[0]) if 'A/G' in row.index and len(row['A/G']) > 0 else ''  # Attempts per game
                yards_per_game_data = str(row['Y/G'].iloc[0]) if 'Y/G' in row.index and len(row['Y/G']) > 0 else ''  # Yards per game
                points_data = str(row['Pts'].iloc[0]) if 'Pts' in row.index and len(row['Pts']) > 0 else ''  # Points
                
                # Rush statistics - need to handle duplicate column names properly
                # The DataFrame has duplicate column names, so we need to access by position
                rush_attempts_data = ''
                rush_yards_data = ''
                rush_tds_data = ''
                rush_attempts_per_game_data = ''
                rush_yards_per_game_data = ''
                
                # Get column positions for rush stats (they appear after passing stats)
                if len(row.index) > 15:  # If we have enough columns for rush stats
                    # Find the second occurrence of 'Att', 'Yds', 'TD', 'A/G', 'Y/G' for rush stats
                    att_columns = [i for i, col in enumerate(row.index) if col == 'Att']
                    yds_columns = [i for i, col in enumerate(row.index) if col == 'Yds']
                    td_columns = [i for i, col in enumerate(row.index) if col == 'TD']
                    ag_columns = [i for i, col in enumerate(row.index) if col == 'A/G']
                    yg_columns = [i for i, col in enumerate(row.index) if col == 'Y/G']
                    
                    if len(att_columns) > 1:
                        rush_attempts_data = str(row.iloc[att_columns[1]]) if att_columns[1] < len(row) else ''
                    if len(yds_columns) > 1:
                        rush_yards_data = str(row.iloc[yds_columns[1]]) if yds_columns[1] < len(row) else ''
                    if len(td_columns) > 1:
                        rush_tds_data = str(row.iloc[td_columns[1]]) if td_columns[1] < len(row) else ''
                    if len(ag_columns) > 1:
                        rush_attempts_per_game_data = str(row.iloc[ag_columns[1]]) if ag_columns[1] < len(row) else ''
                    if len(yg_columns) > 1:
                        rush_yards_per_game_data = str(row.iloc[yg_columns[1]]) if yg_columns[1] < len(row) else ''
                
                # Fumble statistics
                fumbles_data = str(row['Fmb'].iloc[0]) if 'Fmb' in row.index and len(row['Fmb']) > 0 else ''  # Fumbles
                fumbles_lost_data = str(row['FL'].iloc[0]) if 'FL' in row.index and len(row['FL']) > 0 else ''  # Fumbles lost
                fumbles_forced_data = str(row['FF'].iloc[0]) if 'FF' in row.index and len(row['FF']) > 0 else ''  # Fumbles forced
                fumbles_recovered_data = str(row['FR'].iloc[0]) if 'FR' in row.index and len(row['FR']) > 0 else ''  # Fumbles recovered
                
                # Fumble recovery stats - need to handle duplicate column names
                fumble_recovery_yards_data = ''
                fumble_recovery_tds_data = ''
                
                if len(row.index) > 25:  # If we have enough columns for fumble recovery stats
                    # Find the third occurrence of 'Yds' and 'TD' for fumble recovery stats
                    yds_columns = [i for i, col in enumerate(row.index) if col == 'Yds']
                    td_columns = [i for i, col in enumerate(row.index) if col == 'TD']
                    
                    if len(yds_columns) > 2:
                        fumble_recovery_yards_data = str(row.iloc[yds_columns[2]]) if yds_columns[2] < len(row) else ''
                    if len(td_columns) > 2:
                        fumble_recovery_tds_data = str(row.iloc[td_columns[2]]) if td_columns[2] < len(row) else ''
                
                # Calculate total touchdowns
                total_tds = (safe_int(pass_tds_data) or 0) + (safe_int(rush_tds_data) or 0) + (safe_int(fumble_recovery_tds_data) or 0)
                
                logger.debug(f"Raw data for {split_category}: Games={games_data}, Cmp={completions_data}, Att={attempts_data}, Yds={pass_yards_data}")
                
                # Create split stats object with extracted data
                split_stats = QBSplitStats(
                    pfr_id=pfr_id,
                    player_name=player_name,
                    team=team,
                    season=season,
                    split_type=split_type,
                    split_category=split_category,
                    games=safe_int(games_data) if pd.notna(games_data) and games_data != '' else 0,
                    completions=safe_int(completions_data) if pd.notna(completions_data) and completions_data != '' else 0,
                    attempts=safe_int(attempts_data) if pd.notna(attempts_data) and attempts_data != '' else 0,
                    completion_pct=safe_percentage(completion_pct_data) if pd.notna(completion_pct_data) and completion_pct_data != '' else 0.0,
                    pass_yards=safe_int(pass_yards_data) if pd.notna(pass_yards_data) and pass_yards_data != '' else 0,
                    pass_tds=safe_int(pass_tds_data) if pd.notna(pass_tds_data) and pass_tds_data != '' else 0,
                    interceptions=safe_int(interceptions_data) if pd.notna(interceptions_data) and interceptions_data != '' else 0,
                    rating=safe_float(rating_data) if pd.notna(rating_data) and rating_data != '' else 0.0,
                    sacks=safe_int(sacks_data) if pd.notna(sacks_data) and sacks_data != '' else 0,
                    sack_yards=safe_int(sack_yards_data) if pd.notna(sack_yards_data) and sack_yards_data != '' else 0,
                    net_yards_per_attempt=safe_float(str(row['Y/A'].iloc[0])) if 'Y/A' in row.index and len(row['Y/A']) > 0 else 0.0,
                    scraped_at=scraped_at,
                    # Additional fields
                    rush_attempts=safe_int(rush_attempts_data) if pd.notna(rush_attempts_data) and rush_attempts_data != '' else 0,
                    rush_yards=safe_int(rush_yards_data) if pd.notna(rush_yards_data) and rush_yards_data != '' else 0,
                    rush_tds=safe_int(rush_tds_data) if pd.notna(rush_tds_data) and rush_tds_data != '' else 0,
                    fumbles=safe_int(fumbles_data) if pd.notna(fumbles_data) and fumbles_data != '' else 0,
                    fumbles_lost=safe_int(fumbles_lost_data) if pd.notna(fumbles_lost_data) and fumbles_lost_data != '' else 0,
                    fumbles_forced=safe_int(fumbles_forced_data) if pd.notna(fumbles_forced_data) and fumbles_forced_data != '' else 0,
                    fumbles_recovered=safe_int(fumbles_recovered_data) if pd.notna(fumbles_recovered_data) and fumbles_recovered_data != '' else 0,
                    fumble_recovery_yards=safe_int(fumble_recovery_yards_data) if pd.notna(fumble_recovery_yards_data) and fumble_recovery_yards_data != '' else 0,
                    fumble_recovery_tds=safe_int(fumble_recovery_tds_data) if pd.notna(fumble_recovery_tds_data) and fumble_recovery_tds_data != '' else 0,
                    incompletions=safe_int(incompletions_data) if pd.notna(incompletions_data) and incompletions_data != '' else 0,
                    wins=safe_int(wins_data) if pd.notna(wins_data) and wins_data != '' else 0,
                    losses=safe_int(losses_data) if pd.notna(losses_data) and losses_data != '' else 0,
                    ties=safe_int(ties_data) if pd.notna(ties_data) and ties_data != '' else 0,
                    attempts_per_game=safe_float(attempts_per_game_data) if pd.notna(attempts_per_game_data) and attempts_per_game_data != '' else None,
                    yards_per_game=safe_float(yards_per_game_data) if pd.notna(yards_per_game_data) and yards_per_game_data != '' else None,
                    rush_attempts_per_game=safe_float(rush_attempts_per_game_data) if pd.notna(rush_attempts_per_game_data) and rush_attempts_per_game_data != '' else None,
                    rush_yards_per_game=safe_float(rush_yards_per_game_data) if pd.notna(rush_yards_per_game_data) and rush_yards_per_game_data != '' else None,
                    total_tds=total_tds,
                    points=safe_int(points_data) if pd.notna(points_data) and points_data != '' else 0
                )
                
                errors = split_stats.validate()
                if errors:
                    for error in errors:
                        self.metrics.add_warning(f"Validation error for {player_name} {split_type}/{split_category}: {error}")
                
                splits.append(split_stats)
                logger.debug(f"Processed split: {split_type}/{split_category} for {player_name}")
                
            except Exception as e:
                self.metrics.add_error(f"Error processing split row: {e}")
                continue
        
        return splits
    
    def process_players_concurrently(self, qb_stats: List[QBBasicStats], max_workers: int = None) -> List[QBSplitStats]:
        """
        Process multiple players concurrently while respecting rate limits
        
        Args:
            qb_stats: List of QBStats objects
            max_workers: Maximum number of worker threads
            
        Returns:
            List of QBSplitStats objects
        """
        max_workers = max_workers or config.scraping.max_workers
        all_splits = []
        current_time = datetime.now()
        
        logger.info(f"Processing {len(qb_stats)} players with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks
            future_to_player = {}
            for qb_stat in qb_stats:
                player_url = self.find_player_url(qb_stat.player_name)
                if player_url:
                    future = executor.submit(
                        self.scrape_player_splits,
                        player_url,
                        qb_stat.pfr_id,
                        qb_stat.player_name,
                        qb_stat.team,
                        qb_stat.season,
                        current_time
                    )
                    future_to_player[future] = qb_stat.player_name
            
            # Collect results
            for future in as_completed(future_to_player):
                player_name = future_to_player[future]
                try:
                    player_splits = future.result()
                    all_splits.extend(player_splits)
                    logger.info(f"Completed splits for {player_name}: {len(player_splits)} records")
                except Exception as e:
                    self.metrics.add_error(f"Error processing {player_name}: {e}")
        
        logger.info(f"Successfully scraped {len(all_splits)} total split records")
        return all_splits
    
    def get_scraping_metrics(self) -> ScrapingMetrics:
        """Get current scraping metrics"""
        return self.metrics
    
    def reset_metrics(self):
        """Reset scraping metrics"""
        self.metrics = ScrapingMetrics()
        self.metrics.start_time = datetime.now()
    
    def create_scraping_log(self, season: int) -> ScrapingLog:
        """
        Create scraping log entry
        
        Args:
            season: Season year
            
        Returns:
            ScrapingLog object
        """
        end_time = datetime.now()
        processing_time = calculate_processing_time(self.metrics.start_time, end_time)
        
        return ScrapingLog(
            session_id=generate_session_id(),
            season=season,
            start_time=self.metrics.start_time,
            end_time=end_time,
            total_requests=self.metrics.total_requests,
            successful_requests=self.metrics.successful_requests,
            failed_requests=self.metrics.failed_requests,
            total_qb_stats=0,  # Will be set by caller
            total_qb_splits=0,  # Will be set by caller
            errors=self.metrics.errors,
            warnings=self.metrics.warnings,
            rate_limit_violations=self.metrics.rate_limit_violations,
            processing_time_seconds=processing_time
        )
    
    def discover_splits_from_page_url(self, url: str) -> Dict[str, List[str]]:
        """
        Discover splits from a splits page URL
        
        Args:
            url: URL of the splits page
            
        Returns:
            Dictionary mapping split types to their categories
        """
        response = self.make_request_with_retry(url)
        if not response:
            return {}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        return self.discover_splits_from_page(soup) 