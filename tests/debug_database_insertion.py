#!/usr/bin/env python3
"""
Debug database insertion issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_manager import DatabaseManager
from src.models.qb_models import QBBasicStats, Player
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_database_insertion():
    """Debug the database insertion process"""
    
    print("Debugging database insertion...")
    print("=" * 60)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        # Test connection
        print("\n--- Testing Connection ---")
        if db_manager.test_connection():
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
            return
        
        # Create tables
        print("\n--- Creating Tables ---")
        db_manager.create_tables()
        print("✓ Tables created")
        
        # Create test data
        print("\n--- Creating Test Data ---")
        
        # Create a test player
        test_player = Player(
            pfr_id="burrjo01",
            player_name="Joe Burrow",
            position="QB",
            pfr_url="https://www.pro-football-reference.com/players/B/burrjo01/",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create test QB stats
        test_stats = QBBasicStats(
            pfr_id="burrjo01",
            player_name="Joe Burrow",
            player_url="https://www.pro-football-reference.com/players/B/burrjo01/",
            season=2024,
            rk=1,
            age=27,
            team="cin",
            pos="QB",
            g=10,
            gs=10,
            qb_rec="7-3-0",
            cmp=245,
            att=360,
            inc=115,
            cmp_pct=68.1,
            yds=2309,
            td=15,
            td_pct=4.2,
            int=6,
            int_pct=1.7,
            first_downs=115,
            succ_pct=68.1,
            lng=81,
            y_a=6.4,
            ay_a=6.8,
            y_c=9.4,
            y_g=230.9,
            rate=91.2,
            qbr=65.4,
            sk=22,
            sk_yds=165,
            sk_pct=5.8,
            ny_a=5.8,
            any_a=6.2,
            four_qc=2,
            gwd=3,
            awards="",
            player_additional="",
            scraped_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        print(f"✓ Created test player: {test_player.player_name}")
        print(f"✓ Created test stats for {test_stats.player_name}")
        
        # Insert player first
        print("\n--- Inserting Player ---")
        try:
            inserted_players = db_manager.insert_players([test_player])
            print(f"✓ Inserted {inserted_players} players")
        except Exception as e:
            print(f"✗ Failed to insert player: {e}")
            return
        
        # Insert QB stats
        print("\n--- Inserting QB Stats ---")
        try:
            inserted_stats = db_manager.insert_qb_basic_stats([test_stats])
            print(f"✓ Inserted {inserted_stats} QB stats")
        except Exception as e:
            print(f"✗ Failed to insert QB stats: {e}")
            return
        
        # Verify data was inserted
        print("\n--- Verifying Data ---")
        try:
            stats = db_manager.get_qb_stats_for_season(2024)
            print(f"✓ Found {len(stats)} QB stats for 2024")
            
            if stats:
                for stat in stats:
                    print(f"  - {stat.player_name} ({stat.pfr_id}): {stat.g} games, {stat.yds} yards")
        except Exception as e:
            print(f"✗ Failed to verify data: {e}")
        
        print("\n--- Debug Complete ---")
        
    except Exception as e:
        print(f"✗ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database_insertion() 