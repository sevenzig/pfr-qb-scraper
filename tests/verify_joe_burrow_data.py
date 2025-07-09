#!/usr/bin/env python3
"""
Verify Joe Burrow's data is in the database
"""

import sys
sys.path.append('src')

from config.config import config
from database.db_manager import DatabaseManager

def main():
    """Verify Joe Burrow's data in database"""
    print("Verifying Joe Burrow's data in database...")
    
    db_manager = DatabaseManager(config.get_database_url())
    
    try:
        # Get Joe Burrow's stats
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cur:
                cur.execute("""
                    SELECT player_name, team, season, games_played, completions, attempts, 
                           pass_yards, pass_tds, interceptions, rating, scraped_at
                    FROM qb_stats 
                    WHERE player_name = 'Joe Burrow' AND season = 2024
                """)
                result = cur.fetchone()
                
                if result:
                    print("✅ Joe Burrow's data found in database:")
                    print(f"   Player: {result['player_name']}")
                    print(f"   Team: {result['team']}")
                    print(f"   Season: {result['season']}")
                    print(f"   Games: {result['games_played']}")
                    print(f"   Completions: {result['completions']}/{result['attempts']}")
                    print(f"   Yards: {result['pass_yards']}")
                    print(f"   TDs: {result['pass_tds']}")
                    print(f"   INTs: {result['interceptions']}")
                    print(f"   Rating: {result['rating']}")
                    print(f"   Scraped: {result['scraped_at']}")
                else:
                    print("❌ Joe Burrow's data not found in database")
                
                # Check total QB stats count
                cur.execute("SELECT COUNT(*) as count FROM qb_stats")
                total = cur.fetchone()
                print(f"\n📊 Total QB stats records in database: {total['count']}")
                
    except Exception as e:
        print(f"❌ Error querying database: {e}")

if __name__ == "__main__":
    main() 