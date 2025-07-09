#!/usr/bin/env python3
"""Check teams in database and identify missing ones"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

def main():
    db = DatabaseManager()
    
    print("=== Teams currently in database ===")
    teams = db.query('SELECT team_code, team_name FROM teams ORDER BY team_code')
    
    if not teams:
        print("No teams found in database!")
        return
    
    for team in teams:
        print(f"{team['team_code']} - {team['team_name']}")
    
    print(f"\nTotal teams: {len(teams)}")
    
    # Check if we have the expected 32 NFL teams
    if len(teams) < 32:
        print(f"WARNING: Expected 32 teams, but only found {len(teams)}")

if __name__ == "__main__":
    main() 