#!/usr/bin/env python3
"""
Robust NFL QB Data Scraper with Incremental Saving

This scraper:
1. Separates basic splits (type 1) and advanced splits (type 2) correctly
2. Saves data incrementally after each QB to prevent data loss
3. Can resume from where it left off
4. Provides detailed progress tracking

Usage:
    python scripts/robust_qb_scraper.py --all
    python scripts/robust_qb_scraper.py --player "Joe Burrow"
    python scripts/robust_qb_scraper.py --resume
"""

import argparse
import time
import logging
import os
import sys
from datetime import datetime
from typing import List, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.enhanced_qb_scraper import EnhancedQBScraper
from src.models.qb_models import QBBasicStats, QBSplitStats, QBAdvancedStats, Player
from src.database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/robust_qb_scraping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class QBCompleteData:
    """Complete QB data with separated splits types"""
    main_stats: QBBasicStats
    basic_splits: List[QBSplitStats]  # Type 1 splits
    advanced_splits: List[QBAdvancedStats]  # Type 2 splits
    player_url: str

class RobustQBScraper:
    """Robust QB scraper with incremental saving and error recovery"""
    
    def __init__(self):
        self.scraper = EnhancedQBScraper()
        self.db_manager = DatabaseManager()
        
    def separate_splits_data(self, all_splits: List[QBSplitStats]) -> Tuple[List[QBSplitStats], List[QBAdvancedStats]]:
        """
        Separate mixed splits data into basic splits and advanced splits
        
        We examine the actual split values to determine the type:
        - Basic splits (Type 1): Home/Road, Win/Loss, etc. (have game context)
        - Advanced splits (Type 2): 1st/2nd/3rd/4th quarters, downs, etc. (situational)
        """
        basic_splits = []
        advanced_splits = []
        
        # Split values that indicate basic splits (Type 1)
        basic_split_values = {
            'home', 'road', 'away', 'win', 'loss', 'tie', 'indoor', 'outdoor',
            'grass', 'fieldturf', 'artificial', 'natural', 'afc', 'nfc', 
            'vs afc', 'vs nfc', 'vs division', 'vs non-division',
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'playoffs', 'regular season', 'preseason'
        }
        
        # Split values that indicate advanced splits (Type 2)
        advanced_split_values = {
            '1st', '2nd', '3rd', '4th', '1st quarter', '2nd quarter', '3rd quarter', '4th quarter',
            '1st down', '2nd down', '3rd down', '4th down', 
            '1st & 10', '2nd & 1', '2nd & 2', '2nd & 3', '3rd & 1', '3rd & 2', '3rd & 3',
            '1-3', '4-6', '7-9', '10+', 'red zone', 'goal line',
            'behind', 'tied', 'ahead', 'within 7', 'within 14',
            '1st half', '2nd half', 'ot'
        }
        
        for split in all_splits:
            value = (split.value or '').lower().strip()
            
            # Check if this is a basic or advanced split based on the value
            is_basic = False
            is_advanced = False
            
            # Direct value matches
            if value in basic_split_values:
                is_basic = True
            elif value in advanced_split_values:
                is_advanced = True
            else:
                # Pattern matching for advanced splits
                if (value.startswith(('1st', '2nd', '3rd', '4th')) or
                    value.endswith(('quarter', 'down', 'half')) or
                    any(pattern in value for pattern in ['1-', '2-', '3-', '4-', 'behind by', 'ahead by'])):
                    is_advanced = True
                else:
                    # Fallback: if split has game-level data (wins/losses/games), it's basic
                    if hasattr(split, 'g') and split.g is not None and split.g > 0:
                        is_basic = True
                    else:
                        # Default to advanced for situational data
                        is_advanced = True
            
            if is_basic:
                basic_splits.append(split)
            else:
                # Convert to advanced split
                advanced_stat = QBAdvancedStats(
                    pfr_id=split.pfr_id,
                    player_name=split.player_name,
                    season=split.season,
                    split=split.split,
                    value=split.value,
                    cmp=split.cmp,
                    att=split.att,
                    inc=split.inc,
                    cmp_pct=split.cmp_pct,
                    yds=split.yds,
                    td=split.td,
                    first_downs=getattr(split, 'first_downs', None),
                    int=split.int,
                    rate=split.rate,
                    sk=split.sk,
                    sk_yds=split.sk_yds,
                    y_a=split.y_a,
                    ay_a=split.ay_a,
                    rush_att=split.rush_att,
                    rush_yds=split.rush_yds,
                    rush_y_a=split.rush_y_a,
                    rush_td=split.rush_td,
                    rush_first_downs=getattr(split, 'rush_first_downs', None),
                    scraped_at=split.scraped_at,
                    updated_at=split.updated_at
                )
                advanced_splits.append(advanced_stat)
        
        return basic_splits, advanced_splits
    
    def scrape_single_qb_complete(self, player_name: str) -> Optional[QBCompleteData]:
        """Scrape complete data for a single QB with proper separation"""
        logger.info(f"Scraping complete data for: {player_name}")
        
        try:
            # Get the QB data using existing scraper
            qb_data = self.scraper.scrape_single_qb(player_name)
            if not qb_data:
                return None
            
            # Separate the splits data properly
            basic_splits, advanced_splits = self.separate_splits_data(qb_data.splits_data)
            
            logger.info(f"Separated splits for {player_name}: {len(basic_splits)} basic, {len(advanced_splits)} advanced")
            
            return QBCompleteData(
                main_stats=qb_data.main_stats,
                basic_splits=basic_splits,
                advanced_splits=advanced_splits,
                player_url=qb_data.player_url
            )
            
        except Exception as e:
            logger.error(f"Error scraping {player_name}: {e}")
            return None
    
    def save_qb_data_incremental(self, qb_data: QBCompleteData) -> bool:
        """Save QB data incrementally with proper error handling"""
        try:
            # Save player
            player = Player(
                pfr_id=qb_data.main_stats.pfr_id,
                player_name=qb_data.main_stats.player_name,
                pfr_url=qb_data.player_url,
            )
            self.db_manager.insert_player(player)
            
            # Save main stats
            self.db_manager.insert_qb_basic_stats([qb_data.main_stats])
            
            # Save basic splits (type 1)
            if qb_data.basic_splits:
                self.db_manager.insert_qb_splits(qb_data.basic_splits)
            
            # Save advanced splits (type 2)
            if qb_data.advanced_splits:
                self.db_manager.insert_qb_advanced_stats(qb_data.advanced_splits)
            
            logger.info(f"Successfully saved all data for {qb_data.main_stats.player_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data for {qb_data.main_stats.player_name}: {e}")
            return False
    
    def get_already_processed_qbs(self) -> List[str]:
        """Get list of QBs already in the database"""
        try:
            query = "SELECT DISTINCT player_name FROM players ORDER BY player_name"
            results = self.db_manager.query(query)
            return [row['player_name'] for row in results]
        except Exception as e:
            logger.error(f"Error getting processed QBs: {e}")
            return []
    
    def scrape_all_qbs_robust(self, resume: bool = False) -> dict:
        """Scrape all QBs with robust error handling and incremental saving"""
        logger.info("Starting robust QB scraping for all 78 QBs...")
        
        # Get list of all QBs from the main stats page
        all_qb_stats = self.scraper.scrape_all_qb_main_stats()
        logger.info(f"Found {len(all_qb_stats)} QBs to process")
        
        # If resuming, skip already processed QBs
        already_processed = set()
        if resume:
            already_processed = set(self.get_already_processed_qbs())
            logger.info(f"Resume mode: {len(already_processed)} QBs already processed")
        
        # Stats tracking
        stats = {
            'total_qbs': len(all_qb_stats),
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'total_basic_splits': 0,
            'total_advanced_splits': 0,
            'start_time': datetime.now()
        }
        
        for i, qb_stat in enumerate(all_qb_stats):
            qb_name = qb_stat.player_name
            
            # Skip if already processed (resume mode)
            if resume and qb_name in already_processed:
                logger.info(f"Skipping already processed QB {i+1}/{len(all_qb_stats)}: {qb_name}")
                stats['skipped'] += 1
                continue
            
            logger.info(f"Processing QB {i+1}/{len(all_qb_stats)}: {qb_name}")
            
            # Scrape QB data
            qb_data = self.scrape_single_qb_complete(qb_name)
            if qb_data:
                # Save data incrementally
                if self.save_qb_data_incremental(qb_data):
                    stats['processed'] += 1
                    stats['total_basic_splits'] += len(qb_data.basic_splits)
                    stats['total_advanced_splits'] += len(qb_data.advanced_splits)
                    
                    logger.info(f"✅ Completed {qb_name}: "
                              f"{len(qb_data.basic_splits)} basic splits, "
                              f"{len(qb_data.advanced_splits)} advanced splits")
                else:
                    stats['errors'] += 1
                    logger.error(f"❌ Failed to save data for {qb_name}")
            else:
                stats['errors'] += 1
                logger.error(f"❌ Failed to scrape data for {qb_name}")
            
            # Add delay between QBs to be respectful
            if i < len(all_qb_stats) - 1:
                time.sleep(2)
        
        # Final stats
        stats['end_time'] = datetime.now()
        stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
        
        return stats
    
    def print_database_summary(self):
        """Print current database contents"""
        try:
            players_count = self.db_manager.query("SELECT COUNT(*) as count FROM players")[0]['count']
            passing_count = self.db_manager.query("SELECT COUNT(*) as count FROM qb_passing_stats")[0]['count'] 
            splits1_count = self.db_manager.query("SELECT COUNT(*) as count FROM qb_splits_type1")[0]['count']
            splits2_count = self.db_manager.query("SELECT COUNT(*) as count FROM qb_splits_type2")[0]['count']
            
            print(f"\n📊 Current Database Summary:")
            print(f"  Players: {players_count}")
            print(f"  Passing Stats: {passing_count}")
            print(f"  Basic Splits (Type 1): {splits1_count}")
            print(f"  Advanced Splits (Type 2): {splits2_count}")
            
        except Exception as e:
            logger.error(f"Error getting database summary: {e}")

def main():
    """Main function for robust QB scraper"""
    parser = argparse.ArgumentParser(description='Robust NFL QB Data Scraper')
    parser.add_argument('--player', type=str, help='Scrape data for specific QB (e.g., "Joe Burrow")')
    parser.add_argument('--all', action='store_true', help='Scrape data for all QBs')
    parser.add_argument('--resume', action='store_true', help='Resume scraping (skip already processed QBs)')
    
    args = parser.parse_args()
    
    scraper = RobustQBScraper()
    
    if args.player:
        # Single QB
        qb_data = scraper.scrape_single_qb_complete(args.player)
        if qb_data:
            if scraper.save_qb_data_incremental(qb_data):
                print(f"\n✅ Successfully scraped and saved {args.player}")
                print(f"  Main Stats: ✅")
                print(f"  Basic Splits: {len(qb_data.basic_splits)} records")
                print(f"  Advanced Splits: {len(qb_data.advanced_splits)} records")
            else:
                print(f"❌ Failed to save data for {args.player}")
        else:
            print(f"❌ Failed to scrape data for {args.player}")
    
    elif args.all or args.resume:
        # All QBs
        stats = scraper.scrape_all_qbs_robust(resume=args.resume)
        
        print(f"\n🏆 Scraping Complete!")
        print(f"  Total QBs: {stats['total_qbs']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Basic Splits: {stats['total_basic_splits']}")
        print(f"  Advanced Splits: {stats['total_advanced_splits']}")
        print(f"  Duration: {stats['duration']:.1f} seconds")
    
    else:
        print("No arguments provided. Use --help for options.")
    
    # Show final database state
    scraper.print_database_summary()

if __name__ == "__main__":
    main() 