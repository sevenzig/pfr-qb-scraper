#!/usr/bin/env python3
"""
Update teams table to use proper PFR team codes

This script updates the teams table to use the correct Pro Football Reference
team codes that match what the scraper actually encounters.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Update teams table with correct PFR codes"""
    db = DatabaseManager()
    
    try:
        logger.info("Updating teams table to use PFR team codes...")
        
        # First, check existing teams
        existing_teams = db.query("SELECT team_code, team_name FROM teams ORDER BY team_code")
        logger.info(f"Found {len(existing_teams)} existing teams")
        
        # Team code updates mapping old codes to new PFR codes
        team_updates = [
            ('SF', 'SFO'),
            ('GB', 'GNB'), 
            ('KC', 'KAN'),
            ('LV', 'LVR'),
            ('NE', 'NWE'),
            ('NO', 'NOR')
        ]
        
        # Update existing team codes
        for old_code, new_code in team_updates:
            rows_affected = db.execute(
                "UPDATE teams SET team_code = %s WHERE team_code = %s",
                (new_code, old_code)
            )
            logger.info(f"Updated {old_code} -> {new_code} (affected {rows_affected} rows)")
        
        # Check if Tampa Bay exists
        tampa_check = db.query(
            "SELECT * FROM teams WHERE team_code = 'TAM' OR team_name ILIKE '%tampa%'"
        )
        
        if not tampa_check:
            logger.info("Tampa Bay not found, adding...")
            db.execute(
                """INSERT INTO teams (team_code, team_name, city, conference, division) 
                   VALUES (%s, %s, %s, %s, %s)""",
                ('TAM', 'Tampa Bay Buccaneers', 'Tampa Bay', 'NFC', 'South')
            )
            logger.info("Added Tampa Bay Buccaneers")
        else:
            logger.info("Tampa Bay already exists")
        
        # Verify final teams
        final_teams = db.query("SELECT team_code, team_name FROM teams ORDER BY team_code")
        logger.info("Final teams in database:")
        for team in final_teams:
            logger.info(f"  {team['team_code']} - {team['team_name']}")
        
        logger.info("Teams update completed successfully!")
        
    except Exception as e:
        logger.error(f"Error updating teams: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 