#!/usr/bin/env python3
"""
NFL QB Data Scraper for 2024 Season

This script scrapes QB data from Pro Football Reference for the 2024 season:
1. Scrapes main passing stats for QBs only (filters by position)
2. Extracts QB URLs from the main table
3. Scrapes splits data for each QB from their individual pages
4. Stores all data in the PostgreSQL database

Usage:
    python scripts/scrape_qb_data_2024.py
"""

import asyncio
import logging
import sys
import os
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.config import config
from database.db_manager import DatabaseManager
from models.qb_models import QBBasicStats, QBSplitStats
from scrapers.enhanced_scraper import EnhancedPFRScraper
from utils.data_utils import normalize_pfr_team_code

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG to see more detailed information
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qb_scraping_2024.log'),
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

class QBDataScraper2024:
    """Scraper specifically for 2024 QB data with QB-only filtering"""
    
    def __init__(self):
        """Initialize the scraper with configuration"""
        self.config = config
        self.db_manager = DatabaseManager(config.get_database_url())
        self.scraper = EnhancedPFRScraper(rate_limit_delay=config.get_rate_limit_delay())  # Use config rate limit delay
        self.season = 2024
        self.base_url = "https://www.pro-football-reference.com"
        
    def scrape_qb_main_stats(self) -> List[QBBasicStats]:
        """
        Scrape main QB statistics for 2024 season, filtering for QBs only
        
        Returns:
            List of QBBasicStats objects for QBs only
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
                
                # Extract team
                team_cell = row.find('td', {'data-stat': 'team_name_abbr'})  # type: ignore
                team = normalize_pfr_team_code(team_cell.get_text(strip=True) if team_cell else '')  # type: ignore
                
                # Extract basic stats
                stats = self._extract_row_stats(cast(Tag, row))
                
                # Create QBBasicStats object with player URL
                # Generate unique PFR ID for multi-team players
                base_pfr_id = self._generate_player_id(player_name)
                if team and ('2TM' in team or '3TM' in team or len(team) == 3):
                    pfr_id = f"{base_pfr_id}_{team.lower()}"
                else:
                    pfr_id = base_pfr_id
                
                qb_stat = QBBasicStats(
                    pfr_id=pfr_id,
                    player_name=player_name,
                    player_url=player_url,
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
                    sacks=self._safe_int(stats.get('sacks', 0)),
                    sack_yards=self._safe_int(stats.get('sack_yards', 0)),
                    net_yards_per_attempt=self._safe_float(stats.get('net_yards_per_attempt', 0)),
                    scraped_at=current_time
                )
                
                # Store the player URL for later use
                qb_stat.player_url = player_url
                
                qb_stats.append(qb_stat)
                logger.info(f"Extracted QB stats for {player_name} ({team})")
                
            except Exception as e:
                logger.error(f"Error processing QB row: {e}")
                continue
        
        logger.info(f"Successfully extracted stats for {len(qb_stats)} QBs")
        
        # Save the collected URLs for verification
        self._save_player_urls(qb_stats)
        
        return qb_stats
    
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
            'pass_sacked_pct': 'sack_pct',
            'pass_td_pct': 'touchdown_pct',
            'pass_int_pct': 'interception_pct',
            'pass_first_down': 'first_downs',
            'pass_success': 'success_rate',
            'pass_long': 'longest_pass',
            'comeback': 'comebacks',
            'gwd': 'game_winning_drives',
            'qb_rec': 'qb_record',
            'awards': 'awards'
        }
        
        for stat_attr, field_name in stat_mapping.items():
            cell = row.find('td', {'data-stat': stat_attr})  # type: ignore
            if cell:
                stats[field_name] = cell.get_text(strip=True)  # type: ignore
        
        return stats
    
    def _generate_player_id(self, player_name: str) -> str:
        """Generate a unique player ID from name"""
        # Simple ID generation - in production, you might want a more robust approach
        return player_name.lower().replace(' ', '_').replace('.', '')[:20]
    
    def _safe_int(self, value: Union[str, int, float, None]) -> int:
        """Safely convert value to integer"""
        try:
            if value is None:
                return 0
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                return int(value) if value.strip() else 0
            return 0
        except (ValueError, TypeError):
            return 0
    
    def _safe_float(self, value: Union[str, int, float, None]) -> float:
        """Safely convert value to float"""
        try:
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                return float(value) if value.strip() else 0.0
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _save_player_urls(self, qb_stats: List[QBBasicStats]):
        """Save collected player URLs to a file for verification"""
        try:
            filename = f"player_urls_{self.season}.txt"
            with open(filename, 'w') as f:
                f.write(f"# Player URLs collected for {self.season} season\n")
                f.write(f"# Total QBs: {len(qb_stats)}\n")
                f.write(f"# Generated: {datetime.now()}\n\n")
                
                for qb in qb_stats:
                    if hasattr(qb, 'player_url') and qb.player_url:
                        f.write(f"{qb.player_name} ({qb.team}): {qb.player_url}\n")
                    else:
                        f.write(f"{qb.player_name} ({qb.team}): NO URL\n")
            
            logger.info(f"Saved {len(qb_stats)} player URLs to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving player URLs: {e}")
    
    def _load_player_urls(self, filename: str) -> Dict[str, str]:
        """Load player URLs from a saved file"""
        urls = {}
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ': ' in line:
                            player_info, url = line.rsplit(': ', 1)
                            if url != 'NO URL':
                                urls[player_info] = url
            
            logger.info(f"Loaded {len(urls)} player URLs from {filename}")
            return urls
            
        except Exception as e:
            logger.error(f"Error loading player URLs: {e}")
            return {}
    
    def scrape_qb_splits(self, qb_stats: List[QBBasicStats]) -> List[QBSplitStats]:
        """
        Scrape splits data for each QB using collected URLs
        
        Args:
            qb_stats: List of QBBasicStats objects with player URLs
            
        Returns:
            List of QBSplitStats objects
        """
        logger.info(f"Starting splits scraping for {len(qb_stats)} QBs")
        
        # Collect all valid player URLs
        valid_qbs = [qb for qb in qb_stats if hasattr(qb, 'player_url') and qb.player_url]
        logger.info(f"Found {len(valid_qbs)} QBs with valid URLs for splits scraping")
        
        if not valid_qbs:
            logger.warning("No valid player URLs found for splits scraping")
            return []
        
        # Log the URLs we'll be scraping
        logger.info("Player URLs to scrape splits from:")
        for qb in valid_qbs[:5]:  # Show first 5 for logging
            logger.info(f"  - {qb.player_name}: {qb.player_url}")
        if len(valid_qbs) > 5:
            logger.info(f"  ... and {len(valid_qbs) - 5} more")
        
        all_splits = []
        successful_scrapes = 0
        failed_scrapes = 0
        
        for i, qb_stat in enumerate(valid_qbs, 1):
            try:
                logger.info(f"Scraping splits for {qb_stat.player_name} ({i}/{len(valid_qbs)})")
                
                # Convert player URL to splits URL
                if qb_stat.player_url:
                    splits_url = qb_stat.player_url.replace('.htm', f'/splits/{self.season}/')
                    logger.info(f"  Splits URL: {splits_url}")
                    
                    # Scrape splits for this player
                    splits = self.scraper.scrape_player_splits(
                        splits_url, 
                        qb_stat.pfr_id, 
                        qb_stat.player_name, 
                        qb_stat.team, 
                        self.season, 
                        datetime.now()
                    )
                    
                    all_splits.extend(splits)
                    successful_scrapes += 1
                    logger.info(f"  ✓ Scraped {len(splits)} splits for {qb_stat.player_name}")
                else:
                    logger.warning(f"  No player URL for {qb_stat.player_name}")
                    failed_scrapes += 1
                
                # Rate limiting - 5 second base + 0-5 second random variation
                random_delay = random.uniform(0, 5)
                total_delay = 5 + random_delay
                logger.info(f"  Rate limiting: {total_delay:.1f}s delay (5s base + {random_delay:.1f}s random)")
                time.sleep(total_delay)
                
            except Exception as e:
                failed_scrapes += 1
                logger.error(f"  ✗ Error scraping splits for {qb_stat.player_name}: {e}")
                continue
        
        logger.info(f"Splits scraping completed:")
        logger.info(f"  - Successful: {successful_scrapes}/{len(valid_qbs)}")
        logger.info(f"  - Failed: {failed_scrapes}/{len(valid_qbs)}")
        logger.info(f"  - Total splits records: {len(all_splits)}")
        
        return all_splits
    
    def save_to_database(self, qb_stats: List[QBBasicStats], splits_data: List[QBSplitStats]):
        """Save all data to database"""
        logger.info("Saving data to database...")
        
        try:
            # Save main QB stats
            if qb_stats:
                self.db_manager.insert_qb_basic_stats(qb_stats)
                logger.info(f"Saved {len(qb_stats)} QB stats records")
            
            # Save splits data
            if splits_data:
                self.db_manager.insert_qb_splits(splits_data)
                logger.info(f"Saved {len(splits_data)} QB splits records")
            
            logger.info("Database save completed successfully")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            raise
    
    def run_complete_scrape(self):
        """Run the complete scraping process"""
        logger.info("Starting complete QB data scrape for 2024 season")
        
        try:
            # Step 1: Scrape main QB stats
            logger.info("Step 1: Scraping main QB stats...")
            qb_stats = self.scrape_qb_main_stats()
            
            if not qb_stats:
                logger.error("No QB stats found. Exiting.")
                return
            
            # Step 2: Scrape splits data
            logger.info("Step 2: Scraping QB splits...")
            splits_data = self.scrape_qb_splits(qb_stats)
            
            # Step 3: Save to database
            logger.info("Step 3: Saving to database...")
            self.save_to_database(qb_stats, splits_data)
            
            logger.info("Complete QB data scrape finished successfully!")
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise

def main():
    """Main entry point"""
    scraper = QBDataScraper2024()
    scraper.run_complete_scrape()

if __name__ == "__main__":
    main() 