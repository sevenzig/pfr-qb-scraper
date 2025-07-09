#!/usr/bin/env python3
"""
Enhanced NFL QB Data Scraper for 2024 Season

This script scrapes QB data from Pro Football Reference for the 2024 season:
1. Scrapes main passing stats for all QBs from /years/2024/passing.htm
2. For each QB, scrapes advanced splits from /players/{player_id}/splits/{year}/
3. Stores all data in the PostgreSQL database (Supabase)

Usage:
    python scripts/enhanced_qb_scraper.py [--player PLAYER_NAME] [--all]
"""

import asyncio
import logging
import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union, Any, cast
import pandas as pd
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
import requests
import time
import re
from dataclasses import dataclass

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.config import config
from database.db_manager import DatabaseManager
from models.qb_models import QBBasicStats, QBAdvancedStats, QBSplitStats, Player
from scrapers.enhanced_scraper import EnhancedPFRScraper
from utils.data_utils import normalize_pfr_team_code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_qb_scraping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QBData:
    """Container for QB data including main stats and splits"""
    main_stats: QBBasicStats
    splits_data: List[QBSplitStats]
    player_url: str

class EnhancedQBScraper:
    """Enhanced scraper for QB data with advanced splits support"""
    
    def __init__(self):
        """Initialize the scraper with configuration"""
        self.config = config
        self.db_manager = DatabaseManager(config.get_database_url())
        self.scraper = EnhancedPFRScraper(rate_limit_delay=config.get_rate_limit_delay())  # Use config rate limit delay
        self.season = 2024
        self.base_url = "https://www.pro-football-reference.com"
        
    def scrape_all_qb_main_stats(self) -> List[QBBasicStats]:
        """
        Scrape main QB statistics for 2024 season from /years/2024/passing.htm
        
        Returns:
            List of QBBasicStats objects for all QBs
        """
        url = f"{self.base_url}/years/{self.season}/passing.htm"
        logger.info(f"Scraping QB main stats for {self.season} season from {url}")
        
        response = self.scraper.make_request_with_retry(url)
        if not response:
            logger.error("Failed to fetch main passing page")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main passing table
        table = soup.find('table', {'id': 'passing'})  # type: ignore
        if not table:
            logger.error("Could not find passing table")
            return []
        
        qb_stats = []
        current_time = datetime.now()
        
        # Find all rows in the table body
        tbody = table.find('tbody')  # type: ignore
        if not tbody:
            logger.error("Could not find table body")
            return []
        
        for row in tbody.find_all('tr'):  # type: ignore
            # Skip header rows and empty rows
            row_classes = row.get('class', [])  # type: ignore
            if isinstance(row_classes, list) and 'thead' in row_classes:
                continue
            
            # Extract position from the row
            pos_cell = row.find('td', {'data-stat': 'pos'})  # type: ignore
            if not pos_cell:
                continue
            
            position = pos_cell.get_text(strip=True).upper()  # type: ignore
            
            # Filter for QBs only
            if position != 'QB':
                continue
            
            try:
                # Extract player name and URL
                name_cell = row.find('td', {'data-stat': 'name_display'})  # type: ignore
                if not name_cell:
                    continue
                
                name_link = name_cell.find('a')  # type: ignore
                if not name_link:
                    continue
                
                player_name = name_link.get_text(strip=True)  # type: ignore
                href = name_link.get('href', '')  # type: ignore
                player_url = self.base_url + str(href) if href else ''
                base_pfr_id = self._extract_player_id_from_url(player_url)

                if not base_pfr_id:
                    logger.warning(f"Could not extract pfr_id for {player_name}, skipping.")
                    continue
                
                # Extract team to handle multi-team players
                team_cell = row.find('td', {'data-stat': 'team_name_abbr'})  # type: ignore
                team_code = normalize_pfr_team_code(team_cell.get_text(strip=True) if team_cell else '')  # type: ignore
                
                # For multi-team players (2TM, 3TM, etc.), append team code to make unique PFR ID
                if team_code and ('2TM' in team_code or '3TM' in team_code or len(team_code) == 3):
                    pfr_id = f"{base_pfr_id}_{team_code.lower()}"
                else:
                    pfr_id = base_pfr_id
                
                # Extract all the stats you mentioned
                stats = self._extract_comprehensive_row_stats(cast(Tag, row))
                
                # Create QBBasicStats object with all fields
                qb_stat = QBBasicStats(
                    pfr_id=pfr_id,
                    player_name=player_name,
                    player_url=player_url,
                    season=self.season,
                    rk=self._safe_int(stats.get('rank')),
                    age=self._safe_int(stats.get('age')),
                    team=team_code,
                    pos='QB',  # We filter for QBs so this is always QB
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
                
                qb_stats.append(qb_stat)
                logger.info(f"Extracted QB stats for {player_name} ({qb_stat.team})")
                
            except Exception as e:
                logger.error(f"Error processing QB row: {e}")
                continue
        
        logger.info(f"Successfully extracted stats for {len(qb_stats)} QBs")
        return qb_stats
    
    def _extract_comprehensive_row_stats(self, row: Tag) -> Dict[str, str]:
        """Extract all stats from a table row including all the fields you mentioned"""
        stats = {}
        
        # Comprehensive mapping of all data-stat attributes to our field names
        stat_mapping = {
            # Basic info
            'ranker': 'rank',
            'age': 'age',
            'team_name_abbr': 'team',
            'games': 'games',
            'games_started': 'games_started',
            'qb_rec': 'qb_record',
            
            # Passing stats
            'pass_cmp': 'completions',
            'pass_att': 'attempts',
            'pass_cmp_pct': 'completion_pct',
            'pass_yds': 'pass_yards',
            'pass_td': 'pass_tds',
            'pass_td_pct': 'td_pct',
            'pass_int': 'interceptions',
            'pass_int_pct': 'int_pct',
            'pass_first_down': 'first_downs',
            'pass_success': 'success_pct',
            'pass_long': 'longest_pass',
            'pass_yds_per_att': 'yards_per_attempt',
            'pass_adj_yds_per_att': 'adjusted_yards_per_attempt',
            'pass_yds_per_cmp': 'yards_per_completion',
            'pass_yds_per_g': 'yards_per_game',
            'pass_rating': 'rating',
            'qbr': 'qbr',
            
            # Sacks
            'pass_sacked': 'sacks',
            'pass_sacked_yds': 'sack_yards',
            'pass_sacked_pct': 'sack_pct',
            
            # Advanced stats
            'pass_net_yds_per_att': 'net_yards_per_attempt',
            'pass_adj_net_yds_per_att': 'adjusted_net_yards_per_attempt',
            'comebacks': 'fourth_quarter_comebacks',
            'gwd': 'game_winning_drives',
            
            # Awards (we'll store this separately)
            'awards': 'awards',
            'player_additional': 'player_additional'
        }
        
        for stat_attr, field_name in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            if cell:
                stats[field_name] = cell.get_text(strip=True)
        
        return stats
    
    def scrape_qb_advanced_splits(self, qb_stat: QBBasicStats) -> List[QBSplitStats]:
        """
        Scrape QB advanced splits from /players/{player_id}/splits/{year}/
        
        Args:
            qb_stat: QBBasicStats object containing player info
            
        Returns:
            List of QBSplitStats objects
        """
        # Extract player ID from the URL
        player_id = self._extract_player_id_from_url(qb_stat.player_url)
        if not player_id:
            logger.error(f"Could not extract player ID from URL: {qb_stat.player_url}")
            return []
        
        # Construct the splits URL
        splits_url = f"{self.base_url}/players/{player_id[0]}/{player_id}/splits/{self.season}/"
        logger.info(f"Scraping advanced splits for {qb_stat.player_name} from: {splits_url}")
        
        response = self.scraper.make_request_with_retry(splits_url)
        if not response:
            logger.error(f"Failed to fetch splits page for {qb_stat.player_name}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all splits tables - they might be in different formats
        splits_tables = []
        
        # Look for tables with splits data
        all_tables = soup.find_all('table')
        for table in all_tables:
            # Check if table has splits-like structure
            if self._is_splits_table(cast(Tag, table)):
                splits_tables.append(table)
        
        logger.info(f"Found {len(splits_tables)} splits tables for {qb_stat.player_name}")
        
        all_splits = []
        current_time = datetime.now()
        
        for table in splits_tables:
            try:
                table_splits = self._process_advanced_splits_table(cast(Tag, table), qb_stat, current_time)
                all_splits.extend(table_splits)
                table_id = table.get('id', 'unknown') if hasattr(table, 'get') else 'unknown'
                logger.info(f"Processed {len(table_splits)} splits from table {table_id}")
            except Exception as e:
                table_id = table.get('id', 'unknown') if hasattr(table, 'get') else 'unknown'
                logger.error(f"Error processing splits table {table_id}: {e}")
                continue
        
        logger.info(f"Total splits extracted for {qb_stat.player_name}: {len(all_splits)}")
        return all_splits
    
    def _extract_player_id_from_url(self, player_url: str) -> Optional[str]:
        """Extract PFR player ID from URL"""
        if not player_url:
            return None
        match = re.search(r'/players/[a-zA-Z]/([a-zA-Z0-9]+)\.htm', player_url)
        return match.group(1) if match else None
    
    def _is_splits_table(self, table: Tag) -> bool:
        """Check if a table is a splits table by looking for a 'Split' column"""
        # Look for common splits indicators
        rows = table.find_all('tr')
        for row in rows:
            # Check for split_value data-stat (common in splits tables)
            split_cell = cast(Tag, row).find('td', {'data-stat': 'split_value'})
            if split_cell:
                return True
            
            # Check for "Split" or "Value" headers
            cells = cast(Tag, row).find_all(['th', 'td'])
            for cell in cells:
                cell_text = cell.get_text(strip=True).lower()
                if cell_text in ['split', 'value', 'category']:
                    return True
        
        return False

    def _process_advanced_splits_table(self, table: Tag, qb_stat: QBBasicStats, current_time: datetime) -> List[QBSplitStats]:
        """Process a single advanced splits table and extract QBSplitStats"""
        
        splits_data = []
        table_id = str(table.get('id', 'unknown_splits_table'))
        split_type = self._determine_split_type(table_id)
        
        tbody = table.find('tbody')
        if not tbody:
            logger.warning(f"Could not find tbody in table {table_id}")
            return []
            
        for row in cast(Tag, tbody).find_all('tr'):
            # Skip header rows
            if cast(Tag, row).find('th', {'scope': 'row'}) is None:
                continue
            
            # Extract stats based on table type
            if split_type == 'basic_splits':
                stats = self._extract_basic_split_row_stats(cast(Tag, row))
            else:
                stats = self._extract_advanced_split_row_stats(cast(Tag, row))
            
            if not stats:
                continue

            try:
                split_stat = QBSplitStats(
                    pfr_id=qb_stat.pfr_id,
                    player_name=qb_stat.player_name,
                    season=self.season,
                    split=split_type,
                    value=stats.get('category', 'Unknown'),
                    g=self._safe_int(stats.get('games', 0)),
                    cmp=self._safe_int(stats.get('completions', 0)),
                    att=self._safe_int(stats.get('attempts', 0)),
                    cmp_pct=self._safe_float(stats.get('completion_pct', 0)),
                    yds=self._safe_int(stats.get('pass_yards', 0)),
                    td=self._safe_int(stats.get('pass_tds', 0)),
                    int=self._safe_int(stats.get('interceptions', 0)),
                    rate=self._safe_float(stats.get('rating', 0)),
                    sk=self._safe_int(stats.get('sacks', 0)),
                    sk_yds=self._safe_int(stats.get('sack_yards', 0)),
                    y_a=self._safe_float(stats.get('net_yards_per_attempt', 0)),
                    rush_att=self._safe_int(stats.get('rush_attempts', 0)),
                    rush_yds=self._safe_int(stats.get('rush_yards', 0)),
                    rush_td=self._safe_int(stats.get('rush_tds', 0)),
                    total_td=self._safe_int(stats.get('total_tds', 0)),
                    fmb=self._safe_int(stats.get('fumbles', 0)),
                    fl=self._safe_int(stats.get('fumbles_lost', 0)),
                    ff=self._safe_int(stats.get('fumbles_forced', 0)),
                    fr=self._safe_int(stats.get('fumbles_recovered', 0)),
                    fr_yds=self._safe_int(stats.get('fumble_recovery_yards', 0)),
                    fr_td=self._safe_int(stats.get('fumble_recovery_tds', 0)),
                    pts=self._safe_int(stats.get('points', 0)),
                    w=self._safe_int(stats.get('wins', 0)),
                    l=self._safe_int(stats.get('losses', 0)),
                    t=self._safe_int(stats.get('ties', 0)),
                    inc=self._safe_int(stats.get('incompletions', 0)),
                    a_g=self._safe_float(stats.get('attempts_per_game')),
                    y_g=self._safe_float(stats.get('yards_per_game')),
                    rush_a_g=self._safe_float(stats.get('rush_attempts_per_game')),
                    rush_y_g=self._safe_float(stats.get('rush_yards_per_game')),
                    scraped_at=current_time,
                    updated_at=current_time,
                )
                splits_data.append(split_stat)
                
            except (ValueError, TypeError) as e:
                logger.error(f"Error creating QBSplitStats object for row: {row}")
                logger.error(f"Error details: {e}")
                continue
        
        return splits_data

    def _extract_basic_split_row_stats(self, row: Tag) -> Dict[str, Any]:
        """Extract stats from the main stats table row, convert types, and calculate totals."""
        stats: Dict[str, Any] = {}
        
        # First, extract the category from the row
        split_id_cell = row.find('td', {'data-stat': 'split_id'})
        split_value_cell = row.find('td', {'data-stat': 'split_value'})
        category = (split_id_cell.get_text(strip=True) if split_id_cell else '') or \
                   (split_value_cell.get_text(strip=True) if split_value_cell else '') or \
                   'Unknown'
        stats['category'] = category
        
        # Define types along with mappings
        stat_mapping: Dict[str, Tuple[str, type]] = {
            'g': ('games', int),
            'wins': ('wins', int),
            'losses': ('losses', int),
            'ties': ('ties', int),
            'pass_cmp': ('completions', int),
            'pass_att': ('attempts', int),
            'pass_inc': ('incompletions', int),
            'pass_cmp_perc': ('completion_pct', float),
            'pass_yds': ('pass_yards', int),
            'pass_td': ('pass_tds', int),
            'pass_int': ('interceptions', int),
            'pass_rating': ('rating', float),
            'pass_sacked': ('sacks', int),
            'pass_sacked_yds': ('sack_yards', int),
            'pass_yds_per_att': ('yards_per_attempt', float),
            'pass_adj_yds_per_att': ('adjusted_yards_per_attempt', float),
            'pass_att_per_g': ('attempts_per_game', float),
            'pass_yds_per_g': ('yards_per_game', float),
            'rush_att': ('rush_attempts', int),
            'rush_yds': ('rush_yards', int),
            'rush_yds_per_att': ('rush_yards_per_attempt', float),
            'rush_td': ('rush_tds', int),
            'rush_att_per_g': ('rush_attempts_per_game', float),
            'rush_yds_per_g': ('rush_yards_per_game', float),
            'scoring': ('points', int),
            'fumbles': ('fumbles', int),
            'fumbles_lost': ('fumbles_lost', int),
            'fumbles_forced': ('fumbles_forced', int),
            'fumbles_rec': ('fumbles_recovered', int),
            'fumbles_rec_yds': ('fumble_recovery_yards', int),
            'fumbles_rec_td': ('fumble_recovery_tds', int),
            'total_td': ('total_tds', int),  # Only scrape if available
        }

        for stat_attr, (field_name, field_type) in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            value = cell.get_text(strip=True) if cell else ''
            if field_type is int:
                stats[field_name] = self._safe_int(value)
            elif field_type is float:
                stats[field_name] = self._safe_float(value)

        return stats

    def _extract_advanced_split_row_stats(self, row: Tag) -> Dict[str, Any]:
        """Extract stats from an advanced split table row, convert types."""
        stats: Dict[str, Any] = {}
        
        # First, extract the category from the row
        split_id_cell = row.find('td', {'data-stat': 'split_id'})
        split_value_cell = row.find('td', {'data-stat': 'split_value'})
        category = (split_id_cell.get_text(strip=True) if split_id_cell else '') or \
                   (split_value_cell.get_text(strip=True) if split_value_cell else '') or \
                   'Unknown'
        stats['category'] = category
        
        stat_mapping: Dict[str, Tuple[str, type]] = {
            'g': ('games', int),
            'pass_cmp': ('completions', int),
            'pass_att': ('attempts', int),
            'pass_cmp_perc': ('completion_pct', float),
            'pass_yds': ('pass_yards', int),
            'pass_td': ('pass_tds', int),
            'pass_int': ('interceptions', int),
            'pass_rating': ('rating', float),
            'pass_sacked': ('sacks', int),
            'pass_sacked_yds': ('sack_yards', int),
            'pass_yds_per_att': ('yards_per_attempt', float),
            'pass_adj_yds_per_att': ('adjusted_yards_per_attempt', float),
            'total_td': ('total_tds', int),  # Only scrape if available
        }
        
        for stat_attr, (field_name, field_type) in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            value = cell.get_text(strip=True) if cell else ''
            if field_type is int:
                stats[field_name] = self._safe_int(value)
            elif field_type is float:
                stats[field_name] = self._safe_float(value)
        
        return stats
    
    def _determine_split_type(self, table_id: str) -> str:
        """Determine split type from table ID or content"""
        table_id_lower = table_id.lower()
        
        if 'home' in table_id_lower or 'away' in table_id_lower:
            return 'home_away'
        elif 'quarter' in table_id_lower:
            return 'by_quarter'
        elif 'half' in table_id_lower:
            return 'by_half'
        elif 'month' in table_id_lower:
            return 'by_month'
        elif 'down' in table_id_lower:
            return 'by_down'
        elif 'distance' in table_id_lower:
            return 'by_distance'
        elif 'win' in table_id_lower or 'loss' in table_id_lower:
            return 'win_loss'
        elif 'division' in table_id_lower:
            return 'vs_division'
        elif 'indoor' in table_id_lower or 'outdoor' in table_id_lower:
            return 'indoor_outdoor'
        elif 'surface' in table_id_lower:
            return 'surface'
        elif 'weather' in table_id_lower:
            return 'weather'
        elif 'temperature' in table_id_lower:
            return 'temperature'
        elif 'score' in table_id_lower:
            return 'by_score'
        elif 'red' in table_id_lower or 'zone' in table_id_lower:
            return 'red_zone'
        elif 'time' in table_id_lower:
            return 'time_of_game'
        elif 'winning' in table_id_lower:
            return 'vs_winning_teams'
        elif 'day' in table_id_lower:
            return 'day_of_week'
        elif 'game_time' in table_id_lower:
            return 'game_time'
        elif 'playoff' in table_id_lower:
            return 'playoff_type'
        else:
            return 'other'
    
    def _generate_player_id(self, player_name: str) -> str:
        """Generate a unique player ID from player name"""
        return re.sub(r'[^a-zA-Z0-9]', '', player_name.lower())
    
    def _safe_int(self, value: Union[str, int, float, None]) -> int:
        """Safely convert value to integer"""
        if value is None or value == '':
            return 0
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return 0
    
    def _safe_float(self, value: Union[str, int, float, None]) -> float:
        """Safely convert value to float, handling None and empty strings"""
        if value is None or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def save_to_database(self, qb_stats: List[QBBasicStats], all_splits_data: List[QBSplitStats]):
        """
        Save QB stats and splits data to the database
        
        Args:
            qb_stats: List of QBBasicStats objects
            all_splits_data: List of QBSplitStats objects
        """
        try:
            if qb_stats:
                logger.info(f"Saving {len(qb_stats)} players to database...")
                for qb_stat in qb_stats:
                    player = Player(
                        pfr_id=qb_stat.pfr_id,
                        player_name=qb_stat.player_name,
                        pfr_url=qb_stat.player_url,
                    )
                    self.db_manager.insert_player(player)

                logger.info(f"Saving {len(qb_stats)} QB main stats to database...")
                self.db_manager.insert_qb_basic_stats(qb_stats)
            
            if all_splits_data:
                logger.info(f"Saving {len(all_splits_data)} QB splits to database...")
                self.db_manager.insert_qb_splits(all_splits_data)
                
            logger.info("Database save operation completed")
            
        except Exception as e:
            logger.error(f"Error saving QB data to database: {e}")
            raise
    
    def scrape_single_qb(self, player_name: str) -> Optional[QBData]:
        """Scrape main stats and splits for a single QB"""
        logger.info(f"Scraping data for single QB: {player_name}")
        
        # First get all QB stats to find the target player
        all_qb_stats = self.scrape_all_qb_main_stats()
        
        # Find the target QB
        target_qb = None
        for qb_stat in all_qb_stats:
            if qb_stat.player_name.lower() == player_name.lower():
                target_qb = qb_stat
                break
        
        if not target_qb:
            logger.error(f"Could not find QB: {player_name}")
            return None
        
        # Scrape splits for this QB
        splits_data = self.scrape_qb_advanced_splits(target_qb)
        
        return QBData(
            main_stats=target_qb,
            splits_data=splits_data,
            player_url=target_qb.player_url
        )
    
    def scrape_all_qbs(self) -> List[QBData]:
        """Scrape data for all QBs"""
        logger.info("Scraping data for all QBs")
        
        # Get all QB main stats
        all_qb_stats = self.scrape_all_qb_main_stats()
        
        all_qb_data = []
        all_splits_data = []
        
        for i, qb_stat in enumerate(all_qb_stats):
            logger.info(f"Processing QB {i+1}/{len(all_qb_stats)}: {qb_stat.player_name}")
            
            # Scrape splits for this QB
            splits_data = self.scrape_qb_advanced_splits(qb_stat)
            
            qb_data = QBData(
                main_stats=qb_stat,
                splits_data=splits_data,
                player_url=qb_stat.player_url
            )
            
            all_qb_data.append(qb_data)
            all_splits_data.extend(splits_data)
            
            # Add delay between QBs to be respectful
            if i < len(all_qb_stats) - 1:
                time.sleep(2)
        
        return all_qb_data

def main():
    """Main function to run the enhanced QB scraper"""
    parser = argparse.ArgumentParser(description='Enhanced NFL QB Data Scraper')
    parser.add_argument('--player', type=str, help='Scrape data for specific QB (e.g., "Joe Burrow")')
    parser.add_argument('--all', action='store_true', help='Scrape data for all QBs')
    
    args = parser.parse_args()
    
    scraper = EnhancedQBScraper()
    
    if args.player:
        # Scrape single QB
        qb_data = scraper.scrape_single_qb(args.player)
        if qb_data:
            scraper.save_to_database([qb_data.main_stats], qb_data.splits_data)
            print(f"\n=== {qb_data.main_stats.player_name} 2024 Data Summary ===")
            print(f"Player: {qb_data.main_stats.player_name}")
            print(f"Team: {qb_data.main_stats.team}")
            print(f"Games: {qb_data.main_stats.g}")
            print(f"Completions: {qb_data.main_stats.cmp}/{qb_data.main_stats.att}")
            print(f"Yards: {qb_data.main_stats.yds}")
            print(f"TDs: {qb_data.main_stats.td}")
            print(f"INTs: {qb_data.main_stats.int}")
            print(f"Rating: {qb_data.main_stats.rate}")
            print(f"Splits Records: {len(qb_data.splits_data)}")
        else:
            print(f"Failed to scrape data for {args.player}")
    
    elif args.all:
        # Scrape all QBs
        all_qb_data = scraper.scrape_all_qbs()
        
        # Save all data
        all_qb_stats = [qb_data.main_stats for qb_data in all_qb_data]
        all_splits_data = []
        for qb_data in all_qb_data:
            all_splits_data.extend(qb_data.splits_data)
        
        scraper.save_to_database(all_qb_stats, all_splits_data)
        
        print(f"\n=== Scraping Complete ===")
        print(f"Total QBs processed: {len(all_qb_data)}")
        print(f"Total splits records: {len(all_splits_data)}")
    
    else:
        # Default: scrape Joe Burrow as example
        print("No arguments provided. Scraping Joe Burrow as example...")
        qb_data = scraper.scrape_single_qb("Joe Burrow")
        if qb_data:
            scraper.save_to_database([qb_data.main_stats], qb_data.splits_data)
            print(f"\n=== {qb_data.main_stats.player_name} 2024 Data Summary ===")
            print(f"Player: {qb_data.main_stats.player_name}")
            print(f"Team: {qb_data.main_stats.team}")
            print(f"Games: {qb_data.main_stats.g}")
            print(f"Completions: {qb_data.main_stats.cmp}/{qb_data.main_stats.att}")
            print(f"Yards: {qb_data.main_stats.yds}")
            print(f"TDs: {qb_data.main_stats.td}")
            print(f"INTs: {qb_data.main_stats.int}")
            print(f"Rating: {qb_data.main_stats.rate}")
            print(f"Splits Records: {len(qb_data.splits_data)}")

if __name__ == "__main__":
    main() 