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
from pathlib import Path

# Add src/ to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.models.qb_models import Player, QBBasicStats, QBAdvancedStats, QBSplitStats
from src.utils.data_utils import generate_player_id, clean_player_name
from src.database.db_manager import DatabaseManager
from core.selenium_manager import SeleniumManager, SeleniumConfig

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
    """
    Scrape Joe Burrow's 2024 stats and splits using SeleniumManager for all PFR page loads.
    """
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
    
    selenium_config = SeleniumConfig(headless=True)
    selenium_manager = SeleniumManager(selenium_config)
    selenium_manager.start_session()
    
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
        main_url = f"https://www.pro-football-reference.com/years/{season}/passing.htm"
        main_result = selenium_manager.get_page(main_url, enable_js=False)
        if not main_result['success']:
            print(f"ERROR: Failed to fetch main stats page: {main_result['error']}")
            return
        main_html = main_result['content']
        
        soup = BeautifulSoup(main_html, 'html.parser')
        table = soup.find('table', {'id': 'passing'})
        
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
                    player_name=player_name,
                    player_url=player_url,
                    season=season,
                    rk=int(player_row.get('Rk', 0)),
                    age=int(player_row.get('Age', 0)),
                    team=player_row.get('Tm', ''),
                    pos=player_row.get('Pos', ''),
                    g=int(player_row.get('G', 0)),
                    gs=int(player_row.get('GS', 0)),
                    qb_rec=player_row.get('QBrec', ''),
                    cmp=int(player_row.get('Cmp', 0)),
                    att=int(player_row.get('Att', 0)),
                    inc=int(player_row.get('Att', 0)) - int(player_row.get('Cmp', 0)),
                    cmp_pct=float(player_row.get('Cmp%', 0)) if player_row.get('Cmp%') else None,
                    yds=int(player_row.get('Yds', 0)),
                    td=int(player_row.get('TD', 0)),
                    td_pct=float(player_row.get('TD%', 0)) if player_row.get('TD%') else None,
                    int=int(player_row.get('Int', 0)),
                    int_pct=float(player_row.get('Int%', 0)) if player_row.get('Int%') else None,
                    first_downs=int(player_row.get('1D', 0)),
                    succ_pct=float(player_row.get('Succ%', 0)) if player_row.get('Succ%') else None,
                    lng=int(player_row.get('Lng', 0)),
                    y_a=float(player_row.get('Y/A', 0)) if player_row.get('Y/A') else None,
                    ay_a=float(player_row.get('AY/A', 0)) if player_row.get('AY/A') else None,
                    y_c=float(player_row.get('Y/C', 0)) if player_row.get('Y/C') else None,
                    y_g=float(player_row.get('Y/G', 0)) if player_row.get('Y/G') else None,
                    rate=float(player_row.get('Rate', 0)) if player_row.get('Rate') else None,
                    qbr=float(player_row.get('QBR', 0)) if player_row.get('QBR') else None,
                    sk=int(player_row.get('Sk', 0)),
                    sk_yds=int(player_row.get('Yds.1', 0)),
                    ny_a=float(player_row.get('NY/A', 0)) if player_row.get('NY/A') else None,
                    any_a=float(player_row.get('ANY/A', 0)) if player_row.get('ANY/A') else None,
                    four_qc=int(player_row.get('4QC', 0)),
                    gwd=int(player_row.get('GWD', 0)),
                    awards=player_row.get('Awards', ''),
                    player_additional=player_row.get('Player-additional', ''),
                    scraped_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                
                print(f"Basic Stats:")
                print(f"  Team: {basic_stats.team}")
                print(f"  Games: {basic_stats.g} played, {basic_stats.gs} started")
                print(f"  Passing: {basic_stats.cmp}/{basic_stats.att} ({basic_stats.cmp_pct}%)")
                print(f"  Yards: {basic_stats.yds}, TDs: {basic_stats.td}, INTs: {basic_stats.int}")
                print(f"  Rating: {basic_stats.rate}")
                
                # Save to database
                db_manager.insert_player(player)
                db_manager.insert_qb_basic_stats([basic_stats])
                print("[OK] Basic stats saved to database")
            else:
                print("[FAIL] Could not find Joe Burrow in basic stats")
        else:
            print("[FAIL] Could not find passing stats table")
        
        # Step 3: Scrape advanced stats
        print("\nScraping advanced stats...")
        adv_stats_url = f"https://www.pro-football-reference.com/years/{season}/passing_advanced.htm"
        adv_result = selenium_manager.get_page(adv_stats_url, enable_js=False)
        if not adv_result['success']:
            print(f"ERROR: Failed to fetch advanced stats page: {adv_result['error']}")
            return
        adv_html = adv_result['content']

        soup = BeautifulSoup(adv_html, 'html.parser')
        table = soup.find('table', {'id': 'advanced_splits'})
        
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
                print("[OK] Advanced stats saved to database")
            else:
                print("[FAIL] Could not find Joe Burrow in advanced stats")
        else:
            print("[FAIL] Could not find advanced passing stats table")
        
        # Step 4: Scrape splits
        print("\nScraping splits data...")
        splits_url = f"{player_url.replace('.htm', '')}/splits/{season}/"
        splits_result = selenium_manager.get_page(splits_url, enable_js=False)
        if not splits_result['success']:
            print(f"ERROR: Failed to fetch splits page: {splits_result['error']}")
            return
        splits_html = splits_result['content']

        soup = BeautifulSoup(splits_html, 'html.parser')
        # In the splits section, replace the loop over all tables with a direct lookup for the 'stats' table
        splits_table = soup.find('table', {'id': 'stats'})
        splits = []
        if splits_table:
            try:
                df = pd.read_html(str(splits_table))[0]
                # Find Joe Burrow's row
                player_row = None
                for _, row in df.iterrows():
                    if clean_player_name(row.get('Player', '')) == clean_player_name(player_name):
                        player_row = row
                        break
                if player_row is not None:
                    # Create split stats (update field names as needed)
                    split_stats = QBSplitStats(
                        pfr_id=pfr_id,
                        season=season,
                        split_type="basic_splits",
                        split_category="all",
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
                    print(f"  Found split: basic_splits - all")
            except Exception as e:
                print(f"  Error processing table stats: {e}")
        else:
            print("[FAIL] Could not find splits table with id 'stats'")
        
        if splits:
            db_manager.insert_qb_splits(splits)
            print(f"[OK] Saved {len(splits)} splits to database")
        else:
            print("[FAIL] No splits found")
        
        # Step 5: Show database stats
        print("\nDatabase Statistics:")
        # stats = db_manager.get_database_stats()
        # for key, value in stats.items():
        #     print(f"  {key}: {value}")
        
        print(f"\n[SUCCESS] Scraped Joe Burrow data for {season}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        logger.error(f"Error scraping Joe Burrow: {e}")
    
    finally:
        selenium_manager.end_session()
        db_manager.close()

if __name__ == "__main__":
    setup_logging()
    scrape_joe_burrow_2024() 