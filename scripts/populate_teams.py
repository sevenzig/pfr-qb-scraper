#!/usr/bin/env python3
"""
Script to populate the teams table with all 32 NFL teams
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

def populate_teams():
    """Populate the teams table with all NFL teams"""
    print("Populating teams table with all NFL teams...")
    
    # All 32 NFL teams with their codes, names, cities, divisions, and conferences
    teams_data = [
        # AFC East
        ('BUF', 'Buffalo Bills', 'Buffalo', 'East', 'AFC'),
        ('MIA', 'Miami Dolphins', 'Miami', 'East', 'AFC'),
        ('NE', 'New England Patriots', 'Foxborough', 'East', 'AFC'),
        ('NYJ', 'New York Jets', 'East Rutherford', 'East', 'AFC'),
        
        # AFC North
        ('BAL', 'Baltimore Ravens', 'Baltimore', 'North', 'AFC'),
        ('CIN', 'Cincinnati Bengals', 'Cincinnati', 'North', 'AFC'),
        ('CLE', 'Cleveland Browns', 'Cleveland', 'North', 'AFC'),
        ('PIT', 'Pittsburgh Steelers', 'Pittsburgh', 'North', 'AFC'),
        
        # AFC South
        ('HOU', 'Houston Texans', 'Houston', 'South', 'AFC'),
        ('IND', 'Indianapolis Colts', 'Indianapolis', 'South', 'AFC'),
        ('JAX', 'Jacksonville Jaguars', 'Jacksonville', 'South', 'AFC'),
        ('TEN', 'Tennessee Titans', 'Nashville', 'South', 'AFC'),
        
        # AFC West
        ('DEN', 'Denver Broncos', 'Denver', 'West', 'AFC'),
        ('KC', 'Kansas City Chiefs', 'Kansas City', 'West', 'AFC'),
        ('LV', 'Las Vegas Raiders', 'Las Vegas', 'West', 'AFC'),
        ('LAC', 'Los Angeles Chargers', 'Los Angeles', 'West', 'AFC'),
        
        # NFC East
        ('DAL', 'Dallas Cowboys', 'Arlington', 'East', 'NFC'),
        ('NYG', 'New York Giants', 'East Rutherford', 'East', 'NFC'),
        ('PHI', 'Philadelphia Eagles', 'Philadelphia', 'East', 'NFC'),
        ('WAS', 'Washington Commanders', 'Landover', 'East', 'NFC'),
        
        # NFC North
        ('CHI', 'Chicago Bears', 'Chicago', 'North', 'NFC'),
        ('DET', 'Detroit Lions', 'Detroit', 'North', 'NFC'),
        ('GB', 'Green Bay Packers', 'Green Bay', 'North', 'NFC'),
        ('MIN', 'Minnesota Vikings', 'Minneapolis', 'North', 'NFC'),
        
        # NFC South
        ('ATL', 'Atlanta Falcons', 'Atlanta', 'South', 'NFC'),
        ('CAR', 'Carolina Panthers', 'Charlotte', 'South', 'NFC'),
        ('NO', 'New Orleans Saints', 'New Orleans', 'South', 'NFC'),
        ('TB', 'Tampa Bay Buccaneers', 'Tampa', 'South', 'NFC'),
        
        # NFC West
        ('ARI', 'Arizona Cardinals', 'Glendale', 'West', 'NFC'),
        ('LAR', 'Los Angeles Rams', 'Los Angeles', 'West', 'NFC'),
        ('SF', 'San Francisco 49ers', 'Santa Clara', 'West', 'NFC'),
        ('SEA', 'Seattle Seahawks', 'Seattle', 'West', 'NFC'),
    ]
    
    db_manager = DatabaseManager()
    
    try:
        # Insert all teams
        insert_query = """
        INSERT INTO teams (team_code, team_name, city, division, conference, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (team_code) 
        DO UPDATE SET
            team_name = EXCLUDED.team_name,
            city = EXCLUDED.city,
            division = EXCLUDED.division,
            conference = EXCLUDED.conference
        """
        
        now = datetime.now()
        values = [(team_code, team_name, city, division, conference, now) for team_code, team_name, city, division, conference in teams_data]
        
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cur:
                from psycopg2.extras import execute_batch
                execute_batch(cur, insert_query, values, page_size=100)
                conn.commit()
        
        print(f"✓ Successfully inserted/updated {len(teams_data)} teams")
        
        # Verify the teams were inserted
        result = db_manager.query("SELECT COUNT(*) as count FROM teams")
        if result:
            count = result[0]['count']
            print(f"✓ Teams table now contains {count} teams")
        
        # Show a few teams as verification
        print("\nSample teams in database:")
        sample_teams = db_manager.query("SELECT * FROM teams ORDER BY team_code LIMIT 10")
        for team in sample_teams:
            print(f"  {team['team_code']} - {team['team_name']} ({team['conference']})")
            
    except Exception as e:
        print(f"✗ Error populating teams: {e}")
        raise
    finally:
        db_manager.close()

if __name__ == "__main__":
    populate_teams() 