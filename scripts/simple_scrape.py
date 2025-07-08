#!/usr/bin/env python3
"""
Simple standalone scraper for a single NFL QB player
No complex dependencies, just direct scraping and database operations
"""

import sys
import os
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, Any
import time
import re

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.qb_models import Player, QBBasicStats, QBAdvancedStats, QBSplitStats
from utils.data_utils import generate_player_id, extract_pfr_id, clean_player_name
from database.db_manager import DatabaseManager

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/simple_scrape.log'),
            logging.StreamHandler()
        ]
    )

def find_player_url(player_name: str) -> Optional[str]:
    """Find player's PFR URL by searching"""
    logger = logging.getLogger(__name__)
    
    # Clean player name
    clean_name = clean_player_name(player_name)
    
    # Try to construct URL directly first
    # Extract first letter of last name and create player code
    name_parts = clean_name.split()
    if len(name_parts) >= 2:
        last_name = name_parts[-1]
        first_name = name_parts[0]
        
        # Create player code (first 4 letters of last name + first 2 letters of first name + 01)
        player_code = f"{last_name[:4].lower()}{first_name[:2].lower()}01"
        first_letter = last_name[0].upper()
        
        # Try the constructed URL
        url = f"https://www.pro-football-reference.com/players/{first_letter}/{player_code}.htm"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Check if this is actually the right player
                title = soup.find('title')
                if title and clean_name.lower() in title.text.lower():
                    logger.info(f"Found player URL: {url}")
                    return url
        except Exception as e:
            logger.warning(f"Error checking constructed URL: {e}")
    
    # If direct construction fails, we'll need to implement search
    # For now, return None and let the user provide the URL
    logger.warning(f"Could not find URL for {player_name}. You may need to provide the PFR URL manually.")
    return None

def scrape_basic_stats(pfr_id: str, player_name: str, season: int) -> Optional[QBBasicStats]:
    """Scrape basic stats for a player in a specific season"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get the main stats page for the season
        stats_url = f"https://www.pro-football-reference.com/years/{season}/passing.htm"
        response = requests.get(stats_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the stats table
        table = soup.find('table', {'id': 'stats_passing'})
        if not table:
            logger.error("Could not find passing stats table")
            return None
        
        # Parse the table
        df = pd.read_html(str(table))[0]
        
        # Find the player's row
        player_row = None
        for _, row in df.iterrows():
            if clean_player_name(row.get('Player', '')) == clean_player_name(player_name):
                player_row = row
                break
        
        if player_row is None:
            logger.warning(f"Could not find {player_name} in {season} stats")
            return None
        
        # Create basic stats object
        basic_stats = QBBasicStats(
            pfr_id=pfr_id,
            season=season,
            team=player_row.get('Tm', ''),
            games_played=int(player_row.get('G', 0)),
            games_started=int(player_row.get('GS', 0)),
            completions=int(player_row.get('Cmp', 0)),
            attempts=int(player_row.get('Att', 0)),
            completion_pct=float(player_row.get('Cmp%', 0)) if player_row.get('Cmp%') else None,
            pass_yards=int(player_row.get('Yds', 0)),
            pass_tds=int(player_row.get('TD', 0)),
            interceptions=int(player_row.get('Int', 0)),
            longest_pass=int(player_row.get('Lng', 0)),
            rating=float(player_row.get('Rate', 0)) if player_row.get('Rate') else None,
            sacks=int(player_row.get('Sk', 0)),
            sack_yards=int(player_row.get('Yds.1', 0)),
            net_yards_per_attempt=float(player_row.get('NY/A', 0)) if player_row.get('NY/A') else None,
            scraped_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        logger.info(f"Scraped basic stats for {player_name}: {basic_stats.pass_yards} yards, {basic_stats.pass_tds} TDs")
        return basic_stats
        
    except Exception as e:
        logger.error(f"Error scraping basic stats: {e}")
        return None

def scrape_advanced_stats(pfr_id: str, player_name: str, season: int) -> Optional[QBAdvancedStats]:
    """Scrape advanced stats for a player in a specific season"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get the advanced stats page for the season
        stats_url = f"https://www.pro-football-reference.com/years/{season}/passing_advanced.htm"
        response = requests.get(stats_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the stats table
        table = soup.find('table', {'id': 'advanced_passing'})
        if not table:
            logger.warning("Could not find advanced passing stats table")
            return None
        
        # Parse the table
        df = pd.read_html(str(table))[0]
        
        # Find the player's row
        player_row = None
        for _, row in df.iterrows():
            if clean_player_name(row.get('Player', '')) == clean_player_name(player_name):
                player_row = row
                break
        
        if player_row is None:
            logger.warning(f"Could not find {player_name} in {season} advanced stats")
            return None
        
        # Create advanced stats object
        advanced_stats = QBAdvancedStats(
            pfr_id=pfr_id,
            season=season,
            qbr=float(player_row.get('QBR', 0)) if player_row.get('QBR') else None,
            adjusted_net_yards_per_attempt=float(player_row.get('ANY/A', 0)) if player_row.get('ANY/A') else None,
            fourth_quarter_comebacks=int(player_row.get('4QC', 0)),
            game_winning_drives=int(player_row.get('GWD', 0)),
            scraped_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        logger.info(f"Scraped advanced stats for {player_name}: QBR={advanced_stats.qbr}")
        return advanced_stats
        
    except Exception as e:
        logger.error(f"Error scraping advanced stats: {e}")
        return None

def scrape_splits(pfr_id: str, player_name: str, season: int, player_url: str) -> list[QBSplitStats]:
    """Scrape splits data for a player"""
    logger = logging.getLogger(__name__)
    
    splits = []
    
    try:
        # Get the splits page
        splits_url = f"{player_url.replace('.htm', '')}/splits/{season}/"
        response = requests.get(splits_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables that look like splits tables
        tables = soup.find_all('table')
        
        for table in tables:
            table_id = table.get('id', '')
            if 'splits' in table_id.lower():
                try:
                    # Parse the table
                    df = pd.read_html(str(table))[0]
                    
                    # Find the player's row
                    player_row = None
                    for _, row in df.iterrows():
                        if clean_player_name(row.get('Player', '')) == clean_player_name(player_name):
                            player_row = row
                            break
                    
                    if player_row is not None:
                        # Determine split type and category from table context
                        split_type = "basic_splits"
                        split_category = "unknown"
                        
                        # Try to find the category from the table
                        caption = table.find('caption')
                        if caption:
                            caption_text = caption.text.lower()
                            if 'home' in caption_text or 'away' in caption_text:
                                split_type = "location_splits"
                                split_category = "home" if 'home' in caption_text else "away"
                            elif 'quarter' in caption_text:
                                split_type = "quarter_splits"
                                split_category = caption_text.split()[0]  # e.g., "1st", "2nd"
                        
                        # Create split stats object
                        split_stats = QBSplitStats(
                            pfr_id=pfr_id,
                            season=season,
                            split_type=split_type,
                            split_category=split_category,
                            games=int(player_row.get('G', 0)),
                            completions=int(player_row.get('Cmp', 0)),
                            attempts=int(player_row.get('Att', 0)),
                            completion_pct=float(player_row.get('Cmp%', 0)) if player_row.get('Cmp%') else None,
                            pass_yards=int(player_row.get('Yds', 0)),
                            pass_tds=int(player_row.get('TD', 0)),
                            interceptions=int(player_row.get('Int', 0)),
                            rating=float(player_row.get('Rate', 0)) if player_row.get('Rate') else None,
                            sacks=int(player_row.get('Sk', 0)),
                            sack_yards=int(player_row.get('Yds.1', 0)),
                            net_yards_per_attempt=float(player_row.get('NY/A', 0)) if player_row.get('NY/A') else None,
                            scraped_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        
                        splits.append(split_stats)
                        logger.info(f"Found split: {split_type} - {split_category}")
                        
                except Exception as e:
                    logger.warning(f"Error processing splits table {table_id}: {e}")
                    continue
        
        logger.info(f"Found {len(splits)} splits for {player_name}")
        return splits
        
    except Exception as e:
        logger.error(f"Error scraping splits: {e}")
        return []

def scrape_single_player(player_name: str, season: int, save_to_db: bool = True) -> dict:
    """
    Scrape data for a single player
    
    Args:
        player_name: Full name of the player (e.g., "Joe Burrow")
        season: Season year to scrape
        save_to_db: Whether to save data to database
        
    Returns:
        Dictionary with scraping results
    """
    logger = logging.getLogger(__name__)
    
    # Initialize database manager if saving
    db_manager = None
    if save_to_db:
        db_manager = DatabaseManager()
        db_manager.create_tables()
    
    results = {
        'player_name': player_name,
        'season': season,
        'success': False,
        'player': None,
        'basic_stats': None,
        'advanced_stats': None,
        'splits': [],
        'errors': [],
        'warnings': []
    }
    
    try:
        logger.info(f"Starting scrape for {player_name} ({season} season)")
        
        # Step 1: Find player URL and generate PFR ID
        logger.info("Finding player URL...")
        player_url = find_player_url(player_name)
        if not player_url:
            error_msg = f"Could not find PFR URL for {player_name}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        pfr_id = generate_player_id(player_name, player_url)
        logger.info(f"Found PFR ID: {pfr_id}")
        logger.info(f"Player URL: {player_url}")
        
        # Step 2: Create Player object
        player = Player(
            pfr_id=pfr_id,
            player_name=clean_player_name(player_name),
            pfr_url=player_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        results['player'] = player
        
        # Step 3: Scrape basic stats
        logger.info("Scraping basic stats...")
        basic_stats = scrape_basic_stats(pfr_id, player_name, season)
        if basic_stats:
            results['basic_stats'] = basic_stats
        else:
            results['warnings'].append("Could not scrape basic stats")
        
        # Step 4: Scrape advanced stats
        logger.info("Scraping advanced stats...")
        advanced_stats = scrape_advanced_stats(pfr_id, player_name, season)
        if advanced_stats:
            results['advanced_stats'] = advanced_stats
        else:
            results['warnings'].append("Could not scrape advanced stats")
        
        # Step 5: Scrape splits data
        logger.info("Scraping splits data...")
        splits = scrape_splits(pfr_id, player_name, season, player_url)
        results['splits'] = splits
        
        # Step 6: Save to database if requested
        if save_to_db and db_manager:
            logger.info("Saving data to database...")
            try:
                # Insert player
                db_manager.insert_player(player)
                
                # Insert basic stats
                if results['basic_stats']:
                    db_manager.insert_qb_basic_stats([results['basic_stats']])
                
                # Insert advanced stats
                if results['advanced_stats']:
                    db_manager.insert_qb_advanced_stats([results['advanced_stats']])
                
                # Insert splits
                if results['splits']:
                    db_manager.insert_qb_splits(results['splits'])
                
                logger.info("Data saved to database successfully")
                
            except Exception as e:
                error_msg = f"Error saving to database: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Step 7: Print results
        print(f"\n=== SCRAPING RESULTS FOR {player_name.upper()} ({season}) ===")
        print(f"PFR ID: {pfr_id}")
        print(f"Player URL: {player_url}")
        
        if results['basic_stats']:
            stats = results['basic_stats']
            print(f"\nBasic Stats:")
            print(f"  Team: {stats.team}")
            print(f"  Games: {stats.games_played} played, {stats.games_started} started")
            print(f"  Passing: {stats.completions}/{stats.attempts} ({stats.completion_pct}%)")
            print(f"  Yards: {stats.pass_yards}, TDs: {stats.pass_tds}, INTs: {stats.interceptions}")
            print(f"  Rating: {stats.rating}")
        
        if results['advanced_stats']:
            adv = results['advanced_stats']
            print(f"\nAdvanced Stats:")
            print(f"  QBR: {adv.qbr}")
            print(f"  ANY/A: {adv.adjusted_net_yards_per_attempt}")
            print(f"  4QC: {adv.fourth_quarter_comebacks}, GWD: {adv.game_winning_drives}")
        
        print(f"\nSplits Found: {len(results['splits'])}")
        for split in results['splits'][:5]:  # Show first 5 splits
            print(f"  {split.split_type} - {split.split_category}")
        if len(results['splits']) > 5:
            print(f"  ... and {len(results['splits']) - 5} more")
        
        if results['warnings']:
            print(f"\nWarnings ({len(results['warnings'])}):")
            for warning in results['warnings'][:3]:
                print(f"  {warning}")
        
        if results['errors']:
            print(f"\nErrors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  {error}")
        
        results['success'] = len(results['errors']) == 0
        logger.info(f"Scraping completed for {player_name}")
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
        results['success'] = False
    
    finally:
        if db_manager:
            db_manager.close()
    
    return results

def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python simple_scrape.py \"Player Name\" [season] [--no-db]")
        print("Examples:")
        print("  python simple_scrape.py \"Joe Burrow\" 2024")
        print("  python simple_scrape.py \"Patrick Mahomes\" 2023 --no-db")
        sys.exit(1)
    
    player_name = sys.argv[1]
    season = int(sys.argv[2]) if len(sys.argv) > 2 else 2024
    save_to_db = "--no-db" not in sys.argv
    
    setup_logging()
    
    print(f"Simple Scrape - {player_name} ({season} season)")
    print("=" * 50)
    
    results = scrape_single_player(player_name, season, save_to_db)
    
    if results['success']:
        print(f"\n🎉 SUCCESS! Scraped data for {player_name}")
        print(f"📊 Found {len(results['splits'])} splits")
        if save_to_db:
            print("💾 Data saved to database")
        else:
            print("📝 Data scraped but not saved (--no-db flag)")
    else:
        print(f"\n❌ FAILED to scrape data for {player_name}")
        print("Check the logs for details")
    
    return results['success']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 