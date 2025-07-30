#!/usr/bin/env python3
"""
Check database tables and create them if needed
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_manager import DatabaseManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_tables():
    """Check what tables exist in the database"""
    
    print("Checking database tables...")
    print("=" * 60)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        # Check if tables exist
        print("\n--- Checking Tables ---")
        
        # Try to create tables
        print("Creating tables...")
        db_manager.create_tables()
        print("Tables created successfully!")
        
        # Check what tables exist
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                
                print(f"\nFound {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table[0] if isinstance(table, tuple) else table}")
        
        # Check if Joe Burrow data exists
        print("\n--- Checking Joe Burrow Data ---")
        
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Check basic stats
                cursor.execute("SELECT COUNT(*) FROM qb_passing_stats WHERE player_name ILIKE '%burrow%'")
                result = cursor.fetchone()
                basic_count = result['count'] if isinstance(result, dict) else result[0]
                print(f"Joe Burrow basic stats: {basic_count}")
                
                # Check splits
                cursor.execute("SELECT COUNT(*) FROM qb_splits WHERE player_name ILIKE '%burrow%'")
                result = cursor.fetchone()
                splits_count = result['count'] if isinstance(result, dict) else result[0]
                print(f"Joe Burrow splits: {splits_count}")
                
                # Check advanced splits
                cursor.execute("SELECT COUNT(*) FROM qb_splits_advanced WHERE player_name ILIKE '%burrow%'")
                result = cursor.fetchone()
                advanced_count = result['count'] if isinstance(result, dict) else result[0]
                print(f"Joe Burrow advanced splits: {advanced_count}")
                
                if basic_count > 0:
                    cursor.execute("SELECT player_name, season, team, g, cmp, att, yds, td FROM qb_passing_stats WHERE player_name ILIKE '%burrow%' LIMIT 1")
                    row = cursor.fetchone()
                    if row:
                        if isinstance(row, dict):
                            print(f"Sample basic stat: {row['player_name']} - {row['season']} - {row['team']} - {row['g']} games - {row['cmp']}/{row['att']} - {row['yds']} yards - {row['td']} TDs")
                        else:
                            print(f"Sample basic stat: {row}")
                    else:
                        print("No basic stats found")
                
                if splits_count > 0:
                    cursor.execute("SELECT split, value, cmp, yds FROM qb_splits WHERE player_name ILIKE '%burrow%' LIMIT 3")
                    rows = cursor.fetchall()
                    print(f"Sample splits: {rows}")
        
    except Exception as e:
        print(f"Error checking database: {e}")
        logger.error(f"Error checking database: {e}", exc_info=True)
    
    finally:
        db_manager.close()

if __name__ == "__main__":
    check_database_tables() 