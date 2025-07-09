#!/usr/bin/env python3
"""
Raw Data Scraper for NFL QB Statistics
Extracts data matching CSV structures exactly - NO CALCULATIONS
"""

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import random
import re
from dataclasses import dataclass

from models.qb_models import Player, QBPassingStats, QBSplitsType1, QBSplitsType2
from utils.data_utils import (
    safe_int, safe_float, safe_percentage, clean_player_name
)

logger = logging.getLogger(__name__)

class RawDataScraper:
    """Raw data scraper that extracts data matching CSV structures exactly"""
    
    def __init__(self, rate_limit_delay: float = 3.0):
        self.base_url = "https://www.pro-football-reference.com"
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def make_request_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Requesting: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Add delay to be respectful
                time.sleep(self.rate_limit_delay)
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All retries failed for {url}")
                    return None
                
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        return None
    
    def scrape_passing_stats(self, season: int) -> List[QBPassingStats]:
        """
        Scrape main passing stats matching 2024_passing.csv structure exactly
        Filters for QBs only and extracts ALL columns
        """
        url = f"{self.base_url}/years/{season}/passing.htm"
        logger.info(f"Scraping passing stats for {season} season")
        
        response = self.make_request_with_retry(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main passing table
        table = soup.find('table', {'id': 'passing'})
        if not table:
            logger.error("Could not find passing table")
            return []
        
        passing_stats = []
        tbody = table.find('tbody')
        if not tbody:
            logger.error("Could not find table body")
            return []
        
        for row in tbody.find_all('tr'):
            # Skip header rows
            if 'thead' in row.get('class', []):
                continue
            
            # Extract position and filter for QBs only
            pos_cell = row.find('td', {'data-stat': 'pos'})
            if not pos_cell:
                continue
            
            position = pos_cell.get_text(strip=True).upper()
            if position != 'QB':
                continue
            
            try:
                # Extract player info
                name_cell = row.find('td', {'data-stat': 'name_display'})
                if not name_cell:
                    continue
                
                name_link = name_cell.find('a')
                if not name_link:
                    continue
                
                player_name = name_link.get_text(strip=True)
                href = name_link.get('href', '')
                player_url = self.base_url + href if href else ''
                
                # Extract PFR ID from URL
                pfr_id = self._extract_pfr_id_from_url(player_url)
                if not pfr_id:
                    logger.warning(f"Could not extract PFR ID for {player_name}")
                    continue
                
                # Extract all raw stats matching CSV columns exactly
                stats_data = self._extract_passing_stats_from_row(row)
                
                # Create QBPassingStats object with all raw data
                passing_stat = QBPassingStats(
                    pfr_id=pfr_id,
                    player_name=player_name,
                    player_url=player_url,
                    season=season,
                    **stats_data
                )
                
                passing_stats.append(passing_stat)
                logger.debug(f"Extracted passing stats for {player_name} ({stats_data.get('team', 'N/A')})")
                
            except Exception as e:
                logger.error(f"Error processing passing stats row: {e}")
                continue
        
        logger.info(f"Extracted {len(passing_stats)} QB passing stats")
        return passing_stats
    
    def _extract_passing_stats_from_row(self, row) -> Dict[str, Any]:
        """Extract all passing stats from a row matching CSV structure exactly"""
        stats = {}
        
        # Mapping of data-stat attributes to CSV column names
        stat_mapping = {
            'ranker': 'rk',
            'age': 'age',
            'team_name_abbr': 'team',
            'pos': 'pos',
            'games': 'g',
            'games_started': 'gs',
            'qb_rec': 'qb_rec',
            'pass_cmp': 'cmp',
            'pass_att': 'att',
            'pass_cmp_pct': 'cmp_pct',
            'pass_yds': 'yds',
            'pass_td': 'td',
            'pass_td_pct': 'td_pct',
            'pass_int': 'int',
            'pass_int_pct': 'int_pct',
            'pass_first_down': 'first_downs',
            'pass_success': 'succ_pct',
            'pass_long': 'lng',
            'pass_yds_per_att': 'y_a',
            'pass_adj_yds_per_att': 'ay_a',
            'pass_yds_per_cmp': 'y_c',
            'pass_yds_per_g': 'y_g',
            'pass_rating': 'rate',
            'qbr': 'qbr',
            'pass_sacked': 'sk',
            'pass_sacked_yds': 'sk_yds',
            'pass_sacked_pct': 'sk_pct',
            'pass_net_yds_per_att': 'ny_a',
            'pass_adj_net_yds_per_att': 'any_a',
            'comebacks': 'four_qc',
            'game_winning_drives': 'gwd',
            'awards': 'awards',
            'player_additional': 'player_additional'
        }
        
        # Extract each stat
        for data_stat, csv_col in stat_mapping.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = cell.get_text(strip=True)
                
                # Convert to appropriate type based on CSV column
                if csv_col in ['rk', 'age', 'g', 'gs', 'cmp', 'att', 'yds', 'td', 'int', 'first_downs', 'lng', 'sk', 'sk_yds', 'four_qc', 'gwd']:
                    stats[csv_col] = safe_int(value) if value else None
                elif csv_col in ['cmp_pct', 'td_pct', 'int_pct', 'succ_pct', 'y_a', 'ay_a', 'y_c', 'y_g', 'rate', 'qbr', 'sk_pct', 'ny_a', 'any_a']:
                    stats[csv_col] = safe_float(value) if value else None
                else:
                    stats[csv_col] = value if value else None
        
        return stats
    
    def scrape_splits_data(self, qb_passing_stats: List[QBPassingStats]) -> Tuple[List[QBSplitsType1], List[QBSplitsType2]]:
        """
        Scrape splits data for all QBs
        Returns both types of splits data
        """
        all_splits_type1 = []
        all_splits_type2 = []
        
        for qb_stat in qb_passing_stats:
            logger.info(f"Scraping splits for {qb_stat.player_name}")
            
            # Get splits URL
            splits_url = self._get_splits_url(qb_stat.player_url, qb_stat.season)
            if not splits_url:
                logger.warning(f"Could not construct splits URL for {qb_stat.player_name}")
                continue
            
            # Scrape splits data
            splits_type1, splits_type2 = self._scrape_player_splits(
                splits_url, qb_stat.pfr_id, qb_stat.player_name, qb_stat.season
            )
            
            all_splits_type1.extend(splits_type1)
            all_splits_type2.extend(splits_type2)
        
        logger.info(f"Extracted {len(all_splits_type1)} type 1 splits and {len(all_splits_type2)} type 2 splits")
        return all_splits_type1, all_splits_type2
    
    def _get_splits_url(self, player_url: str, season: int) -> Optional[str]:
        """Construct splits URL from player URL"""
        if not player_url:
            return None
        
        # Extract player ID from URL
        pfr_id = self._extract_pfr_id_from_url(player_url)
        if not pfr_id:
            return None
        
        # Construct splits URL
        return f"{self.base_url}/players/{pfr_id[0]}/{pfr_id}/splits/{season}/"
    
    def _scrape_player_splits(self, splits_url: str, pfr_id: str, player_name: str, season: int) -> Tuple[List[QBSplitsType1], List[QBSplitsType2]]:
        """Scrape splits data for a single player"""
        response = self.make_request_with_retry(splits_url)
        if not response:
            return [], []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find splits tables
        splits_type1 = self._extract_splits_type1(soup, pfr_id, player_name, season)
        splits_type2 = self._extract_splits_type2(soup, pfr_id, player_name, season)
        
        return splits_type1, splits_type2
    
    def _extract_splits_type1(self, soup: BeautifulSoup, pfr_id: str, player_name: str, season: int) -> List[QBSplitsType1]:
        """Extract splits matching advanced_stats_1.csv structure"""
        splits = []
        
        # Find the main splits table (usually 'splits')
        table = soup.find('table', {'id': 'splits'})
        if not table:
            logger.warning(f"Could not find splits table for {player_name}")
            return splits
        
        tbody = table.find('tbody')
        if not tbody:
            return splits
        
        for row in tbody.find_all('tr'):
            # Skip header rows
            if 'thead' in row.get('class', []):
                continue
            
            try:
                # Extract split type and value
                split_info = self._extract_split_info(row)
                if not split_info:
                    continue
                
                # Extract all stats matching CSV structure
                stats_data = self._extract_splits_type1_from_row(row)
                
                # Create QBSplitsType1 object
                split_stat = QBSplitsType1(
                    pfr_id=pfr_id,
                    player_name=player_name,
                    season=season,
                    split=split_info['split'],
                    value=split_info['value'],
                    **stats_data
                )
                
                splits.append(split_stat)
                
            except Exception as e:
                logger.error(f"Error processing splits type 1 row: {e}")
                continue
        
        return splits
    
    def _extract_splits_type2(self, soup: BeautifulSoup, pfr_id: str, player_name: str, season: int) -> List[QBSplitsType2]:
        """Extract splits matching advanced_stats.2.csv structure"""
        splits = []
        
        # Find the advanced splits table (usually 'advanced_splits')
        table = soup.find('table', {'id': 'advanced_splits'})
        if not table:
            logger.warning(f"Could not find advanced splits table for {player_name}")
            return splits
        
        tbody = table.find('tbody')
        if not tbody:
            return splits
        
        for row in tbody.find_all('tr'):
            # Skip header rows
            if 'thead' in row.get('class', []):
                continue
            
            try:
                # Extract split type and value
                split_info = self._extract_split_info(row)
                if not split_info:
                    continue
                
                # Extract all stats matching CSV structure
                stats_data = self._extract_splits_type2_from_row(row)
                
                # Create QBSplitsType2 object
                split_stat = QBSplitsType2(
                    pfr_id=pfr_id,
                    player_name=player_name,
                    season=season,
                    split=split_info['split'],
                    value=split_info['value'],
                    **stats_data
                )
                
                splits.append(split_stat)
                
            except Exception as e:
                logger.error(f"Error processing splits type 2 row: {e}")
                continue
        
        return splits
    
    def _extract_split_info(self, row) -> Optional[Dict[str, str]]:
        """Extract split type and value from a row"""
        # Try different approaches to get split info
        split_id_cell = row.find('td', {'data-stat': 'split_id'})
        split_value_cell = row.find('td', {'data-stat': 'split_value'})
        
        if split_id_cell and split_value_cell:
            return {
                'split': split_id_cell.get_text(strip=True),
                'value': split_value_cell.get_text(strip=True)
            }
        
        # Alternative approach - look for first two cells
        cells = row.find_all('td')
        if len(cells) >= 2:
            return {
                'split': cells[0].get_text(strip=True),
                'value': cells[1].get_text(strip=True)
            }
        
        return None
    
    def _extract_splits_type1_from_row(self, row) -> Dict[str, Any]:
        """Extract splits type 1 stats matching advanced_stats_1.csv exactly"""
        stats = {}
        
        # Mapping of data-stat attributes to CSV columns
        stat_mapping = {
            'g': 'g',
            'wins': 'w',
            'losses': 'l',
            'ties': 't',
            'pass_cmp': 'cmp',
            'pass_att': 'att',
            'pass_inc': 'inc',
            'pass_cmp_pct': 'cmp_pct',
            'pass_yds': 'yds',
            'pass_td': 'td',
            'pass_int': 'int',
            'pass_rating': 'rate',
            'pass_sacked': 'sk',
            'pass_sacked_yds': 'sk_yds',
            'pass_yds_per_att': 'y_a',
            'pass_adj_yds_per_att': 'ay_a',
            'pass_att_per_g': 'a_g',
            'pass_yds_per_g': 'y_g',
            'rush_att': 'rush_att',
            'rush_yds': 'rush_yds',
            'rush_yds_per_att': 'rush_y_a',
            'rush_td': 'rush_td',
            'rush_att_per_g': 'rush_a_g',
            'rush_yds_per_g': 'rush_y_g',
            'total_td': 'total_td',
            'scoring': 'pts',
            'fumbles': 'fmb',
            'fumbles_lost': 'fl',
            'fumbles_forced': 'ff',
            'fumbles_recovered': 'fr',
            'fumbles_rec_yds': 'fr_yds',
            'fumbles_rec_td': 'fr_td'
        }
        
        # Extract each stat
        for data_stat, csv_col in stat_mapping.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = cell.get_text(strip=True)
                
                # Convert to appropriate type
                if csv_col in ['g', 'w', 'l', 't', 'cmp', 'att', 'inc', 'yds', 'td', 'int', 'sk', 'sk_yds', 'rush_att', 'rush_yds', 'rush_td', 'total_td', 'pts', 'fmb', 'fl', 'ff', 'fr', 'fr_yds', 'fr_td']:
                    stats[csv_col] = safe_int(value) if value else None
                elif csv_col in ['cmp_pct', 'rate', 'y_a', 'ay_a', 'a_g', 'y_g', 'rush_y_a', 'rush_a_g', 'rush_y_g']:
                    stats[csv_col] = safe_float(value) if value else None
                else:
                    stats[csv_col] = value if value else None
        
        return stats
    
    def _extract_splits_type2_from_row(self, row) -> Dict[str, Any]:
        """Extract splits type 2 stats matching advanced_stats.2.csv exactly"""
        stats = {}
        
        # Mapping of data-stat attributes to CSV columns
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
            'rush_first_down': 'rush_first_downs'
        }
        
        # Extract each stat
        for data_stat, csv_col in stat_mapping.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = cell.get_text(strip=True)
                
                # Convert to appropriate type
                if csv_col in ['cmp', 'att', 'inc', 'yds', 'td', 'first_downs', 'int', 'sk', 'sk_yds', 'rush_att', 'rush_yds', 'rush_td', 'rush_first_downs']:
                    stats[csv_col] = safe_int(value) if value else None
                elif csv_col in ['cmp_pct', 'rate', 'y_a', 'ay_a', 'rush_y_a']:
                    stats[csv_col] = safe_float(value) if value else None
                else:
                    stats[csv_col] = value if value else None
        
        return stats
    
    def _extract_pfr_id_from_url(self, url: str) -> Optional[str]:
        """Extract PFR ID from player URL"""
        if not url:
            return None
        
        # URL format: /players/B/BurrJo01.htm
        match = re.search(r'/players/[A-Z]/([A-Za-z0-9]+)\.htm', url)
        if match:
            return match.group(1)
        
        return None
    
    def create_players_from_passing_stats(self, passing_stats: List[QBPassingStats]) -> List[Player]:
        """Create Player objects from passing stats"""
        players = []
        
        for stat in passing_stats:
            player = Player(
                pfr_id=stat.pfr_id,
                player_name=stat.player_name,
                age=stat.age,
                position='QB',
                pfr_url=stat.player_url
            )
            players.append(player)
        
        return players 