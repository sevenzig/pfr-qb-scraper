#!/usr/bin/env python3
"""
Check what teams are in the database
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.db_manager import DatabaseManager

def check_teams():
    """Check what teams are in the database"""
    print("Checking teams in database...")
    
    db_manager = DatabaseManager()
    
    try:
        # Get all teams
        result = db_manager.query("SELECT * FROM teams ORDER BY team_code")
        
        if result:
            print(f"Found {len(result)} teams:")
            for row in result:
                print(f"  {row['team_code']} - {row['team_name']} ({row['conference']})")
        else:
            print("No teams found in database")
            
    except Exception as e:
        print(f"Error checking teams: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    check_teams() 