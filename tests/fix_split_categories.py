#!/usr/bin/env python3
"""
Fix the categorization of existing "other" splits by mapping values to proper split types
"""

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def create_split_mapping():
    """Create mapping from values to proper split types"""
    
    # Define the mapping based on the values we saw
    split_mapping = {
        # Place splits
        'Home': 'place',
        'Road': 'place',
        
        # Result splits  
        'Win': 'result',
        'Loss': 'result',
        
        # Time splits
        'Early': 'time',
        'Late': 'time',
        'Afternoon': 'time',
        
        # Day splits
        'Sunday': 'day',
        'Monday': 'day',
        
        # Month splits
        'September': 'month',
        'October': 'month', 
        'November': 'month',
        'December': 'month',
        'January': 'month',
        
        # Conference splits
        'AFC': 'conference',
        'NFC': 'conference',
        
        # Division splits
        'AFC North': 'division',
        'AFC South': 'division',
        'AFC East': 'division',
        'AFC West': 'division',
        'NFC North': 'division',
        'NFC South': 'division',
        'NFC East': 'division',
        'NFC West': 'division',
        
        # Score differential splits
        '0-7 points': 'score_differential',
        '5-8': 'score_differential',
        '8-14 points': 'score_differential',
        '9-12': 'score_differential',
        '13+': 'score_differential',
        '15+ points': 'score_differential',
        
        # Field position splits
        '1-4': 'field_position',
        
        # Stadium type splits
        'outdoors': 'stadium_type',
        'retroof': 'stadium_type',
        'dome': 'stadium_type',
        
        # Game situation splits
        'Starter': 'game_situation',
        
        # League splits
        'NFL': 'league',
    }
    
    return split_mapping

def fix_split_categories():
    """Fix the categorization of existing 'other' splits"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    split_mapping = create_split_mapping()
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("=== Fixing Split Categories ===")
        print(f"Mapping {len(split_mapping)} value types to proper split categories")
        
        # Get current stats
        cur.execute("SELECT COUNT(*) FROM qb_splits WHERE split = 'other'")
        total_other = cur.fetchone()[0]
        print(f"Total 'other' splits to process: {total_other}")
        
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
        print(f"\n=== New Split Distribution ===")
        cur.execute("""
            SELECT split, COUNT(*) as count 
            FROM qb_splits 
            GROUP BY split 
            ORDER BY count DESC
        """)
        
        result = cur.fetchall()
        for row in result:
            print(f"  - {row[0]}: {row[1]} records")
        
        # Show remaining "other" values
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

def preview_changes():
    """Preview what changes would be made without actually updating"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    split_mapping = create_split_mapping()
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("=== Preview of Split Category Changes ===")
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
        preview_changes()
    else:
        # Ask for confirmation
        print("This script will update the split categories for existing 'other' splits.")
        print("This will change the 'split' field from 'other' to proper categories like 'place', 'result', etc.")
        response = input("Do you want to proceed? (y/N): ")
        
        if response.lower() in ['y', 'yes']:
            fix_split_categories()
        else:
            print("Operation cancelled. Use --preview to see what would be changed.") 