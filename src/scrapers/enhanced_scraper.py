#!/usr/bin/env python3
"""
Enhanced PFR Scraper for NFL QB Data
Comprehensive scraper with integrated splits extraction and advanced features
"""

import logging
import time
import random
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from urllib.parse import urljoin
import re

from bs4 import BeautifulSoup
import pandas as pd
import requests

from src.models.qb_models import (
    QBBasicStats, QBSplitsType1, QBSplitsType2, QBPassingStats,
    Player, Team, ScrapingLog, QBSplitStats
)
from src.utils.data_utils import (
    safe_int, safe_float, safe_percentage, clean_player_name,
    extract_pfr_id, build_splits_url, generate_session_id,
    calculate_processing_time, normalize_pfr_team_code
)
from src.config.config import config, SplitTypes, SplitCategories
from src.core.selenium_manager import SeleniumManager, SeleniumConfig
from src.core.splits_manager import SplitsManager

logger = logging.getLogger(__name__)


@dataclass
class ScrapingMetrics:
    """Metrics tracking for scraping operations"""
    start_time: datetime
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rate_limit_violations: int = 0
    
    def add_error(self, error: str):
        """Add error to metrics"""
        self.errors.append(error)
        self.failed_requests += 1
    
    def add_warning(self, warning: str):
        """Add warning to metrics"""
        self.warnings.append(warning)


class EnhancedPFRScraper:
    """Enhanced Pro Football Reference scraper with automatic split discovery"""
    
    def __init__(self, rate_limit_delay: float = None, splits_manager: Optional['SplitsManager'] = None):
        self.base_url = "https://www.pro-football-reference.com"
        self.rate_limit_delay = rate_limit_delay or config.get_rate_limit_delay()
        
        # Use the Selenium manager for all HTTP requests
        selenium_config = SeleniumConfig(
            headless=True,
            human_behavior_delay=(self.rate_limit_delay, self.rate_limit_delay + 3.0)
        )
        self.selenium_manager = SeleniumManager(selenium_config)
        
        # Use injected SplitsManager if provided, otherwise create default one
        if splits_manager is not None:
            self.splits_manager = splits_manager
            logger.info("Using injected SplitsManager in EnhancedPFRScraper")
        else:
            # Initialize the dedicated SplitsManager with the Selenium manager
            self.splits_manager = SplitsManager(self.selenium_manager)
            logger.info("Created new SplitsManager in EnhancedPFRScraper")
        
        # Metrics tracking
        self.metrics = ScrapingMetrics(start_time=datetime.now())
        
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
        
        logger.info(f"Initialized EnhancedPFRScraper with rate limit delay: {self.rate_limit_delay}s")
    
    def make_request_with_retry(self, url: str, max_retries: int = None) -> Optional[str]:
        """
        Make HTTP request with retry logic and rate limiting using Selenium
        
        Args:
            url: URL to request
            max_retries: Maximum number of retries (defaults to config value)
            
        Returns:
            Page source HTML or None if request failed
        """
        max_retries = max_retries or config.scraping.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                self.metrics.total_requests += 1
                
                # Use the Selenium manager for consistent rate limiting
                result = self.selenium_manager.get_page(url, enable_js=False)
                
                if result['success']:
                    self.metrics.successful_requests += 1
                    return result['content']
                else:
                    self.metrics.add_error(f"Failed to load page for {url}: {result['error']}")
                    
            except Exception as e:
                self.metrics.add_error(f"Request failed for {url}: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries:
                wait_time = (2 ** attempt) * self.rate_limit_delay
                logger.debug(f"Retrying {url} in {wait_time:.2f}s (attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(wait_time)
        
        return None
    
    def parse_simple_table(self, soup: BeautifulSoup, table_id: str) -> Optional[pd.DataFrame]:
        """
        Parse a simple HTML table (like main passing stats) to DataFrame
        
        Args:
            soup: BeautifulSoup object
            table_id: ID of the table to parse
            
        Returns:
            DataFrame with table data or None if parsing failed
        """
        try:
            # Find the table by ID
            table = soup.find('table', {'id': table_id})
            if not table or not isinstance(table, Tag):
                logger.error(f"Table with ID '{table_id}' not found")
                return None
            
            # Extract headers
            headers = []
            header_row = table.find('thead')
            if header_row and isinstance(header_row, Tag):
                # Get headers from thead
                th_elements = header_row.find_all('th')
                headers = [th.get_text(strip=True) for th in th_elements]
            else:
                # Try to get headers from first row
                first_row = table.find('tr')
                if first_row and isinstance(first_row, Tag):
                    th_elements = first_row.find_all('th')
                    headers = [th.get_text(strip=True) for th in th_elements]
            
            if not headers:
                logger.error("No headers found in table")
                return None
            
            logger.debug(f"Found headers: {headers}")
            
            # Extract data rows
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
            else:
                # Skip first row if it contains headers
                all_rows = table.find_all('tr')
                rows = all_rows[1:] if all_rows and all_rows[0].find('th') else all_rows
            
            data = []
            for row in rows:
                # Skip header rows within tbody
                if row.find('th') and row.get('class') and 'thead' in row.get('class'):
                    continue
                
                cells = row.find_all(['td', 'th'])
                if len(cells) >= len(headers):
                    row_data = [cell.get_text(strip=True) for cell in cells[:len(headers)]]
                    data.append(row_data)
            
            if not data:
                logger.warning("No data rows found in table")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=headers)
            logger.debug(f"Successfully parsed simple table '{table_id}' with {len(df)} rows and {len(df.columns)} columns")
            
            return df
            
        except Exception as e:
            logger.error(f"Error parsing simple table data: {e}")
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
        
        page_source = self.make_request_with_retry(player_url)
        if not page_source:
            return {}
        
        soup = BeautifulSoup(page_source, 'html.parser')
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
    
    def get_qb_main_stats(self, season: int, player_names: Optional[List[str]] = None) -> Tuple[List[Player], List[QBBasicStats]]:
        """
        Scrape main QB statistics for a given season, with an option to filter for specific players.
        
        Args:
            season: Season year
            player_names: Optional list of player names to filter for
            
        Returns:
            A tuple containing a list of Player objects and a list of QBBasicStats objects.
        """
        url = f"{self.base_url}/years/{season}/passing.htm"
        logger.info(f"Scraping QB main stats for {season} season")
        
        # Set realistic referer to simulate coming from search engines or Reddit
        realistic_referers = [
            "https://www.google.com/",
            "https://www.google.com/search?q=patrick+mahomes+stats+2024+pro+football+reference",
            "https://www.google.com/search?q=nfl+quarterback+passing+stats+2024+pro+football+reference",
            "https://duckduckgo.com/?q=pro+football+reference+nfl+stats+2024",
            "https://www.reddit.com/r/nfl/comments/",
            "https://www.reddit.com/r/fantasyfootball/comments/",
            "https://www.reddit.com/r/nfl/comments/2024+quarterback+stats+pro+football+reference",
            "https://www.bing.com/search?q=pro+football+reference+quarterback+stats+2024"
        ]
        # Selenium manager handles referer automatically
        
        page_source = self.make_request_with_retry(url)
        if not page_source:
            return [], []
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        player_rows = defaultdict(list)
        
        table = soup.find('table', {'id': 'passing'})
        if not table or not table.find('tbody'):
            logger.error(f"Could not find passing table or its body for {season}")
            return [], []
            
        for i, row in enumerate(table.find('tbody').find_all('tr')):
            logger.info(f"Processing row {i}")
            if 'thead' in row.get('class', []):
                logger.info(f"Row {i} is a header, skipping.")
                continue

            name_cell = row.find('td', {'data-stat': 'name_display'})
            if not name_cell:
                logger.warning(f"Row {i}: Could not find name cell with data-stat='name_display'.")
                continue

            player_name_anchor = name_cell.find('a')
            if not player_name_anchor:
                logger.warning(f"Row {i}: Could not find player name anchor tag.")
                continue

            player_name = clean_player_name(player_name_anchor.get_text(strip=True))
            logger.info(f"Row {i}: Found player name: {player_name}")
            
            # Filter for specific players if requested
            if player_names:
                logger.info(f"Row {i}: Checking if '{player_name}' is in requested list: {player_names}")
                if player_name.lower() not in [name.lower() for name in player_names]:
                    logger.info(f"Row {i}: '{player_name}' not in list, skipping.")
                    continue
            
            logger.info(f"Row {i}: Player '{player_name}' is in requested list, proceeding.")
            
            # Ensure the row is for a QB
            pos_cell = row.find('td', {'data-stat': 'pos'})
            if not pos_cell or pos_cell.get_text(strip=True).upper() != 'QB':
                continue
                
            player_url = urljoin(self.base_url, player_name_anchor['href'])
            pfr_id = extract_pfr_id(player_url)

            if not pfr_id:
                logger.warning(f"Could not extract PFR ID for {player_name}, skipping row.")
                continue

            team_cell = row.find('td', {'data-stat': 'team_name_abbr'})
            team_code = normalize_pfr_team_code(team_cell.get_text(strip=True)) if team_cell else ''

            is_total = team_code in {'2TM', '3TM', '4TM'}
            
            player_rows[pfr_id].append({
                'row_data': row, 
                'team_code': team_code, 
                'is_total': is_total, 
                'player_name': player_name, 
                'player_url': player_url
            })
        
        players_list = []
        basic_stats_list = []
        current_time = datetime.now()
        
        for pfr_id, rows in player_rows.items():
            try:
                if len(rows) > 1: # Multi-team player
                    total_row_data = next((r for r in rows if r['is_total']), None)
                    
                    if not total_row_data:
                        logger.warning(f"Multi-team player {rows[0]['player_name']} missing total row. Using last entry as stat source.")
                        total_row_data = rows[-1]

                    # Collect team codes from non-total rows
                    teams = {r['team_code'] for r in rows if not r['is_total'] and r['team_code']}
                    
                    if not teams:
                        logger.warning(f"Could not determine individual teams for multi-team player {total_row_data['player_name']}. Skipping this player.")
                        continue # Skip this player if we can't figure out their teams

                    team_str = ','.join(sorted(list(teams)))
                    stat_source_row = total_row_data['row_data']
                    player_name = total_row_data['player_name']
                    player_url = total_row_data['player_url']
                else: # Single-team player
                    stat_source_row = rows[0]['row_data']
                    team_str = rows[0]['team_code']
                    player_name = rows[0]['player_name']
                    player_url = rows[0]['player_url']
                
                if not team_str:
                    logger.warning(f"Player {player_name} has no team associated. Skipping.")
                    continue

                player = Player(pfr_id=pfr_id, player_name=player_name, pfr_url=player_url or '', created_at=current_time, updated_at=current_time)
                
                stats = self._extract_stats_from_row(stat_source_row)
                stats['team'] = team_str

                basic_stats = QBBasicStats(pfr_id=pfr_id, player_name=player_name, player_url=player_url, season=season, **stats)
                basic_stats.scraped_at = current_time
                basic_stats.updated_at = current_time

                players_list.append(player)
                basic_stats_list.append(basic_stats)
                
            except Exception as e:
                self.metrics.add_error(f"Error processing stats for PFR ID {pfr_id}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(players_list)} QB players with basic stats for {season}")
        return players_list, basic_stats_list
    
    def _extract_stats_from_row(self, row: Any) -> Dict[str, Any]:
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
            'succ_pct': safe_percentage(get_stat('pass_succ_pct')),
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
    
    def scrape_all_qb_data(self, season: int, use_concurrent_splits: bool = False) -> Tuple[List[QBBasicStats], List[QBSplitsType1], List[QBSplitsType2]]:
        """
        Scrape all QB data including passing stats and splits
        
        Args:
            season: Season year
            use_concurrent_splits: Whether to use concurrent processing for splits
            
        Returns:
            Tuple of (passing_stats, basic_splits, advanced_splits)
        """
        logger.info(f"Starting comprehensive QB data scraping for {season} season")
        
        # Scrape basic passing stats
        players, passing_stats = self.get_qb_main_stats(season)
        if not passing_stats:
            logger.error("Failed to scrape basic passing stats")
            return [], [], []
        
        logger.info(f"Successfully scraped {len(passing_stats)} QB passing stats")
        
        # Use the dedicated SplitsManager for comprehensive splits extraction
        basic_splits, advanced_splits = self.splits_manager.extract_all_player_splits(
            passing_stats, use_concurrent=use_concurrent_splits
        )
        
        # Log comprehensive results
        logger.info(f"Comprehensive QB data scraping completed:")
        logger.info(f"  - Passing stats: {len(passing_stats)}")
        logger.info(f"  - Basic splits: {len(basic_splits)}")
        logger.info(f"  - Advanced splits: {len(advanced_splits)}")
        
        # Log splits manager summary
        self.splits_manager.log_extraction_summary()
        
        return passing_stats, basic_splits, advanced_splits
    
    def scrape_player_splits(self, player_url: str, pfr_id: str, player_name: str,
                             team: str, season: int, scraped_at: datetime) -> Tuple[List[QBSplitStats], List[QBSplitsType2]]:
        """Scrape all basic **and** advanced splits for a specific player.

        Returns a tuple ``(basic_splits, advanced_splits)`` so the caller can
        insert each set into its respective table.
        """
        # Use the dedicated SplitsManager for individual player splits
        result = self.splits_manager.extract_player_splits_by_name(player_name, pfr_id, season)
        
        # Convert to legacy format for backwards compatibility
        basic_splits = []
        for split in result.basic_splits:
            # Convert QBSplitsType1 to legacy format
            basic_splits.append(type('obj', (object,), {
                'pfr_id': split.pfr_id,
                'player_name': split.player_name,
                'season': split.season,
                'split': split.split,
                'value': split.value,
                'g': split.g,
                'w': split.w,
                'l': split.l,
                't': split.t,
                'cmp': split.cmp,
                'att': split.att,
                'inc': split.inc,
                'cmp_pct': split.cmp_pct,
                'yds': split.yds,
                'td': split.td,
                'int': split.int,
                'rate': split.rate,
                'sk': split.sk,
                'sk_yds': split.sk_yds,
                'y_a': split.y_a,
                'ay_a': split.ay_a,
                'a_g': split.a_g,
                'y_g': split.y_g,
                'rush_att': split.rush_att,
                'rush_yds': split.rush_yds,
                'rush_y_a': split.rush_y_a,
                'rush_td': split.rush_td,
                'rush_a_g': split.rush_a_g,
                'rush_y_g': split.rush_y_g,
                'total_td': split.total_td,
                'pts': split.pts,
                'fmb': split.fmb,
                'fl': split.fl,
                'ff': split.ff,
                'fr': split.fr,
                'fr_yds': split.fr_yds,
                'fr_td': split.fr_td,
                'scraped_at': split.scraped_at
            })())
        
        return basic_splits, result.advanced_splits

    # ------------------------------------------------------------------
    # Advanced-splits helpers
    # ------------------------------------------------------------------

    def _extract_split_info(self, row) -> Optional[Dict[str, str]]:
        """Extract ``split`` and ``value`` labels from a row (helper copied from RawDataScraper)."""
        split_id_cell = row.find('td', {'data-stat': 'split_id'})
        split_value_cell = row.find('td', {'data-stat': 'split_value'})

        if split_id_cell and split_value_cell:
            return {
                'split': split_id_cell.get_text(strip=True),
                'value': split_value_cell.get_text(strip=True),
            }

        # Fallback – use first two <td> cells
        cells = row.find_all('td')
        if len(cells) >= 2:
            return {
                'split': cells[0].get_text(strip=True),
                'value': cells[1].get_text(strip=True),
            }

        return None

    def _extract_advanced_stats_from_row(self, row) -> Dict[str, Any]:
        """Extract stats for ``QBSplitsType2`` from an <tr> element.

        Mirrors the mapping logic from ``RawDataScraper`` so we maintain a
        single source of truth for CSV-to-DB column names.
        """
        stat_mapping = {
            'pass_cmp': 'cmp',
            'pass_att': 'att',
            'pass_inc': 'inc',
            'pass_cmp_pct': 'cmp_pct',
            'pass_yds': 'yds',
            'pass_td': 'td',
            'pass_first_down': 'first_downs',
            'pass_int': 'int',
            'pass_rating': 'rate',
            'pass_sacked': 'sk',
            'pass_sacked_yds': 'sk_yds',
            'pass_yds_per_att': 'y_a',
            'pass_adj_yds_per_att': 'ay_a',
            'rush_att': 'rush_att',
            'rush_yds': 'rush_yds',
            'rush_yds_per_att': 'rush_y_a',
            'rush_td': 'rush_td',
            'rush_first_down': 'rush_first_downs',
        }

        stats: Dict[str, Any] = {}
        for data_stat, csv_col in stat_mapping.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell is None:
                continue
            value = cell.get_text(strip=True)

            if csv_col in {
                'cmp',
                'att',
                'inc',
                'yds',
                'td',
                'first_downs',
                'int',
                'sk',
                'sk_yds',
                'rush_att',
                'rush_yds',
                'rush_td',
                'rush_first_downs',
            }:
                stats[csv_col] = safe_int(value) if value else None
            elif csv_col in {'cmp_pct', 'rate', 'y_a', 'ay_a', 'rush_y_a'}:
                stats[csv_col] = safe_float(value) if value else None
            else:
                stats[csv_col] = value if value else None

        return stats

    def _extract_advanced_splits(
        self,
        soup: BeautifulSoup,
        pfr_id: str,
        player_name: str,
        season: int,
        scraped_at: datetime,
    ) -> List[QBSplitsType2]:
        """Parse the ``advanced_splits`` table into ``QBSplitsType2`` objects."""

        splits_adv: List[QBSplitsType2] = []
        table = soup.find('table', {'id': 'advanced_splits'})
        if not table:
            logger.debug(f"Advanced splits table not found for {player_name}")
            return splits_adv

        tbody = table.find('tbody')
        if not tbody:
            return splits_adv

        for row in tbody.find_all('tr'):
            # Skip header rows
            if 'thead' in row.get('class', []):
                continue

            split_info = self._extract_split_info(row)
            if not split_info:
                continue

            stats_data = self._extract_advanced_stats_from_row(row)

            split_obj = QBSplitsType2(
                pfr_id=pfr_id,
                player_name=player_name,
                season=season,
                split=split_info['split'],
                value=split_info['value'],
                scraped_at=scraped_at,
                **stats_data,
            )

            splits_adv.append(split_obj)

        logger.debug(f"Extracted {len(splits_adv)} advanced split rows for {player_name}")
        return splits_adv
    
    def discover_splits_from_page(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """
        Discover splits from a splits page by analyzing the actual PFR structure.
        PFR splits pages have multiple tables, each containing different split categories.
        We need to identify the split type based on the content and structure of each table.
        """
        discovered_splits = {}
        tables = soup.find_all('table')
        logger.debug(f"Found {len(tables)} tables on the page")
        
        # Common split categories and their expected values
        split_patterns = {
            'place': ['Home', 'Away'],
            'result': ['Win', 'Loss', 'Tie'],
            'quarter': ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter', 'Overtime'],
            'score_differential': ['Leading', 'Tied', 'Trailing'],
            'time': ['1st Half', '2nd Half'],
            'opponent': ['vs. AFC', 'vs. NFC', 'vs. Division', 'vs. Conference'],
            'game_situation': ['Close and Late', 'Late and Close'],
            'down': ['1st Down', '2nd Down', '3rd Down', '4th Down'],
            'yards_to_go': ['1-3 Yards', '4-6 Yards', '7-9 Yards', '10+ Yards'],
            'field_position': ['Own 1-10', 'Own 11-20', 'Own 21-50', 'Opp 49-20', 'Opp 19-1', 'Red Zone'],
            'snap_type': ['Huddle', 'No Huddle', 'Shotgun', 'Under Center'],
            'play_action': ['Play Action', 'Non-Play Action'],
            'run_pass_option': ['RPO', 'Non-RPO'],
            'time_in_pocket': ['2.5+ Seconds', 'Under 2.5 Seconds']
        }
        
        # Process each table
        for table_idx, table in enumerate(tables):
            tbody = table.find('tbody')
            if not tbody:
                continue
                
            rows = tbody.find_all('tr')
            if len(rows) < 3:  # Skip tables with too few rows
                continue
                
            logger.debug(f"Analyzing table {table_idx} with {len(rows)} rows")
            
            # Extract all potential split values from the first column
            split_values = []
            for row in rows:
                # Skip header rows
                if row.get('class') and 'thead' in row.get('class'):
                    continue
                    
                first_cell = row.find('td')
                if first_cell:
                    value = first_cell.get_text(strip=True)
                    if value and value not in split_values:
                        split_values.append(value)
            
            logger.debug(f"Table {table_idx} split values: {split_values}")
            
            # Try to identify the split type based on the values found
            identified_split_type = None
            best_match_score = 0
            
            for split_type, expected_values in split_patterns.items():
                # Calculate how many expected values match what we found
                matches = sum(1 for expected in expected_values 
                            for found in split_values 
                            if expected.lower() in found.lower() or found.lower() in expected.lower())
                
                if matches > 0:
                    match_score = matches / len(expected_values)
                    if match_score > best_match_score:
                        best_match_score = match_score
                        identified_split_type = split_type
            
            # If we found a good match, add it to discovered splits
            if identified_split_type and best_match_score >= 0.3:  # At least 30% match
                if identified_split_type not in discovered_splits:
                    discovered_splits[identified_split_type] = {}
                
                # Add all found values as categories
                for value in split_values:
                    if value:  # Skip empty values
                        discovered_splits[identified_split_type][value] = identified_split_type
                
                logger.debug(f"Table {table_idx}: Identified as '{identified_split_type}' with {len(split_values)} categories (match score: {best_match_score:.2f})")
            else:
                # If we can't identify the split type, use a generic approach
                # Look for common patterns in the values
                if split_values:
                    # Try to infer split type from the values themselves
                    inferred_type = self._infer_split_type_from_values(split_values)
                    if inferred_type:
                        if inferred_type not in discovered_splits:
                            discovered_splits[inferred_type] = {}
                        for value in split_values:
                            if value:
                                discovered_splits[inferred_type][value] = inferred_type
                        logger.debug(f"Table {table_idx}: Inferred type '{inferred_type}' with {len(split_values)} categories")
                    else:
                        # Fallback: use "other" but with the actual values
                        if 'other' not in discovered_splits:
                            discovered_splits['other'] = {}
                        for value in split_values:
                            if value:
                                discovered_splits['other'][value] = 'other'
                        logger.debug(f"Table {table_idx}: Using 'other' type with {len(split_values)} categories")
        
        total_categories = sum(len(cats) for cats in discovered_splits.values())
        logger.info(f"Discovered {len(discovered_splits)} split types with {total_categories} total categories")
        return discovered_splits
    
    def _infer_split_type_from_values(self, values: List[str]) -> Optional[str]:
        """
        Infer split type from the actual values found in the table
        
        Args:
            values: List of split values found in the table
            
        Returns:
            Inferred split type or None if can't determine
        """
        if not values:
            return None
        
        # Convert to lowercase for comparison
        values_lower = [v.lower() for v in values]
        
        # Check for common patterns - order matters for priority
        if any('quarter' in v for v in values_lower):
            return 'quarter'
        elif any('half' in v for v in values_lower):
            return 'time'
        elif any('leading' in v or 'trailing' in v or 'tied' in v for v in values_lower):
            return 'score_differential'
        elif any('home' in v or 'away' in v for v in values_lower):
            return 'place'
        elif any('win' in v or 'loss' in v for v in values_lower):
            return 'result'
        elif any('down' in v for v in values_lower):
            return 'down'
        elif any('yard' in v for v in values_lower):
            return 'yards_to_go'
        elif any('zone' in v for v in values_lower):
            return 'field_position'
        elif any(('own ' in v or 'opp ') and ('1-' in v or '2-' in v or '3-' in v or '4-' in v or '5-' in v or '6-' in v or '7-' in v or '8-' in v or '9-' in v) for v in values_lower):
            return 'field_position'
        elif any('huddle' in v or 'shotgun' in v for v in values_lower):
            return 'snap_type'
        elif any('action' in v for v in values_lower):
            return 'play_action'
        elif any('rpo' in v for v in values_lower):
            return 'run_pass_option'
        elif any('second' in v or 'pocket' in v for v in values_lower):
            return 'time_in_pocket'
        
        return None
    
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
                def get_value(row, col):
                    if col in row.index:
                        val = row[col]
                        if isinstance(val, pd.Series):
                            return str(val.iloc[0]) if not val.empty else ''
                        return str(val) if pd.notna(val) else ''
                    return ''

                games_data = get_value(row, 'G')  # Games played
                completions_data = get_value(row, 'Cmp')  # Completions
                attempts_data = get_value(row, 'Att')  # Attempts
                completion_pct_data = get_value(row, 'Cmp%')  # Completion percentage
                pass_yards_data = get_value(row, 'Yds')  # Passing yards
                pass_tds_data = get_value(row, 'TD')  # Passing touchdowns
                interceptions_data = get_value(row, 'Int')  # Interceptions
                rating_data = get_value(row, 'Rate')  # Passer rating
                sacks_data = get_value(row, 'Sk')  # Sacks
                sack_yards_data = get_value(row, 'Yds')  # Sack yards (second 'Yds' column)
                incompletions_data = get_value(row, 'Inc')  # Incompletions
                wins_data = get_value(row, 'W')  # Wins
                losses_data = get_value(row, 'L')  # Losses
                ties_data = get_value(row, 'T')  # Ties
                attempts_per_game_data = get_value(row, 'A/G')  # Attempts per game
                yards_per_game_data = get_value(row, 'Y/G')  # Yards per game
                points_data = get_value(row, 'Pts')  # Points
                fumbles_data = get_value(row, 'Fmb')  # Fumbles
                fumbles_lost_data = get_value(row, 'FL')  # Fumbles lost
                fumbles_forced_data = get_value(row, 'FF')  # Fumbles forced
                fumbles_recovered_data = get_value(row, 'FR')  # Fumbles recovered
                # For net_yards_per_attempt
                net_yards_per_attempt_data = get_value(row, 'Y/A')

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
                fumbles_data = str(row['Fmb']) if 'Fmb' in row.index and pd.notna(row['Fmb']) else ''  # Fumbles
                fumbles_lost_data = str(row['FL']) if 'FL' in row.index and pd.notna(row['FL']) else ''  # Fumbles lost
                fumbles_forced_data = str(row['FF']) if 'FF' in row.index and pd.notna(row['FF']) else ''  # Fumbles forced
                fumbles_recovered_data = str(row['FR']) if 'FR' in row.index and pd.notna(row['FR']) else ''  # Fumbles recovered
                
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
                split_stats = QBSplitsType1(
                    pfr_id=pfr_id,
                    player_name=player_name,
                    season=season,
                    split=split_type,
                    value=split_category,
                    g=safe_int(games_data) if pd.notna(games_data) and games_data != '' else 0,
                    cmp=safe_int(completions_data) if pd.notna(completions_data) and completions_data != '' else 0,
                    att=safe_int(attempts_data) if pd.notna(attempts_data) and attempts_data != '' else 0,
                    cmp_pct=safe_percentage(completion_pct_data) if pd.notna(completion_pct_data) and completion_pct_data != '' else 0.0,
                    yds=safe_int(pass_yards_data) if pd.notna(pass_yards_data) and pass_yards_data != '' else 0,
                    td=safe_int(pass_tds_data) if pd.notna(pass_tds_data) and pass_tds_data != '' else 0,
                    int=safe_int(interceptions_data) if pd.notna(interceptions_data) and interceptions_data != '' else 0,
                    rate=safe_float(rating_data) if pd.notna(rating_data) and rating_data != '' else 0.0,
                    sk=safe_int(sacks_data) if pd.notna(sacks_data) and sacks_data != '' else 0,
                    sk_yds=safe_int(sack_yards_data) if pd.notna(sack_yards_data) and sack_yards_data != '' else 0,
                    y_a=safe_float(net_yards_per_attempt_data) if pd.notna(net_yards_per_attempt_data) and net_yards_per_attempt_data != '' else 0.0,
                    ay_a=safe_float(net_yards_per_attempt_data) if pd.notna(net_yards_per_attempt_data) and net_yards_per_attempt_data != '' else 0.0,  # Using same value as y_a for now
                    scraped_at=scraped_at,
                    # Additional fields
                    rush_att=safe_int(rush_attempts_data) if pd.notna(rush_attempts_data) and rush_attempts_data != '' else 0,
                    rush_yds=safe_int(rush_yards_data) if pd.notna(rush_yards_data) and rush_yards_data != '' else 0,
                    rush_td=safe_int(rush_tds_data) if pd.notna(rush_tds_data) and rush_tds_data != '' else 0,
                    fmb=safe_int(fumbles_data) if pd.notna(fumbles_data) and fumbles_data != '' else 0,
                    fl=safe_int(fumbles_lost_data) if pd.notna(fumbles_lost_data) and fumbles_lost_data != '' else 0,
                    ff=safe_int(fumbles_forced_data) if pd.notna(fumbles_forced_data) and fumbles_forced_data != '' else 0,
                    fr=safe_int(fumbles_recovered_data) if pd.notna(fumbles_recovered_data) and fumbles_recovered_data != '' else 0,
                    fr_yds=safe_int(fumble_recovery_yards_data) if pd.notna(fumble_recovery_yards_data) and fumble_recovery_yards_data != '' else 0,
                    fr_td=safe_int(fumble_recovery_tds_data) if pd.notna(fumble_recovery_tds_data) and fumble_recovery_tds_data != '' else 0,
                    inc=safe_int(incompletions_data) if pd.notna(incompletions_data) and incompletions_data != '' else 0,
                    w=safe_int(get_value(row, 'W')) if get_value(row, 'W') != '' else 0,
                    l=safe_int(get_value(row, 'L')) if get_value(row, 'L') != '' else 0,
                    t=safe_int(get_value(row, 'T')) if get_value(row, 'T') != '' else 0,
                    a_g=safe_float(attempts_per_game_data) if pd.notna(attempts_per_game_data) and attempts_per_game_data != '' else None,
                    y_g=safe_float(yards_per_game_data) if pd.notna(yards_per_game_data) and yards_per_game_data != '' else None,
                    rush_a_g=safe_float(rush_attempts_per_game_data) if pd.notna(rush_attempts_per_game_data) and rush_attempts_per_game_data != '' else None,
                    rush_y_g=safe_float(rush_yards_per_game_data) if pd.notna(rush_yards_per_game_data) and rush_yards_per_game_data != '' else None,
                    total_td=total_tds,
                    pts=safe_int(points_data) if pd.notna(points_data) and points_data != '' else 0
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
    
    def process_players_concurrently(
        self,
        qb_stats: List[QBBasicStats],
        max_workers: int = None,
    ) -> Tuple[List[QBSplitStats], List[QBSplitsType2]]:
        """
        Process multiple players concurrently while respecting rate limits
        
        Args:
            qb_stats: List of QBStats objects
            max_workers: Maximum number of worker threads
            
        Returns:
            List of QBSplitStats objects
        """
        max_workers = max_workers or config.scraping.max_workers
        all_basic: List[QBSplitStats] = []
        all_adv: List[QBSplitsType2] = []
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
                    basic, adv = future.result()
                    all_basic.extend(basic)
                    all_adv.extend(adv)
                    logger.info(
                        f"Completed splits for {player_name}: basic={len(basic)}, adv={len(adv)}"
                    )
                except Exception as e:
                    self.metrics.add_error(f"Error processing {player_name}: {e}")
        
        logger.info(
            f"Successfully scraped {len(all_basic)} basic and {len(all_adv)} advanced split records"
        )
        return all_basic, all_adv
    
    def get_scraping_metrics(self) -> ScrapingMetrics:
        """Get current scraping metrics"""
        # Get metrics from Selenium manager and merge with our own
        if self.selenium_manager:
            selenium_metrics = self.selenium_manager.get_metrics()
            
            # Update our metrics with Selenium manager data
            self.metrics.total_requests = selenium_metrics.total_requests
            self.metrics.successful_requests = selenium_metrics.successful_requests
            self.metrics.failed_requests = selenium_metrics.failed_requests
            self.metrics.rate_limit_violations = selenium_metrics.blocked_requests
        
        return self.metrics
    
    def reset_metrics(self):
        """Reset scraping metrics"""
        self.metrics = ScrapingMetrics(start_time=datetime.now())
        if self.selenium_manager:
            self.selenium_manager.reset_metrics()
    
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
            total_players=0,  # Will be set by caller
            total_passing_stats=0,  # Will be set by caller
            total_splits=0,  # Will be set by caller
            total_splits_advanced=0, # Will be set by caller
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
        page_source = self.make_request_with_retry(url)
        if not page_source:
            return {}
        
        soup = BeautifulSoup(page_source, 'html.parser')
        return self.discover_splits_from_page(soup)
    
    def close(self):
        """Close the scraper and cleanup resources"""
        if self.selenium_manager:
            self.selenium_manager.end_session()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close() 