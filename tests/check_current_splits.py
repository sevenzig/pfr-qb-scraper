#!/usr/bin/env python3
"""
Check current split categories in the database
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_current_splits():
    """Check current split categories in the database"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check what split categories exist
        print("=== Current Split Categories ===")
        cur.execute("""
            SELECT split, COUNT(*) as count 
            FROM qb_splits 
            GROUP BY split 
            ORDER BY count DESC
        """)
        
        result = cur.fetchall()
        for row in result:
            print(f"  - {row[0]}: {row[1]} records")
        
        # Check what values are being used for "other" splits
        print(f"\n=== Values for 'other' splits ===")
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
        
        # Show sample records with "other" split
        print(f"\n=== Sample 'other' split records ===")
        cur.execute("""
            SELECT pfr_id, player_name, season, value, 
                   cmp, att, yds, td, rush_att, rush_yds, rush_td
            FROM qb_splits 
            WHERE split = 'other' 
            ORDER BY player_name, season 
            LIMIT 10
        """)
        
        result = cur.fetchall()
        for row in result:
            print(f"  - {row[1]} ({row[2]}): {row[3]}")
            print(f"    Passing: {row[4]}/{row[5]} for {row[6]} yards, {row[7]} TDs")
            print(f"    Rushing: {row[8]} att for {row[9]} yards, {row[10]} TDs")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_current_splits() 