#!/usr/bin/env python3
"""
Joe Burrow Data Scraper for 2024 Season

This script scrapes Joe Burrow's QB data from Pro Football Reference for the 2024 season:
1. Scrapes main passing stats for Joe Burrow only
2. Extracts Joe Burrow's URL from the main table
3. Scrapes splits data for Joe Burrow from his individual page
4. Stores all data in the PostgreSQL database (Supabase)

Usage:
    python scripts/scrape_joe_burrow.py
"""

import asyncio
import logging
import sys
import random
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
sys.path.append('src')

from config.config import config
from database.db_manager import DatabaseManager
from models.qb_models import QBStats, QBSplitStats
from scrapers.enhanced_scraper import EnhancedPFRScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('joe_burrow_scraping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QBData:
    """Container for QB data including main stats and splits"""
    main_stats: QBStats
    splits_data: List[QBSplitStats]
    player_url: str

class JoeBurrowScraper:
    """Scraper specifically for Joe Burrow's 2024 data"""
    
    def __init__(self):
        """Initialize the scraper with configuration"""
        self.config = config
        self.db_manager = DatabaseManager(config.get_database_url())
        self.scraper = EnhancedPFRScraper(rate_limit_delay=3.0)  # 3 second delay between requests
        self.season = 2024
        self.base_url = "https://www.pro-football-reference.com"
        self.target_player = "Joe Burrow"
        
    def scrape_joe_burrow_main_stats(self) -> Optional[QBStats]:
        """
        Scrape Joe Burrow's main QB statistics for 2024 season
        
        Returns:
            QBStats object for Joe Burrow or None if not found
        """
        url = f"{self.base_url}/years/{self.season}/passing.htm"
        logger.info(f"Scraping Joe Burrow's main stats for {self.season} season from {url}")
        
        response = self.scraper.make_request_with_retry(url)
        if not response:
            logger.error("Failed to fetch main passing page")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main passing table
        table = soup.find('table', {'id': 'passing'})  # type: ignore
        if not table:
            logger.error("Could not find passing table")
            return None
        
        current_time = datetime.now()
        
        # Find all rows in the table body
        tbody = table.find('tbody')  # type: ignore
        if not tbody:
            logger.error("Could not find table body")
            return None
        
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
                
                # Only process Joe Burrow
                if player_name != self.target_player:
                    continue
                
                href = name_link.get('href', '')  # type: ignore
                player_url = self.base_url + str(href) if href else ''
                
                # Extract team
                team_cell = row.find('td', {'data-stat': 'team_name_abbr'})  # type: ignore
                team = team_cell.get_text(strip=True) if team_cell else ''  # type: ignore
                
                # Extract basic stats
                stats = self._extract_row_stats(cast(Tag, row))
                
                # Create QBStats object with player URL
                qb_stat = QBStats(
                    player_id=self._generate_player_id(player_name),
                    player_name=player_name,
                    team=team,
                    season=self.season,
                    games_played=self._safe_int(stats.get('games', 0)),
                    games_started=self._safe_int(stats.get('games_started', 0)),
                    completions=self._safe_int(stats.get('completions', 0)),
                    attempts=self._safe_int(stats.get('attempts', 0)),
                    completion_pct=self._safe_float(stats.get('completion_pct', 0)),
                    pass_yards=self._safe_int(stats.get('yards', 0)),
                    pass_tds=self._safe_int(stats.get('touchdowns', 0)),
                    interceptions=self._safe_int(stats.get('interceptions', 0)),
                    longest_pass=self._safe_int(stats.get('longest_pass', 0)),
                    rating=self._safe_float(stats.get('rating', 0)),
                    qbr=None,  # QBR not available in basic stats
                    sacks=self._safe_int(stats.get('sacks', 0)),
                    sack_yards=self._safe_int(stats.get('sack_yards', 0)),
                    net_yards_per_attempt=self._safe_float(stats.get('net_yards_per_attempt', 0)),
                    adjusted_net_yards_per_attempt=self._safe_float(stats.get('adjusted_net_yards_per_attempt', 0)),
                    fourth_quarter_comebacks=self._safe_int(stats.get('comebacks', 0)),
                    game_winning_drives=self._safe_int(stats.get('game_winning_drives', 0)),
                    scraped_at=current_time
                )
                
                # Store the player URL for later use
                qb_stat.player_url = player_url
                
                logger.info(f"Found Joe Burrow's stats: {player_name} ({team}) - {qb_stat.games_played} games")
                return qb_stat
                
            except Exception as e:
                logger.error(f"Error processing QB row: {e}")
                continue
        
        logger.error(f"Could not find Joe Burrow in the 2024 passing stats")
        return None
    
    def _extract_row_stats(self, row: Tag) -> Dict[str, str]:
        """Extract all stats from a table row"""
        stats = {}
        
        # Map of data-stat attributes to our field names
        stat_mapping = {
            'games': 'games',
            'games_started': 'games_started',
            'pass_cmp': 'completions',
            'pass_att': 'attempts',
            'pass_cmp_pct': 'completion_pct',
            'pass_yds': 'yards',
            'pass_td': 'touchdowns',
            'pass_int': 'interceptions',
            'pass_rating': 'rating',
            'pass_sacked': 'sacks',
            'pass_sacked_yds': 'sack_yards',
            'pass_yds_per_att': 'yards_per_attempt',
            'pass_yds_per_cmp': 'yards_per_completion',
            'pass_yds_per_g': 'yards_per_game',
            'pass_adj_yds_per_att': 'adjusted_yards_per_attempt',
            'pass_net_yds_per_att': 'net_yards_per_attempt',
            'pass_adj_net_yds_per_att': 'adjusted_net_yards_per_attempt',
            'pass_long': 'longest_pass',
            'comebacks': 'comebacks',
            'game_winning_drives': 'game_winning_drives'
        }
        
        for stat_attr, field_name in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            if cell:
                stats[field_name] = cell.get_text(strip=True)
        
        return stats
    
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
    
    def scrape_joe_burrow_splits(self, qb_stat: QBStats) -> List[QBSplitStats]:
        """
        Scrape Joe Burrow's splits data from his individual page
        
        Args:
            qb_stat: QBStats object containing Joe Burrow's main stats and URL
            
        Returns:
            List of QBSplitStats objects
        """
        if not qb_stat.player_url:
            logger.error("No player URL available for Joe Burrow")
            return []
        
        logger.info(f"Scraping Joe Burrow's splits from: {qb_stat.player_url}")
        
        response = self.scraper.make_request_with_retry(qb_stat.player_url)
        if not response:
            logger.error("Failed to fetch Joe Burrow's player page")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all splits tables
        splits_tables = soup.find_all('table', {'id': re.compile(r'splits.*')})
        logger.info(f"Found {len(splits_tables)} splits tables for Joe Burrow")
        
        all_splits = []
        current_time = datetime.now()
        
        for table in splits_tables:
            try:
                table_splits = self._process_splits_table(cast(Tag, table), qb_stat, current_time)
                all_splits.extend(table_splits)
                table_id = table.get('id', 'unknown') if hasattr(table, 'get') else 'unknown'
                logger.info(f"Processed {len(table_splits)} splits from table {table_id}")
            except Exception as e:
                table_id = table.get('id', 'unknown') if hasattr(table, 'get') else 'unknown'
                logger.error(f"Error processing splits table {table_id}: {e}")
                continue
        
        logger.info(f"Total splits extracted for Joe Burrow: {len(all_splits)}")
        return all_splits
    
    def _process_splits_table(self, table: Tag, qb_stat: QBStats, current_time: datetime) -> List[QBSplitStats]:
        """Process a single splits table and extract split statistics"""
        splits = []
        
        # Get table ID to determine split type
        table_id = str(table.get('id', ''))
        split_type = self._determine_split_type(table_id)
        
        # Find all rows in the table
        rows = table.find_all('tr')
        
        for row in rows:
            try:
                # Skip header rows
                if cast(Tag, row).find('th'):
                    continue
                
                # Extract category name
                category_cell = cast(Tag, row).find('td', {'data-stat': 'split_value'})
                if not category_cell:
                    continue
                
                category = category_cell.get_text(strip=True)
                if not category or category == 'Split':
                    continue
                
                # Extract stats
                stats = self._extract_split_row_stats(cast(Tag, row))
                
                # Create QBSplitStats object
                split_stat = QBSplitStats(
                    player_id=qb_stat.player_id,
                    player_name=qb_stat.player_name,
                    team=qb_stat.team,
                    season=qb_stat.season,
                    split_type=split_type,
                    split_category=category,
                    games=self._safe_int(stats.get('games', 0)),
                    completions=self._safe_int(stats.get('completions', 0)),
                    attempts=self._safe_int(stats.get('attempts', 0)),
                    completion_pct=self._safe_float(stats.get('completion_pct', 0)),
                    pass_yards=self._safe_int(stats.get('yards', 0)),
                    pass_tds=self._safe_int(stats.get('touchdowns', 0)),
                    interceptions=self._safe_int(stats.get('interceptions', 0)),
                    rating=self._safe_float(stats.get('rating', 0)),
                    sacks=self._safe_int(stats.get('sacks', 0)),
                    sack_yards=self._safe_int(stats.get('sack_yards', 0)),
                    net_yards_per_attempt=self._safe_float(stats.get('net_yards_per_attempt', 0)),
                    scraped_at=current_time
                )
                
                splits.append(split_stat)
                
            except Exception as e:
                logger.error(f"Error processing split row: {e}")
                continue
        
        return splits
    
    def _determine_split_type(self, table_id: str) -> str:
        """Determine split type from table ID"""
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
    
    def _extract_split_row_stats(self, row: Tag) -> Dict[str, str]:
        """Extract stats from a split table row"""
        stats = {}
        
        # Map of data-stat attributes to our field names
        stat_mapping = {
            'games': 'games',
            'games_started': 'games_started',
            'pass_cmp': 'completions',
            'pass_att': 'attempts',
            'pass_cmp_pct': 'completion_pct',
            'pass_yds': 'yards',
            'pass_td': 'touchdowns',
            'pass_int': 'interceptions',
            'pass_rating': 'rating',
            'pass_sacked': 'sacks',
            'pass_sacked_yds': 'sack_yards',
            'pass_net_yds_per_att': 'net_yards_per_attempt',
            'pass_adj_net_yds_per_att': 'adjusted_net_yards_per_attempt'
        }
        
        for stat_attr, field_name in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})
            if cell:
                stats[field_name] = cell.get_text(strip=True)
        
        return stats
    
    def save_to_database(self, qb_stat: QBStats, splits_data: List[QBSplitStats]):
        """
        Save Joe Burrow's data to the database
        
        Args:
            qb_stat: Joe Burrow's main QB stats
            splits_data: List of Joe Burrow's split statistics
        """
        try:
            # Save main QB stats
            logger.info("Saving Joe Burrow's main stats to database...")
            self.db_manager.insert_qb_stats([qb_stat])
            logger.info("Successfully saved Joe Burrow's main stats")
            
            # Save splits data
            if splits_data:
                logger.info(f"Saving {len(splits_data)} splits records to database...")
                self.db_manager.insert_qb_splits(splits_data)
                logger.info("Successfully saved Joe Burrow's splits data")
            else:
                logger.warning("No splits data to save")
                
        except Exception as e:
            logger.error(f"Error saving Joe Burrow's data to database: {e}")
            raise
    
    def run_joe_burrow_scrape(self):
        """Run the complete Joe Burrow scraping process"""
        logger.info("Starting Joe Burrow data scraping process...")
        
        try:
            # Step 1: Scrape Joe Burrow's main stats
            qb_stat = self.scrape_joe_burrow_main_stats()
            if not qb_stat:
                logger.error("Failed to scrape Joe Burrow's main stats")
                return
            
            logger.info(f"Successfully scraped Joe Burrow's main stats: {qb_stat.player_name} ({qb_stat.team})")
            
            # Step 2: Scrape Joe Burrow's splits data
            splits_data = self.scrape_joe_burrow_splits(qb_stat)
            logger.info(f"Successfully scraped {len(splits_data)} splits records for Joe Burrow")
            
            # Step 3: Save to database
            self.save_to_database(qb_stat, splits_data)
            
            logger.info("Joe Burrow data scraping completed successfully!")
            
            # Print summary
            print(f"\n=== Joe Burrow 2024 Data Summary ===")
            print(f"Player: {qb_stat.player_name}")
            print(f"Team: {qb_stat.team}")
            print(f"Games Played: {qb_stat.games_played}")
            print(f"Completions: {qb_stat.completions}/{qb_stat.attempts}")
            print(f"Passing Yards: {qb_stat.pass_yards}")
            print(f"Touchdowns: {qb_stat.pass_tds}")
            print(f"Interceptions: {qb_stat.interceptions}")
            print(f"Rating: {qb_stat.rating}")
            print(f"Splits Records: {len(splits_data)}")
            
        except Exception as e:
            logger.error(f"Error during Joe Burrow scraping process: {e}")
            raise

def main():
    """Main function to run Joe Burrow scraper"""
    scraper = JoeBurrowScraper()
    scraper.run_joe_burrow_scrape()

if __name__ == "__main__":
    main() 