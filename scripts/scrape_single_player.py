#!/usr/bin/env python3
"""
Simple script to scrape data for a single NFL QB player
Usage: python scrape_single_player.py "Joe Burrow" 2024
"""

import sys
import os
import logging
from datetime import datetime
from typing import Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.enhanced_scraper import EnhancedPFRScraper
from models.qb_models import Player, QBBasicStats, QBAdvancedStats, QBSplitStats
from utils.data_utils import generate_player_id, extract_pfr_id, clean_player_name
from database.db_manager import DatabaseManager

def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0

def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/single_player_scraping.log'),
            logging.StreamHandler()
        ]
    )

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
    
    # Initialize scraper
    scraper = EnhancedPFRScraper(rate_limit_delay=2.0)  # Be respectful with rate limiting
    
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
        player_url = scraper.find_player_url(player_name)
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
        
        # Validate player
        player_errors = player.validate()
        if player_errors:
            for error in player_errors:
                results['warnings'].append(f"Player validation: {error}")
        
        results['player'] = player
        
        # Step 3: Scrape basic stats (season totals)
        logger.info("Scraping basic stats...")
        try:
            # Get the main stats page for the season
            stats_url = f"{scraper.base_url}/years/{season}/passing.htm"
            response = scraper.make_request_with_retry(stats_url)
            
            if response:
                from bs4 import BeautifulSoup
                import pandas as pd
                
                soup = BeautifulSoup(response.content, 'html.parser')
                # Try both possible table IDs for 2024
                # Use pandas directly for main stats table (simpler structure)
                table = soup.find('table', {'id': 'stats_passing'})
                if not table:
                    table = soup.find('table', {'id': 'passing'})
                
                if table:
                    df = pd.read_html(str(table))[0]
                else:
                    df = None
                
                # --- NEW: Extract team code from the Team column (2024 table) ---
                team_code = None
                player_row = None
                if df is not None:
                    for _, row in df.iterrows():
                        if clean_player_name(row.get('Player', '')) == player.player_name:
                            player_row = row
                            team_val = row.get('Team', '')
                            if isinstance(team_val, str) and team_val.strip():
                                team_code = team_val.strip().upper()
                            else:
                                team_code = ''
                            break
                # ... existing code ...
                    if player_row is not None:
                        # Create basic stats
                        basic_stats = QBBasicStats(
                            pfr_id=pfr_id,
                            season=season,
                            team=team_code or '',
                            games_played=safe_int(player_row.get('G', 0)),
                            games_started=safe_int(player_row.get('GS', 0)),
                            completions=safe_int(player_row.get('Cmp', 0)),
                            attempts=safe_int(player_row.get('Att', 0)),
                            completion_pct=safe_float(player_row.get('Cmp%', 0)),
                            pass_yards=safe_int(player_row.get('Yds', 0)),
                            pass_tds=safe_int(player_row.get('TD', 0)),
                            interceptions=safe_int(player_row.get('Int', 0)),
                            longest_pass=safe_int(player_row.get('Lng', 0)),
                            rating=safe_float(player_row.get('Rate', 0)),
                            sacks=safe_int(player_row.get('Sk', 0)),
                            sack_yards=safe_int(player_row.get('Yds.1', 0)),
                            net_yards_per_attempt=safe_float(player_row.get('NY/A', 0)),
                            scraped_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        
                        # Create advanced stats
                        advanced_stats = QBAdvancedStats(
                            pfr_id=pfr_id,
                            season=season,
                            qbr=safe_float(player_row.get('QBR', 0)),
                            adjusted_net_yards_per_attempt=safe_float(player_row.get('ANY/A', 0)),
                            fourth_quarter_comebacks=safe_int(player_row.get('4QC', 0)),
                            game_winning_drives=safe_int(player_row.get('GWD', 0)),
                            scraped_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        
                        # Validate stats
                        basic_errors = basic_stats.validate()
                        advanced_errors = advanced_stats.validate()
                        
                        for error in basic_errors + advanced_errors:
                            results['warnings'].append(f"Stats validation: {error}")
                        
                        results['basic_stats'] = basic_stats
                        results['advanced_stats'] = advanced_stats
                        
                        logger.info(f"Found basic stats: {basic_stats.pass_yards} yards, {basic_stats.pass_tds} TDs")
                    else:
                        error_msg = f"Could not find {player_name} in {season} stats"
                        logger.error(error_msg)
                        results['errors'].append(error_msg)
                else:
                    error_msg = f"Could not parse stats table for {season}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            else:
                error_msg = f"Could not fetch stats page for {season}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                
        except Exception as e:
            error_msg = f"Error scraping basic stats: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        # Step 4: Scrape splits data
        logger.info("Scraping splits data...")
        try:
            splits_url = f"{player_url.replace('.htm', '')}/splits/{season}/"
            response = scraper.make_request_with_retry(splits_url)
            
            if response:
                from bs4 import BeautifulSoup
                
                soup = BeautifulSoup(response.content, 'html.parser')
                discovered_splits = scraper.discover_splits_from_page(soup)
                
                for split_type, categories in discovered_splits.items():
                    for category in categories:
                        try:
                            table_id = scraper.find_table_id_for_split(soup, split_type, category)
                            if table_id:
                                df = scraper.parse_table_data(soup, table_id)
                                if df is not None:
                                    # Find the player's row in splits
                                    player_row = None
                                    for _, row in df.iterrows():
                                        if clean_player_name(row.get('Player', '')) == player.player_name:
                                            player_row = row
                                            break
                                    
                                    if player_row is not None:
                                        # Create split stats object
                                        split_stats = QBSplitStats(
                                            pfr_id=pfr_id,
                                            season=season,
                                            split_type=split_type,
                                            split_category=category,
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
                                        
                                        # Add additional fields if available
                                        if 'Rush' in player_row.index:
                                            split_stats.rush_attempts = int(player_row.get('Rush', 0))
                                            split_stats.rush_yards = int(player_row.get('RushYds', 0))
                                            split_stats.rush_tds = int(player_row.get('RushTD', 0))
                                        
                                        results['splits'].append(split_stats)
                                        logger.info(f"Found split: {split_type} - {category}")
                                        
                        except Exception as e:
                            logger.warning(f"Error processing split {split_type}/{category}: {e}")
                            results['warnings'].append(f"Split error {split_type}/{category}: {e}")
            else:
                logger.warning(f"Could not fetch splits page for {player_name}")
                results['warnings'].append("Could not fetch splits page")
                
        except Exception as e:
            error_msg = f"Error scraping splits: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        # Step 5: Save to database if requested
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
        
        # Step 6: Print results
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
        print("Usage: python scrape_single_player.py \"Player Name\" [season] [--no-db]")
        print("Examples:")
        print("  python scrape_single_player.py \"Joe Burrow\" 2024")
        print("  python scrape_single_player.py \"Patrick Mahomes\" 2023 --no-db")
        sys.exit(1)
    
    player_name = sys.argv[1]
    season = int(sys.argv[2]) if len(sys.argv) > 2 else 2024
    save_to_db = "--no-db" not in sys.argv
    
    setup_logging()
    
    print(f"Scraping data for {player_name} ({season} season)")
    if not save_to_db:
        print("Note: Data will NOT be saved to database (--no-db flag)")
    
    results = scrape_single_player(player_name, season, save_to_db)
    
    if results['success']:
        print(f"\n✓ Successfully scraped data for {player_name}")
        sys.exit(0)
    else:
        print(f"\n✗ Failed to scrape data for {player_name}")
        sys.exit(1)

if __name__ == "__main__":
    main() 