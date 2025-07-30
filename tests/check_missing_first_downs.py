#!/usr/bin/env python3
"""
Check which specific splits are missing first_downs data
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_missing_first_downs():
    """Check which splits are missing first_downs data"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Find rows missing first_downs
        print("=== Rows Missing first_downs ===")
        cur.execute("""
            SELECT pfr_id, player_name, season, split, value, 
                   cmp_pct, first_downs, cmp, att
            FROM qb_splits_advanced 
            WHERE first_downs IS NULL
            ORDER BY player_name, season, split, value
            LIMIT 20
        """)
        
        rows = cur.fetchall()
        print(f"Found {len(rows)} rows missing first_downs (showing first 20):")
        for row in rows:
            print(f"  {row[0]} ({row[1]}) - {row[2]} - {row[3]}={row[4]}")
            print(f"    cmp_pct: {row[5]}, first_downs: {row[6]}, cmp: {row[7]}, att: {row[8]}")
        
        # Check by split type
        print(f"\n=== Missing first_downs by Split Type ===")
        cur.execute("""
            SELECT split, COUNT(*) as missing_count
            FROM qb_splits_advanced 
            WHERE first_downs IS NULL
            GROUP BY split
            ORDER BY missing_count DESC
        """)
        
        split_stats = cur.fetchall()
        for split, count in split_stats:
            print(f"  {split}: {count} missing")
        
        # Check by split value
        print(f"\n=== Missing first_downs by Split Value ===")
        cur.execute("""
            SELECT split, value, COUNT(*) as missing_count
            FROM qb_splits_advanced 
            WHERE first_downs IS NULL
            GROUP BY split, value
            ORDER BY missing_count DESC
            LIMIT 10
        """)
        
        value_stats = cur.fetchall()
        for split, value, count in value_stats:
            print(f"  {split}={value}: {count} missing")
        
        # Check if this is a pattern or random
        print(f"\n=== Pattern Analysis ===")
        cur.execute("""
            SELECT 
                split,
                COUNT(*) as total_rows,
                COUNT(first_downs) as rows_with_first_downs,
                COUNT(*) - COUNT(first_downs) as rows_missing_first_downs
            FROM qb_splits_advanced 
            GROUP BY split
            HAVING COUNT(*) - COUNT(first_downs) > 0
            ORDER BY rows_missing_first_downs DESC
        """)
        
        pattern_stats = cur.fetchall()
        for split, total, with_data, missing in pattern_stats:
            pct_missing = (missing / total) * 100
            print(f"  {split}: {missing}/{total} missing ({pct_missing:.1f}%)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_missing_first_downs() 