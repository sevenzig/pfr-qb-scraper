#!/usr/bin/env python3
"""
Debug Joe Burrow's data to see what's wrong
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_manager import DatabaseManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_joe_burrow_data():
    """Debug Joe Burrow's data in detail"""
    
    print("DEBUGGING JOE BURROW'S DATA")
    print("=" * 60)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Check basic stats
                print("\n--- BASIC STATS ---")
                cursor.execute("""
                    SELECT pfr_id, player_name, season, team, g, gs, cmp, att, yds, td, int, rate
                    FROM qb_passing_stats 
                    WHERE player_name ILIKE '%burrow%'
                    ORDER BY season DESC
                """)
                basic_stats = cursor.fetchall()
                
                print(f"Found {len(basic_stats)} basic stats records:")
                for stat in basic_stats:
                    if isinstance(stat, dict):
                        print(f"  {stat['season']}: {stat['player_name']} - {stat['team']} - {stat['g']} games - {stat['cmp']}/{stat['att']} - {stat['yds']} yards - {stat['td']} TDs - {stat['int']} INTs - {stat['rate']} rating")
                    else:
                        print(f"  {stat}")
                
                # Check splits by type
                print("\n--- BASIC SPLITS BY TYPE ---")
                cursor.execute("""
                    SELECT split, COUNT(*) as count
                    FROM qb_splits 
                    WHERE player_name ILIKE '%burrow%' AND season = 2024
                    GROUP BY split
                    ORDER BY count DESC
                """)
                split_types = cursor.fetchall()
                
                print(f"Split types for 2024:")
                for split_type in split_types:
                    if isinstance(split_type, dict):
                        print(f"  {split_type['split']}: {split_type['count']} records")
                    else:
                        print(f"  {split_type}")
                
                # Check some sample splits
                print("\n--- SAMPLE BASIC SPLITS ---")
                cursor.execute("""
                    SELECT split, value, g, cmp, att, yds, td
                    FROM qb_splits 
                    WHERE player_name ILIKE '%burrow%' AND season = 2024
                    ORDER BY split, value
                    LIMIT 10
                """)
                sample_splits = cursor.fetchall()
                
                print(f"Sample splits:")
                for split in sample_splits:
                    if isinstance(split, dict):
                        print(f"  {split['split']} - {split['value']}: {split['g']} games, {split['cmp']}/{split['att']}, {split['yds']} yards, {split['td']} TDs")
                    else:
                        print(f"  {split}")
                
                # Check advanced splits
                print("\n--- ADVANCED SPLITS BY TYPE ---")
                cursor.execute("""
                    SELECT split, COUNT(*) as count
                    FROM qb_splits_advanced 
                    WHERE player_name ILIKE '%burrow%' AND season = 2024
                    GROUP BY split
                    ORDER BY count DESC
                """)
                advanced_split_types = cursor.fetchall()
                
                print(f"Advanced split types for 2024:")
                for split_type in advanced_split_types:
                    if isinstance(split_type, dict):
                        print(f"  {split_type['split']}: {split_type['count']} records")
                    else:
                        print(f"  {split_type}")
                
                # Check for duplicate records
                print("\n--- CHECKING FOR DUPLICATES ---")
                cursor.execute("""
                    SELECT split, value, COUNT(*) as count
                    FROM qb_splits 
                    WHERE player_name ILIKE '%burrow%' AND season = 2024
                    GROUP BY split, value
                    HAVING COUNT(*) > 1
                    ORDER BY count DESC
                """)
                duplicates = cursor.fetchall()
                
                if duplicates:
                    print(f"Found {len(duplicates)} duplicate split combinations:")
                    for dup in duplicates:
                        if isinstance(dup, dict):
                            print(f"  {dup['split']} - {dup['value']}: {dup['count']} times")
                        else:
                            print(f"  {dup}")
                else:
                    print("No duplicates found in basic splits")
                
                # Check advanced splits duplicates
                cursor.execute("""
                    SELECT split, value, COUNT(*) as count
                    FROM qb_splits_advanced 
                    WHERE player_name ILIKE '%burrow%' AND season = 2024
                    GROUP BY split, value
                    HAVING COUNT(*) > 1
                    ORDER BY count DESC
                """)
                advanced_duplicates = cursor.fetchall()
                
                if advanced_duplicates:
                    print(f"Found {len(advanced_duplicates)} duplicate advanced split combinations:")
                    for dup in advanced_duplicates:
                        if isinstance(dup, dict):
                            print(f"  {dup['split']} - {dup['value']}: {dup['count']} times")
                        else:
                            print(f"  {dup}")
                else:
                    print("No duplicates found in advanced splits")
        
    except Exception as e:
        print(f"Error debugging data: {e}")
        logger.error(f"Error debugging data: {e}", exc_info=True)
    
    finally:
        db_manager.close()

if __name__ == "__main__":
    debug_joe_burrow_data() 