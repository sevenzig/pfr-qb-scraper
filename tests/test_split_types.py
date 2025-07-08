#!/usr/bin/env python3
"""
Debug script to verify split types are being stored correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from database.db_manager import DatabaseManager
from config.config import config

def main():
    """Check the split types in the database"""
    db_manager = DatabaseManager()
    
    try:
        # Query to check split types
        query = """
        SELECT split_type, COUNT(*) as count
        FROM qb_splits 
        WHERE player_name = 'Joe Burrow' AND season = 2024
        GROUP BY split_type
        ORDER BY split_type
        """
        
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cur:
                cur.execute(query)
                results = cur.fetchall()
        
        print("=== Split Types for Joe Burrow 2024 ===")
        for row in results:
            print(f"{row['split_type']}: {row['count']} records")
            
        # Show sample records from each type
        print("\n=== Sample Basic Splits ===")
        basic_query = """
        SELECT split_category, games, completions, attempts, pass_yards, pass_tds, rating
        FROM qb_splits 
        WHERE player_name = 'Joe Burrow' AND season = 2024 AND split_type = 'basic_splits'
        LIMIT 5
        """
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cur:
                cur.execute(basic_query)
                basic_results = cur.fetchall()
        
        for row in basic_results:
            print(f"{row['split_category']}: {row['completions']}/{row['attempts']} for {row['pass_yards']} yards, {row['pass_tds']} TDs, {row['rating']} rating")
            
        print("\n=== Sample Advanced Splits ===")
        advanced_query = """
        SELECT split_category, games, completions, attempts, pass_yards, pass_tds, rating
        FROM qb_splits 
        WHERE player_name = 'Joe Burrow' AND season = 2024 AND split_type = 'advanced_splits'
        LIMIT 5
        """
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cur:
                cur.execute(advanced_query)
                advanced_results = cur.fetchall()
        
        for row in advanced_results:
            print(f"{row['split_category']}: {row['completions']}/{row['attempts']} for {row['pass_yards']} yards, {row['pass_tds']} TDs, {row['rating']} rating")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    main() 