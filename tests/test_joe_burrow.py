#!/usr/bin/env python3
"""
Test script to scrape Joe Burrow data using a known PFR URL
"""

import sys
import os
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.qb_models import Player, QBBasicStats, QBAdvancedStats, QBSplitStats
from utils.data_utils import generate_player_id, clean_player_name
from database.db_manager import DatabaseManager

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/test_joe_burrow.log'),
            logging.StreamHandler()
        ]
    )

def scrape_joe_burrow_2024():
    """Scrape Joe Burrow's 2024 data"""
    logger = logging.getLogger(__name__)
    
    # Known Joe Burrow PFR URL
    player_url = "https://www.pro-football-reference.com/players/B/BurrJo01.htm"
    player_name = "Joe Burrow"
    season = 2024
    pfr_id = "burrjo01"
    
    print(f"Scraping {player_name} ({season} season)")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    db_manager.create_tables()
    
    try:
        # Step 1: Create Player object
        player = Player(
            pfr_id=pfr_id,
            player_name=clean_player_name(player_name),
            pfr_url=player_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        print(f"Player: {player.player_name} (PFR ID: {player.pfr_id})")
        
        # Step 2: Scrape basic stats
        print("\nScraping basic stats...")
        stats_url = f"https://www.pro-football-reference.com/years/{season}/passing.htm"
        response = requests.get(stats_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'stats_passing'})
        
        if table:
            df = pd.read_html(str(table))[0]
            
            # Find Joe Burrow's row
            player_row = None
            for _, row in df.iterrows():
                if clean_player_name(row.get('Player', '')) == clean_player_name(player_name):
                    player_row = row
                    break
            
            if player_row is not None:
                # Create basic stats
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
                
                print(f"Basic Stats:")
                print(f"  Team: {basic_stats.team}")
                print(f"  Games: {basic_stats.games_played} played, {basic_stats.games_started} started")
                print(f"  Passing: {basic_stats.completions}/{basic_stats.attempts} ({basic_stats.completion_pct}%)")
                print(f"  Yards: {basic_stats.pass_yards}, TDs: {basic_stats.pass_tds}, INTs: {basic_stats.interceptions}")
                print(f"  Rating: {basic_stats.rating}")
                
                # Save to database
                db_manager.insert_player(player)
                db_manager.insert_qb_basic_stats([basic_stats])
                print("✓ Basic stats saved to database")
            else:
                print("✗ Could not find Joe Burrow in basic stats")
        else:
            print("✗ Could not find passing stats table")
        
        # Step 3: Scrape advanced stats
        print("\nScraping advanced stats...")
        adv_stats_url = f"https://www.pro-football-reference.com/years/{season}/passing_advanced.htm"
        response = requests.get(adv_stats_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'advanced_passing'})
        
        if table:
            df = pd.read_html(str(table))[0]
            
            # Find Joe Burrow's row
            player_row = None
            for _, row in df.iterrows():
                if clean_player_name(row.get('Player', '')) == clean_player_name(player_name):
                    player_row = row
                    break
            
            if player_row is not None:
                # Create advanced stats
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
                
                print(f"Advanced Stats:")
                print(f"  QBR: {advanced_stats.qbr}")
                print(f"  ANY/A: {advanced_stats.adjusted_net_yards_per_attempt}")
                print(f"  4QC: {advanced_stats.fourth_quarter_comebacks}, GWD: {advanced_stats.game_winning_drives}")
                
                # Save to database
                db_manager.insert_qb_advanced_stats([advanced_stats])
                print("✓ Advanced stats saved to database")
            else:
                print("✗ Could not find Joe Burrow in advanced stats")
        else:
            print("✗ Could not find advanced passing stats table")
        
        # Step 4: Scrape splits
        print("\nScraping splits data...")
        splits_url = f"{player_url.replace('.htm', '')}/splits/{season}/"
        response = requests.get(splits_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        
        splits = []
        for table in tables:
            table_id = table.get('id', '')
            if 'splits' in table_id.lower():
                try:
                    df = pd.read_html(str(table))[0]
                    
                    # Find Joe Burrow's row
                    player_row = None
                    for _, row in df.iterrows():
                        if clean_player_name(row.get('Player', '')) == clean_player_name(player_name):
                            player_row = row
                            break
                    
                    if player_row is not None:
                        # Determine split type and category
                        split_type = "basic_splits"
                        split_category = "unknown"
                        
                        caption = table.find('caption')
                        if caption:
                            caption_text = caption.text.lower()
                            if 'home' in caption_text:
                                split_type = "location_splits"
                                split_category = "home"
                            elif 'away' in caption_text:
                                split_type = "location_splits"
                                split_category = "away"
                            elif 'quarter' in caption_text:
                                split_type = "quarter_splits"
                                split_category = caption_text.split()[0]
                        
                        # Create split stats
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
                        print(f"  Found split: {split_type} - {split_category}")
                        
                except Exception as e:
                    print(f"  Error processing table {table_id}: {e}")
                    continue
        
        if splits:
            db_manager.insert_qb_splits(splits)
            print(f"✓ Saved {len(splits)} splits to database")
        else:
            print("✗ No splits found")
        
        # Step 5: Show database stats
        print("\nDatabase Statistics:")
        stats = db_manager.get_database_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\n🎉 SUCCESS! Scraped Joe Burrow data for {season}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error(f"Error scraping Joe Burrow: {e}")
    
    finally:
        db_manager.close()

if __name__ == "__main__":
    setup_logging()
    scrape_joe_burrow_2024() 