#!/usr/bin/env python3
"""
Debug script to check what data attributes are present in the "other=1-4" split rows
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_other_split():
    """Debug the "other=1-4" split to see what data attributes are available"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check what data we have for "other=1-4" splits
        print("=== Data for 'other=1-4' splits ===")
        cur.execute("""
            SELECT pfr_id, player_name, season, 
                   cmp, att, inc, cmp_pct, yds, td, first_downs, int, rate,
                   sk, sk_yds, y_a, ay_a, rush_att, rush_yds, rush_y_a, rush_td, rush_first_downs
            FROM qb_splits_advanced 
            WHERE split = 'other' AND value = '1-4'
            ORDER BY player_name
            LIMIT 10
        """)
        
        rows = cur.fetchall()
        print(f"Found {len(rows)} 'other=1-4' rows (showing first 10):")
        for row in rows:
            print(f"  {row[0]} ({row[1]}) - {row[2]}")
            print(f"    Passing: cmp={row[3]}, att={row[4]}, inc={row[5]}, cmp_pct={row[6]}")
            print(f"    Passing: yds={row[7]}, td={row[8]}, first_downs={row[9]}, int={row[10]}, rate={row[11]}")
            print(f"    Passing: sk={row[12]}, sk_yds={row[13]}, y_a={row[14]}, ay_a={row[15]}")
            print(f"    Rushing: att={row[16]}, yds={row[17]}, y_a={row[18]}, td={row[19]}, first_downs={row[20]}")
        
        # Compare with a different split that has first_downs
        print(f"\n=== Comparison: Data for 'down=1st' splits ===")
        cur.execute("""
            SELECT pfr_id, player_name, season, 
                   cmp, att, inc, cmp_pct, yds, td, first_downs, int, rate,
                   sk, sk_yds, y_a, ay_a, rush_att, rush_yds, rush_y_a, rush_td, rush_first_downs
            FROM qb_splits_advanced 
            WHERE split = 'down' AND value = '1st'
            ORDER BY player_name
            LIMIT 5
        """)
        
        rows = cur.fetchall()
        print(f"Found {len(rows)} 'down=1st' rows (showing first 5):")
        for row in rows:
            print(f"  {row[0]} ({row[1]}) - {row[2]}")
            print(f"    Passing: cmp={row[3]}, att={row[4]}, inc={row[5]}, cmp_pct={row[6]}")
            print(f"    Passing: yds={row[7]}, td={row[8]}, first_downs={row[9]}, int={row[10]}, rate={row[11]}")
            print(f"    Passing: sk={row[12]}, sk_yds={row[13]}, y_a={row[14]}, ay_a={row[15]}")
            print(f"    Rushing: att={row[16]}, yds={row[17]}, y_a={row[18]}, td={row[19]}, first_downs={row[20]}")
        
        # Check if this is a data source issue or scraping issue
        print(f"\n=== Data Completeness Analysis ===")
        cur.execute("""
            SELECT 
                split,
                value,
                COUNT(*) as total_rows,
                COUNT(cmp) as cmp_count,
                COUNT(att) as att_count,
                COUNT(inc) as inc_count,
                COUNT(cmp_pct) as cmp_pct_count,
                COUNT(first_downs) as first_downs_count,
                COUNT(rush_first_downs) as rush_first_downs_count
            FROM qb_splits_advanced 
            WHERE split = 'other' OR split = 'down'
            GROUP BY split, value
            ORDER BY split, value
        """)
        
        completeness = cur.fetchall()
        for row in completeness:
            split, value, total, cmp, att, inc, cmp_pct, first_downs, rush_first_downs = row
            print(f"  {split}={value}: {total} rows")
            print(f"    cmp: {cmp}/{total} ({cmp/total*100:.1f}%)")
            print(f"    att: {att}/{total} ({att/total*100:.1f}%)")
            print(f"    inc: {inc}/{total} ({inc/total*100:.1f}%)")
            print(f"    cmp_pct: {cmp_pct}/{total} ({cmp_pct/total*100:.1f}%)")
            print(f"    first_downs: {first_downs}/{total} ({first_downs/total*100:.1f}%)")
            print(f"    rush_first_downs: {rush_first_downs}/{total} ({rush_first_downs/total*100:.1f}%)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_other_split() 