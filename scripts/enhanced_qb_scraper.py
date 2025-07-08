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
from models.qb_models import QBBasicStats, QBAdvancedStats, QBSplitStats
from scrapers.enhanced_scraper import EnhancedPFRScraper

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
        self.scraper = EnhancedPFRScraper(rate_limit_delay=3.0)  # 3 second delay between requests
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
                
                # Extract all the stats you mentioned
                stats = self._extract_comprehensive_row_stats(cast(Tag, row))
                
                # Create QBBasicStats object with all fields
                qb_stat = QBBasicStats(
                    player_id=self._generate_player_id(player_name),
                    player_name=player_name,
                    team=stats.get('team', ''),
                    season=self.season,
                    games_played=self._safe_int(stats.get('games', 0)),
                    games_started=self._safe_int(stats.get('games_started', 0)),
                    completions=self._safe_int(stats.get('completions', 0)),
                    attempts=self._safe_int(stats.get('attempts', 0)),
                    completion_pct=self._safe_float(stats.get('completion_pct', 0)),
                    pass_yards=self._safe_int(stats.get('pass_yards', 0)),
                    pass_tds=self._safe_int(stats.get('pass_tds', 0)),
                    interceptions=self._safe_int(stats.get('interceptions', 0)),
                    longest_pass=self._safe_int(stats.get('longest_pass', 0)),
                    rating=self._safe_float(stats.get('rating', 0)),
                    qbr=self._safe_float(stats.get('qbr', None)),
                    sacks=self._safe_int(stats.get('sacks', 0)),
                    sack_yards=self._safe_int(stats.get('sack_yards', 0)),
                    net_yards_per_attempt=self._safe_float(stats.get('net_yards_per_attempt', 0)),
                    adjusted_net_yards_per_attempt=self._safe_float(stats.get('adjusted_net_yards_per_attempt', 0)),
                    fourth_quarter_comebacks=self._safe_int(stats.get('fourth_quarter_comebacks', 0)),
                    game_winning_drives=self._safe_int(stats.get('game_winning_drives', 0)),
                    scraped_at=current_time
                )
                
                # Store the player URL for later use
                qb_stat.player_url = player_url
                
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
            'pass_1st': 'first_downs',
            'pass_succ_pct': 'success_pct',
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
            'game_winning_drives': 'game_winning_drives',
            
            # Awards (we'll store this separately)
            'awards': 'awards'
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
            if self._is_splits_table(table):
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
        """Extract player ID from player URL"""
        if not player_url:
            return None
        
        # URL format: /players/B/BurrJo01.htm
        match = re.search(r'/players/([A-Z])/([A-Za-z0-9]+)\.htm', player_url)
        if match:
            return match.group(2)  # Return the player ID part
        
        return None
    
    def _is_splits_table(self, table: Tag) -> bool:
        """Check if a table contains splits data"""
        # Look for common splits indicators
        rows = table.find_all('tr')
        for row in rows:
            # Check for split_value data-stat (common in splits tables)
            split_cell = row.find('td', {'data-stat': 'split_value'})
            if split_cell:
                return True
            
            # Check for "Split" or "Value" headers
            cells = row.find_all(['th', 'td'])
            for cell in cells:
                cell_text = cell.get_text(strip=True).lower()
                if cell_text in ['split', 'value', 'category']:
                    return True
        
        return False
    
    def _process_advanced_splits_table(self, table: Tag, qb_stat: QBBasicStats, current_time: datetime) -> List[QBSplitStats]:
        """Process an advanced splits table and extract split statistics"""
        splits = []

        # Get table ID to determine split type
        table_id = str(table.get('id', ''))
        
        # Determine if this is the main stats table or advanced splits table
        if table_id == 'stats':
            split_type = 'basic_splits'
            stats = self._extract_basic_split_row_stats
        elif table_id == 'advanced_splits':
            split_type = 'advanced_splits'
            stats = self._extract_advanced_split_row_stats
        else:
            split_type = self._determine_split_type(table_id)
            stats = self._extract_advanced_split_row_stats

        # Find all rows in the table
        rows = table.find_all('tr')

        for row in rows:
            # Only process rows with <td> elements (skip headers)
            tds = row.find_all('td')
            if not tds:
                continue

            # Extract split/category from split_id and split_value
            split_id_cell = row.find('td', {'data-stat': 'split_id'})
            split_value_cell = row.find('td', {'data-stat': 'split_value'})
            split_id = split_id_cell.get_text(strip=True) if split_id_cell else ''
            split_value = split_value_cell.get_text(strip=True) if split_value_cell else ''

            # Skip rows with no split/category
            if not split_id and not split_value:
                continue

            # Use split_id as the main category, fallback to split_value
            category = split_id if split_id else split_value

            # Extract stats based on table type
            stats_data = stats(row)

            # Only process if there are completions/attempts or other key stats
            if not any(stats_data.values()):
                continue

            # Create QBSplitStats object
            split_stat = QBSplitStats(
                player_id=qb_stat.player_id,
                player_name=qb_stat.player_name,
                team=qb_stat.team,
                season=qb_stat.season,
                split_type=split_type,
                split_category=category,
                games=self._safe_int(stats_data.get('games', 0)),
                completions=self._safe_int(stats_data.get('completions', 0)),
                attempts=self._safe_int(stats_data.get('attempts', 0)),
                completion_pct=self._safe_float(stats_data.get('completion_pct', 0)),
                pass_yards=self._safe_int(stats_data.get('pass_yards', 0)),
                pass_tds=self._safe_int(stats_data.get('pass_tds', 0)),
                interceptions=self._safe_int(stats_data.get('interceptions', 0)),
                rating=self._safe_float(stats_data.get('rating', 0)),
                sacks=self._safe_int(stats_data.get('sacks', 0)),
                sack_yards=self._safe_int(stats_data.get('sack_yards', 0)),
                net_yards_per_attempt=self._safe_float(stats_data.get('yards_per_attempt', 0)),
                scraped_at=current_time
            )
            splits.append(split_stat)

        return splits

    def _extract_basic_split_row_stats(self, row: Tag) -> Dict[str, str]:
        """Extract stats from the main stats table row (has more columns)"""
        stats = {}
        # Map of data-stat attributes to our field names for the main stats table
        # This table has 34 columns including rushing, scoring, fumbles, etc.
        stat_mapping = {
            'g': 'games',
            'wins': 'wins',
            'losses': 'losses',
            'ties': 'ties',
            'pass_cmp': 'completions',
            'pass_att': 'attempts',
            'pass_inc': 'incompletions',
            'pass_cmp_perc': 'completion_pct',
            'pass_yds': 'pass_yards',
            'pass_td': 'pass_tds',
            'pass_int': 'interceptions',
            'pass_rating': 'rating',
            'pass_sacked': 'sacks',
            'pass_sacked_yds': 'sack_yards',
            'pass_yds_per_att': 'yards_per_attempt',
            'pass_adj_yds_per_att': 'adjusted_yards_per_attempt',
            'pass_att_per_g': 'attempts_per_game',
            'pass_yds_per_g': 'yards_per_game',
            'rush_att': 'rush_attempts',
            'rush_yds': 'rush_yards',
            'rush_yds_per_att': 'rush_yards_per_attempt',
            'rush_td': 'rush_tds',
            'rush_att_per_g': 'rush_attempts_per_game',
            'rush_yds_per_g': 'rush_yards_per_game',
            'all_td': 'total_tds',
            'scoring': 'points',
            'fumbles': 'fumbles',
            'fumbles_lost': 'fumbles_lost',
            'fumbles_forced': 'fumbles_forced',
            'fumbles_rec': 'fumbles_recovered',
            'fumbles_rec_yds': 'fumble_recovery_yards',
            'fumbles_rec_td': 'fumble_recovery_tds'
        }
        for stat_attr, field_name in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            if cell:
                stats[field_name] = cell.get_text(strip=True)
        return stats

    def _extract_advanced_split_row_stats(self, row: Tag) -> Dict[str, str]:
        """Extract stats from an advanced split table row (fewer columns)"""
        stats = {}
        # Map of data-stat attributes to our field names for advanced splits table
        # This table has 20 columns, focused on passing and situational data
        stat_mapping = {
            'g': 'games',
            'pass_cmp': 'completions',
            'pass_att': 'attempts',
            'pass_cmp_perc': 'completion_pct',
            'pass_yds': 'pass_yards',
            'pass_td': 'pass_tds',
            'pass_int': 'interceptions',
            'pass_rating': 'rating',
            'pass_sacked': 'sacks',
            'pass_sacked_yds': 'sack_yards',
            'pass_yds_per_att': 'yards_per_attempt',
            'pass_adj_yds_per_att': 'adjusted_yards_per_attempt'
        }
        for stat_attr, field_name in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            if cell:
                stats[field_name] = cell.get_text(strip=True)
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
        """Safely convert value to float"""
        if value is None or value == '':
            return 0.0
        try:
            return float(str(value))
        except (ValueError, TypeError):
            return 0.0
    
    def save_to_database(self, qb_stats: List[QBBasicStats], all_splits_data: List[QBSplitStats]):
        """
        Save QB data to the database
        
        Args:
            qb_stats: List of QB main stats
            all_splits_data: List of all QB split statistics
        """
        try:
            # Save main QB stats
            logger.info(f"Saving {len(qb_stats)} QB main stats to database...")
            self.db_manager.insert_qb_stats(qb_stats)
            logger.info("Successfully saved QB main stats")
            
            # Save splits data
            if all_splits_data:
                logger.info(f"Saving {len(all_splits_data)} splits records to database...")
                self.db_manager.insert_qb_splits(all_splits_data)
                logger.info("Successfully saved QB splits data")
            else:
                logger.warning("No splits data to save")
                
        except Exception as e:
            logger.error(f"Error saving QB data to database: {e}")
            raise
    
    def scrape_single_qb(self, player_name: str) -> Optional[QBData]:
        """Scrape data for a single QB"""
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
            print(f"Games: {qb_data.main_stats.games_played}")
            print(f"Completions: {qb_data.main_stats.completions}/{qb_data.main_stats.attempts}")
            print(f"Yards: {qb_data.main_stats.pass_yards}")
            print(f"TDs: {qb_data.main_stats.pass_tds}")
            print(f"INTs: {qb_data.main_stats.interceptions}")
            print(f"Rating: {qb_data.main_stats.rating}")
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
            print(f"Games: {qb_data.main_stats.games_played}")
            print(f"Completions: {qb_data.main_stats.completions}/{qb_data.main_stats.attempts}")
            print(f"Yards: {qb_data.main_stats.pass_yards}")
            print(f"TDs: {qb_data.main_stats.pass_tds}")
            print(f"INTs: {qb_data.main_stats.interceptions}")
            print(f"Rating: {qb_data.main_stats.rating}")
            print(f"Splits Records: {len(qb_data.splits_data)}")

if __name__ == "__main__":
    main() 