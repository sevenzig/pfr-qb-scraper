#!/usr/bin/env python3
"""
Fix the remaining "other" splits with more comprehensive mapping
"""

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def create_comprehensive_mapping():
    """Create comprehensive mapping for remaining values"""
    
    # Define the comprehensive mapping
    split_mapping = {
        # Day splits
        'Thursday': 'day',
        'Saturday': 'day',
        'Wednesday': 'day',
        'Friday': 'day',
        
        # Team/opponent splits
        'Denver Broncos': 'opponent',
        'Dallas Cowboys': 'opponent',
        'New England Patriots': 'opponent',
        'Washington Commanders': 'opponent',
        'Houston Texans': 'opponent',
        'Cleveland Browns': 'opponent',
        'Baltimore Ravens': 'opponent',
        'San Francisco 49ers': 'opponent',
        'New York Jets': 'opponent',
        'New York Giants': 'opponent',
        'Carolina Panthers': 'opponent',
        'Chicago Bears': 'opponent',
        'Los Angeles Chargers': 'opponent',
        'Jacksonville Jaguars': 'opponent',
        'Philadelphia Eagles': 'opponent',
        'Kansas City Chiefs': 'opponent',
        'Cincinnati Bengals': 'opponent',
        'New Orleans Saints': 'opponent',
        'Buffalo Bills': 'opponent',
        'Indianapolis Colts': 'opponent',
        'Atlanta Falcons': 'opponent',
        'Tampa Bay Buccaneers': 'opponent',
        'Seattle Seahawks': 'opponent',
        'Los Angeles Rams': 'opponent',
        'Miami Dolphins': 'opponent',
        'Pittsburgh Steelers': 'opponent',
        'Tennessee Titans': 'opponent',
        'Detroit Lions': 'opponent',
        'Minnesota Vikings': 'opponent',
        'Arizona Cardinals': 'opponent',
        'Green Bay Packers': 'opponent',
        'Las Vegas Raiders': 'opponent',
        
        # Time splits
        'Morning': 'time',
        
        # Playoff type splits
        'Wild Card': 'playoff_type',
        'Divisional': 'playoff_type',
        'Conference Championship': 'playoff_type',
        'Super Bowl': 'playoff_type',
        
        # Snap type splits
        'Huddle': 'snap_type',
        'No Huddle': 'snap_type',
        'Shotgun': 'snap_type',
        'Under Center': 'snap_type',
        
        # Down splits
        '1st': 'down',
        '2nd': 'down',
        '3rd': 'down',
        '4th': 'down',
        '1st & 10': 'down',
        '1st & >10': 'down',
        '1st & <10': 'down',
        '2nd & 1-3': 'down',
        '2nd & 4-6': 'down',
        '2nd & 7-9': 'down',
        '2nd & 10+': 'down',
        '3rd & 1-3': 'down',
        '3rd & 4-6': 'down',
        '3rd & 7-9': 'down',
        '3rd & 10+': 'down',
        '4th & 1-3': 'down',
        '4th & 4-6': 'down',
        '4th & 10+': 'down',
        
        # Yards to go splits
        '1-3': 'yards_to_go',
        '4-6': 'yards_to_go',
        '7-9': 'yards_to_go',
        '10+': 'yards_to_go',
        
        # Quarter splits
        '1st Qtr': 'quarter',
        '2nd Qtr': 'quarter',
        '3rd Qtr': 'quarter',
        '4th Qtr': 'quarter',
        'OT': 'quarter',
        
        # Half splits
        '1st Half': 'half',
        '2nd Half': 'half',
        
        # Score differential splits
        'Leading': 'score_differential',
        'Tied': 'score_differential',
        'Trailing': 'score_differential',
        'Leading, < 2 min to go': 'score_differential',
        'Leading, < 4 min to go': 'score_differential',
        'Tied, < 2 min to go': 'score_differential',
        'Tied, < 4 min to go': 'score_differential',
        'Trailing, < 2 min to go': 'score_differential',
        'Trailing, < 4 min to go': 'score_differential',
        
        # Field position splits
        'Own 1-10': 'field_position',
        'Own 1-20': 'field_position',
        'Own 21-50': 'field_position',
        'Opp 1-10': 'field_position',
        'Opp 49-20': 'field_position',
        'Red Zone': 'field_position',
        
        # Play action splits
        'play action': 'play_action',
        'non-play action': 'play_action',
        
        # RPO splits
        'rpo': 'run_pass_option',
        'non-rpo': 'run_pass_option',
        
        # Time in pocket splits
        '2.5+ seconds': 'time_in_pocket',
        '< 2.5 seconds': 'time_in_pocket',
        
        # Game situation splits
        'Total': 'game_situation',
    }
    
    return split_mapping

def fix_remaining_splits():
    """Fix the remaining 'other' splits"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    split_mapping = create_comprehensive_mapping()
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("=== Fixing Remaining Split Categories ===")
        print(f"Mapping {len(split_mapping)} additional value types to proper split categories")
        
        # Get current stats
        cur.execute("SELECT COUNT(*) FROM qb_splits WHERE split = 'other'")
        total_other = cur.fetchone()[0]
        print(f"Total remaining 'other' splits to process: {total_other}")
        
        # Process each mapping
        updated_count = 0
        for value, new_split_type in split_mapping.items():
            # Update records for this value
            cur.execute("""
                UPDATE qb_splits 
                SET split = %s, updated_at = %s
                WHERE split = 'other' AND value = %s
            """, (new_split_type, datetime.now(), value))
            
            rows_updated = cur.rowcount
            if rows_updated > 0:
                print(f"  ✓ Updated {rows_updated} records: '{value}' -> '{new_split_type}'")
                updated_count += rows_updated
        
        # Commit the changes
        conn.commit()
        
        print(f"\n=== Update Summary ===")
        print(f"Total records updated: {updated_count}")
        print(f"Records remaining as 'other': {total_other - updated_count}")
        
        # Show new split distribution
        print(f"\n=== Final Split Distribution ===")
        cur.execute("""
            SELECT split, COUNT(*) as count 
            FROM qb_splits 
            GROUP BY split 
            ORDER BY count DESC
        """)
        
        result = cur.fetchall()
        for row in result:
            print(f"  - {row[0]}: {row[1]} records")
        
        # Show any remaining "other" values
        if total_other - updated_count > 0:
            print(f"\n=== Remaining 'other' values ===")
            cur.execute("""
                SELECT value, COUNT(*) as count 
                FROM qb_splits 
                WHERE split = 'other' 
                GROUP BY value 
                ORDER BY count DESC
            """)
            
            result = cur.fetchall()
            for row in result:
                print(f"  - {row[0]}: {row[1]} records")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()

def preview_remaining_changes():
    """Preview what changes would be made for remaining splits"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    split_mapping = create_comprehensive_mapping()
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("=== Preview of Remaining Split Category Changes ===")
        print("(This is a preview - no changes will be made)")
        
        for value, new_split_type in split_mapping.items():
            # Count records that would be updated
            cur.execute("""
                SELECT COUNT(*) 
                FROM qb_splits 
                WHERE split = 'other' AND value = %s
            """, (value,))
            
            count = cur.fetchone()[0]
            if count > 0:
                print(f"  '{value}' -> '{new_split_type}': {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        preview_remaining_changes()
    else:
        # Ask for confirmation
        print("This script will update the remaining split categories for 'other' splits.")
        print("This will categorize the remaining 771 records with proper split types.")
        response = input("Do you want to proceed? (y/N): ")
        
        if response.lower() in ['y', 'yes']:
            fix_remaining_splits()
        else:
            print("Operation cancelled. Use --preview to see what would be changed.") 