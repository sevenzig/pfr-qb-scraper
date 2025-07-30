#!/usr/bin/env python3
"""
Check Joe Burrow's data in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_joe_burrow_data():
    """Check Joe Burrow's data in the database"""
    print("Checking Joe Burrow's data in the database...")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    try:
        # Check basic stats
        print("\n--- Basic Stats ---")
        basic_stats = db_manager.get_qb_stats_for_season(2024)
        print(f"Total basic stats for 2024: {len(basic_stats)}")
        
        for stat in basic_stats:
            if 'burrow' in stat.player_name.lower():
                print(f"Found Joe Burrow: {stat.player_name}")
                print(f"  Season: {stat.season}")
                print(f"  Team: {stat.team}")
                print(f"  Games: {stat.g}")
                print(f"  Completions: {stat.cmp}")
                print(f"  Attempts: {stat.att}")
                print(f"  Yards: {stat.yds}")
                print(f"  TDs: {stat.td}")
        
        # Check basic splits using direct query
        print("\n--- Basic Splits ---")
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT pfr_id, player_name, season, split, value, g, cmp, att, yds, td, int, rate
                    FROM qb_splits
                    WHERE player_name ILIKE '%burrow%' AND season = 2024
                    ORDER BY split, value
                    LIMIT 10
                """)
                basic_splits = cursor.fetchall()
                
                print(f"Total basic splits for Joe Burrow 2024: {len(basic_splits)}")
                for split in basic_splits[:5]:  # Show first 5
                    print(f"  Split: {split['split']} = {split['value']}")
                    print(f"    Games: {split['g']}, Cmp: {split['cmp']}, Att: {split['att']}, Yds: {split['yds']}")
        
        # Check advanced splits using direct query
        print("\n--- Advanced Splits ---")
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT pfr_id, player_name, season, split, value, cmp, att, yds, td, int, rate
                    FROM qb_splits_advanced
                    WHERE player_name ILIKE '%burrow%' AND season = 2024
                    ORDER BY split, value
                    LIMIT 10
                """)
                advanced_splits = cursor.fetchall()
                
                print(f"Total advanced splits for Joe Burrow 2024: {len(advanced_splits)}")
                for split in advanced_splits[:5]:  # Show first 5
                    print(f"  Split: {split['split']} = {split['value']}")
                    print(f"    Cmp: {split['cmp']}, Att: {split['att']}, Yds: {split['yds']}")
        
        # Check for any NULL values in splits
        print("\n--- Data Quality Check ---")
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_basic,
                        COUNT(CASE WHEN cmp IS NULL THEN 1 END) as null_cmp,
                        COUNT(CASE WHEN att IS NULL THEN 1 END) as null_att,
                        COUNT(CASE WHEN yds IS NULL THEN 1 END) as null_yds
                    FROM qb_splits
                    WHERE player_name ILIKE '%burrow%' AND season = 2024
                """)
                quality_stats = cursor.fetchone()
                
                print(f"Basic splits total: {quality_stats['total_basic']}")
                print(f"  NULL completions: {quality_stats['null_cmp']}")
                print(f"  NULL attempts: {quality_stats['null_att']}")
                print(f"  NULL yards: {quality_stats['null_yds']}")
        
    except Exception as e:
        logger.error(f"Error checking data: {e}")
        raise
    finally:
        db_manager.close()

if __name__ == "__main__":
    check_joe_burrow_data() 