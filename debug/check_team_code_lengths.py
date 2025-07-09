#!/usr/bin/env python3
"""Check which teams don't have 3-letter codes"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

def main():
    db = DatabaseManager()
    
    try:
        print("=== Team Code Length Check ===")
        teams = db.query('SELECT team_code, team_name FROM teams ORDER BY team_code')
        
        print("Current team codes:")
        non_three_letter = []
        
        for team in teams:
            code_length = len(team['team_code'])
            status = "✓" if code_length == 3 else "❌"
            print(f"  {team['team_code']} ({code_length} chars) {status} - {team['team_name']}")
            
            if code_length != 3:
                non_three_letter.append(team)
        
        print(f"\nSummary:")
        print(f"Total teams: {len(teams)}")
        print(f"3-letter codes: {len(teams) - len(non_three_letter)}")
        print(f"Non-3-letter codes: {len(non_three_letter)}")
        
        if non_three_letter:
            print("\nTeams needing 3-letter codes:")
            for team in non_three_letter:
                print(f"  {team['team_code']} - {team['team_name']}")
        else:
            print("\n✅ All teams have 3-letter codes!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 